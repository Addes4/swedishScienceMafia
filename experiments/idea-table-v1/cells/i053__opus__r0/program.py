# EVOLVE-BLOCK-START
"""Nested shelf packing (rows in columns in rows ...) optimised by exact DP."""
import math
import sys
import time
from fractions import Fraction as F


def solve(n):
    sys.setrecursionlimit(10000)
    if n <= 0:
        return []
    memo = {}
    K = n if n <= 20 else 6
    DEPTH = 3
    t0 = time.time()

    def f(a, b, m, d):
        # a: shelf span length, b: stacking length, m squares, d transposes left
        if m == 0 or a <= 0 or b <= 0:
            return F(0)
        key = (a, b, m, d)
        r = memo.get(key)
        if r is not None:
            return r[0]
        best = F(0)
        choice = None
        cmin = max(1, math.ceil(a / b))
        cmax = min(m, cmin + K)
        for c in range(cmin, cmax + 1):
            s = a / c
            if s > b:
                continue
            v = a + f(a, b - s, m - c, d)
            if v > best:
                best = v
                choice = ('shelf', c)
        if d > 0 and time.time() - t0 < 50:
            v = f(b, a, m, d - 1)
            if v > best:
                best = v
                choice = ('T',)
        memo[key] = (best, choice)
        return best

    total = f(F(1), F(1), n, DEPTH)

    squares = []

    def build(x0, y0, w, h, orient, m, d):
        # orient 0: shelves are rows spanning width w, stacked upward along h
        # orient 1: shelves are columns spanning height h, stacked rightward along w
        while m > 0:
            a, b = (w, h) if orient == 0 else (h, w)
            if a <= 0 or b <= 0:
                return
            key = (a, b, m, d)
            if key not in memo:
                f(a, b, m, d)
            val, ch = memo[key]
            if ch is None:
                return
            if ch[0] == 'T':
                orient = 1 - orient
                d -= 1
                continue
            c = ch[1]
            s = a / c
            for i in range(c):
                if orient == 0:
                    cx = x0 + s * i + s / 2
                    cy = y0 + s / 2
                else:
                    cx = x0 + s / 2
                    cy = y0 + s * i + s / 2
                squares.append((float(cx), float(cy), 0.0, max(0.0, float(s) - 1e-12)))
            if orient == 0:
                y0 = y0 + s
                h = h - s
            else:
                x0 = x0 + s
                w = w - s
            m -= c

    build(F(0), F(0), F(1), F(1), 0, n, DEPTH)

    # grid baseline fallback
    k = math.isqrt(n)
    if float(total) < k - 1e-9 or len(squares) > n:
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side - 1e-12)
                   for i in range(k) for j in range(k)]
    squares = squares[:n]
    while len(squares) < n:
        squares.append((0.0, 0.0, 0.0, 0.0))
    out = []
    for (x, y, a, s) in squares:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return out
# EVOLVE-BLOCK-END
