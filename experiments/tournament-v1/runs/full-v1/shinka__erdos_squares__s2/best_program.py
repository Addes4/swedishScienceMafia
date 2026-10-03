# EVOLVE-BLOCK-START
"""Squares in a square: recursive DP over all square-tilings of m x m grids."""
import math


def _tilings(m):
    """All distinct (by size multiset) tilings of m x m by integer squares."""
    res = {}
    grid = [[False] * m for _ in range(m)]
    tiles = []

    def rec(pos):
        while pos < m * m and grid[pos // m][pos % m]:
            pos += 1
        if pos == m * m:
            key = tuple(sorted((s for _, _, s in tiles), reverse=True))
            if key not in res and len(key) > 1:
                res[key] = sorted(tiles, key=lambda z: -z[2])
            return
        r, c = divmod(pos, m)
        smax = min(m - r, m - c)
        for s in range(smax, 0, -1):
            ok = True
            for a in range(r, r + s):
                for b in range(c, c + s):
                    if grid[a][b]:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            for a in range(r, r + s):
                for b in range(c, c + s):
                    grid[a][b] = True
            tiles.append((r, c, s))
            rec(pos + 1)
            tiles.pop()
            for a in range(r, r + s):
                for b in range(c, c + s):
                    grid[a][b] = False

    rec(0)
    return list(res.values())


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    if n > 150:
        MAXM = 4
    elif n > 80:
        MAXM = 5
    else:
        MAXM = 6

    structs = []  # (m, tiles)
    for m in range(2, MAXM + 1):
        for tl in _tilings(m):
            structs.append((m, tl))

    Q = len(structs)
    H = []
    CH = []
    GV = []
    GX = []
    for (m, tl) in structs:
        L = len(tl)
        H.append([[0.0] * (n + 1) for _ in range(L + 1)])
        CH.append([[0] * (n + 1) for _ in range(L + 1)])
        GV.append([[0.0] * (n + 1) for _ in range(L + 1)])
        GX.append([[0] * (n + 1) for _ in range(L + 1)])

    f = [0.0] * (n + 1)
    choice = [None] * (n + 1)

    for t in range(1, n + 1):
        best = 1.0
        ch = ('single',)
        if f[t - 1] > best + 1e-12:
            best = f[t - 1]
            ch = ('same',)
        for q in range(Q):
            m, tl = structs[q]
            Hq = H[q]
            Cq = CH[q]
            for i in range(1, len(tl) + 1):
                s = tl[i - 1][2]
                prev = Hq[i - 1]
                gv = -1.0
                gx = 0
                for x in range(1, t):
                    v = prev[t - x] + s * f[x]
                    if v > gv:
                        gv = v
                        gx = x
                GV[q][i][t] = gv
                GX[q][i][t] = gx
                if gv > prev[t]:
                    Hq[i][t] = gv
                    Cq[i][t] = gx
                else:
                    Hq[i][t] = prev[t]
                    Cq[i][t] = 0
            v = Hq[len(tl)][t] / m
            if v > best + 1e-12:
                best = v
                ch = ('tiling', q)
        f[t] = best
        choice[t] = ch
        # second pass: finalise H[i][t], allowing a tile to take all t squares
        for q in range(Q):
            m, tl = structs[q]
            Hq = H[q]
            Cq = CH[q]
            for i in range(1, len(tl) + 1):
                s = tl[i - 1][2]
                bv = Hq[i - 1][t]
                bx = 0
                gv = GV[q][i][t]
                if gv > bv:
                    bv = gv
                    bx = GX[q][i][t]
                v = s * f[t]
                if v > bv:
                    bv = v
                    bx = t
                Hq[i][t] = bv
                Cq[i][t] = bx

    out = []
    shrink = 1.0 - 1e-12

    def build(t, x0, y0, size):
        if t <= 0:
            return
        ch = choice[t]
        if ch[0] == 'single':
            out.append((x0 + size / 2, y0 + size / 2, 0.0, size * shrink))
        elif ch[0] == 'same':
            build(t - 1, x0, y0, size)
        else:
            q = ch[1]
            m, tl = structs[q]
            cs = size / m
            s_rem = t
            for i in range(len(tl), 0, -1):
                x = CH[q][i][s_rem]
                s_rem -= x
                r, c, s = tl[i - 1]
                if x > 0:
                    build(x, x0 + c * cs, y0 + r * cs, s * cs)

    build(n, 0.0, 0.0, 1.0)
    out = out[:n]
    out = [(min(1.0, max(0.0, a)), min(1.0, max(0.0, b)), 0.0, min(1.0, max(0.0, s)))
           for (a, b, _, s) in out]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END