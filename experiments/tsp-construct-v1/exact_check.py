"""Prove the optimum of a few test200 instances exactly (integer programming), to check the LKH reference.

Symmetric TSP as an integer program over edge variables, solved with HiGHS (scipy.optimize.milp):
degree-2 constraints, then subtour-elimination cuts sum_{e in delta(S)} x_e >= 2 added for every
connected component of the current solution until it is one tour. Distances are scaled by 1e6 and
rounded to integers for the solver; the proved tour is then measured in float coordinates. Single
process (HiGHS threads = 1 via scipy's default).

    python exact_check.py --k 3      # first k instances of data/mctsahd/test200.npy
Writes results/exact_check_test200.json.
"""
import argparse
import json
import time

import numpy as np
from scipy.optimize import LinearConstraint, Bounds, milp
from scipy.sparse import coo_matrix, vstack
from scipy.spatial.distance import cdist


def solve_exact(pts, time_limit=3600):
    n = len(pts)
    D = cdist(pts, pts)
    iu, ju = np.triu_indices(n, 1)
    m = len(iu)
    c = np.rint(D[iu, ju] * 1e6)
    # degree constraints
    rows = np.concatenate([iu, ju])
    cols = np.concatenate([np.arange(m), np.arange(m)])
    A_deg = coo_matrix((np.ones(2 * m), (rows, cols)), shape=(n, m)).tocsr()
    cons = [LinearConstraint(A_deg, 2, 2)]
    cuts = []
    t0 = time.time()
    rounds = 0
    while True:
        rounds += 1
        res = milp(c, constraints=cons + ([LinearConstraint(vstack(cuts), 2, np.inf)] if cuts else []),
                   integrality=np.ones(m), bounds=Bounds(0, 1),
                   options={"time_limit": max(10, time_limit - (time.time() - t0)), "mip_rel_gap": 0})
        if res.x is None:
            return None
        x = res.x > 0.5
        # components
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for e in np.flatnonzero(x):
            ra, rb = find(iu[e]), find(ju[e])
            if ra != rb:
                parent[ra] = rb
        comp = np.array([find(v) for v in range(n)])
        labels = np.unique(comp)
        if len(labels) == 1:
            # extract tour
            adj = [[] for _ in range(n)]
            for e in np.flatnonzero(x):
                adj[iu[e]].append(ju[e])
                adj[ju[e]].append(iu[e])
            tour, prev, cur = [0], -1, 0
            for _ in range(n - 1):
                nx = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
                tour.append(nx)
                prev, cur = cur, nx
            t = np.array(tour)
            L = float(D[t, np.roll(t, -1)].sum())
            return {"length": L, "rounds": rounds, "cuts": int(sum(cc.shape[0] for cc in cuts)),
                    "seconds": time.time() - t0, "status": res.message, "mip_gap": getattr(res, "mip_gap", None)}
        for lab in labels:
            S = comp == lab
            cut = (S[iu] != S[ju]).astype(float)
            cuts.append(coo_matrix(cut.reshape(1, -1)))
        if time.time() - t0 > time_limit:
            return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3)
    a = ap.parse_args()
    X = np.load("data/mctsahd/test200.npy")[: a.k]
    ref = np.load("results/lkh_test200.npy")[: a.k]
    out = []
    for i, x in enumerate(X):
        r = solve_exact(x)
        r = r or {"length": None}
        r.update({"instance": i, "lkh_reference": float(ref[i])})
        out.append(r)
        print(r, flush=True)
        json.dump(out, open("results/exact_check_test200.json", "w"), indent=1)
