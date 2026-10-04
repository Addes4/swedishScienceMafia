"""Running model-written strategy code.

A strategy defines initialize(record, neighbours, rng, count) and vary(parents, rng, count), each returning a list of
candidates (x, value). The code runs with only numpy, math and numba available, under a time limit, and every call
starts from a fresh namespace, so a strategy keeps no state between calls. Candidates that fail the domain's
validation are dropped and counted; a call fails only if its code raises or nothing valid comes back. A call can be
split over forked workers, each with its own chunk of the count and its own random stream.
"""
from __future__ import annotations

import math
import signal
import threading
import traceback

import numpy as np

SECONDS = 240
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
        namespace = {"np": np, "math": math, "numba": numba}
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
