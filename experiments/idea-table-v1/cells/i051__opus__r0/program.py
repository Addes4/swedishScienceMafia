# EVOLVE-BLOCK-START
"""Guillotine (Euclidean / continued-fraction style) square dissections of a
K x K grid, optimised by DP over integer rectangles, for all K up to a
time-dependent limit.  Squares may be dropped (padded as zero-size points)."""
import math
import numpy as np

NEG = -(10 ** 12)


def _key(w, h):
    return (w, h) if w <= h else (h, w)


def _combine(A, B, Lr):
    La = len(A)
    Lb = len(B)
    Bext = np.concatenate([B, np.array([NEG], dtype=np.int64)])
    idx = np.subtract.outer(np.arange(La), np.zeros(1, dtype=np.int64))  # placeholder shape
    idx = np.arange(Lr)[None, :] - np.arange(La)[:, None]
    idx = np.minimum(idx, Lb - 1)
    idx[idx < 0] = -1
    M = A[:, None] + Bext[idx]
    return M.max(axis=0)


def solve(n):
    if n <= 0:
        return []
    # choose K by cost estimate
    budget = 20.0
    cost = 0.0
    Kmax = 1
    for K in range(1, 91):
        c = 0.0
        h = K
        for w in range(1, h + 1):
            Lr = min(n, w * h) + 1
            for a in range(1, w // 2 + 1):
                La = min(n, a * h) + 1
                c += La * Lr * 3e-9 + 4e-6
            for b in range(1, h // 2 + 1):
                La = min(n, w * b) + 1
                c += La * Lr * 3e-9 + 4e-6
        if cost + c > budget:
            break
        cost += c
        Kmax = K
    Kmax = max(Kmax, 1)

    G = {}
    for h in range(1, Kmax + 1):
        for w in range(1, h + 1):
            Lr = min(n, w * h) + 1
            g = np.zeros(Lr, dtype=np.int64)
            if w == h:
                g[1:] = w
            for a in range(1, w // 2 + 1):
                r = _combine(G[_key(a, h)], G[_key(w - a, h)], Lr)
                np.maximum(g, r, out=g)
            for b in range(1, h // 2 + 1):
                r = _combine(G[_key(w, b)], G[_key(w, h - b)], Lr)
                np.maximum(g, r, out=g)
            # enforce monotone
            g = np.maximum.accumulate(g)
            G[(w, h)] = g

    bestK, bestV = 1, 0
    for K in range(1, Kmax + 1):
        v = int(G[(K, K)][-1])
        if v * bestK > bestV * K:
            bestK, bestV = K, v

    K = bestK
    out = []

    def val(w, h, m):
        arr = G[_key(w, h)]
        return int(arr[min(m, len(arr) - 1)])

    def build(x0, y0, w, h, m):
        t = val(w, h, m)
        if t <= 0 or m <= 0:
            return
        if w == h and t == w:
            out.append((x0, y0, w))
            return
        for a in range(1, w // 2 + 1):
            for m1 in range(0, m + 1):
                if val(a, h, m1) + val(w - a, h, m - m1) == t:
                    build(x0, y0, a, h, m1)
                    build(x0 + a, y0, w - a, h, m - m1)
                    return
        for b in range(1, h // 2 + 1):
            for m1 in range(0, m + 1):
                if val(w, b, m1) + val(w, h - b, m - m1) == t:
                    build(x0, y0, w, b, m1)
                    build(x0, y0 + b, w, h - b, m - m1)
                    return

    import sys
    sys.setrecursionlimit(10000)
    build(0, 0, K, K, n)

    res = []
    shrink = 1.0 - 1e-12
    for (x0, y0, s) in out[:n]:
        cx = (x0 + s / 2.0) / K
        cy = (y0 + s / 2.0) / K
        side = s / K * shrink
        res.append((min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0), 0.0, min(side, 1.0)))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
