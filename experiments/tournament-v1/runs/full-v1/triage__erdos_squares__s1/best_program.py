# EVOLVE-BLOCK-START
"""Hierarchical grid layouts (DP) + penalty-based continuous post-optimisation."""
import math
import time
import numpy as np

NEG = -1e18
TWO_PI = 2.0 * math.pi


def _build_plans(N, kmax=6):
    F = [0.0] * (N + 1)
    PL = [None] * (N + 1)
    ks = list(range(2, kmax + 1))
    G = {}
    CH = {}
    for k in ks:
        K2 = k * k
        G[k] = [[NEG] * (N + 1) for _ in range(K2 + 1)]
        CH[k] = [[0] * (N + 1) for _ in range(K2 + 1)]
        for j in range(K2 + 1):
            G[k][j][0] = 0.0
    for n in range(1, N + 1):
        best = 1.0
        plan = None
        cps = {}
        for k in ks:
            K2 = k * k
            Gk = G[k]
            gp = [NEG] * (K2 + 1)
            cp = [0] * (K2 + 1)
            for j in range(1, K2 + 1):
                bv = NEG
                bt = 0
                for t in range(0, n):
                    prev = gp[j - 1] if t == 0 else Gk[j - 1][n - t]
                    if prev < -1e17:
                        continue
                    v = prev + F[t] / k
                    if v > bv:
                        bv = v
                        bt = t
                gp[j] = bv
                cp[j] = bt
            if gp[K2] > best + 1e-12:
                best = gp[K2]
                plan = (k, 0, 0, cp)
            for m in range(2, k):
                r = K2 - m * m
                for tb in range(1, n):
                    base = Gk[r][n - tb]
                    if base < -1e17:
                        continue
                    v = base + (m / k) * F[tb]
                    if v > best + 1e-12:
                        best = v
                        plan = (k, m, tb, cp)
        F[n] = best
        PL[n] = plan
        for k in ks:
            K2 = k * k
            Gk = G[k]
            for j in range(1, K2 + 1):
                bv = NEG
                bt = 0
                for t in range(0, n + 1):
                    prev = Gk[j - 1][n - t]
                    if prev < -1e17:
                        continue
                    v = prev + F[t] / k
                    if v > bv:
                        bv = v
                        bt = t
                Gk[j][n] = bv
                CH[k][j][n] = bt
    return F, PL, CH


def _place(n, x0, y0, size, PL, CH, out):
    if n <= 0:
        return
    plan = PL[n]
    if plan is None:
        out.append((x0 + size / 2, y0 + size / 2, 0.0, size))
        return
    k, m, tb, cp = plan
    cell = size / k
    r = k * k - m * m
    c = n - tb
    counts = []
    for j in range(r, 0, -1):
        if c == n:
            t = cp[j]
        else:
            t = CH[k][j][c]
        counts.append(t)
        c -= t
    idx = 0
    if m > 0:
        _place(tb, x0, y0, m * cell, PL, CH, out)
    for i in range(k):
        for j in range(k):
            if m > 0 and i < m and j < m:
                continue
            t = counts[idx]
            idx += 1
            _place(t, x0 + i * cell, y0 + j * cell, cell, PL, CH, out)


def _pair_depth(P, I, J):
    th = TWO_PI * P[:, 2]
    c = np.cos(th)
    s = np.sin(th)
    U = np.stack([c, s], 1)
    V = np.stack([-s, c], 1)
    h = P[:, 3] / 2
    C = P[:, :2]
    axes = np.stack([U[I], V[I], U[J], V[J]], 1)
    d = C[J] - C[I]
    dist = np.abs(np.einsum('mac,mc->ma', axes, d))
    ri = h[I, None] * (np.abs(np.einsum('mac,mc->ma', axes, U[I])) +
                       np.abs(np.einsum('mac,mc->ma', axes, V[I])))
    rj = h[J, None] * (np.abs(np.einsum('mac,mc->ma', axes, U[J])) +
                       np.abs(np.einsum('mac,mc->ma', axes, V[J])))
    return (ri + rj - dist).min(1)


