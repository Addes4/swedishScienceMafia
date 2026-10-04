"""online-frontier-v1: online bin-packing policies, FunSearch's evaluator, the exact optimum and the
distribution class. See PROTOCOL.md.

Policies over the gap histogram take (N, s, C, t, T) and return the gap g of the bin that receives
item s (g == C opens a new bin). N[g] is the number of open bins with remaining capacity g,
0 < g < C. Policies through FunSearch's evaluator are `priority(item, bins)` functions.
"""
import gzip
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))
sys.path.insert(0, str(ROOT))
import verify  # noqa: E402
from falsify.funsearch_heuristics import ab_priority  # noqa: E402

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "problems" / "bin_packing_online" / "baselines" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.priority


FS_W = _load("funsearch_weibull")
FS_OR = _load("funsearch_or")


# ---------------------------------------------------------------- policies over the gap histogram

def pack_hist(items, C, rule):
    """Number of bins a gap-histogram rule uses on `items`."""
    N = [0] * (C + 1)
    opened = 0
    T = len(items)
    for t, s in enumerate(items, start=1):
        g = rule(N, s, C, t, T)
        if g == C:
            opened += 1
        else:
            assert N[g] > 0 and g >= s
            N[g] -= 1
        if g - s > 0:
            N[g - s] += 1
    return opened


def best_fit(N, s, C, t, T):
    return next((g for g in range(s, C) if N[g]), C)


def sum_of_squares(N, s, C, t, T):
    """Csirik et al.: minimise sum_{0<g<C} N(g)^2; ties to the smaller resulting gap."""
    best, best_g = None, C
    for g in range(s, C + 1):
        if g < C and not N[g]:
            continue
        r = g - s
        d = (1 - 2 * N[g] if g < C else 0) + (2 * N[r] + 1 if r > 0 else 0)
        if best is None or (d, r) < best:
            best, best_g = (d, r), g
    return best_g


def _pd_exp(N, s, C, eps, kappa=1.0):
    """Gupta & Radovanovic Algorithm 1 in gap terms: minimise (#bins) + (kappa/eps) sum_{0<g<C} exp(-eps N(g))."""
    c = kappa / eps
    best, best_g = None, C
    for g in range(s, C + 1):
        if g < C and not N[g]:
            continue
        r = g - s
        d = 0.0
        if g < C:
            d += c * (math.exp(-eps * (N[g] - 1)) - math.exp(-eps * N[g]))   # level depleted
        else:
            d += 1.0                                                          # a new bin
        if r > 0:
            d += c * (math.exp(-eps * (N[r] + 1)) - math.exp(-eps * N[r]))    # level filled
        if best is None or (d, r) < best:
            best, best_g = (d, r), g
    return best_g


def pd_exp(N, s, C, t, T):
    """Open-ended setting (their Theorem 3): eps_t = sqrt(C / (2 (t + 1))), kappa = 1."""
    return _pd_exp(N, s, C, math.sqrt(C / (2 * (t + 1))))


def pd_exp_T(N, s, C, t, T):
    """Known horizon (their Theorem 2): eps = sqrt(C / T), kappa = 1."""
    return _pd_exp(N, s, C, math.sqrt(C / T))


HIST_POLICIES = {"BF": best_fit, "SS": sum_of_squares, "PD-exp": pd_exp, "PD-exp-T": pd_exp_T}


# ---------------------------------------------------------------- FunSearch's evaluator

def ss_view(item, bins, C=100):
    """SS restricted to FunSearch's stateless view: N(g) counted over the shown bins only."""
    N = np.bincount(bins[bins < C], minlength=C + 1)
    r = bins - item
    d = np.where(bins < C, 1 - 2 * N[bins], 0) + np.where(r > 0, 2 * N[np.clip(r, 0, C)] + 1, 0)
    return -(d + 1e-6 * r)


def ab_worst_fit(a=1, b=21, C=100):
    """Herrmann & Pallez ab-WorstFit, vectorised; identical scores to falsify.funsearch_heuristics.ab_priority."""
    def priority(item, bins):
        bins = np.asarray(bins)
        r = bins - item
        return np.where(bins <= item + a, C - bins + 1.0,
               np.where(bins <= item + b, -2.0,
               np.where(bins == C, -1.0, -1.0 / np.maximum(r, 1))))
    return priority


