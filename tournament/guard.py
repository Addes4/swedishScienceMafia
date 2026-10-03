"""Route every Anthropic SDK message call in this process through a Budget.

install(budget) patches the SDK's resource classes, so it covers clients created anywhere,
including inside ShinkaEvolve. Budgeted paths:

    client.messages.create(...)                 sync and async, non-streaming (ShinkaEvolve)
    client.beta.messages.stream(...)            sync (autoresearch.claude.Claude: triage, lean)

Every other path that can generate tokens (streaming create, messages.stream, beta create, async
streams, batches, parse) raises UnbudgetedCall instead of sending anything.

Server-side refusal fallbacks are stripped from every request: with them, a refused request is
re-run on another model at that model's prices, so the worst case could not be bounded. A
refusal is then an ordinary outcome (stop_reason "refusal") that the arm records.

Rate limits and overload: a request that fails at the start with HTTP 429, 500, 502, 503, 504 or
529 (after the SDK's own retries) is retried here with exponential backoff for up to 10 minutes,
holding its reservation. These failures are not billed. Every retry is logged. Many tournament
containers share one API organisation, so this keeps a busy minute from ending a run.

Fatal errors: no credit ("credit balance is too low", HTTP 400), a bad key (401) or no permission
(403), whether returned at once or inside a stream, are never retried. The guard marks the budget
fatal and raises FatalAPIError; every later call in the process is refused without being sent.
These are charged nothing: the API generates nothing it can bill. (In full-v1, before this rule,
ShinkaEvolve's own retries sent such a refused request more than 12,000 times.)
"""
import asyncio
import random
import time

import anthropic
from anthropic.resources.beta.messages import batches as beta_batches
from anthropic.resources.beta.messages import messages as beta_messages
from anthropic.resources.messages import batches as std_batches
from anthropic.resources.messages import messages as std_messages

from .budget import Budget, FatalAPIError, UnbudgetedCall, input_upper_bound

_ORIG = {}
_BUDGET = None


def _prepare(kwargs: dict):
    kwargs = dict(kwargs)
    stripped = kwargs.pop("fallbacks", None) is not None
    betas = kwargs.get("betas")
    if isinstance(betas, (list, tuple)):
        kept = [b for b in betas if not str(b).startswith("server-side-fallback")]
        stripped = stripped or len(kept) != len(betas)
        if kept:
            kwargs["betas"] = kept
        else:
            kwargs.pop("betas")
    if "model" not in kwargs or "max_tokens" not in kwargs:
        raise UnbudgetedCall("model and max_tokens must be passed as keyword arguments")
    return kwargs, stripped


def _upper(kwargs):
    return input_upper_bound(kwargs.get("system"), kwargs.get("messages"))


def _unknown_billing(e: BaseException) -> bool:
    """An HTTP error status means nothing was generated; anything else may have been billed."""
    return not isinstance(e, anthropic.APIStatusError)


RETRY_STATUSES = (429, 500, 502, 503, 504, 529)
RETRY_MAX_WAIT_S = 600.0
FATAL_STATUSES = (401, 403)
FATAL_MARKERS = ("authentication_error", "permission_error", "invalid x-api-key")


def fatal_reason(e: BaseException):
    """Why this API error cannot be fixed by retrying, or None."""
    if not isinstance(e, anthropic.APIStatusError):
        return None
    text = str(e).lower()
    if "credit balance" in text or "billing_error" in text:
        return f"billing: {str(e)[:160]}"
    if getattr(e, "status_code", None) in FATAL_STATUSES or any(m in text for m in FATAL_MARKERS):
        return f"authentication or permission (HTTP {getattr(e, 'status_code', None)}): {str(e)[:160]}"
    return None


def _settle_failure(budget, res, e, path, extra):
    """Settle a failed call; on a fatal error stop every later call and raise FatalAPIError."""
    reason = fatal_reason(e)
    if reason:
        budget.settle(res, error=e, charge_reservation=False, path=path, extra=dict(extra, fatal=True))
        budget.mark_fatal(reason)
        raise FatalAPIError(reason) from e
    budget.settle(res, error=e, charge_reservation=_unknown_billing(e), path=path, extra=extra)


