import math
from math import comb


def _counts(d, n):
    size = comb(n + d, d)
    sums = comb(2 * n + d, d)
    diffs = 0
    for i in range(0, d + 1):
        ci = comb(d, i) * comb(n, i)
        if ci == 0:
            continue
        for j in range(0, d - i + 1):
            diffs += ci * comb(d - i, j) * comb(n, j)
    return size, sums, diffs


def _gen(d, n):
    pts = []

    def rec(pref, rem, k):
        if k == d:
            pts.append(tuple(pref))
            return
        for v in range(rem + 1):
            pref.append(v)
            rec(pref, rem - v, k + 1)
            pref.pop()

    rec([], n, 0)
    return pts


def solve():
    best = None
    best_sc = -1
    for d in range(1, 40):
        for n in range(1, 200):
            if comb(n + d, d) > 4000:
                break
            if (2 * n + 1) ** d > 5e14:
                break
            size, s, df = _counts(d, n)
            if size < 2:
                continue
            sc = math.log(df) / math.log(s) + (1 - 1 / size) / 100
            if sc > best_sc:
                best_sc = sc
                best = (d, n)
    d, n = best
    B = 2 * n + 1
    pts = _gen(d, n)
    res = []
    for p in pts:
        v = 0
        m = 1
        for x in p:
            v += x * m
            m *= B
        res.append(v)
    return sorted(set(res))
