# EVOLVE-BLOCK-START
"""Recursive grid-with-block construction.

Take an m x m grid of squares of side 1/m, and replace a j x j block of cells
(a square of side j/m) by a scaled copy of the best construction for n'
squares.  Count = m^2 - j^2 + n', sum = m - j^2/m + (j/m) * F(n').
Zero-size squares pad any missing count, so F is monotone.
"""
import math


def _plan(n):
    F = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    choice[0] = ('empty',)
    for t in range(1, n + 1):
        best = F[t - 1]
        ch = ('pad',)
        # plain grids
        k = math.isqrt(t)
        if k > best + 1e-15:
            best = float(k)
            ch = ('grid', k)
        # grid with a recursive block
        for m in range(2, t + 2):
            if 2 * m - 1 > t:
                break
            for j in range(1, m):
                base = m * m - j * j
                if base > t:
                    continue
                np_ = t - base
                if np_ >= t:
                    continue
                val = m - j * j / m + (j / m) * F[np_]
                if val > best + 1e-12:
                    best = val
                    ch = ('block', m, j, np_)
        F[t] = best
        choice[t] = ch
    return F, choice


def _build(t, x0, y0, s, choice, out):
    ch = choice[t]
    if ch[0] == 'empty':
        return
    if ch[0] == 'pad':
        _build(t - 1, x0, y0, s, choice, out)
        return
    if ch[0] == 'grid':
        k = ch[1]
        c = s / k
        for i in range(k):
            for jj in range(k):
                out.append((x0 + (i + 0.5) * c, y0 + (jj + 0.5) * c, c))
        return
    _, m, j, np_ = ch
    c = s / m
    for i in range(m):
        for jj in range(m):
            if i < j and jj < j:
                continue
            out.append((x0 + (i + 0.5) * c, y0 + (jj + 0.5) * c, c))
    _build(np_, x0, y0, s * j / m, choice, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    F, choice = _plan(n)
    raw = []
    _build(n, 0.0, 0.0, 1.0, choice, raw)
    shrink = 1.0 - 1e-12
    squares = []
    for (cx, cy, s) in raw[:n]:
        cx = min(1.0, max(0.0, cx))
        cy = min(1.0, max(0.0, cy))
        side = min(1.0, max(0.0, s * shrink))
        squares.append((cx, cy, 0.0, side))
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares[:n]
# EVOLVE-BLOCK-END
