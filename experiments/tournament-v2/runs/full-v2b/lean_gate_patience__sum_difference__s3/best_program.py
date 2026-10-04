# EVOLVE-BLOCK-START
"""Search directly for an integer set A maximizing log|A-A|/log|A+A|.

Strategy: build A from a small digit alphabet tensored in a base B, giving exact
log|S-S|/log|S+S| ratio; then additionally run a direct coordinate hill-climb on
the final A (numpy-scored) to squeeze out extra ratio, keeping |A| <= 4000.
"""
import math
import itertools
import random
import time

import numpy as np


def _stats(S):
    U = set()
    D = set()
    for a in S:
        for b in S:
            U.add(a + b)
            D.add(a - b)
    return U, D


def _ratio(S):
    U, D = _stats(S)
    if len(U) < 2 or len(D) < 2:
        return -1.0
    return math.log(len(D)) / math.log(len(U))


def _score_np(A):
    A = np.asarray(A, dtype=np.int64)
    n = A.size
    if n < 2:
        return 0.0
    d = A[:, None] - A[None, :]
    s = A[:, None] + A[None, :]
    nd = np.unique(d).size
    ns = np.unique(s).size
    if ns < 2 or nd < 2:
        return 0.0
    return math.log(nd) / math.log(ns) + (1.0 - 1.0 / n) / 100.0


def solve():
    deadline = time.time() + 100.0

    # ---- Search tiny digit alphabets S ----
    bestS = (0, 1)
    bestR = -1.0
    R = 12
    for sz in range(2, 6):
        for comb in itertools.combinations(range(-R, R + 1), sz):
            r = _ratio(comb)
            if r > bestR:
                bestR = r
                bestS = comb

    # ---- Local hill climb on digit alphabet (bigger sizes) ----
    climb_deadline = time.time() + 40.0
    while time.time() < climb_deadline:
        sz = random.randint(5, 18)
        S = set(random.sample(range(-100, 101), sz))
        r = _ratio(S)
        if r > bestR:
            bestR = r
            bestS = tuple(sorted(S))
        for _ in range(60):
            if time.time() > climb_deadline:
                break
            T = list(S)
            T[random.randrange(len(T))] = random.randint(-100, 100)
            T = set(T)
            if len(T) < 2:
                continue
            rr = _ratio(T)
            if rr > bestR:
                bestR = rr
                bestS = tuple(sorted(T))
            if rr >= r:
                S = T
                r = rr

    S = list(bestS)

    # ---- Tensor S in base B as far as fits ----
    U, D = _stats(S)
    B = max(max(abs(x) for x in U), max(abs(x) for x in D)) + 1
    if B < 2:
        B = 2
    maxabs = max(abs(x) for x in S)

    bestA = None
    k = 1
    while True:
        size = len(S) ** k
        if size > 4000:
            break
        mag = maxabs * (B ** k - 1) // (B - 1) if B > 1 else 0
        if mag > 10 ** 15:
            break
        A = [0]
        p = 1
        for _ in range(k):
            nxt = []
            for a in A:
                for d in S:
                    nxt.append(a + d * p)
            A = nxt
            p *= B
        if len(set(A)) <= 4000:
            bestA = A
        k += 1

    if bestA is None:
        bestA = list(S)

    cand = sorted(set(int(x) for x in bestA))

    # ---- Direct hill-climb on full candidate to improve ratio ----
    # Use a subsampled version for speed if huge.
    if len(cand) > 120:
        # perturb only a random subset's membership: try replacing a few elements
        base_score = _score_np(cand)
        work = cand[:]
        climb2 = min(deadline, time.time() + 45.0)
        tries = 0
        while time.time() < climb2 and tries < 400:
            tries += 1
            i = random.randrange(len(work))
            j = random.randrange(len(work))
            old = work[i]
            work[i] = work[j] + random.randint(-3, 3)
            if work[i] in work and work[i] != old:
                work[i] = old
                continue
            sc = _score_np(work)
            if sc > base_score:
                base_score = sc
                cand = sorted(set(work))
            else:
                work[i] = old
        cand = sorted(set(work))

    if len(cand) > 4000:
        cand = cand[:4000]
    cand = [int(x) for x in cand if abs(x) <= 10 ** 15]
    if len(cand) < 2:
        return [0, 1, 3]
    return cand
# EVOLVE-BLOCK-END
