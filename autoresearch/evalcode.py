"""Score one program source with the integrity gate (used locally and inside Modal containers).

Imports only the gate, so it runs where anthropic and the other loop dependencies are absent.
"""
import json
import tempfile
import time
from pathlib import Path

from .gate import evaluate


def evaluate_code(problem_dir, code: str) -> dict:
    """Run autoresearch.gate.evaluate on `code`; return metrics, correct.json and an integrity summary."""
    with tempfile.TemporaryDirectory(prefix="ideatable_") as tmp:
        prog = Path(tmp) / "program.py"
        prog.write_text(code)
        t0 = time.time()
        metrics = evaluate(Path(problem_dir), str(prog), str(Path(tmp) / "results"))
        seconds = time.time() - t0
        correct = json.loads((Path(tmp) / "results" / "correct.json").read_text())
        integ = json.loads((Path(tmp) / "results" / "integrity.json").read_text())
    summary = {"static_violations": integ.get("static_violations", []),
               "instances": [{k: r.get(k) for k in ("label", "status", "score", "normalized", "seconds", "reason")}
                             for r in integ.get("public", []) + integ.get("hidden", [])]}
    return {"metrics": metrics, "correct": correct, "integrity": summary, "seconds": round(seconds, 2)}
