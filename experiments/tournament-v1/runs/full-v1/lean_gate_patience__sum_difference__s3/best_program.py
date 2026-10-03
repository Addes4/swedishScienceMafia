# EVOLVE-BLOCK-START
"""Simplex lattice points embedded in integers; search over (d, n) with exact formulas."""
import math
from math import comb, factorial


def _counts(d, n):
    sums = comb(2 * n + d, d)
    diffs = 0
    for j in range(0, min(n, d) + 1):
        for k in range(0, min(n, d - j) + 1):
            multi = factorial(d) // (factorial(j) * factorial(k) * factorial(d - j - k))
            diffs += multi * comb(n, j) * comb(n, k)
    return diffs, sums


def _simplex(d, n):
    B = 2 * n + 1
    states = [(0, 0)]
    for i in range(d):
        w = B ** i
        new = []
        for v, u in states:
            for x in range(0, n - u + 1):
                new.append((v + x * w, u + x))
        states = new
    return [v for v, u in states]


def solve():
    best_s, best_dn = -1.0, (2, 2)
    for d in range(1, 80):
        for n in range(1, 80):
            size = comb(n + d, d)
            if size < 3 or size > 4000:
                continue
            B = 2 * n + 1
            if n * (B ** (d - 1)) > 9.9e14:
                continue
            df, sm = _counts(d, n)
            if sm < 2:
                continue
            s = math.log(df) / math.log(sm) + (1 - 1 / size) / 100
            if s > best_s:
                best_s, best_dn = s, (d, n)
    d, n = best_dn
    a = _simplex(d, n)
    return sorted(set(int(x) for x in a))
# EVOLVE-BLOCK-END
