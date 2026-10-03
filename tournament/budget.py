"""A hard dollar cap for every Anthropic call made in one process.

Before a request is sent, its worst-case cost is reserved:

    input upper bound x input price  +  max_tokens x output price

The input upper bound is the UTF-8 byte length of the JSON-encoded system prompt and messages
plus a margin (a token is never shorter than one byte). If the reservation does not fit in what
is left of the cap (after money already spent and money reserved by calls still in flight),
the caller first waits for calls in flight to settle (their reservations are worst cases). With
nothing in flight, max_tokens is lowered to what fits; below a floor the budget is exhausted and
the call is refused.

After the call, the reservation is replaced by the cost of the usage the API reported. A call
that fails with an HTTP error status is charged nothing (errors are not billed). A call that
fails any other way (timeout, dropped connection, unfinished stream) is charged its full
reservation, because what was billed is unknown; this keeps the cap a hard guarantee.

Every call, refusal and failure is appended to usage.jsonl.
"""
import asyncio
import itertools
import json
import math
import threading
import time
from dataclasses import dataclass
from typing import Optional

from autoresearch.claude import PRICES

INPUT_MARGIN_TOKENS = 2000
DEFAULT_MIN_OUTPUT_TOKENS = 2048


class BudgetExhausted(RuntimeError):
    """The cap cannot pay for another call."""


class FatalAPIError(BudgetExhausted):
    """The API refused for a reason retrying cannot fix (no credit, bad key, no permission).

    A subclass of BudgetExhausted so every arm stops exactly as it does at the end of its budget;
    the run's status records the difference. After it, no call in the process is sent again.
    """


class UnbudgetedCall(RuntimeError):
    """A call path or model the guard cannot bound; refused rather than sent."""


def input_upper_bound(system, messages) -> int:
    raw = json.dumps({"system": system, "messages": messages}, default=str, ensure_ascii=False)
    return len(raw.encode("utf-8")) + INPUT_MARGIN_TOKENS


# $ per million tokens (input, output) for models outside autoresearch.claude.PRICES, registered at run
# start from the provider's own price list (e.g. the Hugging Face router's /v1/models).
EXTRA_PRICES = {}


def register_prices(prices: dict) -> None:
    EXTRA_PRICES.update({m: (float(i), float(o)) for m, (i, o) in prices.items()})


def known_price(model: str) -> bool:
    return model in EXTRA_PRICES or model in PRICES


def per_token_prices(model: str):
    if model in EXTRA_PRICES:
        pin, pout = EXTRA_PRICES[model]
    elif model in PRICES:
        pin, pout = PRICES[model]
    else:
        raise UnbudgetedCall(f"no price known for model {model!r}; refusing to call it")
    return pin / 1e6, pout / 1e6


def usage_cost(model: str, usage) -> float:
    """Same formula as autoresearch.claude._cost: cache reads at 0.1x, cache writes at 1.25x input."""
    pin, pout = per_token_prices(model)
    get = (lambda k: usage.get(k) or 0) if isinstance(usage, dict) else (lambda k: getattr(usage, k, 0) or 0)
    return (get("input_tokens") * pin + get("output_tokens") * pout
            + get("cache_read_input_tokens") * pin * 0.1 + get("cache_creation_input_tokens") * pin * 1.25)


@dataclass
class Reservation:
    id: int
    model: str
    requested_max_tokens: int
    granted_max_tokens: int
    input_upper: int
    amount: float
    t0: float


