"""Tournament budget guard: hard dollar cap, usage logging, blocked call paths. Uses the local
mock API only (no network, no cost)."""
import asyncio
import json
import threading

import anthropic
import pytest

from autoresearch.claude import Claude
from tournament import guard
from tournament.budget import Budget, BudgetExhausted, UnbudgetedCall, input_upper_bound, usage_cost
from tournament.mockapi import MockAnthropic

PROGRAM = "```python\n# EVOLVE-BLOCK-START\ndef solve(n):\n    return 0.5 * n\n# EVOLVE-BLOCK-END\n```"


@pytest.fixture
def mock():
    with MockAnthropic(seed=3, latency=0.0) as m:
        yield m
    guard.uninstall()


def _usage(path):
    return [json.loads(line) for line in open(path)]


def test_cap_is_never_exceeded_and_every_call_is_logged(tmp_path, mock):
    budget = Budget(0.25, tmp_path / "usage.jsonl")
    guard.install(budget)
    claude = Claude()
    calls = 0
    with pytest.raises(BudgetExhausted):
        while True:
            res = claude.call("claude-sonnet-5-5", "system", "Improve this:\n" + PROGRAM, max_tokens=32000, effort="high")
            assert res.text and "def solve" in res.text
            calls += 1
    assert calls >= 3
    assert budget.spent <= budget.cap + 1e-12
    log = _usage(tmp_path / "usage.jsonl")
    done = [r for r in log if r["event"] == "call"]
    assert len(done) == calls
    assert log[-1]["event"] == "refused"
    assert abs(sum(r["cost_usd"] for r in done) - budget.spent) < 1e-5
    # Near the end of the budget max_tokens is lowered so the worst case still fits.
    assert any(r["granted_max_tokens"] < r["requested_max_tokens"] for r in done)
    assert all(not r["over_reservation"] for r in done)
    # Once exhausted, nothing more is sent.
    sent = mock.requests
    with pytest.raises(BudgetExhausted):
        claude.call("claude-haiku-4-5", "s", "u", max_tokens=1000)
    assert mock.requests == sent


def test_fallbacks_are_stripped(tmp_path, mock):
    guard.install(Budget(1.0, tmp_path / "usage.jsonl"))
    Claude().call("claude-opus-5-5", "s", "hello", max_tokens=4000)
    assert mock.log[-1]["has_fallbacks"] is False
    assert _usage(tmp_path / "usage.jsonl")[-1]["fallback_stripped"] is True


def test_sync_and_async_create_are_budgeted(tmp_path, mock):
    budget = Budget(1.0, tmp_path / "usage.jsonl")
    guard.install(budget)
    msg = anthropic.Anthropic(timeout=900).messages.create(
        model="claude-sonnet-5-5", max_tokens=16000, system="s", messages=[{"role": "user", "content": PROGRAM}])
    assert [b.type for b in msg.content] == ["thinking", "text"]

    async def go():
        client = anthropic.AsyncAnthropic(timeout=900)
        return await client.messages.create(model="claude-haiku-4-5", max_tokens=8000,
                                            messages=[{"role": "user", "content": "hi"}])
    asyncio.run(go())
    log = _usage(tmp_path / "usage.jsonl")
    assert [r["path"] for r in log] == ["messages.create", "messages.create(async)"]
    assert abs(budget.spent - sum(r["cost_usd"] for r in log)) < 1e-5


def test_unbudgeted_paths_and_unknown_models_are_refused(tmp_path, mock):
    guard.install(Budget(1.0, tmp_path / "usage.jsonl"))
    client = anthropic.Anthropic(timeout=900)
    with pytest.raises(UnbudgetedCall):
        client.messages.stream(model="claude-sonnet-5-5", max_tokens=100, messages=[{"role": "user", "content": "x"}])
    with pytest.raises(UnbudgetedCall):
        client.beta.messages.create(model="claude-sonnet-5-5", max_tokens=100, messages=[{"role": "user", "content": "x"}])
    with pytest.raises(UnbudgetedCall):
        client.messages.create(model="claude-mystery-9", max_tokens=100, messages=[{"role": "user", "content": "x"}])
    assert mock.requests == 0


def test_parallel_callers_wait_for_in_flight_calls(tmp_path, mock):
    mock.latency = 0.05
    budget = Budget(0.4, tmp_path / "usage.jsonl")
    guard.install(budget)
    errors = []

    def worker():
        claude = Claude()
        try:
            while True:
                claude.call("claude-sonnet-5-5", "s", PROGRAM, max_tokens=32000)
        except BudgetExhausted:
            pass
        except Exception as e:  # pragma: no cover - reported below
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert not errors
    assert budget.spent <= budget.cap + 1e-12
    assert budget.spent > 0.6 * budget.cap   # shrink-to-fit uses most of the budget
    assert not budget.reserved
    # Parallel calls wait for in-flight reservations instead of being truncated; only calls made
    # when the remaining budget cannot cover one full worst case are shortened.
    worst = 32000 * 10 / 1e6
    for r in _usage(tmp_path / "usage.jsonl"):
        if r["event"] == "call" and r["granted_max_tokens"] < r["requested_max_tokens"]:
            assert r["spent_usd"] - r["cost_usd"] > budget.cap - worst - 0.05


def test_failed_status_is_free_and_unknown_failures_charge_the_reservation(tmp_path):
    budget = Budget(1.0, tmp_path / "usage.jsonl")
    res = budget.reserve("claude-sonnet-5-5", 1000, 500)
    budget.settle(res, error=RuntimeError("timeout"), charge_reservation=True)
    assert abs(budget.spent - res.amount) < 1e-12
    res2 = budget.reserve("claude-sonnet-5-5", 1000, 500)
    budget.settle(res2, error=RuntimeError("400"), charge_reservation=False)
    assert abs(budget.spent - res.amount) < 1e-12


def test_input_bound_and_cost_formula():
    assert input_upper_bound("ab", [{"role": "user", "content": "é"}]) > len("ab")
    cost = usage_cost("claude-sonnet-5-5", {"input_tokens": 1_000_000, "output_tokens": 100_000})
    assert abs(cost - (2.0 + 1.0)) < 1e-9


def test_rate_limits_are_retried_free_and_logged(tmp_path, mock, monkeypatch):
    fast = lambda e, attempt, waited: (0.01 if getattr(e, "status_code", None) in guard.RETRY_STATUSES
                                       and attempt < 20 else None)
    monkeypatch.setattr(guard, "_retry_delay", fast)
    budget = Budget(1.0, tmp_path / "usage.jsonl")
    guard.install(budget)
    mock.fail_next, mock.fail_status = 7, 529      # more failures than the SDK's own retries absorb
    assert Claude().call("claude-sonnet-5-5", "s", PROGRAM, max_tokens=8000).text
    mock.fail_next, mock.fail_status = 4, 429
    anthropic.Anthropic(timeout=900, max_retries=1).messages.create(
        model="claude-haiku-4-5", max_tokens=4000, messages=[{"role": "user", "content": "hi"}])
    log = _usage(tmp_path / "usage.jsonl")
    assert sum(r["event"] == "retry" for r in log) >= 2
    calls = [r for r in log if r["event"] == "call"]
    assert len(calls) == 2 and all(r["error"] is None and r["cost_basis"] == "usage" for r in calls)
    assert not budget.reserved
