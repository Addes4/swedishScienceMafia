# EVOLVE-BLOCK-START
import math
import random
import time

import numpy as np


def _score(a):
    a = np.array(sorted(set(a)), dtype=np.int64)
    if len(a) < 2:
        return 0.0
    d = np.unique((a[:, None] - a[None, :]).ravel()).size
    s = np.unique((a[:, None] + a[None, :]).ravel()).size
    return math.log(d) / math.log(s) + (1 - 1 / len(a)) / 100


def _sizes(d, k):
    nA = math.comb(k + d, d)
    nS = math.comb(2 * k + d, d)
    nD = 0
    fd = math.factorial(d)
    for p in range(0, min(d, k) + 1):
        for n in range(0, min(d - p, k) + 1):
            mult = fd // (math.factorial(p) * math.factorial(n) * math.factorial(d - p - n))
            nD += mult * math.comb(k, p) * math.comb(k, n)
    return nA, nS, nD


def _simplex_points(d, k):
    pts = []

    def rec(prefix, rem, left):
        if left == 0:
            pts.append(tuple(prefix))
            return
        for v in range(rem + 1):
            prefix.append(v)
            rec(prefix, rem - v, left - 1)
            prefix.pop()

    rec([], k, d)
    return pts


def _build(d, k, m):
    M = 2 * k + 1
    pts = _simplex_points(d, k)
    base_vals = [sum(x * M ** i for i, x in enumerate(p)) for p in pts]
    vals = [0]
    shift = M ** d
    for j in range(m):
        mul = shift ** j
        vals = [v + b * mul for v in vals for b in base_vals]
    return vals


def solve():
    LIMIT_N = 4000
    LIMIT_V = 10 ** 15
    best = None  # (score, d, k, m)
    for d in range(1, 60):
        for k in range(1, 60):
            M = 2 * k + 1
            if M ** d > LIMIT_V:
                break
            nA, nS, nD = _sizes(d, k)
            if nA > LIMIT_N:
                break
            if nA < 2:
                continue
            ratio = math.log(nD) / math.log(nS)
            m = 1
            while True:
                if nA ** m > LIMIT_N or M ** (d * m) > LIMIT_V:
                    break
                sc = ratio + (1 - 1 / nA ** m) / 100
                if best is None or sc > best[0]:
                    best = (sc, d, k, m)
                m += 1
    fallback = [7, 15, 18, 22, -3, -2]
    try:
        _, d, k, m = best
        A = sorted(set(_build(d, k, m)))
        # center values to reduce magnitude
        if A:
            off = (A[0] + A[-1]) // 2
            A = [x - off for x in A]
        if len(A) <= LIMIT_N and max(abs(x) for x in A) <= LIMIT_V:
            if _score(A) >= _score(fallback):
                return A
    except Exception:
        pass
    return sorted(set(fallback))
# EVOLVE-BLOCK-END
