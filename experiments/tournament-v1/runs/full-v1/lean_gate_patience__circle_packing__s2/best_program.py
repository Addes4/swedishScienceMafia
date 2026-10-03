import numpy as np
import time
from scipy.optimize import minimize


def _feasible_radii(c):
    n = len(c)
    r = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    r = np.maximum(r, 0)
    for _ in range(200):
        ch = False
        for i in range(n):
            d = np.hypot(c[i + 1:, 0] - c[i, 0], c[i + 1:, 1] - c[i, 1])
            for k in range(len(d)):
                j = i + 1 + k
                if r[i] + r[j] > d[k] + 1e-15:
                    s = d[k] / (r[i] + r[j])
                    r[i] *= s
                    r[j] *= s
                    ch = True
        if not ch:
            break
    return r


def _opt_pairs(x0, n, i_idx, j_idx, maxiter):
    m = len(i_idx)

    def obj(x):
        return -np.sum(x[2 * n:])

    def obj_g(x):
        g = np.zeros_like(x)
        g[2 * n:] = -1
        return g

    def cons(x):
        c = x[:2 * n].reshape(n, 2)
        r = x[2 * n:]
        d = c[i_idx] - c[j_idx]
        dist = np.sqrt((d ** 2).sum(1) + 1e-18)
        pair = dist - r[i_idx] - r[j_idx]
        wall = np.concatenate([c[:, 0] - r, 1 - c[:, 0] - r, c[:, 1] - r, 1 - c[:, 1] - r])
        return np.concatenate([pair, wall])

    a = np.arange(n)
    k = np.arange(m)

    def cons_j(x):
        c = x[:2 * n].reshape(n, 2)
        d = c[i_idx] - c[j_idx]
        dist = np.sqrt((d ** 2).sum(1) + 1e-18)
        u = d / dist[:, None]
        J = np.zeros((m + 4 * n, 3 * n))
        J[k, 2 * i_idx] = u[:, 0]
        J[k, 2 * i_idx + 1] = u[:, 1]
        J[k, 2 * j_idx] = -u[:, 0]
        J[k, 2 * j_idx + 1] = -u[:, 1]
        J[k, 2 * n + i_idx] = -1
        J[k, 2 * n + j_idx] = -1
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
    res = minimize(obj, x0, jac=obj_g, method='SLSQP', bounds=bounds,
                   constraints=[{'type': 'ineq', 'fun': cons, 'jac': cons_j}],
                   options={'maxiter': maxiter, 'ftol': 1e-10})
    return res.x


def _select(x, n, iu, cutoff):
    i_idx, j_idx = iu
    c = x[:2 * n].reshape(n, 2)
    d = np.hypot(c[i_idx, 0] - c[j_idx, 0], c[i_idx, 1] - c[j_idx, 1])
    mask = d < cutoff
    return i_idx[mask], j_idx[mask]


def _optimize(x0, n, iu, maxiter=300):
    ii, jj = _select(x0, n, iu, 0.4)
    x = _opt_pairs(x0, n, ii, jj, maxiter)
    ii, jj = _select(x, n, iu, 0.35)
    x = _opt_pairs(x, n, ii, jj, 100)
    return x


def _random_start(rng, n, it):
    mode = it % 4
    if mode == 0:
        c = rng.uniform(0.05, 0.95, (n, 2))
    elif mode == 1:
        k = int(np.ceil(np.sqrt(n)))
        g = [(0.1 + 0.8 * (a + 0.5) / k, 0.1 + 0.8 * (b + 0.5) / k)
             for a in range(k) for b in range(k)]
        idx = rng.permutation(len(g))[:n]
        c = np.array(g)[idx] + rng.normal(0, 0.04, (n, 2))
    elif mode == 2:
        c = [[0.5, 0.5]]
        c += [[0.5 + 0.25 * np.cos(2 * np.pi * i / 8), 0.5 + 0.25 * np.sin(2 * np.pi * i / 8)] for i in range(8)]
        c += [[0.5 + 0.43 * np.cos(2 * np.pi * i / 17), 0.5 + 0.43 * np.sin(2 * np.pi * i / 17)] for i in range(17)]
        c = np.array(c[:n]) + rng.normal(0, 0.03, (n, 2))
    else:
        k = int(rng.integers(4, 7))
        counts = np.full(k, n // k)
        extra = n - counts.sum()
        for e in rng.choice(k, extra, replace=False):
            counts[e] += 1
        pts = []
        off = rng.random() < 0.5
        for i in range(k):
            m = counts[i]
            y = (i + 0.5) / k
            shift = 0.5 / max(m, 1) * 0.0
            for j in range(m):
                x = (j + 0.5) / m
                pts.append((x + shift, y))
        c = np.array(pts)
        if rng.random() < 0.5:
            c = c[:, ::-1]
        c = c + rng.normal(0, 0.02, c.shape)
    return np.clip(c, 0.02, 0.98), np.full(n, 0.05)


def solve(n=26):
    t0 = time.time()
    T_total = 250
    T_explore = 50
    rng = np.random.default_rng(1)
    iu = np.triu_indices(n, 1)
    best = None
    best_s = -1
    it = 0

    def run(c, r0):
        x0 = np.concatenate([c.ravel(), r0])
        x = _optimize(x0, n, iu)
        cc = np.clip(x[:2 * n].reshape(n, 2), 0, 1)
        r = _feasible_radii(cc)
        return cc, r, r.sum()

    while time.time() - t0 < T_explore or best is None:
        c, r0 = _random_start(rng, n, it)
        it += 1
        try:
            cc, r, s = run(c, r0)
        except Exception:
            continue
        if s > best_s:
            best_s = s
            best = (cc.copy(), r.copy())

    cur = (best[0].copy(), best[1].copy())
    cur_s = best_s
    fails = 0
    while time.time() - t0 < T_total:
        c, r = cur
        c = c.copy()
        r = r.copy()
        mode = rng.integers(0, 3)
        if mode == 0:
            c += rng.normal(0, rng.choice([0.01, 0.03, 0.06]), c.shape)
        elif mode == 1:
            kk = rng.integers(1, 4)
            idx = np.argsort(r)[:kk] if rng.random() < 0.5 else rng.choice(n, kk, replace=False)
            c[idx] = rng.uniform(0.05, 0.95, (len(idx), 2))
            c += rng.normal(0, 0.005, c.shape)
        else:
            i, j = rng.choice(n, 2, replace=False)
            c[[i, j]] = c[[j, i]]
            c += rng.normal(0, 0.01, c.shape)
        c = np.clip(c, 0.01, 0.99)
        r0 = r * 0.7
        try:
            cc, rr, s = run(c, r0)
        except Exception:
            continue
        if s > cur_s + 1e-9:
            cur = (cc, rr)
            cur_s = s
            fails = 0
            if s > best_s:
                best_s = s
                best = (cc.copy(), rr.copy())
        else:
            fails += 1
            if fails > 150:
                c0, r00 = _random_start(rng, n, it)
                it += 1
                try:
                    cc, rr, s = run(c0, r00)
                    cur, cur_s = (cc, rr), s
                    if s > best_s:
                        best_s = s
                        best = (cc.copy(), rr.copy())
                except Exception:
                    pass
                fails = 0

    c, r = best
    return c, r * (1 - 1e-12)
