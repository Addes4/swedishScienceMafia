"""Tournament: lean loop logic, metrics, grids, and end-to-end runs against the mock API."""
import json
import os
from pathlib import Path

import pytest

from tournament import grid as grids
from tournament.context import Evaluation
from tournament.lean import Gate, parse_change, regressions
from tournament.metrics import area, incumbents, summarize

ROOT = Path(__file__).resolve().parents[1]


def _ev(public, combined=None, correct=True, tag="x"):
    return Evaluation(tag=tag, code="", combined=sum(public) / len(public) if combined is None else combined,
                      correct=correct, rejected=False, feedback="", public=list(public),
                      labels=[f"n={i}" for i in range(len(public))], sha=tag)


def test_gate_blocks_regressions_only_on_archived_instances():
    gate = Gate(True)
    parent = _ev([0.8, 0.8, 0.8])
    first = _ev([0.9, 0.7, 0.95])            # better overall, worse on instance 1
    assert gate.check(first, parent) == (True, set())   # archive empty: passes
    gate.record(first, parent)
    assert gate.archive == {1}
    second = _ev([1.0, 0.75, 1.0])           # better overall but regresses on archived instance 1
    passes, hits = gate.check(second, parent)
    assert not passes and hits == {1}
    third = _ev([0.79, 0.8, 1.0])            # regresses on 0, which is not archived yet
    assert gate.check(third, parent)[0]


def test_gate_ignores_invalid_candidates_and_can_be_disabled():
    gate = Gate(True)
    gate.record(_ev([0.0, 0.0], correct=False), _ev([0.5, 0.5]))
    assert gate.archive == set()
    off = Gate(False)
    off.record(_ev([0.1, 0.9]), _ev([0.5, 0.5]))
    assert off.check(_ev([0.0, 1.0]), _ev([0.5, 0.5])) == (True, set())


def test_regressions_and_change_parsing():
    assert regressions(_ev([0.5, 0.6]), _ev([0.5, 0.7])) == {1}
    assert parse_change("<change> use a\n hexagonal   grid </change>```python\n```") == "use a hexagonal grid"
    assert parse_change("no tags") == "(no description)"


def test_area_and_incumbents():
    # starts at 0.5, reaches 0.75 after half the budget: area = 0.5*0.5 + 0.75*0.5
    assert abs(area([(0.0, 0.5), (1.0, 0.75)], 2.0, 0.5) - 0.625) < 1e-12
    evals = [{"t": 1, "combined": 0.5, "correct": True, "sha": "a"},
             {"t": 2, "combined": 0.9, "correct": False, "sha": "b"},
             {"t": 3, "combined": 0.6, "correct": True, "sha": "c"},
             {"t": 4, "combined": 0.55, "correct": True, "sha": "d"}]
    assert [s for _, s, _ in incumbents(evals, [])] == [0.5, 0.6]
    explicit = [{"event": "incumbent", "t": 1, "score": 0.5, "sha": "a"}]
    assert [s for _, s, _ in incumbents(evals, explicit)] == [0.5]


def test_grid_expansion_and_caps():
    g = grids.load(ROOT / "experiments" / "tournament-v1" / "grids" / "mock.json")
    jobs = grids.jobs(g)
    assert len(jobs) == len(g["arms"]) * len(g["problems"]) * len(g["seeds"])
    assert len({j["job_id"] for j in jobs}) == len(jobs)
    assert all(j["mock"] for j in jobs)
    grids.check_caps(g, jobs)
    live = dict(g, mode="live", anthropic_cap_usd=1.0)
    with pytest.raises(SystemExit):
        grids.check_caps(live, grids.jobs(live))       # 16 x $0.50 > $1


@pytest.mark.parametrize("arm_config", [{"type": "lean"}, {"type": "lean", "gate": True, "patience": 2},
                                        {"type": "independent"}])
