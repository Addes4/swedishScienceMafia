import numpy as np
import time
from scipy.optimize import minimize, linprog


def _lp_radii(centers):
    n = len(centers)
    wall = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    wall = np.maximum(wall, 0)
    I, J = np.triu_indices(n, 1)
    d = np.linalg.norm(centers[I] - centers[J], axis=1)
    m = len(I)
    A = np.zeros((m, n))
    A[np.arange(m), I] = 1
    A[np.arange(m), J] = 1
    try:
        res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=[(0, w) for w in wall], method="highs")
        if res.status == 0:
            r = res.x
        else:
            raise RuntimeError
    except Exception:
        r = wall * 0.5
    return np.maximum(r, 0)


def _fix(centers, r):
    r = r.copy()
    n = len(r)
    wall = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    r = np.minimum(r, np.maximum(wall, 0))
    for _ in range(100):
        bad = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                s = r[i] + r[j]
                if s > d:
                    f = d / s * (1 - 1e-13)
                    r[i] *= f
                    r[j] *= f
                    bad = True
        if not bad:
            break
    return np.maximum(r, 0)


def solve(n=26):
    t0 = time.time()
    budget = 230.0
    rng = np.random.default_rng(12345)
    I, J = np.triu_indices(n, 1)
    m = len(I)
    ar = np.arange(m)

    def obj(z):
        return -np.sum(z[2 * n:])

    def gobj(z):
        g = np.zeros(3 * n)
        g[2 * n:] = -1
        return g

    def cons(z):
        x = z[:n]; y = z[n:2 * n]; r = z[2 * n:]
        dx = x[I] - x[J]; dy = y[I] - y[J]; s = r[I] + r[J]
        return np.concatenate([x - r, 1 - x - r, y - r, 1 - y - r, dx * dx + dy * dy - s * s])

    def jac(z):
        x = z[:n]; y = z[n:2 * n]; r = z[2 * n:]
        dx = x[I] - x[J]; dy = y[I] - y[J]; s = r[I] + r[J]
        Jm = np.zeros((4 * n + m, 3 * n))
        k = np.arange(n)
        Jm[k, k] = 1; Jm[k, 2 * n + k] = -1
        Jm[n + k, k] = -1; Jm[n + k, 2 * n + k] = -1
        Jm[2 * n + k, n + k] = 1; Jm[2 * n + k, 2 * n + k] = -1
        Jm[3 * n + k, n + k] = -1; Jm[3 * n + k, 2 * n + k] = -1
        row = 4 * n + ar
        Jm[row, I] = 2 * dx
        Jm[row, J] = -2 * dx
        Jm[row, n + I] = 2 * dy
        Jm[row, n + J] = -2 * dy
        Jm[row, 2 * n + I] = -2 * s
        Jm[row, 2 * n + J] = -2 * s
        return Jm

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    best = [-1.0, None]

    def run(c, r0, maxiter=300):
        z0 = np.concatenate([c[:, 0], c[:, 1], r0])
        try:
            res = minimize(obj, z0, jac=gobj, bounds=bounds,
                           constraints=[{'type': 'ineq', 'fun': cons, 'jac': jac}],
                           method='SLSQP', options={'maxiter': maxiter, 'ftol': 1e-11})
        except Exception:
            return None
        z = res.x
        c2 = np.clip(np.stack([z[:n], z[n:2 * n]], 1), 0, 1)
        r = _lp_radii(c2)
        v = r.sum()
        if v > best[0]:
            best[0] = v
            best[1] = c2.copy()
        return v, c2

    def init_random():
        mode = rng.integers(3)
        if mode == 0:
            c = rng.random((n, 2))
        elif mode == 1:
            # jittered grid-ish
            k = 5
            g = [(i + 0.5) / k for i in range(k) for j in range(k)]
            g2 = [(j + 0.5) / k for i in range(k) for j in range(k)]
            c = np.stack([g, g2], 1)
            c = np.vstack([c, rng.random((n - len(c), 2))])
            c += rng.normal(0, 0.04, c.shape)
        else:
            c = [[0.5, 0.5]]
            k1 = rng.integers(5, 9)
            c += [[0.5 + 0.25 * np.cos(2 * np.pi * i / k1), 0.5 + 0.25 * np.sin(2 * np.pi * i / k1)] for i in range(k1)]
            k2 = n - 1 - k1
            c += [[0.5 + 0.43 * np.cos(2 * np.pi * i / k2), 0.5 + 0.43 * np.sin(2 * np.pi * i / k2)] for i in range(k2)]
            c = np.array(c) + rng.normal(0, 0.03, (n, 2))
        return np.clip(c, 0.02, 0.98)

    # phase 1: multi-start
    pool = []
    while time.time() - t0 < budget * 0.4:
        c = init_random()
        out = run(c, np.full(n, 0.03))
        if out:
            pool.append(out)
    # phase 2: perturbation of best
    while time.time() - t0 < budget:
        c = best[1].copy()
        mode = rng.integers(3)
        if mode == 0:
            c += rng.normal(0, 0.03, c.shape)
        elif mode == 1:
            k = rng.integers(1, 4)
            idx = rng.choice(n, k, replace=False)
            c[idx] = rng.random((k, 2))
        else:
            r = _lp_radii(c)
            k = rng.integers(1, 3)
            idx = np.argsort(r)[:k]
            c[idx] = rng.random((k, 2))
            c += rng.normal(0, 0.01, c.shape)
        c = np.clip(c, 0.01, 0.99)
        run(c, np.full(n, 0.03) if mode else _lp_radii(c) * 0.8)

    c = best[1]
    r = _lp_radii(c)
    r = _fix(c, r * (1 - 1e-12))
    return c, r
