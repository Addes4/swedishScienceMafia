# EVOLVE-BLOCK-START
"""Integer-grid guillotine DP: choose grid size m, partition m x m into axis-aligned
squares (guillotine cuts) using at most n squares, maximising the sum of sides."""
import math
import numpy as np


def _grid(n):
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq[:n]


def solve(n):
    if n <= 0:
        return []
    if n > 400:
        return _grid(n)
    M = min(20, max(12, math.isqrt(n) + 1))
    K = min(n, M * M)
    f = {}
    for a in range(1, M + 1):
        for b in range(a, M + 1):
            arr = np.full(K + 1, min(a, b), dtype=np.int64)
            arr[0] = 0
            # guillotine cuts
            for (p, q, cuts) in ((a, b, "a"), (a, b, "b")):
                pass
            for cutdim in (0, 1):
                tot = a if cutdim == 0 else b
                for c in range(1, tot // 2 + 1):
                    if cutdim == 0:
                        d1, d2 = (c, b), (tot - c, b)
                    else:
                        d1, d2 = (a, c), (a, tot - c)
                    A = f[(min(d1), max(d1))] if (min(d1), max(d1)) in f else None
                    B = f[(min(d2), max(d2))] if (min(d2), max(d2)) in f else None
                    if A is None or B is None:
                        continue
                    g = arr.copy()
                    for k1 in range(0, K + 1):
                        cand = A[k1] + B[:K + 1 - k1]
                        np.maximum(g[k1:], cand, out=g[k1:])
                    arr = g
            f[(a, b)] = arr

    def F(a, b):
        return f[(min(a, b), max(a, b))]

    best_m, best_v = 1, -1.0
    for m in range(1, M + 1):
        v = F(m, m)[K] / m
        if v > best_v + 1e-12:
            best_v, best_m = v, m
    m = best_m
    res = []

    def rec(a, b, k, x, y):
        if k <= 0:
            return
        k = min(k, K)
        arr = F(a, b)
        val = arr[k]
        s = min(a, b)
        if val == s:
            res.append((x, y, s))
            return
        for cutdim in (0, 1):
            tot = a if cutdim == 0 else b
            for c in range(1, tot):
                if cutdim == 0:
                    d1, d2 = (c, b), (tot - c, b)
                    o2 = (x + c, y)
                else:
                    d1, d2 = (a, c), (a, tot - c)
                    o2 = (x, y + c)
                A = F(*d1)
                B = F(*d2)
                for k1 in range(0, k + 1):
                    if A[k1] + B[k - k1] == val:
                        rec(d1[0], d1[1], k1, x, y)
                        rec(d2[0], d2[1], k - k1, o2[0], o2[1])
                        return
        res.append((x, y, s))

    rec(m, m, min(n, K), 0, 0)
    out = []
    for (x, y, s) in res:
        out.append(((x + s / 2.0) / m, (y + s / 2.0) / m, 0.0, s / m))
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END
