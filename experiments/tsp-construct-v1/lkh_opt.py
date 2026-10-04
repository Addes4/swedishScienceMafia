"""Reference optimum for each instance with LKH (via the elkai package, which bundles LKH).

Coordinates are scaled by 1e7 and solved as EUC_2D (LKH rounds each distance to an integer, so the
rounding error is below 1e-7 per edge). The returned tour is then measured in the original float
coordinates. MCTS-AHD's appendix used RUNS = 10, MAX_TRIALS = 10000; we use RUNS = 3 and LKH's
default MAX_TRIALS = n, which gave identical tours on 16 n=50 and 6 n=200 checks and is about 40x
faster (see RESULTS.md, work log).

Usage:
    python lkh_opt.py --dataset data/test50.npy --out results/lkh_test50.npy [--workers 4] [--limit N]
"""

import os as _os, sys as _sys
if _os.path.exists("HOLD") and _os.environ.get("TSP_IGNORE_HOLD") != "1":
    print("HOLD file present: exiting without running (load cap requested by session cc, RUN_LOG.md)")
    _sys.exit(0)

import argparse
import time
from multiprocessing import Pool

import numpy as np
from elkai import _elkai

SCALE = 1e7


def lkh_tour(pts, runs=3, max_trials=None, seed=1):
    n = pts.shape[0]
    if max_trials is None:
        max_trials = n
    params = f"RUNS = {runs}\nMAX_TRIALS = {max_trials}\nSEED = {seed}\nPROBLEM_FILE = :stdin:\n"
    lines = [f"TYPE : TSP", f"DIMENSION : {n}", "EDGE_WEIGHT_TYPE : EUC_2D", "NODE_COORD_SECTION"]
    for i, (x, y) in enumerate(pts):
        lines.append(f"{i + 1} {x * SCALE:.3f} {y * SCALE:.3f}")
    problem = "\n".join(lines) + "\n"
    sol = _elkai.solve_problem(params, problem)
    return np.array([s - 1 for s in sol], dtype=np.int64)


def length(pts, tour):
    p = pts[tour]
    return float(np.sqrt(((p - np.roll(p, -1, axis=0)) ** 2).sum(1)).sum())


def _one(pts):
    t = lkh_tour(pts)
    assert sorted(t.tolist()) == list(range(pts.shape[0]))
    return length(pts, t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    X = np.load(a.dataset)
    if a.limit:
        X = X[: a.limit]
    t0 = time.time()
    with Pool(a.workers) as pool:
        L = pool.map(_one, list(X), chunksize=4)
    L = np.array(L)
    np.save(a.out, L)
    print(f"{a.dataset}: {len(L)} instances, mean LKH length {L.mean():.6f}, {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
