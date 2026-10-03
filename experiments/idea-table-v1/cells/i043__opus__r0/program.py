# EVOLVE-BLOCK-START
"""Grid-based exact rectangle-count tables (guillotine cuts + pinwheel
decompositions) over several grid denominators D."""
import math
import time
import numpy as np


def solve(n):
    t0 = time.time()
    TL = 40.0
    if n <= 0:
        return []
    L = n + 1
    I, J = np.meshgrid(np.arange(L), np.arange(L), indexing='ij')
    S = (I + J).ravel()
    idx = np.nonzero(S <= n)[0]
    order = np.argsort(S[idx], kind='stable')
    perm = idx[order]
    sums = S[perm]
    starts = np.searchsorted(sums, np.arange(L))

    def conv(u, v):
        M = (u[:, None] + v[None, :]).ravel()[perm]
        return np.maximum.reduceat(M, starts)

    def pin_configs(a, b):
        for x1 in range(1, a - 1):
            for x2 in range(x1 + 1, a):
                for y1 in range(1, b - 1):
                    for y2 in range(y1 + 1, b):
                        yield x1, x2, y1, y2

    def pin_pieces(a, b, x1, x2, y1, y2):
        # (x, y, w, h)
        return [(0, 0, x1, y2), (x1, 0, a - x1, y1), (x2, y1, a - x2, b - y1),
                (0, y2, x2, b - y2), (x1, y1, x2 - x1, y2 - y1)]

    def build_table(D, full_pin):
        T = {}

        def get(w, h):
            return T[(w, h)] if w <= h else T[(h, w)]

        for a in range(1, D + 1):
            for b in range(a, D + 1):
                best = np.full(L, a, dtype=np.int64)
                best[0] = 0
                for a1 in range(1, a // 2 + 1):
                    best = np.maximum(best, conv(get(a1, b), get(a - a1, b)))
                for b1 in range(1, b // 2 + 1):
                    best = np.maximum(best, conv(get(a, b1), get(a, b - b1)))
                if (full_pin or (a == D and b == D)) and a >= 3 and b >= 3:
                    cnt = 0
                    for (x1, x2, y1, y2) in pin_configs(a, b):
                        cnt += 1
                        if (cnt & 255) == 0 and time.time() - t0 > TL + 10:
                            break
                        pcs = pin_pieces(a, b, x1, x2, y1, y2)
                        c = get(pcs[0][2], pcs[0][3])
                        for p in pcs[1:]:
                            c = conv(c, get(p[2], p[3]))
                        best = np.maximum(best, c)
                T[(a, b)] = best
        return T, get

    k = math.isqrt(n)
    Dmax = max(12, k + 3)
    cand = []
    for d in [k, k + 1, k - 1, k + 2, 2 * k, 2 * k + 1, 2 * k - 1, 2 * k + 2]:
        if 1 <= d <= Dmax and d not in cand:
            cand.append(d)
    for d in range(1, Dmax + 1):
        if d not in cand:
            cand.append(d)

    bestval, bestD, best_info = -1, 1, None
    for D in cand:
        if time.time() - t0 > TL:
            break
        full_pin = (D <= 12 and n <= 60) or D <= 7
        T, get = build_table(D, full_pin)
        v = int(T[(D, D)][n])
        if best_info is None or v * bestD > bestval * D:
            bestval, bestD, best_info = v, D, (T, get, full_pin)

    T, get, full_pin = best_info
    D = bestD
    out = []

    def build(a, b, m, x, y):
        target = int(get(a, b)[m])
        if m == 0 or target == 0:
            return
        s = min(a, b)
        if target == s:
            out.append((x, y, s))
            return
        for a1 in range(1, a):
            u, v = get(a1, b), get(a - a1, b)
            for i in range(m + 1):
                if int(u[i]) + int(v[m - i]) == target:
                    build(a1, b, i, x, y)
                    build(a - a1, b, m - i, x + a1, y)
                    return
        for b1 in range(1, b):
            u, v = get(a, b1), get(a, b - b1)
            for i in range(m + 1):
                if int(u[i]) + int(v[m - i]) == target:
                    build(a, b1, i, x, y)
                    build(a, b - b1, m - i, x, y + b1)
                    return
        if a >= 3 and b >= 3:
            for (x1, x2, y1, y2) in pin_configs(a, b):
                pcs = pin_pieces(a, b, x1, x2, y1, y2)
                arrs = [get(p[2], p[3]) for p in pcs]
                cs = [arrs[0]]
                for ar in arrs[1:]:
                    cs.append(conv(cs[-1], ar))
                if int(cs[-1][m]) != target:
                    continue
                rem, tgt = m, target
                alloc = [0] * 5
                for j in range(4, 0, -1):
                    for i in range(rem + 1):
                        if int(cs[j - 1][rem - i]) + int(arrs[j][i]) == tgt:
                            alloc[j] = i
                            tgt -= int(arrs[j][i])
                            rem -= i
                            break
                alloc[0] = rem
                for p, cnum in zip(pcs, alloc):
                    build(p[2], p[3], cnum, x + p[0], y + p[1])
                return
        # fallback (should not happen)
        out.append((x, y, s))

    build(D, D, n, 0, 0)
    squares = []
    for (x, y, s) in out[:n]:
        cx = min(1.0, max(0.0, (x + s / 2.0) / D))
        cy = min(1.0, max(0.0, (y + s / 2.0) / D))
        squares.append((cx, cy, 0.0, min(1.0, s / D)))
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares[:n]
# EVOLVE-BLOCK-END
