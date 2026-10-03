import time
import numpy as np
from scipy.optimize import minimize, linprog

# EVOLVE-BLOCK-START


def _lp_radii(centers):
    """Optimal radii for fixed centres (LP); always feasible."""
    n = len(centers)
    c = np.clip(centers, 0.0, 1.0)
    I, J = np.triu_indices(n, 1)
    d = np.linalg.norm(c[I] - c[J], axis=1)
    A = np.zeros((len(I), n))
    A[np.arange(len(I)), I] = 1.0
    A[np.arange(len(I)), J] = 1.0
    wall = np.minimum.reduce([c[:, 0], c[:, 1], 1 - c[:, 0], 1 - c[:, 1]])
    wall = np.maximum(wall, 0.0)
    try:
        res = linprog(-np.ones(n), A_ub=A, b_ub=d,
                      bounds=[(0, w) for w in wall], method="highs")
        if res.status == 0:
            r = np.maximum(res.x, 0.0)
        else:
            raise RuntimeError
    except Exception:
        r = wall.copy()
        for _ in range(100):
            ch = False
            for i, j, dd in zip(I, J, d):
                if r[i] + r[j] > dd:
                    s = dd / (r[i] + r[j])
                    r[i] *= s
                    r[j] *= s
                    ch = True
            if not ch:
                break
    return c, r


def _score_safe(centers):
    c, r = _lp_radii(centers)
    r = np.maximum(r - 1e-12, 0.0)
    return c, r, r.sum()


def _make_init(rng, n, kind):
    if kind == 0:
        g = (np.arange(5) + 0.5) / 5
        pts = [[x, y] for x in g for y in g]
        pts.append(rng.random(2))
        pts = np.array(pts) + rng.normal(0, 0.02, (26, 2))
    elif kind == 1:
        patterns = [[5, 5, 6, 5, 5], [5, 6, 5, 6, 4], [4, 5, 4, 5, 4, 4],
                    [6, 5, 5, 5, 5], [5, 5, 5, 5, 6], [4, 5, 5, 5, 4, 3]]
        pat = patterns[rng.integers(len(patterns))]
        pts = []
        k = len(pat)
        for ri, m in enumerate(pat):
            y = (ri + 0.5) / k
            off = 0.0 if ri % 2 == 0 else 0.5 / m
            for ci in range(m):
                pts.append([(ci + 0.5) / m * (1 - off) + off * 0.5 * (1 if ri % 2 else 0) , y])
        pts = np.array(pts[:n])
        while len(pts) < n:
            pts = np.vstack([pts, rng.random(2)])
        pts = pts + rng.normal(0, 0.02, pts.shape)
    elif kind == 2:
        n1 = int(rng.integers(5, 9))
        n2 = n - 1 - n1
        pts = [[0.5, 0.5]]
        pts += [[0.5 + 0.25 * np.cos(2 * np.pi * i / n1), 0.5 + 0.25 * np.sin(2 * np.pi * i / n1)] for i in range(n1)]
        pts += [[0.5 + 0.42 * np.cos(2 * np.pi * i / n2 + 0.3), 0.5 + 0.42 * np.sin(2 * np.pi * i / n2 + 0.3)] for i in range(n2)]
        pts = np.array(pts) + rng.normal(0, 0.02, (n, 2))
    else:
        pts = rng.random((n, 2))
    return np.clip(pts, 0.03, 0.97)


def _optimize(pts, n, I, J, Alin, rows):
    m = len(I)

    def obj(x):
        return -x[2 * n:].sum()

    gobj = np.zeros(3 * n)
    gobj[2 * n:] = -1.0

    def jobj(x):
        return gobj

    def pair(x):
        dx = x[I] - x[J]
        dy = x[n + I] - x[n + J]
        s = x[2 * n + I] + x[2 * n + J]
        return dx * dx + dy * dy - s * s

    def pair_jac(x):
        dx = x[I] - x[J]
        dy = x[n + I] - x[n + J]
        s = x[2 * n + I] + x[2 * n + J]
        Jm = np.zeros((m, 3 * n))
        Jm[rows, I] = 2 * dx
        Jm[rows, J] = -2 * dx
        Jm[rows, n + I] = 2 * dy
        Jm[rows, n + J] = -2 * dy
        Jm[rows, 2 * n + I] = -2 * s
        Jm[rows, 2 * n + J] = -2 * s
        return Jm

    def lin(x):
        return Alin[0] @ x + Alin[1]

    def lin_jac(x):
        return Alin[0]

    r0 = np.full(n, 0.05)
    x0 = np.concatenate([pts[:, 0], pts[:, 1], r0])
    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    try:
        res = minimize(obj, x0, jac=jobj, method="SLSQP", bounds=bounds,
                       constraints=[{"type": "ineq", "fun": pair, "jac": pair_jac},
                                    {"type": "ineq", "fun": lin, "jac": lin_jac}],
                       options={"maxiter": 250, "ftol": 1e-10})
        x = res.x
    except Exception:
        return pts
    return np.stack([x[:n], x[n:2 * n]], axis=1)


def solve(n=26):
    t0 = time.time()
    budget = 200.0
    rng = np.random.default_rng(12345)
    I, J = np.triu_indices(n, 1)
    rows = np.arange(len(I))
    # linear containment: x-r>=0, 1-x-r>=0, y-r>=0, 1-y-r>=0
    A = np.zeros((4 * n, 3 * n))
    b = np.zeros(4 * n)
    for i in range(n):
        A[i, i] = 1; A[i, 2 * n + i] = -1
        A[n + i, i] = -1; A[n + i, 2 * n + i] = -1; b[n + i] = 1
        A[2 * n + i, n + i] = 1; A[2 * n + i, 2 * n + i] = -1
        A[3 * n + i, n + i] = -1; A[3 * n + i, 2 * n + i] = -1; b[3 * n + i] = 1
    Alin = (A, b)

    best_c, best_r = _lp_radii(np.full((n, 2), 0.5))[0], np.zeros(n)
    best_s = -1.0
    it = 0
    last = 0.0
    while time.time() - t0 < budget:
        el = time.time() - t0
        if el < budget * 0.55 or best_s < 0:
            kind = it % 4
            pts = _make_init(rng, n, kind)
        else:
            sig = rng.choice([0.01, 0.03, 0.06])
            pts = np.clip(best_c + rng.normal(0, sig, best_c.shape), 0.02, 0.98)
            if rng.random() < 0.3:
                k = rng.integers(n)
                pts[k] = rng.random(2)
        it += 1
        ts = time.time()
        out = _optimize(pts, n, I, J, Alin, rows)
        c, r, s = _score_safe(out)
        if s > best_s:
            best_s, best_c, best_r = s, c, r
        last = time.time() - ts
        if time.time() - t0 + 2 * last > budget:
            break
    return best_c, best_r
# EVOLVE-BLOCK-END
