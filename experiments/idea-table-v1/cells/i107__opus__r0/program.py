# EVOLVE-BLOCK-START
"""Recursive grid packing: k x k grids whose cells hold sub-packings (including
j x j subgrids or empty cells), plus grids with one merged m x m block.
A knapsack DP over cells hits n exactly without zero-padding waste."""
import math
import numpy as np


def solve(n):
    if n <= 0:
        return []
    Kmax = math.isqrt(n) + 3
    C = Kmax * Kmax
    NEG = -1e18
    H = np.full((C + 1, n + 1), NEG)
    H[:, 0] = 0.0
    choice = np.zeros((C + 1, n + 1), dtype=np.int64)
    F = np.zeros(n + 1)
    fch = [None] * (n + 1)

    F[1] = 1.0
    fch[1] = ('single',)
    for c in range(1, C + 1):
        H[c, 1] = 1.0
        choice[c, 1] = 1

    for N in range(2, n + 1):
        ts = np.arange(N)
        idx = N - ts
        FN = F[:N]
        for c in range(1, C + 1):
            v = H[c - 1, idx] + FN
            j = int(np.argmax(v))
            H[c, N] = v[j]
            choice[c, N] = j
        best = -1.0
        bch = None
        for k in range(2, Kmax + 1):
            val = H[k * k, N] / k
            if val > best + 1e-12:
                best = val
                bch = ('grid', k)
        nb = np.arange(1, N)
        for k in range(3, Kmax + 1):
            for m in range(2, k):
                rest = k * k - m * m
                v = m * F[1:N] + H[rest, N - nb]
                j = int(np.argmax(v))
                val = v[j] / k
                if val > best + 1e-12:
                    best = val
                    bch = ('merge', k, m, int(nb[j]))
        F[N] = best
        fch[N] = bch
        for c in range(1, C + 1):
            if F[N] > H[c, N]:
                H[c, N] = F[N]
                choice[c, N] = N

    def backtrack(c, m):
        out = []
        while m > 0 and c > 0:
            t = int(choice[c, m])
            out.append(t)
            m -= t
            c -= 1
        return out

    res = []

    def build(N, x, y, s):
        if N <= 0:
            return
        ch = fch[N]
        if ch[0] == 'single':
            res.append((x + s / 2, y + s / 2, 0.0, s))
            return
        if ch[0] == 'grid':
            k = ch[1]
            tl = backtrack(k * k, N)
            cs = s / k
            for i, t in enumerate(tl):
                if t > 0:
                    a, b = divmod(i, k)
                    build(t, x + a * cs, y + b * cs, cs)
            return
        _, k, m, nbk = ch
        cs = s / k
        build(nbk, x, y, m * cs)
        tl = backtrack(k * k - m * m, N - nbk)
        cells = [(a, b) for a in range(k) for b in range(k) if a >= m or b >= m]
        for i, t in enumerate(tl):
            if t > 0:
                a, b = cells[i]
                build(t, x + a * cs, y + b * cs, cs)

    build(n, 0.0, 0.0, 1.0)
    out = []
    for (cx, cy, ang, sd) in res:
        sd2 = max(0.0, sd - 1e-12)
        out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), ang, sd2))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
