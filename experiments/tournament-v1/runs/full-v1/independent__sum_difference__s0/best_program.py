import math
import time
import random
import numpy as np


def _count(d, n, m):
    # number of vectors in Z^d, coords in 0..m, sum <= n
    dp = [1] + [0] * n  # dp[s] = ways with sum exactly s
    for _ in range(d):
        nd = [0] * (n + 1)
        for s in range(n + 1):
            if dp[s]:
                for v in range(0, min(m, n - s) + 1):
                    nd[s + v] += dp[s]
        dp = nd
    return sum(dp)


def _gen(d, n, m):
    pts = np.zeros((1, 0), dtype=np.int64)
    sums = np.zeros(1, dtype=np.int64)
    for _ in range(d):
        parts = []
        sp = []
        for v in range(0, m + 1):
            mask = sums + v <= n
            if not mask.any():
                break
            p = pts[mask]
            parts.append(np.hstack([p, np.full((p.shape[0], 1), v, dtype=np.int64)]))
            sp.append(sums[mask] + v)
        pts = np.vstack(parts)
        sums = np.concatenate(sp)
    return pts


def _embed(pts, n):
    B = 2 * n + 1
    d = pts.shape[1]
    w = np.array([B ** i for i in range(d)], dtype=np.int64)
    return pts @ w


def _eval(vals):
    a = np.unique(vals)
    k = len(a)
    s = np.unique((a[:, None] + a[None, :]).ravel())
    df = np.unique((a[:, None] - a[None, :]).ravel())
    return math.log(len(df)) / math.log(len(s)) + (1 - 1 / k) / 100, a


def solve():
    t0 = time.time()
    limit = 85
    cands = []
    for d in range(2, 16):
        for n in range(1, 25):
            B = 2 * n + 1
            if B ** d * n > 5e14:
                continue
            for m in range(1, n + 1):
                c = _count(d, n, m)
                if 8 <= c <= 4000:
                    cands.append((d, n, m, c))
    random.seed(1)
    random.shuffle(cands)
    # always include a few large ones early
    cands.sort(key=lambda t: 0 if t[3] > 300 else 1)
    big = [c for c in cands if c[3] > 300]
    small = [c for c in cands if c[3] <= 300]
    random.shuffle(big)
    order = big + small
    best = [0, 1, 3, 7]
    best_s = -1
    try:
        best_s, _a = _eval(np.array(best, dtype=np.int64))
    except Exception:
        pass
    for d, n, m, c in order:
        if time.time() - t0 > limit:
            break
        if c > 2500 and time.time() - t0 > limit - 15:
            continue
        pts = _gen(d, n, m)
        vals = _embed(pts, n)
        vals = vals - vals.min()
        try:
            s, a = _eval(vals)
        except Exception:
            continue
        if s > best_s:
            best_s = s
            best = [int(x) for x in a]
    return best
