# EVOLVE-BLOCK-START
"""Block-product over Sidon set with tight spacing and tuned sum-collision search."""
import math
import random
import time

import numpy as np


def _counts(a):
    arr = np.array(a, dtype=np.int64)
    diffs = np.unique(arr[:, None] - arr[None, :])
    sums = np.unique(arr[:, None] + arr[None, :])
    return len(diffs), len(sums)


def _score(a):
    a = sorted(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _counts(a)
    if ns < 2 or nd < 2:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / n) / 100


def _is_prim_root(g, p):
    n = p - 1
    facs = set()
    m = n
    d = 2
    while d * d <= m:
        while m % d == 0:
            facs.add(d)
            m //= d
        d += 1
    if m > 1:
        facs.add(m)
    for q in facs:
        if pow(g, n // q, p) == 1:
            return False
    return True


def _bose_chowla(p):
    g = 2
    while not _is_prim_root(g, p):
        g += 1
    return [pow(g, i, p) for i in range(1, p)]


def _build(B, k, M):
    A = []
    for i in range(k):
        off = i * M
        for b in B:
            A.append(off + b)
    return A


def solve():
    deadline = time.time() + 112
    best = None
    best_score = -1.0
    rng = random.Random(987654321)

    seeds = []
    for p in [29, 53, 101, 211, 401, 809]:
        B = _bose_chowla(p)
        nb = len(B)
        spread = max(B) - min(B)
        baseM = spread + 1
        for k in [2, 3, 4, 5, 6, 7, 8]:
            if k * nb > 4000 or k * nb < 20:
                continue
            # try spacing from very tight (sums collide) to wide
            for mult in [0.05, 0.15, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]:
                M = max(2, int(baseM * mult))
                seeds.append(_build(B, k, M))

    # also try tight spacings relative to B-range itself (not spread+1)
    for p in [53, 101, 211, 401]:
        B = _bose_chowla(p)
        nb = len(B)
        lo, hi = min(B), max(B)
        rngb = hi - lo
        for k in [2, 3, 4, 5, 6]:
            if k * nb > 4000 or k * nb < 20:
                continue
            for M in [rngb, rngb + 1, rngb // 2, rngb // 3, rngb // 4]:
                if M < 2:
                    continue
                seeds.append(_build(B, k, M))

    for s in seeds:
        sc = _score(s)
        if sc > best_score:
            best_score, best = sc, s[:]

    def local_opt(base, tlimit):
        cur = base[:]
        cs = _score(cur)
        curset = set(cur)
        best_local, best_local_s = cur[:], cs
        step = 0
        stall = 0
        while time.time() < tlimit and step < 80000:
            step += 1
            cand = cur[:]
            op = rng.random()
            if op < 0.20 and cand:
                i = rng.randrange(len(cand))
                cand[i] += rng.randint(-20, 20)
            elif op < 0.35 and cand:
                i = rng.randrange(len(cand))
                cand[i] += rng.randint(-3, 3)
            elif op < 0.48:
                if cand:
                    i = rng.randrange(len(cand))
                    cand[i] += rng.choice([-1, 1]) * rng.randint(50, 3000)
            elif op < 0.60:
                cand = sorted(set(cand))
                if cand:
                    i = rng.randrange(len(cand))
                    cand[i] += rng.randint(-300, 300)
            elif op < 0.70 and len(cand) > 5:
                i = rng.randrange(len(cand))
                del cand[i]
            elif op < 0.82:
                # insert near an existing element to fill sums/diffs
                if cand:
                    base_el = rng.choice(cand)
                    cand.append(base_el + rng.randint(-50, 50))
            elif op < 0.92:
                # insert an element that is a + a' for two existing elems (sum-fill)
                if len(cand) >= 2:
                    a1 = rng.choice(cand)
                    a2 = rng.choice(cand)
                    cand.append(a1 + a2 - rng.choice(cand))
            else:
                cand.append(rng.randint(-5000, 5000))
            cand = sorted(set(cand))
            if len(cand) > 4000 or len(cand) < 3:
                continue
            s = _score(cand)
            if s >= cs:
                cur, cs = cand, s
                if s > best_local_s:
                    best_local, best_local_s = cand[:], s
                    stall = 0
                else:
                    stall += 1
            else:
                stall += 1
            if stall > 5000:
                break
        return best_local, best_local_s

    idx = 0
    nseeds = len(seeds)
    while time.time() < deadline:
        if idx < nseeds:
            base = seeds[idx]
            idx += 1
        else:
            if rng.random() < 0.7 and seeds:
                base = [x + rng.randint(-20, 20) for x in rng.choice(seeds)]
            else:
                n = rng.randint(30, 300)
                base = [rng.randint(-10 ** 6, 10 ** 6) for _ in range(n)]
            base = sorted(set(base))
        tlimit = min(deadline, time.time() + 10)
        b, bs = local_opt(base, tlimit)
        if bs > best_score:
            best_score, best = bs, b[:]

    return sorted(set(best))
# EVOLVE-BLOCK-END
