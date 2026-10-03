# EVOLVE-BLOCK-START
"""DP over corner-frame recursion plus grids."""
import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    val = [0.0] * (n + 1)
    choice = [("zero", 0)] * (n + 1)
    for m in range(1, n + 1):
        bv, bc = val[m - 1], ("pad", 0)
        k = math.isqrt(m)
        if k * k > 0 and float(k) > bv + 1e-12:
            # grid sum = k*k*(1/k) = k
            bv, bc = float(k), ("grid", k)
        j = 1
        while 2 * j - 1 <= m:
            r = m - (2 * j - 1)
            v = (2 * j - 1) / j + (1 - 1.0 / j) * val[r]
            if v > bv + 1e-12:
                bv, bc = v, ("frame", j)
            j += 1
        val[m] = bv
        choice[m] = bc

    def build(m):
        if m == 0:
            return []
        kind, p = choice[m]
        if kind == "pad":
            return build(m - 1) + [(0.5, 0.5, 0.0, 0.0)]
        if kind == "grid":
            k = p
            s = 1.0 / k
            sq = [((i + 0.5) * s, (jj + 0.5) * s, 0.0, s)
                  for i in range(k) for jj in range(k)]
            return sq + [(0.5, 0.5, 0.0, 0.0)] * (m - len(sq))
        j = p
        s = 1.0 / j
        sq = [((i + 0.5) * s, 0.5 * s, 0.0, s) for i in range(j)]
        sq += [(0.5 * s, (r + 1.5) * s, 0.0, s) for r in range(j - 1)]
        rem = m - len(sq)
        sub = build(rem)
        sc = 1.0 - s
        for (x, y, a, d) in sub:
            sq.append((s + x * sc, s + y * sc, a, d * sc))
        return sq

    res = build(n)
    out = []
    for (x, y, a, d) in res:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, d))))
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out[:n]
# EVOLVE-BLOCK-END
