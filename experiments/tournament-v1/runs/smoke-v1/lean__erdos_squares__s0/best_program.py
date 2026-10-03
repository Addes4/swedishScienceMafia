# EVOLVE-BLOCK-START
"""Recursive grid/block DP: f(m) = best sum of sides for m squares in a unit square,
built from k x k grids whose cells (or aligned b x b blocks of cells) are recursively packed."""
import math
import time
import numpy as np


def _knap(J, T, fv):
    cap = len(fv) - 1
    s = np.arange(cap + 1)
    t = np.arange(T + 1)
    idx = t[:, None] - s[None, :]
    valid = idx >= 0
    idxc = np.clip(idx, 0, None)
    K = np.full((J + 1, T + 1), -np.inf)
    K[0, 0] = 0.0
    A = np.zeros((J + 1, T + 1), dtype=int)
    for j in range(1, J + 1):
        cand = np.where(valid, K[j - 1][idxc] + fv[None, :], -np.inf)
        K[j] = cand.max(axis=1)
        A[j] = cand.argmax(axis=1)
    return K, A


def _backtrack(A, J, T):
    out = []
    for j in range(J, 0, -1):
        s = int(A[j][T])
        out.append(s)
        T -= s
    return out


def solve(n):
    t0 = time.time()
    f = np.zeros(n + 1)
    choice = [None] * (n + 1)
    if n >= 1:
        f[1] = 1.0
        choice[1] = ('one',)
    for m in range(2, n + 1):
        f[m] = f[m - 1]
        choice[m] = ('pad',)
        if time.time() - t0 > 40:
            continue
        kmax = min(10, math.isqrt(m) + 3)
        K, A = _knap(kmax * kmax, m, f[:m])
        for k in range(2, kmax + 1):
            for b in range(1, k):
                if b == 1:
                    cs = [0]
                else:
                    cs = range(1, (k // b) ** 2 + 1)
                for c in cs:
                    J2 = k * k - c * b * b
                    if J2 < 0:
                        continue
                    if c == 0:
                        v = K[J2][m] / k
                        tb = 0
                    else:
                        vals = b * K[c][:m + 1] + K[J2][::-1]
                        tb = int(np.argmax(vals))
                        v = vals[tb] / k
                    if v > f[m] + 1e-12:
                        f[m] = v
                        choice[m] = ('grid', k, b, c, tb)

    squares = []

    def build(m, x0, y0, size):
        if m <= 0:
            return
        ch = choice[m]
        if ch[0] == 'one':
            squares.append((x0 + size / 2, y0 + size / 2, 0.0, size))
            return
        if ch[0] == 'pad':
            build(m - 1, x0, y0, size)
            return
        _, k, b, c, tb = ch
        K, A = _knap(k * k, m, f[:m])
        J2 = k * k - c * b * b
        bc = _backtrack(A, c, tb) if c > 0 else []
        cc = _backtrack(A, J2, m - tb)
        cell = size / k
        covered = [[False] * k for _ in range(k)]
        per = k // b if b > 0 else 1
        for i in range(c):
            bx = (i % per) * b
            by = (i // per) * b
            for u in range(b):
                for w in range(b):
                    covered[bx + u][by + w] = True
            build(bc[i], x0 + bx * cell, y0 + by * cell, b * cell)
        ci = 0
        for u in range(k):
            for w in range(k):
                if not covered[u][w]:
                    if ci < len(cc):
                        build(cc[ci], x0 + u * cell, y0 + w * cell, cell)
                    ci += 1

    if n >= 1:
        build(n, 0.0, 0.0, 1.0)
    res = []
    for (x, y, a, s) in squares:
        s2 = s * (1 - 1e-12)
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), 0.0, min(1.0, max(0.0, s2))))
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
