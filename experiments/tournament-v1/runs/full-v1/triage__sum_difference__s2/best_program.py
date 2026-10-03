# EVOLVE-BLOCK-START
"""Lattice simplex construction: points of Z_{>=0}^d with coordinate sum <= n,
embedded into the integers with a carry-free base."""
import math
import numpy as np


def _formula_score(d, n):
    size = math.comb(n + d, d)
    ns = math.comb(2 * n + d, d)
    nd = 0
    for j in range(0, min(d, n) + 1):
        for k in range(0, min(d - j, n) + 1):
            nd += math.comb(d, j) * math.comb(d - j, k) * math.comb(n, j) * math.comb(n, k)
    return math.log(nd) / math.log(ns) + (1 - 1.0 / size) / 100


def _build(d, n):
    B = 2 * n + 1
    # list of (value, used) built dimension by dimension
    vals = np.zeros(1, dtype=np.int64)
    used = np.zeros(1, dtype=np.int64)
    for i in range(d):
        nv = []
        nu = []
        w = B ** i
        for x in range(n + 1):
            m = used + x <= n
            nv.append(vals[m] + x * w)
            nu.append(used[m] + x)
        vals = np.concatenate(nv)
        used = np.concatenate(nu)
    return vals


def _exact(a):
    a = np.asarray(a, dtype=np.int64)
    s = np.unique((a[:, None] + a[None, :]).ravel())
    df = np.unique((a[:, None] - a[None, :]).ravel())
    return math.log(len(df)) / math.log(len(s)) + (1 - 1.0 / len(a)) / 100


def solve():
    cands = []
    for n in range(1, 200):
        for d in range(1, 64):
            if n == 0:
                continue
            size = math.comb(n + d, d)
            if size > 4000:
                break
            if size < 2:
                continue
            B = 2 * n + 1
            if float(B) ** d > 1e15:
                break
            cands.append((_formula_score(d, n), d, n))
    cands.sort(reverse=True)
    best = None
    best_s = -1.0
    for _, d, n in cands[:5]:
        try:
            a = _build(d, n)
            s = _exact(a)
        except Exception:
            continue
        if s > best_s:
            best_s = s
            best = a
    if best is None:
        return [7, 15, 18, 22, -3, -2]
    return [int(x) for x in np.unique(best)]
# EVOLVE-BLOCK-END
