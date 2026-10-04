import numpy as np
from scipy.optimize import minimize


def max_radii_from_centers(centers):
    """Given fixed centers, compute the largest feasible radii.
    This is an LP in radii: maximize sum r_i subject to
    r_i <= x_i, r_i <= 1-x_i, r_i <= y_i, r_i <= 1-y_i,
    r_i + r_j <= d_ij (i<j), r_i >= 0.
    We solve it with a simple iterative projection scheme which is
    very effective for this structure."""
    n = len(centers)
    r = np.minimum.reduce([centers[:, 0], centers[:, 1],
                           1 - centers[:, 0], 1 - centers[:, 1]]).copy()

    # Precompute pairwise distances
    diff = centers[:, None, :] - centers[None, :, :]
    D = np.sqrt(np.sum(diff * diff, axis=2))

    for _ in range(200):
        changed = False
        # pair constraints
        for i in range(n):
            for j in range(i + 1, n):
                s = r[i] + r[j]
                d = D[i, j]
                if s > d:
                    if s <= 1e-15:
                        continue
                    # shrink both proportionally, but at least move towards feasibility
                    scale = d / s
                    r[i] *= scale
                    r[j] *= scale
                    changed = True
        # box constraints
        cap = np.minimum.reduce([centers[:, 0], centers[:, 1],
                                 1 - centers[:, 0], 1 - centers[:, 1]])
        if np.any(r > cap + 1e-15):
            r = np.minimum(r, cap)
            changed = True
        if not changed:
            break
    return np.maximum(r, 0.0)


def objective(z, n):
    """z = flattened vector of centers (2n). For fixed centers compute
    the maximum sum of radii. We use negative sum as the objective."""
    centers = z.reshape(n, 2)
    # clamp slightly inside the box so wall distance >= 0
    centers = np.clip(centers, 1e-6, 1 - 1e-6)
    r = max_radii_from_centers(centers)
    return -np.sum(r), r


def solve(n=26):
    rng = np.random.default_rng(12345)

    best_centers = None
    best_radii = None
    best_sum = -1.0

    # Build several heuristic starts.
    starts = []

    # Start 1: center + rings (baseline-ish)
    c = [[0.5, 0.5]]
    c += [[0.5 + 0.3 * np.cos(2 * np.pi * i / 8),
           0.5 + 0.3 * np.sin(2 * np.pi * i / 8)] for i in range(8)]
    c += [[0.5 + 0.7 * np.cos(2 * np.pi * i / 16),
           0.5 + 0.7 * np.sin(2 * np.pi * i / 16)] for i in range(16)]
    c = np.array(c[:n])
    starts.append(np.clip(c, 0.02, 0.98))

    # Start 2: hex-like lattice
    m = int(np.ceil(np.sqrt(n)))
    pts = []
    for i in range(m):
        for j in range(m):
            if len(pts) < n:
                x = (i + 0.5) / m
                y = (j + 0.5 + (0.5 if i % 2 else 0.0)) / m
                pts.append([x, y])
    pts = np.array(pts[:n])
    starts.append(np.clip(pts, 0.02, 0.98))

    # Random starts
    for _ in range(6):
        starts.append(np.clip(rng.random((n, 2)), 0.02, 0.98))

    for s in starts:
        z0 = s.reshape(-1)
        try:
            res = minimize(
                lambda z: objective(z, n)[0],
                z0,
                method="L-BFGS-B",
                options={"maxiter": 400, "ftol": 1e-12, "gtol": 1e-9},
            )
            z = res.x
            centers = np.clip(z.reshape(n, 2), 0.0, 1.0)
            radii = max_radii_from_centers(centers)
            ssum = float(np.sum(radii))
            if ssum > best_sum:
                best_sum = ssum
                best_centers = centers.copy()
                best_radii = radii.copy()
        except Exception:
            continue

    # Local refinement: coordinate descent on centers.
    if best_centers is None:
        best_centers = np.clip(rng.random((n, 2)), 0.02, 0.98)
        best_radii = max_radii_from_centers(best_centers)
        best_sum = float(np.sum(best_radii))

    centers = np.clip(best_centers, 1e-4, 1 - 1e-4)
    radii = max_radii_from_centers(centers)

    # Simple local search over centers with shrinking step
    step = 0.02
    for it in range(120):
        improved = False
        idx_order = rng.permutation(n)
        for i in idx_order:
            for dx, dy in [(step, 0), (-step, 0), (0, step), (0, -step)]:
                trial = centers.copy()
                trial[i, 0] = np.clip(trial[i, 0] + dx, 0.0, 1.0)
                trial[i, 1] = np.clip(trial[i, 1] + dy, 0.0, 1.0)
                r_trial = max_radii_from_centers(trial)
                if np.sum(r_trial) > np.sum(radii) + 1e-12:
                    centers = trial
                    radii = r_trial
                    improved = True
        if not improved:
            step *= 0.5
            if step < 1e-4:
                break

    radii = max_radii_from_centers(centers)
    return centers, radii
