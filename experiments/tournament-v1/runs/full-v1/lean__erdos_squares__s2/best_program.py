# EVOLVE-BLOCK-START
"""Recursive grid/merge construction, refined by LP-based local search over
pairwise separation relations (axis-aligned squares)."""
import math
import time
import random
from functools import lru_cache

import numpy as np
from scipy.optimize import linprog


@lru_cache(maxsize=None)
def _f(n):
    """Return (value, descriptor) for n squares in a unit square."""
    if n == 0:
        return 0.0, ("empty",)
    if n == 1:
        return 1.0, ("one",)
    best = (-1.0, None)
    r = math.isqrt(n)
    if r * r < n:
        r += 1
    for m in range(r, r + 7):
        for a in range(1, m):
            maxt = (m // a) ** 2
            for t in range(0, maxt + 1):
                units = m * m - t * a * a
                need = n - t
                if need < 0 or need > units:
                    continue
                val = (t * a + need) / m
                if val > best[0] + 1e-12:
                    best = (val, ("grid", m, a, t, need))
    for k in range(2, 6):
        B = k * k
        NEG = -1e18
        dp = [[NEG] * (n + 1) for _ in range(B + 1)]
        ch = [[0] * (n + 1) for _ in range(B + 1)]
        dp[0][0] = 0.0
        for j in range(1, B + 1):
            for c in range(n + 1):
                bv = NEG
                bc = 0
                for ni in range(0, min(c, n - 1) + 1):
                    p = dp[j - 1][c - ni]
                    if p <= NEG / 2:
                        continue
                    v = p + _f(ni)[0] / k
                    if v > bv:
                        bv = v
                        bc = ni
                dp[j][c] = bv
                ch[j][c] = bc
        if dp[B][n] > best[0] + 1e-12:
            alloc = []
            c = n
            for j in range(B, 0, -1):
                alloc.append(ch[j][c])
                c -= ch[j][c]
            best = (dp[B][n], ("split", k, tuple(alloc)))
    return best


def _build(n):
    val, d = _f(n)
    kind = d[0]
    if kind == "empty":
        return []
    if kind == "one":
        return [(0.5, 0.5, 1.0)]
    out = []
    if kind == "grid":
        _, m, a, t, need = d
        s = 1.0 / m
        covered = [[False] * m for _ in range(m)]
        per = m // a
        cnt = 0
        for bi in range(per):
            for bj in range(per):
                if cnt >= t:
                    break
                cnt += 1
                for x in range(a):
                    for y in range(a):
                        covered[bi * a + x][bj * a + y] = True
                out.append(((bi * a + a / 2) * s, (bj * a + a / 2) * s, a * s))
        u = 0
        for i in range(m):
            for j in range(m):
                if not covered[i][j] and u < need:
                    out.append(((i + 0.5) * s, (j + 0.5) * s, s))
                    u += 1
        return out
    _, k, alloc = d
    idx = 0
    for i in range(k):
        for j in range(k):
            ni = alloc[idx]
            idx += 1
            for (cx, cy, sd) in _build(ni):
                out.append(((i + cx) / k, (j + cy) / k, sd / k))
    return out


class _LP:
    def __init__(self, n):
        self.n = n
        I, J = np.triu_indices(n, 1)
        self.I = I
        self.J = J
        self.P = len(I)
        self.c = np.zeros(3 * n)
        self.c[2 * n:] = -1.0
        # boundary rows
        B = np.zeros((2 * n, 3 * n))
        for i in range(n):
            B[i, i] = 1
            B[i, 2 * n + i] = 1
            B[n + i, n + i] = 1
            B[n + i, 2 * n + i] = 1
        self.B = B
        self.bb = np.ones(2 * n)
        self.bounds = [(0, 1)] * (3 * n)

    def rel(self, x, y, s):
        I, J = self.I, self.J
        g0 = x[J] - (x[I] + s[I])
        g1 = x[I] - (x[J] + s[J])
        g2 = y[J] - (y[I] + s[I])
        g3 = y[I] - (y[J] + s[J])
        return np.argmax(np.stack([g0, g1, g2, g3]), axis=0)

    def solve(self, rel):
        n, P = self.n, self.P
        I, J = self.I, self.J
        a = np.where((rel == 0) | (rel == 2), I, J)
        b = np.where((rel == 0) | (rel == 2), J, I)
        off = np.where(rel < 2, 0, n)
        A = np.zeros((P, 3 * n))
        k = np.arange(P)
        A[k, off + a] += 1
        A[k, 2 * n + a] += 1
        A[k, off + b] -= 1
        Aub = np.vstack([A, self.B])
        bub = np.concatenate([np.zeros(P), self.bb])
        try:
            res = linprog(self.c, A_ub=Aub, b_ub=bub, bounds=self.bounds,
                          method="highs")
        except Exception:
            return None
        if res.status != 0 or res.x is None:
            return None
        v = res.x
        return -res.fun, v[:n].copy(), v[n:2 * n].copy(), v[2 * n:].copy()


def _refine(n, sq, budget):
    t0 = time.time()
    rng = np.random.default_rng(12345 + n)
    lp = _LP(n)
    x = np.array([c - s / 2 for c, _, s in sq])
    y = np.array([c - s / 2 for _, c, s in sq])
    s = np.array([s for _, _, s in sq])
    # fix: y uses cy
    y = np.array([cy - sd / 2 for _, cy, sd in sq])
    r = lp.solve(lp.rel(x, y, s))
    if r is None:
        return None
    cur = r
    best = r
    stagn = 0
    while time.time() - t0 < budget:
        _, cx, cy, cs = cur
        x = cx.copy()
        y = cy.copy()
        s = cs.copy()
        mode = rng.random()
        if mode < 0.5:
            k = int(rng.integers(1, 4))
            idx = rng.choice(n, size=min(k, n), replace=False)
            s[idx] = 0.0
            x[idx] = rng.random(len(idx))
            y[idx] = rng.random(len(idx))
        elif mode < 0.8:
            sig = rng.choice([0.01, 0.03, 0.08])
            x = x + rng.normal(0, sig, n)
            y = y + rng.normal(0, sig, n)
            s = s * 0.8
        else:
            k = int(rng.integers(1, 4))
            idx = rng.choice(n, size=min(k, n), replace=False)
            x[idx] += rng.normal(0, 0.15, len(idx))
            y[idx] += rng.normal(0, 0.15, len(idx))
            s[idx] *= 0.5
        r = lp.solve(lp.rel(x, y, s))
        if r is None:
            continue
        if r[0] >= cur[0] - 1e-9:
            if r[0] > cur[0] + 1e-9:
                stagn = 0
            cur = r
            if r[0] > best[0] + 1e-9:
                best = r
        else:
            stagn += 1
        if stagn > 400:
            cur = best
            stagn = 0
    return best


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    sq = _build(n)
    sq = sq[:n]
    base = sum(s for _, _, s in sq)
    out = [(min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, min(1.0, s))
           for cx, cy, s in sq]
    if 2 <= n <= 40 and len(sq) == n:
        try:
            r = _refine(n, sq, 22.0)
        except Exception:
            r = None
        if r is not None and r[0] > base + 1e-7:
            _, x, y, s = r
            out = []
            for i in range(n):
                sd = max(0.0, float(s[i]) - 2e-9)
                cx = float(x[i]) + float(s[i]) / 2
                cy = float(y[i]) + float(s[i]) / 2
                out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0,
                            min(1.0, sd)))
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out[:n]
# EVOLVE-BLOCK-END
