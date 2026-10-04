# EVOLVE-BLOCK-START
"""Recursive mixed-scale lattice: DP over grids / L-shaped layouts with sub-solutions."""
import math
import numpy as np

_cache = {}


def _build(n):
    K = min(math.isqrt(n) + 2, 12)
    if n > 150:
        K = min(K, 8)
    K = max(K, 2)
    ks = list(range(2, K + 1))
    F = np.zeros(n + 1)
    choice = [None] * (n + 1)
    G = {k: np.zeros((k * k + 1, n + 1)) for k in ks}
    A = {k: np.zeros((k * k + 1, n + 1), dtype=np.int64) for k in ks}
    for m in range(1, n + 1):
        if m > 1 and F[m - 1] > 1:
            best = F[m - 1]
            ch = ('c',)
        else:
            best = 1.0
            ch = ('s',)
        Fm = F[0:m]
        for k in ks:
            Gk = G[k]
            Ak = A[k]
            kk = k * k
            for c in range(1, kk + 1):
                vals = Gk[c - 1, m:0:-1] + Fm
                a = int(np.argmax(vals))
                Gk[c, m] = vals[a]
                Ak[c, m] = a
            cand = Gk[kk, m] / k
            if cand > best + 1e-12:
                best = cand
                ch = ('g', k)
            for j in range(1, k):
                cand = (j + Gk[kk - j * j, m - 1]) / k
                if cand > best + 1e-12:
                    best = cand
                    ch = ('l', k, j)
        F[m] = best
        choice[m] = ch
        for k in ks:
            Gk = G[k]
            Ak = A[k]
            for c in range(1, k * k + 1):
                if best > Gk[c, m] + 1e-12:
                    Gk[c, m] = best
                    Ak[c, m] = m
    return F, choice, A


def solve(n):
    if n not in _cache:
        _cache[n] = _build(n)
    F, choice, A = _cache[n]
    out = []
    eps = 1.0 - 1e-12

    def rec(m, x0, y0, size):
        if m <= 0:
            return
        ch = choice[m]
        while ch[0] == 'c':
            m -= 1
            ch = choice[m]
        if ch[0] == 's':
            out.append((x0 + size / 2, y0 + size / 2, 0.0, size * eps))
            return
        k = ch[1]
        s = size / k
        Ak = A[k]
        if ch[0] == 'g':
            cells = [(i, j) for i in range(k) for j in range(k)]
            c = k * k
            t = m
        else:
            j0 = ch[2]
            out.append((x0 + j0 * s / 2, y0 + j0 * s / 2, 0.0, j0 * s * eps))
            cells = [(i, j) for i in range(k) for j in range(k) if not (i < j0 and j < j0)]
            c = len(cells)
            t = m - 1
        while c >= 1 and t > 0:
            a = int(Ak[c, t])
            if a > 0:
                i, j = cells[c - 1]
                rec(a, x0 + i * s, y0 + j * s, s)
            t -= a
            c -= 1

    rec(n, 0.0, 0.0, 1.0)
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END
