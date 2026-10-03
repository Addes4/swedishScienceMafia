# EVOLVE-BLOCK-START
import math
import time
import sys
import numpy as np
from scipy.optimize import minimize

_U0 = np.array([1.0, -1.0, -1.0, 1.0])
_U1 = np.array([1.0, 1.0, -1.0, -1.0])


class _Timeout(Exception):
    pass


# ---------------------------------------------------------------- grid search
def _grid_search(n, m, best_val, deadline):
    mm = m * m
    g = [False] * mm
    need = [math.floor(best_val * m + 1e-7) + 1]
    best = [None]
    place = []
    cnt = [0]

    def rec(pos, used, cur, A):
        cnt[0] += 1
        if (cnt[0] & 1023) == 0 and time.time() > deadline:
            raise _Timeout()
        while pos < mm and g[pos]:
            pos += 1
        if pos == mm or used == n:
            if cur >= need[0]:
                best[0] = list(place)
                need[0] = cur + 1
            return
        if cur + math.sqrt((n - used) * A) < need[0] - 1e-9:
            return
        r, c = divmod(pos, m)
        k = 0
        base = r * m + c
        while c + k < m and not g[base + k]:
            k += 1
        smax = min(k, m - r)
        for s in range(smax, 0, -1):
            for rr in range(r, r + s):
                b = rr * m + c
                for cc in range(s):
                    g[b + cc] = True
            place.append((r, c, s))
            rec(pos + s, used + 1, cur + s, A - s * s)
            place.pop()
            for rr in range(r, r + s):
                b = rr * m + c
                for cc in range(s):
                    g[b + cc] = False
        g[pos] = True
        rec(pos + 1, used, cur, A - 1)
        g[pos] = False

    try:
        rec(0, 0, 0, mm)
    except _Timeout:
        pass
    if best[0] is None:
        return None
    sq = [((c + s / 2.0) / m, (r + s / 2.0) / m, 0.0, s / m) for (r, c, s) in best[0]]
    return sq


# ---------------------------------------------------------------- geometry
def _sq_data(x, y, t, s):
    c = np.cos(t)
    sn = np.sin(t)
    h = 0.5 * s
    VX = x[:, None] + h[:, None] * (c[:, None] * _U0 - sn[:, None] * _U1)
    VY = y[:, None] + h[:, None] * (sn[:, None] * _U0 + c[:, None] * _U1)
    return VX, VY, c, sn


def _pair_sep(x, y, t, s, I, J):
    VX, VY, c, sn = _sq_data(x, y, t, s)
    P = len(I)
    if P == 0:
        return np.zeros(0), np.zeros((0, 2)), VX, VY, c, sn
    ax = np.stack([np.stack([c, sn], -1), np.stack([-sn, c], -1)], 1)
    A = np.concatenate([ax[I], ax[J]], 1)
    pi = A[:, :, 0:1] * VX[I][:, None, :] + A[:, :, 1:2] * VY[I][:, None, :]
    pj = A[:, :, 0:1] * VX[J][:, None, :] + A[:, :, 1:2] * VY[J][:, None, :]
    g1 = pj.min(2) - pi.max(2)
    g2 = pi.min(2) - pj.max(2)
    gap = np.maximum(g1, g2)
    k = gap.argmax(1)
    ar = np.arange(P)
    sep = gap[ar, k]
    axis = A[ar, k].copy()
    flip = g1[ar, k] < g2[ar, k]
    axis[flip] *= -1.0
    return sep, axis, VX, VY, c, sn