def _retry_delay(e: BaseException, attempt: int, waited: float):
    """Seconds to wait before retrying, or None to give up."""
    if not (isinstance(e, anthropic.APIStatusError) and e.status_code in RETRY_STATUSES) or waited >= RETRY_MAX_WAIT_S:
        return None
    return min(60.0, 2.0 ** attempt) * (0.5 + random.random())


def _note_retry(budget, path, e, delay):
    budget.log_event({"event": "retry", "path": path, "status": getattr(e, "status_code", None),
                      "delay_s": round(delay, 2), "error": f"{type(e).__name__}: {str(e)[:200]}"})


def _with_retries(fn, budget, path):
    attempt, waited = 0, 0.0
    while True:
        try:
            return fn()
        except anthropic.APIStatusError as e:
            delay = None if fatal_reason(e) else _retry_delay(e, attempt, waited)
            if delay is None:
                raise
            _note_retry(budget, path, e, delay)
            time.sleep(delay)
            attempt, waited = attempt + 1, waited + delay


async def _with_retries_async(fn, budget, path):
    attempt, waited = 0, 0.0
    while True:
        try:
            return await fn()
        except anthropic.APIStatusError as e:
            delay = None if fatal_reason(e) else _retry_delay(e, attempt, waited)
            if delay is None:
                raise
            _note_retry(budget, path, e, delay)
            await asyncio.sleep(delay)
            attempt, waited = attempt + 1, waited + delay


def _sync_create(self, *args, **kwargs):
    budget = _BUDGET
    if budget is None:
        return _ORIG["create"](self, *args, **kwargs)
    if kwargs.get("stream"):
        raise UnbudgetedCall("messages.create(stream=True) is not budgeted")
    kwargs, stripped = _prepare(kwargs)
    path = "messages.create"
    res = budget.reserve(kwargs["model"], kwargs["max_tokens"], _upper(kwargs), path)
    kwargs["max_tokens"] = res.granted_max_tokens
    extra = {"fallback_stripped": stripped}
    try:
        msg = _with_retries(lambda: _ORIG["create"](self, *args, **kwargs), budget, path)
    except BaseException as e:
        _settle_failure(budget, res, e, path, extra)
        raise
    budget.settle(res, usage=msg.usage, served_model=getattr(msg, "model", None), stop_reason=msg.stop_reason,
                  path=path, extra=extra)
    return msg


async def _async_create(self, *args, **kwargs):
    budget = _BUDGET
    if budget is None:
        return await _ORIG["acreate"](self, *args, **kwargs)
    if kwargs.get("stream"):
        raise UnbudgetedCall("messages.create(stream=True) is not budgeted")
    kwargs, stripped = _prepare(kwargs)
    path = "messages.create(async)"
    res = await budget.reserve_async(kwargs["model"], kwargs["max_tokens"], _upper(kwargs), path)
    kwargs["max_tokens"] = res.granted_max_tokens
    extra = {"fallback_stripped": stripped}
    try:
        msg = await _with_retries_async(lambda: _ORIG["acreate"](self, *args, **kwargs), budget, path)
    except BaseException as e:
        _settle_failure(budget, res, e, path, extra)
        raise
    budget.settle(res, usage=msg.usage, served_model=getattr(msg, "model", None), stop_reason=msg.stop_reason,
                  path=path, extra=extra)
    return msg


