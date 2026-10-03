# EVOLVE-BLOCK-START
"""Erdos-Soifer family: k x k grid with one a x a block of cells replaced by a
b x b grid of equal squares (b = a+1 gives n = k^2 + 2a + 1 and total k + a/k;
b = 1 merges a block; b = 0 leaves a hole). Pad with zero-size squares."""
import math


def _build(k, a, b):
    """k x k grid of side 1/k, a x a corner block replaced by b x b squares."""
    s = 1.0 / k
    sq = []
    for i in range(k):
        for j in range(k):
            if i < a and j < a:
                continue
            sq.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
    if b > 0 and a > 0:
        t = a * s / b
        for i in range(b):
            for j in range(b):
                sq.append(((i + 0.5) * t, (j + 0.5) * t, 0.0, t))
    return sq


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    best_val = -1.0
    best_cfg = (1, 0, 0)
    kmax = math.isqrt(n) + 2
    for k in range(1, kmax + 1):
        for a in range(0, k + 1):
            base = k * k - a * a
            if base > n:
                continue
            # b ranges so that base + b^2 <= n
            bmax = math.isqrt(n - base)
            for b in range(0, bmax + 1):
                if a == 0 and b > 0:
                    continue
                cnt = base + b * b
                if cnt > n:
                    break
                val = (k * k - a * a) / k + (a / k if b > 0 else 0.0)
                if val > best_val + 1e-12:
                    best_val = val
                    best_cfg = (k, a, b)
    k, a, b = best_cfg
    squares = _build(k, a, b)
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END
