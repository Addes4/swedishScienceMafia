# EVOLVE-BLOCK-START
"""Grid constructions: k x k grid of side 1/k where an a x a corner block is
replaced by a b x b grid of squares of side a/(k b). Includes the plain
ceil(sqrt(n)) grid with n cells (a = 0). Extra squares are dropped (smallest
first), missing ones padded with size-zero squares."""
import math


def _evaluate(n, k, a, b):
    """Return (value, u, v): best total using u unit cells (side 1/k) and
    v block cells (side a/(k b)) with u + v <= n."""
    U = k * k - a * a
    V = b * b if (a > 0 and b > 0) else 0
    s_unit = 1.0 / k
    s_blk = (a / (k * b)) if V > 0 else 0.0
    budget = n
    if s_blk > s_unit:
        v = min(V, budget)
        u = min(U, budget - v)
    else:
        u = min(U, budget)
        v = min(V, budget - u)
    return u * s_unit + v * s_blk, u, v


def _build(n, k, a, b, u, v):
    eps = 1e-12
    unit = 1.0 / k
    cells = []
    for i in range(k):
        for j in range(k):
            if i < a and j < a:
                continue
            cells.append(((i + 0.5) * unit, (j + 0.5) * unit, 0.0, unit * (1 - eps)))
    blk = []
    if a > 0 and b > 0:
        s = a / (k * b)
        for i in range(b):
            for j in range(b):
                blk.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s * (1 - eps)))
    res = cells[:u] + blk[:v]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    out = []
    for (x, y, t, s) in res[:n]:
        out.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), t, min(max(s, 0.0), 1.0)))
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    r = math.isqrt(n)
    kmax = 2 * r + 4
    bmax = r + 3
    best = (-1.0, None)
    for k in range(1, kmax + 1):
        for a in range(0, k + 1):
            brange = [0] if a == 0 else range(1, bmax + 1)
            for b in brange:
                val, u, v = _evaluate(n, k, a, b)
                if val > best[0] + 1e-12:
                    best = (val, (k, a, b, u, v))
    k, a, b, u, v = best[1]
    return _build(n, k, a, b, u, v)
# EVOLVE-BLOCK-END
