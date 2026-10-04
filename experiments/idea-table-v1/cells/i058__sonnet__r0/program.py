# EVOLVE-BLOCK-START
"""Grid-merge seeds + contact-relation flipping search with LP re-solve."""
import math
import time
import random
import numpy as np
from scipy.optimize import linprog


def _baseline(n):
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq[:n]


def _place(m, ks, d):
    occ = np.zeros((m, m), dtype=bool)
    out = []
    for k in ks:
        done = False
        for r in range(m - k + 1):
            for c in range(m - k + 1):
                if not occ[r:r + k, c:c + k].any():
                    occ[r:r + k, c:c + k] = True
                    out.append((c / m, r / m, k / m))
                    done = True
                    break
            if done:
                break
        if not done:
            return None
    free = [(r, c) for r in range(m) for c in range(m) if not occ[r, c]]
    if d > len(free):
        return None
    free = free[:len(free) - d]
    for r, c in free:
        out.append((c / m, r / m, 1.0 / m))
    return out


def _seeds(n, deadline):
    res = []
    k0 = max(1, math.isqrt(n))
    for m in range(k0, k0 + 6):
        r = m * m - n
        if r <= 0:
            sq = [(c / m, rr / m, 1.0 / m) for rr in range(m) for c in range(m)]
            res.append((m * 1.0 / m * m / m if False else sum(t[2] for t in sq), sq))
            continue
        combos = []
        cnt = [0]

        def rec(k, area, red, loss, cur):
            if cnt[0] > 20000:
                return
            if k < 2:
                combos.append((loss + (r - red), list(cur), r - red))
                cnt[0] += 1
                return
            c = 0
            while True:
                a2 = area + c * k * k
                rd = red + c * (k * k - 1)
                if a2 > m * m or rd > r:
                    break
                rec(k - 1, a2, rd, loss + c * (k * k - k), cur + [k] * c)
                c += 1

        rec(m - 1, 0, 0, 0, [])
        combos.sort(key=lambda t: t[0])
        got = 0
        for loss, ks, d in combos[:60]:
            if time.time() > deadline:
                break
            sq = _place(m, ks, d)
            if sq is None or len(sq) > n:
                continue
            res.append((sum(t[2] for t in sq), sq))
            got += 1
            if got >= 2:
                break
    res.sort(key=lambda t: -t[0])
    return res


class _LP:
    def __init__(self, n):
        self.n = n
        I, J = np.triu_indices(n, 1)
        self.I, self.J = I, J
        self.P = len(I)
        self.pr = np.arange(self.P)
        self.b = np.zeros(self.P + 2 * n)
        self.b[self.P:] = 1.0
        self.c = np.zeros(3 * n)
        self.c[2 * n:] = -1.0
        base = np.zeros((2 * n, 3 * n))
        for i in range(n):
            base[i, i] = 1
            base[i, 2 * n + i] = 1
            base[n + i, n + i] = 1
            base[n + i, 2 * n + i] = 1
        self.base = base

    def solve(self, rel):
        n, P, I, J = self.n, self.P, self.I, self.J
        A = np.zeros((P + 2 * n, 3 * n))
        a = np.where((rel == 0) | (rel == 2), I, J)
        bb = np.where((rel == 0) | (rel == 2), J, I)
        off = np.where(rel < 2, 0, n)
        pr = self.pr
        A[pr, off + a] = 1.0
        A[pr, 2 * n + a] += 1.0
        A[pr, off + bb] = -1.0
        A[P:] = self.base
        try:
            r = linprog(self.c, A_ub=A, b_ub=self.b, bounds=(0, 1), method='highs')
        except Exception:
            return None
        if r.status != 0 or r.x is None:
            return None
        z = r.x
        return -r.fun, z[:n].copy(), z[n:2 * n].copy(), z[2 * n:].copy()

    def canon(self, x, y, s):
        I, J = self.I, self.J
        sl = np.stack([x[J] - (x[I] + s[I]), x[I] - (x[J] + s[J]),
                       y[J] - (y[I] + s[I]), y[I] - (y[J] + s[J])])
        return np.argmax(sl, axis=0), sl


