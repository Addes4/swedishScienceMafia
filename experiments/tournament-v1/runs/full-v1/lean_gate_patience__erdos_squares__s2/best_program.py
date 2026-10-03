# EVOLVE-BLOCK-START
"""Recursive grid / corner-block construction with DP allocation of squares to cells."""
import math
import numpy as np

NEG = -1e18


def solve(n):
    N = n
    if N <= 0:
        return []
    K = math.isqrt(N) + 2
    Cmax = K * K
    f = np.zeros(N + 1)
    G = np.full((Cmax + 1, N + 1), NEG)
    Gx = np.full((Cmax + 1, N + 1), NEG)
    G[:, 0] = 0.0
    Gx[:, 0] = 0.0
    best = [None] * (N + 1)
    best[0] = ('zero',)

    for s in range(1, N + 1):
        if s == 1:
            f[1] = 1.0
            best[1] = ('leaf',)
        else:
            bv = f[s - 1]
            bd = ('pad',)
            Gx[0][s] = NEG
            for c in range(1, Cmax + 1):
                v = Gx[c - 1][s]
                vals = f[1:s] + G[c - 1][s - 1:0:-1]
                m = vals.max()
                Gx[c][s] = max(v, m)
            Ks = math.isqrt(s) + 2
            for k in range(2, Ks + 1):
                v = Gx[k * k][s] / k
                if v > bv + 1e-12:
                    bv = v
                    bd = ('grid', k)
                for j in range(2, k):
                    c = k * k - j * j
                    arr = f[1:s] * (j / k) + G[c][s - 1:0:-1] / k
                    i = int(np.argmax(arr))
                    if arr[i] > bv + 1e-12:
                        bv = arr[i]
                        bd = ('block', k, j, i + 1)
            f[s] = bv
            best[s] = bd
        for c in range(1, Cmax + 1):
            vals = f[0:s + 1] + G[c - 1][s::-1]
            G[c][s] = vals.max()

    def alloc(c, s, excl):
        out = []
        while c > 0 and s > 0:
            if excl:
                vals = np.empty(s)
                vals[0] = Gx[c - 1][s]
                if s > 1:
                    vals[1:] = f[1:s] + G[c - 1][s - 1:0:-1]
                a = int(np.argmax(vals))
                if a == 0:
                    out.append(0)
                    c -= 1
                    continue
                out.append(a)
                s -= a
                c -= 1
                excl = False
            else:
                vals = f[0:s + 1] + G[c - 1][s::-1]
                a = int(np.argmax(vals))
                out.append(a)
                s -= a
                c -= 1
        return out

    def place(sub, sc, ox, oy):
        return [(ox + x * sc, oy + y * sc, a, sd * sc) for (x, y, a, sd) in sub]

    def build(s):
        if s <= 0:
            return []
        if s == 1:
            return [(0.5, 0.5, 0.0, 1.0)]
        d = best[s]
        if d[0] == 'pad':
            return build(s - 1) + [(0.5, 0.5, 0.0, 0.0)]
        res = []
        if d[0] == 'grid':
            k = d[1]
            cells = [(r, cc) for r in range(k) for cc in range(k)]
            counts = alloc(k * k, s, True)
        else:
            _, k, j, m = d
            res += place(build(m), j / k, 0.0, 0.0)
            cells = [(r, cc) for r in range(k) for cc in range(k)
                     if not (r < j and cc < j)]
            counts = alloc(len(cells), s - m, False)
        for idx, (r, cc) in enumerate(cells):
            cnt = counts[idx] if idx < len(counts) else 0
            if cnt > 0:
                res += place(build(cnt), 1.0 / k, cc / k, r / k)
        return res

    res = build(N)
    res = res[:N]
    while len(res) < N:
        res.append((0.5, 0.5, 0.0, 0.0))
    out = []
    for (x, y, a, sd) in res:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)),
                    min(1.0, max(0.0, a)), min(1.0, max(0.0, sd))))
    return out
# EVOLVE-BLOCK-END
