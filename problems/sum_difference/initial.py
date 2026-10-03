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


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
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
    return sorted(set(best))
# EVOLVE-BLOCK-END
