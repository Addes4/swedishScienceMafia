# EVOLVE-BLOCK-START
"""Recursive guillotine split with uniform grids in the leaves."""
import math
import numpy as np


def solve(n):
    P = 8
    fr = set()
    for p in range(2, P + 1):
        for k in range(1, p):
            fr.add(round(k / p, 12))
    fr = sorted(fr)
    depth = 2 if n <= 80 else 1
    memo = {}

    def key(w, h, d):
        return (round(w, 9), round(h, 9), d)

    def S(w, h, d):
        k = key(w, h, d)
        if k in memo:
            return memo[k]
        N = n
        vals = np.zeros(N + 1)
        ch = [None] * (N + 1)
        ch[0] = ('N',)
        for m in range(1, N + 1):
            bv = -1.0
            bc = None
            for p in range(1, m + 1):
                q = -(-m // p)
                s = min(w / p, h / q)
                v = m * s
                if v > bv + 1e-12:
                    bv = v
                    bc = ('L', p, q, m)
            if bv < vals[m - 1]:
                bv = vals[m - 1]
                bc = ch[m - 1]
            vals[m] = bv
            ch[m] = bc
        if d > 0:
            for orient in (0, 1):
                dim = h if orient == 0 else w
                for f in fr:
                    t = f * dim
                    if orient == 0:
                        A = (w, t)
                        B = (w, h - t)
                    else:
                        A = (t, h)
                        B = (w - t, h)
                    a = S(A[0], A[1], d - 1)[0]
                    b = S(B[0], B[1], d - 1)[0]
                    best = np.full(N + 1, -1.0)
                    arg = np.zeros(N + 1, dtype=int)
                    for m1 in range(N + 1):
                        cand = a[m1] + b[:N + 1 - m1]
                        seg = best[m1:]
                        upd = cand > seg + 1e-15
                        if upd.any():
                            seg[upd] = cand[upd]
                            arg[m1:][upd] = m1
                    better = np.nonzero(best > vals + 1e-12)[0]
                    for m in better:
                        vals[m] = best[m]
                        ch[m] = ('C', orient, t, int(arg[m]))
        memo[k] = (vals, ch)
        return memo[k]

    out = []

    def place(w, h, x0, y0, m, d):
        if m <= 0 or w <= 0 or h <= 0:
            return
        c = S(w, h, d)[1][m]
        if c[0] == 'N':
            return
        if c[0] == 'L':
            _, p, q, cnt = c
            s = min(w / p, h / q)
            idx = 0
            for j in range(q):
                for i in range(p):
                    if idx >= cnt:
                        return
                    out.append((x0 + (i + 0.5) * s, y0 + (j + 0.5) * s, 0.0, s * (1 - 1e-9)))
                    idx += 1
            return
        _, orient, t, m1 = c
        if orient == 0:
            place(w, t, x0, y0, m1, d - 1)
            place(w, h - t, x0, y0 + t, m - m1, d - 1)
        else:
            place(t, h, x0, y0, m1, d - 1)
            place(w - t, h, x0 + t, y0, m - m1, d - 1)

    place(1.0, 1.0, 0.0, 0.0, n, depth)
    res = []
    for (x, y, a, s) in out:
        x = min(max(x, 0.0), 1.0)
        y = min(max(y, 0.0), 1.0)
        res.append((x, y, a, min(max(s, 0.0), 1.0)))
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
