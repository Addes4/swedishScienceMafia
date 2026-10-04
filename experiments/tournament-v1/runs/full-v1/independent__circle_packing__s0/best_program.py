import time
import numpy as np
from scipy.optimize import minimize, linprog

N_DEFAULT = 26


def _lp_radii(centers):
    n = len(centers)
    x, y = centers[:, 0], centers[:, 1]
    wall = np.minimum.reduce([x, y, 1 - x, 1 - y])
    wall = np.maximum(wall, 0)
    iu, ju = np.triu_indices(n, 1)
    d = np.hypot(x[iu] - x[ju], y[iu] - y[ju])
    m = len(iu)
    A = np.zeros((m, n))
    A[np.arange(m), iu] = 1
    A[np.arange(m), ju] = 1
    res = linprog(-np.ones(n), A_ub=A, b_ub=d,
                  bounds=[(0, w) for w in wall], method="highs")
    if res.success:
        return np.maximum(res.x - 1e-11, 0)
    return np.zeros(n)


def _make(n):
    iu, ju = np.triu_indices(n, 1)
    m = len(iu)
    ar = np.arange(m)
    idx = np.arange(n)

    def obj(z):
        return -np.sum(z[2 * n:])

    def objg(z):
        g = np.zeros(3 * n)
        g[2 * n:] = -1
        return g

    def con(z):
        x, y, r = z[:n], z[n:2 * n], z[2 * n:]
        dx = x[iu] - x[ju]
        dy = y[iu] - y[ju]
        s = r[iu] + r[ju]
        c1 = dx * dx + dy * dy - s * s
        return np.concatenate([c1, x - r, 1 - x - r, y - r, 1 - y - r])

    def conj(z):
        x, y, r = z[:n], z[n:2 * n], z[2 * n:]
        dx = x[iu] - x[ju]
        dy = y[iu] - y[ju]
        s = r[iu] + r[ju]
        J = np.zeros((m + 4 * n, 3 * n))
        J[ar, iu] = 2 * dx
        J[ar, ju] = -2 * dx
        J[ar, n + iu] = 2 * dy
        J[ar, n + ju] = -2 * dy
        J[ar, 2 * n + iu] = -2 * s
        J[ar, 2 * n + ju] = -2 * s
        o = m
        J[o + idx, idx] = 1; J[o + idx, 2 * n + idx] = -1
        o += n
        J[o + idx, idx] = -1; J[o + idx, 2 * n + idx] = -1
        o += n
        J[o + idx, n + idx] = 1; J[o + idx, 2 * n + idx] = -1
        o += n
        J[o + idx, n + idx] = -1; J[o + idx, 2 * n + idx] = -1
        return J

    return obj, objg, con, conj


def _run(z0, n, fns, maxiter=200):
    obj, objg, con, conj = fns
    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    try:
        res = minimize(obj, z0, jac=objg, method="SLSQP", bounds=bounds,
                       constraints=[{"type": "ineq", "fun": con, "jac": conj}],
                       options={"maxiter": maxiter, "ftol": 1e-12})
    except Exception:
        return None
    return res.x


def _score(z, n):
    c = np.stack([np.clip(z[:n], 0, 1), np.clip(z[n:2 * n], 0, 1)], 1)
    r = _lp_radii(c)
    return r.sum(), c, r


def _init(n, rng):
    kind = rng.integers(0, 3)
    if kind == 0:
        c = rng.random((n, 2))
    elif kind == 1:
        # perturbed hex-ish / grid layout
        rows = rng.integers(4, 7)
        pts = []
        for i in range(rows):
            k = 5 if i % 2 == 0 else 6
            k = k if rng.random() < 0.5 else 5
            for j in range(k):
                pts.append([(j + 0.5 + 0.5 * (i % 2) * rng.random()) / k, (i + 0.5) / rows])
        pts = np.array(pts)
        if len(pts) >= n:
            pts = pts[rng.permutation(len(pts))[:n]]
        else:
            pts = np.vstack([pts, rng.random((n - len(pts), 2))])
        c = pts + rng.normal(0, 0.03, pts.shape)
    else:
        k = 1 + rng.integers(0, 2)
        c = [[0.5, 0.5]] if k else []
        c = list(c)
        c += [[0.5 + 0.25 * np.cos(2 * np.pi * i / 8 + 0.3), 0.5 + 0.25 * np.sin(2 * np.pi * i / 8 + 0.3)] for i in range(8)]
        rem = n - len(c)
        c += [[0.5 + 0.43 * np.cos(2 * np.pi * i / rem), 0.5 + 0.43 * np.sin(2 * np.pi * i / rem)] for i in range(rem)]
        c = np.array(c) + rng.normal(0, 0.03, (n, 2))
    c = np.clip(c, 0.02, 0.98)
    r = np.full(n, 0.05)
    return np.concatenate([c[:, 0], c[:, 1], r])


def solve(n=26):
    t0 = time.time()
    budget = 200.0
    rng = np.random.default_rng(12345)
    fns = _make(n)
    best = (-1, None, None)
    bestz = None
    it = 0
    while time.time() - t0 < budget:
        it += 1
        if bestz is None or it % 3 == 0 and time.time() - t0 < budget * 0.4 or rng.random() < 0.3 and bestz is None:
            z0 = _init(n, rng)
        elif rng.random() < 0.3 and time.time() - t0 < budget * 0.4:
            z0 = _init(n, rng)
        else:
            z0 = bestz.copy()
            mode = rng.integers(0, 3)
            if mode == 0:
                z0[:2 * n] += rng.normal(0, 0.02, 2 * n)
            elif mode == 1:
                # relocate a couple of circles randomly
                for k in rng.choice(n, size=rng.integers(1, 4), replace=False):
                    z0[k] = rng.random(); z0[n + k] = rng.random()
                    z0[2 * n + k] = 0.02
            else:
                z0[:2 * n] += rng.normal(0, 0.005, 2 * n)
            z0[:2 * n] = np.clip(z0[:2 * n], 0.01, 0.99)
            z0[2 * n:] *= 0.8
        z = _run(z0, n, fns)
        if z is None or not np.all(np.isfinite(z)):
            continue
        s, c, r = _score(z, n)
        if s > best[0]:
            best = (s, c, r)
            bestz = np.concatenate([c[:, 0], c[:, 1], r])
    if best[1] is None:
        c = np.random.rand(n, 2)
        return c, _lp_radii(c)
    return best[1], best[2]
