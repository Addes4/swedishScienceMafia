# EVOLVE-BLOCK-START
"""Baseline: the largest k x k grid that fits, plus size-zero squares for the rest."""
import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    import numpy as np
    import sys
    sys.setrecursionlimit(10000)
    if n <= 150:
        M = min(math.isqrt(n) + 9, 20)
    else:
        M = min(math.isqrt(n) + 4, 16)
    f = {}

    def get(w, h):
        return f[(w, h)] if w <= h else f[(h, w)]

    def comb(f1, f2):
        res = np.zeros(n + 1, dtype=np.int64)
        for a in range(n + 1):
            np.maximum(res[a:], f1[a] + f2[:n + 1 - a], out=res[a:])
        return res

    for w in range(1, M + 1):
        for h in range(w, M + 1):
            best = np.zeros(n + 1, dtype=np.int64)
            best[1:] = min(w, h)
            for a in range(1, w // 2 + 1):
                np.maximum(best, comb(get(a, h), get(w - a, h)), out=best)
            for b in range(1, h // 2 + 1):
                np.maximum(best, comb(get(w, b), get(w, h - b)), out=best)
            f[(w, h)] = best

    bm, bv = 1, -1.0
    for m in range(1, M + 1):
        v = f[(m, m)][n] / m
        if v > bv + 1e-12:
            bv, bm = v, m

    m = bm
    out = []

    def rec(w, h, k, ox, oy):
        if k <= 0 or w <= 0 or h <= 0:
            return
        target = int(get(w, h)[k])
        if target == 0:
            return
        if target == min(w, h):
            s = min(w, h)
            out.append(((ox + s / 2.0) / m, (oy + s / 2.0) / m, 0.0, s / m))
            return
        for a in range(1, w // 2 + 1):
            f1, f2 = get(a, h), get(w - a, h)
            for ka in range(k + 1):
                if f1[ka] + f2[k - ka] == target:
                    rec(a, h, ka, ox, oy)
                    rec(w - a, h, k - ka, ox + a, oy)
                    return
        for b in range(1, h // 2 + 1):
            f1, f2 = get(w, b), get(w, h - b)
            for kb in range(k + 1):
                if f1[kb] + f2[k - kb] == target:
                    rec(w, b, kb, ox, oy)
                    rec(w, h - b, k - kb, ox, oy + b)
                    return

    rec(m, m, n, 0, 0)
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END