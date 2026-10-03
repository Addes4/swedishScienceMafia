# EVOLVE-BLOCK-START
"""Guillotine DP over integer rectangles (units 1/D) with single squares,
uniform grids and guillotine cuts; best over denominators D."""
import math
import time
import numpy as np


def _run_dp(D, n):
    """Returns tables for denominator D: val[p][q] arrays, choice arrays."""
    N = n + 1
    val = {}
    kind = {}
    pa = {}
    pb = {}
    for p in range(1, D + 1):
        for q in range(1, D + 1):
            C = np.zeros(N)
            K = np.zeros(N, dtype=np.int64)
            A1 = np.zeros(N, dtype=np.int64)
            B1 = np.zeros(N, dtype=np.int64)
            # single square
            if n >= 1:
                C[1] = min(p, q)
                K[1] = 1
            # uniform grids
            for a in range(1, n + 1):
                for b in range(1, n // a + 1):
                    if a == 1 and b == 1:
                        continue
                    s = min(p / a, q / b)
                    v = a * b * s
                    m = a * b
                    if v > C[m] + 1e-12:
                        C[m] = v
                        K[m] = 2
                        A1[m] = a
                        B1[m] = b
            # cuts
            for direction in (3, 4):
                L = p if direction == 3 else q
                for x in range(1, L // 2 + 1):
                    if direction == 3:
                        Av = val[(x, q)]
                        Bv = val[(p - x, q)]
                    else:
                        Av = val[(p, x)]
                        Bv = val[(p, q - x)]
                    for i in range(N):
                        cand = Av[i] + Bv[:N - i]
                        sub = C[i:]
                        mask = cand > sub + 1e-12
                        if mask.any():
                            sub[mask] = cand[mask]
                            K[i:][mask] = direction
                            A1[i:][mask] = x
                            B1[i:][mask] = i
            # monotone (at most m)
            for m in range(1, N):
                if C[m - 1] > C[m] + 1e-12:
                    C[m] = C[m - 1]
                    K[m] = K[m - 1]
                    A1[m] = A1[m - 1]
                    B1[m] = B1[m - 1]
            val[(p, q)] = C
            kind[(p, q)] = K
            pa[(p, q)] = A1
            pb[(p, q)] = B1
    return val, kind, pa, pb


def _build(D, n, tables):
    val, kind, pa, pb = tables
    out = []

    def rec(p, q, m, x0, y0):
        if m <= 0:
            return
        k = int(kind[(p, q)][m])
        if k == 0:
            return
        if k == 1:
            s = min(p, q)
            out.append((x0 + s / 2.0, y0 + s / 2.0, s))
        elif k == 2:
            a = int(pa[(p, q)][m])
            b = int(pb[(p, q)][m])
            s = min(p / a, q / b)
            for i in range(a):
                for j in range(b):
                    out.append((x0 + (i + 0.5) * s, y0 + (j + 0.5) * s, s))
        elif k == 3:
            x = int(pa[(p, q)][m])
            m1 = int(pb[(p, q)][m])
            rec(x, q, m1, x0, y0)
            rec(p - x, q, m - m1, x0 + x, y0)
        elif k == 4:
            y = int(pa[(p, q)][m])
            m1 = int(pb[(p, q)][m])
            rec(p, y, m1, x0, y0)
            rec(p, q - y, m - m1, x0, y0 + y)

    rec(D, D, n, 0, 0)
    res = []
    for (cx, cy, s) in out:
        side = max(0.0, s / D - 1e-12)
        res.append((min(1.0, max(0.0, cx / D)), min(1.0, max(0.0, cy / D)), 0.0, min(1.0, side)))
    return res


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    k = math.isqrt(n)
    best_val = -1.0
    best = None
    Dmax = max(12, k + 4)
    last = None
    for D in range(1, Dmax + 1):
        el = time.time() - t0
        if last is not None:
            pred = last * ((D / max(1, D - 1)) ** 3) * 1.3
            if el + pred > 45.0:
                break
        ts = time.time()
        tables = _run_dp(D, n)
        v = tables[0][(D, D)][n] / D
        if v > best_val + 1e-12:
            sq = _build(D, n, tables)
            if len(sq) <= n:
                best_val = v
                best = sq
        last = time.time() - ts
    if best is None:
        side = 1.0 / k
        best = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    best = list(best[:n])
    best += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best))
    return best
# EVOLVE-BLOCK-END
