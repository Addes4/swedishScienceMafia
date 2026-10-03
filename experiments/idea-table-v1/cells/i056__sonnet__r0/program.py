# EVOLVE-BLOCK-START
"""Recursive grid / merged-block packing found by dynamic programming."""
import math

NEG = float("-inf")


def _plan(n):
    K = math.isqrt(max(n, 1)) + 3
    U = K * K
    F = [0.0] * (n + 1)
    cfg = [None] * (n + 1)
    H = [[NEG] * (n + 1) for _ in range(U + 1)]
    par = [[0] * (n + 1) for _ in range(U + 1)]
    for u in range(U + 1):
        H[u][0] = 0.0
    for m in range(1, n + 1):
        # primed table (no single cell holding all m)
        Hp = [NEG] * (U + 1)
        parp = [0] * (U + 1)
        for u in range(1, U + 1):
            best = Hp[u - 1]
            pj = 0
            Hprev = H[u - 1]
            for j in range(1, m):
                v = Hprev[m - j] + F[j]
                if v > best:
                    best = v
                    pj = j
            Hp[u] = best
            parp[u] = pj

        def recon(u, c):
            counts = []
            while u > 0:
                j = parp[u] if c == m else par[u][c]
                counts.append(j)
                c -= j
                u -= 1
            return counts

        bestv = 1.0
        bestc = ("single",)
        if m >= 1 and F[m - 1] > bestv:
            bestv = F[m - 1]
            bestc = ("prev",)
        if m >= 2:
            for k in range(2, math.isqrt(m) + 4):
                if k > K:
                    break
                v = Hp[k * k] / k
                if v > bestv + 1e-12:
                    bestv = v
                    bestc = ("grid", k, 0, 0)
                for a in range(2, k):
                    u = k * k - a * a
                    Hu = H[u]
                    for j in range(1, m):
                        w = Hu[m - j]
                        if w == NEG:
                            continue
                        v = (a * F[j] + w) / k
                        if v > bestv + 1e-12:
                            bestv = v
                            bestc = ("grid", k, a, j)
        F[m] = bestv
        # reconstruct counts for chosen config
        if bestc[0] == "grid":
            _, k, a, j = bestc
            if a == 0:
                counts = recon(k * k, m)
            else:
                counts = recon(k * k - a * a, m - j)
            cfg[m] = ("grid", k, a, j, counts)
        else:
            cfg[m] = bestc
        # finalize H
        for u in range(1, U + 1):
            if F[m] > Hp[u]:
                H[u][m] = F[m]
                par[u][m] = m
            else:
                H[u][m] = Hp[u]
                par[u][m] = parp[u]
    return F, cfg


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    F, cfg = _plan(n)
    cache = {}

    def build(m):
        if m in cache:
            return cache[m]
        if m == 0:
            return []
        c = cfg[m]
        if c[0] == "single":
            res = [(0.0, 0.0, 1.0)]
        elif c[0] == "prev":
            res = build(m - 1)
        else:
            _, k, a, j, counts = c
            s = 1.0 / k
            res = []
            cells = []
            for r in range(k):
                for q in range(k):
                    if a and r < a and q < a:
                        continue
                    cells.append((q, r))
            if a:
                for (x, y, sd) in build(j):
                    res.append((x * a * s, y * a * s, sd * a * s))
            for (q, r), cnt in zip(cells, counts):
                if cnt <= 0:
                    continue
                for (x, y, sd) in build(cnt):
                    res.append((q * s + x * s, r * s + y * s, sd * s))
        cache[m] = res
        return res

    sq = build(n)
    out = []
    shrink = 1.0 - 1e-9
    for (x, y, sd) in sq[:n]:
        sd2 = sd * shrink
        cx = min(1.0, max(0.0, x + sd / 2.0))
        cy = min(1.0, max(0.0, y + sd / 2.0))
        out.append((cx, cy, 0.0, min(1.0, max(0.0, sd2))))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
