# EVOLVE-BLOCK-START
"""Penalty-method Adam optimisation (batched random restarts) + SLSQP polish + LP radii."""
import time
import numpy as np
from scipy.optimize import minimize, linprog


def _lp_radii(centers):
    n = len(centers)
    I, J = np.triu_indices(n, 1)
    d = np.linalg.norm(centers[I] - centers[J], axis=1)
    A = np.zeros((len(I), n))
    A[np.arange(len(I)), I] = 1.0
    A[np.arange(len(I)), J] = 1.0
    wall = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    wall = np.maximum(wall, 0.0)
    try:
        res = linprog(-np.ones(n), A_ub=A, b_ub=d, bounds=list(zip(np.zeros(n), wall)), method="highs")
        if res.status == 0:
            return np.maximum(res.x, 0.0)
    except Exception:
        pass
    return _shrink_radii(centers, wall.copy())


def _shrink_radii(centers, radii):
    n = len(centers)
    for _ in range(200):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > d:
                    s = d / (radii[i] + radii[j])
                    radii[i] *= s
                    radii[j] *= s
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0)


def _valid(centers, radii, tol=1e-12):
    n = len(centers)
    if np.any(radii < 0):
        return False
    if np.any(centers[:, 0] - radii < -tol) or np.any(centers[:, 1] - radii < -tol):
        return False
    if np.any(centers[:, 0] + radii > 1 + tol) or np.any(centers[:, 1] + radii > 1 + tol):
        return False
    I, J = np.triu_indices(n, 1)
    d = np.linalg.norm(centers[I] - centers[J], axis=1)
    return bool(np.all(radii[I] + radii[J] <= d + tol))


def _adam_batch(X, Y, R, iters, lr0, lr1, mu0, mu1):
    B, n = X.shape
    off = 1.0 - np.eye(n)[None]
    P = np.stack([X, Y, R])
    m = np.zeros_like(P)
    v = np.zeros_like(P)
    b1, b2, eps = 0.9, 0.999, 1e-8
    for t in range(iters):
        frac = t / max(iters - 1, 1)
        lr = lr0 * (lr1 / lr0) ** frac
        mu = mu0 * (mu1 / mu0) ** frac
        X, Y, R = P[0], P[1], P[2]
        dx = X[:, :, None] - X[:, None, :]
        dy = Y[:, :, None] - Y[:, None, :]
        d = np.sqrt(dx * dx + dy * dy + 1e-12)
        ov = np.maximum(R[:, :, None] + R[:, None, :] - d, 0.0) * off
        gR = 2 * ov.sum(2)
        coef = 2 * ov / d
        gX = -(coef * dx).sum(2)
        gY = -(coef * dy).sum(2)
        w = np.maximum(R - X, 0); gR += 2 * w; gX -= 2 * w
        w = np.maximum(R + X - 1, 0); gR += 2 * w; gX += 2 * w
        w = np.maximum(R - Y, 0); gR += 2 * w; gY -= 2 * w
        w = np.maximum(R + Y - 1, 0); gR += 2 * w; gY += 2 * w
        w = np.minimum(R, 0); gR += 2 * w
        g = mu * np.stack([gX, gY, gR])
        g[2] -= 1.0
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        mh = m / (1 - b1 ** (t + 1))
        vh = v / (1 - b2 ** (t + 1))
        P = P - lr * mh / (np.sqrt(vh) + eps)
        P[0] = np.clip(P[0], 0.0, 1.0)
        P[1] = np.clip(P[1], 0.0, 1.0)
    return P[0], P[1], P[2]


