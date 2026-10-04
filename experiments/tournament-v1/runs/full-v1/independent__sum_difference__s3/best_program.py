import math


def _count(d, n):
    size = math.comb(n + d, d)
    s = math.comb(2 * n + d, d)
    diff = 0
    for p in range(0, d + 1):
        for q in range(0, d - p + 1):
            if p > n or q > n:
                continue
            diff += math.comb(d, p) * math.comb(d - p, q) * math.comb(n, p) * math.comb(n, q)
    return size, s, diff


def _gen(d, n):
    res = []

    def rec(i, rem, cur):
        if i == d:
            res.append(tuple(cur))
            return
        for v in range(rem + 1):
            cur.append(v)
            rec(i + 1, rem - v, cur)
            cur.pop()

    rec(0, n, [])
    return res


def solve():
    best = None
    for d in range(1, 40):
        for n in range(1, 200):
            size = math.comb(n + d, d)
            if size > 4000:
                break
            B = 2 * n + 1
            if B ** d > 4 * 10 ** 14:
                break
            size, s, diff = _count(d, n)
            if s < 2:
                continue
            sc = math.log(diff) / math.log(s) + (1 - 1 / size) / 100
            if best is None or sc > best[0]:
                best = (sc, d, n)
    _, d, n = best
    B = 2 * n + 1
    pts = _gen(d, n)
    out = []
    for p in pts:
        v = 0
        for x in reversed(p):
            v = v * B + x
        out.append(v)
    return sorted(set(out))
