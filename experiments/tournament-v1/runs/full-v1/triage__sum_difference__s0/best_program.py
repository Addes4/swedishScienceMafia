# EVOLVE-BLOCK-START
"""Simplex lattice with lossy / mixed-base / wrapped embeddings into Z, searched exactly."""
import math
import time
import random
import numpy as np


def _formula_counts(d, n):
    size = math.comb(n + d, d)
    sums = math.comb(2 * n + d, d)
    diffs = 0
    for p in range(0, d + 1):
        cp = math.comb(d, p) * math.comb(n, p)
        if cp == 0:
            continue
        for q in range(0, d - p + 1):
            diffs += cp * math.comb(d - p, q) * math.comb(n, q)
    return size, sums, diffs


def _score_counts(size, sums, diffs):
    if size < 2 or sums < 2:
        return 0.0
    return math.log(diffs) / math.log(sums) + (1 - 1 / size) / 100


def _simplex_points(d, n):
    pts = []

    def rec(prefix, remaining, k):
        if k == d:
            pts.append(tuple(prefix))
            return
        for v in range(remaining + 1):
            prefix.append(v)
            rec(prefix, remaining - v, k + 1)
            prefix.pop()

    rec([], n, 0)
    return np.array(pts, dtype=np.int64)


LIMIT = 10 ** 15


def _exact_score_arr(arr):
    arr = np.unique(np.asarray(arr, dtype=np.int64))
    N = arr.size
    if N < 2:
        return 0.0
    arr = arr - arr[0]
    R = int(arr[-1])
    B = max(1, min(N, 2000000 // N))
    if R < 300_000_000:
        sb = np.zeros(2 * R + 1, dtype=bool)
        db = np.zeros(R + 1, dtype=bool)
        for i in range(0, N, B):
            blk = arr[i:i + B]
            rest = arr[i:]
            s = blk[:, None] + rest[None, :]
            sb[s.ravel()] = True
            df = rest[None, :] - blk[:, None]
            db[np.abs(df).ravel()] = True
        ns = int(np.count_nonzero(sb))
        nd = 2 * int(np.count_nonzero(db[1:])) + 1
    else:
        ss = []
        ds = []
        for i in range(0, N, B):
            blk = arr[i:i + B]
            rest = arr[i:]
            ss.append(np.unique((blk[:, None] + rest[None, :]).ravel()))
            ds.append(np.unique(np.abs(rest[None, :] - blk[:, None]).ravel()))
        ns = np.unique(np.concatenate(ss)).size
        dd = np.unique(np.concatenate(ds))
        nd = 2 * int(np.count_nonzero(dd)) + 1
    if ns < 2:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / N) / 100


def solve():
    t0 = time.time()
    deadline = 100.0
    rng = random.Random(12345)

    def tleft():
        return deadline - (time.time() - t0)

    cands = []
    for d in range(1, 60):
        n = 1
        while True:
            size = math.comb(n + d, d)
            if size > 4000:
                break
            M = 2 * n + 1
            if n * M ** (d - 1) > LIMIT // 2:
                break
            sz, su, di = _formula_counts(d, n)
            cands.append((_score_counts(sz, su, di), d, n))
            n += 1
    cands.sort(reverse=True)

    # baseline: exact Freiman embedding with M = 2n+1
    sc0, d0, n0 = cands[0]
    P0 = _simplex_points(d0, n0)
    w0 = [(2 * n0 + 1) ** (d0 - 1 - i) for i in range(d0)]
    best_set = P0 @ np.array(w0, dtype=np.int64)
    best_score = sc0
    best_info = (d0, n0, w0)

    pcache = {}

    def getP(d, n):
        if (d, n) not in pcache:
            pcache[(d, n)] = _simplex_points(d, n)
        return pcache[(d, n)]

    def eval_w(d, n, w, mod=None):
        nonlocal best_set, best_score, best_info
        if any(x <= 0 for x in w) or n * max(w) > LIMIT:
            return -1.0
        P = getP(d, n)
        A = P @ np.array(w, dtype=np.int64)
        if mod is not None:
            A = A % mod
        A = np.unique(A)
        if A.size > 4000 or A.size < 2:
            return -1.0
        s = _exact_score_arr(A)
        if s > best_score:
            best_score = s
            best_set = A.copy()
            best_info = (d, n, list(w))
        return s

    top = [(d, n) for _, d, n in cands[:6]]

    # Phase 1: uniform lossy base M in [n+1, 4n]
    results = []
    for d, n in top:
        for M in range(n + 1, 4 * n + 1):
            if tleft() < 70:
                break
            w = [M ** (d - 1 - i) for i in range(d)]
            s = eval_w(d, n, w)
            results.append((s, d, n, w))

    # Phase 2: random mixed bases on top candidates
    results.sort(reverse=True, key=lambda r: r[0])
    seeds = [(d, n) for _, d, n, _ in results[:3]] or top[:2]
    while tleft() > 45:
        d, n = rng.choice(seeds)
        bases = [rng.randint(n + 1, 4 * n) for _ in range(d - 1)]
        w = [1]
        for b in bases:
            w.append(w[-1] * b)
        w = w[::-1]
        rng.shuffle(w)
        eval_w(d, n, w)

    # Phase 3: local search on weights of best
    d, n, w = best_info
    cur_w = list(w)
    cur_s = best_score
    while tleft() > 10:
        nw = list(cur_w)
        k = rng.randrange(d)
        r = rng.random()
        if r < 0.5:
            step = max(1, int(abs(nw[k]) * rng.choice([0.001, 0.01, 0.05])))
            nw[k] += rng.choice([-1, 1]) * rng.randint(1, max(1, step))
        elif r < 0.8:
            nw[k] = max(1, int(nw[k] * rng.uniform(0.8, 1.25)))
        else:
            j = rng.randrange(d)
            nw[k], nw[j] = nw[j], nw[k]
        s = eval_w(d, n, nw)
        if s >= cur_s:
            cur_s = s
            cur_w = nw

    # Phase 4: modulus wrap on best weights
    d, n, w = best_info
    mx = n * max(w)
    for frac in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        if tleft() < 2:
            break
        m = max(2, int(mx * frac))
        eval_w(d, n, w, mod=m)

    out = sorted(set(int(x) for x in best_set))
    if len(out) < 2:
        out = [0, 1, 3]
    return out
# EVOLVE-BLOCK-END
