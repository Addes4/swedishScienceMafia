# EVOLVE-BLOCK-START
"""Recursive grid / L-shape / two-grid constructions for squares in a square."""
import math
import time


def _two_grid(n, tlimit=20.0):
    t0 = time.time()
    best = (-1.0, None)
    pairs = []
    for a in range(1, n + 1):
        for b in range(1, n // a + 1):
            pairs.append((a, b))
    for (a, b) in pairs:
        if time.time() - t0 > tlimit:
            break
        for (c, d) in pairs:
            if a * b + c * d < n:
                continue
            ws = (a / b, 1 - c / d, a / (a + c), a / d, 1 - c / b)
            for w in ws:
                if not (0 < w < 1):
                    continue
                s1 = min(w / a, 1.0 / b)
                s2 = min((1 - w) / c, 1.0 / d)
                if s1 >= s2:
                    n1 = min(n, a * b)
                    n2 = min(n - n1, c * d)
                else:
                    n2 = min(n, c * d)
                    n1 = min(n - n2, a * b)
                v = n1 * s1 + n2 * s2
                if v > best[0] + 1e-12:
                    best = (v, (a, b, c, d, w, s1, s2, n1, n2))
    return best


def _build_two_grid(p):
    a, b, c, d, w, s1, s2, n1, n2 = p
    out = []
    cnt = 0
    for i in range(a):
        for j in range(b):
            if cnt < n1:
                out.append(((i + 0.5) * s1, (j + 0.5) * s1, s1))
                cnt += 1
    cnt = 0
    for i in range(c):
        for j in range(d):
            if cnt < n2:
                out.append((w + (i + 0.5) * s2, (j + 0.5) * s2, s2))
                cnt += 1
    return out


def _solve_rec(n):
    NEG = -1e18
    g = [0.0] * (n + 1)
    struct = [None] * (n + 1)
    if n >= 60 and n < 150:
        K = 4
    elif n < 60:
        K = 6
    elif n < 400:
        K = 3
    else:
        K = 2
    ks = list(range(2, K + 1))
    dp = {}
    for k in ks:
        tab = []
        row0 = [(NEG, None)] * (n + 1)
        row0[0] = (0.0, ())
        tab.append(row0)
        for c in range(1, k * k + 1):
            tab.append([(NEG, None)] * (n + 1))
        dp[k] = tab

    for m in range(1, n + 1):
        # pass 1: exclude x = m
        for k in ks:
            tab = dp[k]
            for c in range(1, k * k + 1):
                prev = tab[c - 1]
                bv, ba = NEG, None
                for x in range(0, m):
                    pv, pa = prev[m - x]
                    if pa is None:
                        continue
                    v = pv + g[x] / k
                    if v > bv + 1e-12:
                        bv = v
                        ba = (x,) + pa
                tab[c][m] = (bv, ba)
        bestv, bests = NEG, None
        if m == 1:
            bestv, bests = 1.0, ('one',)
        for k in ks:
            v, a = dp[k][k * k][m]
            if a is not None and v > bestv + 1e-12:
                bestv, bests = v, ('alloc', k, a)
        # L shapes
        for k in range(2, math.isqrt(m) + 4):
            for mb in range(1, k):
                if k * k - mb * mb < m - 1:
                    continue
                v = mb / k + (m - 1) / k
                if v > bestv + 1e-12:
                    bestv, bests = v, ('L', k, mb)
        g[m] = bestv
        struct[m] = bests
        # pass 2: include x = m
        for k in ks:
            tab = dp[k]
            for c in range(1, k * k + 1):
                prev = tab[c - 1]
                bv, ba = NEG, None
                for x in range(0, m + 1):
                    pv, pa = prev[m - x]
                    if pa is None:
                        continue
                    v = pv + g[x] / k
                    if v > bv + 1e-12:
                        bv = v
                        ba = (x,) + pa
                tab[c][m] = (bv, ba)

    memo = {}

    def build(m):
        if m <= 0:
            return []
        if m in memo:
            return memo[m]
        st = struct[m]
        out = []
        if st[0] == 'one':
            out = [(0.5, 0.5, 1.0)]
        elif st[0] == 'alloc':
            k = st[1]
            al = sorted(st[2], reverse=True)
            for idx, x in enumerate(al):
                if x <= 0:
                    continue
                i = idx % k
                j = idx // k
                for (cx, cy, s) in build(x):
                    out.append(((i + cx) / k, (j + cy) / k, s / k))
        else:
            k, mb = st[1], st[2]
            out.append((mb / (2.0 * k), mb / (2.0 * k), mb / k))
            need = m - 1
            for i in range(k):
                for j in range(k):
                    if need <= 0:
                        break
                    if i < mb and j < mb:
                        continue
                    out.append(((i + 0.5) / k, (j + 0.5) / k, 1.0 / k))
                    need -= 1
        memo[m] = out
        return out

    return g[n], build(n)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    val, sq = _solve_rec(n)
    sq = list(sq)
    try:
        tv, tp = _two_grid(n)
        if tp is not None and tv > val + 1e-12:
            sq = _build_two_grid(tp)
    except Exception:
        pass
    shrink = 1.0 - 1e-10
    res = []
    for (cx, cy, s) in sq[:n]:
        s2 = max(0.0, min(1.0, s * shrink))
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, s2))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
