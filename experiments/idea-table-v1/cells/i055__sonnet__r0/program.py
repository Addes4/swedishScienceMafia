# EVOLVE-BLOCK-START
"""Guillotine DP on an integer board: F[w][h][m] = max total side using at most m
squares in a w x h rectangle; choose the best board size k and rebuild the layout."""
import math
import numpy as np


def _conv(A, B, M):
    res = np.zeros(M + 1, dtype=np.int64)
    for a in range(M + 1):
        np.maximum(res[a:], A[a] + B[:M + 1 - a], out=res[a:])
    return res


def solve(n):
    K = 16
    M = min(n, K * K)
    F = {}

    def get(a, b):
        return F[(a, b)] if a >= b else F[(b, a)]

    for w in range(1, K + 1):
        for h in range(1, w + 1):
            best = np.full(M + 1, min(w, h), dtype=np.int64)
            best[0] = 0
            for x in range(1, w // 2 + 1):
                best = np.maximum(best, _conv(get(x, h), get(w - x, h), M))
            for y in range(1, h // 2 + 1):
                best = np.maximum(best, _conv(get(w, y), get(w, h - y), M))
            F[(w, h)] = best

    # choose best board size
    bestk, bestv = 1, -1.0
    for k in range(1, K + 1):
        v = get(k, k)[min(n, M)] / k
        if v > bestv + 1e-12:
            bestv, bestk = v, k
    k = bestk

    out = []

    def rec(x0, y0, w, h, m):
        if m <= 0 or w <= 0 or h <= 0:
            return
        m = min(m, M)
        val = int(get(w, h)[m])
        if val == 0:
            return
        if val == min(w, h):
            s = min(w, h)
            out.append((x0, y0, s))
            return
        for x in range(1, w):
            A = get(x, h)
            B = get(w - x, h)
            for a in range(0, m + 1):
                if int(A[min(a, M)]) + int(B[min(m - a, M)]) == val:
                    rec(x0, y0, x, h, a)
                    rec(x0 + x, y0, w - x, h, m - a)
                    return
        for y in range(1, h):
            A = get(w, y)
            B = get(w, h - y)
            for a in range(0, m + 1):
                if int(A[min(a, M)]) + int(B[min(m - a, M)]) == val:
                    rec(x0, y0, w, y, a)
                    rec(x0, y0 + y, w, h - y, m - a)
                    return
        s = min(w, h)
        out.append((x0, y0, s))

    rec(0, 0, k, k, min(n, M))

    shrink = 1.0 - 1e-9
    squares = []
    for (x0, y0, s) in out[:n]:
        cx = (x0 + s / 2.0) / k
        cy = (y0 + s / 2.0) / k
        squares.append((cx, cy, 0.0, s / k * shrink))
    if len(squares) < 1 and n > 0:
        # fallback to simple grid
        g = math.isqrt(n)
        side = 1.0 / g
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side * shrink)
                   for i in range(g) for j in range(g)]
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
