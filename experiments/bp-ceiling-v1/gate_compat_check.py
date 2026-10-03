"""Backward-compatibility check for the gate's online extension.

Two initial programs (circle_packing, erdos_discrepancy) are unseeded and time-bounded, so
`python -m autoresearch.check --all` differs between any two runs. This script removes that
noise: for each existing problem it runs initial.py once, freezes its output into a program
that returns the same construction, and scores the frozen program with the gate at
git revision BASE and with the working-tree gate. Every metrics.json must be identical.

    python experiments/bp-ceiling-v1/gate_compat_check.py [BASE]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
PROBLEMS = ["circle_packing", "erdos_discrepancy", "erdos_squares", "sum_difference"]


def old_gate(base, tmp):
    pkg = Path(tmp) / "old" / "autoresearch"
    pkg.mkdir(parents=True)
    for name in ["__init__.py", "gate.py", "sandbox.py"]:
        src = subprocess.run(["git", "show", f"{base}:autoresearch/{name}"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
        (pkg / name).write_text(src)
    return pkg.parent


def score(gate_root, problem, program, out):
    code = ("import json,sys; sys.path.insert(0, sys.argv[1]); from autoresearch.gate import evaluate;"
            "print(json.dumps(evaluate(sys.argv[2], sys.argv[3], sys.argv[4]), sort_keys=True))")
    res = subprocess.run([sys.executable, "-c", code, str(gate_root), str(ROOT / "problems" / problem),
                          str(program), str(out)], capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "main"
    from autoresearch.gate import _load_verify
    from autoresearch.sandbox import run_candidate
    report = {}
    with tempfile.TemporaryDirectory() as tmp:
        old_root = old_gate(base, tmp)
        for problem in PROBLEMS:
            verify = _load_verify(ROOT / "problems" / problem)
            frozen = {}
            for inst in verify.PUBLIC + getattr(verify, "HIDDEN", []):
                run = run_candidate(str(ROOT / "problems" / problem / "initial.py"), verify.FUNCTION, inst,
                                    verify.TIMEOUT_S)
                assert run.ok, run.error
                frozen[json.dumps(inst, sort_keys=True)] = run.construction
            program = Path(tmp) / f"frozen_{problem}.py"
            program.write_text("import json\nTABLE = json.loads(%r)\n\ndef %s(**kw):\n"
                               "    return TABLE[json.dumps(kw, sort_keys=True)]\n"
                               % (json.dumps(frozen), verify.FUNCTION))
            old = score(old_root, problem, program, Path(tmp) / f"old_{problem}")
            new = score(ROOT, problem, program, Path(tmp) / f"new_{problem}")
            report[problem] = {"identical": old == new, "combined_score": new["combined_score"]}
            print(problem, report[problem], flush=True)
    assert all(r["identical"] for r in report.values()), "gate change altered existing scores"
    print("all identical")


if __name__ == "__main__":
    main()
