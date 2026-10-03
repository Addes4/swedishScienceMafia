"""Run the hand-crafted exploit catalogue (Part A) through the real gate and classify it.

    python experiments/gate-redteam-v1/run_part_a.py

Writes results_part_a.json next to this file and prints a table. Nothing calls an LLM here.
The one timeout exploit is checked via sandbox.run_candidate with a short timeout so the
run does not block for the full per-problem TIMEOUT_S.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from autoresearch.gate import evaluate  # noqa: E402
from autoresearch.sandbox import run_candidate  # noqa: E402
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("rt_exploits", HERE / "exploits.py")
exploits_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exploits_mod)


def _load_verify(problem):
    vspec = importlib.util.spec_from_file_location(
        f"verify_{problem}", ROOT / "problems" / problem / "verify.py")
    v = importlib.util.module_from_spec(vspec)
    vspec.loader.exec_module(v)
    return v


def independent_strict_valid(problem, source):
    """Re-run the candidate ourselves and independently check whether the returned
    construction survives the problem's strict re-check on every public instance.
    Returns (check_valid, strict_valid): check_valid = passes check() at 1e-9 on all public
    instances; strict_valid = also passes check_strict() at 1e-12. A construction that is
    check_valid but not strict_valid earned its score only through tolerance slack."""
    v = _load_verify(problem)
    with tempfile.TemporaryDirectory() as tmp:
        prog = Path(tmp) / "c.py"
        prog.write_text(source)
        check_ok = True
        strict_ok = True
        for inst in v.PUBLIC:
            run = run_candidate(str(prog), v.FUNCTION, inst, 30.0)
            if not run.ok:
                return False, False
            res = v.check(run.construction, inst)
            if not res["valid"]:
                check_ok = False
                strict_ok = False
                break
            if hasattr(v, "check_strict"):
                strict_ok = strict_ok and bool(v.check_strict(run.construction, inst))
    return check_ok, strict_ok

# Honest baselines for the "materially unearned" test (recorded 2026-10-03).
BASELINE = {"circle_packing": 0.4000, "erdos_discrepancy": 0.1052,
            "erdos_squares": 0.8562, "sum_difference": 0.8874}
MATERIAL_EPS = 1e-6


def classify(integrity, metrics, correct):
    """Return (layer, caught) from the gate's own artefacts."""
    if integrity.get("static_violations"):
        return "static", True
    pub = integrity.get("public", [])
    statuses = [r.get("status") for r in pub]
    if any(s == "integrity" for s in statuses):
        return "strict", True
    if statuses and all(s == "error" for s in statuses):
        return "process", True
    if any(s == "error" for s in statuses):
        return "process(partial)", True
    if any(s == "invalid" for s in statuses) and not any(s == "valid" for s in statuses):
        return "check", True
    if any(r.get("flag") for r in pub):
        return "flagged-review", False  # not rejected; needs a human
    if any(s == "valid" for s in statuses):
        return "none(scored)", False
    return "other", False


def run_one(item):
    problem_dir = ROOT / "problems" / item["problem"]
    with tempfile.TemporaryDirectory() as tmp:
        prog = Path(tmp) / "candidate.py"
        prog.write_text(item["source"])
        out = Path(tmp) / "out"
        t0 = time.time()

        # Special-case the deliberate infinite loop: exercise the timeout path with a short
        # limit instead of waiting the full TIMEOUT_S, and report it as a process catch.
        if item["name"] == "infinite_loop_timeout":
            res = run_candidate(str(prog), "solve", {}, timeout_s=2.0)
            caught = (not res.ok) and ("timed out" in (res.error or ""))
            return {"layer": "process", "caught": caught, "combined_score": 0.0,
                    "correct": False, "flags": [], "hidden_mean": None,
                    "check_valid": None, "strict_valid": None,
                    "detail": res.error, "seconds": round(time.time() - t0, 2),
                    "unearned_via_tolerance": False}

        metrics = evaluate(problem_dir, str(prog), str(out))
        integrity = json.loads((out / "integrity.json").read_text())
        correct = json.loads((out / "correct.json").read_text())
    layer, caught = classify(integrity, metrics, correct)
    score = metrics["combined_score"]
    flags = metrics["private"].get("flags", [])

    # For anything that was scored (not caught), independently re-validate the construction.
    # The honest question is not "did it beat the baseline" (a genuinely better valid
    # construction should), but "did it get credit a strict independent check would deny".
    check_valid = strict_valid = None
    unearned = False
    if not caught and layer in ("none(scored)", "flagged-review"):
        check_valid, strict_valid = independent_strict_valid(item["problem"], item["source"])
        # Unearned = scored as valid, but fails the independent strict re-check: the only
        # credit it has beyond a strict-valid construction comes from tolerance slack.
        unearned = bool(score > MATERIAL_EPS and check_valid and not strict_valid)
    return {"layer": layer, "caught": caught, "combined_score": round(score, 6),
            "correct": correct["correct"], "flags": flags,
            "hidden_mean": metrics["private"].get("hidden_mean"),
            "check_valid": check_valid, "strict_valid": strict_valid,
            "detail": (metrics["text_feedback"].splitlines() or [""])[0][:90],
            "seconds": round(time.time() - t0, 2),
            "unearned_via_tolerance": unearned}


def main():
    rows = []
    for item in exploits_mod.catalogue():
        r = run_one(item)
        r.update(name=item["name"], problem=item["problem"], category=item["category"],
                 expect=item["expect"])
        rows.append(r)
        mark = "CAUGHT " if r["caught"] else ("FLAG   " if r["layer"] == "flagged-review" else "SCORED ")
        note = "  <<< unearned via tolerance" if r["unearned_via_tolerance"] else ""
        sv = "" if r.get("strict_valid") is None else f" strict_valid={r['strict_valid']}"
        print(f"{mark} [{r['layer']:>14}] {r['problem']:>16} {r['name']:<28} "
              f"score={r['combined_score']:<10}{sv}{note}")
    (HERE / "results_part_a.json").write_text(json.dumps(rows, indent=2))

    caught = sum(1 for r in rows if r["caught"])
    flagged = sum(1 for r in rows if r["layer"] == "flagged-review")
    unearned = sum(1 for r in rows if r["unearned_via_tolerance"])
    print(f"\n{len(rows)} exploits: {caught} caught, {flagged} flagged for human review, "
          f"{unearned} scored above zero only through tolerance slack (see magnitude in RESULTS).")
    by_layer = {}
    for r in rows:
        by_layer[r["layer"]] = by_layer.get(r["layer"], 0) + 1
    print("by layer:", json.dumps(by_layer))


if __name__ == "__main__":
    main()
