"""Hugging Face router path: prices from /v1/models, budget guard on the openai SDK, reasoning tokens,
fatal credit errors. Uses the local mock only (no network, no cost)."""
import asyncio
import json
import types

import openai
import pytest

from tournament import hf
from tournament.budget import Budget, BudgetExhausted, FatalAPIError, register_prices
from tournament.mockapi import MOCK_HF_PRICES, MockAnthropic

FLASH = "deepseek-ai/DeepSeek-V4.1-Flash:deepinfra"
PROGRAM = "```python\n# EVOLVE-BLOCK-START\ndef solve(n):\n    return 0.5 * n\n# EVOLVE-BLOCK-END\n```"


@pytest.fixture
def mock():
    with MockAnthropic(seed=5, latency=0.0) as m:
        register_prices(hf.fetch_prices(list(MOCK_HF_PRICES)))
        yield m
    hf.uninstall()


def _usage(path):
    return [json.loads(line) for line in open(path)]


def test_prices_come_from_the_router_listing(mock):
    assert hf.fetch_prices([FLASH]) == {FLASH: MOCK_HF_PRICES[FLASH]}
    with pytest.raises(SystemExit):
        hf.fetch_prices(["deepseek-ai/DeepSeek-V4.1-Flash:unlisted-provider"])


def test_cap_holds_and_usage_is_logged(tmp_path, mock):
    budget = Budget(0.02, tmp_path / "usage.jsonl")
    hf.install(budget)
    client = hf.HFClient()
    n = with_code = 0
    with pytest.raises(BudgetExhausted):
        while True:
            res = client.call(FLASH, "system", "Improve:\n" + PROGRAM, max_tokens=32000)
            with_code += "def solve" in res.text     # the last, shortened call may come back empty
            n += 1
    assert with_code >= 3 and budget.spent <= budget.cap + 1e-12
    calls = [r for r in _usage(tmp_path / "usage.jsonl") if r["event"] == "call"]
    assert len(calls) == n and all(r["path"] == "chat.completions.create" for r in calls)


def test_reasoning_reported_on_top_of_completion_is_counted():
    included = types.SimpleNamespace(completion_tokens=900, completion_tokens_details=types.SimpleNamespace(reasoning_tokens=700))
    on_top = types.SimpleNamespace(completion_tokens=200, completion_tokens_details=types.SimpleNamespace(reasoning_tokens=700))
    assert hf.output_tokens(included) == 900
    assert hf.output_tokens(on_top) == 900


@pytest.mark.parametrize("status,message", [(402, "Payment required"), (401, "Invalid credentials"),
                                            (403, "forbidden"), (400, "You have insufficient credits")])
def test_credit_and_auth_errors_are_fatal(tmp_path, mock, status, message):
    budget = Budget(1.0, tmp_path / "usage.jsonl")
    hf.install(budget)
    mock.fail_next, mock.fail_status, mock.fail_message = 1000, status, message
    with pytest.raises(FatalAPIError):
        hf.HFClient().call(FLASH, "s", PROGRAM, max_tokens=8000)
    assert mock.failed == 1 and budget.fatal and budget.spent == 0.0

    async def again():
        client = openai.AsyncOpenAI(base_url=hf.base_url(), api_key="x")
        await client.chat.completions.create(model=FLASH, max_tokens=100, messages=[{"role": "user", "content": "hi"}])
    with pytest.raises(FatalAPIError):     # ShinkaEvolve's async path is refused without sending
        asyncio.run(again())
    assert mock.failed == 1


def test_rate_limits_are_retried(tmp_path, mock, monkeypatch):
    monkeypatch.setattr(hf, "_retry_delay", lambda e, a, w: 0.01 if getattr(e, "status_code", 0) == 429 and a < 10 else None)
    budget = Budget(1.0, tmp_path / "usage.jsonl")
    hf.install(budget)
    mock.fail_next, mock.fail_status = 5, 429
    assert hf.HFClient().call(FLASH, "s", PROGRAM, max_tokens=8000).text
    log = _usage(tmp_path / "usage.jsonl")
    assert any(r["event"] == "retry" for r in log) and not budget.fatal


def test_unbounded_requests_are_refused(tmp_path, mock):
    hf.install(Budget(1.0, tmp_path / "usage.jsonl"))
    client = openai.OpenAI(base_url=hf.base_url(), api_key="x")
    with pytest.raises(Exception):
        client.chat.completions.create(model=FLASH, messages=[{"role": "user", "content": "hi"}])   # no max_tokens
    assert mock.requests == 0
