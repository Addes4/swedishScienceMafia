# EVOLVE-BLOCK-START
"""Circle packing in the unit square: maximise sum of radii.

Approach: multi-start. For each starting configuration, alternate between
(a) inflating all radii proportionally (using a fixed-centre max-radii solve)
and (b) resolving overlaps via a gradient-based relaxation of the centres.
Keep the best feasible packing found.
"""
import numpy as np
from scipy.optimize import minimize


def _hex_init(n):
    """Hexagonal-ish starting configuration."""
    centers = []
    r0 = 0.5 / np.sqrt(n)
    spacing = 2.0 * r0
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    for i in range(n):
        row = i // cols
        col = i % cols
        x = 0.5 + (col - (cols - 1) / 2.0) * min(spacing, 0.9 / max(cols, 1))
        y = 0.5 + (row - (rows - 1) / 2.0) * min(spacing, 0.9 / max(rows, 1))
        if row % 2 == 1:
            x += min(spacing, 0.9 / max(cols, 1)) * 0.5
        centers.append([x, y])
    centers = np.clip(np.array(centers), 0.05, 0.95)
    return centers


def max_radii(centers):
    """Largest radii for fixed centres via iterative pairwise shrinking."""
    n = len(centers)
    c = np.asarray(centers)
    radii = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    for _ in range(400):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                dx = c[i, 0] - c[j, 0]
                dy = c[i, 1] - c[j, 1]
                d = np.sqrt(dx * dx + dy * dy)
                s = radii[i] + radii[j]
                if s > d and s > 1e-12:
                    scale = d / s
                    radii[i] *= scale
                    radii[j] *= scale
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0)


def _relax_centers(centers, radii, iters=300):
    """Push overlapping centres apart while keeping radii, keeping in box."""
    c = centers.copy().astype(float)
    n = len(c)
    for _ in range(iters):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                dx = c[j, 0] - c[i, 0]
                dy = c[j, 1] - c[i, 1]
                d = np.sqrt(dx * dx + dy * dy) + 1e-12
                overlap = radii[i] + radii[j] - d
                if overlap > 1e-9:
                    ux, uy = dx / d, dy / d
                    c[i, 0] -= ux * overlap * 0.5
                    c[i, 1] -= uy * overlap * 0.5
                    c[j, 0] += ux * overlap * 0.5
                    c[j, 1] += uy * overlap * 0.5
                    moved = True
        np.clip(c[:, 0], radii * 0 + 1e-6, 1 - radii * 0 - 1e-6, out=c[:, 0])
        np.clip(c[:, 1], 1e-6, 1 - 1e-6, out=c[:, 1])
        if not moved:
            break
    return c


def _grow(centers, rounds=60):
    """Alternate inflate + relax to grow radii/improve sum."""
    c = centers.copy().astype(float)
    r = max_radii(c)
    best_sum = r.sum()
    best = (c.copy(), r.copy())
    for _ in range(rounds):
        # inflate slightly
        r = r * 1.02
        # relax centres to remove overlaps (radii temporarily too big)
        c = _relax_centers(c, r, iters=80)
        # recompute feasible radii for new centres
        r = max_radii(c)
        s = r.sum()
        if s > best_sum:
            best_sum = s
            best = (c.copy(), r.copy())
    return best


def solve(n=26):
    """Return (centers, radii) for n disjoint circles inside the unit square."""
    rng = np.random.default_rng(12345)
    best_sum = -1.0
    best_c = None
    best_r = None

    starts = []
    # hexagonal starts with a few jitters
    base = _hex_init(n)
    starts.append(base)
    for _ in range(4):
        starts.append(np.clip(base + rng.normal(0, 0.03, base.shape), 0.03, 0.97))
    # random starts
    for _ in range(5):
        starts.append(rng.uniform(0.05, 0.95, size=(n, 2)))

    for c0 in starts:
        try:
            c, r = _grow(c0, rounds=60)
        except Exception:
            continue
        s = r.sum()
        if s > best_sum:
            best_sum = s
            best_c = c.copy()
            best_r = r.copy()

    # final polish using L-BFGS-B on the smooth penalty
    def unpack(v):
        c = v[:2 * n].reshape(n, 2)
        r = np.abs(v[2 * n:])
        return c, r

    def penalty(v):
        c, r = unpack(v)
        total = -np.sum(r)
        cx = c[:, 0]
        cy = c[:, 1]
        # wall penalties
        w = np.minimum.reduce([cx - r, cy - r, 1 - cx - r, 1 - cy - r])
        neg = w < 0
        total += 1e4 * np.sum(w[neg] ** 2)
        # overlap penalties
        dx = cx[:, None] - cx[None, :]
        dy = cy[:, None] - cy[None, :]
        dist = np.sqrt(dx * dx + dy * dy)
        rsum = r[:, None] + r[None, :]
        gap = dist - rsum
        np.fill_diagonal(gap, 1.0)
        mask = gap < 0
        total += 1e4 * np.sum(gap[mask] ** 2)
        return total

    if best_c is not None:
        v0 = np.concatenate([best_c.ravel(), best_r])
        res = minimize(penalty, v0, method='L-BFGS-B',
                       options={'maxiter': 3000, 'maxfun': 100000,
                                'ftol': 1e-12, 'gtol': 1e-10})
        c, r = unpack(res.x)
        c = np.clip(c, 1e-6, 1 - 1e-6)
        r = max_radii(c)
        if r.sum() > best_sum:
            best_sum = r.sum()
            best_c = c
            best_r = r

    return best_c, best_r
# EVOLVE-BLOCK-END
