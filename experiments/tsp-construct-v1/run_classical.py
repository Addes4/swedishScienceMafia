"""Run the classical constructions (and their 2-opt / Or-opt polish) on one dataset.

Writes results/classical_<tag>.json: per-method per-instance tour lengths and total CPU seconds.

    python run_classical.py --dataset data/mctsahd/test50.npy --tag test50 [--limit N] [--methods ...]
"""

import os as _os, sys as _sys
if _os.path.exists("HOLD") and _os.environ.get("TSP_IGNORE_HOLD") != "1":
    print("HOLD file present: exiting without running (load cap requested by session cc, RUN_LOG.md)")
    _sys.exit(0)

import argparse
import json
import time

import numpy as np
from scipy.spatial import distance_matrix

import tspalgs as A

CONSTRUCT = {
    "nearest_neighbour": lambda D: A.nearest_neighbour(D, 0),
    "farthest_insertion": lambda D: A.insertion(D, 0),
    "nearest_insertion": lambda D: A.insertion(D, 1),
    "random_insertion": lambda D: A.insertion(D, 2),
    "cheapest_insertion": lambda D: A.insertion(D, 3),
    "greedy_edge": A.greedy_edge,
    "savings": A.savings,
}
POLISH = {
    "": None,
    "+2opt": A.two_opt,
    "+2opt+oropt": A.two_opt_or_opt,
}


def check_tour(t, n):
    assert t.shape[0] == n and np.array_equal(np.sort(t), np.arange(n)), "not a permutation"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--methods", nargs="*", default=None, help="construction names (default all)")
    ap.add_argument("--polish", nargs="*", default=list(POLISH), help="polish suffixes")
    a = ap.parse_args()
    X = np.load(a.dataset)
    if a.limit:
        X = X[: a.limit]
    methods = a.methods or list(CONSTRUCT)
    # warm up numba
    D0 = distance_matrix(X[0], X[0])
    for m in methods:
        t = CONSTRUCT[m](D0)
        for p in a.polish:
            if POLISH[p] is not None:
                POLISH[p](D0, t)
    out = {"dataset": a.dataset, "n_instances": int(X.shape[0]), "n": int(X.shape[1]), "methods": {}}
    for m in methods:
        for p in a.polish:
            out["methods"][m + p] = {"lengths": [], "seconds": 0.0}
    for x in X:
        D = distance_matrix(x, x)
        for m in methods:
            t0 = time.process_time()
            t = CONSTRUCT[m](D)
            tc = time.process_time() - t0
            check_tour(t, D.shape[0])
            for p in a.polish:
                rec = out["methods"][m + p]
                if POLISH[p] is None:
                    tt, extra = t, 0.0
                else:
                    t1 = time.process_time()
                    tt = POLISH[p](D, t)
                    extra = time.process_time() - t1
                    check_tour(tt, D.shape[0])
                rec["lengths"].append(float(A.tour_length(D, tt)))
                rec["seconds"] += tc + extra
    path = f"results/classical_{a.tag}.json"
    with open(path, "w") as f:
        json.dump(out, f)
    for k, v in out["methods"].items():
        print(f"{a.tag} {k:32s} mean {np.mean(v['lengths']):.4f}  cpu {v['seconds']:.2f}s")


if __name__ == "__main__":
    main()
