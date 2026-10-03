# EVOLVE-BLOCK-START
import math
import time


def _two_value(m, n1, s1, n2, s2):
    if s1 < s2:
        n1, s1, n2, s2 = n2, s2, n1, s1
    t1 = min(n1, m)
    t2 = min(n2, m - t1)
    return t1 * s1 + t2 * s2


def solve(n):
    t0 = time.time()
    budget = 40.0
    best = [0.0] * (n + 1)
    rec = [None] * (n + 1)
    for m in range(1, n + 1):
        bv, br = best[m - 1], ('pad',)
        # grids
        k0 = math.isqrt(m)
        for k in {max(1, k0), k0 + 1}:
            v = min(m, k * k) / k
            if v > bv + 1e-12:
                bv, br = v, ('grid', k)
        # L-strip recursion
        k = 2
        while 2 * k - 1 <= m:
            v = (2 * k - 1) / k + (k - 1) / k * best[m - (2 * k - 1)]
            if v > bv + 1e-12:
                bv, br = v, ('L', k)
            k += 1
        # two grids side by side
        if time.time() - t0 < budget:
            pairs = [(a, b) for a in range(1, m + 1) for b in range(1, m // a + 1)]
            if len(pairs) ** 2 <= 400000 or m == n:
                for (a, b) in pairs:
                    if time.time() - t0 > budget:
                        break
                    for (c, d) in pairs:
                        ws = (a / b, 1 - c / d, a / (a + c), a / d, 1 - c / b, 0.0, 1.0)
                        for w in ws:
                            if w < 0 or w > 1:
                                continue
                            s1 = min(w / a, 1.0 / b)
                            s2 = min((1 - w) / c, 1.0 / d)
                            v = _two_value(m, a * b, s1, c * d, s2)
                            if v > bv + 1e-12:
                                bv, br = v, ('two', a, b, c, d, w)
        best[m], rec[m] = bv, br

    def build(m, ox, oy, sc):
        out = []
        while m > 0 and rec[m][0] == 'pad':
            m -= 1
        if m <= 0:
            return out
        r = rec[m]
        if r[0] == 'grid':
            k = r[1]
            s = 1.0 / k
            sq = [((i + 0.5) * s, (j + 0.5) * s, s) for i in range(k) for j in range(k)]
            sq = sq[:m]
            out = [(ox + x * sc, oy + y * sc, s * sc) for x, y, s in sq]
        elif r[0] == 'L':
            k = r[1]
            s = 1.0 / k
            for i in range(k):
                out.append((ox + (i + 0.5) * s * sc, oy + (k - 0.5) * s * sc, s * sc))
            for j in range(k - 1):
                out.append((ox + (k - 0.5) * s * sc, oy + (j + 0.5) * s * sc, s * sc))
            out += build(m - (2 * k - 1), ox, oy, sc * (k - 1) / k)
        elif r[0] == 'two':
            _, a, b, c, d, w = r
            s1 = min(w / a, 1.0 / b)
            s2 = min((1 - w) / c, 1.0 / d)
            sq = []
            for i in range(a):
                for j in range(b):
                    sq.append(((i + 0.5) * s1, (j + 0.5) * s1, s1))
            for i in range(c):
                for j in range(d):
                    sq.append((w + (i + 0.5) * s2, (j + 0.5) * s2, s2))
            sq.sort(key=lambda t: -t[2])
            sq = sq[:m]
            out = [(ox + x * sc, oy + y * sc, s * sc) for x, y, s in sq]
        return out

    sqs = build(n, 0.0, 0.0, 1.0)
    res = []
    for x, y, s in sqs[:n]:
        if s <= 0:
            continue
        s2 = s * (1 - 1e-9)
        res.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), 0.0, max(s2, 0.0)))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
