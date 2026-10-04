"""Extract an explicit packing from the arc-flow solution and check it (used for instances where the solver
beats OR-Library's listed value)."""
import sys, json, numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
import frontier as F

def packing(items, C):
    demand = {}
    for x in items: demand[x] = demand.get(x, 0) + 1
    arcs = F._arcflow(C, demand)
    sizes, A_cons, A_cov, cost = F._flow_matrices(C, arcs, demand)
    d = np.array([demand[s] for s in sizes], float)
    res = milp(cost, integrality=np.ones(len(arcs)), bounds=Bounds(0, np.inf),
               constraints=[LinearConstraint(A_cons, 0, 0), LinearConstraint(A_cov, d, np.inf)], options={"time_limit": 600})
    flow = {a: int(round(v)) for a, v in zip(arcs, res.x) if round(v) > 0}
    bins = []
    while any(flow.get(a, 0) for a in flow if a[0] == 0):
        u, path = 0, []
        while u != C:
            a = next(a for a in flow if a[0] == u and flow[a] > 0)
            flow[a] -= 1; path.append(a[2]); u = a[1]
        bins.append([s for s in path if s])
    # assign actual items (drop overcovered copies)
    left = dict(demand); packed = []
    for b in bins:
        kept = []
        for s in b:
            if left.get(s, 0) > 0: left[s] -= 1; kept.append(s)
        packed.append(kept)
    assert all(v == 0 for v in left.values()), "not all items packed"
    assert all(sum(b) <= C for b in packed), "capacity violated"
    assert sorted(x for b in packed for x in b) == sorted(items)
    return [b for b in packed if b]

out = {}
for setno, name in [(1, "u120_08"), (1, "u120_19"), (2, "u250_07"), (2, "u250_12")]:
    C, items, listed = F.load_orlib(setno)[name]
    p = packing(items, C)
    out[name] = {"listed": listed, "bins": len(p), "loads": sorted(sum(b) for b in p), "packing": p}
    print(name, "listed", listed, "verified packing with", len(p), "bins; L1", F.l1_bound(items, C), "L2", F.verify.l2_bound(items, C), flush=True)
json.dump(out, open("or_improved_packings.json", "w"))
