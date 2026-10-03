import numpy as np
import time
from scipy.optimize import minimize, linprog


def max_radii(centers):
    n = len(centers)
    I, J = np.triu_indices(n, 1)
    d = np.sqrt(((centers[I] - centers[J]) ** 2).sum(1))
    m = len(I)
    A = np.zeros((m, n))
    A[np.arange(m), I] = 1
    A[np.arange(m), J] = 1
    wall = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    wall = np.maximum(wall, 0)
    try:
        res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=[(0, w) for w in wall], method='highs')
        if res.status == 0:
            r = np.maximum(res.x, 0)
            # shrink slightly for safety
            return r * (1 - 1e-12)
    except Exception:
        pass
    radii = wall.copy()
    for _ in range(100):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                dd = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > dd:
                    s = dd / (radii[i] + radii[j] + 1e-18)
                    radii[i] *= s
                    radii[j] *= s
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0)


def _optimize(x0, n, iu, maxiter=200):
    I, J = iu
    m = len(I)
    a = np.arange(n)
    k = np.arange(m)

    def obj(v):
        return -np.sum(v[2 * n:])

    def obj_grad(v):
        g = np.zeros_like(v)
        g[2 * n:] = -1
        return g

    def cons(v):
        x = v[:n]; y = v[n:2 * n]; r = v[2 * n:]
        d = np.sqrt((x[I] - x[J]) ** 2 + (y[I] - y[J]) ** 2)
        pair = d - r[I] - r[J]
        return np.concatenate([pair, x - r, 1 - x - r, y - r, 1 - y - r])

    def cjac(v):
        x = v[:n]; y = v[n:2 * n]
        d = np.sqrt((x[I] - x[J]) ** 2 + (y[I] - y[J]) ** 2) + 1e-12
        Jm = np.zeros((m + 4 * n, 3 * n))
        dx = (x[I] - x[J]) / d
        dy = (y[I] - y[J]) / d
        Jm[k, I] = dx; Jm[k, J] = -dx
        Jm[k, n + I] = dy; Jm[k, n + J] = -dy
        Jm[k, 2 * n + I] = -1; Jm[k, 2 * n + J] = -1
        Jm[m + a, a] = 1; Jm[m + a, 2 * n + a] = -1
        Jm[m + n + a, a] = -1; Jm[m + n + a, 2 * n + a] = -1
        Jm[m + 2 * n + a, n + a] = 1; Jm[m + 2 * n + a, 2 * n + a] = -1
        Jm[m + 3 * n + a, n + a] = -1; Jm[m + 3 * n + a, 2 * n + a] = -1
        return Jm

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    res = minimize(obj, x0, jac=obj_grad, method='SLSQP', bounds=bounds,
                   constraints=[{'type': 'ineq', 'fun': cons, 'jac': cjac}],
                   options={'maxiter': maxiter, 'ftol': 1e-10})
    return res.x


def _init(rng, n, mode):
    if mode == 0:
        c = rng.random((n, 2)) * 0.9 + 0.05
    elif mode == 1:
        k = int(np.ceil(np.sqrt(n)))
        g = np.array([[(i + 0.5) / k, (j + 0.5) / k] for i in range(k) for j in range(k)])
        idx = rng.permutation(len(g))[:n]
        c = g[idx] + rng.normal(0, 0.03, (n, 2))
        c = np.clip(c, 0.02, 0.98)
    else:
        c = [[0.5, 0.5]]
        c += [[0.5 + 0.25 * np.cos(2 * np.pi * i / 8 + rng.random() * 0.2),
               0.5 + 0.25 * np.sin(2 * np.pi * i / 8)] for i in range(8)]
        c += [[0.5 + 0.43 * np.cos(2 * np.pi * i / 17), 0.5 + 0.43 * np.sin(2 * np.pi * i / 17)] for i in range(17)]
        c = np.clip(np.array(c[:n]) + rng.normal(0, 0.02, (n, 2)), 0.02, 0.98)
    return c


def _run(c, n, iu):
    r0 = max_radii(c) * 0.9
    x0 = np.concatenate([c[:, 0], c[:, 1], r0])
    v = _optimize(x0, n, iu)
    cen = np.clip(np.stack([v[:n], v[n:2 * n]], 1), 0, 1)
    rad = max_radii(cen)
    return cen, rad


def solve(n=26):
    t0 = time.time()
    rng = np.random.default_rng(1)
    iu = np.triu_indices(n, 1)
    best = None
    best_s = -1
    it = 0
    T1 = 60
    T = 230
    while time.time() - t0 < T1:
        it += 1
        try:
            cen, rad = _run(_init(rng, n, it % 3), n, iu)
        except Exception:
            continue
        s = rad.sum()
        if s > best_s:
            best_s = s
            best = (cen, rad)
    cur = best
    cur_s = best_s
    stall = 0
    while time.time() - t0 < T:
        c = cur[0].copy()
        r = cur[1]
        u = rng.random()
        if u < 0.5:
            k = rng.integers(1, 4)
            # prefer relocating small circles
            if rng.random() < 0.5:
                idx = np.argsort(r)[:k + 2]
                idx = rng.choice(idx, size=k, replace=False)
            else:
                idx = rng.choice(n, size=k, replace=False)
            c[idx] = rng.random((k, 2)) * 0.9 + 0.05
        elif u < 0.8:
            c += rng.normal(0, 0.02, c.shape)
        else:
            i, j = rng.choice(n, 2, replace=False)
            c[[i, j]] = c[[j, i]]
            c += rng.normal(0, 0.01, c.shape)
        c = np.clip(c, 0.01, 0.99)
        try:
            cen, rad = _run(c, n, iu)
        except Exception:
            continue
        s = rad.sum()
        if s > best_s:
            best_s = s
            best = (cen, rad)
        if s > cur_s - 1e-9:
            if s > cur_s + 1e-9:
                stall = 0
            cur, cur_s = (cen, rad), s
        else:
            stall += 1
        if stall > 150:
            cur, cur_s = best, best_s
            stall = 0
    return best[0], best[1]
