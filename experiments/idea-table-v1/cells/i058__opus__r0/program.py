# EVOLVE-BLOCK-START
"""Contact-graph flipping tabu search over pairwise separation relations,
with an LP (sum of sides) re-solved after each move.  Seeded by a recursive
grid-subdivision dynamic program."""
import math
import random
import time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix

NEG = -1e9
OPP = np.array([1, 0, 3, 2], dtype=np.int64)


# ---------------------------------------------------------------- DP layout
def _make_conv(N):
    U, V = np.meshgrid(np.arange(N + 1), np.arange(N + 1), indexing="ij")
    T = U + V
    m = T <= N
    U, V, T = U[m], V[m], T[m]

    def conv(a, b):
        out = np.full((N + 1, N + 1), NEG)
        out[U, T] = a[U] + b[V]
        return out.max(axis=0)
    return conv


def _dp_layout(n):
    N = n
    conv = _make_conv(N)
    K = min(max(2, math.isqrt(n) + 2), 10)
    opts = [(k, b) for k in range(2, K + 1) for b in range(1, k)]
    ident = np.full(N + 1, NEG)
    ident[0] = 0.0

    def power(base, c):
        res = ident.copy()
        while c:
            if c & 1:
                res = conv(res, base)
            c >>= 1
            if c:
                base = conv(base, base)
        return res

    best = np.ones(N + 1)
    best[0] = 0.0
    for _ in range(8):
        new = best.copy()
        new[1:] = np.maximum(new[1:], 1.0)
        for k, b in opts:
            c = min(k * k - b * b, N)
            h = power(best, c)
            v = conv(b * best, h) / k
            new = np.maximum(new, v)
        new = np.maximum.accumulate(new)
        if np.allclose(new, best, atol=1e-12):
            best = new
            break
        best = new

    out = []

    def build(m, x0, y0, side, depth):
        if m <= 0:
            return
        if depth > 12 or best[m] <= 1.0 + 1e-12:
            out.append((x0, y0, side))
            return
        target = best[m]
        chosen = None
        for k, b in opts:
            c = min(k * k - b * b, N)
            h = power(best, c)
            v = conv(b * best, h) / k
            if v[m] >= target - 1e-9:
                chosen = (k, b, c)
                break
        if chosen is None:
            out.append((x0, y0, side))
            return
        k, b, c = chosen
        H = [ident.copy()]
        for _ in range(c):
            H.append(conv(H[-1], best))
        hc = H[c]
        bestm0, bv = 0, NEG
        for m0 in range(m + 1):
            val = b * best[m0] + hc[m - m0]
            if val > bv + 1e-12:
                bv, bestm0 = val, m0
        cell = side / k
        build(bestm0, x0, y0, cell * b, depth + 1)
        cells = [(a, bb) for a in range(k) for bb in range(k) if not (a < b and bb < b)][:c]
        t = m - bestm0
        alloc = [0] * c
        for j in range(c, 0, -1):
            bu, bvv = 0, NEG
            for u in range(t + 1):
                val = H[j - 1][t - u] + best[u]
                if val > bvv + 1e-12:
                    bvv, bu = val, u
            alloc[j - 1] = bu
            t -= bu
        for (a, bb), cnt in zip(cells, alloc):
            build(cnt, x0 + a * cell, y0 + bb * cell, cell, depth + 1)

    build(n, 0.0, 0.0, 1.0, 0)
    out = out[:n]
    while len(out) < n:
        out.append((1.0, 1.0, 0.0))
    return out


def _rel_from_geom(rects):
    n = len(rects)
    R = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        xi, yi, si = rects[i]
        for j in range(n):
            if i == j:
                continue
            xj, yj, sj = rects[j]
            g = [xj - (xi + si), xi - (xj + sj), yj - (yi + si), yi - (yj + sj)]
            R[i, j] = int(np.argmax(g))
    return R


def _rel_seqpair(n, rng):
    gp = list(range(n)); rng.shuffle(gp)
    gm = list(range(n)); rng.shuffle(gm)
    pp = [0] * n; pm = [0] * n
    for k, v in enumerate(gp):
        pp[v] = k
    for k, v in enumerate(gm):
        pm[v] = k
    R = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if pp[i] < pp[j] and pm[i] < pm[j]:
                R[i, j] = 0
            elif pp[i] > pp[j] and pm[i] > pm[j]:
                R[i, j] = 1
            elif pp[i] < pp[j] and pm[i] > pm[j]:
                R[i, j] = 3
            else:
                R[i, j] = 2
    return R


# ---------------------------------------------------------------- LP
class _LP:
    def __init__(self, n):
        self.n = n
        I, J = np.triu_indices(n, 1)
        self.I, self.J = I, J
        self.P = P = len(I)
        k = np.arange(n)
        self.brows = np.concatenate([P + k, P + k, P + n + k, P + n + k])
        self.bcols = np.concatenate([k, 2 * n + k, n + k, 2 * n + k])
        self.bdata = np.ones(4 * n)
        self.b_ub = np.concatenate([np.zeros(P), np.ones(2 * n)])
        self.c = np.zeros(3 * n)
        self.c[2 * n:] = -1.0

    def solve(self, R):
        n, P, I, J = self.n, self.P, self.I, self.J
        if P > 0:
            r = R[I, J]
            lo = (r == 0) | (r == 2)
            a = np.where(lo, I, J)
            b = np.where(lo, J, I)
            off = np.where(r < 2, 0, n)
            rows = np.concatenate([np.arange(P)] * 3 + [self.brows])
            cols = np.concatenate([off + a, off + b, 2 * n + a, self.bcols])
            data = np.concatenate([np.ones(P), -np.ones(P), np.ones(P), self.bdata])
        else:
            rows, cols, data = self.brows, self.bcols, self.bdata
        A = csr_matrix((data, (rows, cols)), shape=(P + 2 * n, 3 * n))
        try:
            res = linprog(self.c, A_ub=A, b_ub=self.b_ub, bounds=(0, 1), method="highs-ds")
        except Exception:
            return NEG, None, None
        if res.status != 0 or res.x is None:
            return NEG, None, None
        try:
            marg = np.asarray(res.ineqlin.marginals)[:P]
        except Exception:
            marg = np.zeros(P)
        return -res.fun, res.x, marg


