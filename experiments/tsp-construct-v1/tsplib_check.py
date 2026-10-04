"""Exploratory (not pre-registered): MCTS-AHD's TSPLIB protocol (its test/test_tsplib.py) for the
interface methods. Coordinates are scaled to the unit square as MCTS-AHD does; each heuristic runs from
start nodes 0, 1 and 2; the mean float tour length times the scale is compared with the TSPLIB optimum.
MCTS-AHD's Table 11 numbers (copied from its appendix; Christofides, Greedy and Nearest insertion taken
there from Duflo et al. 2019) are listed alongside. Only 14 of its 15 instance files are in its repository
(fl417 is missing), so averages are over 14.

    python tsplib_check.py     # writes results/tsplib_check.json
"""
import importlib.util
import json
from copy import copy

import numpy as np
import warnings

warnings.filterwarnings("ignore")
from scipy.spatial import distance_matrix  # noqa: E402

OPT = {"ts225": 126643, "rat99": 1211, "bier127": 118282, "lin318": 42029, "eil51": 426, "d493": 35002,
       "kroB100": 22141, "kroC100": 20749, "ch130": 6110, "pr299": 48191, "kroA150": 26524, "pr264": 49135,
       "pr226": 80369, "pr439": 107217}
# MCTS-AHD Table 11 (gap %): Christofides, Greedy, Nearest insertion, Nearest-greedy, GPHH-best, EoH, ReEvo, MCTS-AHD
T11 = {"ts225": (5.67, 5.38, 19.93, 16.82, 7.71, 5.57, 6.56, 10.84), "rat99": (9.43, 22.30, 21.05, 21.79, 14.09, 18.78, 12.41, 10.46),
       "bier127": (13.03, 19.50, 23.05, 23.25, 15.64, 14.05, 10.79, 7.56), "lin318": (13.80, 18.75, 24.44, 25.78, 14.30, 14.03, 16.63, 14.07),
       "eil51": (15.18, 13.03, 16.14, 31.96, 10.20, 8.37, 6.47, 15.98), "d493": (9.52, 16.68, 20.39, 24.00, 15.58, 12.41, 13.43, 11.73),
       "kroB100": (9.82, 16.59, 21.53, 26.26, 14.06, 13.46, 12.20, 11.43), "kroC100": (9.08, 12.94, 24.25, 25.76, 16.22, 16.85, 15.88, 8.27),
       "ch130": (10.09, 28.40, 19.21, 25.66, 14.77, 12.26, 9.40, 10.18), "pr299": (11.23, 31.42, 25.05, 31.42, 18.24, 23.58, 20.63, 11.23),
       "kroA150": (13.44, 20.24, 19.09, 26.08, 15.59, 18.36, 11.62, 10.08), "pr264": (11.28, 11.89, 34.28, 17.87, 23.96, 18.03, 16.78, 12.27),
       "pr226": (14.17, 21.44, 28.02, 24.65, 15.51, 19.90, 18.02, 7.15), "pr439": (11.16, 20.08, 24.67, 27.36, 21.36, 21.96, 19.25, 15.12)}
T11_COLS = ["Christofides", "Greedy", "Nearest insertion", "Nearest-greedy", "GPHH-best", "EoH", "ReEvo", "MCTS-AHD"]
HEUR = ["nearest_neighbour", "fi_emit", "greedy_ls_emit", "lkh_emit"]


def load(name):
    spec = importlib.util.spec_from_file_location(name, f"heuristics/{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.select_next_node


def read(name):
    lines = open(f"data/tsplib/{name}.tsp").read().splitlines()
    i = lines.index("NODE_COORD_SECTION") + 1
    pts = []
    for ln in lines[i:]:
        if ln.strip() in ("EOF", ""):
            break
        pts.append([float(v) for v in ln.split()[1:3]])
    return np.array(pts)


def run(f, X, start):
    D = distance_matrix(X, X)
    sol, un = [start], set(range(len(X))) - {start}
    for _ in range(len(X) - 1):
        v = f(current_node=sol[-1], destination_node=start, unvisited_nodes=copy(un), distance_matrix=D.copy())
        sol.append(v)
        un.remove(v)
    return sum(D[sol[i], sol[(i + 1) % len(sol)]] for i in range(len(sol)))


if __name__ == "__main__":
    fs = {h: load(h) for h in HEUR}
    out = {}
    for name in OPT:
        data = read(name)
        scale = max(np.max(data, axis=0) - np.min(data, axis=0))
        X = (data - np.min(data, axis=0)) / scale
        out[name] = {}
        for h, f in fs.items():
            objs = [run(f, X, s) * scale for s in range(3)]
            out[name][h] = 100 * (np.mean(objs) - OPT[name]) / OPT[name]
        print(name, {h: round(v, 2) for h, v in out[name].items()}, flush=True)
    avg = {h: float(np.mean([out[n][h] for n in OPT])) for h in HEUR}
    avg_t11 = {c: float(np.mean([T11[n][i] for n in OPT])) for i, c in enumerate(T11_COLS)}
    json.dump({"per_instance": out, "average_14": avg, "mctsahd_table11_average_same_14": avg_t11}, open("results/tsplib_check.json", "w"), indent=1)
    print("ours", {h: round(v, 2) for h, v in avg.items()})
    print("MCTS-AHD Table 11 (same 14)", {c: round(v, 2) for c, v in avg_t11.items()})