def test_lean_end_to_end_with_mock_api(tmp_path, arm_config):
    from tournament.run import main
    out = tmp_path / "run"
    cwd = os.getcwd()
    try:
        main(["--arm", "lean_test", "--arm-config", json.dumps(arm_config), "--problem", "circle_packing",
              "--seed", "4", "--budget", "0.25", "--mock", "--out", str(out)])
    finally:
        os.chdir(cwd)
        for key in ("TOURNAMENT_EVAL_LOG", "TOURNAMENT_PROBLEM_DIR"):
            os.environ.pop(key, None)
    s = json.loads((out / "summary.json").read_text())
    assert s["mock"] and s["within_cap"] and s["calls"] >= 3
    assert s["evals"] == s["calls"] + 1                 # the initial program plus one candidate per call
    assert s["final_public"] >= s["initial_public"]
    assert (out / "curve.csv").exists() and (out / "best_program.py").exists()
    assert (out / "artifacts.tar.gz").exists() and not (out / "programs").exists()
    steps = [json.loads(l) for l in open(out / "events.jsonl") if '"step"' in l]
    if arm_config.get("patience"):   # after T non-improving steps, the next step restarts
        for before, after in zip(steps, steps[1:]):
            if before.get("stall", 0) >= arm_config["patience"]:
                assert after["op"] == "restart"
    if arm_config["type"] == "independent":
        assert {e["op"] for e in steps} == {"sample"}


def test_record_flags_compare_margin_with_n_times_tolerance(tmp_path):
    from tournament.evallog import record_flags
    integrity = {"public": [{"label": "n=26", "instance": {"n": 26}, "score": 2.6359830849176076 + 1e-8,
                             "best_known": 2.6359830849176076, "flag": "exceeds best known value"},
                            {"label": "n=26", "instance": {"n": 26}, "score": 2.6359830849176076 + 1e-6,
                             "best_known": 2.6359830849176076, "flag": "exceeds best known value"}],
                 "hidden": []}
    (tmp_path / "integrity.json").write_text(json.dumps(integrity))
    flags = record_flags(ROOT / "problems" / "circle_packing", tmp_path)
    assert [f["worth_review"] for f in flags] == [False, True]          # 26 x 1e-9 = 2.6e-8
    assert flags[0]["reference"] == 2.6359830849176076 and flags[0]["tolerance"] == 1e-9


def test_independent_rejects_gate_and_patience(tmp_path):
    from tournament import lean
    from tournament.budget import Budget
    from tournament.context import Context
    ctx = Context(problem_dir=ROOT / "problems" / "circle_packing", out=tmp_path, seed=0, budget=Budget(0.1),
                  config={"independent": True, "patience": 3})
    with pytest.raises(ValueError):
        lean.run(ctx)


def test_triage_end_to_end_with_mock_api(tmp_path):
    from tournament.run import main
    out = tmp_path / "run"
    cwd = os.getcwd()
    try:
        main(["--arm", "triage", "--arm-config", json.dumps({"type": "triage", "ranker": "random", "ideas": 3}),
              "--problem", "circle_packing", "--seed", "0", "--budget", "0.4", "--mock", "--out", str(out)])
    finally:
        os.chdir(cwd)
        for key in ("TOURNAMENT_EVAL_LOG", "TOURNAMENT_PROBLEM_DIR"):
            os.environ.pop(key, None)
    s = summarize(out)
    assert s["within_cap"] and s["calls"] >= 4 and s["evals"] >= 4


def test_report_statistics():
    from tournament.report import bootstrap_p_greater, holm, sign_flip_p
    assert sign_flip_p([1.0, 1.0, 1.0]) == 2 / 8          # all positive: only the two extreme sign patterns
    assert sign_flip_p([1.0, -1.0]) == 1.0
    adj = holm({"a": 0.01, "b": 0.04, "c": 0.5})
    assert adj == {"a": 0.03, "b": 0.08, "c": 0.5}
    p, ci = bootstrap_p_greater([1.0, 0.0, -1.0, 1.0])
    assert p == (2 + 0.5) / 4 and ci[0] <= p <= ci[1]
