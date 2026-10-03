# EVOLVE-BLOCK-START
"""Recursive subdivision search (exact DP over subdivision trees).

Patterns applied to a square region:
  * j x j grid of equal squares
  * j x j grid with a b x b corner block merged into one square
  * corner a x a grid of side s=(1-1/m)/a plus an L-band of squares of side 1/m
Each piece is recursively subdivided or deleted (gets 0 squares).
"""
import math
import numpy as np


def solve(n):
    if n <= 0:
        return []
    N = n
    r = math.isqrt(N)
    Qcap = (r + 2) ** 2
    lim = min(N + 2, 2 * r + 8)

    patterns = []  # list of groups: [(q, side, [(rx, ry, rs), ...]), ...]
    # plain grids
    for j in range(2, r + 3):
        q = j * j
        if q > Qcap:
            break
        s = 1.0 / j
        sq = [(i * s, jj * s, s) for i in range(j) for jj in range(j)]
        patterns.append([(q, s, sq)])
    # merged-corner grids
    for j in range(3, lim + 1):
        s = 1.0 / j
        for b in range(2, j):
            q = j * j - b * b
            if q > Qcap:
                continue
            big = [(0.0, 0.0, b * s)]
            rest = [(i * s, jj * s, s) for i in range(j) for jj in range(j)
                    if not (i < b and jj < b)]
            patterns.append([(1, b * s, big), (q, s, rest)])
    # corner grid + L band
    for a in range(1, r + 2):
        if a * a > Qcap:
            break
        for m in range(2, lim + 1):
            t = 1.0 / m
            s = (1.0 - t) / a
            ga = [(i * s, t + jj * s, s) for i in range(a) for jj in range(a)]
            gb = [(1.0 - t, rr * t, t) for rr in range(m)] + \
                 [(rr * t, 0.0, t) for rr in range(m - 1)]
            qb = min(len(gb), N, Qcap)
            gb = gb[:qb]
            patterns.append([(a * a, s, ga), (qb, t, gb)])

    Q = max(g[0] for p in patterns for g in p)
    NEG = -np.inf
    F = np.full((Q + 1, N + 1), NEG)
    FB = np.zeros((Q + 1, N + 1), dtype=np.int64)
    G = np.full((Q + 1, N + 1), NEG)
    GB = np.zeros((Q + 1, N + 1), dtype=np.int64)
    f = np.full(N + 1, NEG)
    fch = [None] * (N + 1)
    f[0] = 0.0
    F[:, 0] = 0.0
    G[:, 0] = 0.0

    for k in range(1, N + 1):
        if k >= 2:
            S = F[:Q, k - 1:0:-1] + f[1:k]
            M = S.max(axis=1)
            Mi = S.argmax(axis=1) + 1
        else:
            M = np.full(Q, NEG)
            Mi = np.zeros(Q, dtype=np.int64)
        gprev = NEG
        for q in range(1, Q + 1):
            if M[q - 1] > gprev:
                gprev = M[q - 1]
                GB[q, k] = Mi[q - 1]
            else:
                GB[q, k] = 0
            G[q, k] = gprev
        best = f[k - 1]
        ch = ('pad',)
        if k == 1 and 1.0 > best:
            best = 1.0
            ch = ('one',)
        for pid, p in enumerate(patterns):
            if len(p) == 1:
                q, L, _ = p[0]
                v = L * G[q, k]
                if v > best + 1e-12:
                    best = v
                    ch = ('pat', pid, k)
            else:
                qa, La, _ = p[0]
                qb, Lb, _ = p[1]
                HA = F[qa, :k + 1].copy()
                HA[k] = G[qa, k]
                HB = F[qb, :k + 1].copy()
                HB[k] = G[qb, k]
                vals = La * HA + Lb * HB[::-1]
                idx = int(np.argmax(vals))
                v = vals[idx]
                if v > best + 1e-12:
                    best = v
                    ch = ('pat', pid, idx)
        f[k] = best
        fch[k] = ch
        col = G[1:, k]
        take = f[k] >= col
        F[1:, k] = np.where(take, f[k], col)
        FB[1:, k] = np.where(take, k, -1)

    def assign(q, k, restricted):
        counts = [0] * q
        cur = k
        res = restricted
        for p in range(q, 0, -1):
            if cur == 0:
                break
            if not res:
                b = int(FB[p, cur])
                if b == -1:
                    res = True
                else:
                    counts[p - 1] = b
                    cur -= b
                    continue
            i = int(GB[p, cur])
            counts[p - 1] = i
            if i > 0:
                cur -= i
                res = False
        return counts

    out = []
    zeros = [0]

    def rec(k, x0, y0, L):
        if k == 0:
            return
        ch = fch[k]
        if ch[0] == 'one':
            out.append((x0 + L / 2, y0 + L / 2, L))
        elif ch[0] == 'pad':
            rec(k - 1, x0, y0, L)
            zeros[0] += 1
        else:
            _, pid, k1 = ch
            p = patterns[pid]
            if len(p) == 1:
                parts = [(p[0], k)]
            else:
                parts = [(p[0], k1), (p[1], k - k1)]
            for (q, _, sq), kk in parts:
                if kk == 0:
                    continue
                counts = assign(q, kk, kk == k)
                for (rx, ry, rs), c in zip(sq, counts):
                    if c > 0:
                        rec(c, x0 + rx * L, y0 + ry * L, rs * L)

    rec(N, 0.0, 0.0, 1.0)

    def cl(v):
        return min(1.0, max(0.0, v))

    res = [(cl(x), cl(y), 0.0, cl(s * (1 - 1e-10))) for (x, y, s) in out]
    res = res[:n]
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