def pack_funsearch(items, C, priority, compact=True):
    """FunSearch's evaluator: priority sees every bin the item fits in, unused ones included, in bin order;
    the item goes to the first highest score. compact=True passes only the bins up to two past the highest
    opened index (all later bins are unused); see PROTOCOL.md for why this cannot change a choice."""
    n = len(items)
    bins = np.full(n, C, dtype=np.int64)
    top = -1                                   # highest opened index
    for it in items:
        view = bins[: min(n, top + 3)] if compact else bins
        valid = np.nonzero(view - it >= 0)[0]
        scores = np.asarray(priority(it, view[valid]), dtype=np.float64)
        j = int(valid[np.argmax(scores)])
        bins[j] -= it
        top = max(top, j)
    return int((bins != C).sum())


# ---------------------------------------------------------------- bounds and the exact optimum

def l1_bound(items, C):
    return math.ceil(sum(items) / C)


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


# ---------------------------------------------------------------- distribution class

def weibull_pmf(C=100, scale=45.0, shape=3.0):
    """Exact probabilities of verify.items_for: min(C, max(1, int(W))), W ~ Weibull(scale, shape)."""
    F = lambda x: 1.0 - math.exp(-((x / scale) ** shape))
    p = {s: F(s + 1) - F(s) for s in range(2, C)}
    p[1] = F(2)                                # int(W) in {0, 1}
    p[C] = 1.0 - F(C)                          # W >= C
    return p


def distribution_class(p, C):
    """Minimum expected waste per item (linear waste if > 0) and, if zero, whether p lies in the interior of
    the cone of perfect packings (bounded waste) or on its boundary (sqrt-n waste)."""
    sizes = sorted(p, reverse=True)
    scale = 1.0 / min(p.values())               # the cone is scale-invariant; keep coefficients O(1)..O(1e5)
    q = np.array([p[s] * scale for s in sizes])
    arcs = _arcflow(C, sizes)
    sizes_, A_cons, A_cov, cost = _flow_matrices(C, arcs, sizes)
    assert sizes_ == sizes
    lp = linprog(cost, A_ub=-A_cov, b_ub=-q, A_eq=A_cons, b_eq=np.zeros(C - 1), bounds=(0, None), method="highs")
    bins_per_unit = lp.fun / scale
    mean_size = sum(s * p[s] for s in sizes)
    waste_rate = bins_per_unit - mean_size / C  # bins of waste per item
    out = {"lp_status": lp.status, "bins_per_item": bins_per_unit, "waste_per_item": waste_rate}
    if waste_rate > 1e-9:
        out["class"] = "linear waste"
        return out
    # Interior test on perfect packings only (no loss arcs): for each size j, can p move by +-t e_j?
    perfect = [k for k, a in enumerate(arcs) if a[2] != 0]
    Ac = A_cons[:, perfect]
    Av = A_cov[:, perfect]
    margins = []
    for j in range(len(sizes)):
        for sign in (+1.0, -1.0):
            # variables: flows (perfect arcs) and t; maximise t s.t. Av x = q + sign*t*e_j, Ac x = 0, t <= 1
            e = np.zeros(len(sizes)); e[j] = sign
            A_eq = sp.vstack([sp.hstack([Av, sp.csr_matrix(-e.reshape(-1, 1))]),
                              sp.hstack([Ac, sp.csr_matrix((C - 1, 1))])]).tocsr()
            b_eq = np.concatenate([q, np.zeros(C - 1)])
            c = np.zeros(len(perfect) + 1); c[-1] = -1.0
            r = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * len(perfect) + [(0, 1.0)], method="highs")
            margins.append({"size": sizes[j], "sign": int(sign), "status": r.status,
                            "t": (-r.fun if r.status == 0 else None)})
    feasible = [m["t"] for m in margins if m["t"] is not None]
    min_t = min(feasible) if len(feasible) == len(margins) else None
    out["interior_min_margin"] = min_t
    out["interior_margins"] = margins
    out["class"] = ("bounded waste (interior)" if (min_t is not None and min_t > 1e-7)
                    else "perfectly packable, boundary (sqrt-n waste)")
    return out


# ---------------------------------------------------------------- instances

def load_released_weibull():
    d = json.load(gzip.open(ROOT / "experiments" / "bp-ceiling-v1" / "funsearch_weibull5k_test.json.gz"))
    return {k: (v["capacity"], [int(x) for x in v["items"]]) for k, v in d["instances"].items()}


def load_orlib(i, folder=HERE / "data"):
    t = (folder / f"binpack{i}.txt").read_text().split()
    n, k, out = int(t[0]), 1, {}
    for _ in range(n):
        name, cap, m, best = t[k], int(float(t[k + 1])), int(t[k + 2]), int(t[k + 3])
        k += 4
        out[name] = (cap, [int(float(x)) for x in t[k:k + m]], best)
        k += m
    return out


def fresh(seed, n):
    return 100, list(verify.items_for(seed, n))
