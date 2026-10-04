# EVOLVE-BLOCK-START
"""Guillotine dynamic program over integer L x L boards (fallback for CP-SAT idea).

For every board size L we compute, via DP over all integer rectangles, the best
total side length of at most n axis-parallel integer squares obtainable by
recursive guillotine cuts. This includes grids, merged blocks, recursive
subdivisions and 'ring' constructions. The best L (normalised) is returned.
"""
import math
import time
import numpy as np


def _build(N, Lmax, t0, tlimit):
    I = np.arange(N + 1)[:, None]
    K = np.arange(N + 1)[None, :]
    J = K - I
    mask = J < 0
    Jc = np.clip(J, 0, N)
    cols = np.arange(N + 1)

    V = {}
    T = {}
    P = {}
    S = {}

    def get(w, h):
        return V[(w, h)] if w >= h else V[(h, w)]

    def mp(A, B):
        D = A[:, None] + B[Jc]
        D[mask] = -1e18
        arg = D.argmax(axis=0)
        return D[arg, cols], arg

    done_L = 0
    for a in range(1, Lmax + 1):
        if time.time() - t0 > tlimit:
            break
        for b in range(1, a + 1):
            val = np.full(N + 1, float(b))
            val[0] = 0.0
            typ = np.ones(N + 1, dtype=np.int8)
            typ[0] = 0
            pos = np.zeros(N + 1, dtype=np.int32)
            spl = np.zeros(N + 1, dtype=np.int32)
            # vertical cuts: pieces (x,b) and (a-x,b)
            for x in range(1, a // 2 + 1):
                C, arg = mp(get(x, b), get(a - x, b))
                upd = C > val + 1e-9
                if upd.any():
                    val[upd] = C[upd]
                    typ[upd] = 2
                    pos[upd] = x
                    spl[upd] = arg[upd]
            for y in range(1, b // 2 + 1):
                C, arg = mp(get(a, y), get(a, b - y))
                upd = C > val + 1e-9
                if upd.any():
                    val[upd] = C[upd]
                    typ[upd] = 3
                    pos[upd] = y
                    spl[upd] = arg[upd]
            V[(a, b)] = val
            T[(a, b)] = typ
            P[(a, b)] = pos
            S[(a, b)] = spl
        done_L = a
    return V, T, P, S, done_L


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    N = n
    # choose Lmax adaptively
    Lmax = 48
    while Lmax > 4 and (Lmax ** 3) * (N + 1) ** 2 / 2.0 > 6e8:
        Lmax -= 1
    V, T, P, S, doneL = _build(N, Lmax, t0, 25.0)

    bestL, bestv = 1, -1.0
    for L in range(1, doneL + 1):
        v = V[(L, L)][N] / L
        if v > bestv + 1e-12:
            bestv, bestL = v, L

    import sys
    sys.setrecursionlimit(10000)

    def place(w, h, k):
        # returns list of (x, y, s) local lower-left coords, rect width w height h
        if k <= 0:
            return []
        if w < h:
            return [(y, x, s) for (x, y, s) in place(h, w, k)]
        key = (w, h)
        t = int(T[key][k])
        if t == 0:
            return []
        if t == 1:
            return [(0, 0, h)]
        p = int(P[key][k])
        i = int(S[key][k])
        if t == 2:
            r = place(p, h, i)
            r += [(x + p, y, s) for (x, y, s) in place(w - p, h, k - i)]
            return r
        r = place(w, p, i)
        r += [(x, y + p, s) for (x, y, s) in place(w, h - p, k - i)]
        return r

    L = bestL
    sq = place(L, L, N)
    out = []
    for (x, y, s) in sq:
        cx = (x + s / 2.0) / L
        cy = (y + s / 2.0) / L
        out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, s / L))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
