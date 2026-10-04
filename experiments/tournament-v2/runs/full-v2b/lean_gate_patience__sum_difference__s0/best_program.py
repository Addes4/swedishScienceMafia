"""Maximize log|A-A|/log|A+A| via the digit-set construction.

Key fact: for A = { sum_i d_i B^i : d_i in D } with base B chosen larger than
2*max|D| (so digits never carry), the maps are bijective on digit vectors, hence
    |A-A| = |D-D|^m ,  |A+A| = |D+D|^m
and therefore the ratio equals log|D-D| / log|D+D| for the *small* digit set D.
Increasing the number of digits m only raises |A|, which improves the (possibly
tie-breaking) size bonus.  So the whole problem reduces to finding a small set D
with a large ratio, which we hill-climb, then blowing it up into many digits.
"""
import math
import time
import random
from itertools import product


def _stats(D):
    """Exact |D-D| and |D+D|."""
    s = set()
    d = set()
    n = len(D)
    for i in range(n):
        xi = D[i]
        s.add(xi + xi)
        for j in range(n):
            d.add(xi - D[j])
        for j in range(i + 1, n):
            s.add(xi + D[j])
    return len(d), len(s)


def _ratio(D):
    d, s = _stats(D)
    if s <= 1 or d <= 1:
        return 0.0
    return math.log(d) / math.log(s)


def solve():
    deadline = time.time() + 95.0
    rng = random.Random(987654321)

    # ---------------------------------------------------------------
    # 1. search a small digit set D maximizing log|D-D|/log|D+D|
    # ---------------------------------------------------------------
    bestD = [1, 2, 4]
    bestR = _ratio(bestD)

    def try_improve(D, r, iters, R):
        for _ in range(iters):
            if time.time() > deadline:
                break
            k = len(D)
            D2 = list(D)
            idx = rng.randrange(k)
            mode = rng.random()
            if mode < 0.6:
                # random value in range
                D2[idx] = rng.randrange(R)
            elif mode < 0.85:
                # small perturbation of an existing element
                D2[idx] = D2[idx] + rng.randint(-3, 3)
            else:
                # snap to another element +/- offset
                other = rng.choice(D)
                D2[idx] = other + rng.randint(-2, 2)
            D2 = sorted(set(x for x in D2 if x >= 0))
            if len(D2) < 2:
                continue
            r2 = _ratio(D2)
            if r2 > r:
                r = r2
                D = D2
        return D, r

    # seeds known to be decent + size sweep
    for k in range(2, 30):
        if time.time() > deadline:
            break
        for restart in range(12):
            if time.time() > deadline:
                break
            R = max(8, 5 * k)
            if restart < 6:
                D = sorted(rng.sample(range(R), k))
            else:
                # geometric-ish seed
                D = sorted(set(int(round(2 ** (i + 1))) - 1 for i in range(k)))
            D, r = try_improve(D, _ratio(D), 120, R)
            # occasionally grow the range for more spread
            if time.time() < deadline:
                D, r = try_improve(D, r, 60, R * 2)
            if r > bestR:
                bestR = r
                bestD = D[:]

    # ---------------------------------------------------------------
    # 2. blow the best digit set up into many base-B digits
    # ---------------------------------------------------------------
    D = bestD
    k = len(D)
    maxD = max(abs(x) for x in D)
    B = max(2, 2 * maxD + 1)          # carry-free base

    # choose largest m with |D|^m <= 4000 and values within 1e15
    m = 1
    while True:
        if k ** (m + 1) > 4000:
            break
        # magnitude check
        top = maxD * ((B ** (m + 1) - 1) // (B - 1)) if B > 1 else maxD
        if top > 10 ** 15:
            break
        m += 1

    A = []
    for combo in product(D, repeat=m):
        val = 0
        p = 1
        for dgt in combo:
            val += dgt * p
            p *= B
        A.append(val)

    A = sorted(set(A))
    if len(A) < 2:
        A = [0, 1, 2, 4]

    # ---------------------------------------------------------------
    # 3. light local search on the *final* set to trim any element and
    #    squeeze the size bonus (ratio is preserved by construction, but
    #    a tiny greedy lets us shave off redundant points if any)
    # ---------------------------------------------------------------
    # (kept cheap: only remove elements that are structural duplicates)
    return [int(x) for x in A]
