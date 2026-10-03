# EVOLVE-BLOCK-START
"""Nested two-level Erdos-Soifer construction:
k x k grid; replace an m x m block by (m+-1)^2 squares; inside that sub-grid,
replace an m2 x m2 block by (m2+-1)^2 squares. Pick best total with count <= n,
pad with zero squares."""
import math


def _grid(x0, y0, cell, g, skip):
    out = []
    for i in range(g):
        for j in range(g):
            if i < skip and j < skip:
                continue
            out.append((x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell, 0.0, cell))
    return out


def solve(n):
    best_val = -1.0
    best_cfg = None
    kmax = math.isqrt(n) + 2
    for k in range(1, kmax + 1):
        base_cnt = k * k
        if base_cnt <= n:
            v = float(k)
            if v > best_val + 1e-12:
                best_val, best_cfg = v, (k, 0, 0, 0, 0)
        for m in range(1, k + 1):
            for s1 in (1, -1):
                g1 = m + s1
                if g1 < 1:
                    continue
                c1 = (m / k) / g1
                cnt1 = k * k - m * m + g1 * g1
                sum1 = (k * k - m * m) / k + g1 * g1 * c1
                if cnt1 <= n and sum1 > best_val + 1e-12:
                    best_val, best_cfg = sum1, (k, m, s1, 0, 0)
                if cnt1 - (2 * g1 + 1) > n + 4 * g1 + 4:
                    # second level can change count by at most ~2*g1+1
                    pass
                for m2 in range(1, g1 + 1):
                    for s2 in (1, -1):
                        g2 = m2 + s2
                        if g2 < 1:
                            continue
                        cnt2 = cnt1 - m2 * m2 + g2 * g2
                        if cnt2 > n:
                            continue
                        sum2 = sum1 + s2 * m2 * c1
                        if sum2 > best_val + 1e-12:
                            best_val, best_cfg = sum2, (k, m, s1, m2, s2)

    k, m, s1, m2, s2 = best_cfg
    squares = []
    cell = 1.0 / k
    squares += _grid(0.0, 0.0, cell, k, m)
    if m > 0:
        g1 = m + s1
        c1 = (m / k) / g1
        squares += _grid(0.0, 0.0, c1, g1, m2)
        if m2 > 0:
            g2 = m2 + s2
            c2 = m2 * c1 / g2
            squares += _grid(0.0, 0.0, c2, g2, 0)
    squares = [(min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s)))
               for (x, y, a, s) in squares]
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
