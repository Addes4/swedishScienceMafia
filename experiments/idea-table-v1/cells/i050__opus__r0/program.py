# EVOLVE-BLOCK-START
"""Recursive guillotine splitting into rectangles, each filled with a uniform grid.
Cut positions are taken at breakpoints of the piecewise-linear grid-side functions;
the squares are distributed between the two parts by max-plus convolution."""
import math
import time
import numpy as np


class _Timeout(Exception):
    pass


def solve(n):
    if n <= 0:
        return []
    N = n
    K = max(4, math.isqrt(N) + 2)
    start = time.time()
    budget = 40.0

    grid_memo = {}
    memo = {}

    def key(w, h):
        return (round(w, 10), round(h, 10))

    def grid_arr(w, h):
        k = key(w, h)
        if k in grid_memo:
            return grid_memo[k]
        vals = np.zeros(N + 1)
        ch = [None] * (N + 1)
        for m in range(1, N + 1):
            best = vals[m - 1]
            c = ('zero',)
            for p in range(1, m + 1):
                q = -(-m // p)
                s = min(h / p, w / q)
                v = m * s
                if v > best + 1e-12:
                    best = v
                    c = ('grid', p, q)
            vals[m] = best
            ch[m] = c
        ch[0] = ('none',)
        grid_memo[k] = (vals, ch)
        return vals, ch

    def maxplus(A, B):
        C = np.full(N + 1, -1.0)
        arg = np.zeros(N + 1, dtype=int)
        for a in range(N + 1):
            v = A[a] + B[:N + 1 - a]
            seg = C[a:]
            mask = v > seg + 1e-12
            if mask.any():
                seg[mask] = v[mask]
                sub = arg[a:]
                sub[mask] = a
        return C, arg

    def cut_candidates(w, h):
        # vertical cut at x = t of a w x h rectangle
        ts = set()
        for r in range(1, K + 1):
            for c in range(1, K + 1):
                t = c * h / r
                if 1e-9 < t < w - 1e-9:
                    ts.add(round(t, 10))
                t2 = w - t
                if 1e-9 < t2 < w - 1e-9:
                    ts.add(round(t2, 10))
        ts.add(round(w / 2, 10))
        return sorted(ts)

    def f(w, h, d):
        if w < h:
            return f(h, w, d)
        k = key(w, h) + (d,)
        if k in memo:
            return memo[k]
        if time.time() - start > budget:
            raise _Timeout()
        gv, gch = grid_arr(w, h)
        vals = gv.copy()
        ch = list(gch)
        if d > 0:
            # vertical cuts (along width)
            for orient in (0, 1):
                if orient == 0:
                    W, H = w, h
                else:
                    W, H = h, w
                    if abs(w - h) < 1e-12:
                        break
                for t in cut_candidates(W, H):
                    if orient == 0:
                        A = f(t, h, d - 1)[0]
                        B = f(w - t, h, d - 1)[0]
                    else:
                        A = f(w, t, d - 1)[0]
                        B = f(w, h - t, d - 1)[0]
                    C, arg = maxplus(A, B)
                    better = C > vals + 1e-12
                    if better.any():
                        for m in np.nonzero(better)[0]:
                            vals[m] = C[m]
                            ch[m] = ('cut', orient, t, int(arg[m]), d - 1)
        memo[k] = (vals, ch)
        return vals, ch

    def rec(w, h, m, d):
        if m <= 0:
            return []
        if w < h:
            return [(y, x, s) for (x, y, s) in rec(h, w, m, d)]
        vals, ch = f(w, h, d)
        c = ch[m]
        if c[0] == 'zero':
            return rec(w, h, m - 1, d)
        if c[0] == 'grid':
            p, q = c[1], c[2]
            s = min(h / p, w / q)
            out = []
            cnt = 0
            for j in range(p):
                for i in range(q):
                    if cnt >= m:
                        break
                    out.append(((i + 0.5) * s, (j + 0.5) * s, s))
                    cnt += 1
            return out
        if c[0] == 'cut':
            _, orient, t, a, d1 = c
            if orient == 0:
                L = rec(t, h, a, d1)
                R = rec(w - t, h, m - a, d1)
                return L + [(x + t, y, s) for (x, y, s) in R]
            else:
                L = rec(w, t, a, d1)
                R = rec(w, h - t, m - a, d1)
                return L + [(x, y + t, s) for (x, y, s) in R]
        return []

    best_layout = None
    best_val = -1.0
    d = 0
    while True:
        try:
            vals, _ = f(1.0, 1.0, d)
            if vals[N] > best_val + 1e-12 or best_layout is None:
                lay = rec(1.0, 1.0, N, d)
                best_val = vals[N]
                best_layout = lay
        except _Timeout:
            break
        d += 1
        if d > 8 or time.time() - start > budget * 0.5:
            break

    out = []
    for (x, y, s) in best_layout:
        s2 = max(0.0, s * (1 - 1e-12) - 1e-13)
        x = min(max(x, s2 / 2), 1 - s2 / 2)
        y = min(max(y, s2 / 2), 1 - s2 / 2)
        out.append((x, y, 0.0, s2))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
