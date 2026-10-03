# EVOLVE-BLOCK-START
"""Symmetry-restricted SLSQP multistart, followed by full unconstrained refinement."""
import time
import numpy as np
from scipy.optimize import minimize


class Prob:
    """Circle packing problem with full vector v = A z + b, v = [x(n), y(n), r(n)]."""

    def __init__(self, n, A, b, lo, hi, rtype, rng):
        self.n = n
        self.A = A
        self.b = b
        self.lo = lo
        self.hi = hi
        self.rtype = rtype  # boolean mask: variable is a radius
        self.bounds = list(zip(lo, hi))
        self.c = A[2 * n:3 * n, :].sum(axis=0)
        PI, PJ = np.triu_indices(n, 1)
        self.PI, self.PJ = PI, PJ
        npair = len(PI)
        self.npair = npair
        # wall constraints (linear in v)
        W = np.zeros((4 * n, 3 * n))
        wc = np.zeros(4 * n)
        for i in range(n):
            W[4 * i, i] = 1; W[4 * i, 2 * n + i] = -1; wc[4 * i] = 0
            W[4 * i + 1, i] = -1; W[4 * i + 1, 2 * n + i] = -1; wc[4 * i + 1] = 1
            W[4 * i + 2, n + i] = 1; W[4 * i + 2, 2 * n + i] = -1; wc[4 * i + 2] = 0
            W[4 * i + 3, n + i] = -1; W[4 * i + 3, 2 * n + i] = -1; wc[4 * i + 3] = 1
        self.W = W
        self.wc = wc
        self.WA = W @ A
        self.wcz = W @ b + wc
        self.rows = np.arange(npair)
        # dedupe constraints using a random point
        self.sel_w = np.arange(4 * n)
        self.sel_p = np.arange(npair)
        z0 = self.random_z(rng)
        gw = self.WA @ z0 + self.wcz
        gp, Jp = self._pairs_full(z0)
        G = np.concatenate([gw, gp])
        J = np.vstack([self.WA, Jp])
        key = np.round(np.hstack([G[:, None], J]), 9)
        # also drop trivially constant rows (zero gradient)
        _, idx = np.unique(key, axis=0, return_index=True)
        idx = np.sort(idx)
        nz_grad = np.abs(J[idx]).sum(axis=1) > 0
        idx = idx[nz_grad]
        self.sel_w = idx[idx < 4 * n]
        self.sel_p = idx[idx >= 4 * n] - 4 * n
        self.WAs = self.WA[self.sel_w]
        self.wczs = self.wcz[self.sel_w]
        self.PIs = PI[self.sel_p]
        self.PJs = PJ[self.sel_p]
        self._cache_z = None

    def random_z(self, rng):
        z = rng.uniform(self.lo, self.hi)
        z[self.rtype] = rng.uniform(0.01, 0.06, self.rtype.sum())
        return z

    def _pairs_full(self, z, PI=None, PJ=None):
        n = self.n
        if PI is None:
            PI, PJ = self.PI, self.PJ
        v = self.A @ z + self.b
        x, y, r = v[:n], v[n:2 * n], v[2 * n:]
        dx = x[PI] - x[PJ]
        dy = y[PI] - y[PJ]
        rs = r[PI] + r[PJ]
        g = dx * dx + dy * dy - rs * rs
        m = len(PI)
        Jv = np.zeros((m, 3 * n))
        rows = np.arange(m)
        np.add.at(Jv, (rows, PI), 2 * dx)
        np.add.at(Jv, (rows, PJ), -2 * dx)
        np.add.at(Jv, (rows, n + PI), 2 * dy)
        np.add.at(Jv, (rows, n + PJ), -2 * dy)
        np.add.at(Jv, (rows, 2 * n + PI), -2 * rs)
        np.add.at(Jv, (rows, 2 * n + PJ), -2 * rs)
        return g, Jv @ self.A

    def _eval(self, z):
        if self._cache_z is not None and np.array_equal(z, self._cache_z):
            return
        gp, Jp = self._pairs_full(z, self.PIs, self.PJs)
        gw = self.WAs @ z + self.wczs
        self._g = np.concatenate([gw, gp])
        self._J = np.vstack([self.WAs, Jp])
        self._cache_z = z.copy()

    def g(self, z):
        self._eval(z)
        return self._g

    def jac(self, z):
        self._eval(z)
        return self._J

    def solve(self, z0, maxiter=400):
        cons = {'type': 'ineq', 'fun': self.g, 'jac': self.jac}
        c = self.c
        try:
            res = minimize(lambda z: -c @ z, z0, jac=lambda z: -c,
                           bounds=self.bounds, constraints=[cons], method='SLSQP',
                           options={'maxiter': maxiter, 'ftol': 1e-12})
            z = res.x
        except Exception:
            z = z0
        return z

    def full(self, z):
        v = self.A @ z + self.b
        n = self.n
        return np.stack([v[:n], v[n:2 * n]], axis=1), v[2 * n:].copy()


