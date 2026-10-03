# EVOLVE-BLOCK-START
"""L-frame recursion: corner square plus a two-arm frame of side 1/j,
remaining (1-1/j) square filled recursively; plus k x k grids."""
import math


def _build_table(n):
    best = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    choice[0] = ('empty',)
    for m in range(1, n + 1):
        # option: point square added to best[m-1]
        b = best[m - 1]
        c = ('point',)
        # option: k x k grid
        k = math.isqrt(m)
        if k >= 1 and k > b + 1e-12:
            b = float(k)
            c = ('grid', k)
        # option: L-frame with side 1/j (uses 2j-1 squares)
        j = 1
        while 2 * j - 1 <= m:
            rest = m - (2 * j - 1)
            val = (2 * j - 1) / j + (1 - 1.0 / j) * best[rest]
            if val > b + 1e-12:
                b = val
                c = ('frame', j)
            j += 1
        best[m] = b
        choice[m] = c
    return best, choice


def _place(m, x0, y0, s, choice, out):
    """Place configuration for m squares into square [x0,x0+s]x[y0,y0+s]."""
    while m > 0:
        c = choice[m]
        if c[0] == 'point':
            out.append((x0 + s / 2, y0 + s / 2, 0.0, 0.0))
            m -= 1
        elif c[0] == 'grid':
            k = c[1]
            a = s / k
            for i in range(k):
                for jj in range(k):
                    out.append((x0 + (i + 0.5) * a, y0 + (jj + 0.5) * a, 0.0, a))
            # remaining m - k*k handled as points
            for _ in range(m - k * k):
                out.append((x0 + s / 2, y0 + s / 2, 0.0, 0.0))
            m = 0
        elif c[0] == 'frame':
            j = c[1]
            a = s / j
            for i in range(j):
                out.append((x0 + (i + 0.5) * a, y0 + 0.5 * a, 0.0, a))
            for i in range(1, j):
                out.append((x0 + 0.5 * a, y0 + (i + 0.5) * a, 0.0, a))
            m -= 2 * j - 1
            x0 += a
            y0 += a
            s -= a
            if s <= 0:
                for _ in range(m):
                    out.append((min(1.0, max(0.0, x0)), min(1.0, max(0.0, y0)), 0.0, 0.0))
                m = 0
        else:
            break


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    best, choice = _build_table(n)
    out = []
    _place(n, 0.0, 0.0, 1.0, choice, out)
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    res = []
    for (x, y, ang, sd) in out[:n]:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), ang, min(1.0, max(0.0, sd))))
    return res
# EVOLVE-BLOCK-END
