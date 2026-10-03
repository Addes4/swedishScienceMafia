"""Integrity gate tests: honest programs pass, exploits are caught, and the LLM-facing
feedback never reveals why. Run with:  python -m pytest tests/ -q"""
import json
import textwrap
from pathlib import Path

from autoresearch.gate import GENERIC_REJECTION, evaluate

ROOT = Path(__file__).resolve().parents[1]
CIRCLES_26 = json.loads((ROOT / "tests" / "alphaevolve_circles_26.json").read_text())


def _run(tmp_path, problem, source):
    prog = tmp_path / "candidate.py"
    prog.write_text(textwrap.dedent(source))
    out = tmp_path / "out"
    metrics = evaluate(ROOT / "problems" / problem, str(prog), str(out))
    integrity = json.loads((out / "integrity.json").read_text())
    correct = json.loads((out / "correct.json").read_text())
    return metrics, correct, integrity


def test_alphaevolve_circles_pass(tmp_path):
    metrics, correct, _ = _run(tmp_path, "circle_packing", f"""
        def solve(n=26):
            return {CIRCLES_26!r}
    """)
    assert correct["correct"]
    assert abs(metrics["combined_score"] - 1.0) < 1e-9
    assert metrics["private"]["integrity_rejections"] == 0


def test_tolerance_exploit_circles_caught(tmp_path):
    # Inflate every radius by 4e-10: overlaps stay inside the 1e-9 tolerance, total beats the record.
    metrics, correct, integrity = _run(tmp_path, "circle_packing", f"""
        def solve(n=26):
            d = {CIRCLES_26!r}
            return {{"centers": d["centers"], "radii": [r + 4e-10 for r in d["radii"]]}}
    """)
    assert not correct["correct"]
    assert metrics["combined_score"] == 0.0
    assert integrity["public"][0]["status"] == "integrity"
    assert metrics["text_feedback"] == f"n=26: {GENERIC_REJECTION}"   # no reason leaked to the LLM


def test_tolerance_exploit_squares_caught(tmp_path):
    # 2 x 2 grid with sides 0.5 + 4e-10: tiny overlaps the 1e-9 tolerance forgives, sum above 2.
    metrics, correct, _ = _run(tmp_path, "erdos_squares", """
        import math
        def solve(n):
            k = math.isqrt(n)
            s = 1 / k + 4e-10
            sq = [((i + 0.5) / k, (j + 0.5) / k, 0.0, s) for i in range(k) for j in range(k)]
            return (sq + [(0.5, 0.5, 0.0, 0.0)] * n)[:n]
    """)
    assert metrics["combined_score"] == 0.0 and not correct["correct"]
    assert GENERIC_REJECTION in metrics["text_feedback"]
    assert "strict" not in metrics["text_feedback"]


def test_reading_the_verifier_is_rejected_statically(tmp_path):
    metrics, correct, integrity = _run(tmp_path, "sum_difference", """
        def solve():
            src = open("../verify.py").read()
            return [0, 1, 3]
    """)
    assert integrity["static_violations"] and not correct["correct"]
    assert metrics["text_feedback"] == f"Program {GENERIC_REJECTION}."


def test_runtime_import_of_verifier_cannot_reach_it(tmp_path):
    # Runs in a separate process with no access to the problem folder.
    metrics, correct, integrity = _run(tmp_path, "sum_difference", """
        def solve():
            import verify
            verify.check = lambda *a: {"valid": True, "score": 99.0, "reason": ""}
            return [0, 1, 3]
    """)
    assert integrity["public"][0]["status"] == "error"
    assert metrics["combined_score"] == 0.0


def test_timeout_is_reported(tmp_path):
    from autoresearch.sandbox import run_candidate
    prog = tmp_path / "slow.py"
    prog.write_text("import time\ndef solve():\n    time.sleep(60)\n")
    res = run_candidate(str(prog), "solve", {}, timeout_s=1.0)
    assert not res.ok and "timed out" in res.error


def test_sum_difference_size_bonus_alone_is_not_a_record(tmp_path):
    # The score adds a size bonus below 0.01, so a ratio near 1.262 would beat the bare 1.2715 constant.
    # The reference must include the maximum bonus; an ordinary set must not be flagged.
    import importlib.util
    spec = importlib.util.spec_from_file_location("sd_verify", ROOT / "problems" / "sum_difference" / "verify.py")
    verify = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verify)
    assert verify.best_known({}) >= verify.BEST_KNOWN + 0.01
    metrics, _, integrity = _run(tmp_path, "sum_difference", """
        def solve():
            return [0, 1, 3]
    """)
    assert not metrics["private"]["flags"]
    assert integrity["public"][0]["status"] == "valid"


def test_api_keys_never_reach_the_candidate(tmp_path, monkeypatch):
    from autoresearch.sandbox import run_candidate
    for key in ("ANTHROPIC_API_KEY", "TYPESAFE_API_KEY", "SOME_NEW_SERVICE_TOKEN"):
        monkeypatch.setenv(key, "dummy-value")
    prog = tmp_path / "peek.py"
    prog.write_text("import os\ndef solve():\n    return sorted(os.environ)\n")
    res = run_candidate(str(prog), "solve", {}, timeout_s=30.0)
    assert res.ok
    assert not {"ANTHROPIC_API_KEY", "TYPESAFE_API_KEY", "SOME_NEW_SERVICE_TOKEN"} & set(res.construction)


def test_oversized_output_is_refused(tmp_path):
    # A candidate that returns a huge object must be refused before the parent loads it,
    # so it cannot exhaust memory/disk on the shared host. Bounded here to just over the cap.
    from autoresearch.sandbox import run_candidate, MAX_OUTPUT_BYTES
    prog = tmp_path / "big.py"
    chunk = MAX_OUTPUT_BYTES // 8 + 100  # each float serialises to several bytes
    prog.write_text(f"def solve():\n    return [1.123456789] * {chunk}\n")
    res = run_candidate(str(prog), "solve", {}, timeout_s=60.0)
    assert not res.ok and "exceeds" in res.error


def test_normal_output_still_passes_the_size_guard(tmp_path):
    from autoresearch.sandbox import run_candidate
    prog = tmp_path / "ok.py"
    prog.write_text("def solve():\n    return [0, 1, 3]\n")
    res = run_candidate(str(prog), "solve", {}, timeout_s=30.0)
    assert res.ok and res.construction == [0, 1, 3]


def test_circle_inf_radius_rejected_at_parse(tmp_path):
    # An infinite radius used to slip _parse (only NaN and r<0 were checked) and was caught
    # only downstream by the containment test; reject it cleanly at parse instead.
    metrics, correct, _ = _run(tmp_path, "circle_packing", f"""
        def solve(n=26):
            d = {CIRCLES_26!r}
            r = list(d["radii"]); r[0] = float("inf")
            return {{"centers": d["centers"], "radii": r}}
    """)
    assert not correct["correct"] and metrics["combined_score"] == 0.0
