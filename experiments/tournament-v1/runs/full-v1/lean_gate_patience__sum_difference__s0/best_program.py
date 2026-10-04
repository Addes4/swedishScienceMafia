# EVOLVE-BLOCK-START
"""Search over simplex-like lattice sets embedded into integers."""
import math
import time
import numpy as np


def _score_arr(a):
    n = len(a)
    d = np.unique((a[:, None] - a[None, :]).ravel()).size
    s = np.unique((a[:, None] + a[None, :]).ravel()).size
    return math.log(d) / math.log(s) + (1 - 1 / n) / 100


def _points(d, n):
    res = []

    def rec(pref, left, k):
        if k == d:
            res.append(tuple(pref))
            return
        for v in range(left + 1):
            pref.append(v)
            rec(pref, left - v, k + 1)
            pref.pop()

    rec([], n, 0)
    return res


def _embed(d, n):
    pts = _points(d, n)
    B = 2 * n + 1
    w = [B ** i for i in range(d)]
    vals = [sum(c * x for c, x in zip(p, w)) for p in pts]
    return vals


def solve():
    start = time.time()
    cands = []
    for d in range(1, 40):
        for n in range(1, 60):
            size = math.comb(n + d, d)
            if size > 4000:
                break
            if size < 4:
                continue
            if n * (2 * n + 1) ** (d - 1) > 9e14:
                break
            cands.append((size, d, n))
    cands.sort()
    best, best_s = [0, 1, 3], -1
    for size, d, n in cands:
        el = time.time() - start
        # rough cost estimate: ~ size^2 * 1e-7 s
        est = size * size * 1.2e-7
        if el + est > 105:
            continue
        vals = _embed(d, n)
        a = np.array(vals, dtype=np.int64)
        s = _score_arr(a)
        if s > best_s:
            best_s, best = s, vals
    return sorted(set(int(v) for v in best))
# EVOLVE-BLOCK-END
