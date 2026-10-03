# EVOLVE-BLOCK-START
"""Guillotine dynamic programming over discretised rectangles."""
import math
import time
import numpy as np


def _dp(G, n):
    F = np.zeros((G + 1, G + 1, n + 1))
    for a in range(1, G + 1):
        for b in range(a, G + 1):
            best = np.full(n + 1, float(a))
            best[0] = 0.0
            Ps = []
            Qs = []
            if a >= 2:
                xs = np.arange(1, a // 2 + 1)
                Ps.append(F[xs, b])
                Qs.append(F[a - xs, b])
            if b >= 2:
                ys = np.arange(1, b // 2 + 1)
                Ps.append(F[a, ys])
                Qs.append(F[a, b - ys])
            if Ps:
                P = np.concatenate(Ps, axis=0)
                Q = np.concatenate(Qs, axis=0)
                R = P + Q[:, 0:1]
                for j in range(1, n + 1):
                    cand = P[:, :n + 1 - j] + Q[:, j:j + 1]
                    np.maximum(R[:, j:], cand, out=R[:, j:])
                best = np.maximum(best, R.max(axis=0))
            F[a, b] = best
            F[b, a] = best
    return F


def _rebuild(F, a, b, m, x0, y0, out):
    if m <= 0 or a <= 0 or b <= 0:
        return
    target = F[a, b, m]
    if target <= 0:
        return
    s = min(a, b)
    if s == target:
        out.append((x0 + s / 2.0, y0 + s / 2.0, s))
        return
    for x in range(1, a):
        L = F[x, b, :m + 1]
        Rr = F[a - x, b, m::-1]
        tot = L + Rr
        k = int(np.argmax(tot))
        if tot[k] == target:
            _rebuild(F, x, b, k, x0, y0, out)
            _rebuild(F, a - x, b, m - k, x0 + x, y0, out)
            return
    for y in range(1, b):
        L = F[a, y, :m + 1]
        Rr = F[a, b - y, m::-1]
        tot = L + Rr
        k = int(np.argmax(tot))
        if tot[k] == target:
            _rebuild(F, a, y, k, x0, y0, out)
            _rebuild(F, a, b - y, m - k, x0, y0 + y, out)
            return
    out.append((x0 + s / 2.0, y0 + s / 2.0, s))


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    start = time.time()
    budget = 45.0
    s = math.isqrt(n)
    cands = set()
    for k in range(max(1, s - 2), s + 3):
        for L in range(1, 13):
            cands.add(k * L)
    for g in (12, 24, 36, 48, 60, 72, 84, 90, 96, 120, 144):
        cands.add(g)
    cands = sorted(c for c in cands if 2 <= c <= 160)
    # drop candidates dividing a larger candidate (dominated), keep a few small for timing
    cands_f = [c for c in cands if not any(d > c and d % c == 0 for d in cands)]
    cands = sorted(set(cands_f) | {12})

    best_val = -1.0
    best_sq = None
    unit_time = None
    for G in cands:
        elapsed = time.time() - start
        if unit_time is not None:
            pred = unit_time * (G ** 3) * (n + 1) ** 1.2
            if elapsed + pred > budget:
                continue
        t0 = time.time()
        F = _dp(G, n)
        dt = time.time() - t0
        u = dt / ((G ** 3) * (n + 1) ** 1.2)
        unit_time = u if unit_time is None else max(unit_time, u)
        val = F[G, G, n] / G
        if val > best_val + 1e-12:
            out = []
            _rebuild(F, G, G, n, 0, 0, out)
            best_val = val
            best_sq = [(cx / G, cy / G, sd / G) for cx, cy, sd in out]
    if best_sq is None:
        k = s
        side = 1.0 / k
        best_sq = [((i + 0.5) * side, (j + 0.5) * side, side) for i in range(k) for j in range(k)]
    res = []
    for cx, cy, sd in best_sq[:n]:
        cx = min(1.0, max(0.0, cx))
        cy = min(1.0, max(0.0, cy))
        sd = min(1.0, max(0.0, sd))
        res.append((cx, cy, 0.0, sd))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