class _GuardedStreamManager:
    """Wraps BetaMessageStreamManager: settles the reservation when the `with` block exits."""

    def __init__(self, make, budget: Budget, res, extra):
        self.make, self.budget, self.res, self.extra = make, budget, res, extra
        self.inner = self.stream = None

    def _open(self):
        self.inner = self.make()
        return self.inner.__enter__()

    def __enter__(self):
        try:
            self.stream = _with_retries(self._open, self.budget, "beta.messages.stream")
        except BaseException as e:
            _settle_failure(self.budget, self.res, e, "beta.messages.stream", self.extra)
            raise
        return self.stream

    def __exit__(self, exc_type, exc, tb):
        try:
            result = self.inner.__exit__(exc_type, exc, tb) if self.inner is not None else False
        finally:
            snap = None
            try:
                snap = self.stream.current_message_snapshot
            except (AssertionError, AttributeError):
                pass
            finished = snap is not None and snap.stop_reason is not None
            if finished:
                self.budget.settle(self.res, usage=snap.usage, served_model=getattr(snap, "model", None),
                                   stop_reason=snap.stop_reason, path="beta.messages.stream", extra=self.extra,
                                   error=exc)
            elif fatal_reason(exc):  # e.g. a credit error delivered inside the stream: nothing billed
                _settle_failure(self.budget, self.res, exc, "beta.messages.stream", self.extra)
            else:  # stream not consumed to the end: billing unknown, charge the reservation
                self.budget.settle(self.res, error=exc or RuntimeError("stream not finished"),
                                   charge_reservation=True, path="beta.messages.stream", extra=self.extra)
        return result


def _beta_stream(self, *args, **kwargs):
    budget = _BUDGET
    if budget is None:
        return _ORIG["bstream"](self, *args, **kwargs)
    kwargs, stripped = _prepare(kwargs)
    res = budget.reserve(kwargs["model"], kwargs["max_tokens"], _upper(kwargs), "beta.messages.stream")
    kwargs["max_tokens"] = res.granted_max_tokens
    extra = {"fallback_stripped": stripped}
    return _GuardedStreamManager(lambda: _ORIG["bstream"](self, *args, **kwargs), budget, res, extra)


def _blocked(name):
    def blocked(self, *args, **kwargs):
        if _BUDGET is None:
            return _ORIG[name](self, *args, **kwargs)
        raise UnbudgetedCall(f"{name} is not budgeted by the tournament guard")
    return blocked


_BLOCKED = {
    "std.stream": (std_messages.Messages, "stream"),
    "std.parse": (std_messages.Messages, "parse"),
    "std.astream": (std_messages.AsyncMessages, "stream"),
    "std.aparse": (std_messages.AsyncMessages, "parse"),
    "beta.create": (beta_messages.Messages, "create"),
    "beta.parse": (beta_messages.Messages, "parse"),
    "beta.acreate": (beta_messages.AsyncMessages, "create"),
    "beta.astream": (beta_messages.AsyncMessages, "stream"),
    "beta.aparse": (beta_messages.AsyncMessages, "parse"),
    "std.batches": (std_batches.Batches, "create"),
    "beta.batches": (beta_batches.Batches, "create"),
}


def install(budget: Budget) -> None:
    """Route all message calls through `budget` (idempotent; a second call swaps the budget)."""
    global _BUDGET
    _BUDGET = budget
    if _ORIG:
        return
    _ORIG["create"] = std_messages.Messages.create
    _ORIG["acreate"] = std_messages.AsyncMessages.create
    _ORIG["bstream"] = beta_messages.Messages.stream
    std_messages.Messages.create = _sync_create
    std_messages.AsyncMessages.create = _async_create
    beta_messages.Messages.stream = _beta_stream
    for name, (cls, attr) in _BLOCKED.items():
        if hasattr(cls, attr):
            _ORIG[name] = getattr(cls, attr)
            setattr(cls, attr, _blocked(name))


def uninstall() -> None:
    global _BUDGET
    _BUDGET = None
    if not _ORIG:
        return
    std_messages.Messages.create = _ORIG.pop("create")
    std_messages.AsyncMessages.create = _ORIG.pop("acreate")
    beta_messages.Messages.stream = _ORIG.pop("bstream")
    for name, (cls, attr) in _BLOCKED.items():
        if name in _ORIG:
            setattr(cls, attr, _ORIG.pop(name))


def current() -> Budget:
    return _BUDGET

