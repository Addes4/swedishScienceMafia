# EVOLVE-BLOCK-START
"""Recursive grid DP: split a square into a k x k grid, optionally merge an m x m corner
block, and recursively fill the block and cells with the best arrangement for their counts."""
import math
import numpy as np

_best = [0.0, 1.0]
_choice = [None, ("single",)]
NEG = -1e18


def _compute(n):
    for N in range(len(_best), n + 1):
        bestarr = np.array(_best[:N], dtype=float)
        kmax = min(int(math.ceil(math.sqrt(N))) + 2, 12)
        J = kmax * kmax
        G = np.full((J + 1, N + 1), NEG)
        G[0, 0] = 0.0
        arg = np.zeros((J + 1, N + 1), dtype=int)
        for j in range(1, J + 1):
            prev = G[j - 1]
            for c in range(N + 1):
                cp = min(c, N - 1)
                a = prev[c - cp:c + 1][::-1] + bestarr[:cp + 1]
                i = int(np.argmax(a))
                G[j, c] = a[i]
                arg[j, c] = i

        def counts(j, c):
            out = []
            while j > 0:
                cc = int(arg[j, c])
                out.append(cc)
                c -= cc
                j -= 1
            return out

        bv = 1.0
        bc = ("single",)
        for k in range(2, kmax + 1):
            v = G[k * k, N] / k
            if v > bv + 1e-12:
                bv = v
                bc = (k, 1, 0, counts(k * k, N))
            for m in range(2, k):
                j = k * k - m * m
                for b in range(1, N):
                    r = N - b
                    if G[j, r] < -1e17:
                        continue
                    v = (m * _best[b] + G[j, r]) / k
                    if v > bv + 1e-12:
                        bv = v
                        bc = (k, m, b, counts(j, r))
        _best.append(bv)
        _choice.append(bc)


def _place(N, x0, y0, s, out):
    if N == 0:
        return
    ch = _choice[N]
    if ch[0] == "single":
        out.append((x0 + s / 2, y0 + s / 2, 0.0, s * (1 - 1e-9)))
        for _ in range(N - 1):
            out.append((x0 + s / 2, y0 + s / 2, 0.0, 0.0))
        return
    k, m, b, cnts = ch
    cell = s / k
    if m >= 2:
        _place(b, x0, y0, m * cell, out)
    idx = 0
    for i in range(k):
        for j in range(k):
            if m >= 2 and i < m and j < m:
                continue
            c = cnts[idx]
            idx += 1
            if c > 0:
                _place(c, x0 + i * cell, y0 + j * cell, cell, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    _compute(n)
    out = []
    _place(n, 0.0, 0.0, 1.0, out)
    out = [(min(1.0, max(0.0, a)), min(1.0, max(0.0, b)), 0.0, min(1.0, max(0.0, s)))
           for a, b, _, s in out]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
