import numpy as np
import time
from scipy.optimize import minimize


def _feasible_radii(centers):
    n = len(centers)
    r = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    r = np.maximum(r, 0).tolist()
    D = np.sqrt(((centers[:, None, :] - centers[None, :, :]) ** 2).sum(-1)).tolist()
    for _ in range(100):
        changed = False
        for i in range(n):
            Di = D[i]
            for j in range(i + 1, n):
                d = Di[j]
                s = r[i] + r[j]
                if s > d:
                    f = d / (s + 1e-18)
                    r[i] *= f
                    r[j] *= f
                    changed = True
        if not changed:
            break
    return np.array(r)


def solve(n=26):
    t0 = time.time()
    budget = 240.0
    rng = np.random.default_rng(1)
    iu, ju = np.triu_indices(n, 1)
    m = len(iu)
    ar = np.arange(m)
    k_ = np.arange(n)

    def obj(v):
        return -np.sum(v[2 * n:])

    gvec = np.zeros(3 * n)
    gvec[2 * n:] = -1

    def obj_grad(v):
        return gvec

    def cons(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        dx = x[iu] - x[ju]; dy = y[iu] - y[ju]
        pair = dx * dx + dy * dy - (r[iu] + r[ju]) ** 2
        return np.concatenate([pair, x - r, 1 - x - r, y - r, 1 - y - r])

    def cons_jac(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        J = np.zeros((m + 4 * n, 3 * n))
        dx = x[iu] - x[ju]; dy = y[iu] - y[ju]
        s = r[iu] + r[ju]
        J[ar, iu] = 2 * dx
        J[ar, ju] = -2 * dx
        J[ar, n + iu] = 2 * dy
        J[ar, n + ju] = -2 * dy
        J[ar, 2 * n + iu] = -2 * s
        J[ar, 2 * n + ju] = -2 * s
        J[m + k_, k_] = 1; J[m + k_, 2 * n + k_] = -1
        J[m + n + k_, k_] = -1; J[m + n + k_, 2 * n + k_] = -1
        J[m + 2 * n + k_, n + k_] = 1; J[m + 2 * n + k_, 2 * n + k_] = -1
        J[m + 3 * n + k_, n + k_] = -1; J[m + 3 * n + k_, 2 * n + k_] = -1
        return J

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    cdict = [{'type': 'ineq', 'fun': cons, 'jac': cons_jac}]

    def run(c, r0, maxiter=300):
        c = np.clip(c, 0.02, 0.98)
        v0 = np.concatenate([c[:, 0], c[:, 1], r0])
        try:
            res = minimize(obj, v0, jac=obj_grad, method='SLSQP', bounds=bounds,
                           constraints=cdict, options={'maxiter': maxiter, 'ftol': 1e-10})
        except Exception:
            return None
        v = res.x
        cc = np.clip(np.stack([v[:n], v[n:2 * n]], 1), 0, 1)
        rr = _feasible_radii(cc)
        return rr.sum(), cc, rr

    best = (-1, None, None)
    it = 0
    explore_end = 0.3 * budget
    while time.time() - t0 < explore_end:
        it += 1
        if it % 3 == 1:
            k = 5
            g = np.array([[(i + 0.5) / k, (j + 0.5) / k] for i in range(k) for j in range(k)])
            g = np.vstack([g, [[0.5, 0.5]]])[:n]
            c = g + rng.normal(0, 0.04, g.shape)
        else:
            c = rng.random((n, 2)) * 0.9 + 0.05
        r0 = np.full(n, 0.05) * (0.5 + rng.random(n))
        out = run(c, r0)
        if out and out[0] > best[0]:
            best = out

    cur = best
    while time.time() - t0 < budget:
        _, cc, rr = cur
        c = cc.copy()
        r0 = rr * 0.9
        mode = rng.integers(0, 3)
        if mode == 0:
            sig = rng.uniform(0.01, 0.06)
            c = c + rng.normal(0, sig, c.shape)
        elif mode == 1:
            k = rng.integers(1, 4)
            order = np.argsort(rr)
            pool = order[:10]
            idx = rng.choice(pool, size=k, replace=False)
            c[idx] = rng.random((k, 2)) * 0.9 + 0.05
            r0[idx] = 0.03
            c = c + rng.normal(0, 0.005, c.shape)
        else:
            i, j = rng.choice(n, 2, replace=False)
            c[[i, j]] = c[[j, i]]
            r0[[i, j]] = r0[[j, i]]
            c = c + rng.normal(0, 0.01, c.shape)
        out = run(c, r0)
        if out is None:
            continue
        if out[0] > cur[0] - 1e-9 or rng.random() < 0.02 * (out[0] > cur[0] - 0.05):
            cur = out
        if out[0] > best[0]:
            best = out
            cur = out
        elif rng.random() < 0.01:
            cur = best
    return best[1], best[2]
