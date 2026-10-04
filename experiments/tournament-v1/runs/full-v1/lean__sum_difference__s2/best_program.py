# EVOLVE-BLOCK-START
import math
import random
import time
from math import comb, factorial
import numpy as np


def _simplex_stats(d, n):
    size = comb(n + d, d)
    sums = comb(2 * n + d, d)
    diffs = 0
    for i in range(0, min(d, n) + 1):
        for j in range(0, min(d - i, n) + 1):
            m = factorial(d) // (factorial(i) * factorial(j) * factorial(d - i - j))
            diffs += m * comb(n, i) * comb(n, j)
    return size, sums, diffs


def _points(d, n):
    res = []

    def rec(pos, rem, cur):
        if pos == d:
            res.append(tuple(cur))
            return
        for x in range(rem + 1):
            cur.append(x)
            rec(pos + 1, rem - x, cur)
            cur.pop()

    rec(0, n, [])
    return np.array(res, dtype=np.int64)


def _build(P, d, n):
    k = len(P)
    base = np.array([(2 * n + 1) ** i for i in range(d)], dtype=np.int64)
    a = P @ base
    i0, i1 = np.triu_indices(k)
    codes = a[i0] + a[i1]
    _, idx = np.unique(codes, return_index=True)
    Sv = np.ascontiguousarray(P[i0[idx]] + P[i1[idx]])
    del i0, i1, codes, idx
    j0, j1 = np.triu_indices(k, 1)
    codes = np.abs(a[j0] - a[j1])
    _, idx = np.unique(codes, return_index=True)
    Dv = np.ascontiguousarray(P[j0[idx]] - P[j1[idx]])
    del j0, j1, codes, idx
    return Sv, Dv


def _fast_eval(P, Sv, Dv, c):
    s = np.unique(Sv @ c).size
    h = np.abs(Dv @ c)
    u = np.unique(h)
    dd = 2 * int((u > 0).sum()) + 1
    k = np.unique(P @ c).size
    if s < 2 or k < 2:
        return 0.0
    return math.log(dd) / math.log(s) + (1 - 1 / k) / 100


def solve():
    t0 = time.time()
    deadline = t0 + 98
    cands = []
    for d in range(1, 40):
        for n in range(1, 60):
            size = comb(n + d, d)
            if size > 4000:
                break
            if (2 * n + 1) ** d > 5e14:
                break
            sz, su, di = _simplex_stats(d, n)
            s = math.log(di) / math.log(su) + (1 - 1 / sz) / 100
            cands.append((s, d, n))
    cands.sort(reverse=True)
    top = cands[:2]

    best = None  # (score, P, Sv, Dv, c, n)
    for ci, (fs, d, n) in enumerate(top):
        if ci > 0 and time.time() > t0 + 35:
            break
        P = _points(d, n)
        Sv, Dv = _build(P, d, n)
        c0 = np.array([(2 * n + 1) ** i for i in range(d)], dtype=np.int64)
        s0 = _fast_eval(P, Sv, Dv, c0)
        loc = (s0, P, Sv, Dv, c0, n)
        tb = time.time()
        for B in range(2 * n, max(1, n - 1), -1):
            if time.time() > t0 + 30 + 20 * ci:
                break
            if n * B ** (d - 1) * 2 > 5e14:
                continue
            c = np.array([B ** i for i in range(d)], dtype=np.int64)
            s = _fast_eval(P, Sv, Dv, c)
            if s > loc[0] + 1e-12:
                loc = (s, P, Sv, Dv, c, n)
        if best is None or loc[0] > best[0]:
            best = loc
        else:
            del Sv, Dv

    cur_s, P, Sv, Dv, c, n_max = best
    best_s = cur_s
    best_c = c.copy()
    c = c.copy()
    last = 1.0
    while time.time() + last * 1.5 < deadline:
        ts = time.time()
        c2 = c.copy()
        nm = 1 if random.random() < 0.7 else 2
        for _ in range(nm):
            i = random.randrange(len(c2))
            r = random.random()
            if r < 0.4:
                c2[i] += random.choice([-1, 1]) * random.randint(1, max(1, int(c2[i]) // 8))
            elif r < 0.8:
                c2[i] += random.choice([-1, 1])
            else:
                j = random.randrange(len(c2))
                c2[i], c2[j] = c2[j], c2[i]
        if c2.min() < 1 or int(c2.max()) * n_max * 2 > 5e14:
            continue
        s = _fast_eval(P, Sv, Dv, c2)
        last = time.time() - ts
        if s >= cur_s:
            if s > best_s + 1e-12:
                best_s = s
                best_c = c2.copy()
            cur_s = s
            c = c2

    res = np.unique(P @ best_c)
    res = res - res.min()
    return [int(x) for x in res]
# EVOLVE-BLOCK-END
