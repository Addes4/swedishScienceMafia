# EVOLVE-BLOCK-START
"""Circle packing in the unit square via barrier optimisation.

The objective  maximize sum(r_i)  subject to
    r_i >= 0,  r_i <= x_i, r_i <= 1-x_i,  r_i <= y_i,  r_i <= 1-y_i,
    r_i + r_j <= ||c_i - c_j||  for all i<j
is solved with an interior-point (log-barrier) method.  We optimise
theta = (r_i) together with centres using L-BFGS-B on the barrier objective

    f = -sum(r) - (1/mu) * sum log(slack)

with slack being the constraint slacks.  Barrier parameter mu is increased
geometrically.  A final feasible repair + greedy growth step polishes the
solution.
"""
import numpy as np
from scipy.optimize import minimize


def _initial(n, rng):
    """Tangled ring-style initial layout, pushed to a feasible region."""
    centers = [[0.5, 0.5]]
    centers += [[0.5 + 0.25 * np.cos(2 * np.pi * i / 8),
                 0.5 + 0.25 * np.sin(2 * np.pi * i / 8)] for i in range(8)]
    centers += [[0.5 + 0.62 * np.cos(2 * np.pi * i / 17),
                 0.5 + 0.62 * np.sin(2 * np.pi * i / 17)] for i in range(n - 9)]
    centers = np.array(centers[:n], dtype=float)
    centers = np.clip(centers + rng.normal(0, 0.01, centers.shape), 0.03, 0.97)
    r = np.full(n, 0.04)
    # shrink radii iteratively until feasible
    for _ in range(500):
        r = np.minimum.reduce([r, centers[:, 0], centers[:, 1],
                               1 - centers[:, 0], 1 - centers[:, 1]])
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if r[i] + r[j] > d:
                    s = d / (r[i] + r[j])
                    r[i] *= s
                    r[j] *= s
                    changed = True
        if not changed:
            break
    r *= 0.9  # keep a small margin from the barrier
    return centers, np.maximum(r, 1e-3)


def _slacks(c, r, n):
    s = []
    s.append(r)                  # r >= 0
    s.append(c[:, 0] - r)        # r <= x
    s.append(1 - c[:, 0] - r)    # r <= 1-x
    s.append(c[:, 1] - r)        # r <= y
    s.append(1 - c[:, 1] - r)    # r <= 1-y
    dx = c[:, None, 0] - c[None, :, 0]
    dy = c[:, None, 1] - c[None, :, 1]
    d = np.sqrt(dx * dx + dy * dy)
    rs = r[:, None] + r[None, :]
    iu = np.triu_indices(n, 1)
    s.append(d[iu] - rs[iu])     # r_i + r_j <= d
    return s


def _obj(z, n, mu):
    c = z[:2 * n].reshape(n, 2)
    r = z[2 * n:]
    slacks = _slacks(c, r, n)
    tot = np.concatenate([np.asarray(s).ravel() for s in slacks])
    tot = np.maximum(tot, 1e-14)
    return -r.sum() - np.log(tot).sum() / mu


def _grad(z, n, mu):
    c = z[:2 * n].reshape(n, 2)
    r = z[2 * n:]
    g = np.zeros_like(z)

    def add_slack_grad(mask, drad, dcx, dcy):
        """add gradient of -log(slack)/mu given derivative mask of slack."""
        sl = mask
        sl = np.maximum(sl, 1e-14)
        coef = -1.0 / (mu * sl)
        g[2 * n:] += coef * drad
        g[0::2][:n] += coef * dcx
        g[1::2][:n] += coef * dcy

    # sum term
    g[2 * n:] += -1.0

    one = np.ones(n)
    zero = np.zeros(n)
    # r >= 0 -> slack = r
    add_slack_grad(r, one, zero, zero)
    # slack = x - r
    add_slack_grad(c[:, 0] - r, -one, one, zero)
    # slack = 1 - x - r
    add_slack_grad(1 - c[:, 0] - r, -one, -one, zero)
    # slack = y - r
    add_slack_grad(c[:, 1] - r, -one, zero, one)
    # slack = 1 - y - r
    add_slack_grad(1 - c[:, 1] - r, -one, zero, -one)

    # pairwise slacks
    dx = c[:, None, 0] - c[None, :, 0]
    dy = c[:, None, 1] - c[None, :, 1]
    d = np.sqrt(dx * dx + dy * dy) + 1e-14
    rs = r[:, None] + r[None, :]
    iu = np.triu_indices(n, 1)
    ii, jj = iu
    sl = np.maximum(d[ii, jj] - rs[ii, jj], 1e-14)
    coef = -1.0 / (mu * sl)
    ux = dx[ii, jj] / d[ii, jj]
    uy = dy[ii, jj] / d[ii, jj]
    # d/dx_i = ux, d/dx_j = -ux ; d/dr_i = -1
    gx = np.zeros(n)
    gy = np.zeros(n)
    gr = np.zeros(n)
    np.add.at(gx, ii, coef * ux)
    np.add.at(gx, jj, coef * (-ux))
    np.add.at(gy, ii, coef * uy)
    np.add.at(gy, jj, coef * (-uy))
    np.add.at(gr, ii, coef * (-1.0))
    np.add.at(gr, jj, coef * (-1.0))
    g[0::2][:n] += gx
    g[1::2][:n] += gy
    g[2 * n:] += gr
    return g


