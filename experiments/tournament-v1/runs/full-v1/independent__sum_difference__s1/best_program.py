import math
import itertools


def _counts(d, n):
    s = math.comb(2 * n + d, d)
    df = 0
    for i in range(d + 1):
        for j in range(d - i + 1):
            df += (math.factorial(d) // (math.factorial(i) * math.factorial(j) *
                                         math.factorial(d - i - j))) * math.comb(n, i) * math.comb(n, j)
    return df, s


def _gen(d, n):
    pts = []

    def rec(pos, rem, cur):
        if pos == d:
            pts.append(cur)
            return
        for v in range(rem + 1):
            rec(pos + 1, rem - v, cur + [v])

    rec(0, n, [])
    return pts


def solve():
    best = None
    bs = -1
    for d in range(1, 40):
        for n in range(1, 200):
            size = math.comb(n + d, d)
            if size > 4000:
                break
            B = 2 * n + 1
            if B ** d > 4e14:
                break
            df, s = _counts(d, n)
            sc = math.log(df) / math.log(s) + (1 - 1 / size) / 100
            if sc > bs:
                bs = sc
                best = (d, n)
    d, n = best
    B = 2 * n + 1
    pts = _gen(d, n)
    res = []
    for p in pts:
        v = 0
        for x in reversed(p):
            v = v * B + x
        res.append(v)
    return sorted(set(res))
