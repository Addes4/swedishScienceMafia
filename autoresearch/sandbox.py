"""Run a candidate program in a separate process.

The candidate only hands back a JSON-serialisable construction; scoring happens in
the parent process, so a candidate cannot patch or read the verifier at runtime.
API keys are stripped from the child's environment and it runs in a scratch
directory. This is isolation for an honest search loop, not a security sandbox.
"""
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Any, Optional

_CHILD = r"""
import importlib.util, json, sys, time
path, fn_name, kwargs_json, out_path = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("candidate", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def plain(x):
    try:
        import numpy as np
        if isinstance(x, np.ndarray):
            return x.tolist()
        if isinstance(x, np.generic):
            return x.item()
    except ImportError:
        pass
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    return x

t0 = time.perf_counter()
result = getattr(mod, fn_name)(**json.loads(kwargs_json))
seconds = time.perf_counter() - t0
with open(out_path, "w") as f:
    json.dump({"result": plain(result), "seconds": seconds}, f)
"""

_SECRET_ENV_PREFIXES = ("ANTHROPIC", "TYPESAFE", "OPENAI", "GEMINI", "GOOGLE", "AWS", "AZURE", "HF_", "MODAL", "WANDB",
                        "GITHUB", "GH_")
# Catch credentials from services not listed above.
_SECRET_ENV_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD")

# A valid construction for any of our problems is a few KB. A candidate that returns a huge
# or malformed object would make the parent load it into memory and could exhaust RAM/disk on
# the shared host before check() ever rejects it, so refuse to read an oversized result.
# This bounds the parent's exposure; it does not bound memory the child burns while *building*
# the object (true memory isolation needs an OS sandbox -- see this module's docstring).
MAX_OUTPUT_BYTES = 64 * 1024 * 1024


@dataclass
class RunResult:
    ok: bool
    construction: Any = None
    seconds: Optional[float] = None
    error: Optional[str] = None


def _child_env():
    return {k: v for k, v in os.environ.items()
            if not k.upper().startswith(_SECRET_ENV_PREFIXES) and not any(m in k.upper() for m in _SECRET_ENV_MARKERS)}


def run_candidate(program_path: str, fn_name: str, kwargs: dict, timeout_s: float) -> RunResult:
    program_path = os.path.abspath(program_path)
    with tempfile.TemporaryDirectory(prefix="candidate_") as tmp:
        out_path = os.path.join(tmp, "out.json")
        try:
            proc = subprocess.run(
                [sys.executable, "-c", _CHILD, program_path, fn_name, json.dumps(kwargs), out_path],
                cwd=tmp, env=_child_env(), capture_output=True, text=True, timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return RunResult(ok=False, error=f"timed out after {timeout_s:.0f}s")
        if proc.returncode != 0 or not os.path.exists(out_path):
            tail = "\n".join((proc.stderr or "").strip().splitlines()[-6:])
            return RunResult(ok=False, error=tail or f"exit code {proc.returncode}")
        if os.path.getsize(out_path) > MAX_OUTPUT_BYTES:
            return RunResult(ok=False, error=f"result exceeds {MAX_OUTPUT_BYTES} bytes")
        try:
            with open(out_path) as f:
                payload = json.load(f)
        except (OSError, ValueError) as e:
            return RunResult(ok=False, error=f"could not read result: {e}")
        return RunResult(ok=True, construction=payload["result"], seconds=payload["seconds"])
