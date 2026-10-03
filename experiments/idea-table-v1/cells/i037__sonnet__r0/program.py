# EVOLVE-BLOCK-START
"""Guillotine DP over grid-aligned squares (multiple grid resolutions)."""
import math
import numpy as np


def _dp(m, n):
    C = min(n, m * m)
    F = {}
    KIND = {}
    POS = {}
    C1 = {}
    for w in range(1, m + 1):
        for h in range(1, m + 1):
            best = np.zeros(C + 1)
            best[1:] = min(w, h)
            kind = np.zeros(C + 1, dtype=int)
            pos = np.zeros(C + 1, dtype=int)
            c1s = np.zeros(C + 1, dtype=int)
            cuts = []
            for i in range(1, w // 2 + 1):
                cuts.append((1, i, F[(i, h)], F[(w - i, h)]))
            for j in range(1, h // 2 + 1):
                cuts.append((2, j, F[(w, j)], F[(w, h - j)]))
            for k, p, A, B in cuts:
                G = np.full(C + 1, -1.0)
                ac = np.zeros(C + 1, dtype=int)
                for c1 in range(C + 1):
                    cand = A[c1] + B[:C + 1 - c1]
                    sl = slice(c1, C + 1)
                    upd = cand > G[sl]
                    G[sl] = np.where(upd, cand, G[sl])
                    ac[sl] = np.where(upd, c1, ac[sl])
                upd = G > best + 1e-12
                best = np.where(upd, G, best)
                kind = np.where(upd, k, kind)
                pos = np.where(upd, p, pos)
                c1s = np.where(upd, ac, c1s)
            F[(w, h)] = best
            KIND[(w, h)] = kind
            POS[(w, h)] = pos
            C1[(w, h)] = c1s
    return C, F, KIND, POS, C1


def _build(m, C, KIND, POS, C1):
    out = []

    def rec(w, h, c, x, y):
        if c <= 0:
            return
        k = KIND[(w, h)][c]
        if k == 0:
            s = min(w, h)
            out.append(((x + s / 2.0) / m, (y + s / 2.0) / m, 0.0, s / m))
            return
        p = int(POS[(w, h)][c])
        c1 = int(C1[(w, h)][c])
        if k == 1:
            rec(p, h, c1, x, y)
            rec(w - p, h, c - c1, x + p, y)
        else:
            rec(w, p, c1, x, y)
            rec(w, h - p, c - c1, x, y + p)

    rec(m, m, C, 0, 0)
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    mmax = max(6, min(14, math.isqrt(n) + 4))
    best_val = -1.0
    best_sq = None
    for m in range(1, mmax + 1):
        C, F, KIND, POS, C1 = _dp(m, n)
        val = F[(m, m)][C] / m
        if val > best_val + 1e-12:
            sq = _build(m, C, KIND, POS, C1)
            best_val = val
            best_sq = sq
    sq = list(best_sq)
    sq = [(min(1.0, max(0.0, a)), min(1.0, max(0.0, b)), 0.0, min(1.0, max(0.0, s)))
          for a, b, _, s in sq]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq[:n]
# EVOLVE-BLOCK-END
