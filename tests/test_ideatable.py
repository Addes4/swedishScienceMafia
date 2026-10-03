"""Idea table: spend cap, dedupe, end-to-end mock run, and the offline policy evaluation.

Run with:  python -m pytest tests/test_ideatable.py -q   (no network; uses MockClaude)
"""
import json

import numpy as np
import pytest

from autoresearch.claude import CallResult
from autoresearch.ideatable import CodexRanker, IdeaTable, classify, dedupe, parse_rankings
from autoresearch.policy_eval import Data, Draw, analyse, auc, data_summary, kappa, report, tiers, topk
from autoresearch.spend import BudgetExceeded, CappedClaude, SpendLedger, worst_case_cost


class FixedClient:
    def __init__(self, cost=0.01, fail=False):
        self.cost, self.fail = cost, fail

    def call(self, model, system, user, max_tokens=32000, effort=None):
        if self.fail:
            raise RuntimeError("boom")
        return CallResult(text="ok", model=model, cost=self.cost, input_tokens=10, output_tokens=10, seconds=0.0)


def test_worst_case_covers_full_output_and_fallback():
    wc = worst_case_cost("claude-opus-5-5", "s" * 100, "u" * 100, 32000)
    assert wc >= 32000 * 20 / 1e6 + 32000 * 25 / 1e6       # own price plus fallback price
    assert worst_case_cost("claude-haiku-4-5", "", "", 1000) >= 1000 * 5 / 1e6


def test_ledger_refuses_and_logs(tmp_path):
    ledger = SpendLedger(cap=0.05, path=tmp_path / "usage.jsonl")
    claude = CappedClaude(FixedClient(cost=0.001), ledger)
    with claude.tagged("t1"):
        claude.call("claude-haiku-4-5", "s", "u", max_tokens=1000)   # worst case ~$0.005: allowed
    with pytest.raises(BudgetExceeded):
        claude.call("claude-opus-5-5", "s", "u", max_tokens=32000)   # worst case > $0.05: refused before sending
    failing = CappedClaude(FixedClient(fail=True), ledger)
    with pytest.raises(RuntimeError):
        failing.call("claude-haiku-4-5", "s", "u", max_tokens=1000)
    rows = [json.loads(l) for l in (tmp_path / "usage.jsonl").read_text().splitlines()]
    assert [r["ok"] for r in rows] == [True, False]                  # refused call never sent, failure logged
    assert rows[0]["tag"] == "t1" and rows[0]["cost"] == 0.001
    assert SpendLedger(cap=0.05, path=tmp_path / "usage.jsonl").spent == pytest.approx(0.001)  # persists


def test_dedupe_drops_near_copies():
    kept, dropped = dedupe(["Use simulated annealing on positions.", "use SIMULATED annealing on positions",
                            "Rotate squares by 45 degrees."])
    assert kept == ["Use simulated annealing on positions.", "Rotate squares by 45 degrees."]
    assert dropped[0]["dup_of"] == "Use simulated annealing on positions."


def test_classify_matches_triage_rules():
    rec = {"status": "pending_eval"}
    ev = lambda score, correct=True, rej=0, static=False: {
        "metrics": {"combined_score": score, "private": {"integrity_rejections": rej, "hidden_mean": 0.9,
                                                         **({"integrity": "static"} if static else {})}},
        "correct": {"correct": correct}}
    assert classify(rec, ev(0.9), 0.856)["outcome"] == "improved"
    assert classify(rec, ev(0.856 + 1e-10), 0.856)["outcome"] == "not_better"
    assert classify(rec, ev(0.9, correct=False), 0.856)["outcome"] == "invalid"
    assert classify(rec, ev(0.0, correct=False, rej=1), 0.856)["outcome"] == "rejected"
    assert classify(rec, ev(0.0, correct=False, static=True), 0.856)["outcome"] == "rejected"
    assert classify({"status": "no_code"}, None, 0.856)["outcome"] == "no_code"


