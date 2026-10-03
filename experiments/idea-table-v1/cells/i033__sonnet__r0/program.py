# EVOLVE-BLOCK-START
"""Recursive grid / merged-corner-block DP construction + compaction LP on the topology."""
import math
import numpy as np


def _build(n):
    NEG = -1e18
    G = max(2, math.isqrt(n) + 2)
    M = G * G
    f = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    h = [[NEG] * (n + 1) for _ in range(M + 1)]
    lt = [[NEG] * (n + 1) for _ in range(M + 1)]
    ltarg = [[0] * (n + 1) for _ in range(M + 1)]
    hone = [[False] * (n + 1) for _ in range(M + 1)]
    for m in range(1, M + 1):
        h[m][0] = 0.0
    for c in range(1, n + 1):
        for m in range(1, M + 1):
            best = lt[m - 1][c]
            arg = 0
            hm = h[m - 1]
            for k in range(1, c):
                if hm[c - k] <= NEG / 2:
                    continue
                v = f[k] + hm[c - k]
                if v > best:
                    best = v
                    arg = k
            lt[m][c] = best
            ltarg[m][c] = arg
        bestv = f[c - 1]
        bestc = ('prev',)
        if 1.0 > bestv + 1e-12:
            bestv = 1.0
            bestc = ('single',)
        for g in range(2, G + 1):
            m = g * g
            if lt[m][c] > NEG / 2:
                v = lt[m][c] / g
                if v > bestv + 1e-12:
                    bestv = v
                    bestc = ('grid', g, 1, c)
            for a in range(2, g):
                m = g * g - a * a
                hv = h[m][c - 1]
                if hv > NEG / 2:
                    v = (a + hv) / g
                    if v > bestv + 1e-12:
                        bestv = v
                        bestc = ('grid', g, a, c - 1)
        f[c] = bestv
        choice[c] = bestc
        for m in range(1, M + 1):
            if f[c] >= lt[m][c]:
                h[m][c] = f[c]
                hone[m][c] = True
            else:
                h[m][c] = lt[m][c]
                hone[m][c] = False

    def full(m, c):
        if m == 0:
            return []
        if c == 0:
            return [0] * m
        if hone[m][c]:
            return [c] + [0] * (m - 1)
        return lt_list(m, c)

    def lt_list(m, c):
        if m == 0:
            return []
        k = ltarg[m][c]
        if k == 0:
            return [0] + lt_list(m - 1, c)
        return [k] + full(m - 1, c - k)

    out = []

    def place(c, x0, y0, size):
        if c <= 0:
            return
        ch = choice[c]
        if ch[0] == 'prev':
            place(c - 1, x0, y0, size)
        elif ch[0] == 'single':
            out.append((x0, y0, size))
        else:
            _, g, a, cc = ch
            cs = size / g
            cells = []
            if a == 1:
                counts = lt_list(g * g, cc)
                for i in range(g):
                    for j in range(g):
                        cells.append((i, j))
            else:
                counts = full(g * g - a * a, cc)
                out.append((x0, y0, a * cs))
                for i in range(g):
                    for j in range(g):
                        if i < a and j < a:
                            continue
                        cells.append((i, j))
            for (i, j), cnt in zip(cells, counts):
                if cnt > 0:
                    place(cnt, x0 + i * cs, y0 + j * cs, cs)

    place(n, 0.0, 0.0, 1.0)
    return out


def _compact(sq):
    k = len(sq)
    if k < 2:
        return None
    try:
        from scipy.optimize import linprog
    except Exception:
        return None
    X = [s[0] for s in sq]
    Y = [s[1] for s in sq]
    S = [s[2] for s in sq]
    rows = []
    for i in range(k):
        for j in range(i + 1, k):
            gaps = [
                (X[j] - (X[i] + S[i]), 'xij'),
                (X[i] - (X[j] + S[j]), 'xji'),
                (Y[j] - (Y[i] + S[i]), 'yij'),
                (Y[i] - (Y[j] + S[j]), 'yji'),
            ]
            g, t = max(gaps, key=lambda z: z[0])
            r = np.zeros(3 * k)
            if t == 'xij':
                r[i] = 1; r[2 * k + i] = 1; r[j] = -1
            elif t == 'xji':
                r[j] = 1; r[2 * k + j] = 1; r[i] = -1
            elif t == 'yij':
                r[k + i] = 1; r[2 * k + i] = 1; r[k + j] = -1
            else:
                r[k + j] = 1; r[2 * k + j] = 1; r[k + i] = -1
            rows.append((r, 0.0))
    for i in range(k):
        r = np.zeros(3 * k); r[i] = 1; r[2 * k + i] = 1
        rows.append((r, 1.0))
        r = np.zeros(3 * k); r[k + i] = 1; r[2 * k + i] = 1
        rows.append((r, 1.0))
    A = np.array([r for r, _ in rows])
    b = np.array([v for _, v in rows])
    cost = np.zeros(3 * k)
    cost[2 * k:] = -1.0
    res = linprog(cost, A_ub=A, b_ub=b, bounds=[(0, 1)] * (3 * k), method='highs')
    if not res.success:
        return None
    z = res.x
    return [(z[i], z[k + i], z[2 * k + i]) for i in range(k)]


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    sq = _build(n)
    sq = [s for s in sq if s[2] > 1e-12]
    base = sum(s[2] for s in sq)
    try:
        new = _compact(sq)
        if new is not None and sum(s[2] for s in new) > base + 1e-9:
            sq = [s for s in new if s[2] > 1e-12]
    except Exception:
        pass
    res = []
    for x, y, s in sq[:n]:
        s2 = max(0.0, s - 1e-12)
        cx = min(1.0, max(0.0, x + s / 2))
        cy = min(1.0, max(0.0, y + s / 2))
        res.append((cx, cy, 0.0, s2))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
