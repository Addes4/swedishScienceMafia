# EVOLVE-BLOCK-START
"""Simplex construction: A = {x in Z_{>=0}^d : sum x <= n} embedded into Z (Freiman isomorphism)."""
import math


def _counts(d, n):
    size = math.comb(n + d, d)
    sums = math.comb(2 * n + d, d)
    diffs = 0
    for i in range(0, min(d, n) + 1):
        for j in range(0, min(d - i, n) + 1):
            diffs += (math.factorial(d) // (math.factorial(i) * math.factorial(j) * math.factorial(d - i - j))
                      * math.comb(n, i) * math.comb(n, j))
    return size, sums, diffs


def _points(d, n):
    res = []

    def rec(pos, rem, cur):
        if pos == d:
            res.append(tuple(cur))
            return
        for v in range(rem + 1):
            cur.append(v)
            rec(pos + 1, rem - v, cur)
            cur.pop()

    rec(0, n, [])
    return res


def solve():
    best = None
    best_sc = -1.0
    for d in range(1, 40):
        for n in range(1, 200):
            size = math.comb(n + d, d)
            if size > 4000:
                break
            B = 2 * n + 1
            if n * B ** d > 10 ** 15:
                break
            size, sums, diffs = _counts(d, n)
            if sums < 2:
                continue
            sc = math.log(diffs) / math.log(sums) + (1 - 1 / size) / 100
            if sc > best_sc:
                best_sc = sc
                best = (d, n)
    d, n = best
    B = 2 * n + 1
    pts = _points(d, n)
    out = []
    for p in pts:
        v = 0
        for c in p:
            v = v * B + c
        out.append(v)
    return sorted(set(out))
# EVOLVE-BLOCK-END
