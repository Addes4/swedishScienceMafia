# EVOLVE-BLOCK-START
import time
import numpy as np
from scipy.optimize import minimize


def _feasible_radii(centers):
    n = len(centers)
    r = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    r = np.maximum(r, 0)
    for _ in range(200):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if r[i] + r[j] > d:
                    s = d / (r[i] + r[j]) if r[i] + r[j] > 0 else 0
                    r[i] *= s
                    r[j] *= s
                    changed = True
        if not changed:
            break
    return r


def _optimize(x0, n, iu, ju, maxiter=300):
    def obj(x):
        return -np.sum(x[2 * n:])

    def grad(x):
        g = np.zeros(3 * n)
        g[2 * n:] = -1
        return g

    def cons(x):
        c = x[:2 * n].reshape(n, 2)
        r = x[2 * n:]
        d = np.sqrt(((c[iu] - c[ju]) ** 2).sum(1))
        pair = d - r[iu] - r[ju]
        wall = np.concatenate([c[:, 0] - r, 1 - c[:, 0] - r, c[:, 1] - r, 1 - c[:, 1] - r])
        return np.concatenate([pair, wall])

    def cjac(x):
        c = x[:2 * n].reshape(n, 2)
        m = len(iu)
        J = np.zeros((m + 4 * n, 3 * n))
        diff = c[iu] - c[ju]
        d = np.sqrt((diff ** 2).sum(1)) + 1e-12
        u = diff / d[:, None]
        k = np.arange(m)
        J[k, 2 * iu] = u[:, 0]
        J[k, 2 * iu + 1] = u[:, 1]
        J[k, 2 * ju] = -u[:, 0]
        J[k, 2 * ju + 1] = -u[:, 1]
        J[k, 2 * n + iu] = -1
        J[k, 2 * n + ju] = -1
        a = np.arange(n)
        J[m + a, 2 * a] = 1
        J[m + a, 2 * n + a] = -1
        J[m + n + a, 2 * a] = -1
        J[m + n + a, 2 * n + a] = -1
        J[m + 2 * n + a, 2 * a + 1] = 1
        J[m + 2 * n + a, 2 * n + a] = -1
        J[m + 3 * n + a, 2 * a + 1] = -1
        J[m + 3 * n + a, 2 * n + a] = -1
        return J

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    res = minimize(obj, x0, jac=grad, method='SLSQP', bounds=bounds,
                   constraints=[{'type': 'ineq', 'fun': cons, 'jac': cjac}],
                   options={'maxiter': maxiter, 'ftol': 1e-10})
    return res.x


def _finalize(x, n, iu, ju):
    cc = np.clip(x[:2 * n].reshape(n, 2), 0, 1)
    r = x[2 * n:].copy()
    r = np.maximum(r, 0)
    r = np.minimum(r, np.minimum.reduce([cc[:, 0], cc[:, 1], 1 - cc[:, 0], 1 - cc[:, 1]]))
    d = np.sqrt(((cc[iu] - cc[ju]) ** 2).sum(1))
    for _ in range(5):
        viol = r[iu] + r[ju] - d
        if viol.max() <= 0:
            break
        for k in np.where(viol > 0)[0]:
            i, j = iu[k], ju[k]
            s = d[k] / (r[i] + r[j])
            r[i] *= s
            r[j] *= s
    if np.all(r[iu] + r[ju] <= d + 1e-12):
        return cc, r, r.sum()
    return None


def solve(n=26):
    rng = np.random.default_rng(12345)
    t0 = time.time()
    budget = 240
    phase1 = 0.4 * budget
    iu, ju = np.triu_indices(n, 1)
    best = None
    best_s = -1
    it = 0
    while time.time() - t0 < phase1:
        mode = it % 3
        if mode == 0:
            c = rng.random((n, 2)) * 0.9 + 0.05
        elif mode == 1:
            k = 6
            g = np.array([[(i + 0.5) / k, (j + 0.5) / k] for i in range(k) for j in range(k)])
            idx = rng.permutation(len(g))[:n]
            c = g[idx] + rng.normal(0, 0.03, (n, 2))
        else:
            c = [[0.5, 0.5]]
            c += [[0.5 + 0.25 * np.cos(2 * np.pi * i / 8), 0.5 + 0.25 * np.sin(2 * np.pi * i / 8)] for i in range(8)]
            c += [[0.5 + 0.43 * np.cos(2 * np.pi * i / 17), 0.5 + 0.43 * np.sin(2 * np.pi * i / 17)] for i in range(17)]
            c = np.array(c[:n]) + rng.normal(0, 0.03, (n, 2))
        c = np.clip(c, 0.03, 0.97)
        x0 = np.concatenate([c.ravel(), np.full(n, 0.05)])
        it += 1
        try:
            x = _optimize(x0, n, iu, ju)
        except Exception:
            continue
        f = _finalize(x, n, iu, ju)
        if f is not None and f[2] > best_s:
            best_s = f[2]
            best = (f[0].copy(), f[1].copy())

    # Phase 2: basin hopping around the best
    if best is not None:
        cur_c, cur_r = best[0].copy(), best[1].copy()
        cur_s = best_s
        while time.time() - t0 < budget:
            c = cur_c.copy()
            r = cur_r.copy()
            t = rng.integers(0, 3)
            if t == 0:
                c = c + rng.normal(0, rng.uniform(0.01, 0.06), c.shape)
            elif t == 1:
                k = rng.integers(1, 4)
                order = np.argsort(r)
                if rng.random() < 0.6:
                    idx = rng.choice(order[:10], size=k, replace=False)
                else:
                    idx = rng.choice(n, size=k, replace=False)
                c[idx] = rng.random((k, 2)) * 0.9 + 0.05
            else:
                i, j = rng.choice(n, size=2, replace=False)
                c[[i, j]] = c[[j, i]]
                c = c + rng.normal(0, 0.005, c.shape)
            c = np.clip(c, 0.02, 0.98)
            x0 = np.concatenate([c.ravel(), np.full(n, 0.03)])
            try:
                x = _optimize(x0, n, iu, ju)
            except Exception:
                continue
            f = _finalize(x, n, iu, ju)
            if f is not None and f[2] > cur_s + 1e-9:
                cur_c, cur_r, cur_s = f[0].copy(), f[1].copy(), f[2]
                best = (cur_c.copy(), cur_r.copy())
                best_s = cur_s

    if best is None:
        c = rng.random((n, 2)) * 0.9 + 0.05
        return c, _feasible_radii(c)
    return best
# EVOLVE-BLOCK-END
