"""Exploratory behavioural checks on MCTS-AHD's val50 set (not part of the confirmatory protocol).

1. Does Clade-AHD's released heuristic build exactly the nearest-neighbour tour on every instance?
2. HiFo-Prompt's released heuristic averages 8 'lookahead simulations' that are deterministic. Does
   simulations=1 give the identical tour on every instance, and how much faster is it?

    python checks/behaviour.py
"""
import importlib.util
import json
import sys
import time
from copy import copy

import numpy as np
import warnings

warnings.filterwarnings("ignore")
from scipy.spatial import distance_matrix  # noqa: E402


def load(path):
    spec = importlib.util.spec_from_file_location(path, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.select_next_node


def tour(f, x):
    D = distance_matrix(x, x)
    sol, un = [0], set(range(1, len(x)))
    for _ in range(len(x) - 1):
        v = f(current_node=sol[-1], destination_node=0, unvisited_nodes=copy(un), distance_matrix=D.copy())
        sol.append(v)
        un.remove(v)
    return sol


X = np.load("data/mctsahd/val50.npy")
out = {}
nn, cl = load("heuristics/nearest_neighbour.py"), load("heuristics/fetched/clade_released.py")
out["clade_equals_nn_instances"] = int(sum(tour(nn, x) == tour(cl, x) for x in X))
h8, h1 = load("heuristics/hifo_best.py"), load("checks/hifo_best_1sim.py")
same, t8, t1 = 0, 0.0, 0.0
for x in X[:32]:
    a = time.perf_counter(); s8 = tour(h8, x); b = time.perf_counter(); s1 = tour(h1, x); c = time.perf_counter()
    same += s8 == s1; t8 += b - a; t1 += c - b
out.update({"instances": int(len(X)), "hifo_instances_checked": 32, "hifo_1sim_identical": int(same),
            "hifo_seconds_8sim": t8, "hifo_seconds_1sim": t1})
json.dump(out, open("checks/behaviour_val50.json", "w"), indent=1)
print(out)
