# EVOLVE-BLOCK-START
"""Simplex lattice construction: A = {x in Z^d_{>=0}: sum x <= n} embedded in Z via base 2n+1."""
import math
import time
import numpy as np


def _points(d, n):
    # all d-tuples of nonneg ints with sum <= n
    pts = [()]
    for _ in range(d):
        new = []
        for p in pts:
            s = sum(p)
            for v in range(n - s + 1):
                new.append(p + (v,))
        pts = new
    return np.array(pts, dtype=np.int64).reshape(len(pts), d)


def _count(arr):
    arr = arr.ravel()
    arr.sort()
    return int(1 + np.count_nonzero(arr[1:] != arr[:-1]))


def _eval(a):
    a = np.asarray(a, dtype=np.int64)
    s = _count(a[:, None] + a[None, :])
    d = _count(a[:, None] - a[None, :])
    return math.log(d) / math.log(s) + (1 - 1 / len(a)) / 100


def solve():
    start = time.time()
    cands = []
    for d in range(2, 14):
        for n in range(1, 60):
            sz = math.comb(n + d, d)
            if sz > 4000:
                break
            if sz >= 150 and (2 * n + 1) ** d < 10 ** 14:
                cands.append((sz, d, n))
    cands.sort()
    best, best_score = [0, 1, 3], -1
    for sz, d, n in cands:
        if time.time() - start > 90:
            break
        pts = _points(d, n)
        B = 2 * n + 1
        w = np.array([B ** i for i in range(d)], dtype=np.int64)
        a = pts @ w
        sc = _eval(a)
        if sc > best_score:
            best_score, best = sc, [int(x) for x in a]
    return sorted(set(best))
# EVOLVE-BLOCK-END