def _repair_feasible(c, r, n):
    """Tune radii down so the configuration is strictly feasible."""
    r = np.maximum(r, 1e-6)
    for _ in range(400):
        r = np.minimum.reduce([r, c[:, 0], c[:, 1],
                               1 - c[:, 0], 1 - c[:, 1]])
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(c[i] - c[j])
                if d < 1e-12:
                    r[j] *= 0.5
                    changed = True
                    continue
                if r[i] + r[j] > d:
                    s = d / (r[i] + r[j]) * 0.9999
                    r[i] *= s
                    r[j] *= s
                    changed = True
        if not changed:
            break
    return c, np.maximum(r, 0.0)


def _polish(c, r, n, iters=4000):
    """Greedy growth: repeatedly increase radii where possible."""
    rng = np.random.default_rng(12345)
    for it in range(iters):
        order = np.arange(n)
        if it % 4 == 3:
            rng.shuffle(order)
        improved = False
        for i in order:
            # max feasible radius for circle i given others fixed
            hi = min(c[i, 0], c[i, 1], 1 - c[i, 0], 1 - c[i, 1])
            for j in range(n):
                if j == i:
                    continue
                dist = np.linalg.norm(c[i] - c[j])
                hi = min(hi, dist - r[j])
            hi = max(hi, 0.0)
            if hi > r[i] + 1e-12:
                r[i] = hi
                improved = True
        if not improved and it > n * 4:
            break
    return r


def solve(n=26):
    rng = np.random.default_rng(1)
    best_val = -np.inf
    best_c, best_r = None, None
    n_trials = 4
    for trial in range(n_trials):
        centers, radii = _initial(n, rng if trial > 0 else np.random.default_rng(0))
        if trial > 0:
            centers = np.clip(centers + rng.normal(0, 0.03, centers.shape),
                              0.02, 0.98)
            radii = np.maximum(radii * 0.9, 1e-3)
        z0 = np.concatenate([centers.ravel(), radii])
        # increasing barrier parameter
        for mu in [30.0, 100.0, 500.0, 3000.0, 20000.0]:
            try:
                res = minimize(_obj, z0, args=(n, mu), jac=_grad,
                               method="L-BFGS-B",
                               options={"maxiter": 1500, "maxfun": 200000,
                                        "ftol": 1e-14, "gtol": 1e-12})
                z0 = res.x
            except Exception:
                break
        c = z0[:2 * n].reshape(n, 2)
        r = z0[2 * n:]
        c = np.clip(c, 0.0, 1.0)
        c, r = _repair_feasible(c, r, n)
        # polish: alternate greedy growth with local coordinate descent
        for _ in range(30):
            r = _polish(c, r, n, iters=n * 40)
            c = c + rng.normal(0, 0.004, c.shape)
            c = np.clip(c, 1e-4, 1 - 1e-4)
            c, r = _repair_feasible(c, r, n)
            r = _polish(c, r, n, iters=n * 40)
        val = r.sum()
        if val > best_val:
            best_val = val
            best_c, best_r = c.copy(), r.copy()
    # final hard repair for safety
    best_c, best_r = _repair_feasible(best_c, best_r, n)
    best_r = _polish(best_c, best_r, n, iters=n * 60)
    best_c, best_r = _repair_feasible(best_c, best_r, n)
    return best_c, best_r
# EVOLVE-BLOCK-END
