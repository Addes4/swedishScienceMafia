"""Evaluate a select_next_node heuristic exactly as MCTS-AHD's tsp_constructive/eval.py does.

The loop below is copied from MCTS-AHD (github.com/zz1358m/MCTS-AHD-master, commit in
data/MCTS-AHD-COMMIT.txt, MIT licence): start at node 0, destination 0, call
select_next_node(current_node, destination_node, unvisited_nodes=copy(set), distance_matrix=copy)
once per step, append its answer, and measure the closed tour.

    python eval_interface.py heuristics/<file>.py --dataset data/mctsahd/test50.npy --tag test50 \
        [--limit N] [--workers 4]

Writes results/interface_<heuristic>_<tag>.json with per-instance lengths and per-instance wall
seconds (wall time inflates under load; compare speeds only within one run).
"""

import os as _os, sys as _sys
if _os.path.exists("HOLD") and _os.environ.get("TSP_IGNORE_HOLD") != "1":
    print("HOLD file present: exiting without running (load cap requested by session cc, RUN_LOG.md)")
    _sys.exit(0)

import argparse
import importlib.util
import json
import os
import sys
import time
import warnings
from copy import copy
from multiprocessing import Pool

import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.spatial import distance_matrix  # noqa: E402  (same call as MCTS-AHD's eval.py)

_H = None


def _load(path):
    spec = importlib.util.spec_from_file_location("heuristic", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["heuristic"] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, "select_next_node_v2", None) or mod.select_next_node


def _init(path):
    global _H
    _H = _load(path)


def eval_heuristic(node_positions):
    select_next_node = _H
    problem_size = node_positions.shape[0]
    dist_mat = distance_matrix(node_positions, node_positions)
    start_node = 0
    solution = [start_node]
    unvisited = set(range(problem_size))
    unvisited.remove(start_node)
    for _ in range(problem_size - 1):
        next_node = select_next_node(
            current_node=solution[-1],
            destination_node=start_node,
            unvisited_nodes=copy(unvisited),
            distance_matrix=dist_mat.copy(),
        )
        solution.append(next_node)
        if next_node in unvisited:
            unvisited.remove(next_node)
        else:
            raise KeyError(f"Node {next_node} is already visited.")
    obj = 0
    for i in range(problem_size):
        obj += dist_mat[solution[i], solution[(i + 1) % problem_size]]
    return obj


def _timed(x):
    t0 = time.perf_counter()
    L = eval_heuristic(x)
    return float(L), time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("heuristic")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    X = np.load(a.dataset)[a.start:]
    if a.limit:
        X = X[: a.limit]
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(a.heuristic,)) as pool:
        res = pool.map(_timed, list(X), chunksize=1)
    name = os.path.splitext(os.path.basename(a.heuristic))[0]
    out = {
        "heuristic": a.heuristic,
        "dataset": a.dataset,
        "start": a.start,
        "n_instances": len(res),
        "lengths": [r[0] for r in res],
        "wall_seconds": [r[1] for r in res],
    }
    suffix = f"_{a.start}" if a.start else ""
    path = f"results/interface_{name}_{a.tag}{suffix}.json"
    with open(path, "w") as f:
        json.dump(out, f)
    L = np.array(out["lengths"])
    print(f"{name} {a.tag}: {len(L)} instances, mean {L.mean():.4f}, "
          f"median wall {np.median(out['wall_seconds']):.3f}s/instance, total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
