# EVOLVE-BLOCK-START
"""Recursive grid / merged-block dynamic program with zero-size padding."""
import math
import numpy as np

NEG = -1e18


def _plan(N):
    Ks = list(range(2, math.isqrt(N) + 3))
    F = np.zeros(N + 1)
    choice = [None] * (N + 1)
    G, chG, chX = {}, {}, {}
    CM = {}
    for k in Ks:
        cm = min(k * k, N)
        CM[k] = cm
        g = np.full((cm + 1, N + 1), NEG)
        g[:, 0] = 0.0
        G[k] = g
        chG[k] = np.zeros((cm + 1, N + 1), dtype=np.int64)
        chX[k] = np.zeros((cm + 1, N + 1), dtype=np.int64)
    for n in range(1, N + 1):
        if n == 1:
            F[1] = 1.0
            choice[1] = ('one',)
        else:
            best = F[n - 1]
            ch = ('pad',)
            for k in Ks:
                if k * k > 4 * n + 4:
                    # still must fill chX? not needed for unused k
                    pass
                cm = CM[k]
                gxp = NEG
                gx_last = NEG
                for c in range(1, cm + 1):
                    Gp = G[k][c - 1]
                    cand = Gp[n - 1:0:-1] + F[1:n]
                    ii = int(np.argmax(cand))
                    v = cand[ii]
                    jj = ii + 1
                    if gxp > v:
                        v = gxp
                        jj = 0
                    chX[k][c][n] = jj
                    gxp = v
                    gx_last = v
                val = gx_last / k
                if val > best + 1e-12:
                    best = val
                    ch = ('grid', k)
                for a in range(2, k):
                    c = min(k * k - a * a, N)
                    if c < 1:
                        continue
                    vec = (a / k) * F[1:n] + G[k][c][n - 1:0:-1] / k
                    ii = int(np.argmax(vec))
                    if vec[ii] > best + 1e-12:
                        best = vec[ii]
                        ch = ('block', k, a, ii + 1)
            F[n] = best
            choice[n] = ch
        for k in Ks:
            cm = CM[k]
            for c in range(1, cm + 1):
                Gp = G[k][c - 1]
                cand = Gp[n::-1] + F[0:n + 1]
                jj = int(np.argmax(cand))
                G[k][c][n] = cand[jj]
                chG[k][c][n] = jj
    return F, choice, chG, chX, CM


def _dist_x(chX, chG, k, c, n):
    res = []
    mode = 'x'
    m = n
    while c > 0:
        if mode == 'x':
            j = int(chX[k][c][m])
            res.append(j)
            if j != 0:
                mode = 'g'
                m -= j
        else:
            j = int(chG[k][c][m])
            res.append(j)
            m -= j
        c -= 1
    return res


def _dist_g(chG, k, c, m):
    res = []
    while c > 0:
        j = int(chG[k][c][m])
        res.append(j)
        m -= j
        c -= 1
    return res


def _build(n, x, y, s, plan, out):
    F, choice, chG, chX, CM = plan
    if n <= 0:
        return
    ch = choice[n]
    if ch[0] == 'one':
        out.append((x + s / 2, y + s / 2, 0.0, s))
    elif ch[0] == 'pad':
        _build(n - 1, x, y, s, plan, out)
    elif ch[0] == 'grid':
        k = ch[1]
        cm = CM[k]
        counts = _dist_x(chX, chG, k, cm, n)
        cs = s / k
        for idx, cnt in enumerate(counts):
            if cnt > 0:
                i, j = idx % k, idx // k
                _build(cnt, x + i * cs, y + j * cs, cs, plan, out)
    else:
        _, k, a, m = ch
        cs = s / k
        _build(m, x, y, a * cs, plan, out)
        c = min(k * k - a * a, CM[k] if False else len(chG[k]) - 1)
        c = min(k * k - a * a, chG[k].shape[0] - 1 if k * k - a * a > chG[k].shape[0] - 1 else k * k - a * a)
        counts = _dist_g(chG, k, c, n - m)
        cells = [(i, j) for j in range(k) for i in range(k) if not (i < a and j < a)]
        for (i, j), cnt in zip(cells, counts):
            if cnt > 0:
                _build(cnt, x + i * cs, y + j * cs, cs, plan, out)


def _grid_fallback(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    return sq


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    if n > 200:
        sq = _grid_fallback(n)
    else:
        plan = _plan(n)
        sq = []
        _build(n, 0.0, 0.0, 1.0, plan, sq)
    clean = []
    for (cx, cy, ang, s) in sq:
        s = min(max(s, 0.0), 1.0)
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        clean.append((cx, cy, ang, s))
    clean = clean[:n]
    clean += [(0.5, 0.5, 0.0, 0.0)] * (n - len(clean))
    return clean
# EVOLVE-BLOCK-END
