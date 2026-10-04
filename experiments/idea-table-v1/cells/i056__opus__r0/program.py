# EVOLVE-BLOCK-START
"""Generalised Erdos-Soifer construction: k x k grid with up to two corner
m x m blocks re-gridded into p x p squares; search over k, m1, m2, p1, p2."""
import math


def _best_plan(n):
    best = (-1.0, None)
    kmax = math.isqrt(n) + 3
    for k in range(1, kmax + 1):
        base_cnt = k * k
        for m1 in range(0, k + 1):
            for m2 in range(0, k - m1 + 1):
                if m2 > m1:
                    continue
                cnt0 = base_cnt - m1 * m1 - m2 * m2
                if cnt0 > n:
                    continue
                s0 = (k * k - m1 * m1 - m2 * m2) / k
                p1_range = range(0, math.isqrt(n - cnt0) + 1) if m1 > 0 else [0]
                for p1 in p1_range:
                    rem = n - cnt0 - p1 * p1
                    if rem < 0:
                        break
                    if m2 > 0:
                        p2 = math.isqrt(rem)
                    else:
                        p2 = 0
                    tot = s0 + (p1 * m1 + p2 * m2) / k
                    if tot > best[0] + 1e-12:
                        best = (tot, (k, m1, p1, m2, p2))
    return best


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    tot, plan = _best_plan(n)
    k, m1, p1, m2, p2 = plan
    c = 1.0 / k
    squares = []
    for i in range(k):
        for j in range(k):
            in1 = i < m1 and j < m1
            in2 = i >= k - m2 and j >= k - m2
            if in1 or in2:
                continue
            squares.append(((i + 0.5) * c, (j + 0.5) * c, 0.0, c))
    # block 1 at bottom-left
    if m1 > 0 and p1 > 0:
        L = m1 * c
        s = L / p1
        for a in range(p1):
            for b in range(p1):
                squares.append(((a + 0.5) * s, (b + 0.5) * s, 0.0, s))
    # block 2 at top-right
    if m2 > 0 and p2 > 0:
        L = m2 * c
        off = 1.0 - L
        s = L / p2
        for a in range(p2):
            for b in range(p2):
                squares.append((off + (a + 0.5) * s, off + (b + 0.5) * s, 0.0, s))
    out = []
    for (x, y, ang, sd) in squares[:n]:
        sd = max(0.0, min(1.0, sd * (1 - 1e-12)))
        x = min(1.0, max(0.0, x))
        y = min(1.0, max(0.0, y))
        out.append((x, y, ang, sd))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
