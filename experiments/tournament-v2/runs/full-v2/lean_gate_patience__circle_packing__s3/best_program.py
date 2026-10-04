# EVOLVE-BLOCK-START
"""Maximise sum of radii of 26 non-overlapping circles in the unit square.

Strategy: for fixed centres the optimal radii are determined by the wall
constraints r_i <= min(x_i, 1-x_i, y_i, 1-y_i) and the pair constraints
r_i + r_j <= dist(i, j).  We compute these radii with a fast iterative
projection, then optimise the centre positions with scipy's SLSQP using
numerical gradients of the sum of radii, seeded from a dense triangular
lattice plus structured patterns.
"""
import numpy as np
from scipy.optimize import minimize


def max_radii(centers, iters=60):
    """Largest radii for fixed centres (fast iterative projection)."""
    c = np.asarray(centers, dtype=float)
    n = len(c)
    r = np.minimum.reduce([c[:, 0], c[:, 1], 1.0 - c[:, 0], 1.0 - c[:, 1]]).copy()
    for _ in range(iters):
        diff = c[:, None, :] - c[None, :, :]
        d = np.sqrt(np.sum(diff * diff, axis=-1))
        np.fill_diagonal(d, np.inf)
        s_ij = r[:, None] + r[None, :]
        viol = s_ij - d               # >0 means overlap
        ratio = np.where(d > 1e-12, d / np.maximum(s_ij, 1e-12), 1.0)
        factor = np.where((viol > 0) & (ratio < 1.0), ratio, 1.0)
        shrink = np.minimum.reduce(factor, axis=1)
        if np.all(shrink >= 1.0 - 1e-15):
            break
        r = r * np.minimum(shrink, 1.0)
    return np.maximum(r, 0.0)


def total_radius(centers, iters=60):
    return float(np.sum(max_radii(centers, iters)))


def tri_lattice(n, scale):
    """Triangular lattice points, scaled about the centre."""
    pts = []
    dy = np.sqrt(3.0) / 2.0
    k = 0
    row = 0
    while len(pts) < n:
        for col in range(row + 1):
            x = scale * (col - row / 2.0)
            y = scale * dy * row
            pts.append([x, y])
        row += 1
    pts = np.array(pts[:n], dtype=float)
    pts -= pts.mean(axis=0)
    extent = max(pts[:, 0].ptp(), pts[:, 1].ptp(), 1e-9)
    pts /= extent
    return 0.5 + pts * 0.9


def make_inits(n, rng):
    """A few structured starting configurations."""
    inits = []
    # triangular lattice at several scales
    for scale in (0.9, 1.05, 1.2, 1.4):
        try:
            inits.append(np.clip(tri_lattice(n, scale), 0.02, 0.98))
        except Exception:
            pass
    # hexagonal-like grid
    pts = []
    rows = int(np.ceil(np.sqrt(n)))
    for i in range(rows):
        for j in range(rows):
            x = (j + 0.5 + 0.5 * (i % 2)) / rows
            y = (i + 0.5) / rows
            pts.append([x, y])
    pts = np.array(pts[:n])
    inits.append(np.clip(pts, 0.02, 0.98))
    # grid
    g = int(np.ceil(np.sqrt(n)))
    pts = np.array([[(i % g + 0.5) / g, (i // g + 0.5) / g] for i in range(n)])
    inits.append(np.clip(pts, 0.02, 0.98))
    # ring patterns
    for rad in (0.35, 0.42):
        pts = [[0.5, 0.5]]
        m = n - 1
        for i in range(m):
            a = 2 * np.pi * i / m
            pts.append([0.5 + rad * np.cos(a), 0.5 + rad * np.sin(a)])
        inits.append(np.clip(np.array(pts), 0.02, 0.98))
    # random
    for _ in range(4):
        inits.append(rng.uniform(0.05, 0.95, size=(n, 2)))
    return inits


def slsqp_opt(centers, maxiter=200):
    """SLSQP on flattened centres maximising sum of radii."""
    n = len(centers)
    x0 = np.clip(centers, 0.005, 0.995).flatten()

    def neg_obj(x):
        c = x.reshape(n, 2)
        return -total_radius(c, iters=40)

    bounds = [(0.005, 0.995)] * (2 * n)
    try:
        res = minimize(neg_obj, x0, method="SLSQP", bounds=bounds,
                       options={"maxiter": maxiter, "ftol": 1e-9})
        c = res.x.reshape(n, 2)
    except Exception:
        c = x0.reshape(n, 2)
    return np.clip(c, 0.005, 0.995), -neg_obj(c.flatten())


def solve(n=26):
    rng = np.random.default_rng(12345)
    best = None
    best_val = -1.0
    inits = make_inits(n, rng)
    for c0 in inits:
        c, v = slsqp_opt(c0, maxiter=150)
        if v > best_val:
            best_val = v
            best = c
    # final polish with higher iteration SLSQP and accurate radii
    c, v = slsqp_opt(best, maxiter=300)
    if v > best_val:
        best_val = v
        best = c
    radii = max_radii(best, iters=200)
    return np.asarray(best, dtype=float), radii
# EVOLVE-BLOCK-END
