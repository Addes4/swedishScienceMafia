import numpy as np
import time
from scipy.optimize import minimize, linprog


def _radii_lp(centers):
    n = len(centers)
    wall = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    wall = np.maximum(wall, 0)
    iu, ju = np.triu_indices(n, 1)
    d = np.linalg.norm(centers[iu] - centers[ju], axis=1)
    m = len(iu)
    A = np.zeros((m, n))
    A[np.arange(m), iu] = 1
    A[np.arange(m), ju] = 1
    res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=[(0, w) for w in wall], method="highs")
    if res.status == 0:
        return np.maximum(res.x, 0)
    return np.zeros(n)


def _optimize(x0, n, iu, ju):
    def obj(x):
        return -np.sum(x[2 * n:])

    def obj_g(x):
        g = np.zeros(3 * n)
        g[2 * n:] = -1
        return g

    m = len(iu)
    rows = np.arange(m)

    def cons(x):
        cx = x[:n]; cy = x[n:2 * n]; r = x[2 * n:]
        dd = np.hypot(cx[iu] - cx[ju], cy[iu] - cy[ju])
        pair = dd - r[iu] - r[ju]
        return np.concatenate([pair, cx - r, cy - r, 1 - cx - r, 1 - cy - r])

    def cons_j(x):
        cx = x[:n]; cy = x[n:2 * n]
        dx = cx[iu] - cx[ju]; dy = cy[iu] - cy[ju]
        dd = np.maximum(np.hypot(dx, dy), 1e-12)
        J = np.zeros((m + 4 * n, 3 * n))
        J[rows, iu] = dx / dd
        J[rows, ju] = -dx / dd
        J[rows, n + iu] = dy / dd
        J[rows, n + ju] = -dy / dd
        J[rows, 2 * n + iu] = -1
        J[rows, 2 * n + ju] = -1
        k = np.arange(n)
        J[m + k, k] = 1; J[m + k, 2 * n + k] = -1
        J[m + n + k, n + k] = 1; J[m + n + k, 2 * n + k] = -1
        J[m + 2 * n + k, k] = -1; J[m + 2 * n + k, 2 * n + k] = -1
        J[m + 3 * n + k, n + k] = -1; J[m + 3 * n + k, 2 * n + k] = -1
        return J

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    res = minimize(obj, x0, jac=obj_g, method="SLSQP", bounds=bounds,
                   constraints=[{"type": "ineq", "fun": cons, "jac": cons_j}],
                   options={"maxiter": 300, "ftol": 1e-11})
    return res.x


def solve(n=26):
    rng = np.random.default_rng(1)
    iu, ju = np.triu_indices(n, 1)
    start = time.time()
    budget = 200
    best = (-1, None, None)
    it = 0
    while time.time() - start < budget:
        it += 1
        if it % 3 == 0 and best[1] is not None:
            c = best[1] + rng.normal(0, 0.05, best[1].shape)
            c = np.clip(c, 0.02, 0.98)
        else:
            c = rng.random((n, 2)) * 0.9 + 0.05
        r0 = np.full(n, 0.05)
        x0 = np.concatenate([c[:, 0], c[:, 1], r0])
        try:
            x = _optimize(x0, n, iu, ju)
        except Exception:
            continue
        c = np.clip(np.stack([x[:n], x[n:2 * n]], axis=1), 0, 1)
        r = _radii_lp(c)
        s = r.sum()
        if s > best[0]:
            best = (s, c, r)
    return best[1], best[2]
