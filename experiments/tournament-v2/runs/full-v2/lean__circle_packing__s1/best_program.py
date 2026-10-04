# EVOLVE-BLOCK-START
"""Optimise circle packing by maximising the sum of radii through a smooth
surrogate over the centres, with radii derived deterministically so that
every circle is as large as its centre allows."""
import numpy as np
from scipy.optimize import minimize


def solve(n=26):
    rng = np.random.default_rng(0)
    best = None
    # multiple restarts to escape poor local minima
    starts = []
    # a few structured starts
    starts.append(initial_hex(n))
    for _ in range(8):
        starts.append(np.clip(rng.random((n, 2)), 0.05, 0.95))

    for c0 in starts:
        res = minimize(obj, c0.ravel(), method="L-BFGS-B",
                       bounds=[(0.0, 1.0)] * (2 * n),
                       options={"maxiter": 6000, "ftol": 1e-14, "gtol": 1e-12})
        c = res.x.reshape(n, 2)
        c = np.clip(c, 0.0, 1.0)
        val = -obj(c.ravel())
        if best is None or val > best[0]:
            best = (val, c)

    centers = best[1]
    radii = max_radii(centers)
    # tiny push-out safety: recompute after a final polish
    return centers, radii


def obj(x):
    """Negative smooth surrogate of sum of feasible radii at given centres."""
    c = x.reshape(-1, 2)
    n = len(c)
    # wall distances
    walls = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    # soft pairwise coupling: sum of half-distances acts as smooth barrier proxy;
    # combine with walls via a soft-min that encourages both to grow
    diff = c[:, None, :] - c[None, :, :]
    d = np.sqrt(np.sum(diff ** 2, axis=-1) + 1e-12)
    np.fill_diagonal(d, np.inf)
    half = 0.5 * d.min(axis=1)
    r = np.minimum(walls, half)
    return -np.sum(r)


def max_radii(centers):
    """Largest radii for fixed centres: wall distance then iterative shrink."""
    n = len(centers)
    radii = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    for _ in range(300):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                s = radii[i] + radii[j]
                if s > d:
                    scale = d / s
                    radii[i] *= scale
                    radii[j] *= scale
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0)


def initial_hex(n):
    c = []
    # hexagonal-ish grid over the square
    rows = int(np.ceil(np.sqrt(n)))
    for i in range(rows):
        for j in range(rows):
            x = (j + 0.5 * (i % 2)) / rows
            y = (i + 0.5) / rows
            c.append([x, y])
    c = np.array(c[:n])
    return np.clip(c, 0.05, 0.95)
# EVOLVE-BLOCK-END