def _bviol(P):
    th = TWO_PI * P[:, 2]
    ext = P[:, 3] / 2 * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    v = 0.0
    for q in (0, 1):
        x = P[:, q]
        v = v + np.maximum(ext - x, 0) + np.maximum(x + ext - 1, 0)
    return v


def _feasible(P):
    m = P[:, 3] > 1e-12
    Q = P[m]
    q = len(Q)
    if q == 0:
        return True
    if np.any(_bviol(Q) > 0):
        return False
    if np.any(Q[:, :2] < 0) or np.any(Q[:, :2] > 1):
        return False
    if q > 1:
        I, J = np.triu_indices(q, 1)
        if np.max(_pair_depth(Q, I, J)) > -1e-12:
            return False
    return True


def _repair(P):
    P = P.copy()
    P[:, 0:2] = np.clip(P[:, 0:2], 0, 1)
    P[:, 2] = np.mod(P[:, 2], 1.0)
    P[:, 3] = np.clip(P[:, 3], 0, 1)
    eps = 1e-7
    while eps < 0.3:
        Q = P.copy()
        Q[:, 3] *= (1 - eps)
        if _feasible(Q):
            return Q
        eps *= 2.5
    return None


class _Timeout(Exception):
    pass


def _optimise(P0, n, deadline):
    I, J = np.triu_indices(n, 1)
    best = None
    bestval = -1.0
    x = P0.flatten()
    lo = np.tile([0.0, 0.0, -0.5, 0.0], n)
    hi = np.tile([1.0, 1.0, 1.5, 1.0], n)
    bounds = list(zip(lo, hi))

    def f(xv, mu):
        if time.time() > deadline:
            raise _Timeout()
        P = xv.reshape(n, 4)
        pen = 0.0
        if n > 1:
            d = _pair_depth(P, I, J)
            pen = np.sum(np.maximum(d, 0) ** 2)
        b = _bviol(P)
        pen = pen + np.sum(b ** 2)
        return -np.sum(P[:, 3]) + mu * pen

    try:
        from scipy.optimize import minimize
        for mu in (10.0, 100.0, 1e3, 1e4, 1e5, 1e6):
            res = minimize(f, x, args=(mu,), method='L-BFGS-B', bounds=bounds,
                           options={'maxiter': 150, 'eps': 1e-7})
            x = res.x
            Q = _repair(x.reshape(n, 4))
            if Q is not None:
                v = Q[:, 3].sum()
                if v > bestval:
                    bestval = v
                    best = Q
    except _Timeout:
        pass
    except Exception:
        pass
    return best, bestval


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t_start = time.time()
    F, PL, CH = _build_plans(n)
    out = []
    _place(n, 0.0, 0.0, 1.0, PL, CH, out)
    out = out[:n]
    base = np.zeros((n, 4))
    for i, (x, y, a, s) in enumerate(out):
        base[i] = (x, y, a, s * (1 - 1e-8))
    base_val = base[:, 3].sum()
    result = base

    if n <= 40 and n >= 2:
        deadline = t_start + 12.0
        rng = np.random.default_rng(1)
        for trial in range(3):
            if time.time() > deadline:
                break
            P0 = base.copy()
            P0[:, 3] = P0[:, 3] / (1 - 1e-8)
            zero = P0[:, 3] < 1e-12
            if trial > 0:
                P0[~zero, :2] += rng.normal(0, 0.01 * trial, (int((~zero).sum()), 2))
                P0[~zero, 2] += rng.normal(0, 0.01 * trial, int((~zero).sum()))
                P0[~zero, 3] *= 0.97
            P0[zero, :2] = rng.random((int(zero.sum()), 2))
            P0[zero, 3] = 0.0
            Q, v = _optimise(P0, n, deadline)
            if Q is not None and v > base_val + 1e-9:
                result = Q
                base_val = v
    return [(float(min(max(r[0], 0.0), 1.0)), float(min(max(r[1], 0.0), 1.0)),
             float(min(max(r[2], 0.0), 1.0)), float(min(max(r[3], 0.0), 1.0)))
            for r in result]
# EVOLVE-BLOCK-END
