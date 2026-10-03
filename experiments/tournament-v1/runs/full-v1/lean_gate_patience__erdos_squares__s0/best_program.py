# EVOLVE-BLOCK-START
"""Recursive grid DP: F(m) = best sum of sides for m squares in a unit square, built from
k x k grids with an optional j x j merged corner block, each cell filled recursively."""
import math

NEG = -1e18


def solve(n):
    K = 8 if n <= 150 else 6
    C = K * K
    F = [0.0] * (n + 1)
    G = [[NEG] * (n + 1) for _ in range(C + 1)]
    for c in range(C + 1):
        G[c][0] = 0.0
    P = [[0] * (n + 1) for _ in range(C + 1)]
    Pc = {}
    choice = {}
    for m in range(1, n + 1):
        if m == 1:
            F[1] = 1.0
            choice[1] = ('one',)
        else:
            Gc = [NEG] * (C + 1)
            par = [0] * (C + 1)
            for c in range(1, C + 1):
                best = NEG
                bt = 0
                for t in range(0, m):
                    prev = Gc[c - 1] if t == 0 else G[c - 1][m - t]
                    if prev <= NEG / 2:
                        continue
                    v = prev + F[t]
                    if v > best:
                        best = v
                        bt = t
                Gc[c] = best
                par[c] = bt
            Pc[m] = par
            bestv = F[m - 1]
            bestc = ('waste',)
            for k in range(2, K + 1):
                for j in range(0, k):
                    if j == 1:
                        continue
                    cells = k * k - j * j
                    if j == 0:
                        v = Gc[cells] / k
                        if v > bestv + 1e-12:
                            bestv = v
                            bestc = (k, 0, 0)
                    else:
                        for m0 in range(1, m):
                            rest = m - m0
                            gp = G[cells][rest] if rest < m else Gc[cells]
                            if gp <= NEG / 2:
                                continue
                            v = (j * F[m0] + gp) / k
                            if v > bestv + 1e-12:
                                bestv = v
                                bestc = (k, j, m0)
            F[m] = bestv
            choice[m] = bestc
        # full G for s = m
        for c in range(1, C + 1):
            best = NEG
            bt = 0
            for t in range(0, m + 1):
                prev = G[c - 1][m - t]
                if prev <= NEG / 2:
                    continue
                v = prev + F[t]
                if v > best:
                    best = v
                    bt = t
            G[c][m] = best
            P[c][m] = bt

    out = []

    def counts_for(cells, m):
        cnt = [0] * cells
        s = m
        for c in range(cells, 0, -1):
            if s == m:
                t = Pc[m][c]
            else:
                t = P[c][s]
            cnt[c - 1] = t
            s -= t
        return cnt

    def build(m, x, y, size):
        if m <= 0:
            return
        ch = choice[m]
        if ch[0] == 'one':
            out.append((x + size / 2, y + size / 2, 0.0, size))
            return
        if ch[0] == 'waste':
            build(m - 1, x, y, size)
            return
        k, j, m0 = ch
        u = size / k
        cells = k * k - j * j
        cnt = counts_for(cells, m - m0)
        if j > 0:
            build(m0, x, y, j * u)
        idx = 0
        for a in range(k):
            for b in range(k):
                if a < j and b < j:
                    continue
                build(cnt[idx], x + a * u, y + b * u, u)
                idx += 1

    build(n, 0.0, 0.0, 1.0)
    res = []
    for (cx, cy, an, s) in out[:n]:
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), an, min(1.0, max(0.0, s))))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
