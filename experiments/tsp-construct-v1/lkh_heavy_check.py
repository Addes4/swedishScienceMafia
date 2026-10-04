"""Positive-control check at n = 200: MCTS-AHD's LKH setting (RUNS = 10, MAX_TRIALS = 10000) on the
first K test200 instances, compared with our reference (RUNS = 3, MAX_TRIALS = n).

    python lkh_heavy_check.py --k 20 --workers 3
"""

import os as _os, sys as _sys
if _os.path.exists("HOLD") and _os.environ.get("TSP_IGNORE_HOLD") != "1":
    print("HOLD file present: exiting without running (load cap requested by session cc, RUN_LOG.md)")
    _sys.exit(0)

import argparse
import json
from multiprocessing import Pool

import numpy as np

from lkh_opt import length, lkh_tour


def _one(x):
    return length(x, lkh_tour(x, runs=10, max_trials=10000))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    X = np.load("data/mctsahd/test200.npy")[: a.k]
    ref = np.load("results/lkh_test200.npy")[: a.k]
    with Pool(a.workers) as p:
        H = np.array(p.map(_one, list(X), chunksize=1))
    out = {"k": a.k, "heavy": H.tolist(), "reference": ref.tolist(),
           "max_reference_minus_heavy": float((ref - H).max()), "n_heavy_shorter_by_1e-6": int(((ref - H) > 1e-6).sum())}
    json.dump(out, open("results/lkh_heavy_check_test200.json", "w"), indent=1)
    print(out["max_reference_minus_heavy"], out["n_heavy_shorter_by_1e-6"])
