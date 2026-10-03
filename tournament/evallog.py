"""Score programs with the integrity gate and append one record per evaluation to a private log.

Every arm's evaluations go through here, so the tournament measures all of them the same way:
in-process arms call evaluate_logged directly (or have it patched in), and ShinkaEvolve runs
`python -m tournament.shinka_eval` as its evaluation program. The log path comes from
TOURNAMENT_EVAL_LOG. The log holds hidden-instance scores: it is read only by the analysis after
a run and never reaches an LLM.
"""
import fcntl
import hashlib
import json
import os
import time
from pathlib import Path

from autoresearch.gate import evaluate

EVAL_LOG_ENV = "TOURNAMENT_EVAL_LOG"
PROBLEM_ENV = "TOURNAMENT_PROBLEM_DIR"


def evaluate_logged(problem_dir, program_path: str, results_dir: str, tag: str = None) -> dict:
    t0 = time.time()
    metrics = evaluate(problem_dir, program_path, results_dir)
    log_path = os.environ.get(EVAL_LOG_ENV)
    if log_path:
        append(log_path, record(program_path, results_dir, metrics, t0, tag))
    return metrics


def record(program_path, results_dir, metrics, t0, tag=None) -> dict:
    results = Path(results_dir)
    correct = json.loads((results / "correct.json").read_text())
    integrity = json.loads((results / "integrity.json").read_text())
    code = Path(program_path).read_bytes()
    public = integrity.get("public", [])
    private = metrics.get("private", {})
    return {
        "t": time.time(), "seconds": round(time.time() - t0, 3), "tag": tag,
        "program": str(program_path), "sha": hashlib.sha256(code).hexdigest()[:16],
        "combined": metrics["combined_score"], "correct": bool(correct["correct"]),
        "static_rejected": bool(integrity.get("static_violations")),
        "public_labels": [r["label"] for r in public],
        "public_normalized": [r["normalized"] for r in public],
        "public_status": [r["status"] for r in public],
        "hidden_normalized": private.get("hidden_normalized"),
        "hidden_mean": private.get("hidden_mean"),
        "integrity_rejections": private.get("integrity_rejections"),
        "flags": private.get("flags"),
    }


def append(path, rec: dict):
    with open(path, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(rec, default=str) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)
