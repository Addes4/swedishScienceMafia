# EVOLVE-BLOCK-START
"""Grid of side 1/k with one corner m x m block re-tiled by a p x p grid.
Count = k^2 - m^2 + p^2, sum = k - m^2/k + m*p/k.  With p = m +/- 1 this
realises f(k^2 + 2c + 1) >= k + c/k (|c| < k).  Remaining squares have size 0."""
import math


def _best_config(n):
    best = None  # (value, k, m, p)
    kmax = math.isqrt(n) + 3
    for k in range(1, kmax + 1):
        if k * k > n + 4 * k * k:  # never triggers; keep loop simple
            break
        for m in range(0, k + 1):
            base = k * k - m * m
            if base > n:
                continue
            rem = n - base
            pmax = math.isqrt(rem)
            for p in range(0, pmax + 1):
                if m == 0 and p > 0:
                    continue
                val = k - m * m / k + m * p / k
                if best is None or val > best[0] + 1e-12:
                    best = (val, k, m, p)
    return best


def solve(n):
    if n <= 0:
        return []
    val, k, m, p = _best_config(n)
    shrink = 1.0 - 1e-12
    squares = []
    s = 1.0 / k
    for i in range(k):
        for j in range(k):
            if i < m and j < m:
                continue
            squares.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s * shrink))
    if m > 0 and p > 0:
        t = (m / k) / p
        for i in range(p):
            for j in range(p):
                squares.append(((i + 0.5) * t, (j + 0.5) * t, 0.0, t * shrink))
    squares = squares[:n]
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares
# EVOLVE-BLOCK-END
