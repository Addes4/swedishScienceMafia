# EVOLVE-BLOCK-START
"""Guillotine DP on an integer L x L board: f[w][h][m] = best sum of sides using at most m
axis-aligned squares inside a w x h rectangle. Try several L, keep the best."""
import math
import time

import numpy as np


def _dp(L, n):
    F = {}
    T = {}
    for w in range(1, L + 1):
        for h in range(1, L + 1):
            best = np.full(n + 1, float(min(w, h)))
            best[0] = 0.0
            typ = np.zeros(n + 1, dtype=np.int8)
            cut = np.zeros(n + 1, dtype=np.int16)
            sp = np.zeros(n + 1, dtype=np.int16)
            for t, size in ((1, w), (2, h)):
                for x in range(1, size // 2 + 1):
                    if t == 1:
                        A = F[(x, h)]
                        B = F[(w - x, h)]
                    else:
                        A = F[(w, x)]
                        B = F[(w, h - x)]
                    for m1 in range(0, n):
                        cand = A[m1] + B[: n + 1 - m1]
                        seg = best[m1:]
                        mask = cand > seg + 1e-9
                        if mask.any():
                            idx = np.nonzero(mask)[0] + m1
                            best[idx] = cand[mask]
                            typ[idx] = t
                            cut[idx] = x
                            sp[idx] = m1
            F[(w, h)] = best
            T[(w, h)] = (typ, cut, sp)
    return F, T


def _build(T, w, h, m, x0, y0, out):
    if m <= 0:
        return
    typ, cut, sp = T[(w, h)]
    t = int(typ[m])
    if t == 0:
        s = min(w, h)
        out.append((x0, y0, s))
        return
    x = int(cut[m])
    m1 = int(sp[m])
    if t == 1:
        _build(T, x, h, m1, x0, y0, out)
        _build(T, w - x, h, m - m1, x0 + x, y0, out)
    else:
        _build(T, w, x, m1, x0, y0, out)
        _build(T, w, h - x, m - m1, x0, y0 + x, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    k = math.isqrt(n)
    side = 1.0 / k
    best_val = k * k * side
    best_sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
               for i in range(k) for j in range(k)][:n]

    for L in range(1, 15):
        if time.time() - t0 > 40:
            break
        F, T = _dp(L, n)
        val = F[(L, L)][n] / L
        if val > best_val + 1e-9:
            out = []
            _build(T, L, L, n, 0, 0, out)
            sq = [((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / L) for x, y, s in out]
            if len(sq) <= n:
                best_val = val
                best_sq = sq

    squares = list(best_sq)
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END
