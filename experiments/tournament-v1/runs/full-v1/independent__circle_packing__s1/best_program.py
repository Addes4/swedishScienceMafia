import numpy as np
import time
from scipy.optimize import minimize, linprog


def _lp_radii(centers):
    n = len(centers)
    wall = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    wall = np.maximum(wall, 0)
    I, J = np.triu_indices(n, 1)
    d = np.hypot(centers[I, 0] - centers[J, 0], centers[I, 1] - centers[J, 1])
    A = np.zeros((len(I), n))
    A[np.arange(len(I)), I] = 1
    A[np.arange(len(I)), J] = 1
    res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=[(0, w) for w in wall], method="highs")
    if res.status == 0:
        r = np.maximum(res.x, 0)
    else:
        r = np.zeros(n)
    r = r * (1 - 1e-12)
    return r


def _optimize(x0, n, I, J, maxiter=300):
    m = len(I)
    k = np.arange(m)

    def obj(v):
        return -np.sum(v[2 * n:])

    def obj_jac(v):
        g = np.zeros(3 * n)
        g[2 * n:] = -1
        return g

    def cons(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        c1 = (x[I] - x[J]) ** 2 + (y[I] - y[J]) ** 2 - (r[I] + r[J]) ** 2
        return np.concatenate([c1, x - r, 1 - x - r, y - r, 1 - y - r])

    def cons_jac(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        Jm = np.zeros((m + 4 * n, 3 * n))
        dx = 2 * (x[I] - x[J]); dy = 2 * (y[I] - y[J]); dr = -2 * (r[I] + r[J])
        Jm[k, I] = dx; Jm[k, J] = -dx
        Jm[k, n + I] = dy; Jm[k, n + J] = -dy
        Jm[k, 2 * n + I] = dr; Jm[k, 2 * n + J] = dr
        e = np.arange(n)
        o = m
        Jm[o + e, e] = 1; Jm[o + e, 2 * n + e] = -1
        o += n
        Jm[o + e, e] = -1; Jm[o + e, 2 * n + e] = -1
        o += n
        Jm[o + e, n + e] = 1; Jm[o + e, 2 * n + e] = -1
        o += n
        Jm[o + e, n + e] = -1; Jm[o + e, 2 * n + e] = -1
        return Jm

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    res = minimize(obj, x0, jac=obj_jac, bounds=bounds,
                   constraints=[{"type": "ineq", "fun": cons, "jac": cons_jac}],
                   method="SLSQP", options={"maxiter": maxiter, "ftol": 1e-11})
    return res.x


def _init(n, rng):
    t = rng.random()
    if t < 0.4:
        c = rng.random((n, 2)) * 0.9 + 0.05
    elif t < 0.8:
        g = 5
        pts = [((i + 0.5) / g, (j + 0.5) / g) for i in range(g) for j in range(g)]
        pts.append((0.5, 0.5))
        c = np.array(pts[:n]) + rng.normal(0, 0.04, (n, 2))
    else:
        # staggered rows
        rows = [5, 5, 6, 5, 5]
        pts = []
        for ri, cnt in enumerate(rows):
            for q in range(cnt):
                pts.append(((q + 0.5 + (0.25 if ri % 2 else -0.0)) / cnt if cnt else 0.5, (ri + 0.5) / len(rows)))
        c = np.array(pts[:n])
        while len(c) < n:
            c = np.vstack([c, rng.random(2)])
        c = c + rng.normal(0, 0.04, c.shape)
    c = np.clip(c, 0.03, 0.97)
    r = np.full(n, 0.04) * (0.5 + rng.random(n))
    return np.concatenate([c[:, 0], c[:, 1], r])


def solve(n=26):
    t0 = time.time()
    budget = 230
    rng = np.random.default_rng(12345)
    I, J = np.triu_indices(n, 1)
    best_s = -1
    best = None
    best_v = None

    def evaluate(v):
        c = np.column_stack([np.clip(v[:n], 0, 1), np.clip(v[n:2 * n], 0, 1)])
        r = _lp_radii(c)
        return c, r, r.sum()

    it = 0
    while time.time() - t0 < budget:
        it += 1
        elapsed = time.time() - t0
        try:
            if best_v is None or elapsed < budget * 0.35 or rng.random() < 0.25:
                x0 = _init(n, rng)
            else:
                x0 = best_v.copy()
                mode = rng.random()
                if mode < 0.5:
                    s = rng.choice([0.01, 0.03, 0.06])
                    x0[:2 * n] += rng.normal(0, s, 2 * n)
                else:
                    # relocate a few circles
                    kk = rng.integers(1, 4)
                    idx = rng.choice(n, kk, replace=False)
                    x0[idx] = rng.random(kk) * 0.9 + 0.05
                    x0[n + idx] = rng.random(kk) * 0.9 + 0.05
                    x0[2 * n + idx] = 0.02
                x0[:2 * n] = np.clip(x0[:2 * n], 0.02, 0.98)
                x0[2 * n:] = np.clip(x0[2 * n:] * 0.9, 0.005, 0.5)
            v = _optimize(x0, n, I, J)
            c, r, s = evaluate(v)
            if s > best_s:
                best_s, best, best_v = s, (c, r), v.copy()
                best_v[2 * n:] = r
        except Exception:
            continue
    if best is None:
        c = rng.random((n, 2))
        return c, _lp_radii(c)
    return best[0], best[1]
