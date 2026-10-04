# EVOLVE-BLOCK-START
"""Guillotine DP over integer rectangles for several grid denominators D."""
import time
import numpy as np


def _run(D, n, I_idx, NEGM, ar):
    N = n + 1
    val = {}
    typ = {}   # 0 single, 1 vcut, 2 hcut
    cut = {}
    mi = {}
    for p in range(1, D + 1):
        for q in range(1, D + 1):
            v = np.full(N, min(p, q), dtype=np.int64)
            v[0] = 0
            t = np.zeros(N, dtype=np.int8)
            c = np.zeros(N, dtype=np.int16)
            mm = np.zeros(N, dtype=np.int32)
            cands = []
            for x in range(1, p // 2 + 1):
                cands.append((1, x, (x, q), (p - x, q)))
            for y in range(1, q // 2 + 1):
                cands.append((2, y, (p, y), (p, q - y)))
            for (ty, pos, k1, k2) in cands:
                f1 = val[k1]
                f2 = val[k2]
                V = f1[None, :] + f2[I_idx] + NEGM
                arg = V.argmax(1)
                best = V[ar, arg]
                better = best > v
                if better.any():
                    v = np.where(better, best, v)
                    t = np.where(better, ty, t).astype(np.int8)
                    c = np.where(better, pos, c).astype(np.int16)
                    mm = np.where(better, arg, mm).astype(np.int32)
            val[(p, q)] = v
            typ[(p, q)] = t
            cut[(p, q)] = c
            mi[(p, q)] = mm
    total = int(val[(D, D)][n])
    return total, typ, cut, mi


def _build(D, n, typ, cut, mi):
    out = []
    stack = [(D, D, n, 0, 0)]
    while stack:
        p, q, m, x0, y0 = stack.pop()
        if m <= 0:
            continue
        t = int(typ[(p, q)][m])
        if t == 0:
            s = min(p, q)
            out.append(((x0 + s / 2.0) / D, (y0 + s / 2.0) / D, 0.0, s / D))
        else:
            c = int(cut[(p, q)][m])
            m1 = int(mi[(p, q)][m])
            m2 = m - m1
            if t == 1:
                stack.append((c, q, m1, x0, y0))
                stack.append((p - c, q, m2, x0 + c, y0))
            else:
                stack.append((p, c, m1, x0, y0))
                stack.append((p, q - c, m2, x0, y0 + c))
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    N = n + 1
    M = np.arange(N)[:, None]
    I = np.arange(N)[None, :]
    idx = M - I
    NEGM = np.where(idx >= 0, 0, -10**9).astype(np.int64)
    I_idx = np.where(idx >= 0, idx, 0)
    ar = np.arange(N)

    best_val = -1.0
    best_sq = None
    last_t = None
    last_D = None
    budget = 38.0
    for D in range(1, 25):
        if last_t is not None:
            est = last_t * (D / last_D) ** 3.2
            if time.time() - t0 + est > budget:
                break
        ts = time.time()
        total, typ, cut, mi = _run(D, n, I_idx, NEGM, ar)
        last_t = max(time.time() - ts, 1e-4)
        last_D = D
        v = total / D
        if v > best_val + 1e-12:
            sq = _build(D, n, typ, cut, mi)
            best_val = v
            best_sq = sq
    sq = list(best_sq)
    sq = sq[:n]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    res = []
    for (x, y, a, s) in sq:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return res
# EVOLVE-BLOCK-END
