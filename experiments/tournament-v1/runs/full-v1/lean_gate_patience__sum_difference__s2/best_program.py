# EVOLVE-BLOCK-START
"""Simplex construction A = {x in N^d : sum x <= n} embedded by integer weights.
First scan bases B, then hill-climb on per-coordinate weights with exact evaluation."""
import math
import time
import random
import numpy as np


def _counts(d, n):
    size = math.comb(n + d, d)
    sums = math.comb(2 * n + d, d)
    diffs = 0
    for k in range(d + 1):
        for j in range(d - k + 1):
            diffs += math.comb(d, k) * math.comb(d - k, j) * math.comb(n, k) * math.comb(n, j)
    return size, sums, diffs


def _coords(d, n):
    res = []

    def rec(i, remaining, cur):
        if i == d:
            res.append(tuple(cur))
            return
        for x in range(remaining + 1):
            cur.append(x)
            rec(i + 1, remaining - x, cur)
            cur.pop()

    rec(0, n, [])
    return np.array(res, dtype=np.int64)


def _eval(arr):
    """arr: sorted unique int64 array. Return (|A+A|, |A-A|)."""
    m = len(arr)
    bs = 256
    su = []
    du = []
    for s in range(0, m, bs):
        e = min(m, s + bs)
        blk = arr[s:e, None] + arr[None, s:]
        su.append(np.unique(blk))
        dd = arr[s:e, None] - arr[None, :e]
        du.append(np.unique(dd[dd > 0]))
    S = np.unique(np.concatenate(su)).size
    D = 2 * np.unique(np.concatenate(du)).size + 1
    return S, D


def _score_w(X, w):
    vals = X @ np.array(w, dtype=np.int64)
    arr = np.unique(vals)
    if len(arr) != len(vals):
        return None, None
    S, D = _eval(arr)
    if S <= 1 or D <= 1:
        return None, None
    return math.log(D) / math.log(S) + (1 - 1 / len(arr)) / 100, arr


def solve():
    t0 = time.time()
    cands = []
    for d in range(1, 30):
        n = 1
        while True:
            size = math.comb(n + d, d)
            if size > 4000 or n * (2 * n + 1) ** (d - 1) > 9e14:
                break
            if size >= 2:
                sz, sums, diffs = _counts(d, n)
                s = math.log(diffs) / math.log(sums) + (1 - 1 / sz) / 100
                cands.append((s, d, n))
            n += 1
    cands.sort(reverse=True)
    best_s, d0, n0 = cands[0]
    X0 = _coords(d0, n0)
    w0 = [(2 * n0 + 1) ** i for i in range(d0)]
    best_set = sorted(int(v) for v in X0 @ np.array(w0, dtype=np.int64))
    best_info = (d0, n0, X0, w0)

    scan_deadline = t0 + 40
    for s0, d, n in cands[:3]:
        if n < 2:
            continue
        X = None
        for B in range(2 * n, n, -1):
            if time.time() > scan_deadline:
                break
            if n * B ** (d - 1) * 2 > 9e14:
                continue
            if X is None:
                X = _coords(d, n)
            w = [B ** i for i in range(d)]
            t1 = time.time()
            sc, arr = _score_w(X, w)
            if sc is not None and sc > best_s:
                best_s = sc
                best_set = [int(v) for v in arr]
                best_info = (d, n, X, w)
            if time.time() + 2 * (time.time() - t1) > scan_deadline:
                break

    # hill-climb on weights
    deadline = t0 + 100
    d, n, X, w = best_info
    w = list(w)
    rng = random.Random(12345)
    cur_s = best_s
    last = 1.0
    maxcoord = n
    while d >= 2:
        now = time.time()
        if now + 1.5 * last > deadline:
            break
        nw = list(w)
        k = 1 if rng.random() < 0.7 else 2
        for _ in range(k):
            i = rng.randrange(d)
            scale = 10 ** (-rng.uniform(0.3, 3.0))
            r = max(1, int(nw[i] * scale))
            delta = rng.randint(1, r) * rng.choice((-1, 1))
            nw[i] = nw[i] + delta
        if min(nw) < 1 or maxcoord * sum(nw) > 9e14:
            continue
        t1 = time.time()
        sc, arr = _score_w(X, nw)
        last = time.time() - t1
        if sc is not None and sc >= cur_s:
            cur_s = sc
            w = nw
            if sc > best_s:
                best_s = sc
                best_set = [int(v) for v in arr]
    return best_set
# EVOLVE-BLOCK-END
