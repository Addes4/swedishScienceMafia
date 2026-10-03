# EVOLVE-BLOCK-START
"""Baseline: random local search over small integer sets (the official starting program, shortened)."""
import math
import random
import time


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def _simplex_params():
    from math import comb, factorial
    best = None
    for d in range(1, 40):
        for n in range(1, 200):
            size = comb(n + d, d)
            if size > 4000:
                break
            B = 2 * n + 1
            if (B ** d) * n * 2 > 10 ** 15:
                break
            sums = comb(2 * n + d, d)
            diffs = 0
            for k in range(0, min(d, n) + 1):
                for j in range(0, min(d - k, n) + 1):
                    diffs += (factorial(d) // (factorial(k) * factorial(j) * factorial(d - k - j))) \
                        * comb(n, k) * comb(n, j)
            if sums < 2:
                continue
            sc = math.log(diffs) / math.log(sums) + (1 - 1 / size) / 100
            if best is None or sc > best[0]:
                best = (sc, d, n)
    return best


def _simplex_set(d, n):
    B = 2 * n + 1
    pts = []

    def rec(i, rem, val):
        if i == d:
            pts.append(val)
            return
        w = B ** i
        for x in range(rem + 1):
            rec(i + 1, rem - x, val + x * w)

    rec(0, n, 0)
    return pts


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
    try:
        p = _simplex_params()
        if p is not None:
            return sorted(set(_simplex_set(p[1], p[2])))
    except Exception:
        pass
    best = [7, 15, 18, 22, -3, -2]
    best_score = _score(best)
    cur = best[:]
    deadline = time.time() + 5
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
    return sorted(set(best))
# EVOLVE-BLOCK-END