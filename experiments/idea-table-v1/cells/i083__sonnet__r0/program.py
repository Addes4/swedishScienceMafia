# EVOLVE-BLOCK-START
"""Randomised skyline packing of integer squares on a k x k grid (exact rational
verification), choose the best k; pad with zero-size squares."""
import math
import random
import time
from fractions import Fraction


def _trial(k, n, e, rng):
    h = [0] * k
    placed = []
    total = 0
    while len(placed) < n:
        m = min(h)
        if m >= k:
            break
        i = h.index(m)
        j = i
        while j < k and h[j] == m:
            j += 1
        mx = min(j - i, k - m)
        sizes = list(range(1, mx + 1))
        if mx == 1:
            s = 1
        else:
            ws = [t ** e for t in sizes]
            s = rng.choices(sizes, ws)[0]
        placed.append((i, m, s))
        total += s
        for x in range(i, i + s):
            h[x] += s
    return total, placed


def _verify(k, placed):
    # exact check on the integer grid with Fractions
    rects = [(Fraction(x, k), Fraction(y, k), Fraction(x + s, k), Fraction(y + s, k))
             for x, y, s in placed]
    for a in rects:
        if a[0] < 0 or a[1] < 0 or a[2] > 1 or a[3] > 1:
            return False
    for i in range(len(rects)):
        a = rects[i]
        for j in range(i + 1, len(rects)):
            b = rects[j]
            if min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1]):
                return False
    return True


def solve(n):
    rng = random.Random(12345 + n)
    t0 = time.time()
    budget = 15.0
    kmax = max(2, min(16, 2 * math.isqrt(n) + 3))
    ks = list(range(1, kmax + 1))
    best = (Fraction(0), None, None)
    # baseline
    kb = math.isqrt(n)
    base = [(i, j, 1) for i in range(kb) for j in range(kb)]
    best = (Fraction(len(base), kb), kb, base)
    rounds = 0
    while time.time() - t0 < budget:
        rounds += 1
        for k in ks:
            if k * k < 1:
                continue
            for _ in range(20):
                e = rng.uniform(-1.0, 5.0)
                tot, placed = _trial(k, n, e, rng)
                val = Fraction(tot, k)
                if val > best[0]:
                    if _verify(k, placed):
                        best = (val, k, placed)
            if time.time() - t0 > budget:
                break
    _, k, placed = best
    eps = 1e-12
    out = []
    for x, y, s in placed:
        side = s / k
        cx = (x + s / 2.0) / k
        cy = (y + s / 2.0) / k
        side = max(0.0, side - eps)
        out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, side))
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
