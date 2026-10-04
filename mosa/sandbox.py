"""Running model-written strategy code.

A strategy defines initialize(record, neighbours, rng, count) and vary(parents, rng, count), each returning a list of
candidates (x, value). The code runs with only numpy, math, numba and the size n available, under a time limit, and every call
starts from a fresh namespace, so a strategy keeps no state between calls. Candidates that fail the domain's
validation are dropped and counted; a call fails only if its code raises or nothing valid comes back. A call can be
split over forked workers, each with its own chunk of the count and its own random stream. Before any code runs it
must pass a static integrity scan (no file, process, network, import-system or evaluator access).
"""
from __future__ import annotations

import io
import math
import re
import signal
import threading
import tokenize
import traceback

import numpy as np

SECONDS = 240
# Static integrity scan, adopted from the team's autoresearch gate (autoresearch/gate.py on main): strategy code has no
# business touching files, processes, the network, the import system or the evaluator. Comments and string contents
# are blanked first, so only code is scanned.
FORBIDDEN = [
    (r"\bopen\s*\(|\bpathlib\b|\bio\s*\.\s*open\b|\btempfile\b|\bpickle\b|\bshelve\b", "file access"),
    (r"(?<![.\w])(eval|exec|compile)\s*\(", "dynamic code execution"),
    (r"\b(subprocess|socket|urllib|requests|httpx|http\.client|ftplib|shutil)\b", "process or network access"),
    (r"\bos\s*\.\s*(system|popen|exec\w*|spawn\w*|remove|unlink|rmdir|environ|getenv|kill|fork)", "os access"),
    (r"\b(importlib|__import__|sys\s*\.\s*modules|builtins|ctypes|gc\s*\.\s*get_objects)\b", "import or runtime tampering"),
    (r"(evaluate|sandbox|audit|kernel)\.py|known-best|catalogue\.json", "evaluator access"),
]


def violations(code):
    """Reasons the code fails the static scan (empty: it passes)."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        tokens = []
    rows = [list(line) for line in code.splitlines(keepends=True)]
    for t in tokens:
        if t.type in (tokenize.STRING, tokenize.COMMENT) or tokenize.tok_name.get(t.type) == "FSTRING_MIDDLE":
            (sr, sc), (er, ec) = t.start, t.end
            for r in range(sr, er+1):
                row = rows[r-1]
                for c in range(sc if r == sr else 0, min(ec if r == er else len(row), len(row))):
                    if row[c] != "\n":
                        row[c] = " "
    scanned = "".join("".join(r) for r in rows)
    return sorted({why for pattern, why in FORBIDDEN if re.search(pattern, scanned)})


_CURRENT = {}  # namespace and payload of the call in progress, inherited by forked workers


def _chunk(job):
    kind, count, seed = job
    rng = np.random.default_rng(seed)
    ns, payload = _CURRENT["namespace"], _CURRENT["payload"]
    if kind == "initialize":
        return list(ns["initialize"](payload["record"], payload["neighbours"], rng, count))[:count]
    return list(ns["vary"](payload["parents"], rng, count))[:count]


def _expire(*_):
    raise TimeoutError(f"strategy code exceeded {SECONDS} s")


def step(domain, code, kind, payload, count, seed, n, cores=1):
    """{"x": [...], "values": [...], "dropped": k} or {"error": traceback}."""
    import numba
    timed = threading.current_thread() is threading.main_thread()
    try:
        if timed:
            signal.signal(signal.SIGALRM, _expire)
            signal.alarm(SECONDS)
        problems = violations(code)
        if problems:
            raise PermissionError("integrity scan: "+", ".join(problems))
        namespace = {"np": np, "math": math, "numba": numba, "n": n, "problem": domain.name}  # the instance of this run
        exec(code, namespace)
        _CURRENT.update(namespace=namespace, payload=payload)
        workers = max(1, min(cores, count//8))
        sizes = [count//workers+(k < count % workers) for k in range(workers)]
        jobs = [(kind, size, [seed, k]) for k, size in enumerate(sizes) if size]
        if len(jobs) == 1:
            made = _chunk(jobs[0])
        else:
            import multiprocessing
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(len(jobs), mp_context=multiprocessing.get_context("fork")) as pool:
                made = [c for chunk in pool.map(_chunk, jobs) for c in chunk]
        xs, values, problems = [], [], []
        for x, value in made[:count]:
            try:
                xs.append(domain.validate(x, value, n))
                values.append(float(value))
            except (ValueError, TypeError) as error:
                problems.append(str(error))
        if not xs:
            raise ValueError(f"{kind} returned no valid candidates" + (f"; first problem: {problems[0]}" if problems else ""))
        return {"x": xs, "values": values, "dropped": len(problems)}
    except Exception:
        return {"error": traceback.format_exc(limit=4)[-2500:]}
    finally:
        if timed:
            signal.alarm(0)
