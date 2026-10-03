# EVOLVE-BLOCK-START
"""Guillotine-cut DP on an integer lattice (generalised column strips)."""
import math
import time
import numpy as np


def _build(g, n):
    dp = {}
    for a in range(1, g + 1):
        for b in range(1, a + 1):
            base = np.full(n + 1, b, dtype=np.int64)
            base[0] = 0
            cand = base.copy()
            # cuts along a
            for a1 in range(1, a // 2 + 1):
                k1 = (a1, b) if a1 >= b else (b, a1)
                a2 = a - a1
                k2 = (a2, b) if a2 >= b else (b, a2)
                f1 = dp[k1]
                f2 = dp[k2]
                for m1 in range(n + 1):
                    np.maximum(cand[m1:], f1[m1] + f2[:n + 1 - m1], out=cand[m1:])
            for b1 in range(1, b // 2 + 1):
                b2 = b - b1
                f1 = dp[(a, b1)] if a >= b1 else dp[(b1, a)]
                f2 = dp[(a, b2)] if a >= b2 else dp[(b2, a)]
                for m1 in range(n + 1):
                    np.maximum(cand[m1:], f1[m1] + f2[:n + 1 - m1], out=cand[m1:])
            dp[(a, b)] = cand
    return dp


def _get(dp, a, b):
    return dp[(a, b)] if a >= b else dp[(b, a)]


def _place(dp, g, x0, y0, w, h, m, out):
    if m <= 0 or w <= 0 or h <= 0:
        return
    target = int(_get(dp, w, h)[m])
    if target == 0:
        return
    s = min(w, h)
    if target == s:
        out.append(((x0 + s / 2.0) / g, (y0 + s / 2.0) / g, 0.0, s / float(g)))
        return
    for w1 in range(1, w):
        f1 = _get(dp, w1, h)
        f2 = _get(dp, w - w1, h)
        for m1 in range(m + 1):
            if int(f1[m1] + f2[m - m1]) == target:
                _place(dp, g, x0, y0, w1, h, m1, out)
                _place(dp, g, x0 + w1, y0, w - w1, h, m - m1, out)
                return
    for h1 in range(1, h):
        f1 = _get(dp, w, h1)
        f2 = _get(dp, w, h - h1)
        for m1 in range(m + 1):
            if int(f1[m1] + f2[m - m1]) == target:
                _place(dp, g, x0, y0, w, h1, m1, out)
                _place(dp, g, x0, y0 + h1, w, h - h1, m - m1, out)
                return


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    budget = 30.0
    best_val = -1.0
    best_g = None
    last = 0.0
    g = 1
    while g <= 60:
        if g > 1:
            est = last * ((g / (g - 1.0)) ** 3.2)
            if time.time() - t0 + est > budget:
                break
        ts = time.time()
        dp = _build(g, n)
        last = time.time() - ts
        val = int(dp[(g, g)][n]) / float(g)
        if val > best_val + 1e-12:
            best_val = val
            best_g = g
            best_dp = dp
        g += 1
    out = []
    if best_g is not None:
        _place(best_dp, best_g, 0, 0, best_g, best_g, n, out)
    if len(out) < n:
        out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    out = out[:n]
    # safety clamp
    res = []
    for (x, y, a, s) in out:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return res
# EVOLVE-BLOCK-END
