# EVOLVE-BLOCK-START
"""Guillotine recursion on a rational grid: a rectangle a x b holding m squares is either
a single square (if a==b) or is cut into two rectangles, with counts distributed optimally.
This generalises 'one big square plus two rectangles' and grid-column fillings."""
import math
import time
import numpy as np


def _dp(n, D, deadline):
    N = n + 1
    NEG = -1e18
    F = np.full((D + 1, D + 1, N), NEG)
    F[:, :, 0] = 0.0
    CO = np.zeros((D + 1, D + 1, N), dtype=np.int8)
    CX = np.zeros((D + 1, D + 1, N), dtype=np.int32)
    CI = np.zeros((D + 1, D + 1, N), dtype=np.int32)
    ar = np.arange(N)
    J = ar[None, :] - ar[:, None]
    J[J < 0] = N
    negpad = np.array([NEG])
    for a in range(1, D + 1):
        if time.time() > deadline:
            return None
        for b in range(1, D + 1):
            best = F[a, b]
            if a == b:
                best[1:] = a
            co = CO[a, b]
            cx = CX[a, b]
            ci = CI[a, b]
            for x in range(1, a // 2 + 1):
                u = F[x, b]
                v = np.concatenate((F[a - x, b], negpad))
                M = u[:, None] + v[J]
                bi = M.argmax(0)
                val = M[bi, ar]
                upd = val > best + 1e-9
                if upd.any():
                    best[upd] = val[upd]
                    co[upd] = 1
                    cx[upd] = x
                    ci[upd] = bi[upd]
            for y in range(1, b // 2 + 1):
                u = F[a, y]
                v = np.concatenate((F[a, b - y], negpad))
                M = u[:, None] + v[J]
                bi = M.argmax(0)
                val = M[bi, ar]
                upd = val > best + 1e-9
                if upd.any():
                    best[upd] = val[upd]
                    co[upd] = 2
                    cx[upd] = y
                    ci[upd] = bi[upd]
    return F, CO, CX, CI


def _reconstruct(D, F, CO, CX, CI, n):
    out = []
    stack = [(D, D, n, 0, 0)]
    while stack:
        a, b, m, ox, oy = stack.pop()
        if m <= 0:
            continue
        c = int(CO[a, b, m])
        if c == 0:
            s = a / D
            out.append(((ox + a / 2) / D, (oy + b / 2) / D, 0.0, s))
            for _ in range(m - 1):
                out.append((ox / D, oy / D, 0.0, 0.0))
        elif c == 1:
            x = int(CX[a, b, m]); i = int(CI[a, b, m])
            stack.append((x, b, i, ox, oy))
            stack.append((a - x, b, m - i, ox + x, oy))
        else:
            y = int(CX[a, b, m]); i = int(CI[a, b, m])
            stack.append((a, y, i, ox, oy))
            stack.append((a, b - y, m - i, ox, oy + y))
    return out


def solve(n):
    t0 = time.time()
    budget = 45.0
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    best = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    best += [(0.0, 0.0, 0.0, 0.0)] * (n - len(best))
    best = best[:n]
    best_val = sum(s[3] for s in best)
    if n <= 1:
        return [(0.5, 0.5, 0.0, 1.0)][:n] if n == 1 else []

    cands = []
    for D in [12, 24, 2 * k, 2 * (k + 1), 3 * k, 3 * (k + 1), 36, 48, k * (k + 1), 60]:
        if D >= 2 and D not in cands and D <= 120:
            cands.append(D)
    rate = None  # seconds per D^3 * (N^2 + 50)
    N = n + 1
    for D in cands:
        elapsed = time.time() - t0
        remaining = budget - elapsed
        if remaining <= 0:
            break
        work = D ** 3 * (N * N + 50)
        if rate is not None and rate * work > remaining:
            continue
        ts = time.time()
        res = _dp(n, D, t0 + budget)
        if res is None:
            break
        dt = time.time() - ts
        rate = max(dt / work, 1e-12) if rate is None else max(rate, dt / work)
        F, CO, CX, CI = res
        val = F[D, D, n] / D
        if val > best_val + 1e-9:
            sq = _reconstruct(D, F, CO, CX, CI, n)
            if len(sq) == n:
                best = sq
                best_val = val
    return best
# EVOLVE-BLOCK-END
