# EVOLVE-BLOCK-START
"""Guillotine DP over integer-grid packings of squares (sizes a/k), best k chosen."""
import math
import time
import numpy as np


def _dp(k, n):
    NEG = 0.0
    F = [[None] * (k + 1) for _ in range(k + 1)]
    CH = [[None] * (k + 1) for _ in range(k + 1)]
    for w in range(1, k + 1):
        for h in range(1, k + 1):
            best = np.zeros(n + 1)
            typ = np.zeros(n + 1, dtype=np.int8)
            pos = np.zeros(n + 1, dtype=np.int32)
            m1s = np.zeros(n + 1, dtype=np.int32)
            if w == h:
                best[1:] = w
                typ[1:] = 1
            for t, lim in ((2, w // 2), (3, h // 2)):
                for c in range(1, lim + 1):
                    if t == 2:
                        A = F[c][h]
                        B = F[w - c][h]
                    else:
                        A = F[w][c]
                        B = F[w][h - c]
                    for a in range(n + 1):
                        cand = A[a] + B[:n + 1 - a]
                        seg = best[a:]
                        mask = cand > seg + 1e-12
                        if mask.any():
                            seg[mask] = cand[mask]
                            typ[a:][mask] = t
                            pos[a:][mask] = c
                            m1s[a:][mask] = a
            F[w][h] = best
            CH[w][h] = (typ, pos, m1s)
    return F, CH


def _build(k, n, CH):
    out = []
    stack = [(0, 0, k, k, n)]
    while stack:
        x, y, w, h, m = stack.pop()
        if m <= 0:
            continue
        typ, pos, m1s = CH[w][h]
        t = typ[m]
        if t == 0:
            continue
        if t == 1:
            out.append(((x + w / 2.0) / k, (y + h / 2.0) / k, 0.0, w / k))
        elif t == 2:
            c = int(pos[m]); a = int(m1s[m])
            stack.append((x, y, c, h, a))
            stack.append((x + c, y, w - c, h, m - a))
        else:
            c = int(pos[m]); a = int(m1s[m])
            stack.append((x, y, w, c, a))
            stack.append((x, y + c, w, h - c, m - a))
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    k0 = max(1, math.isqrt(n))
    # baseline grid
    side = 1.0 / k0
    best_sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
               for i in range(k0) for j in range(k0)][:n]
    best_val = sum(s[3] for s in best_sq)
    ks = list(range(k0, 13))
    for k in ks:
        if time.time() - t0 > 35:
            break
        if k ** 3 * n > 6e6:
            continue
        try:
            F, CH = _dp(k, n)
        except Exception:
            continue
        val = F[k][k][n] / k
        if val > best_val + 1e-12:
            sq = _build(k, n, CH)
            v = sum(s[3] for s in sq)
            if v > best_val + 1e-12:
                best_val = v
                best_sq = sq
    res = []
    for (cx, cy, a, s) in best_sq:
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), a, min(1.0, max(0.0, s))))
    res = res[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res
# EVOLVE-BLOCK-END
