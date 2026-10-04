# EVOLVE-BLOCK-START
"""DP over hierarchical grid layouts (grids with an optional merged corner block)."""
import math
import numpy as np

NEG = -1e18


def solve(n):
    N = n
    J = min(math.isqrt(n) + 1, 12 if n <= 600 else 6)
    J = max(J, 2)
    f = np.zeros(N + 1)
    ftype = [None] * (N + 1)
    ftype[0] = ('zero',)
    Dd, Pp, argD, argP = {}, {}, {}, {}
    for j in range(2, J + 1):
        T = j * j
        D = np.full((T + 1, N + 1), NEG)
        D[:, 0] = 0.0
        P = np.full((T + 1, N + 1), NEG)
        P[:, 0] = 0.0
        Dd[j], Pp[j] = D, P
        argD[j] = np.zeros((T + 1, N + 1), dtype=np.int32)
        argP[j] = np.zeros((T + 1, N + 1), dtype=np.int32)
    for m in range(1, N + 1):
        # pass 1: P (distributions where no cell holds everything)
        for j in range(2, J + 1):
            D, P, aP = Dd[j], Pp[j], argP[j]
            for t in range(1, j * j + 1):
                best = P[t - 1, m]
                ba = 0
                if m >= 2:
                    cand = D[t - 1, m - 1:0:-1] + f[1:m]
                    i = int(np.argmax(cand))
                    if cand[i] > best:
                        best = cand[i]
                        ba = i + 1
                P[t, m] = best
                aP[t, m] = ba
        if m == 1:
            f[1] = 1.0
            ftype[1] = ('leaf',)
        else:
            bestv = f[m - 1]
            bt = ('same',)
            for j in range(2, J + 1):
                v = Pp[j][j * j, m] / j
                if v > bestv + 1e-12:
                    bestv = v
                    bt = ('grid', j)
                D = Dd[j]
                for mb in range(2, j):
                    t = j * j - mb * mb
                    cand = D[t, m - 1:0:-1] + mb * f[1:m]
                    i = int(np.argmax(cand))
                    v = cand[i] / j
                    if v > bestv + 1e-12:
                        bestv = v
                        bt = ('block', j, mb, i + 1)
            f[m] = bestv
            ftype[m] = bt
        # pass 2
        for j in range(2, J + 1):
            D, P = Dd[j], Pp[j]
            col = P[1:, m]
            use_single = f[m] >= col
            D[1:, m] = np.where(use_single, f[m], col)
            argD[j][1:, m] = np.where(use_single, m, argP[j][1:, m])

    def counts(j, t, m, excl):
        res = [0] * t
        while t > 0 and m > 0:
            a = int(argP[j][t, m]) if excl else int(argD[j][t, m])
            res[t - 1] = a
            m -= a
            t -= 1
            excl = excl and a == 0
        return res

    out = []

    def build(m, x0, y0, s):
        if m <= 0 or s <= 0:
            return
        ty = ftype[m]
        if ty[0] == 'leaf':
            out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
        elif ty[0] == 'same':
            build(m - 1, x0, y0, s)
        elif ty[0] == 'grid':
            j = ty[1]
            cs = counts(j, j * j, m, True)
            cell = s / j
            for c, a in enumerate(cs):
                if a > 0:
                    build(a, x0 + (c % j) * cell, y0 + (c // j) * cell, cell)
        elif ty[0] == 'block':
            _, j, mb, a = ty
            cell = s / j
            build(a, x0, y0, cell * mb)
            cells = [(r, c) for r in range(j) for c in range(j) if not (r < mb and c < mb)]
            cs = counts(j, len(cells), m - a, False)
            for idx, k in enumerate(cs):
                if k > 0:
                    r, c = cells[idx]
                    build(k, x0 + c * cell, y0 + r * cell, cell)

    build(n, 0.0, 0.0, 1.0)
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END