def _polish(centers, radii):
    n = len(centers)
    I, J = np.triu_indices(n, 1)
    npair = len(I)
    z0 = np.concatenate([centers[:, 0], centers[:, 1], radii])

    def f(z):
        return -np.sum(z[2 * n:])

    gf = np.zeros(3 * n)
    gf[2 * n:] = -1.0

    def fj(z):
        return gf

    def cons(z):
        x, y, r = z[:n], z[n:2 * n], z[2 * n:]
        d = np.sqrt((x[I] - x[J]) ** 2 + (y[I] - y[J]) ** 2 + 1e-18)
        return np.concatenate([d - r[I] - r[J], x - r, 1 - x - r, y - r, 1 - y - r])

    ar = np.arange(npair)
    an = np.arange(n)

    def cjac(z):
        x, y = z[:n], z[n:2 * n]
        dx = x[I] - x[J]
        dy = y[I] - y[J]
        d = np.sqrt(dx * dx + dy * dy + 1e-18)
        Jm = np.zeros((npair + 4 * n, 3 * n))
        Jm[ar, I] = dx / d
        Jm[ar, J] = -dx / d
        Jm[ar, n + I] = dy / d
        Jm[ar, n + J] = -dy / d
        Jm[ar, 2 * n + I] = -1
        Jm[ar, 2 * n + J] = -1
        o = npair
        Jm[o + an, an] = 1; Jm[o + an, 2 * n + an] = -1; o += n
        Jm[o + an, an] = -1; Jm[o + an, 2 * n + an] = -1; o += n
        Jm[o + an, n + an] = 1; Jm[o + an, 2 * n + an] = -1; o += n
        Jm[o + an, n + an] = -1; Jm[o + an, 2 * n + an] = -1
        return Jm

    bounds = [(0, 1)] * (2 * n) + [(0, 0.5)] * n
    try:
        res = minimize(f, z0, jac=fj, method="SLSQP", bounds=bounds,
                       constraints=[{"type": "ineq", "fun": cons, "jac": cjac}],
                       options={"maxiter": 400, "ftol": 1e-13})
        z = res.x
    except Exception:
        z = z0
    c = np.stack([z[:n], z[n:2 * n]], axis=1)
    c = np.clip(c, 0.0, 1.0)
    return c


def solve(n=26):
    t0 = time.time()
    budget = 200.0
    rng = np.random.default_rng(12345)
    B = 64
    best_c, best_r, best_s = None, None, -1.0

    def consider(c):
        nonlocal best_c, best_r, best_s
        r = _lp_radii(c)
        r = np.maximum(r - 1e-12, 0)
        if not _valid(c, r):
            r = _shrink_radii(c, r.copy())
        s = r.sum()
        if _valid(c, r) and s > best_s:
            best_c, best_r, best_s = c.copy(), r.copy(), s
        return s

    batch = 0
    while time.time() - t0 < budget:
        perturb = best_c is not None and batch % 2 == 1 and (time.time() - t0) > 0.35 * budget
        if perturb:
            X = np.repeat(best_c[None, :, 0], B, 0).copy()
            Y = np.repeat(best_c[None, :, 1], B, 0).copy()
            R = np.repeat(best_r[None], B, 0).copy() * 0.9
            sig = rng.uniform(0.005, 0.06, size=(B, 1))
            X += sig * rng.standard_normal((B, n))
            Y += sig * rng.standard_normal((B, n))
            for b in range(B):
                k = rng.integers(1, 4)
                idx = rng.choice(n, k, replace=False)
                X[b, idx] = rng.uniform(0.05, 0.95, k)
                Y[b, idx] = rng.uniform(0.05, 0.95, k)
                R[b, idx] = 0.03
            X = np.clip(X, 0.01, 0.99); Y = np.clip(Y, 0.01, 0.99)
            X, Y, R = _adam_batch(X, Y, R, 2500, 0.01, 2e-4, 100.0, 1e5)
        else:
            X = rng.uniform(0.05, 0.95, (B, n))
            Y = rng.uniform(0.05, 0.95, (B, n))
            R = rng.uniform(0.02, 0.1, (B, n))
            X, Y, R = _adam_batch(X, Y, R, 3500, 0.02, 2e-4, 10.0, 1e5)
        batch += 1
        # quick scoring with LP
        scores = []
        for b in range(B):
            c = np.stack([X[b], Y[b]], 1)
            scores.append(_lp_radii(c).sum())
        order = np.argsort(scores)[::-1]
        for b in order[:4]:
            if time.time() - t0 > budget + 30:
                break
            c = np.stack([X[b], Y[b]], 1)
            r = _lp_radii(c)
            c2 = _polish(c, r)
            consider(c2)
            consider(c)

    if best_c is None:
        c = rng.uniform(0.1, 0.9, (n, 2))
        return c, _shrink_radii(c, np.full(n, 0.01))
    return best_c, best_r
# EVOLVE-BLOCK-END
