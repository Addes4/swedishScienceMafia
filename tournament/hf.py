"""Open models through the Hugging Face router (OpenAI-compatible), under the same dollar cap.

    install(budget)        route every openai-SDK chat.completions.create call (sync and async) through
                           the budget, as tournament/guard.py does for the Anthropic SDK
    fetch_prices(models)   price per pinned "model:provider" from the router's /v1/models
    HFClient().call(...)   Claude.call's interface (system, user -> CallResult) on the router

Models are pinned to one provider with the router's "model:provider" suffix, so price and
behaviour stay fixed. Prices come from the provider's own entry in /v1/models; a pinned provider
without a listed price is refused.

Accounting. Each request reserves input upper bound x input price + max_tokens x output price
before it is sent and is settled with the reported usage. Reasoning models report their thinking
in completion_tokens_details.reasoning_tokens: if completion_tokens already includes it (the
OpenAI convention) it is counted once; if a provider reports it on top (completion_tokens smaller
than reasoning_tokens), it is added. Either way reasoning is billed as output.

Errors. 401, 402 and 403, and any error mentioning insufficient credit or billing, are fatal: no
retry, nothing charged, every later call in the process refused (FatalAPIError). 429 and 5xx are
retried with backoff for up to 10 minutes. Other failures without a response are charged their
reservation, because what was billed is unknown.
"""
import asyncio
import os
import random
import time
from pathlib import Path

import httpx
import openai
from openai.resources.chat.completions import completions as chat

from autoresearch.claude import CallResult

from .budget import Budget, FatalAPIError, UnbudgetedCall, input_upper_bound

HF_BASE = "https://router.huggingface.co/v1"
BASE_ENV = "TOURNAMENT_HF_BASE_URL"          # tests and mock runs point this at tournament.mockapi
RETRY_STATUSES = (429, 500, 502, 503, 504, 529)
FATAL_STATUSES = (401, 402, 403)
FATAL_MARKERS = ("insufficient", "credit", "billing", "payment required", "quota")
RETRY_MAX_WAIT_S = 600.0

_ORIG = {}
_BUDGET = None


def base_url() -> str:
    return os.environ.get(BASE_ENV, HF_BASE)


def token() -> str:
    tok = os.environ.get("HF_TOKEN")
    if not tok:
        path = Path.home() / ".cache" / "huggingface" / "token"
        tok = path.read_text().strip() if path.exists() else None
    if not tok:
        raise SystemExit("HF_TOKEN is not set and ~/.cache/huggingface/token does not exist")
    return tok


def fetch_prices(models) -> dict:
    """{pinned model: (input $/M, output $/M)} from the router's /v1/models (no billed call)."""
    r = httpx.get(f"{base_url()}/models", headers={"Authorization": f"Bearer {token()}"}, timeout=60)
    r.raise_for_status()
    listed = {m["id"]: m for m in r.json()["data"]}
    out = {}
    for pinned in models:
        name, _, provider = pinned.partition(":")
        entry = next((p for p in listed.get(name, {}).get("providers", []) if p.get("provider") == provider), None)
        pricing = (entry or {}).get("pricing")
        if not pricing:
            raise SystemExit(f"{pinned}: provider not listed or has no price on the router; refusing to run")
        out[pinned] = (float(pricing["input"]), float(pricing["output"]))
    return out


# -- the guard ---------------------------------------------------------------------------------
def fatal_reason(e: BaseException):
    if not isinstance(e, openai.APIStatusError):
        return None
    text = str(e).lower()
    if e.status_code in FATAL_STATUSES or any(m in text for m in FATAL_MARKERS):
        return f"HTTP {e.status_code}: {str(e)[:200]}"
    return None


def _retry_delay(e, attempt, waited):
    if fatal_reason(e) or not isinstance(e, openai.APIStatusError) or e.status_code not in RETRY_STATUSES \
            or waited >= RETRY_MAX_WAIT_S:
        return None
    return min(60.0, 2.0 ** attempt) * (0.5 + random.random())


def output_tokens(usage) -> int:
    completion = int(getattr(usage, "completion_tokens", 0) or 0)
    details = getattr(usage, "completion_tokens_details", None)
    reasoning = int(getattr(details, "reasoning_tokens", 0) or 0) if details is not None else 0
    return completion + reasoning if reasoning > completion else completion


def _prepare(kwargs):
    if kwargs.get("stream"):
        raise UnbudgetedCall("streaming chat completions are not budgeted")
    if "model" not in kwargs or "messages" not in kwargs:
        raise UnbudgetedCall("model and messages must be passed as keyword arguments")
    key = "max_tokens" if "max_tokens" in kwargs else "max_completion_tokens" if "max_completion_tokens" in kwargs else None
    if key is None:
        raise UnbudgetedCall("chat completions need max_tokens so their worst-case cost is bounded")
    return key


