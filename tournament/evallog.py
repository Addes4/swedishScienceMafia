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

from autoresearch.gate import _load_verify, evaluate

EVAL_LOG_ENV = "TOURNAMENT_EVAL_LOG"
PROBLEM_ENV = "TOURNAMENT_PROBLEM_DIR"


def evaluate_logged(problem_dir, program_path: str, results_dir: str, tag: str = None) -> dict:
    t0 = time.time()
    metrics = evaluate(problem_dir, program_path, results_dir)
    log_path = os.environ.get(EVAL_LOG_ENV)
    if log_path:
        rec = record(program_path, results_dir, metrics, t0, tag)
        rec["record_flags"] = record_flags(problem_dir, results_dir)
        append(log_path, rec)
    return metrics


def record_flags(problem_dir, results_dir) -> list:
    """Every instance scored above its best known value, with the numbers needed to judge it.

    A margin is only worth a human look if it exceeds n x the checker's tolerance (n = the
    instance's size, tolerance = verify.TOL; 0 for exact checkers): below that, float slack in
    n constraints could explain it. The gate has already re-checked these at 1e-12.
    """
    integrity = json.loads((Path(results_dir) / "integrity.json").read_text())
    flagged = [r for r in integrity.get("public", []) + integrity.get("hidden", []) if r.get("flag")]
    if not flagged:
        return []
    tol = float(getattr(_load_verify(Path(problem_dir)), "TOL", 0.0))
    out = []
    for r in flagged:
        n = (r.get("instance") or {}).get("n")
        margin = r["score"] - r["best_known"]
        threshold = (n or 1) * tol
        out.append({"label": r["label"], "score": r["score"], "reference": r["best_known"], "margin": margin,
                    "n": n, "tolerance": tol, "n_x_tolerance": threshold, "worth_review": margin > threshold})
    return out


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
        "instance_timeouts": sum("timed out" in str(r.get("reason") or "")
                                 for r in public + integrity.get("hidden", [])),
        "flags": private.get("flags"),
    }


def append(path, rec: dict):
    with open(path, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(rec, default=str) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)
