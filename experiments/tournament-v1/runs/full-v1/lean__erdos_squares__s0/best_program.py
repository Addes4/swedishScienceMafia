# EVOLVE-BLOCK-START
"""DP over recursive grid constructions (with optional merged corner block holding a sub-packing)."""
import math

NEG = -1e18
_MS = list(range(2, 8))


def _build(N):
    V = [0.0] * (N + 1)
    choice = [None] * (N + 1)
    g = {}
    ga = {}
    for m in _MS:
        C = m * m
        g[m] = [[NEG] * (N + 1) for _ in range(C + 1)]
        ga[m] = [[0] * (N + 1) for _ in range(C + 1)]
        g[m][0][0] = 0.0
        for c in range(1, C + 1):
            g[m][c][0] = 0.0
    for n in range(1, N + 1):
        best = V[n - 1]
        bch = ('same',)
        if n == 1:
            best = 1.0
            bch = ('one',)
        gex = {}
        gexa = {}
        for m in _MS:
            C = m * m
            ex = [NEG] * (C + 1)
            exa = [0] * (C + 1)
            gm = g[m]
            for c in range(1, C + 1):
                bv = ex[c - 1]
                ba = 0
                prev = gm[c - 1]
                for k in range(1, n):
                    pv = prev[n - k]
                    if pv > NEG / 2:
                        v = V[k] / m + pv
                        if v > bv:
                            bv = v
                            ba = k
                ex[c] = bv
                exa[c] = ba
            gex[m] = ex
            gexa[m] = exa
            if n >= 2 and ex[C] > best + 1e-12:
                best = ex[C]
                bch = ('grid', m)
            for j in range(2, m):
                c = C - j * j
                gc = gm[c]
                for k in range(1, n + 1):
                    if k == n:
                        continue
                    pv = gc[n - k]
                    if pv > NEG / 2:
                        v = V[k] * j / m + pv
                        if v > best + 1e-12:
                            best = v
                            bch = ('block', m, j, k)
        V[n] = best
        choice[n] = bch
        for m in _MS:
            C = m * m
            for c in range(1, C + 1):
                e = gex[m][c]
                if V[n] / m > e + 1e-12:
                    g[m][c][n] = V[n] / m
                    ga[m][c][n] = n
                else:
                    g[m][c][n] = e
                    ga[m][c][n] = gexa[m][c]
    return V, choice, ga


def _dist(ga, m, c, t):
    ks = []
    while c > 0:
        k = ga[m][c][t]
        ks.append(k)
        t -= k
        c -= 1
    return ks


def _place(n, x0, y0, s, choice, ga, out):
    if n <= 0:
        return
    ch = choice[n]
    if ch[0] == 'same':
        _place(n - 1, x0, y0, s, choice, ga, out)
    elif ch[0] == 'one':
        out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
    elif ch[0] == 'grid':
        m = ch[1]
        ks = _dist(ga, m, m * m, n)
        cs = s / m
        for i, k in enumerate(ks):
            _place(k, x0 + (i % m) * cs, y0 + (i // m) * cs, cs, choice, ga, out)
    else:
        m, j, kb = ch[1], ch[2], ch[3]
        cs = s / m
        _place(kb, x0, y0, j * cs, choice, ga, out)
        cells = [(a, b) for b in range(m) for a in range(m) if not (a < j and b < j)]
        ks = _dist(ga, m, len(cells), n - kb)
        for (a, b), k in zip(cells, ks):
            _place(k, x0 + a * cs, y0 + b * cs, cs, choice, ga, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    V, choice, ga = _build(n)
    out = []
    _place(n, 0.0, 0.0, 1.0, choice, ga, out)
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    res = []
    for (x, y, a, s) in out:
        s = min(max(s, 0.0), 1.0)
        res.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), a, s))
    return res
# EVOLVE-BLOCK-END
