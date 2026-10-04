# EVOLVE-BLOCK-START
"""Partition recurrence: split into j x j equal cells (j=2,3,4), knapsack over counts."""
import math
import numpy as np


def _build_tables(N):
    NEG = -1e18
    h = np.full((17, N + 1), NEG)
    p = np.full((17, N + 1), NEG)
    h[0][0] = 0.0
    f = np.zeros(N + 1)
    choice = [None] * (N + 1)
    choice[0] = ('zero',)
    for n in range(1, N + 1):
        for c in range(2, 17):
            best = p[c - 1][n]
            if n >= 2:
                vals = h[c - 1][n - 1:0:-1] + f[1:n]
                v = vals.max()
                if v > best:
                    best = v
            p[c][n] = best
        k = math.isqrt(n)
        bv = float(k)
        ch = ('grid', k)
        if n >= 2 and f[n - 1] > bv + 1e-12:
            bv = f[n - 1]
            ch = ('prev',)
        for j in (2, 3, 4):
            v = p[j * j][n] / j
            if v > bv + 1e-12:
                bv = v
                ch = ('part', j)
        f[n] = bv
        choice[n] = ch
        for c in range(1, 17):
            h[c][n] = max(p[c][n], f[n])
    return f, h, choice


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    f, h, choice = _build_tables(n)
    out = []

    def place(m, x0, y0, size):
        if m <= 0:
            return
        ch = choice[m]
        if ch[0] == 'grid':
            k = ch[1]
            s = size / k
            for i in range(k):
                for j in range(k):
                    out.append((x0 + (i + 0.5) * s, y0 + (j + 0.5) * s, 0.0, s))
            for _ in range(m - k * k):
                out.append((x0, y0, 0.0, 0.0))
        elif ch[0] == 'prev':
            place(m - 1, x0, y0, size)
            out.append((x0, y0, 0.0, 0.0))
        elif ch[0] == 'part':
            j = ch[1]
            cells = j * j
            allocs = []
            rem = m
            for c in range(cells, 0, -1):
                target = h[c][rem]
                chosen = None
                amax = rem
                if rem == m:
                    amax = m - 1
                for a in range(amax, -1, -1):
                    if h[c - 1][rem - a] + f[a] >= target - 1e-9:
                        chosen = a
                        break
                if chosen is None:
                    chosen = 0
                allocs.append(chosen)
                rem -= chosen
            s = size / j
            idx = 0
            for i in range(j):
                for jj in range(j):
                    a = allocs[idx]
                    idx += 1
                    place(a, x0 + i * s, y0 + jj * s, s)
            for _ in range(rem):
                out.append((x0, y0, 0.0, 0.0))

    place(n, 0.0, 0.0, 1.0)
    out = out[:n]
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    res = []
    for (x, y, a, s) in out:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return res
# EVOLVE-BLOCK-END
