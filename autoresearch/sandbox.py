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
        try:
            with open(out_path) as f:
                payload = json.load(f)
        except (OSError, ValueError) as e:
            return RunResult(ok=False, error=f"could not read result: {e}")
        return RunResult(ok=True, construction=payload["result"], seconds=payload["seconds"])


# Online mode: the parent reveals inputs one at a time over a private pipe and waits for the
# child's decision before sending the next one, so future inputs never exist in the child
# process. The problem's trusted DRIVER source runs in the child and calls the candidate.
_ONLINE_CHILD = r"""
import importlib.util, json, os, sys
path, fn_name, driver_source, rfd, wfd = sys.argv[1:6]
reader = os.fdopen(int(rfd), "r")
writer = os.fdopen(int(wfd), "w")
spec = importlib.util.spec_from_file_location("candidate", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
driver = {}
exec(compile(driver_source, "<driver>", "exec"), driver)

def next_input():
    line = reader.readline()
    return json.loads(line) if line else None

def emit(decision):
    writer.write(json.dumps(decision) + "\n")
    writer.flush()

header = next_input()
driver["drive"](getattr(mod, fn_name), header, next_input, emit)
"""


def _read_line(fd, buffer: bytearray, deadline: float):
    """One newline-terminated line from fd, or None on EOF or when the deadline passes."""
    import select
    import time
    while b"\n" not in buffer:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([fd], [], [], remaining)[0]:
            return None
        chunk = os.read(fd, 65536)
        if not chunk:
            return None
        buffer.extend(chunk)
    line, _, rest = bytes(buffer).partition(b"\n")
    buffer[:] = rest
    return line


def run_online(program_path: str, fn_name: str, driver_source: str, header: dict, inputs: list,
               timeout_s: float) -> RunResult:
    """Run an online candidate: construction = one decision per input, in input order.

    Input k+1 is written only after the decision for input k has been read, so a candidate
    cannot look ahead or reorder. timeout_s bounds the whole instance."""
    import time
    program_path = os.path.abspath(program_path)
    with tempfile.TemporaryDirectory(prefix="candidate_") as tmp:
        to_child_r, to_child_w = os.pipe()
        from_child_r, from_child_w = os.pipe()
        log_path = os.path.join(tmp, "stderr.txt")
        t0 = time.monotonic()
        deadline = t0 + timeout_s
        with open(log_path, "w") as log:
            proc = subprocess.Popen(
                [sys.executable, "-c", _ONLINE_CHILD, program_path, fn_name, driver_source,
                 str(to_child_r), str(from_child_w)],
                pass_fds=(to_child_r, from_child_w), cwd=tmp, env=_child_env(),
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=log)
        os.close(to_child_r)
        os.close(from_child_w)
        writer = os.fdopen(to_child_w, "w")
        buffer, decisions, error = bytearray(), [], None
        try:
            writer.write(json.dumps(header) + "\n")
            writer.flush()
            for value in inputs:
                writer.write(json.dumps(value) + "\n")
                writer.flush()
                line = _read_line(from_child_r, buffer, deadline)
                if line is None:
                    error = (f"timed out after {timeout_s:.0f}s" if time.monotonic() >= deadline
                             else "program stopped before deciding every input")
                    break
                decisions.append(json.loads(line))
        except (BrokenPipeError, ValueError) as e:
            error = f"protocol error ({type(e).__name__})"
        finally:
            try:
                writer.close()
            except BrokenPipeError:
                pass
            os.close(from_child_r)
            try:
                proc.wait(timeout=max(deadline - time.monotonic(), 0.5))
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                error = error or f"timed out after {timeout_s:.0f}s"
        seconds = time.monotonic() - t0
        if error is None and proc.returncode != 0:
            error = f"exit code {proc.returncode}"
        if error is not None:
            with open(log_path) as f:
                tail = "\n".join(f.read().strip().splitlines()[-6:])
            if proc.returncode not in (0, None) and tail and "timed out" not in error:
                error = tail
            return RunResult(ok=False, error=error, seconds=seconds)
        return RunResult(ok=True, construction=decisions, seconds=seconds)