class Budget:
    def __init__(self, cap_usd: float, usage_path=None, min_output_tokens: int = DEFAULT_MIN_OUTPUT_TOKENS,
                 wait_poll_s: float = 0.25):
        self.cap = float(cap_usd)
        self.usage_path = usage_path
        self.min_output_tokens = min_output_tokens
        self.wait_poll_s = wait_poll_s
        self.spent = 0.0
        self.external = 0.0              # non-Anthropic costs (e.g. the Jev ranker), counted against the cap
        self.reserved = {}
        self.calls = 0
        self.refusals = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.exhausted = False
        self.fatal = None                # reason, once the API has refused fatally
        self._cond = threading.Condition()
        self._ids = itertools.count(1)

    # -- reservation ---------------------------------------------------------------------------
    def _try_reserve(self, model, max_tokens, input_upper):
        """With the lock held: a Reservation, None (wait for in-flight calls) or False (exhausted)."""
        pin, pout = per_token_prices(model)
        free = self.cap - self.spent - self.external - sum(self.reserved.values()) - input_upper * pin
        afford = int(math.floor(free / pout)) if free > 0 else 0
        if afford >= max_tokens:
            granted = max_tokens
        elif self.reserved:
            # Reservations are worst cases; calls in flight usually settle far below them. Wait rather
            # than truncate, so parallel arms are not handicapped before their budget is really used.
            return None
        elif afford >= min(max_tokens, self.min_output_tokens):
            granted = afford              # the true end of the budget: shrink the last call to fit
        else:
            self.exhausted = True
            return False
        rid = next(self._ids)
        amount = input_upper * pin + granted * pout
        self.reserved[rid] = amount
        return Reservation(rid, model, max_tokens, granted, input_upper, amount, time.time())

    def _refuse(self, model, max_tokens, input_upper, path, why):
        self.refusals += 1
        if self.fatal:
            why = f"fatal API error earlier ({self.fatal})"
        self._write({"event": "refused", "model": model, "path": path, "requested_max_tokens": max_tokens,
                     "input_upper": input_upper, "reason": why})
        cls = FatalAPIError if self.fatal else BudgetExhausted
        return cls(f"{why} (spent ${self.spent:.4f} of ${self.cap:.2f})")

    def mark_fatal(self, reason: str):
        """Stop all further calls in this process: they are refused locally and never sent."""
        with self._cond:
            if self.fatal is None:
                self.fatal = reason
                self._write({"event": "fatal", "reason": reason})
            self.exhausted = True
            self._cond.notify_all()

    def reserve(self, model: str, max_tokens: int, input_upper: int, path: str = "") -> Reservation:
        with self._cond:
            while True:
                if self.exhausted:
                    raise self._refuse(model, max_tokens, input_upper, path, "budget exhausted")
                res = self._try_reserve(model, max_tokens, input_upper)
                if res:
                    return res
                if res is False:
                    raise self._refuse(model, max_tokens, input_upper, path, "cap cannot pay for another call")
                self._cond.wait(timeout=self.wait_poll_s)

    async def reserve_async(self, model: str, max_tokens: int, input_upper: int, path: str = "") -> Reservation:
        while True:
            with self._cond:
                if self.exhausted:
                    raise self._refuse(model, max_tokens, input_upper, path, "budget exhausted")
                res = self._try_reserve(model, max_tokens, input_upper)
                if res:
                    return res
                if res is False:
                    raise self._refuse(model, max_tokens, input_upper, path, "cap cannot pay for another call")
            await asyncio.sleep(self.wait_poll_s)

    # -- settlement ----------------------------------------------------------------------------
    def settle(self, res: Reservation, usage=None, served_model: Optional[str] = None, error: Optional[BaseException] = None,
               charge_reservation: bool = False, stop_reason=None, path: str = "", extra: Optional[dict] = None) -> float:
        get = (lambda k: usage.get(k) or 0) if isinstance(usage, dict) else (lambda k: getattr(usage, k, 0) or 0)
        with self._cond:
            self.reserved.pop(res.id, None)
            if usage is not None:
                model = served_model if served_model and known_price(served_model) else res.model
                cost, basis = usage_cost(model, usage), "usage"
            elif charge_reservation:
                cost, basis = res.amount, "reservation"
            else:
                cost, basis = 0.0, "none"
            self.spent += cost
            self.calls += 1
            if usage is not None:
                self.input_tokens += get("input_tokens") + get("cache_read_input_tokens") + get("cache_creation_input_tokens")
                self.output_tokens += get("output_tokens")
            rec = {"event": "call", "call": res.id, "model": res.model, "served_by": served_model, "path": path,
                   "requested_max_tokens": res.requested_max_tokens, "granted_max_tokens": res.granted_max_tokens,
                   "input_upper": res.input_upper, "reserved_usd": round(res.amount, 6),
                   "input_tokens": get("input_tokens") if usage is not None else None,
                   "output_tokens": get("output_tokens") if usage is not None else None,
                   "cache_read_input_tokens": get("cache_read_input_tokens") if usage is not None else None,
                   "cache_creation_input_tokens": get("cache_creation_input_tokens") if usage is not None else None,
                   "cost_usd": round(cost, 6), "cost_basis": basis, "over_reservation": cost > res.amount + 1e-9,
                   "stop_reason": stop_reason, "seconds": round(time.time() - res.t0, 3),
                   "error": None if error is None else f"{type(error).__name__}: {str(error)[:300]}"}
            if extra:
                rec.update(extra)
            self._write(rec)
            self._cond.notify_all()
        return cost

    def log_event(self, rec: dict):
        with self._cond:
            self._write(rec)

    def charge_external(self, amount: float, label: str):
        """Costs paid to other APIs (e.g. Jev). Counted against the cap after the fact."""
        with self._cond:
            self.external += amount
            self._write({"event": "external", "label": label, "cost_usd": round(amount, 8)})

    # -- reporting -----------------------------------------------------------------------------
    @property
    def total(self) -> float:
        return self.spent + self.external

    def snapshot(self) -> dict:
        with self._cond:
            return {"cap_usd": self.cap, "spent_usd": round(self.spent, 6), "external_usd": round(self.external, 8),
                    "calls": self.calls, "refusals": self.refusals, "input_tokens": self.input_tokens,
                    "output_tokens": self.output_tokens, "exhausted": self.exhausted, "fatal": self.fatal,
                    "in_flight": len(self.reserved)}

    def _write(self, rec: dict):
        rec = {"t": time.time(), **rec, "spent_usd": round(self.spent + self.external, 6)}
        if self.usage_path:
            with open(self.usage_path, "a") as f:
                f.write(json.dumps(rec, default=str) + "\n")
