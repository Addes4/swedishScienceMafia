import numpy as np
from scipy.optimize import linprog, minimize


def _radii_lp(centers):
    """Maximize sum r_i s.t. r_i <= wall_dist_i, r_i+r_j <= dist_ij, r_i>=0.
    LP with n variables. Returns radii array."""
    n = len(centers)
    c = -np.ones(n)
    A_ub = []
    b_ub = []
    # wall constraints: r_i <= wall_i  -> r_i <= wall_i
    for i in range(n):
        row = np.zeros(n)
        row[i] = 1.0
        A_ub.append(row)
        b_ub.append(_wall(centers[i]))
    # pair constraints
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            row = np.zeros(n)
            row[i] = 1.0
            row[j] = 1.0
            A_ub.append(row)
            b_ub.append(d)
    bounds = [(0, None)] * n
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=bounds, method='highs')
    if res.success:
        return np.maximum(res.x, 0.0)
    # fallback
    return _radii_greedy(centers)


def _wall(p):
    return min(p[0], p[1], 1.0 - p[0], 1.0 - p[1])


def _radii_greedy(centers):
    n = len(centers)
    radii = np.array([_wall(c) for c in centers])
    for _ in range(100):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > d + 1e-12:
                    s = d / (radii[i] + radii[j])
                    radii[i] *= s
                    radii[j] *= s
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0)


def _score(centers):
    return _radii_lp(centers).sum()


def _objective_with_grad(flat, n):
    """Smooth surrogate: keep centers in box, soft penalties for overlaps and walls.
    Returns (negative score proxy, grad). We use a soft-min formulation."""
    c = flat.reshape(n, 2)
    # clamp mildly
    cc = np.clip(c, 1e-6, 1 - 1e-6)
    # wall distances
    wall = np.minimum.reduce([cc[:, 0], cc[:, 1], 1 - cc[:, 0], 1 - cc[:, 1]])
    # pairwise distances
    diff = cc[:, None, :] - cc[None, :, :]
    dist = np.sqrt((diff ** 2).sum(-1) + 1e-12)
    np.fill_diagonal(dist, 1e6)
    # soft objective: sum of min(wall, (nearest half distance)) via log-sum-exp
    # Use a smooth approximation of candidate radius per circle:
    # r_i = softmin over wall_i and min_j (dist_ij / 2) ... but pairing matters.
    # Simpler: use log-sum-exp softmin of wall and half distances.
    beta = 40.0
    # half distances
    half = dist / 2.0
    # build matrix of constraints values for each i: wall_i and half[i,j]
    M = half.copy()
    # replace diagonal with wall
    for i in range(n):
        M[i, i] = wall[i]
    # softmin across rows with logsumexp(-beta*x)
    neg_beta_M = -beta * M
    mx = neg_beta_M.max(axis=1, keepdims=True)
    lse = mx[:, 0] - (np.log(np.exp(neg_beta_M - mx)).sum(axis=1)) / beta
    r = lse  # approximate max radius each circle could have given others fixed
    # score proxy
    score = r.sum()
    # gradient via autograd-like manual: d score / d c
    # We'll just approximate gradient numerically? No, too slow. Use finite difference on
    # a reduced set? Instead use a simpler surrogate gradient:
    grad = np.zeros_like(cc)
    # For each i, active constraint is j* minimizing M[i,j].
    # Move i away from j* and away from nearest wall to increase r_i.
    for i in range(n):
        row = M[i]
        jbest = int(np.argmin(row))
        if jbest == i:
            # wall active: push toward center of square
            d = cc[i] - 0.5
            grad[i] += -0.5 * d / (np.linalg.norm(d) + 1e-9)
        else:
            # pair active: push i away from jbest
            d = cc[i] - cc[jbest]
            nrm = np.linalg.norm(d) + 1e-9
            grad[i] += 0.5 * d / nrm
            grad[jbest] -= 0.5 * d / nrm
    # also add wall gradient softly
    for i in range(n):
        p = cc[i]
        dists = np.array([p[0], p[1], 1 - p[0], 1 - p[1]])
        k = int(np.argmin(dists))
        if k == 0:
            grad[i, 0] += -0.5
        elif k == 1:
            grad[i, 1] += -0.5
        elif k == 2:
            grad[i, 0] += 0.5
        else:
            grad[i, 1] += 0.5
    return -score, -grad.flatten()


