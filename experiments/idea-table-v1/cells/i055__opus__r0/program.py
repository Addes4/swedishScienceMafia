# EVOLVE-BLOCK-START
"""Guillotine dynamic programming on integer D x D boards.

For each board resolution D (chosen so that small denominators like 2,3,4,6,8,...
divide D), compute F[w,h,m] = maximum sum of sides (in grid units) of at most m
axis-parallel squares packed in a w x h rectangle using guillotine cuts.
Leaf: one square of side min(w,h). Internal: vertical/horizontal cut with a
max-plus convolution splitting the square budget. Best D wins, layout is
reconstructed exactly from the integer table."""
import math
import time
import numpy as np


def _dp(D, n):
    F = np.zeros((D + 1, D + 1, n + 1), dtype=np.int64)
    for w in range(1, D + 1):
        for h in range(1, D + 1):
            if n >= 1:
                F[w, h, 1:] = min(w, h)
    for w in range(1, D + 1):
        for h in range(w, D + 1):
            As = []
            Bs = []
            if w // 2 >= 1:
                a = np.arange(1, w // 2 + 1)
                As.append(F[a, h])
                Bs.append(F[w - a, h])
            if h // 2 >= 1:
                b = np.arange(1, h // 2 + 1)
                As.append(F[w, b])
                Bs.append(F[w, h - b])
            if not As:
                continue
            A = np.concatenate(As, axis=0)
            B = np.concatenate(Bs, axis=0)
            res = A + B[:, 0:1]
            for j in range(1, n + 1):
                np.maximum(res[:, j:], A[:, :n + 1 - j] + B[:, j:j + 1], out=res[:, j:])
            best = res.max(axis=0)
            row = np.maximum(F[w, h], best)
            F[w, h] = row
            F[h, w] = row
    return F


def _reconstruct(F, x0, y0, w, h, m, out):
    # out collects (x, y, side) in grid units (lower-left corner)
    while m > 0:
        target = F[w, h, m]
        if F[w, h, m - 1] == target:
            out.append(None)
            m -= 1
            continue
        if target == min(w, h):
            out.append((x0, y0, min(w, h)))
            for _ in range(m - 1):
                out.append(None)
            return
        # vertical cuts
        for a in range(1, w):
            fa = F[a, h]
            fb = F[w - a, h]
            for i in range(0, m + 1):
                if fa[i] + fb[m - i] == target:
                    _reconstruct(F, x0, y0, a, h, i, out)
                    _reconstruct(F, x0 + a, y0, w - a, h, m - i, out)
                    return
        for b in range(1, h):
            fa = F[w, b]
            fb = F[w, h - b]
            for i in range(0, m + 1):
                if fa[i] + fb[m - i] == target:
                    _reconstruct(F, x0, y0, w, b, i, out)
                    _reconstruct(F, x0, y0 + b, w, h - b, m - i, out)
                    return
        # should not happen; fallback
        out.append((x0, y0, min(w, h)))
        for _ in range(m - 1):
            out.append(None)
        return
    return


def _ndiv(d):
    return sum(1 for i in range(1, d + 1) if d % i == 0)


def solve(n):
    t0 = time.time()
    budget = 25.0
    if n <= 0:
        return []
    kmin = max(1, math.isqrt(n))
    cands = list(range(max(1, kmin), 121))
    cands.sort(key=lambda d: (-_ndiv(d), d))
    best_val = -1.0
    best_D = None
    best_F = None
    last_cost_per = None
    for D in cands:
        elapsed = time.time() - t0
        if elapsed > budget:
            break
        if last_cost_per is not None:
            est = last_cost_per * D * D * (n + 1)
            if elapsed + est > budget:
                continue
        ts = time.time()
        F = _dp(D, n)
        dt = time.time() - ts
        last_cost_per = max(dt / (D * D * (n + 1)), 1e-9) if last_cost_per is None else max(last_cost_per, dt / (D * D * (n + 1)))
        val = F[D, D, n] / D
        if val > best_val + 1e-12:
            best_val = val
            best_D = D
            best_F = F
    if best_F is None:
        k = math.isqrt(n)
        side = 1.0 / k
        sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        sq += [(0.0, 0.0, 0.0, 0.0)] * (n - len(sq))
        return sq[:n]
    out = []
    _reconstruct(best_F, 0, 0, best_D, best_D, n, out)
    D = float(best_D)
    shrink = 1.0 - 1e-9
    squares = []
    for item in out:
        if item is None:
            squares.append((0.0, 0.0, 0.0, 0.0))
        else:
            x, y, s = item
            cx = (x + s / 2.0) / D
            cy = (y + s / 2.0) / D
            squares.append((min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0), 0.0, (s / D) * shrink))
    while len(squares) < n:
        squares.append((0.0, 0.0, 0.0, 0.0))
    return squares[:n]
# EVOLVE-BLOCK-END