def _valid(sq):
    m = len(sq)
    for i in range(m):
        cx, cy, _, s = sq[i]
        if s < 0 or cx - s / 2 < -1e-12 or cy - s / 2 < -1e-12 or cx + s / 2 > 1 + 1e-12 or cy + s / 2 > 1 + 1e-12:
            return False
    arr = np.array([[t[0], t[1], t[3]] for t in sq])
    for i in range(m):
        dx = np.minimum(arr[i, 0] + arr[i, 2] / 2, arr[:, 0] + arr[:, 2] / 2) - np.maximum(arr[i, 0] - arr[i, 2] / 2, arr[:, 0] - arr[:, 2] / 2)
        dy = np.minimum(arr[i, 1] + arr[i, 2] / 2, arr[:, 1] + arr[:, 2] / 2) - np.maximum(arr[i, 1] - arr[i, 2] / 2, arr[:, 1] - arr[:, 2] / 2)
        bad = (dx > 1e-12) & (dy > 1e-12)
        bad[i] = False
        if bad.any():
            return False
    return True


def solve(n):
    t0 = time.time()
    budget = 30.0
    deadline = t0 + budget
    if n <= 1:
        return [(0.5, 0.5, 0.0, 1.0)] * n
    try:
        seeds = _seeds(n, t0 + 8.0)
        lp = _LP(n)
        best = None
        for _, sq in seeds[:3]:
            sq = list(sq) + [(0.0, 0.0, 0.0)] * (n - len(sq))
            x = np.array([t[0] for t in sq])
            y = np.array([t[1] for t in sq])
            s = np.array([t[2] for t in sq])
            rel, _ = lp.canon(x, y, s)
            r = lp.solve(rel)
            if r is not None:
                rel2, _ = lp.canon(r[1], r[2], r[3])
                if best is None or r[0] > best[0]:
                    best = (r[0], r[1], r[2], r[3], rel2)
        if best is None:
            return _baseline(n)
        cur = best
        gbest = best
        rng = random.Random(1)
        stall = 0
        start = time.time()
        total = max(1e-6, deadline - start)
        while time.time() < deadline:
            frac = (time.time() - start) / total
            T = 0.02 * (1 - frac) + 0.0005
            f, x, y, s, rel = cur
            _, sl = lp.canon(x, y, s)
            curslack = sl[rel, lp.pr]
            tight = np.nonzero((curslack < 1e-7) & ((s[lp.I] > 1e-9) | (s[lp.J] > 1e-9)))[0]
            if len(tight) > 0 and rng.random() < 0.8:
                p = int(tight[rng.randrange(len(tight))])
            else:
                p = rng.randrange(lp.P)
            opts = [q for q in range(4) if q != rel[p]]
            q = opts[rng.randrange(3)]
            if rng.random() < 0.5:
                # choose the least violated alternative
                q = max(opts, key=lambda o: sl[o, p])
            nrel = rel.copy()
            nrel[p] = q
            r = lp.solve(nrel)
            if r is None:
                continue
            fn = r[0]
            if fn >= f - 1e-9 or rng.random() < math.exp((fn - f) / T):
                crel, _ = lp.canon(r[1], r[2], r[3])
                cur = (fn, r[1], r[2], r[3], crel)
                if fn > gbest[0] + 1e-9:
                    gbest = cur
                    stall = 0
            stall += 1
            if stall > 400:
                cur = gbest
                stall = 0
        f, x, y, s, _ = gbest
        out = []
        shrink = 1e-7
        for i in range(n):
            si = max(0.0, float(s[i]) - shrink)
            cx = float(x[i]) + float(s[i]) / 2
            cy = float(y[i]) + float(s[i]) / 2
            cx = min(1.0, max(0.0, cx))
            cy = min(1.0, max(0.0, cy))
            out.append((cx, cy, 0.0, si))
        if _valid(out):
            if sum(t[3] for t in out) >= sum(t[3] for t in _baseline(n)):
                return out
        return _baseline(n)
    except Exception:
        return _baseline(n)
# EVOLVE-BLOCK-END
