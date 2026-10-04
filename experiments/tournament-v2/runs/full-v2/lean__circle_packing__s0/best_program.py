# EVOLVE-BLOCK-START
"""SLSQP-based multi-start optimizer for circle packing in the unit square.

Maximise sum of radii subject to:
  - wall constraints: r_i <= x_i, r_i <= 1-x_i, r_i <= y_i, r_i <= 1-y_i
  - non-overlap: (x_i-x_j)^2 + (y_i-y_j)^2 >= (r_i+r_j)^2

We build a safe feasible start by first placing centres, computing the max
feasible radii heuristically, then letting SLSQP polish from there.
"""
import numpy as np
from scipy.optimize import minimize


def max_radii(centers):
    """Largest radii for fixed centres via pairwise shrinking."""
    n = len(centers)
    radii = np.minimum.reduce([centers[:, 0], centers[:, 1],
                               1 - centers[:, 0], 1 - centers[:, 1]])
    for _ in range(300):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                dx = centers[i, 0] - centers[j, 0]
                dy = centers[i, 1] - centers[j, 1]
                d = np.sqrt(dx * dx + dy * dy)
                s = radii[i] + radii[j]
                if d < s - 1e-12:
                    scale = d / s if s > 0 else 0.0
                    radii[i] *= scale
                    radii[j] *= scale
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0)


def _init_centers_hex(n, seed):
    rng = np.random.default_rng(seed)
    centers = []
    rows = int(np.ceil(np.sqrt(n)))
    y_step = 1.0 / rows
    x_step = 1.0 / rows
    placed = 0
    r = 0
    while placed < n:
        y = (r + 0.5) * y_step
        offset = 0.5 * x_step if (r % 2) else 0.0
        cols = int(np.floor((1.0 - offset) / x_step)) + 1
        for c in range(cols):
            if placed >= n:
                break
            x = offset + (c + 0.5) * x_step
            centers.append([x + 0.05 * (rng.random() - 0.5),
                            y + 0.05 * (rng.random() - 0.5)])
            placed += 1
        r += 1
    centers = np.array(centers[:n])
    centers = np.clip(centers, 0.1, 0.9)
    return centers


def _init_centers_grid(n, seed):
    rng = np.random.default_rng(seed)
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    centers = []
    for i in range(n):
        rr = i // cols
        cc = i % cols
        x = (cc + 0.5) / cols + 0.03 * (rng.random() - 0.5)
        y = (rr + 0.5) / rows + 0.03 * (rng.random() - 0.5)
        centers.append([x, y])
    return np.clip(np.array(centers), 0.1, 0.9)


def _pack_centers(centers, iters=800, lr=0.02):
    """Push overlapping circles apart (fixed radii = max feasible)."""
    n = len(centers)
    centers = centers.copy()
    for _ in range(iters):
        radii = max_radii(centers)
        grad = np.zeros_like(centers)
        for i in range(n):
            for j in range(i + 1, n):
                dx = centers[i, 0] - centers[j, 0]
                dy = centers[i, 1] - centers[j, 1]
                d = np.sqrt(dx * dx + dy * dy) + 1e-12
                s = radii[i] + radii[j]
                if d < s:
                    f = (s - d) / d
                    grad[i, 0] += f * dx
                    grad[i, 1] += f * dy
                    grad[j, 0] -= f * dx
                    grad[j, 1] -= f * dy
        # wall pressures
        for i in range(n):
            r = radii[i]
            if centers[i, 0] - r < 1e-3:
                grad[i, 0] += 1e-2
            if 1 - centers[i, 0] - r < 1e-3:
                grad[i, 0] -= 1e-2
            if centers[i, 1] - r < 1e-3:
                grad[i, 1] += 1e-2
            if 1 - centers[i, 1] - r < 1e-3:
                grad[i, 1] -= 1e-2
        centers = centers + grad * lr
        centers = np.clip(centers, 0.0, 1.0)
    return centers


def _objective(z):
    n = len(z) // 3
    r = z[2 * n:3 * n]
    return -np.sum(r)


def _constraints(n):
    def confun(z):
        x = z[0:n]
        y = z[n:2 * n]
        r = z[2 * n:3 * n]
        out = []
        # wall constraints as inequalities >= 0
        out.append(x - r)
        out.append(1 - x - r)
        out.append(y - r)
        out.append(1 - y - r)
        # non-overlap
        for i in range(n):
            for j in range(i + 1, n):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                out.append(np.array([dx * dx + dy * dy - (r[i] + r[j]) ** 2]))
        return np.concatenate(out)
    return confun


def _optimize(centers0, radii0, maxiter=400):
    n = len(centers0)
    z0 = np.concatenate([centers0[:, 0], centers0[:, 1], radii0])
    # bounds: x,y in [0,1], r in [0, 0.5]
    bounds = [(0.0, 1.0)] * (2 * n) + [(0.0, 0.5)] * n
    cons = [{'type': 'ineq', 'fun': _constraints(n)}]
    try:
        res = minimize(_objective, z0, method='SLSQP', bounds=bounds,
                       constraints=cons,
                       options={'maxiter': maxiter, 'ftol': 1e-10})
        z = res.x
    except Exception:
        return None
    x = z[0:n]
    y = z[n:2 * n]
    r = z[2 * n:3 * n]
    r = np.maximum(r, 0.0)
    # final feasibility check
    if np.any(x - r < -1e-7) or np.any(1 - x - r < -1e-7):
        return None
    if np.any(y - r < -1e-7) or np.any(1 - y - r < -1e-7):
        return None
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            d2 = dx * dx + dy * dy
            if d2 < (r[i] + r[j]) ** 2 - 1e-7:
                return None
    centers = np.stack([x, y], axis=1)
    return centers, r


def solve(n=26):
    best_sum = -1.0
    best = None

    seeds = []
    for s in range(4):
        seeds.append(('hex', s))
    for s in range(4):
        seeds.append(('grid', s))

    for kind, s in seeds:
        if kind == 'hex':
            c0 = _init_centers_hex(n, s)
        else:
            c0 = _init_centers_grid(n, s)
        c0 = _pack_centers(c0, iters=600, lr=0.02)
        r0 = max_radii(c0)
        # scale down a touch to ensure feasibility under numerical slack
        r0 = r0 * 0.98
        res = _optimize(c0, r0, maxiter=500)
        if res is None:
            continue
        centers, radii = res
        s_val = radii.sum()
        if s_val > best_sum:
            best_sum = s_val
            best = (centers.copy(), radii.copy())

    if best is None:
        # fallback
        c0 = _init_centers_hex(n, 0)
        c0 = _pack_centers(c0)
        r0 = max_radii(c0)
        best = (c0, r0)

    # light polish: repeat SLSQP from best
    centers, radii = best
    r2 = _optimize(centers, radii * 1.0, maxiter=800)
    if r2 is not None and r2[1].sum() > best_sum:
        best = r2

    return best
# EVOLVE-BLOCK-END
