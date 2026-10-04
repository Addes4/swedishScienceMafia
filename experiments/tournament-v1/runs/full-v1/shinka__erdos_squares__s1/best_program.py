# EVOLVE-BLOCK-START
"""Baseline: the largest k x k grid that fits, plus size-zero squares for the rest."""
import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 1:
        return [(0.5, 0.5, 0.0, 1.0)] * n
    K = math.isqrt(n) + 2
    C = K * K
    best = [0.0] * (n + 1)
    plan = [None] * (n + 1)
    best[1] = 1.0
    plan[1] = ('one',)
    g = [[0.0] * (n + 1) for _ in range(C + 1)]
    pg = [[0] * (n + 1) for _ in range(C + 1)]
    for c in range(1, C + 1):
        g[c][1] = 1.0
        pg[c][1] = 1

    def walk(c, t, pex, ex):
        res = []
        while c > 0 and t > 0:
            m = pex[c] if ex else pg[c][t]
            if m > 0:
                res.append(m)
                t -= m
                ex = False
            c -= 1
        return res

    for t in range(2, n + 1):
        gex = [0.0] * (C + 1)
        pex = [0] * (C + 1)
        for c in range(1, C + 1):
            bv = gex[c - 1]
            bm = 0
            prev = g[c - 1]
            for m in range(1, t):
                v = prev[t - m] + best[m]
                if v > bv + 1e-12:
                    bv = v
                    bm = m
            gex[c] = bv
            pex[c] = bm
        bv = best[t - 1]
        cand = ('pad',)
        for k in range(2, K + 1):
            val = gex[k * k] / k
            if val > bv + 1e-12:
                bv = val
                cand = ('grid', k, 0, 0)
            for a in range(2, k):
                c = k * k - a * a
                for mb in range(1, t):
                    val = (a * best[mb] + g[c][t - mb]) / k
                    if val > bv + 1e-12:
                        bv = val
                        cand = ('merge', k, a, mb)
        if cand[0] == 'pad':
            plan[t] = ('pad',)
        elif cand[0] == 'grid':
            k = cand[1]
            plan[t] = ('grid', k, walk(k * k, t, pex, True))
        else:
            _, k, a, mb = cand
            c = k * k - a * a
            plan[t] = ('merge', k, a, mb, walk(c, t - mb, pex, False))
        best[t] = bv
        for c in range(1, C + 1):
            if bv > gex[c] + 1e-12:
                g[c][t] = bv
                pg[c][t] = t
            else:
                g[c][t] = gex[c]
                pg[c][t] = pex[c]

    out = []

    def build(t, x0, y0, size):
        p = plan[t]
        if p[0] == 'one':
            out.append((x0, y0, size))
        elif p[0] == 'pad':
            build(t - 1, x0, y0, size)
        elif p[0] == 'grid':
            k = p[1]
            s = size / k
            for idx, m in enumerate(p[2]):
                i, j = divmod(idx, k)
                build(m, x0 + i * s, y0 + j * s, s)
        else:
            _, k, a, mb, counts = p
            s = size / k
            build(mb, x0, y0, a * s)
            cells = [(i, j) for i in range(k) for j in range(k) if not (i < a and j < a)]
            for (i, j), m in zip(cells, counts):
                build(m, x0 + i * s, y0 + j * s, s)

    build(n, 0.0, 0.0, 1.0)
    shrink = 1.0 - 1e-9
    squares = []
    for (x0, y0, s) in out[:n]:
        squares.append((x0 + s / 2.0, y0 + s / 2.0, 0.0, s * shrink))
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END