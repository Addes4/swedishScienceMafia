import numpy as np
import time
from scipy.optimize import minimize


def _max_radii(centers):
    n = len(centers)
    c = np.asarray(centers, dtype=float)
    D = np.sqrt(((c[:, None, :] - c[None, :, :]) ** 2).sum(-1))
    r = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    r = np.maximum(r, 0).tolist()
    Dl = D.tolist()
    for _ in range(200):
        changed = False
        for i in range(n):
            Di = Dl[i]
            for j in range(i + 1, n):
                d = Di[j]
                if r[i] + r[j] > d:
                    s = d / (r[i] + r[j] + 1e-18)
                    r[i] *= s
                    r[j] *= s
                    changed = True
        if not changed:
            break
    return np.array(r) * (1 - 1e-12)


def _optimize(x0, n, iu, ju, maxiter=300):
    def obj(x):
        return -np.sum(x[2 * n:])

    def obj_grad(x):
        g = np.zeros_like(x)
        g[2 * n:] = -1
        return g

    m = len(iu)

    def cons(x):
        c = x[:2 * n].reshape(n, 2)
        r = x[2 * n:]
        d = np.sqrt(((c[iu] - c[ju]) ** 2).sum(1))
        pair = d - r[iu] - r[ju]
        return np.concatenate([pair, c[:, 0] - r, c[:, 1] - r, 1 - c[:, 0] - r, 1 - c[:, 1] - r])

    def cons_jac(x):
        c = x[:2 * n].reshape(n, 2)
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
        J[m + n + a, 2 * a + 1] = 1
        J[m + n + a, 2 * n + a] = -1
        J[m + 2 * n + a, 2 * a] = -1
        J[m + 2 * n + a, 2 * n + a] = -1
        J[m + 3 * n + a, 2 * a + 1] = -1
        J[m + 3 * n + a, 2 * n + a] = -1
        return J

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    res = minimize(obj, x0, jac=obj_grad, method='SLSQP', bounds=bounds,
                   constraints=[{'type': 'ineq', 'fun': cons, 'jac': cons_jac}],
                   options={'maxiter': maxiter, 'ftol': 1e-10})
    return res.x


def _init(it, n, rng):
    if it % 3 == 0:
        return rng.random((n, 2)) * 0.9 + 0.05
    elif it % 3 == 1:
        k = int(np.ceil(np.sqrt(n)))
        g = [((i + 0.5) / k, (j + 0.5) / k) for i in range(k) for j in range(k)]
        idx = rng.permutation(len(g))[:n]
        c0 = np.array(g)[idx] + rng.normal(0, 0.03, (n, 2))
        return np.clip(c0, 0.03, 0.97)
    else:
        c0 = [[0.5, 0.5]]
        c0 += [[0.5 + 0.25 * np.cos(2 * np.pi * i / 8 + 0.3), 0.5 + 0.25 * np.sin(2 * np.pi * i / 8 + 0.3)] for i in range(8)]
        c0 += [[0.5 + 0.43 * np.cos(2 * np.pi * i / (n - 9)), 0.5 + 0.43 * np.sin(2 * np.pi * i / (n - 9))] for i in range(n - 9)]
        return np.clip(np.array(c0) + rng.normal(0, 0.02, (n, 2)), 0.03, 0.97)


def _run(c0, n, iu, ju, maxiter):
    r0 = _max_radii(c0)
    d0 = np.sqrt(((c0[iu] - c0[ju]) ** 2).sum(1))
    mask = d0 < 0.5
    x0 = np.concatenate([c0.ravel(), r0])
    x = _optimize(x0, n, iu[mask], ju[mask], maxiter)
    c = np.clip(x[:2 * n].reshape(n, 2), 0, 1)
    r = _max_radii(c)
    return c, r


def solve(n=26):
    t0 = time.time()
    rng = np.random.default_rng(1)
    iu, ju = np.triu_indices(n, 1)
    best_s, best = -1, None
    it = 0
    while time.time() - t0 < 90:
        try:
            c, r = _run(_init(it, n, rng), n, iu, ju, 300)
        except Exception:
            it += 1
            continue
        s = r.sum()
        if s > best_s:
            best_s, best = s, (c.copy(), r.copy())
        it += 1

    # basin hopping from the best layout
    while time.time() - t0 < 270:
        c, r = best
        c = c.copy()
        mode = rng.integers(3)
        if mode == 0:
            c = c + rng.normal(0, rng.choice([0.01, 0.02, 0.04]), c.shape)
        elif mode == 1:
            k = rng.integers(1, 4)
            order = np.argsort(r)
            pool = order[:8]
            idx = rng.choice(pool, size=k, replace=False)
            c[idx] = rng.random((k, 2)) * 0.9 + 0.05
        else:
            i, j = rng.choice(n, 2, replace=False)
            c[[i, j]] = c[[j, i]]
            c = c + rng.normal(0, 0.01, c.shape)
        c = np.clip(c, 0.02, 0.98)
        try:
            c2, r2 = _run(c, n, iu, ju, 250)
        except Exception:
            continue
        s = r2.sum()
        if s > best_s + 1e-9:
            best_s, best = s, (c2.copy(), r2.copy())
    return best[0], best[1]
