"""The one-command loop (autoresearch/loop.py) and its explanation step (autoresearch/explain_code.py).
Mock API only: no network, no cost."""
import json
import os
from pathlib import Path

import pytest

from autoresearch import explain_code as ex
from autoresearch.loop import main

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """main() sets GATE_WORKERS; tournament.run changes directory. Undo both after each test."""
    for key in ("GATE_WORKERS", "GATE_TIMEOUT_S", "TOURNAMENT_EVAL_LOG", "TOURNAMENT_PROBLEM_DIR"):
        monkeypatch.delenv(key, raising=False)
    cwd = os.getcwd()
    yield
    os.chdir(cwd)


def test_mock_run_on_erdos_squares_writes_the_report(tmp_path):
    out = tmp_path / "run"
    assert main([str(ROOT / "problems" / "erdos_squares"), "--mock", "--max-iters", "4", "--explain-evals", "12",
                 "--gate-workers", "4", "--out", str(out)]) == 0
    for name in ("report.md", "summary.json", "best_program.py", "job.json", "loop.json", "baselines.json", "explain.json"):
        assert (out / name).exists(), name
    job = json.loads((out / "job.json").read_text())
    s = json.loads((out / "summary.json").read_text())
    assert job["mock"] is True and job["arm_config"] == {"type": "lean", "gate": True, "max_iters": 4,
                                                         "model": "deepseek-ai/DeepSeek-V4.1-Flash:deepinfra",
                                                         "patience": None}
    assert s["within_cap"] and s["calls"] == 4 and s["initial_hidden"] is not None
    report = (out / "report.md").read_text()
    assert "| program | public | hidden | note |" in report and "$0 real" in report
    assert "## Explanation" in report and "python -m autoresearch.loop" in report
    assert "TOURNAMENT_EVAL_LOG" not in os.environ

    (out / "report.md").unlink()                       # --report rebuilds it from the saved files
    assert main(["--report", str(out)]) == 0
    assert (out / "report.md").read_text() == report


@pytest.mark.slow
def test_mock_run_on_bin_packing_scores_the_baselines(tmp_path):
    out = tmp_path / "run"
    main([str(ROOT / "problems" / "bin_packing_online"), "--mock", "--max-iters", "2", "--out", str(out)])
    base = {b["name"]: b for b in json.loads((out / "baselines.json").read_text())}
    assert set(base) == {"funsearch_or", "funsearch_weibull"}
    assert base["funsearch_weibull"]["public"] == pytest.approx(0.9925, abs=1e-3)    # bp-ceiling-v1's reference
    assert all(b["valid"] and b["hidden"] is not None for b in base.values())
    assert "baseline `funsearch_weibull`" in (out / "report.md").read_text()


def test_live_run_needs_a_budget(tmp_path):
    with pytest.raises(SystemExit):
        main([str(ROOT / "problems" / "erdos_squares"), "--out", str(tmp_path / "run")])
    assert not (tmp_path / "run").exists()


def test_an_existing_run_is_never_overwritten(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    (out / "keep.txt").write_text("earlier run")
    with pytest.raises(SystemExit, match="already exists"):
        main([str(ROOT / "problems" / "erdos_squares"), "--mock", "--out", str(out)])
    assert [p.name for p in out.iterdir()] == ["keep.txt"]


# -- explanation --------------------------------------------------------------------------------------
VERIFY = '''
FUNCTION = "solve"
PUBLIC = [{"x": 1}, {"x": 2}]
HIDDEN = [{"x": 3}]
TIMEOUT_S = 20

def check(construction, instance):
    if not isinstance(construction, (int, float)):
        return {"valid": False, "score": None, "reason": "not a number"}
    return {"valid": True, "score": float(construction), "reason": ""}

def best_known(instance):
    return 10.0 * instance["x"]
'''

PROGRAM = '''
def solve(x):
    unused = x * 7
    y = 9 * x
    y = y - 0.5 * x
    return y
'''


def test_two_sided_ablation_removes_dead_code_keeps_essentials_and_labels_repairs(tmp_path):
    problem = tmp_path / "toy"
    problem.mkdir()
    (problem / "verify.py").write_text(VERIFY)
    (problem / "best.py").write_text(PROGRAM)
    r = ex.explain_program(problem, problem / "best.py", workdir=tmp_path / "work")
    by_text = {p["text"]: p for p in r["parts"]}
    dead, essential, repair = by_text["unused = x * 7"], by_text["y = 9 * x"], by_text["y = y - 0.5 * x"]
    assert r["original"]["public"] == pytest.approx(0.85)          # 8.5x / 10x on every instance
    assert dead["verdict"].startswith("can go") and dead["id"] in r["minimal"]["removed"]
    assert essential["verdict"].startswith("essential") and essential["id"] not in r["minimal"]["removed"]
    assert repair["verdict"] == ex.REPAIRED and repair["id"] in r["repaired"]       # removing it scores 0.9
    assert repair["id"] not in r["minimal"]["removed"]                               # two-sided: not dropped
    assert r["minimal"]["public"] == pytest.approx(0.85) and r["minimal"]["hidden"] == pytest.approx(0.85)
    assert "unused" not in r["minimal"]["code"] and "0.5 * x" in r["minimal"]["code"]
    md = ex.to_markdown(r)
    assert "REPAIRED (not an explanation)" in md and "Minimal program" in md


def test_terms_of_a_sum_are_parts_and_drop_with_their_sign():
    src = "def f(a, b, c):\n    return a - b + c\n"
    parts = ex.parts_of(src, "f")
    assert [p.kind for p in parts] == ["term"] * 3        # the final return is not a part; its terms are
    assert ex.variant(src, "f", {0}).strip().endswith("return -b + c")
    assert ex.variant(src, "f", {1}).strip().endswith("return a + c")


def test_nothing_to_explain_is_skipped_with_a_note():
    never = lambda code: pytest.fail("no evaluation expected")
    assert "nothing to remove" in ex.explain("def f(x):\n    return -x\n", "f", never)["skipped"]
    assert "does not parse" in ex.explain("def f(x) return x", "f", never)["skipped"]
    assert "no function" in ex.explain("def g(x):\n    return x\n", "f", never)["skipped"]
