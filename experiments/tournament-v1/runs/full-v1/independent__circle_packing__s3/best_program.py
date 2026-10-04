import time
import numpy as np
from scipy.optimize import minimize, linprog


def _lp_radii(c):
    n = len(c)
    I, J = np.triu_indices(n, 1)
    d = np.linalg.norm(c[I] - c[J], axis=1)
    m = len(I)
    A = np.zeros((m, n))
    A[np.arange(m), I] = 1
    A[np.arange(m), J] = 1
    wall = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    wall = np.maximum(wall, 0)
    res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=[(0, w) for w in wall], method="highs")
    if res.status != 0:
        return None
    return np.maximum(res.x - 1e-12, 0)


def solve(n=26):
    t0 = time.time()
    budget = 230.0
    rng = np.random.default_rng(12345)
    I, J = np.triu_indices(n, 1)
    m = len(I)
    rows = np.arange(m)

    def cons(v):
        x, y, r = v[:n], v[n:2 * n], v[2 * n:]
        d = np.sqrt((x[I] - x[J]) ** 2 + (y[I] - y[J]) ** 2)
        return np.concatenate([d - r[I] - r[J], x - r, 1 - x - r, y - r, 1 - y - r])

    def jac(v):
        x, y = v[:n], v[n:2 * n]
        dx = x[I] - x[J]
        dy = y[I] - y[J]
        d = np.maximum(np.sqrt(dx ** 2 + dy ** 2), 1e-12)
        Jm = np.zeros((m + 4 * n, 3 * n))
        Jm[rows, I] = dx / d
        Jm[rows, J] = -dx / d
        Jm[rows, n + I] = dy / d
        Jm[rows, n + J] = -dy / d
        Jm[rows, 2 * n + I] = -1
        Jm[rows, 2 * n + J] = -1
        k = np.arange(n)
        Jm[m + k, k] = 1; Jm[m + k, 2 * n + k] = -1
        Jm[m + n + k, k] = -1; Jm[m + n + k, 2 * n + k] = -1
        Jm[m + 2 * n + k, n + k] = 1; Jm[m + 2 * n + k, 2 * n + k] = -1
        Jm[m + 3 * n + k, n + k] = -1; Jm[m + 3 * n + k, 2 * n + k] = -1
        return Jm

    g = np.concatenate([np.zeros(2 * n), -np.ones(n)])
    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n

    def run(c0, maxiter=300):
        r0 = np.full(n, 0.05)
        v0 = np.concatenate([c0[:, 0], c0[:, 1], r0])
        try:
            res = minimize(lambda v: -np.sum(v[2 * n:]), v0, jac=lambda v: g, method="SLSQP",
                           bounds=bounds, constraints=[{"type": "ineq", "fun": cons, "jac": jac}],
                           options={"maxiter": maxiter, "ftol": 1e-10})
        except Exception:
            return None, -1
        v = res.x
        c = np.clip(np.stack([v[:n], v[n:2 * n]], 1), 0, 1)
        r = _lp_radii(c)
        if r is None:
            return None, -1
        return c, r.sum()

    best_c, best_s = None, -1
    best_r = None

    def hexstart():
        rows_cnt = rng.choice([5, 6])
        pts = []
        per = int(np.ceil(n / rows_cnt))
        for i in range(rows_cnt):
            for j in range(per):
                off = 0.5 / per if i % 2 else 0
                pts.append([(j + 0.5) / per + off * 0.5, (i + 0.5) / rows_cnt])
        pts = np.array(pts)
        pts = pts[rng.permutation(len(pts))[:n]]
        return np.clip(pts + rng.normal(0, 0.03, pts.shape), 0.02, 0.98)

    it = 0
    while time.time() - t0 < budget:
        it += 1
        mode = it % 3
        if best_c is None or mode == 0 or it < 8:
            c0 = rng.random((n, 2)) * 0.9 + 0.05 if it % 2 else hexstart()
        else:
            c0 = best_c.copy()
            if mode == 1:
                c0 += rng.normal(0, 0.03, c0.shape)
            else:
                k = rng.integers(1, 4)
                idx = rng.choice(n, k, replace=False)
                c0[idx] = rng.random((k, 2))
                c0 += rng.normal(0, 0.005, c0.shape)
            c0 = np.clip(c0, 0.02, 0.98)
        c, s = run(c0)
        if c is not None and s > best_s:
            best_s, best_c = s, c
    if best_c is None:
        best_c = hexstart()
    r = _lp_radii(best_c)
    if r is None:
        r = np.zeros(n)
    return best_c, r