def _settle_ok(budget, res, resp, path):
    usage = resp.usage
    u = {"input_tokens": int(getattr(usage, "prompt_tokens", 0) or 0), "output_tokens": output_tokens(usage)}
    details = getattr(usage, "completion_tokens_details", None)
    choice = resp.choices[0] if resp.choices else None
    budget.settle(res, usage=u, served_model=res.model, stop_reason=getattr(choice, "finish_reason", None), path=path,
                  extra={"reasoning_tokens": int(getattr(details, "reasoning_tokens", 0) or 0) if details else 0,
                         "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
                         "content_empty": not (choice and choice.message and choice.message.content)})


def _settle_failure(budget, res, e, path):
    reason = fatal_reason(e)
    if reason:
        budget.settle(res, error=e, charge_reservation=False, path=path, extra={"fatal": True})
        budget.mark_fatal(reason)
        raise FatalAPIError(reason) from e
    budget.settle(res, error=e, charge_reservation=not isinstance(e, openai.APIStatusError), path=path)


def _sync_create(self, *args, **kwargs):
    budget = _BUDGET
    if budget is None:
        return _ORIG["create"](self, *args, **kwargs)
    key, path = _prepare(kwargs), "chat.completions.create"
    res = budget.reserve(kwargs["model"], int(kwargs[key]), input_upper_bound(None, kwargs["messages"]), path)
    kwargs[key] = res.granted_max_tokens
    attempt, waited = 0, 0.0
    while True:
        try:
            resp = _ORIG["create"](self, *args, **kwargs)
            break
        except BaseException as e:
            delay = _retry_delay(e, attempt, waited)
            if delay is None:
                _settle_failure(budget, res, e, path)
                raise
            budget.log_event({"event": "retry", "path": path, "status": getattr(e, "status_code", None),
                              "delay_s": round(delay, 2)})
            time.sleep(delay)
            attempt, waited = attempt + 1, waited + delay
    _settle_ok(budget, res, resp, path)
    return resp


async def _async_create(self, *args, **kwargs):
    budget = _BUDGET
    if budget is None:
        return await _ORIG["acreate"](self, *args, **kwargs)
    key, path = _prepare(kwargs), "chat.completions.create(async)"
    res = await budget.reserve_async(kwargs["model"], int(kwargs[key]), input_upper_bound(None, kwargs["messages"]), path)
    kwargs[key] = res.granted_max_tokens
    attempt, waited = 0, 0.0
    while True:
        try:
            resp = await _ORIG["acreate"](self, *args, **kwargs)
            break
        except BaseException as e:
            delay = _retry_delay(e, attempt, waited)
            if delay is None:
                _settle_failure(budget, res, e, path)
                raise
            budget.log_event({"event": "retry", "path": path, "status": getattr(e, "status_code", None),
                              "delay_s": round(delay, 2)})
            await asyncio.sleep(delay)
            attempt, waited = attempt + 1, waited + delay
    _settle_ok(budget, res, resp, path)
    return resp


def install(budget: Budget) -> None:
    global _BUDGET
    _BUDGET = budget
    if _ORIG:
        return
    _ORIG["create"] = chat.Completions.create
    _ORIG["acreate"] = chat.AsyncCompletions.create
    chat.Completions.create = _sync_create
    chat.AsyncCompletions.create = _async_create


def uninstall() -> None:
    global _BUDGET
    _BUDGET = None
    if _ORIG:
        chat.Completions.create = _ORIG.pop("create")
        chat.AsyncCompletions.create = _ORIG.pop("acreate")


# -- client ------------------------------------------------------------------------------------
class HFClient:
    """autoresearch.claude.Claude's interface on the HF router; `effort` is ignored (not portable)."""

    def __init__(self, timeout: float = 900.0):
        self.client = openai.OpenAI(base_url=base_url(), api_key=token(), timeout=timeout, max_retries=2)

    def call(self, model: str, system: str, user: str, max_tokens: int = 32000, effort=None) -> CallResult:
        t0 = time.time()
        resp = self.client.chat.completions.create(
            model=model, max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        usage = resp.usage
        pin, pout = (0.0, 0.0)
        from .budget import per_token_prices
        try:
            pin, pout = per_token_prices(model)
        except UnbudgetedCall:
            pass
        n_in, n_out = int(getattr(usage, "prompt_tokens", 0) or 0), output_tokens(usage)
        choice = resp.choices[0] if resp.choices else None
        text = (choice.message.content if choice and choice.message else None) or ""
        return CallResult(text=text, model=model, cost=n_in * pin + n_out * pout, input_tokens=n_in,
                          output_tokens=n_out, seconds=time.time() - t0,
                          refused=bool(choice and choice.finish_reason == "content_filter"), served_by=model)
