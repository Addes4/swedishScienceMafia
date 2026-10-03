# EVOLVE-BLOCK-START
"""Guillotine DP on an m x m integer grid: maximise sum of sides with at most n squares,
trying several grid resolutions m; leftover squares have side zero."""
import math
import time
import numpy as np


def _run(m, n):
    C = min(n, m * m)
    ar = np.arange(C + 1)
    idx = ar[:, None] - ar[None, :]
    idx = np.where(idx >= 0, idx, C + 1)
    rows = ar

    V = [[None] * (m + 1) for _ in range(m + 1)]
    T = [[None] * (m + 1) for _ in range(m + 1)]
    P = [[None] * (m + 1) for _ in range(m + 1)]
    K = [[None] * (m + 1) for _ in range(m + 1)]

    def conv(X, Y):
        Yp = np.append(Y, -1e18)
        Mat = X[None, :] + Yp[idx]
        arg = Mat.argmax(1)
        return Mat[rows, arg], arg

    for a in range(1, m + 1):
        for b in range(1, m + 1):
            best = np.full(C + 1, float(min(a, b)))
            best[0] = 0.0
            typ = np.zeros(C + 1, dtype=np.int8)
            pos = np.zeros(C + 1, dtype=np.int32)
            c1 = np.zeros(C + 1, dtype=np.int32)
            for x in range(1, a // 2 + 1):
                vals, arg = conv(V[x][b], V[a - x][b])
                msk = vals > best + 1e-12
                if msk.any():
                    best = np.where(msk, vals, best)
                    typ[msk] = 1
                    pos[msk] = x
                    c1[msk] = arg[msk]
            for y in range(1, b // 2 + 1):
                vals, arg = conv(V[a][y], V[a][b - y])
                msk = vals > best + 1e-12
                if msk.any():
                    best = np.where(msk, vals, best)
                    typ[msk] = 2
                    pos[msk] = y
                    c1[msk] = arg[msk]
            V[a][b] = best
            T[a][b] = typ
            P[a][b] = pos
            K[a][b] = c1
    value = V[m][m][C] / m

    def build():
        res = []
        stack = [(m, m, C, 0, 0)]
        while stack:
            a, b, c, x0, y0 = stack.pop()
            if c <= 0:
                continue
            t = int(T[a][b][c])
            if t == 0:
                s = min(a, b)
                res.append((x0, y0, s))
            elif t == 1:
                x = int(P[a][b][c])
                k1 = int(K[a][b][c])
                stack.append((x, b, k1, x0, y0))
                stack.append((a - x, b, c - k1, x0 + x, y0))
            else:
                y = int(P[a][b][c])
                k1 = int(K[a][b][c])
                stack.append((a, y, k1, x0, y0))
                stack.append((a, b - y, c - k1, x0, y0 + y))
        return res

    return value, build


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    k = max(1, math.isqrt(n))
    # fallback grid
    best_val = float(k * k) / k
    best_build = None
    ms = list(range(1, math.isqrt(n) + 10))
    r = math.sqrt(n)
    ms.sort(key=lambda m: (abs(m - r), m))
    for m in ms:
        if time.time() - t0 > 35:
            break
        C = min(n, m * m)
        if (m ** 3 / 2.0) * (C + 1) ** 2 > 6e8:
            continue
        val, build = _run(m, n)
        if val > best_val + 1e-12:
            best_val = val
            best_build = (m, build)
    squares = []
    if best_build is None:
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side * (1 - 1e-9))
                   for i in range(k) for j in range(k)]
    else:
        m, build = best_build
        for (x0, y0, s) in build():
            sd = s / m
            squares.append(((x0 / m) + sd / 2, (y0 / m) + sd / 2, 0.0, sd * (1 - 1e-9)))
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
