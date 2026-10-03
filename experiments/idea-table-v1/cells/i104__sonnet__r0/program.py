# EVOLVE-BLOCK-START
import math
import time
import random
import numpy as np


def _dp_structures(n, deadline):
    F = [0.0] * (n + 1)
    cfg = [None] * (n + 1)
    if n >= 1:
        F[1] = 1.0
        cfg[1] = ('single',)
    for c in range(2, n + 1):
        F[c] = F[c - 1]
        cfg[c] = ('pad',)
        if time.time() > deadline:
            continue
        lo = max(2, math.isqrt(c - 1) + 1 - 1)
        hi = math.isqrt(c) + 2
        if c > 120:
            lo = max(2, math.isqrt(c))
            hi = lo + 1
        for k in range(lo, hi + 1):
            cells = k * k
            W = c
            v = np.array([F[x] / k if x < c else -1e18 for x in range(W + 1)])
            dps = [np.zeros(W + 1)]
            chs = [None]
            for t in range(1, cells + 1):
                prev = dps[-1]
                new = prev.copy()  # c'=0
                ch = np.zeros(W + 1, dtype=np.int32)
                for cp in range(1, W):
                    cand = prev[:W + 1 - cp] + v[cp]
                    seg = new[cp:]
                    better = cand > seg + 1e-12
                    if better.any():
                        seg[better] = cand[better]
                        ch[cp:][better] = cp
                dps.append(new)
                chs.append(ch)
            # options: m = 0 or 2..k-1
            opts = [(dps[cells][c], 0, cells, c)]
            for m in range(2, k):
                t = cells - m * m
                if c - 1 >= 0:
                    opts.append((m / k + dps[t][c - 1], m, t, c - 1))
            val, m, t, w = max(opts, key=lambda o: o[0])
            if val > F[c] + 1e-12:
                counts = []
                for tt in range(t, 0, -1):
                    cp = int(chs[tt][w])
                    counts.append(cp)
                    w -= cp
                counts.reverse()
                F[c] = val
                cfg[c] = ('grid', k, m, counts)
    return F, cfg


def _build(c, cfg, memo):
    if c in memo:
        return memo[c]
    if c <= 0:
        res = []
    else:
        cf = cfg[c]
        if cf[0] == 'single':
            res = [(0.5, 0.5, 0.0, 1.0)]
        elif cf[0] == 'pad':
            res = _build(c - 1, cfg, memo)
        else:
            _, k, m, counts = cf
            res = []
            if m:
                s = m / k
                res.append((s / 2, s / 2, 0.0, s))
            idx = 0
            for i in range(k):
                for j in range(k):
                    if i < m and j < m:
                        continue
                    cp = counts[idx]
                    idx += 1
                    if cp <= 0:
                        continue
                    for (x, y, a, s) in _build(cp, cfg, memo):
                        res.append(((i + x) / k, (j + y) / k, 0.0, s / k))
    memo[c] = res
    return res


def _skyline(sizes):
    eps = 1e-9
    sky = [(0.0, 1.0, 0.0)]
    placed = []
    for s in sizes:
        bestY = None
        bestX = None
        for (x, w, h) in sky:
            if x + s > 1 + eps:
                break
            y = 0.0
            for (x2, w2, h2) in sky:
                if x2 >= x + s - eps:
                    break
                if x2 + w2 <= x + eps:
                    continue
                if h2 > y:
                    y = h2
            if y + s <= 1 + eps and (bestY is None or y < bestY - 1e-12):
                bestY, bestX = y, x
        if bestY is None:
            continue
        x, y = bestX, bestY
        new = []
        for (x2, w2, h2) in sky:
            e2 = x2 + w2
            if e2 <= x + eps or x2 >= x + s - eps:
                new.append((x2, w2, h2))
                continue
            if x2 < x - eps:
                new.append((x2, x - x2, h2))
            if e2 > x + s + eps:
                new.append((x + s, e2 - x - s, h2))
        new.append((x, s, y + s))
        new.sort()
        sky = new
        placed.append((x + s / 2, y + s / 2, 0.0, s))
    return placed


def solve(n):
    t0 = time.time()
    F, cfg = _dp_structures(n, t0 + 30)
    base = _build(n, cfg, {})
    base_val = sum(q[3] for q in base)
    best = base
    best_val = base_val
    # --- cross-entropy refinement over multisets of sides 1/d ---
    D = max(2, int(math.ceil(3 * math.sqrt(n))))
    lam = np.full(D + 1, 0.05)
    lam[0] = 0.0
    for q in base:
        if q[3] > 1e-9:
            d = min(D, max(1, int(round(1.0 / q[3]))))
            lam[d] += 1.0
    rng = np.random.default_rng(1)
    cem_deadline = min(t0 + 14, t0 + 55)
    seen_best = None
    N = 150
    while time.time() < cem_deadline:
        samples = []
        for _ in range(N):
            cnt = rng.poisson(lam)
            cnt[0] = 0
            sizes = []
            for d in range(1, D + 1):
                if cnt[d]:
                    sizes += [1.0 / d] * int(cnt[d])
            sizes.sort(reverse=True)
            sizes = sizes[:n]
            placed = _skyline(sizes)
            val = sum(p[3] for p in placed)
            samples.append((val, cnt, placed))
            if time.time() > cem_deadline:
                break
        samples.sort(key=lambda t: -t[0])
        if samples[0][0] > best_val + 1e-9 and len(samples[0][2]) <= n:
            best_val = samples[0][0]
            best = [(x, y, a, s * (1 - 1e-9)) for (x, y, a, s) in samples[0][2]]
        ne = max(2, len(samples) // 10)
        elite = np.mean([s[1] for s in samples[:ne]], axis=0)
        lam = 0.6 * elite + 0.4 * lam + 0.01
        lam[0] = 0.0
    out = list(best)[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    res = []
    for (x, y, a, s) in out:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return res
# EVOLVE-BLOCK-END
