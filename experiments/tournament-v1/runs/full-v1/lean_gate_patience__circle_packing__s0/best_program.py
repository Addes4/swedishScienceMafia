import time
import numpy as np
from scipy.optimize import minimize


def _feasible_radii(centers, radii):
    n = len(centers)
    r = np.minimum(radii, np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]]))
    r = np.maximum(r, 0.0)
    for _ in range(100):
        changed = False
        for i in range(n):
            d = np.sqrt(((centers[i] - centers) ** 2).sum(1))
            for j in range(i + 1, n):
                if r[i] + r[j] > d[j]:
                    s = d[j] / (r[i] + r[j]) * (1 - 1e-12)
                    r[i] *= s
                    r[j] *= s
                    changed = True
        if not changed:
            break
    return r


def solve(n=26):
    t0 = time.time()
    budget = 250.0
    rng = np.random.default_rng(12345)
    I, J = np.triu_indices(n, 1)
    m = len(I)
    ar = np.arange(m)

    def cons(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        dx = x[I] - x[J]; dy = y[I] - y[J]; s = r[I] + r[J]
        pair = dx * dx + dy * dy - s * s
        return np.concatenate([pair, x - r, 1 - x - r, y - r, 1 - y - r])

    def jac(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        dx = x[I] - x[J]; dy = y[I] - y[J]; s = r[I] + r[J]
        Jm = np.zeros((m + 4 * n, 3 * n))
        Jm[ar, I] = 2 * dx
        Jm[ar, J] = -2 * dx
        Jm[ar, n + I] = 2 * dy
        Jm[ar, n + J] = -2 * dy
        Jm[ar, 2 * n + I] = -2 * s
        Jm[ar, 2 * n + J] = -2 * s
        k = np.arange(n)
        Jm[m + k, k] = 1; Jm[m + k, 2 * n + k] = -1
        Jm[m + n + k, k] = -1; Jm[m + n + k, 2 * n + k] = -1
        Jm[m + 2 * n + k, n + k] = 1; Jm[m + 2 * n + k, 2 * n + k] = -1
        Jm[m + 3 * n + k, n + k] = -1; Jm[m + 3 * n + k, 2 * n + k] = -1
        return Jm

    obj = lambda v: -np.sum(v[2 * n:])
    gobj = np.concatenate([np.zeros(2 * n), -np.ones(n)])
    gfun = lambda v: gobj
    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n

    def run(c0, r0, maxiter=300):
        v0 = np.concatenate([c0[:, 0], c0[:, 1], r0])
        try:
            res = minimize(obj, v0, jac=gfun, method='SLSQP', bounds=bounds,
                           constraints=[{'type': 'ineq', 'fun': cons, 'jac': jac}],
                           options={'maxiter': maxiter, 'ftol': 1e-12})
        except Exception:
            return None, -1
        v = res.x
        c = np.stack([v[:n], v[n:2 * n], ][0:2], 1)
        r = _feasible_radii(c, v[2 * n:])
        return (c, r), r.sum()

    best = None
    best_s = -1
    cur = None
    cur_s = -1
    stagn = 0
    while time.time() - t0 < budget:
        if best is None or rng.random() < 0.2:
            mode = rng.integers(2)
            if mode == 0:
                c0 = rng.uniform(0.05, 0.95, (n, 2))
            else:
                k = int(np.ceil(np.sqrt(n)))
                g = np.array([[(i + 0.5) / k, (j + 0.5) / k] for i in range(k) for j in range(k)])
                c0 = g[rng.permutation(len(g))[:n]] + rng.normal(0, 0.03, (n, 2))
                c0 = np.clip(c0, 0.03, 0.97)
            r0 = np.full(n, 0.04)
            out, s = run(c0, r0)
            if out is not None:
                if s > best_s:
                    best_s = s; best = out
                if cur is None or s > cur_s - 0.02:
                    cur, cur_s = out, s
            continue
        if stagn > 30:
            cur, cur_s = best, best_s
            stagn = 0
        c0 = cur[0].copy()
        sig = rng.choice([0.005, 0.01, 0.03, 0.06])
        c0 = np.clip(c0 + rng.normal(0, sig, c0.shape), 0.02, 0.98)
        if rng.random() < 0.3:
            idx = np.argsort(cur[1])[:rng.integers(1, 3)]
            c0[idx] = rng.uniform(0.05, 0.95, (len(idx), 2))
        r0 = cur[1] * 0.8
        out, s = run(c0, r0)
        if out is None:
            continue
        if s > best_s + 1e-9:
            best_s = s; best = out
            stagn = 0
        else:
            stagn += 1
        if s > cur_s - 0.003 * rng.random():
            cur, cur_s = out, s
    return best[0], best[1]
