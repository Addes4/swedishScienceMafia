"""Hard spend cap for Claude calls, enforced before each request is sent.

Before a request goes out, its worst-case cost is reserved: prompt tokens (estimated
generously from the prompt length) plus `max_tokens` of output, at the highest price the
call could be billed at (requests that opt into the server-side refusal fallback can be
billed for the declined attempt *and* the fallback model's answer, so both are reserved).
If the reservation could take total spend over the cap, the call is refused with
BudgetExceeded. After the call the reservation is replaced by the actual cost.

Every call is appended to usage.jsonl, including failures and refusals. Spend already in
usage.jsonl counts against the cap, so separate invocations share one budget.

    ledger = SpendLedger(cap=40.0, path="experiments/x/usage.jsonl")
    claude = CappedClaude(Claude(), ledger)
    with claude.tagged("implement/i003/claude-opus-5-5/r0"):
        res = claude.call("claude-opus-5-5", system, user, max_tokens=32000, effort="high")
"""
import contextlib
import gzip
import json
import threading
import time
from pathlib import Path
from typing import Optional

from .claude import _FALLBACK_MODELS, PRICES

# Characters per token used to over-estimate prompt size (real text is ~3.5-4.5 chars/token).
CHARS_PER_TOKEN_LOWER_BOUND = 2.0
# Price the server-side fallback could bill at (the most expensive non-Fable model in PRICES).
FALLBACK_PRICE = max((p for m, p in PRICES.items() if "fable" not in m), key=lambda p: p[1])


class BudgetExceeded(RuntimeError):
    pass


def worst_case_cost(model: str, system: str, user: str, max_tokens: int) -> float:
    pin, pout = PRICES.get(model, max(PRICES.values(), key=lambda p: p[1]))
    tokens_in = (len(system) + len(user)) / CHARS_PER_TOKEN_LOWER_BOUND + 50
    cost = tokens_in * pin + max_tokens * pout
    if model in _FALLBACK_MODELS:
        fin, fout = FALLBACK_PRICE
        cost += tokens_in * fin + max_tokens * fout
    return cost / 1e6


class SpendLedger:
    """Thread-safe running total of spend plus in-flight reservations, backed by usage.jsonl."""

    def __init__(self, cap: float, path):
        self.cap = float(cap)
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.spent = self._logged()
        self.reserved = 0.0
        self._cv = threading.Condition()

    def _logged(self) -> float:
        """Total cost in usage.jsonl, which other processes sharing the folder also append to."""
        if not self.path.exists():
            return 0.0
        total = 0.0
        for line in self.path.read_text().splitlines():
            if line.strip():
                try:
                    total += float(json.loads(line).get("cost") or 0.0)
                except ValueError:      # a line another process is still writing
                    pass
        return total

    @property
    def remaining(self) -> float:
        return self.cap - self.spent

    def reserve(self, amount: float, wait: bool = True) -> None:
        """Reserve `amount` dollars. If other reservations are in flight and the sum would
        exceed the cap, wait for them to settle; refuse if it cannot fit even alone."""
        with self._cv:
            self.spent = max(self.spent, self._logged())   # include spend settled by other processes
            while self.spent + self.reserved + amount > self.cap + 1e-12:
                if self.reserved <= 1e-12 or not wait:
                    raise BudgetExceeded(
                        f"reserving ${amount:.4f} would exceed the ${self.cap:.2f} cap "
                        f"(spent ${self.spent:.4f}, in flight ${self.reserved:.4f})")
                self._cv.wait(timeout=5.0)
            self.reserved += amount

    def settle(self, reserved: float, entry: dict) -> None:
        """Release a reservation, add the actual cost and append the entry to usage.jsonl."""
        with self._cv:
            self.reserved = max(0.0, self.reserved - reserved)
            with open(self.path, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")
            self.spent = self._logged()
            self._cv.notify_all()


class CappedClaude:
    """Drop-in replacement for autoresearch.claude.Claude that enforces a SpendLedger.

    `call` has the same signature as Claude.call, so rankers and the triage code can use it.
    The tag of the current thread (set with `tagged`) labels each usage row and trace file.
    """

    def __init__(self, inner, ledger: SpendLedger, trace_dir=None):
        self.inner = inner
        self.ledger = ledger
        self.trace_dir = Path(trace_dir) if trace_dir else None
        self._local = threading.local()

    @contextlib.contextmanager
    def tagged(self, tag: str):
        old = getattr(self._local, "tag", None)
        self._local.tag = tag
        try:
            yield self
        finally:
            self._local.tag = old

    @property
    def last(self):
        """The CallResult of this thread's most recent call (None if it raised)."""
        return getattr(self._local, "last", None)

    def call(self, model: str, system: str, user: str, max_tokens: int = 32000, effort: Optional[str] = None):
        tag = getattr(self._local, "tag", None) or "untagged"
        self._local.last = None
        reserve = worst_case_cost(model, system, user, max_tokens)
        self.ledger.reserve(reserve)
        entry = {"time": time.time(), "tag": tag, "model": model, "effort": effort, "max_tokens": max_tokens,
                 "reserved": round(reserve, 6)}
        try:
            res = self.inner.call(model, system, user, max_tokens=max_tokens, effort=effort)
        except Exception as e:
            # The request may have failed before or during generation; partial streams are not
            # reported back, so the cost is unknown (recorded as 0 and flagged).
            entry.update(ok=False, cost=0.0, cost_known=False, error=f"{type(e).__name__}: {str(e)[:300]}")
            self.ledger.settle(reserve, entry)
            raise
        entry.update(ok=True, cost=round(res.cost, 6), cost_known=True, served_by=res.served_by,
                     input_tokens=res.input_tokens, output_tokens=res.output_tokens,
                     seconds=round(res.seconds, 2), refused=res.refused)
        self.ledger.settle(reserve, entry)
        self._local.last = res
        if self.trace_dir is not None:
            self.trace_dir.mkdir(parents=True, exist_ok=True)
            safe = tag.replace("/", "__")
            path, n = self.trace_dir / f"{safe}.json.gz", 1
            while path.exists():
                path, n = self.trace_dir / f"{safe}.{n}.json.gz", n + 1
            with gzip.open(path, "wt") as f:
                json.dump({"usage": entry, "system": system, "user": user, "response": res.text}, f)
        return res