def _make_feasible(x, y, t, s):
    n = len(x)
    x = np.clip(x, 0.0, 1.0)
    y = np.clip(y, 0.0, 1.0)
    s = np.clip(s, 0.0, 1.0)
    I, J = np.triu_indices(n, 1)
    for _ in range(300):
        f = 0.5 * (np.abs(np.cos(t)) + np.abs(np.sin(t)))
        wall = np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y)) / f
        s = np.maximum(np.minimum(s, wall - 1e-12), 0.0)
        if n < 2:
            break
        sep, axis, *_ = _pair_sep(x, y, t, s, I, J)
        bad = (sep < 1e-12) & (s[I] > 0) & (s[J] > 0)
        if not bad.any():
            break
        d = 3e-12 - sep[bad]
        dd = np.zeros(n)
        np.maximum.at(dd, I[bad], d)
        np.maximum.at(dd, J[bad], d)
        s = np.maximum(s - dd, 0.0)
    return x, y, t, s


# ---------------------------------------------------------------- inflation
def _inflate(n, rng, iters=250, rot=True, init=None):
    if init is None:
        x = rng.uniform(0.1, 0.9, n)
        y = rng.uniform(0.1, 0.9, n)
        t = rng.uniform(0, math.pi / 2, n) if rot else np.zeros(n)
        s = np.full(n, 0.02)
    else:
        x, y, t, s = [a.copy() for a in init]
    I, J = np.triu_indices(n, 1)
    for it in range(iters):
        frac = it / iters
        gr = 0.03 * (1 - frac) + 0.002
        sep, axis, VX, VY, c, sn = _pair_sep(x, y, t, s, I, J)
        f = 0.5 * (np.abs(c) + np.abs(sn))
        h = s * f
        slack = np.minimum(np.minimum(x - h, 1 - x - h), np.minimum(y - h, 1 - y - h))
        np.minimum.at(slack, I, sep)
        np.minimum.at(slack, J, sep)
        s = s + 0.5 * np.clip(slack, 0, None) + gr * s
        for _k in range(4):
            sep, axis, VX, VY, c, sn = _pair_sep(x, y, t, s, I, J)
            ov = sep < 0
            if ov.any():
                d = -sep[ov] * 0.55
                ax = axis[ov]
                Io, Jo = I[ov], J[ov]
                dx = np.zeros(n)
                dy = np.zeros(n)
                np.add.at(dx, Io, -d * ax[:, 0])
                np.add.at(dy, Io, -d * ax[:, 1])
                np.add.at(dx, Jo, d * ax[:, 0])
                np.add.at(dy, Jo, d * ax[:, 1])
                x = x + dx
                y = y + dy
                if rot:
                    al = np.arctan2(ax[:, 1], ax[:, 0])
                    dt = np.zeros(n)
                    di = ((al - t[Io] + math.pi / 4) % (math.pi / 2)) - math.pi / 4
                    dj = ((al - t[Jo] + math.pi / 4) % (math.pi / 2)) - math.pi / 4
                    np.add.at(dt, Io, 0.1 * di)
                    np.add.at(dt, Jo, 0.1 * dj)
                    t = t + dt
            f = 0.5 * (np.abs(np.cos(t)) + np.abs(np.sin(t)))
            s = np.minimum(s, 1.0 / f)
            h = np.minimum(s * f, 0.5)
            x = np.clip(x, h, 1 - h)
            y = np.clip(y, h, 1 - h)
        sep, axis, *_ = _pair_sep(x, y, t, s, I, J)
        ov = sep < 0
        if ov.any():
            dd = np.zeros(n)
            np.maximum.at(dd, I[ov], -0.6 * sep[ov])
            np.maximum.at(dd, J[ov], -0.6 * sep[ov])
            s = np.maximum(s - dd, 0.0)
        jit = 0.002 * (1 - frac)
        x = x + rng.normal(0, jit, n)
        y = y + rng.normal(0, jit, n)
    return _make_feasible(x, y, t, s)