def _optimize_centers(centers, iters=200, lr=0.01):
    n = len(centers)
    flat = centers.flatten().copy()
    best = flat.copy()
    best_score = _score(flat.reshape(n, 2))
    for it in range(iters):
        neg, grad = _objective_with_grad(flat, n)
        flat = flat - lr * grad
        flat = np.clip(flat.reshape(n, 2), 0.005, 0.995).flatten()
        # occasionally do exact LP score
        if it % 10 == 0:
            s = _score(flat.reshape(n, 2))
            if s > best_score:
                best_score = s
                best = flat.copy()
    s = _score(flat.reshape(n, 2))
    if s > best_score:
        best_score = s
        best = flat.copy()
    return best.reshape(n, 2), best_score


def _initial_layout(n, rng):
    """Hex-like packing scaled to unit square."""
    centers = []
    # try several rows
    rows = int(np.sqrt(n))
    for r_count in range(1, 12):
        cols = int(np.ceil(n / r_count))
        if cols * r_count < n:
            continue
        pts = []
        for r in range(r_count):
            for c in range(cols):
                if len(pts) >= n:
                    break
                x = (c + 0.5 + (0.5 if r % 2 else 0.0)) / cols
                y = (r + 0.5) / r_count
                pts.append([x, y])
            if len(pts) >= n:
                break
        if len(pts) == n:
            centers.append(np.array(pts))
    if not centers:
        centers.append(rng.random((n, 2)) * 0.8 + 0.1)
    # choose best init by LP score
    best = None
    best_s = -1
    for c in centers:
        c = np.clip(c, 0.05, 0.95)
        s = _score(c)
        if s > best_s:
            best_s = s
            best = c
    return best


def solve(n=26):
    rng = np.random.default_rng(42)
    best_centers = None
    best_score = -1.0
    best_radii = None

    starts = []
    starts.append(_initial_layout(n, rng))
    # random starts
    for _ in range(20):
        c = rng.random((n, 2)) * 0.8 + 0.1
        starts.append(c)
    # jittered hex
    base = _initial_layout(n, rng)
    for _ in range(15):
        c = base + rng.normal(0, 0.03, base.shape)
        starts.append(np.clip(c, 0.02, 0.98))

    for si, c0 in enumerate(starts):
        c = c0.copy()
        # local center optimization
        c_opt, s = _optimize_centers(c, iters=150, lr=0.008)
        # exact radii
        r = _radii_lp(c_opt)
        s = r.sum()
        if s > best_score:
            best_score = s
            best_centers = c_opt.copy()
            best_radii = r.copy()
        # basin hopping with random restarts from best
        for k in range(3):
            c2 = best_centers + rng.normal(0, 0.02, best_centers.shape)
            c2 = np.clip(c2, 0.01, 0.99)
            c2_opt, s2 = _optimize_centers(c2, iters=120, lr=0.01)
            r2 = _radii_lp(c2_opt)
            s2 = r2.sum()
            if s2 > best_score:
                best_score = s2
                best_centers = c2_opt.copy()
                best_radii = r2.copy()

    # final refinement from best
    for _ in range(5):
        c2 = best_centers + rng.normal(0, 0.01, best_centers.shape)
        c2 = np.clip(c2, 0.01, 0.99)
        c2_opt, _ = _optimize_centers(c2, iters=200, lr=0.005)
        r2 = _radii_lp(c2_opt)
        if r2.sum() > best_score:
            best_score = r2.sum()
            best_centers = c2_opt.copy()
            best_radii = r2.copy()

    # Ensure feasibility with greedy fallback
    best_radii = _radii_lp(best_centers)
    # final safety: shrink if needed
    best_radii = np.maximum(best_radii, 0.0)
    for _ in range(200):
        ok = True
        for i in range(n):
            if best_radii[i] < -1e-9:
                ok = False
            for j in range(i + 1, n):
                d = np.linalg.norm(best_centers[i] - best_centers[j])
                if best_radii[i] + best_radii[j] > d + 1e-9:
                    s = d / (best_radii[i] + best_radii[j] + 1e-12)
                    best_radii[i] *= s
                    best_radii[j] *= s
                    ok = False
            w = _wall(best_centers[i])
            if best_radii[i] > w + 1e-9:
                best_radii[i] = w
                ok = False
        if ok:
            break

    return best_centers, best_radii


if __name__ == "__main__":
    c, r = solve(26)
    print("sum radii:", r.sum())
