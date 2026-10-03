# EVOLVE-BLOCK-START
"""Baseline: the largest k x k grid that fits, plus size-zero squares for the rest."""
import math
import time
import numpy as np


def _cells(k, j, N):
    """Cell list: (row, col, size_in_cells). Unit cells first (truncated), block last."""
    units = []
    for r in range(k):
        for c in range(k):
            if r < j and c < j:
                continue
            units.append((r, c, 1))
    if j == 1:
        units.append((0, 0, 1))
    else:
        units.append((0, 0, j))
    # truncate unit cells (each non-empty cell needs >=1 square)
    if len(units) - 1 > N:
        units = units[:N] + [units[-1]]
    return units


def _knap(k, j, N, F):
    cells = _cells(k, j, N)
    dp = np.zeros(N + 1)
    args = []
    for (_, _, sz) in cells:
        w = sz / k
        new = dp.copy()
        arg = np.zeros(N + 1, dtype=np.int64)
        for m in range(1, N):
            cand = dp[:N + 1 - m] + w * F[m]
            seg = new[m:]
            mask = cand > seg + 1e-12
            if mask.any():
                seg[mask] = cand[mask]
                arg[m:][mask] = m
        dp = new
        args.append(arg)
    t = N
    alloc = [0] * len(cells)
    for idx in range(len(cells) - 1, -1, -1):
        m = int(args[idx][t])
        alloc[idx] = m
        t -= m
    return float(dp[N]), cells, alloc


def _build(n, deadline):
    F = [0.0, 1.0] + [0.0] * max(0, n - 1)
    choice = {1: None}
    for N in range(2, n + 1):
        k0 = math.isqrt(N)
        best = float(k0)
        ch = ("grid", k0)
        if F[N - 1] > best + 1e-12:
            best = F[N - 1]
            ch = ("less", N - 1)
        if time.time() < deadline:
            for k in range(2, k0 + 3):
                for j in range(1, k):
                    val, cells, alloc = _knap(k, j, N, F)
                    if val > best + 1e-12:
                        best = val
                        ch = ("cfg", k, cells, alloc)
        F[N] = best
        choice[N] = ch
    return F, choice


def _place(N, x0, y0, s, choice, out):
    if N <= 0:
        return
    if N == 1:
        out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
        return
    ch = choice[N]
    if ch[0] == "less":
        _place(ch[1], x0, y0, s, choice, out)
    elif ch[0] == "grid":
        k = ch[1]
        side = s / k
        for i in range(k):
            for j in range(k):
                out.append((x0 + (i + 0.5) * side, y0 + (j + 0.5) * side, 0.0, side))
    else:
        _, k, cells, alloc = ch
        cs = s / k
        for (r, c, sz), m in zip(cells, alloc):
            if m > 0:
                _place(m, x0 + c * cs, y0 + r * cs, sz * cs, choice, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    deadline = time.time() + 40.0
    F, choice = _build(n, deadline)
    out = []
    _place(n, 0.0, 0.0, 1.0, choice, out)
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    res = []
    for (x, y, a, s) in out:
        s = min(max(s, 0.0), 1.0)
        res.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), a, s))
    return res
# EVOLVE-BLOCK-END