def build(n, kind, m, rng):
    if kind == 'full':
        A = np.eye(3 * n)
        b = np.zeros(3 * n)
        lo = np.zeros(3 * n)
        hi = np.concatenate([np.ones(2 * n), 0.5 * np.ones(n)])
        rtype = np.zeros(3 * n, bool); rtype[2 * n:] = True
        return Prob(n, A, b, lo, hi, rtype, rng)
    k = (n - m) // 2
    nz = 3 * k + 2 * m
    A = np.zeros((3 * n, nz))
    b = np.zeros(3 * n)
    lo = np.zeros(nz)
    hi = np.ones(nz)
    rtype = np.zeros(nz, bool)
    ci = 0
    for p in range(k):
        zx, zy, zr = 3 * p, 3 * p + 1, 3 * p + 2
        hi[zr] = 0.5; rtype[zr] = True
        a, s = ci, ci + 1
        ci += 2
        A[a, zx] = 1; A[n + a, zy] = 1; A[2 * n + a, zr] = 1
        A[2 * n + s, zr] = 1
        if kind == 'vert':
            hi[zx] = 0.5
            A[s, zx] = -1; b[s] = 1
            A[n + s, zy] = 1
        else:  # diag
            A[s, zy] = 1
            A[n + s, zx] = 1
    for q in range(m):
        zt, zr = 3 * k + 2 * q, 3 * k + 2 * q + 1
        hi[zr] = 0.5; rtype[zr] = True
        a = ci
        ci += 1
        A[2 * n + a, zr] = 1
        if kind == 'vert':
            b[a] = 0.5
            A[n + a, zt] = 1
        else:
            A[a, zt] = 1
            A[n + a, zt] = 1
    return Prob(n, A, b, lo, hi, rtype, rng)


def repair(c, r):
    c = np.clip(np.asarray(c, float), 0.0, 1.0)
    r = np.asarray(r, float).copy()
    r = np.minimum(r, np.min([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]], axis=0))
    r = np.maximum(r, 0.0)
    n = len(r)
    d = np.sqrt(((c[:, None, :] - c[None, :, :]) ** 2).sum(-1))
    for _ in range(200):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                s = r[i] + r[j]
                if s > d[i, j] and s > 0:
                    sc = d[i, j] / s * (1 - 1e-13)
                    r[i] *= sc
                    r[j] *= sc
                    changed = True
        if not changed:
            break
    return np.maximum(r, 0.0)


def solve(n=26):
    t0 = time.time()
    T_SYM = 140.0
    T_END = 270.0
    rng = np.random.default_rng(12345)

    configs = []
    for kind in ('vert', 'diag'):
        for m in (0, 2, 4, 6):
            if (n - m) % 2 == 0 and n - m >= 0:
                try:
                    configs.append((kind, m, build(n, kind, m, rng)))
                except Exception:
                    pass

    sym_results = []  # (score, centers, radii)
    best = (-1.0, None, None)

    def consider(c, r):
        nonlocal best
        rr = repair(c, r)
        s = rr.sum()
        if s > best[0]:
            best = (s, c.copy(), rr.copy())
        return s, rr

    it = 0
    while time.time() - t0 < T_SYM and configs:
        kind, m, P = configs[it % len(configs)]
        it += 1
        z0 = P.random_z(rng)
        z = P.solve(z0)
        c, r = P.full(z)
        s, rr = consider(c, r)
        sym_results.append((s, c, rr))

    # full refinement
    F = build(n, 'full', 0, rng)

    def to_z(c, r):
        return np.concatenate([c[:, 0], c[:, 1], r])

    sym_results.sort(key=lambda t: -t[0])
    tops = []
    for s, c, r in sym_results:
        if all(abs(s - t[0]) > 1e-6 for t in tops):
            tops.append((s, c, r))
        if len(tops) >= 10:
            break

    if best[1] is None:
        z = F.solve(F.random_z(rng))
        c, r = F.full(z)
        consider(c, r)

    for s, c, r in tops:
        if time.time() - t0 > T_END:
            break
        z = F.solve(to_z(c, r))
        cc, rr = F.full(z)
        consider(cc, rr)

    # basin hopping on full problem
    while time.time() - t0 < T_END and best[1] is not None:
        c = best[1].copy()
        r = best[2].copy()
        sig = rng.choice([0.01, 0.03, 0.06])
        if rng.random() < 0.5:
            mask = rng.random(n) < 0.3
            c[mask] += rng.normal(0, sig, (mask.sum(), 2))
        else:
            c += rng.normal(0, sig * 0.5, c.shape)
        c = np.clip(c, 0.01, 0.99)
        r = r * 0.9
        z = F.solve(to_z(c, r))
        cc, rr = F.full(z)
        consider(cc, rr)

    centers = np.clip(best[1], 0.0, 1.0)
    radii = repair(centers, best[2])
    return centers, radii
# EVOLVE-BLOCK-END
