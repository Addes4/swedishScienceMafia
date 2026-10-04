# EVOLVE-BLOCK-START
"""Recursive partition construction:
  - j x j grid partition with per-cell counts (knapsack over cells)
  - k x k grid with a b x b corner block holding its own configuration
  - drop a square (side 0)
"""
import math
import numpy as np


def solve(n):
    N = max(n, 1)
    JMAX = 6
    KMAX = 7
    T = max(JMAX * JMAX, KMAX * KMAX)
    NEG = -1e18
    f = np.full(N + 1, NEG)
    f[0] = 0.0
    G = np.full((T + 1, N + 1), NEG)
    G[:, 0] = 0.0
    arg = np.zeros((T + 1, N + 1), dtype=np.int64)
    choice = [None] * (N + 1)
    choice[0] = ('empty',)
    eps = 1e-12

    for m in range(1, N + 1):
        # partial knapsack excluding a cell holding all m
        fm = f[0:m]
        for t in range(1, T + 1):
            vals = G[t - 1][m:0:-1] + fm
            a = int(np.argmax(vals))
            G[t][m] = vals[a]
            arg[t][m] = a
        best = NEG
        ch = None
        if m == 1:
            best = 1.0
            ch = ('one',)
        if f[m - 1] > best + eps:
            best = f[m - 1]
            ch = ('drop',)
        for j in range(2, JMAX + 1):
            v = G[j * j][m] / j
            if v > best + eps:
                best = v
                ch = ('part', j)
        if m >= 2:
            for k in range(2, KMAX + 1):
                for b in range(1, k):
                    r = k * k - b * b
                    vals = b * f[1:m] + G[r][m - 1:0:-1]
                    i = int(np.argmax(vals))
                    v = vals[i] / k
                    if v > best + eps:
                        best = v
                        ch = ('block', k, b, i + 1)
        f[m] = best
        choice[m] = ch
        # full update: allow one cell with all m
        for t in range(1, T + 1):
            if f[m] > G[t][m]:
                G[t][m] = f[m]
                arg[t][m] = m

    def trace(t, m):
        counts = []
        while t > 0:
            a = int(arg[t][m])
            counts.append(a)
            m -= a
            t -= 1
        return counts

    out = []

    def place(m, x, y, s):
        if m <= 0:
            return
        ch = choice[m]
        if ch[0] == 'one':
            out.append((x + s / 2, y + s / 2, 0.0, s))
        elif ch[0] == 'drop':
            place(m - 1, x, y, s)
        elif ch[0] == 'part':
            j = ch[1]
            counts = trace(j * j, m)
            c = s / j
            for i, cnt in enumerate(counts):
                ix, iy = i % j, i // j
                place(cnt, x + ix * c, y + iy * c, c)
        elif ch[0] == 'block':
            _, k, b, cb = ch
            c = s / k
            place(cb, x, y, c * b)
            counts = trace(k * k - b * b, m - cb)
            idx = 0
            for ix in range(k):
                for iy in range(k):
                    if ix < b and iy < b:
                        continue
                    place(counts[idx], x + ix * c, y + iy * c, c)
                    idx += 1

    place(n, 0.0, 0.0, 1.0)
    res = []
    for (cx, cy, ang, sd) in out[:n]:
        sd2 = sd * (1 - 1e-11)
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        res.append((cx, cy, 0.0, max(sd2, 0.0)))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
