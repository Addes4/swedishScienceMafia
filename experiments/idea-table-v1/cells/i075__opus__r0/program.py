# EVOLVE-BLOCK-START
"""Guillotine DP on a K x K integer grid (generalised unequal L-frame peeling).

For each grid resolution K, dp[w,h][m] = max total side (in units of 1/K) of at
most m axis-aligned integer squares packed in a w x h rectangle, built by
guillotine cuts.  This covers grids, L-frames with unequal squares, and
recursive inner squares with arbitrary rational sizes of denominator K."""
import math
import time
import numpy as np


def _conv(a, b, L):
    c = np.zeros(L, dtype=np.int64)
    la, lb = len(a), len(b)
    for i in range(min(la, L)):
        jm = min(lb, L - i)
        seg = a[i] + b[:jm]
        np.maximum(c[i:i + jm], seg, out=c[i:i + jm])
    return np.maximum.accumulate(c)


def _build(K, n, deadline):
    dp = {}
    rects = [(w, h) for w in range(1, K + 1) for h in range(w, K + 1)]
    rects.sort(key=lambda r: (r[0] * r[1], r[0]))

    def get(w, h):
        return dp[(w, h)] if w <= h else dp[(h, w)]

    for (w, h) in rects:
        if time.time() > deadline:
            return None
        L = min(n, w * h) + 1
        arr = np.zeros(L, dtype=np.int64)
        if w == h:
            arr[1:] = w
        for w1 in range(1, w // 2 + 1):
            c = _conv(get(w1, h), get(w - w1, h), L)
            np.maximum(arr, c, out=arr)
        for h1 in range(1, h // 2 + 1):
            c = _conv(get(w, h1), get(w, h - h1), L)
            np.maximum(arr, c, out=arr)
        dp[(w, h)] = arr
    return dp


def _val(dp, w, h, m):
    a = dp[(w, h)] if w <= h else dp[(h, w)]
    return int(a[min(m, len(a) - 1)])


def _rec(dp, w, h, m, x0, y0, out):
    target = _val(dp, w, h, m)
    if target == 0 or m <= 0:
        return
    if w == h and target == w:
        out.append((x0, y0, w))
        return
    for w1 in range(1, w):
        for i in range(0, m + 1):
            if _val(dp, w1, h, i) + _val(dp, w - w1, h, m - i) == target:
                _rec(dp, w1, h, i, x0, y0, out)
                _rec(dp, w - w1, h, m - i, x0 + w1, y0, out)
                return
    for h1 in range(1, h):
        for i in range(0, m + 1):
            if _val(dp, w, h1, i) + _val(dp, w, h - h1, m - i) == target:
                _rec(dp, w, h1, i, x0, y0, out)
                _rec(dp, w, h - h1, m - i, x0, y0 + h1, out)
                return
    # fallback (should not happen)
    if w == h:
        out.append((x0, y0, w))


def solve(n):
    start = time.time()
    deadline = start + 40.0
    if n <= 0:
        return []
    r = math.isqrt(n)
    Kmax = max(16, r + 6)
    order = [max(1, r)] + [K for K in range(1, Kmax + 1) if K != max(1, r)]
    best_val, best_K, best_dp = -1.0, None, None
    for K in order:
        if time.time() > deadline:
            break
        dp = _build(K, n, deadline)
        if dp is None:
            break
        v = _val(dp, K, K, n) / K
        if v > best_val + 1e-12:
            best_val, best_K, best_dp = v, K, dp

    squares = []
    if best_dp is not None:
        cells = []
        _rec(best_dp, best_K, best_K, n, 0, 0, cells)
        K = best_K
        for (x, y, s) in cells[:n]:
            squares.append(((x + s / 2.0) / K, (y + s / 2.0) / K, 0.0, s / K))
    else:
        k = max(1, r)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                   for i in range(k) for j in range(k)][:n]
    while len(squares) < n:
        squares.append((0.0, 0.0, 0.0, 0.0))
    return squares[:n]
# EVOLVE-BLOCK-END
