# EVOLVE-BLOCK-START
"""Simplex-lattice construction (chosen by exact counting formulas) plus random local search fallback."""
import math
import random
import time
from math import comb, factorial


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def _formula(n, d):
    size = comb(n + d, d)
    s = comb(2 * n + d, d)
    t = 0
    for p in range(0, min(d, n) + 1):
        for q in range(0, min(d - p, n) + 1):
            t += (factorial(d) // (factorial(p) * factorial(q) * factorial(d - p - q))) * comb(n, p) * comb(n, q)
    return math.log(t) / math.log(s) + (1 - 1 / size) / 100, size


def _build(n, d):
    base = 2 * n + 1
    pts = []

    def rec(i, rem, val):
        if i == d:
            pts.append(val)
            return
        for x in range(rem + 1):
            rec(i + 1, rem - x, val * base + x)

    rec(0, n, 0)
    return pts


def solve():
    best_f = (0.0, None)
    for n in range(1, 60):
        for d in range(1, 60):
            if comb(n + d, d) > 4000:
                break
            if comb(n + d, d) < 2:
                continue
            if base_ok(n, d):
                f, size = _formula(n, d)
                if f > best_f[0]:
                    best_f = (f, (n, d))
    cand_simplex = None
    if best_f[1] is not None:
        cand_simplex = _build(*best_f[1])
        simplex_score = best_f[0]
    else:
        simplex_score = 0.0

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score(best)
    cur = best[:]
    deadline = time.time() + 20
    while time.time() < deadline:
        cand = cur[:]
        i = random.randrange(len(cand))
        cand[i] += random.randint(-3, 3)
        if random.random() < 0.05:
            cand.append(random.randint(1, 20))
        if random.random() < 0.03 and len(cand) > 5:
            cand = cand[1:]
        s = _score(cand)
        if s >= best_score:
            best, best_score, cur = cand[:], s, cand
        elif random.random() < 0.1:
            cur = best[:]
    if cand_simplex is not None and simplex_score > best_score:
        return sorted(set(cand_simplex))
    return sorted(set(best))


def base_ok(n, d):
    return (2 * n + 1) ** d < 10 ** 15 // 2
# EVOLVE-BLOCK-END
