# EVOLVE-BLOCK-START
"""Recursive grid subdivision with merged corner blocks, optimised by DP.
Zero-size squares are placed on the boundary of the unit square."""
import numpy as np


def _build(N):
    NEG = -1e18
    g = np.full(N + 1, NEG)
    g[0] = 0.0
    if N >= 1:
        g[1] = 1.0
    gchoice = [None] * (N + 1)
    # K[j][c]: best sum of g over j cells with total count c
    K = np.full((N + 1, N + 1), NEG)
    Kx = np.zeros((N + 1, N + 1), dtype=int)
    K[0][0] = 0.0
    for j in range(1, N + 1):
        K[j][0] = 0.0
    if N >= 1:
        for j in range(1, N + 1):
            K[j][1] = 1.0
            Kx[j][1] = 1
    for c in range(2, N + 1):
        # partial K_j(c), parts < c
        for j in range(1, N + 1):
            best = K[j - 1][c]
            bx = 0
            # x from 1..c-1: K[j-1][c-x] + g[x]
            xs = np.arange(1, c)
            vals = K[j - 1][c - xs] + g[1:c]
            k = int(np.argmax(vals))
            if vals[k] > best + 1e-12:
                best = vals[k]
                bx = int(xs[k])
            K[j][c] = best
            Kx[j][c] = bx
        # compute g(c)
        best = g[c - 1]
        choice = ('drop',)
        gl = g[0:c]
        for m in range(2, c + 2):
            for t in range(1, m):
                L = m * m - t * t
                Lj = min(L, N)
                vals = t * gl + K[Lj][c:0:-1]
                k = int(np.argmax(vals))
                v = vals[k] / m
                if v > best + 1e-12:
                    best = v
                    choice = ('grid', m, t, k)
        g[c] = best
        gchoice[c] = choice
        for j in range(1, N + 1):
            if g[c] > K[j][c] + 1e-12:
                K[j][c] = g[c]
                Kx[j][c] = c
    return g, gchoice, K, Kx


def solve(n):
    if n <= 0:
        return []
    N = n
    g, gchoice, K, Kx = _build(N)
    out = []
    zeros = [0]

    def kparts(j, c):
        parts = []
        while j > 0:
            x = int(Kx[j][c]) if c > 0 else 0
            parts.append(x)
            c -= x
            j -= 1
        return parts

    def place(c, x0, y0, s):
        if c == 0:
            return
        if c == 1:
            out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
            return
        ch = gchoice[c]
        if ch[0] == 'drop':
            zeros[0] += 1
            place(c - 1, x0, y0, s)
            return
        _, m, t, a = ch
        cs = s / m
        place(a, x0, y0, t * cs)
        L = m * m - t * t
        Lj = min(L, N)
        parts = kparts(Lj, c - a)
        parts += [0] * (L - len(parts))
        cells = [(i, j) for i in range(m) for j in range(m) if not (i < t and j < t)]
        for (i, j), cnt in zip(cells, parts):
            place(cnt, x0 + i * cs, y0 + j * cs, cs)

    place(n, 0.0, 0.0, 1.0)
    z = n - len(out)
    for j in range(z):
        out.append(((j + 1) / (z + 1), 0.0, 0.0, 0.0))

    def cl(v):
        return min(1.0, max(0.0, v))

    return [(cl(a), cl(b), cl(c), cl(d)) for (a, b, c, d) in out[:n]]
# EVOLVE-BLOCK-END
