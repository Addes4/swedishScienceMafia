# EVOLVE-BLOCK-START
"""Grid k x k with one a x b rectangular block re-tiled by p x q equal squares."""
import math


def _top_sum(n, groups):
    # groups: list of (count, side)
    groups = sorted(groups, key=lambda g: -g[1])
    tot = 0.0
    rem = n
    for c, s in groups:
        t = min(c, rem)
        tot += t * s
        rem -= t
        if rem == 0:
            break
    return tot


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    best = None  # (sum, k, a, b, p, q)
    kmax = int(math.isqrt(n)) + 3
    for k in range(1, kmax + 1):
        # plain grid
        v = _top_sum(n, [(k * k, 1.0 / k)])
        if best is None or v > best[0] + 1e-12:
            best = (v, k, 0, 0, 0, 0)
        for a in range(1, k + 1):
            for b in range(a, k + 1):
                rest = k * k - a * b
                for p in range(1, min(n + k * k, 40) + 1):
                    for q in range(p, min(n + k * k, 40) + 1):
                        if p * q > n + k * k:
                            break
                        s = min(a / p, b / q) / k
                        s2 = min(a / q, b / p) / k
                        if s2 > s:
                            s = s2
                            pp, qq = q, p
                        else:
                            pp, qq = p, q
                        v = _top_sum(n, [(rest, 1.0 / k), (p * q, s)])
                        if v > best[0] + 1e-12:
                            best = (v, k, a, b, pp, qq)
    _, k, a, b, p, q = best
    sq = []
    shrink = 1.0 - 1e-9
    if a == 0:
        side = 1.0 / k
        for i in range(k):
            for j in range(k):
                sq.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side * shrink))
    else:
        side = 1.0 / k
        for i in range(k):
            for j in range(k):
                if i < a and j < b:
                    continue
                sq.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side * shrink))
        W = a / k
        H = b / k
        s = min(W / p, H / q)
        for i in range(p):
            for j in range(q):
                cx = (i + 0.5) * W / p
                cy = (j + 0.5) * H / q
                sq.append((cx, cy, 0.0, s * shrink))
    sq.sort(key=lambda t: -t[3])
    sq = sq[:n]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq
# EVOLVE-BLOCK-END
