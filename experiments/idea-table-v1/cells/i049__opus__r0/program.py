# EVOLVE-BLOCK-START
"""Exact guillotine integer-tiling DP over all grid resolutions.

F[(w,h)][k] = max sum of integer square sides using at most k squares inside an
integer w x h rectangle, where the tiling is a recursive guillotine partition
(each leaf is one square of side min(w,h), or empty). Values are independent of
the grid resolution, so one table grown in max(w,h) serves every grid M:
answer(M) = F[(M,M)][n] / M.
"""
import math
import time
import numpy as np

NEG = -10 ** 9


def _comb(a, b, L):
    c = np.full(L, NEG, dtype=np.int64)
    if len(a) > len(b):
        a, b = b, a
    lb = len(b)
    for i in range(len(a)):
        if i >= L:
            break
        m = min(lb, L - i)
        seg = c[i:i + m]
        np.maximum(seg, a[i] + b[:m], out=seg)
    return c


def _get(vec, k):
    return int(vec[min(k, len(vec) - 1)])


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    F = {}
    best_ratio = -1.0
    best_M = 1
    budget = 20.0
    Mmax = 120
    h = 0
    while h < Mmax:
        h += 1
        if time.time() - t0 > budget:
            break
        for w in range(1, h + 1):
            L = min(n, w * h) + 1
            s = min(w, h)
            vec = np.full(L, s, dtype=np.int64)
            vec[0] = 0
            # vertical cuts (split width w)
            for x in range(1, w // 2 + 1):
                a = F[(min(x, h), max(x, h))]
                b = F[(min(w - x, h), max(w - x, h))]
                np.maximum(vec, _comb(a, b, L), out=vec)
            # horizontal cuts (split height h)
            for y in range(1, h // 2 + 1):
                a = F[(min(w, y), max(w, y))]
                b = F[(min(w, h - y), max(w, h - y))]
                np.maximum(vec, _comb(a, b, L), out=vec)
            vec = np.maximum.accumulate(vec)
            F[(w, h)] = vec
        r = _get(F[(h, h)], n) / h
        if r > best_ratio + 1e-12:
            best_ratio = r
            best_M = h

    M = best_M
    squares = []

    def look(w, h):
        return F[(min(w, h), max(w, h))]

    def build(w, h, k, x0, y0):
        val = _get(look(w, h), k)
        if k <= 0 or val <= 0:
            return
        s = min(w, h)
        if val == s:
            squares.append((x0, y0, s))
            return
        for x in range(1, w):
            a = look(x, h)
            b = look(w - x, h)
            for i in range(0, k + 1):
                if _get(a, i) + _get(b, k - i) == val:
                    build(x, h, i, x0, y0)
                    build(w - x, h, k - i, x0 + x, y0)
                    return
        for y in range(1, h):
            a = look(w, y)
            b = look(w, h - y)
            for i in range(0, k + 1):
                if _get(a, i) + _get(b, k - i) == val:
                    build(w, y, i, x0, y0)
                    build(w, h - y, k - i, x0, y0 + y)
                    return
        squares.append((x0, y0, s))

    build(M, M, n, 0, 0)

    out = []
    for (x0, y0, s) in squares[:n]:
        side = s / M
        cx = (x0 + s / 2.0) / M
        cy = (y0 + s / 2.0) / M
        side = max(0.0, side - 1e-12)
        out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, side))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
