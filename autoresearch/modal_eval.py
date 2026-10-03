"""Run the integrity gate on Modal: one container per candidate program, same gate code.

Each candidate is scored by autoresearch.gate.evaluate (via autoresearch.evalcode) inside a
container with 1 physical core and 1 GiB that holds only autoresearch/ and problems/; no
secrets are mounted. The app (`ssm-idea-table`) is ephemeral and stops when the batch ends.

A spend cap is enforced before submitting: every candidate is charged its worst case (every
instance hitting the per-instance timeout) at Modal's list rates, and a batch that could
exceed the cap is cut. Estimated cost per container is logged to modal_usage.jsonl.
"""
import json
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "ssm-idea-table"
CPU, MEMORY_MB = 1.0, 1024
# `modal billing rates`, 3 Oct 2026: $0.0473 per core-hour, $0.008 per GiB-hour.
CPU_PER_CORE_S, MEM_PER_GIB_S = 0.0473 / 3600, 0.008 / 3600
RATE_PER_S = CPU * CPU_PER_CORE_S + (MEMORY_MB / 1024) * MEM_PER_GIB_S
STARTUP_OVERHEAD_S = 30.0
FUNCTION_TIMEOUT_S = 1500

# Pin the same numpy/scipy as the local venv (read at image-build time on the laptop).
try:
    import numpy as _np
    import scipy as _sp
    _PINS = [f"numpy=={_np.__version__}", f"scipy=={_sp.__version__}"]
except ImportError:      # inside the container the image is already built
    _PINS = ["numpy", "scipy"]

image = (modal.Image.debian_slim(python_version="3.12")
         .pip_install(*_PINS)
         .add_local_dir(str(ROOT / "problems"), "/root/problems", ignore=["**/__pycache__", "**/*.pyc"])
         .add_local_python_source("autoresearch"))
app = modal.App(APP_NAME)


@app.function(image=image, cpu=CPU, memory=MEMORY_MB, timeout=FUNCTION_TIMEOUT_S, max_containers=40)
def eval_candidate(problem_name: str, code: str) -> dict:
    from autoresearch.evalcode import evaluate_code
    t0 = time.time()
    res = evaluate_code(f"/root/problems/{problem_name}", code)
    res["container_seconds"] = round(time.time() - t0, 2)
    return res


def worst_case_seconds(problem_dir: Path) -> float:
    import importlib.util
    spec = importlib.util.spec_from_file_location("verify", Path(problem_dir) / "verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    n = len(mod.PUBLIC) + len(getattr(mod, "HIDDEN", []))
    return min(n * (mod.TIMEOUT_S + 5), FUNCTION_TIMEOUT_S) + STARTUP_OVERHEAD_S


def spent(ledger_path) -> float:
    ledger_path = Path(ledger_path)
    if not ledger_path.exists():
        return 0.0
    return sum(json.loads(l).get("cost_estimate", 0.0) for l in ledger_path.read_text().splitlines() if l.strip())


def evaluate_many(problem_dir, codes, ledger_path, cap=5.0, labels=None) -> list:
    """Score every program; returns a list aligned with `codes` (None where the cap cut it off or it failed)."""
    problem_dir = Path(problem_dir)
    labels = labels or [str(i) for i in range(len(codes))]
    worst = worst_case_seconds(problem_dir) * RATE_PER_S
    remaining = cap - spent(ledger_path)
    n_ok = max(0, min(len(codes), int(remaining // worst)))
    if n_ok < len(codes):
        print(f"[modal] cap ${cap:.2f}: only {n_ok}/{len(codes)} programs fit the worst-case reservation "
              f"(${worst:.4f} each, ${remaining:.3f} left)")
    results = [None] * len(codes)
    if n_ok == 0:
        return results
    t0 = time.time()
    with modal.enable_output(), app.run():
        outs = eval_candidate.map([problem_dir.name] * n_ok, codes[:n_ok], return_exceptions=True)
        for i, out in enumerate(outs):
            if isinstance(out, BaseException):
                print(f"[modal] {labels[i]}: {type(out).__name__}: {str(out)[:200]}")
                entry = {"label": labels[i], "ok": False, "error": type(out).__name__,
                         "cost_estimate": worst}   # unknown duration: charge the worst case
            else:
                results[i] = out
                secs = (out.get("container_seconds") or 0.0) + STARTUP_OVERHEAD_S
                entry = {"label": labels[i], "ok": True, "container_seconds": out.get("container_seconds"),
                         "cost_estimate": round(secs * RATE_PER_S, 6)}
            entry["time"] = time.time()
            with open(ledger_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
    print(f"[modal] {n_ok} programs in {time.time() - t0:.0f}s; estimated Modal spend so far "
          f"${spent(ledger_path):.3f} of ${cap:.2f}")
    return results