# ---------------------------------------------------------------- SLSQP
def _polish(x, y, t, s, maxiter=150, margin=0.08):
    n = len(x)
    I0, J0 = np.triu_indices(n, 1)
    dist = np.hypot(x[I0] - x[J0], y[I0] - y[J0])
    near = dist < 0.7072 * (s[I0] + s[J0]) + margin
    I, J = I0[near], J0[near]
    P = len(I)
    sep, axis, VX, VY, c, sn = _pair_sep(x, y, t, s, I, J)
    if P > 0:
        phi = np.arctan2(axis[:, 1], axis[:, 0])
        pI = axis[:, 0:1] * VX[I] + axis[:, 1:2] * VY[I]
        pJ = axis[:, 0:1] * VX[J] + axis[:, 1:2] * VY[J]
        cc = 0.5 * (pI.max(1) + pJ.min(1))
    else:
        phi = np.zeros(0)
        cc = np.zeros(0)
    z0 = np.concatenate([x, y, t, s, phi, cc])
    nv = 4 * n + 2 * P
    nc = 16 * n + 8 * P
    r4 = np.arange(4 * n)
    iidx = np.repeat(np.arange(n), 4)
    ii = np.repeat(I, 4)
    jj = np.repeat(J, 4)
    pp = np.repeat(np.arange(P), 4)
    rp = np.arange(4 * P)

    def unpack(z):
        return z[:n], z[n:2 * n], z[2 * n:3 * n], z[3 * n:4 * n], z[4 * n:4 * n + P], z[4 * n + P:]

    def obj(z):
        gr = np.zeros(nv)
        gr[3 * n:4 * n] = -1.0
        return -z[3 * n:4 * n].sum(), gr

    def cf(z):
        xx, yy, tt, ss, ph, c0 = unpack(z)
        VX, VY, _, _ = _sq_data(xx, yy, tt, ss)
        cp = np.cos(ph)[:, None]
        sp = np.sin(ph)[:, None]
        gi = c0[:, None] - (cp * VX[I] + sp * VY[I])
        gj = cp * VX[J] + sp * VY[J] - c0[:, None]
        return np.concatenate([VX.ravel(), VY.ravel(), 1 - VX.ravel(), 1 - VY.ravel(),
                               gi.ravel(), gj.ravel()])

    def cj(z):
        xx, yy, tt, ss, ph, c0 = unpack(z)
        VX, VY, c, sn = _sq_data(xx, yy, tt, ss)
        h = 0.5 * ss[:, None]
        DXT = h * (-sn[:, None] * _U0 - c[:, None] * _U1)
        DYT = h * (c[:, None] * _U0 - sn[:, None] * _U1)
        DXS = 0.5 * (c[:, None] * _U0 - sn[:, None] * _U1)
        DYS = 0.5 * (sn[:, None] * _U0 + c[:, None] * _U1)
        Jm = np.zeros((nc, nv))
        Jm[r4, iidx] = 1.0
        Jm[r4, 2 * n + iidx] = DXT.ravel()
        Jm[r4, 3 * n + iidx] = DXS.ravel()
        Jm[4 * n + r4, n + iidx] = 1.0
        Jm[4 * n + r4, 2 * n + iidx] = DYT.ravel()
        Jm[4 * n + r4, 3 * n + iidx] = DYS.ravel()
        Jm[8 * n:16 * n] = -Jm[0:8 * n]
        if P > 0:
            cpr = np.repeat(np.cos(ph), 4)
            spr = np.repeat(np.sin(ph), 4)
            b = 16 * n
            Jm[b + rp, ii] = -cpr
            Jm[b + rp, n + ii] = -spr
            Jm[b + rp, 2 * n + ii] = -(cpr * DXT[I].ravel() + spr * DYT[I].ravel())
            Jm[b + rp, 3 * n + ii] = -(cpr * DXS[I].ravel() + spr * DYS[I].ravel())
            Jm[b + rp, 4 * n + pp] = -(-spr * VX[I].ravel() + cpr * VY[I].ravel())
            Jm[b + rp, 4 * n + P + pp] = 1.0
            b2 = b + 4 * P
            Jm[b2 + rp, jj] = cpr
            Jm[b2 + rp, n + jj] = spr
            Jm[b2 + rp, 2 * n + jj] = cpr * DXT[J].ravel() + spr * DYT[J].ravel()
            Jm[b2 + rp, 3 * n + jj] = cpr * DXS[J].ravel() + spr * DYS[J].ravel()
            Jm[b2 + rp, 4 * n + pp] = -spr * VX[J].ravel() + cpr * VY[J].ravel()
            Jm[b2 + rp, 4 * n + P + pp] = -1.0
        return Jm

    bounds = [(0, 1)] * (2 * n) + [(None, None)] * n + [(0, 1)] * n + [(None, None)] * (2 * P)
    try:
        res = minimize(obj, z0, jac=True, method='SLSQP', bounds=bounds,
                       constraints=[{'type': 'ineq', 'fun': cf, 'jac': cj}],
                       options={'maxiter': maxiter, 'ftol': 1e-12})
        z = res.x
    except Exception:
        z = z0
    if not np.all(np.isfinite(z)):
        z = z0
    xx, yy, tt, ss, _, _ = unpack(z)
    return _make_feasible(xx.copy(), yy.copy(), tt.copy(), ss.copy())


