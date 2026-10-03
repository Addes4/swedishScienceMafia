# EVOLVE-BLOCK-START
"""Block-substitution recurrence with axis-aligned grids and tilted
equal-square packings (Friedman-type) as substitutable blocks."""
import math
import time
import numpy as np

_LIB_CACHE = {}


# ---------------- geometry helpers for tilted packings ----------------
def _corners(x, y, th, a):
    c, s = np.cos(th), np.sin(th)
    h = a / 2.0
    off = np.array([[h, h], [-h, h], [-h, -h], [h, -h]])
    cx = x[:, None] + c[:, None] * off[None, :, 0] - s[:, None] * off[None, :, 1]
    cy = y[:, None] + s[:, None] * off[None, :, 0] + c[:, None] * off[None, :, 1]
    C = np.stack([cx, cy], axis=-1)  # (m,4,2)
    A = np.stack([np.stack([c, s], -1), np.stack([-s, c], -1)], axis=1)  # (m,2,2)
    return C, A


def _depths(x, y, th, a, I, J):
    C, A = _corners(x, y, th, a)
    axes = np.concatenate([A[I], A[J]], axis=1)  # (P,4,2)
    pi = np.einsum('pkd,pcd->pkc', axes, C[I])
    pj = np.einsum('pkd,pcd->pkc', axes, C[J])
    ov = np.minimum(pi.max(-1), pj.max(-1)) - np.maximum(pi.min(-1), pj.min(-1))
    return ov.min(axis=1), C


def _penalty(v, a, m, I, J):
    x, y, th = v[:m], v[m:2 * m], v[2 * m:]
    d, C = _depths(x, y, th, a, I, J)
    p = np.sum(np.clip(d, 0, None) ** 2)
    p += np.sum(np.clip(-C, 0, None) ** 2) + np.sum(np.clip(C - 1, 0, None) ** 2)
    return p


def _verify(x, y, th, a, I, J):
    d, C = _depths(x, y, th, a, I, J)
    if len(d) and d.max() > -1e-12:
        return False
    return C.min() >= 0.0 and C.max() <= 1.0


def _optimise_equal(m, budget):
    """Penalty optimisation for m equal (possibly rotated) squares."""
    from scipy.optimize import minimize
    t0 = time.time()
    I, J = np.triu_indices(m, 1)
    rng = np.random.default_rng(12345 + m)
    best = None
    best_a = 1.0 / math.ceil(math.sqrt(m))
    while time.time() - t0 < budget:
        a = best_a * 0.98
        v = np.concatenate([rng.uniform(0.2, 0.8, 2 * m), rng.uniform(0, math.pi / 2, m)])
        feas_v, feas_a = None, None
        f = 1.03
        while time.time() - t0 < budget and f > 1.0005:
            r = minimize(_penalty, v, args=(a, m, I, J), method='L-BFGS-B',
                         options={'maxiter': 300})
            if r.fun < 1e-16:
                feas_v, feas_a = r.x.copy(), a
                v = r.x
                a *= f
            else:
                if feas_v is None:
                    break
                f = math.sqrt(f)
                v = feas_v.copy()
                a = feas_a * f
        if feas_v is not None:
            aa = feas_a * (1 - 2e-6)
            x, y, th = feas_v[:m], feas_v[m:2 * m], feas_v[2 * m:]
            if _verify(x, y, th, aa, I, J) and (best is None or aa > best[0]):
                best = (aa, x.copy(), y.copy(), th.copy())
                best_a = max(best_a, aa)
    if best is None:
        return None
    aa, x, y, th = best
    lay = []
    for i in range(m):
        ang = (th[i] / (2 * math.pi)) % 0.25
        lay.append((float(x[i]), float(y[i]), float(ang), float(aa)))
    return m * aa, lay


def _friedman5():
    s = 2.0 + 1.0 / math.sqrt(2.0)
    lay = [(0.5 / s, 0.5 / s, 0.0, 1 / s), (1 - 0.5 / s, 0.5 / s, 0.0, 1 / s),
           (0.5 / s, 1 - 0.5 / s, 0.0, 1 / s), (1 - 0.5 / s, 1 - 0.5 / s, 0.0, 1 / s),
           (0.5, 0.5, 0.125, 1 / s)]
    return 5.0 / s, lay


def _library(n):
    lib = {}
    if n >= 5:
        lib[5] = _friedman5()
    total = 0.0
    for m in (10, 11):
        if m <= n and total < 4.0:
            if m not in _LIB_CACHE:
                t = time.time()
                try:
                    _LIB_CACHE[m] = _optimise_equal(m, 1.5)
                except Exception:
                    _LIB_CACHE[m] = None
                total += time.time() - t
            if _LIB_CACHE[m] is not None:
                lib[m] = _LIB_CACHE[m]
    return lib


# ---------------- recurrence ----------------
def solve(n):
    lib = _library(n)
    V = [0.0] * (n + 1)
    ch = [None] * (n + 1)
    if n >= 1:
        V[1], ch[1] = 1.0, ('one',)
    for N in range(2, n + 1):
        best, bc = V[N - 1], ('zero',)
        if N in lib and lib[N][0] > best + 1e-12:
            best, bc = lib[N][0], ('lib', N)
        k = 2
        while 2 * k - 1 <= N:
            for t in range(k - 1, 0, -1):
                rest = k * k - t * t
                if rest > N:
                    break
                m = N - rest
                val = (rest + t * V[m]) / k
                if val > best + 1e-12:
                    best, bc = val, ('grid', k, t, m)
            k += 1
        V[N], ch[N] = best, bc

    out = []

    def build(N, x0, y0, L):
        while N > 0 and ch[N][0] == 'zero':
            out.append((0.0, 0.0, 0.0, 0.0))
            N -= 1
        if N == 0:
            return
        c = ch[N]
        if c[0] == 'one':
            out.append((x0 + L / 2, y0 + L / 2, 0.0, L))
        elif c[0] == 'lib':
            for (cx, cy, ang, sd) in lib[c[1]][1]:
                out.append((x0 + cx * L, y0 + cy * L, ang, sd * L))
        else:
            _, k, t, m = c
            cell = L / k
            for i in range(k):
                for j in range(k):
                    if i < t and j < t:
                        continue
                    out.append((x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell, 0.0, cell))
            if m > 0:
                build(m, x0, y0, t * cell)

    build(n, 0.0, 0.0, 1.0)
    res = []
    for (x, y, a, s) in out[:n]:
        res.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0),
                    min(max(a, 0.0), 1.0), min(max(s, 0.0), 1.0)))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
