import numpy as np
from scipy.optimize import minimize


def _initial_centers(n):
    # Hexagonal-ish arrangement in unit square, densest packing style.
    centers = []
    # simple grid rows
    rows = 6
    cols = 5
    if cols * rows < n:
        cols = 6
        rows = 5
    pts = []
    for r in range(rows):
        for c in range(cols):
            x = (c + 0.5) / cols
            y = (r + 0.5) / rows
            if r % 2 == 1:
                x += 0.5 / cols
            pts.append((x, y))
    pts = np.array(pts[:n])
    return np.clip(pts, 0.02, 0.98)


def _max_radii_given_centers(centers):
    n = len(centers)
    r = np.minimum.reduce([centers[:, 0], centers[:, 1],
                           1 - centers[:, 0], 1 - centers[:, 1]])
    for _ in range(200):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if r[i] + r[j] > d and d > 1e-12:
                    s = d / (r[i] + r[j])
                    r[i] *= s
                    r[j] *= s
                    changed = True
        if not changed:
            break
    return np.maximum(r, 0.0)


def _packing_score(x, n):
    centers = x[:2 * n].reshape(n, 2)
    radii = x[2 * n:]
    radii = np.maximum(radii, 0.0)
    # wall constraints
    walls = np.concatenate([
        centers[:, 0] - radii,
        centers[:, 1] - radii,
        1 - centers[:, 0] - radii,
        1 - centers[:, 1] - radii,
    ])
    pen = -0.0
    neg = np.minimum(walls, 0.0)
    pen += 1e4 * np.sum(neg ** 2)
    # pairwise
    diff = centers[:, None, :] - centers[None, :, :]
    dist = np.sqrt(np.sum(diff ** 2, axis=-1))
    np.fill_diagonal(dist, np.inf)
    rs = radii[:, None] + radii[None, :]
    excess = np.maximum(rs - dist, 0.0)
    pen += 1e4 * np.sum(excess ** 2)
    return -np.sum(radii) + pen


def solve(n=26):
    rng = np.random.default_rng(0)
    best = None
    best_val = np.inf

    def make_x(centers, radii):
        return np.concatenate([centers.ravel(), radii])

    for trial in range(8):
        if trial == 0:
            centers = _initial_centers(n)
        else:
            centers = rng.uniform(0.05, 0.95, size=(n, 2))
        radii = _max_radii_given_centers(centers)
        # slightly shrink
        radii = np.maximum(radii * 0.95, 1e-4)
        x0 = make_x(centers, radii)

        # Local smooth optimization via scipy BFGS on penalty
        res = minimize(lambda x: _packing_score(x, n), x0,
                       method='L-BFGS-B',
                       options={'maxiter': 3000, 'ftol': 1e-12, 'gtol': 1e-10})
        x = res.x

        # Refine: grow radii with fixed centers, then re-optimize centers/radii
        c = x[:2 * n].reshape(n, 2)
        r = _max_radii_given_centers(c)
        x = make_x(c, r)

        # try SLSQP with actual constraints
        try:
            def obj(x):
                return -np.sum(np.maximum(x[2 * n:], 0.0))

            cons = []
            # wall constraints: x_i - r_i >= 0, 1 - x_i - r_i >= 0, ...
            for i in range(n):
                cons.append({'type': 'ineq', 'fun': lambda x, i=i: x[2 * i] - x[2 * n + i]})
                cons.append({'type': 'ineq', 'fun': lambda x, i=i: 1 - x[2 * i] - x[2 * n + i]})
                cons.append({'type': 'ineq', 'fun': lambda x, i=i: x[2 * i + 1] - x[2 * n + i]})
                cons.append({'type': 'ineq', 'fun': lambda x, i=i: 1 - x[2 * i + 1] - x[2 * n + i]})
            for i in range(n):
                for j in range(i + 1, n):
                    def cf(x, i=i, j=j):
                        d = np.sqrt((x[2 * i] - x[2 * j]) ** 2 + (x[2 * i + 1] - x[2 * j + 1]) ** 2)
                        return d - x[2 * n + i] - x[2 * n + j]
                    cons.append({'type': 'ineq', 'fun': cf})

            bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
            res2 = minimize(obj, x, method='SLSQP', bounds=bounds,
                            constraints=cons,
                            options={'maxiter': 500, 'ftol': 1e-10})
            if res2.success or res2.fun < -np.sum(x[2 * n:]):
                x = res2.x

            # final: recompute max radii from centers (guarantees validity)
            c = x[:2 * n].reshape(n, 2)
            c = np.clip(c, 0.0, 1.0)
            r = _max_radii_given_centers(c)
            val = -np.sum(r)
            if val < best_val:
                best_val = val
                best = (c.copy(), r.copy())
        except Exception:
            c = x[:2 * n].reshape(n, 2)
            r = _max_radii_given_centers(c)
            if -np.sum(r) < best_val:
                best_val = -np.sum(r)
                best = (c.copy(), r.copy())

    if best is None:
        centers = _initial_centers(n)
        radii = _max_radii_given_centers(centers)
        return centers, radii

    centers, radii = best
    # Ensure strict validity: squeeze out any tiny overlap
    centers = np.clip(centers, 1e-9, 1 - 1e-9)
    radii = _max_radii_given_centers(centers)
    # small global shrink to be safe, then report
    return centers, radii