# ---------------------------------------------------------------- main
def solve(n):
    if n <= 0:
        return []
    t0 = time.time()
    sys.setrecursionlimit(10000)
    k = math.isqrt(n)
    side = 1.0 / k
    best_sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    best_val = k * side

    # Phase 1: integer-grid branch and bound
    mmax = max(8, 2 * k + 4)
    grid_budget = 16.0
    per = grid_budget / mmax
    for m in range(1, mmax + 1):
        if time.time() - t0 > grid_budget + 1:
            break
        sq = _grid_search(n, m, best_val, time.time() + per)
        if sq is not None:
            v = sum(q[3] for q in sq)
            if v > best_val + 1e-9:
                best_val = v
                best_sq = sq

    # Phase 2: inflation multistart + SLSQP polish
    deadline = t0 + 45.0
    rng = np.random.default_rng(12345)
    if n >= 2:
        gx = np.array([q[0] for q in best_sq] + [0.5] * (n - len(best_sq)))
        gy = np.array([q[1] for q in best_sq] + [0.5] * (n - len(best_sq)))
        gs = np.array([q[3] for q in best_sq] + [0.0] * (n - len(best_sq)))
        nz = n - len(best_sq)
        attempt = 0
        maxit = 150 if n <= 20 else 80
        while time.time() < deadline - 4.0:
            attempt += 1
            try:
                if attempt % 4 == 0:
                    x = gx + rng.normal(0, 0.01, n)
                    y = gy + rng.normal(0, 0.01, n)
                    if nz > 0:
                        x[-nz:] = rng.uniform(0.05, 0.95, nz)
                        y[-nz:] = rng.uniform(0.05, 0.95, nz)
                    t = rng.normal(0, 0.03, n)
                    s = gs * 0.9
                    if nz > 0:
                        s[-nz:] = 0.03
                    x, y, t, s = _inflate(n, rng, iters=60, rot=True, init=(x, y, t, s))
                else:
                    rot = (attempt % 2 == 1)
                    x, y, t, s = _inflate(n, rng, iters=250, rot=rot)
                if time.time() > deadline - 2.0:
                    break
                x, y, t, s = _polish(x, y, t, s, maxiter=maxit)
                v = float(s.sum())
                if v > best_val + 1e-9:
                    best_val = v
                    best_sq = [(float(x[i]), float(y[i]),
                                float((t[i] / (2 * math.pi)) % 1.0), float(s[i]))
                               for i in range(n)]
            except Exception:
                continue

    out = []
    for q in best_sq:
        cx = min(max(q[0], 0.0), 1.0)
        cy = min(max(q[1], 0.0), 1.0)
        a = q[2] % 1.0
        if not (0.0 <= a <= 1.0):
            a = 0.0
        sd = min(max(q[3], 0.0), 1.0)
        out.append((cx, cy, a, sd))
    out += [(0.0, 0.0, 0.0, 0.0)] * (n - len(out))
    return out[:n]
# EVOLVE-BLOCK-END
