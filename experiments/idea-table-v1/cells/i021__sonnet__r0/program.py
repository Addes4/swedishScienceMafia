import math
import numpy as np

NEG = -1e9


def _conv(X, Y):
    n1 = len(X)
    R = np.full(n1, NEG)
    for i in range(n1):
        if X[i] < -1e8:
            continue
        np.maximum(R[i:], X[i] + Y[:n1 - i], out=R[i:])
    return R


def _backtrack(arrs, g, total, count):
    """arrs[c] = c-fold conv of g. Return list of counts for `count` cells summing to total."""
    res = []
    for c in range(count, 0, -1):
        prev = arrs[c - 1]
        best_i, best_v = 0, -1e30
        for i in range(total + 1):
            v = prev[total - i] + g[i]
            if v > best_v + 1e-12:
                best_v, best_i = v, i
        res.append(best_i)
        total -= best_i
    return res


def solve(n):
    if n <= 1:
        return [(0.5, 0.5, 0.0, 1.0)] * n
    A = max(2, math.isqrt(n) + 3)
    G0 = np.ones(n + 1)
    G0[0] = 0.0
    levels = []  # each: dict(Gp, Hs, Bs, choice)
    Gp = G0
    unit0 = np.full(n + 1, NEG)
    unit0[0] = 0.0
    for _ in range(5):
        Hs = {}
        Bs = {}
        Gnew = Gp.copy()
        choice = [None] * (n + 1)
        for a in range(2, A + 1):
            H = [unit0]
            for c in range(1, a * a + 1):
                H.append(_conv(H[-1], Gp))
            Hs[a] = H
            # no blocks
            val = H[a * a] / a
            for m in range(n + 1):
                if val[m] > Gnew[m] + 1e-12:
                    Gnew[m] = val[m]
                    choice[m] = (a, 1, 0)
            for j in range(2, a):
                tmax = (a // j) ** 2
                g = j * Gp
                B = [unit0]
                for t in range(1, tmax + 1):
                    B.append(_conv(B[-1], g))
                Bs[(a, j)] = B
                for t in range(1, tmax + 1):
                    u = a * a - t * j * j
                    comb = _conv(H[u], B[t]) / a
                    for m in range(n + 1):
                        if comb[m] > Gnew[m] + 1e-12:
                            Gnew[m] = comb[m]
                            choice[m] = (a, j, t)
        levels.append(dict(Gp=Gp, Hs=Hs, Bs=Bs, choice=choice))
        changed = np.any(Gnew > Gp + 1e-12)
        Gp = Gnew
        if not changed:
            break
    out = []

    def build(m, L, x0, y0, size):
        if m <= 0:
            return
        if L < 0:
            out.append((x0 + size / 2, y0 + size / 2, 0.0, size))
            return
        lv = levels[L]
        ch = lv['choice'][m]
        if ch is None:
            build(m, L - 1, x0, y0, size)
            return
        a, j, t = ch
        Gprev = lv['Gp']
        H = lv['Hs'][a]
        u = a * a - t * j * j
        cs = size / a
        if t == 0:
            counts_u = _backtrack(H, Gprev, m, a * a)
            counts_b = []
        else:
            B = lv['Bs'][(a, j)]
            comb = None
            best_k, best_v = 0, -1e30
            for k in range(m + 1):
                v = H[u][m - k] + B[t][k]
                if v > best_v + 1e-12:
                    best_v, best_k = v, k
            counts_u = _backtrack(H, Gprev, m - best_k, u)
            counts_b = _backtrack(B, j * Gprev, best_k, t)
        occupied = set()
        blocks = []
        per = a // j
        for idx in range(t):
            bi, bj = divmod(idx, per)
            blocks.append((bi * j, bj * j))
            for di in range(j):
                for dj in range(j):
                    occupied.add((bi * j + di, bj * j + dj))
        ui = 0
        for r in range(a):
            for c in range(a):
                if (r, c) in occupied:
                    continue
                mi = counts_u[ui]
                ui += 1
                build(mi, L - 1, x0 + c * cs, y0 + r * cs, cs)
        for (r, c), mi in zip(blocks, counts_b):
            build(mi, L - 1, x0 + c * cs, y0 + r * cs, cs * j)

    build(n, len(levels) - 1, 0.0, 0.0, 1.0)
    res = []
    for (cx, cy, ang, s) in out:
        s2 = s * (1 - 1e-10)
        res.append((min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0), 0.0, min(max(s2, 0.0), 1.0)))
    res.sort(key=lambda q: -q[3])
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
