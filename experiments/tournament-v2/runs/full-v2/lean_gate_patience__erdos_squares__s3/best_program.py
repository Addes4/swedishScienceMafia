# EVOLVE-BLOCK-START
"""Shelf packing: split the unit square into horizontal strips, and pack each
strip with either one full row of equal squares or a finer sub-grid."""

import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side)."""
    if n <= 0:
        return []

    best = None
    best_sum = -1.0

    # Try dividing into a strip of height h packed with a * b squares,
    # remainder (height 1-h) packed with a full grid.
    # More generally: try every pair (rows of equal squares).
    # We search over: total squares n = p*q + r*s where the first block
    # occupies a rectangle of q columns and p rows ...
    # Simplify to a strong family: choose integer a,b >= 1 such that
    # a*b <= n; put a*b squares in an a-by-b grid filling the whole square,
    # and put remaining squares as a grid in the leftover... but there is none.
    # Instead, split unit square vertically: top part for one grid, bottom for another.

    # Family: split [0,1]x[0,1] into two horizontal strips of heights h1,h2.
    # Strip i holds a grid of ai columns x bi rows of squares of side
    # min(h_i/bi, 1/ai). Total squares = a1*b1 + a2*b2 = n.
    for a1 in range(1, n + 1):
        for b1 in range(1, n + 1):
            m1 = a1 * b1
            if m1 > n:
                break
            rem = n - m1
            if rem == 0:
                # single grid
                s = min(1.0 / a1, 1.0 / b1)
                tot = m1 * s
                if tot > best_sum:
                    best_sum = tot
                    best = ("one", a1, b1)
                continue
            for a2 in range(1, rem + 1):
                if rem % a2 != 0:
                    continue
                b2 = rem // a2
                # heights: choose h1, h2 >= 0 with h1+h2 = 1
                # side1 = min(h1/b1, 1/a1), side2 = min(h2/b2, 1/a2)
                # maximise m1*s1 + m2*s2
                # s1 limited by 1/a1, s2 by 1/a2.
                s1cap = 1.0 / a1
                s2cap = 1.0 / a2
                # try h1 = b1 * s1cap -> s1 = s1cap, then h2 = 1-h1
                h1 = b1 * s1cap
                if h1 <= 1.0:
                    s1 = s1cap
                    h2 = 1.0 - h1
                    s2 = min(h2 / b2, s2cap)
                else:
                    h1 = 1.0
                    s1 = min(h1 / b1, s1cap)
                    h2 = 0.0
                    s2 = 0.0
                tot = m1 * s1 + rem * s2
                if tot > best_sum:
                    best_sum = tot
                    best = ("two", a1, b1, a2, b2, h1, s1, s2)

    # Also consider vertical split (mirror by swapping roles) implicitly covered
    # since we try all a,b in first grid and all a2,b2 in second.

    out = []
    if best[0] == "one":
        _, a, b = best
        s = min(1.0 / a, 1.0 / b)
        for i in range(a):
            for j in range(b):
                out.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
    else:
        _, a1, b1, a2, b2, h1, s1, s2 = best
        for i in range(a1):
            for j in range(b1):
                x = (i + 0.5) * (1.0 / a1) if 1.0 / a1 <= (h1 / b1) else (i + 0.5) * (h1 / b1)
                # center x within [0,1]: place grid centered
                gx = a1
                gs = s1
                out.append(((i + 0.5) * gs + (1.0 - a1 * gs) * 0.5,
                            (j + 0.5) * gs + (h1 - b1 * gs) * 0.5, 0.0, gs))
        for i in range(a2):
            for j in range(b2):
                gs = s2
                out.append(((i + 0.5) * gs + (1.0 - a2 * gs) * 0.5,
                            h1 + (j + 0.5) * gs + ((1.0 - h1) - b2 * gs) * 0.5,
                            0.0, gs))

    # pad
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
