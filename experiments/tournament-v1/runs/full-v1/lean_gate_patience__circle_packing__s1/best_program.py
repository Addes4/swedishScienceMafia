# EVOLVE-BLOCK-START
"""Multi-start SLSQP maximising sum of radii, with basin-hopping perturbations."""
import time
import numpy as np
from scipy.optimize import minimize


def _setup(n):
    I, J = np.triu_indices(n, 1)
    return I, J


def _make(n, I, J):
    m = len(I)
    ar = np.arange(n)
    pr = np.arange(m)

    def g(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        d = np.hypot(x[I] - x[J], y[I] - y[J])
        return np.concatenate([x - r, 1 - x - r, y - r, 1 - y - r,
                               d - r[I] - r[J]])

    def jac(v):
        x = v[:n]; y = v[n:2 * n]
        Jm = np.zeros((4 * n + m, 3 * n))
        Jm[ar, ar] = 1; Jm[ar, 2 * n + ar] = -1
        Jm[n + ar, ar] = -1; Jm[n + ar, 2 * n + ar] = -1
        Jm[2 * n + ar, n + ar] = 1; Jm[2 * n + ar, 2 * n + ar] = -1
        Jm[3 * n + ar, n + ar] = -1; Jm[3 * n + ar, 2 * n + ar] = -1
        dx = x[I] - x[J]; dy = y[I] - y[J]
        d = np.maximum(np.hypot(dx, dy), 1e-12)
        rows = 4 * n + pr
        Jm[rows, I] = dx / d
        Jm[rows, J] = -dx / d
        Jm[rows, n + I] = dy / d
        Jm[rows, n + J] = -dy / d
        Jm[rows, 2 * n + I] = -1
        Jm[rows, 2 * n + J] = -1
        return Jm

    return g, jac


def _fix(centers, radii):
    n = len(centers)
    c = np.clip(centers, 0, 1)
    r = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1], np.maximum(radii, 0)])
    for _ in range(100):
        ok = True
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(c[i] - c[j])
                if r[i] + r[j] > d:
                    s = d / (r[i] + r[j]) if r[i] + r[j] > 0 else 0
                    r[i] *= s; r[j] *= s
                    ok = False
        if ok:
            break
    return c, np.maximum(r - 1e-12, 0)


def solve(n=26):
    t0 = time.time()
    budget = 230.0
    rng = np.random.default_rng(1)
    I, J = _setup(n)
    g, jac = _make(n, I, J)
    cons = [{'type': 'ineq', 'fun': g, 'jac': jac}]
    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    obj = lambda v: -np.sum(v[2 * n:])
    gradv = np.concatenate([np.zeros(2 * n), -np.ones(n)])
    grad = lambda v: gradv

    def run(v0):
        try:
            res = minimize(obj, v0, jac=grad, bounds=bounds, constraints=cons,
                           method='SLSQP', options={'maxiter': 300, 'ftol': 1e-10})
        except Exception:
            return None, -1
        v = res.x
        c, r = _fix(np.column_stack([v[:n], v[n:2 * n]]), v[2 * n:])
        return (c, r), r.sum()

    best = None
    bests = -1
    it = 0
    while time.time() - t0 < budget:
        it += 1
        elapsed = time.time() - t0
        explore = elapsed < 0.25 * budget
        if best is None or (explore and it % 2 == 1) or rng.random() < 0.05:
            pts = rng.random((n, 2))
            r0 = np.full(n, 0.05)
        else:
            c, r = best
            pts = c.copy()
            mv = rng.random()
            if mv < 0.4:
                k = rng.integers(1, 4)
                # bias toward small circles
                p = 1.0 / (r + 0.02)
                p /= p.sum()
                idx = rng.choice(n, k, replace=False, p=p)
                pts[idx] = rng.random((k, 2))
                pts += rng.normal(0, 0.005, pts.shape)
            elif mv < 0.7:
                a, b = rng.choice(n, 2, replace=False)
                pts[[a, b]] = pts[[b, a]]
                pts += rng.normal(0, 0.01, pts.shape)
            else:
                pts += rng.normal(0, rng.choice([0.01, 0.03, 0.06]), pts.shape)
            pts = np.clip(pts, 0.02, 0.98)
            r0 = np.full(n, 0.03)
        v0 = np.concatenate([pts[:, 0], pts[:, 1], r0])
        out, s = run(v0)
        if out is not None and s > bests:
            best, bests = out, s
    return best[0], best[1]
# EVOLVE-BLOCK-END
