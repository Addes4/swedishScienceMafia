"""Regression tests locking in the gate's behaviour on the gate-redteam-v1 exploit catalogue.

These assert the invariants the red-team established: the record-triggered strict re-check
catches over-record tolerance exploits; malformed / NaN / inf constructions are rejected by
check(); lying objects cannot cross the process+JSON boundary; and no catalogued exploit
obtains a construction that passes check() at 1e-9 but fails the strict re-check with a
material (> 1e-3) over-credit.

Only the fast catalogue entries are exercised here (the ones that return immediately); the
timeout/search entries are covered by experiments/gate-redteam-v1/run_part_a.py.
"""
import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from autoresearch.gate import evaluate  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "rt_exploits", ROOT / "experiments" / "gate-redteam-v1" / "exploits.py")
_ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ex)
CATALOGUE = {it["name"]: it for it in _ex.catalogue()}

# Fast entries (no 20 s search, no deliberate timeout).
FAST = ["tol_overlap_over_record", "tol_overlap_squares_over_record", "nan_radius",
        "inf_radius", "inf_side_square", "nan_entry_discrepancy", "wrong_count",
        "ragged_structure", "lying_eq_object", "numpy_subclass_lie", "monkeypatch_math",
        "monkeypatch_builtins_len", "runtime_import_verify", "open_verify_disk",
        "honest_but_comment_rejected"]


def _run(item, tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    prog = tmp_path / "c.py"
    prog.write_text(item["source"])
    out = tmp_path / "o"
    metrics = evaluate(ROOT / "problems" / item["problem"], str(prog), str(out))
    integrity = json.loads((out / "integrity.json").read_text())
    return metrics, integrity


def test_over_record_tolerance_exploits_are_caught_by_strict(tmp_path):
    for name in ("tol_overlap_over_record", "tol_overlap_squares_over_record"):
        metrics, integ = _run(CATALOGUE[name], tmp_path / name)
        assert metrics["combined_score"] == 0.0
        assert any(r["status"] == "integrity" for r in integ["public"]), name


def test_malformed_constructions_rejected(tmp_path):
    for name in ("nan_radius", "inf_radius", "inf_side_square", "nan_entry_discrepancy",
                 "wrong_count", "ragged_structure", "monkeypatch_math"):
        metrics, _ = _run(CATALOGUE[name], tmp_path / name)
        assert metrics["combined_score"] == 0.0, name


def test_lying_object_cannot_cross_the_boundary(tmp_path):
    metrics, integ = _run(CATALOGUE["lying_eq_object"], tmp_path)
    assert metrics["combined_score"] == 0.0
    assert integ["public"][0]["status"] == "error"


def test_numpy_subclass_is_coerced_to_honest_data(tmp_path):
    # Returning the real optimum through a lying numpy subclass yields the honest score, 1.0.
    metrics, _ = _run(CATALOGUE["numpy_subclass_lie"], tmp_path)
    assert abs(metrics["combined_score"] - 1.0) < 1e-9


def test_honest_comment_is_not_a_false_positive(tmp_path):
    # After the Part C static fix, an honest program that only mentions forbidden words in a
    # comment/string is accepted.
    metrics, integ = _run(CATALOGUE["honest_but_comment_rejected"], tmp_path)
    assert not integ["static_violations"]
    assert metrics["combined_score"] > 0.0


@pytest.mark.parametrize("name", FAST)
def test_no_fast_exploit_yields_material_unearned_score(tmp_path, name):
    # Nothing in the fast set may score above zero while failing an independent strict re-check
    # by a material margin (tolerance slack is < 1e-3).
    item = CATALOGUE[name]
    metrics, _ = _run(item, tmp_path / name)
    score = metrics["combined_score"]
    if score <= 1e-3:
        return
    vspec = importlib.util.spec_from_file_location(
        "v_" + name, ROOT / "problems" / item["problem"] / "verify.py")
    v = importlib.util.module_from_spec(vspec)
    vspec.loader.exec_module(v)
    if not hasattr(v, "check_strict"):
        return
    from autoresearch.sandbox import run_candidate
    with tempfile.TemporaryDirectory() as tmp:
        prog = Path(tmp) / "c.py"
        prog.write_text(item["source"])
        for inst in v.PUBLIC:
            run = run_candidate(str(prog), v.FUNCTION, inst, 30.0)
            assert run.ok
            assert v.check_strict(run.construction, inst), (name, inst)
