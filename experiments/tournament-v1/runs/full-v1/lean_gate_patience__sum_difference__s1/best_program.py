# EVOLVE-BLOCK-START
"""Simplex-lattice construction with base-tuning of the integer embedding."""
import math
import time
import numpy as np


def _simplex(k, n):
    pts = []

    def rec(prefix, remaining, dims):
        if dims == 0:
            pts.append(tuple(prefix))
            return
        for v in range(remaining + 1):
            prefix.append(v)
            rec(prefix, remaining - v, dims - 1)
            prefix.pop()

    rec([], n, k)
    return pts


def _embed(pts, B):
    vals = set()
    for p in pts:
        v = 0
        for x in reversed(p):
            v = v * B + x
        vals.add(v)
    return sorted(vals)


def _score_arr(arr):
    a = np.array(arr, dtype=np.int64)
    d = np.unique((a[:, None] - a[None, :]).ravel())
    s = np.unique((a[:, None] + a[None, :]).ravel())
    return math.log(len(d)) / math.log(len(s)) + (1 - 1 / len(a)) / 100


def _center(vals):
    shift = (max(vals) + min(vals)) // 2
    return [v - shift for v in vals]


def solve():
    start = time.time()
    best = [0, 1, 3]
    best_score = -1.0
    best_kn = None
    cands = []
    for k in range(1, 40):
        for n in range(1, 60):
            size = math.comb(n + k, k)
            if size < 4 or size > 4000:
                continue
            B = 2 * n + 1
            if n * B ** (k - 1) * 1.2 > 1.9e15:
                continue
            cands.append((size, k, n))
    cands.sort()
    for size, k, n in cands:
        if time.time() - start > 50:
            break
        pts = _simplex(k, n)
        vals = _center(_embed(pts, 2 * n + 1))
        if max(abs(v) for v in vals) > 10**15:
            continue
        try:
            sc = _score_arr(vals)
        except MemoryError:
            continue
        if sc > best_score:
            best_score = sc
            best = vals
            best_kn = (k, n)

    # base tuning: smaller bases cause collisions that may help the ratio
    if best_kn is not None:
        k, n = best_kn
        pts = _simplex(k, n)
        for B in range(2 * n, n, -1):
            if time.time() - start > 100:
                break
            vals = _embed(pts, B)
            if len(vals) < 4:
                continue
            vals = _center(vals)
            if max(abs(v) for v in vals) > 10**15:
                continue
            try:
                sc = _score_arr(vals)
            except MemoryError:
                continue
            if sc > best_score:
                best_score = sc
                best = vals
    return sorted(set(int(v) for v in best))
# EVOLVE-BLOCK-END
