# EVOLVE-BLOCK-START
"""Construct A as subset-sums over a tuned digit alphabet D.

If A = { sum_i d_i B^i : d_i in D } with B large enough that no two digit-vectors
collide (no carries), then exactly

    |A - A| = |D - D|^k ,   |A + A| = |D + D|^k

so the objective log|A-A|/log|A+A| = log|D-D|/log|D+D| is independent of k.
Therefore we only need to find a small integer alphabet D maximizing
log|D-D|/log|D+D|, then replicate it (largest k with |D|^k <= 4000) for the size bonus.
"""
import math
import random
import time
from itertools import product


def _ddstats(D):
    """Return (|D-D|, |D+D|) for a (small) integer set D."""
    D = list(set(D))
    dd = len({a - b for a in D for b in D})
    ss = len({a + b for a in D for b in D})
    return dd, ss


def _ratio(D):
    dd, ss = _ddstats(D)
    if dd < 2 or ss < 2:
        return 0.0
    return math.log(dd) / math.log(ss)


def _search_alphabet(deadline):
    """Hill-climb over small integer alphabets D, maximizing log|D-D|/log|D+D|."""
    R = 34
    best_D = [0, 1, 2, 4, 8, 16]
    best_r = _ratio(best_D)
    seed_pool = [[0, 1], [0, 1, 3], [0, 1, 2, 4, 8, 16], [0, 1, 2, 4],
                 [0, 1, 3, 7, 15], [0, 1, 2, 4, 8, 16, 32]]
    for sp in seed_pool:
        r = _ratio(sp)
        if r > best_r:
            best_r, best_D = r, sp[:]

    while time.time() < deadline:
        # random restart
        s = random.randint(2, 13)
        D = sorted(random.sample(range(0, R + 1), s))
        r = _ratio(D)
        for _ in range(400):
            if time.time() >= deadline:
                break
            cand = D[:]
            op = random.random()
            if op < 0.7 and cand:
                i = random.randrange(len(cand))
                cand[i] = random.randint(0, R)
            elif op < 0.85:
                cand.append(random.randint(0, R))
            elif len(cand) > 2:
                cand.pop(random.randrange(len(cand)))
            cand = sorted(set(cand))
            if len(cand) < 2:
                continue
            cr = _ratio(cand)
            if cr >= r:
                D, r = cand, cr
        if r > best_r:
            best_r, best_D = r, D[:]
    return best_D, best_r


def _build(D, cap=4000):
    """Build the product set (subset sums) from alphabet D, largest size <= cap."""
    D = sorted(set(D))
    D = [d - min(D) for d in D]          # normalize to start at 0
    s = len(D)
    if s < 2:
        return [0, 1]
    k = 1
    while s ** (k + 1) <= cap:
        k += 1
    span = max(D) - min(D)
    B = 2 * span + 1                     # no carries between digit positions
    vals = []
    for combo in product(D, repeat=k):
        v = 0
        p = 1
        for d in combo:
            v += d * p
            p *= B
        vals.append(v)
    return sorted(set(vals))


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    if len(diffs) < 2 or len(sums) < 2:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def solve():
    deadline = time.time() + 55
    D, r = _search_alphabet(deadline)

    candidates = []
    # product from best alphabet
    candidates.append(_build(D))
    # products from a few known structured alphabets as fallback
    for sp in ([0, 1, 2, 4, 8, 16], [0, 1, 2, 4, 8], [0, 1, 3, 7, 15],
               [0, 1, 2, 4], [0, 1, 2, 3, 4, 5]):
        candidates.append(_build(sp))
    candidates.append([7, 15, 18, 22, -3, -2])

    best = None
    best_s = -1.0
    for c in candidates:
        if len(c) < 2:
            continue
        sc = _score(c)
        if sc > best_s:
            best_s, best = sc, c

    return list(best)
# EVOLVE-BLOCK-END