def test_parse_rankings_is_robust():
    r = parse_rankings('junk [{"promise": "favourite", "p_improve": 1.7}, {"promise": "?"}] tail', 3)
    assert r[0].promise["favourite"] == 1.0 and r[0].p_improve == 1.0
    assert r[1].promise["middle"] == 1.0 and r[2].p_improve == 0.5 and not r[2].raw["parsed"]
    odd = parse_rankings('[{"promise": ["favourite"], "kind": ["bug_fix"], "p_improve": "x", "p_repeat": null}]', 1)
    assert odd[0].kind == "other" and odd[0].promise["middle"] == 1.0 and odd[0].p_improve == 0.5
    ranker = CodexRanker(runner=lambda prompt: '[{"promise": "long_shot", "p_improve": 0.1}]')
    out = ranker.rank("problem", 0.5, "code", [], ["idea a"])
    assert out[0].promise["long_shot"] == 1.0 and out[0].key < 0.5


def test_kappa():
    assert kappa([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0
    assert kappa([1, 1, 0, 0], [1, 0, 1, 0]) == 0.0
    assert np.isnan(kappa([1, 1], [1, 1]))


def test_auc_and_policies():
    assert auc([0.1, 0.2, 0.9, 0.8], [0, 0, 1, 1]) == 1.0
    assert auc([1, 1, 1, 1], [0, 1, 0, 1]) == 0.5
    assert np.isnan(auc([0.1, 0.2], [1, 1]))

    class D:
        batches = [np.arange(6)]
        tie = np.zeros(6)
        swap_u = np.ones(6)
        idx = np.arange(6)
    key = np.array([0.1, 0.9, 0.5, 0.3, 0.8, 0.0])
    assert list(tiers(D, key)) == [0, 2, 1, 1, 2, 0]   # top two -> opus (2), middle -> sonnet, bottom -> haiku
    assert list(topk(D, key, 1)) == [-1, 2, -1, -1, -1, -1]


def test_end_to_end_mock(tmp_path):
    t = IdeaTable(tmp_path / "exp", mock=True, cap=40.0)
    state = t.generate_ideas(calls=2, k=6)
    assert len(state["ideas"]) >= 6 and state["dropped"]          # the mock emits one near-duplicate
    assert sorted(d["order"] for d in state["ideas"]) == list(range(len(state["ideas"])))
    t.implement(t.main_cells(0, 6) + t.replicate_cells(6, 3), workers=3)
    t.run_rankers(["random", "claude-haiku-4-5", "claude-opus-5-5"], n=6)
    with pytest.raises(SystemExit):
        t.run_rankers(["random"], n=5)                            # rankings are tied to one idea set
    t.evaluate_pending(host="local", workers=2, eval_replicates=2)
    rows = t.build_table()
    assert len(rows) == 6 * 3 + 3
    assert {r["outcome"] for r in rows} <= {"improved", "not_better", "invalid", "rejected", "no_code", "refused"}
    assert all(r["score"] is not None for r in rows if r["outcome"] in ("improved", "not_better", "invalid"))
    assert sum(bool(r.get("eval_repeat")) for r in rows) == 2
    usage = [json.loads(l) for l in (tmp_path / "exp" / "usage.jsonl").read_text().splitlines()]
    assert len(usage) == 2 + 18 + 3 + 2                           # ideas, cells, replicates, ranker batches
    assert t.ledger.spent == pytest.approx(sum(u["cost"] for u in usage))

    # resuming does not repeat finished work
    n_before = len(usage)
    t.implement(t.main_cells(0, 6), workers=3)
    assert len((tmp_path / "exp" / "usage.jsonl").read_text().splitlines()) == n_before

    data = Data(tmp_path / "exp", extra_rankings={"perfect": {"meta": {"cost": 0.0}, "ideas": {
        r["idea_id"]: {"key": float(r["improved"]), "p_improve": float(r["improved"])}
        for r in rows if r["model"] == "claude-opus-5-5" and r["replicate"] == 0}}})
    draw = Draw(data, np.random.default_rng(0), resample=False)
    assert draw.imp.shape == (6, 3)
    result = analyse(data, n_boot=30, n_point=10, seed=1)
    assert set(result["policies"]) >= {"uniform:opus", "tiers:random", "tiers:claude-opus-5-5", "top2-opus:perfect"}
    for r in result["rankers"].values():
        a = r["auc_opus"]["mean"]
        assert np.isnan(a) or 0.0 <= a <= 1.0
    md = report(result, data_summary(data))
    assert "Policies over the whole pool" in md
