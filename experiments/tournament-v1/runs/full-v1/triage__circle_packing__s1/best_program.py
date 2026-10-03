import time
import numpy as np
from scipy.optimize import minimize, linprog


def _lp_radii(centers):
    n = len(centers)
    c = np.clip(centers, 0.0, 1.0)
    iu, ju = np.triu_indices(n, 1)
    d = np.sqrt(((c[iu] - c[ju]) ** 2).sum(1))
    m = len(iu)
    A = np.zeros((m, n))
    A[np.arange(m), iu] = 1.0
    A[np.arange(m), ju] = 1.0
    wall = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    bounds = [(0, max(w, 0.0)) for w in wall]
    res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=bounds, method="highs")
    if res.status == 0:
        r = np.maximum(res.x, 0.0)
    else:
        r = np.maximum(wall * 0.0, 0.0)
    # safety shrink
    for _ in range(5):
        dd = np.sqrt(((c[iu] - c[ju]) ** 2).sum(1))
        viol = r[iu] + r[ju] - dd
        if viol.max() <= 0:
            break
        for k in np.where(viol > 0)[0]:
            s = dd[k] / (r[iu[k]] + r[ju[k]])
            r[iu[k]] *= s
            r[ju[k]] *= s
    r = np.maximum(r - 1e-12, 0.0)
    return c, r


def solve(n=26):
    t0 = time.time()
    rng = np.random.default_rng(12345)
    iu, ju = np.triu_indices(n, 1)
    m = len(iu)

    def pen(v, mu):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        dx = x[iu] - x[ju]; dy = y[iu] - y[ju]
        d = np.sqrt(dx * dx + dy * dy + 1e-12)
        viol = np.maximum(r[iu] + r[ju] - d, 0.0)
        f = -r.sum() + mu * (viol ** 2).sum()
        gx = np.zeros(n); gy = np.zeros(n); gr = -np.ones(n)
        w = 2 * mu * viol
        gr += np.bincount(iu, w, n) + np.bincount(ju, w, n)
        tx = w * (-dx / d); ty = w * (-dy / d)
        gx += np.bincount(iu, tx, n) - np.bincount(ju, tx, n)
        gy += np.bincount(iu, ty, n) - np.bincount(ju, ty, n)
        for coord, g in ((x, gx), (y, gy)):
            v1 = np.maximum(r - coord, 0.0)
            v2 = np.maximum(coord + r - 1, 0.0)
            f += mu * ((v1 ** 2).sum() + (v2 ** 2).sum())
            g += -2 * mu * v1 + 2 * mu * v2
            gr += 2 * mu * v1 + 2 * mu * v2
        return f, np.concatenate([gx, gy, gr])

    bnds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n

    cands = []
    budget = 110.0
    while time.time() - t0 < budget:
        x0 = rng.random(n); y0 = rng.random(n)
        r0 = rng.uniform(0.03, 0.1, n)
        v = np.concatenate([x0, y0, r0])
        for mu in (3, 30, 300, 3e3, 3e4, 3e5):
            res = minimize(pen, v, args=(mu,), jac=True, method="L-BFGS-B",
                           bounds=bnds, options={"maxiter": 400})
            v = res.x
        c = np.stack([v[:n], v[n:2 * n]], 1)
        cc, rr = _lp_radii(c)
        cands.append((rr.sum(), v.copy()))
    cands.sort(key=lambda t: -t[0])

    best_s = -1; best = None
    if cands:
        best_s = cands[0][0]
        c = np.stack([cands[0][1][:n], cands[0][1][n:2 * n]], 1)
        best = _lp_radii(c)

    # SLSQP polish
    def cons_f(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        d = np.sqrt((x[iu] - x[ju]) ** 2 + (y[iu] - y[ju]) ** 2 + 1e-18)
        return np.concatenate([d - r[iu] - r[ju], x - r, 1 - x - r, y - r, 1 - y - r])

    def cons_j(v):
        x = v[:n]; y = v[n:2 * n]
        dx = x[iu] - x[ju]; dy = y[iu] - y[ju]
        d = np.sqrt(dx * dx + dy * dy + 1e-18)
        J = np.zeros((m + 4 * n, 3 * n))
        k = np.arange(m)
        J[k, iu] = dx / d; J[k, ju] = -dx / d
        J[k, n + iu] = dy / d; J[k, n + ju] = -dy / d
        J[k, 2 * n + iu] = -1; J[k, 2 * n + ju] = -1
        a = np.arange(n)
        J[m + a, a] = 1; J[m + a, 2 * n + a] = -1
        J[m + n + a, a] = -1; J[m + n + a, 2 * n + a] = -1
        J[m + 2 * n + a, n + a] = 1; J[m + 2 * n + a, 2 * n + a] = -1
        J[m + 3 * n + a, n + a] = -1; J[m + 3 * n + a, 2 * n + a] = -1
        return J

    obj = lambda v: -v[2 * n:].sum()
    objg = lambda v: np.concatenate([np.zeros(2 * n), -np.ones(n)])
    for s, v in cands[:8]:
        if time.time() - t0 > 250:
            break
        try:
            res = minimize(obj, v, jac=objg, method="SLSQP", bounds=bnds,
                           constraints=[{"type": "ineq", "fun": cons_f, "jac": cons_j}],
                           options={"maxiter": 300, "ftol": 1e-12})
            vv = res.x
        except Exception:
            continue
        c = np.stack([vv[:n], vv[n:2 * n]], 1)
        cc, rr = _lp_radii(c)
        if rr.sum() > best_s:
            best_s = rr.sum(); best = (cc, rr)

    if best is None:
        c = rng.random((n, 2))
        best = _lp_radii(c)
    return best[0], best[1]
