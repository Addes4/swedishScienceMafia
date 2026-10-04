"""Exact optimum by the arc-flow integer program: `_arcflow`, `_flow_matrices` and `optimum`, copied
verbatim from experiments/online-frontier-v1/frontier.py (branch exp/online-frontier, SHA-256 of that file
3b74ed1882263d45fb5c976e282b36815346f9c5ceb484ddb8c0e3b79841cc39; full copy in frontier.py here)."""
import math

import numpy as np
import scipy.sparse as sp
from scipy.optimize import Bounds, LinearConstraint, milp

def _arcflow(C, sizes):
    """Arc-flow graph (Valerio de Carvalho 1999) with items in non-increasing order along each path.
    Returns arcs as (tail, head, size); size 0 marks a loss arc."""
    sizes = sorted(set(sizes), reverse=True)
    reach = {0}
    arcs = []
    for s in sizes:                            # nodes reachable with items >= s
        new = set(reach)
        frontier = sorted(reach)
        while frontier:
            nxt = []
            for u in frontier:
                if u + s <= C and (u + s) not in new:
                    new.add(u + s)
                    nxt.append(u + s)
            frontier = nxt
        for u in sorted(new):
            if u + s <= C:
                arcs.append((u, u + s, s))
        reach = new
    arcs += [(u, u + 1, 0) for u in range(1, C)]
    return arcs

def _flow_matrices(C, arcs, sizes):
    """Conservation rows for nodes 1..C-1 and one coverage row per size."""
    sizes = sorted(set(sizes), reverse=True)
    idx = {s: k for k, s in enumerate(sizes)}
    rows, cols, vals = [], [], []
    for j, (u, v, s) in enumerate(arcs):
        if 1 <= u <= C - 1:
            rows.append(u - 1); cols.append(j); vals.append(-1.0)
        if 1 <= v <= C - 1:
            rows.append(v - 1); cols.append(j); vals.append(1.0)
    A_cons = sp.csr_matrix((vals, (rows, cols)), shape=(C - 1, len(arcs)))
    rows, cols = zip(*[(idx[s], j) for j, (u, v, s) in enumerate(arcs) if s]) if arcs else ((), ())
    A_cov = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(sizes), len(arcs)))
    cost = np.array([1.0 if u == 0 else 0.0 for (u, v, s) in arcs])
    return sizes, A_cons, A_cov, cost

def optimum(items, C, time_limit=600.0):
    """Exact minimum number of bins by the arc-flow integer program (HiGHS)."""
    demand = {}
    for x in items:
        demand[x] = demand.get(x, 0) + 1
    arcs = _arcflow(C, demand)
    sizes, A_cons, A_cov, cost = _flow_matrices(C, arcs, demand)
    d = np.array([demand[s] for s in sizes], dtype=float)
    res = milp(cost, integrality=np.ones(len(arcs)), bounds=Bounds(0, np.inf),
               constraints=[LinearConstraint(A_cons, 0, 0), LinearConstraint(A_cov, d, np.inf)],
               options={"time_limit": time_limit, "disp": False})
    out = {"status": int(res.status), "message": res.message, "arcs": len(arcs)}
    if res.x is not None:
        out["opt"] = int(round(res.fun))
    bound = getattr(res, "mip_dual_bound", None)
    if bound is not None and np.isfinite(bound):
        out["dual_bound"] = int(math.ceil(bound - 1e-6))
    out["proved"] = res.status == 0
    return out
