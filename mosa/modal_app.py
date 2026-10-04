"""Modal workers: relaxation, polish and sandboxed strategy code, each in multi-core containers.

The workspace limit counts containers, not cores, so every container works on many candidates at once in forked
processes. Numba kernels are compiled at image build for a generic x86-64 target, so a new container computes at once.
"""
import os
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent
# Moderate defaults (a peak of about 500 cores): raise them with the environment variables for a big campaign.
CORES = int(os.getenv("MOSA_MODAL_CORES", "32"))
CONTAINERS = int(os.getenv("MOSA_MODAL_CONTAINERS", "8"))
POLISH_CORES = 16    # a run polishes 16 basins: one container of this size each
STRATEGY_CORES = 16
IDLE = 120           # seconds an idle container stays warm between rounds

# Tagged with the workspace, so Modal's billing report gives the spend of each workspace (mosa/spend.py).
WORKSPACE = "".join(c for c in os.environ.get("MOSA_WORKSPACE", "") if c.isalnum() or c in "-_.")[:60]
app = modal.App("mosa", tags={"workspace": WORKSPACE} if WORKSPACE else None)
image = (modal.Image.debian_slim(python_version="3.12")
         .pip_install("numpy==2.5.3", "scipy==1.18.1", "numba==0.68.0", "mpmath==1.3.0")  # drafted harnesses may import mpmath
         .env({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "NUMBA_CPU_NAME": "generic", "NUMBA_CACHE_DIR": "/root/numba-cache"})
         .add_local_dir(ROOT, remote_path="/root/mosa", copy=True, ignore=["**/__pycache__", "ui/**"])
         .run_commands('cd /root && python -c "import numpy as np; from mosa.domains.squares.kernel import relax; '
                       'relax(np.array([[.5, .5, 0.], [1.6, .5, .1]]), 2.2, 300)"'))


def _relax_one(job):
    from mosa.domain import get
    name, x, value = job
    try:
        x, value, used = get(name).relax(x, value)
        return {"x": x, "value": value, "used": used}
    except ValueError as error:
        return {"error": str(error)}


_POOL = {}


def _pool(cores, fresh=False):
    """One worker pool per container, kept across calls. Workers start from a forkserver, not by forking this process:
    a fork of a process that also runs Modal's threads can inherit held locks and hang forever (seen as stalled
    sessions). Compiled kernels come from the numba cache, so later workers start fast."""
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    if fresh or cores not in _POOL:
        if cores in _POOL:
            _POOL[cores].shutdown(wait=False, cancel_futures=True)
        _POOL[cores] = ProcessPoolExecutor(cores, mp_context=multiprocessing.get_context("forkserver"))
    return _POOL[cores]


def _forked(function, jobs, cores):
    from concurrent.futures.process import BrokenProcessPool
    chunk = max(1, len(jobs)//(4*cores))
    try:
        return list(_pool(cores).map(function, jobs, chunksize=chunk))
    except BrokenProcessPool:  # a worker died (out of memory, crash): a fresh pool, and the batch once more
        return list(_pool(cores, fresh=True).map(function, jobs, chunksize=chunk))


# A call that hangs fails after its timeout and is retried, instead of blocking a session for half an hour.
@app.function(image=image, cpu=CORES, memory=512*CORES+1024, timeout=600, retries=modal.Retries(max_retries=2, initial_delay=1.0, backoff_coefficient=1.0), max_containers=CONTAINERS, scaledown_window=IDLE)
def relax_batch(name, xs, values):
    return _forked(_relax_one, [(name, x, v) for x, v in zip(xs, values)], CORES)


def _polish_one(job):
    from mosa.domain import get
    name, x, value = job
    return get(name).polish(x, value)


@app.function(image=image, cpu=POLISH_CORES, memory=512*POLISH_CORES+1024, timeout=600, retries=modal.Retries(max_retries=2, initial_delay=1.0, backoff_coefficient=1.0), max_containers=8, scaledown_window=IDLE)
def polish_batch(name, packings):
    return _forked(_polish_one, [(name, x, v) for x, v in packings], POLISH_CORES)


@app.function(image=image, cpu=STRATEGY_CORES, memory=512*STRATEGY_CORES+2048, timeout=300, retries=modal.Retries(max_retries=2, initial_delay=1.0, backoff_coefficient=1.0), max_containers=8, scaledown_window=IDLE)
def strategy_step(name, code, kind, payload, count, seed, n):
    from mosa import sandbox
    from mosa.domain import get
    return sandbox.step(get(name), code, kind, payload, count, seed, n, cores=STRATEGY_CORES)