# ---------------------------------------------------------------- search
def _search(n, R0, deadline, rng):
    lp = _LP(n)
    R = R0.copy()
    val, z, marg = lp.solve(R)
    bestR, bestval, bestz = R.copy(), val, z
    if n < 2:
        return bestval, bestz
    tabu = np.zeros((n, n), dtype=np.int64)
    it = 0
    last_imp = 0
    stall = 40 + 2 * n
    I, J = lp.I, lp.J
    while time.time() < deadline:
        it += 1
        cands = []
        if marg is not None and z is not None:
            bind = np.nonzero(marg < -1e-9)[0].tolist()
            if not bind:
                bind = list(range(lp.P))
            rng.shuffle(bind)
            for p in bind[:6]:
                i, j = int(I[p]), int(J[p])
                alts = [r for r in range(4) if r != R[i, j]]
                rng.shuffle(alts)
                for r in alts[:2]:
                    cands.append(("f", i, j, r))
            s = z[2 * n:]
            zeros = [i for i in range(n) if s[i] < 1e-7]
            pos = [i for i in range(n) if s[i] >= 1e-7]
            if zeros and pos and rng.random() < 0.5:
                for _ in range(2):
                    cands.append(("s", rng.choice(zeros), rng.choice(pos), rng.randrange(4)))
        if not cands:
            R = _rel_seqpair(n, rng)
            val, z, marg = lp.solve(R)
            continue
        bestc = None
        bcv = -1e18
        for cd in cands:
            if time.time() > deadline:
                break
            R2 = R.copy()
            if cd[0] == "f":
                _, i, j, r = cd
                R2[i, j] = r
                R2[j, i] = OPP[r]
                is_tabu = tabu[i, j] > it
            else:
                _, zz, q, r = cd
                row = R[q].copy()
                R2[zz, :] = row
                R2[:, zz] = OPP[row]
                R2[zz, q] = r
                R2[q, zz] = OPP[r]
                R2[zz, zz] = 0
                is_tabu = tabu[zz, q] > it
            v, zz2, mg = lp.solve(R2)
            if v <= NEG / 2:
                continue
            if is_tabu and v <= bestval + 1e-9:
                continue
            score = v + rng.random() * 1e-7
            if score > bcv:
                bcv = score
                bestc = (cd, R2, v, zz2, mg)
        if bestc is None:
            continue
        cd, R, val, z, marg = bestc
        if cd[0] == "f":
            tabu[cd[1], cd[2]] = tabu[cd[2], cd[1]] = it + rng.randint(3, 10)
        else:
            tabu[cd[1], cd[2]] = tabu[cd[2], cd[1]] = it + rng.randint(3, 10)
        if val > bestval + 1e-9:
            bestval, bestR, bestz = val, R.copy(), z
            last_imp = it
        if it - last_imp > stall:
            last_imp = it
            if rng.random() < 0.6:
                R = bestR.copy()
                for _ in range(rng.randint(2, 6)):
                    i, j = rng.sample(range(n), 2)
                    r = rng.randrange(4)
                    R[i, j] = r
                    R[j, i] = OPP[r]
            else:
                R = _rel_seqpair(n, rng)
            val, z, marg = lp.solve(R)
            tabu[:] = 0
    return bestval, bestz


def _finalize(n, z):
    x = z[:n]; y = z[n:2 * n]; s = z[2 * n:]
    cx = x + s / 2
    cy = y + s / 2
    s2 = np.maximum(s - 4e-9, 0.0)
    cx = np.clip(cx, s2 / 2, 1 - s2 / 2)
    cy = np.clip(cy, s2 / 2, 1 - s2 / 2)
    # verify, zero out offenders
    for i in range(n):
        for j in range(i + 1, n):
            if s2[i] <= 0 or s2[j] <= 0:
                continue
            h = (s2[i] + s2[j]) / 2
            if abs(cx[i] - cx[j]) < h and abs(cy[i] - cy[j]) < h:
                if s2[i] < s2[j]:
                    s2[i] = 0.0
                else:
                    s2[j] = 0.0
    out = []
    for i in range(n):
        out.append((float(min(max(cx[i], 0.0), 1.0)), float(min(max(cy[i], 0.0), 1.0)),
                    0.0, float(min(max(s2[i], 0.0), 1.0))))
    return out


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    rng = random.Random(12345 + n)
    rects = _dp_layout(n)
    dp_val = sum(r[2] for r in rects)
    R0 = _rel_from_geom(rects)
    deadline = t0 + 40.0
    val, z = _search(n, R0, deadline, rng)
    if z is None or val < dp_val - 1e-9:
        out = []
        for (x, y, s) in rects:
            s2 = max(s - 4e-9, 0.0)
            out.append((min(max(x + s / 2, 0.0), 1.0), min(max(y + s / 2, 0.0), 1.0), 0.0, s2))
        return out
    return _finalize(n, z)
# EVOLVE-BLOCK-END
