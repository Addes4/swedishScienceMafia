# EVOLVE-BLOCK-START
"""Layout DP: unit square split into a k x k grid, optionally with a j x j merged
corner block; leftover cells filled recursively with a knapsack allocation of counts."""
import math


def solve(n):
    NEG = -1e18
    kmax = max(2, min(8, n))
    C = kmax * kmax
    f = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    g = [[NEG] * (n + 1) for _ in range(C + 1)]
    ch = [[0] * (n + 1) for _ in range(C + 1)]
    for c in range(C + 1):
        g[c][0] = 0.0

    for m in range(1, n + 1):
        tmp = [NEG] * (C + 1)
        tch = [0] * (C + 1)
        for c in range(1, C + 1):
            best = NEG
            ba = 0
            for a in range(0, m):
                prev = tmp[c - 1] if a == 0 else g[c - 1][m - a]
                if prev <= NEG / 2:
                    continue
                v = prev + f[a]
                if v > best:
                    best = v
                    ba = a
            tmp[c] = best
            tch[c] = ba

        bestv = f[m - 1]
        bestc = ('pad',)
        if m == 1:
            bestv = 1.0
            bestc = ('one',)
        else:
            for k in range(2, kmax + 1):
                # no merged block
                c = k * k
                if tmp[c] > NEG / 2:
                    v = tmp[c] / k
                    if v > bestv + 1e-12:
                        bestv = v
                        bestc = ('grid', k, 0, c, True)
                for j in range(2, k):
                    c = k * k - j * j
                    t = m - 1
                    if g[c][t] > NEG / 2:
                        v = (j + g[c][t]) / k
                        if v > bestv + 1e-12:
                            bestv = v
                            bestc = ('grid', k, j, c, False)
        f[m] = bestv
        if bestc[0] == 'grid':
            _, k, j, c, lvl = bestc
            t = m if lvl else m - 1
            alloc = []
            for cc in range(c, 0, -1):
                if t == m:
                    a = tch[cc]
                else:
                    a = ch[cc][t]
                alloc.append(a)
                t -= a
            choice[m] = ('grid', k, j, alloc)
        else:
            choice[m] = bestc

        g[0][m] = NEG
        for c in range(1, C + 1):
            best = NEG
            ba = 0
            for a in range(0, m + 1):
                prev = g[c - 1][m - a]
                if prev <= NEG / 2:
                    continue
                v = prev + f[a]
                if v > best:
                    best = v
                    ba = a
            g[c][m] = best
            ch[c][m] = ba

    out = []

    def place(m, x, y, s):
        if m <= 0:
            return
        cc = choice[m]
        if cc[0] == 'pad':
            place(m - 1, x, y, s)
        elif cc[0] == 'one':
            out.append((x + s / 2, y + s / 2, 0.0, s))
        else:
            _, k, j, alloc = cc
            cs = s / k
            if j >= 2:
                out.append((x + j * cs / 2, y + j * cs / 2, 0.0, j * cs))
            cells = [(i, jj) for i in range(k) for jj in range(k)
                     if not (j >= 2 and i < j and jj < j)]
            for (i, jj), a in zip(cells, alloc):
                if a > 0:
                    place(a, x + i * cs, y + jj * cs, cs)

    place(n, 0.0, 0.0, 1.0)
    res = []
    for (cx, cy, ang, sd) in out[:n]:
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), ang, min(1.0, max(0.0, sd))))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
