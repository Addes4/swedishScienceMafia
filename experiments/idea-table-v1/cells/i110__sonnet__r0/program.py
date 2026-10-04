# EVOLVE-BLOCK-START
"""Guillotine DP over integer tilings of a k x k board (k up to ~sqrt(n)+4)."""
import math
import numpy as np


def solve(n):
    K = min(max(math.isqrt(n) + 4, 2), 16)
    N = n
    F = {}

    def get(w, h):
        return F[(w, h)] if w >= h else F[(h, w)]

    def conv(A, B):
        res = np.maximum(A, B)  # one part empty
        for m1 in range(1, N + 1):
            if A[m1] == 0:
                continue
            cand = A[m1] + B[:N + 1 - m1]
            np.maximum(res[m1:], cand, out=res[m1:])
        return res

    for w in range(1, K + 1):
        for h in range(1, w + 1):
            best = np.zeros(N + 1, dtype=np.int64)
            if w == h:
                best[1:] = w
            for a in range(1, w // 2 + 1):
                r = conv(get(a, h), get(w - a, h))
                best = np.maximum(best, r)
            for b in range(1, h // 2 + 1):
                r = conv(get(w, b), get(w, h - b))
                best = np.maximum(best, r)
            F[(w, h)] = best

    bestk, bestv = 1, -1.0
    for k in range(1, K + 1):
        v = get(k, k)[N] / k
        if v > bestv + 1e-12:
            bestv, bestk = v, k
    k = bestk

    out = []

    def rec(x, y, w, h, m):
        val = int(get(w, h)[m])
        if val == 0:
            return
        if w == h and m >= 1 and val == w:
            out.append((x, y, w))
            return
        for a in range(1, w // 2 + 1):
            A = get(a, h)
            B = get(w - a, h)
            for m1 in range(0, m + 1):
                if int(A[m1]) + int(B[m - m1]) == val:
                    rec(x, y, a, h, m1)
                    rec(x + a, y, w - a, h, m - m1)
                    return
        for b in range(1, h // 2 + 1):
            A = get(w, b)
            B = get(w, h - b)
            for m1 in range(0, m + 1):
                if int(A[m1]) + int(B[m - m1]) == val:
                    rec(x, y, w, b, m1)
                    rec(x, y + b, w, h - b, m - m1)
                    return

    rec(0, 0, k, k, N)
    res = []
    for (x, y, s) in out:
        res.append(((x + s / 2.0) / k, (y + s / 2.0) / k, 0.0, s / k))
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
