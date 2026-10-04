# EVOLVE-BLOCK-START
"""Circle packing: maximise the sum of radii for n circles in the unit square.

Approach:
  * seed centres with a hexagon-ish grid + random jitter
  * for any fixed centre layout, compute the maximum feasible radii by
    finding the largest scale s such that all pairwise constraints
    r_i + r_j <= dist_ij hold when r_i = s * w_i.  A simple water-filling
    / iterative shrink with enough passes converges quickly.
  * random-restart local search: jitter centres, re-solve radii, keep the
    best layout.
"""
import numpy as np


def _radii_for_centers(centers, iters=200):
    """Largest radii for fixed centres via iterative proportional shrink."""
    n = len(centers)
    r = np.minimum.reduce([
        centers[:, 0], centers[:, 1],
        1.0 - centers[:, 0], 1.0 - centers[:, 1],
    ])
    r = np.maximum(r, 0.0)
    for _ in range(iters):
        changed = False
        # vectorised pairwise pass
        dx = centers[:, 0][:, None] - centers[:, 0][None, :]
        dy = centers[:, 1][:, None] - centers[:, 1][None, :]
        d = np.sqrt(dx * dx + dy * dy)
        np.fill_diagonal(d, np.inf)
        s = r[:, None] + r[None, :]
        mask = s > d
        if mask.any():
            scale = np.where(mask, d / np.maximum(s, 1e-12), 1.0)
            factor = scale.min(axis=1)
            factor = np.minimum(factor, 1.0)
            r = r * factor
            changed = True
        if not changed:
            break
    return np.maximum(r, 0.0)


def _seed_centers(n, rng):
    """Hexagonal-ish grid seeded inside the unit square with jitter."""
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    pts = []
    for iy in range(rows):
        for ix in range(cols):
            if len(pts) >= n:
                break
            x = (ix + 0.5) / cols
            y = (iy + 0.5) / rows
            if iy % 2 == 1:
                x += 0.5 / cols
            pts.append([x, y])
    pts = np.array(pts[:n], dtype=float)
    pts += rng.normal(0.0, 0.03, size=pts.shape)
    return np.clip(pts, 0.02, 0.98)


def solve(n=26):
    rng = np.random.default_rng(12345)
    best_centers = None
    best_radii = None
    best_sum = -1.0

    for restart in range(60):
        centers = _seed_centers(n, rng)
        radii = _radii_for_centers(centers)
        cur_sum = radii.sum()

        # coordinate descent on centres
        step = 0.05
        for _ in range(400):
            improved = False
            for i in range(n):
                for _try in range(4):
                    delta = rng.normal(0.0, step, size=2)
                    new_c = centers.copy()
                    new_c[i] = np.clip(centers[i] + delta, 0.0, 1.0)
                    new_r = _radii_for_centers(new_c, iters=60)
                    new_sum = new_r.sum()
                    if new_sum > cur_sum + 1e-7:
                        centers = new_c
                        radii = new_r
                        cur_sum = new_sum
                        improved = True
            if not improved:
                step *= 0.6
                if step < 1e-4:
                    break

        if cur_sum > best_sum:
            best_sum = cur_sum
            best_centers = centers.copy()
            best_radii = radii.copy()

    # final polish with more accurate radii
    best_radii = _radii_for_centers(best_centers, iters=300)
    return best_centers, best_radii
# EVOLVE-BLOCK-END
