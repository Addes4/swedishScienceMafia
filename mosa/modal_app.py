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
app = modal.App("mosa", tags={"workspace": os.environ.get("MOSA_WORKSPACE", "")[:60]})
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


def _forked(function, jobs, cores):
    first = function(jobs[0])  # loads the compiled kernels once; forked workers inherit them
    if len(jobs) == 1:
        return [first]
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(cores, len(jobs)-1), mp_context=multiprocessing.get_context("fork")) as pool:
        return [first]+list(pool.map(function, jobs[1:], chunksize=max(1, (len(jobs)-1)//(4*cores))))


@app.function(image=image, cpu=CORES, memory=256*CORES+1024, timeout=1800, max_containers=CONTAINERS, scaledown_window=IDLE)
def relax_batch(name, xs, values):
    return _forked(_relax_one, [(name, x, v) for x, v in zip(xs, values)], CORES)


def _polish_one(job):
    from mosa.domain import get
    name, x, value = job
    return get(name).polish(x, value)


@app.function(image=image, cpu=POLISH_CORES, memory=256*POLISH_CORES+1024, timeout=1800, max_containers=8, scaledown_window=IDLE)
def polish_batch(name, packings):
    return _forked(_polish_one, [(name, x, v) for x, v in packings], POLISH_CORES)


@app.function(image=image, cpu=STRATEGY_CORES, memory=512*STRATEGY_CORES+2048, timeout=300, max_containers=8, scaledown_window=IDLE)
def strategy_step(name, code, kind, payload, count, seed, n):
    from mosa import sandbox
    from mosa.domain import get
    return sandbox.step(get(name), code, kind, payload, count, seed, n, cores=STRATEGY_CORES)
