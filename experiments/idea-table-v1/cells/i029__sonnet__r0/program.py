# EVOLVE-BLOCK-START
"""Nested Erdos-Soifer style replacement, found by DP over n.

g[n] = best sum for n squares in the unit square. Options:
 - drop one square (size 0)
 - k x k grid (k^2 <= n)
 - s x s grid where an a x a corner block of cells is replaced by a scaled
   copy of the best packing with c squares (recursive => nested replacement).
"""
import math


def _plan(n):
    g = [0.0] * (n + 1)
    ch = [None] * (n + 1)
    for m in range(1, n + 1):
        k = math.isqrt(m)
        best = float(k)
        choice = ("grid", k)
        if m > 1 and g[m - 1] > best + 1e-12:
            best = g[m - 1]
            choice = ("drop",)
        s = 2
        while 2 * s - 1 <= m - 1:
            for a in range(1, s):
                rest = s * s - a * a
                c = m - rest
                if c < 1:
                    break
                val = (rest + a * g[c]) / s
                if val > best + 1e-12:
                    best = val
                    choice = ("blk", s, a, c)
            s += 1
        g[m] = best
        ch[m] = choice
    return g, ch


def _build(m, ch):
    if m <= 0:
        return []
    choice = ch[m]
    if choice[0] == "drop":
        return _build(m - 1, ch) + [(0.5, 0.5, 0.0, 0.0)]
    if choice[0] == "grid":
        k = choice[1]
        side = 1.0 / k
        sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
              for i in range(k) for j in range(k)]
        sq += [(0.5, 0.5, 0.0, 0.0)] * (m - len(sq))
        return sq
    _, s, a, c = choice
    cell = 1.0 / s
    sub = _build(c, ch)
    f = a * cell
    out = [(x * f, y * f, ang, sd * f) for (x, y, ang, sd) in sub]
    for i in range(s):
        for j in range(s):
            if i >= a or j >= a:
                out.append(((i + 0.5) * cell, (j + 0.5) * cell, 0.0, cell))
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    g, ch = _plan(n)
    sq = _build(n, ch)
    res = []
    for (x, y, a, s) in sq:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
