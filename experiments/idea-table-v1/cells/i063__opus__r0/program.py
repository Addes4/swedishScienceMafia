# EVOLVE-BLOCK-START
"""L-infinity power-diagram Lloyd relaxation + exact LP side sizing, combined with
randomised grid tilings. Best valid configuration is returned."""
import math
import time
import random
import numpy as np
from scipy.optimize import linprog


# ---------------------------------------------------------------- LP sizing
def lp_sides(c):
    """Given centres c (n,2), maximise sum of sides of axis-aligned squares
    centred at c with disjoint interiors inside the unit square."""
    n = len(c)
    bd = np.minimum(np.minimum(c[:, 0], 1 - c[:, 0]), np.minimum(c[:, 1], 1 - c[:, 1]))
    ub = np.clip(2 * bd, 0, 1)
    if n == 1:
        return ub.copy()
    ii, jj = np.triu_indices(n, 1)
    d = np.maximum(np.abs(c[ii, 0] - c[jj, 0]), np.abs(c[ii, 1] - c[jj, 1]))
    m = len(ii)
    A = np.zeros((m, n))
    A[np.arange(m), ii] = 1.0
    A[np.arange(m), jj] = 1.0
    try:
        res = linprog(-np.ones(n), A_ub=A, b_ub=2 * d,
                      bounds=list(zip(np.zeros(n), ub)), method="highs")
        if res.status == 0:
            s = np.clip(res.x, 0, ub)
            return s
    except Exception:
        pass
    return np.zeros(n)


def valid_scale(c, s):
    """Safety: shrink sides if any constraint violated numerically."""
    n = len(c)
    s = s * (1 - 1e-9)
    bd = np.minimum(np.minimum(c[:, 0], 1 - c[:, 0]), np.minimum(c[:, 1], 1 - c[:, 1]))
    s = np.minimum(s, 2 * bd)
    for i in range(n):
        for j in range(i + 1, n):
            d = max(abs(c[i, 0] - c[j, 0]), abs(c[i, 1] - c[j, 1]))
            if s[i] + s[j] > 2 * d:
                f = 2 * d / (s[i] + s[j]) if s[i] + s[j] > 0 else 0
                s[i] *= f
                s[j] *= f
    return np.maximum(s, 0)


# ---------------------------------------------------------------- Lloyd
def lloyd(n, rng, deadline, iters=80, G=90):
    xs = (np.arange(G) + 0.5) / G
    PX, PY = np.meshgrid(xs, xs, indexing="ij")
    PX = PX.ravel()
    PY = PY.ravel()
    bdp = np.minimum(np.minimum(PX, 1 - PX), np.minimum(PY, 1 - PY))
    sites = rng.random((n, 2)) * 0.9 + 0.05
    w = np.zeros(n)
    best_val, best = -1, None
    eta = 0.5
    for it in range(iters):
        if time.time() > deadline:
            break
        D = np.maximum(np.abs(PX[None, :] - sites[:, :1]), np.abs(PY[None, :] - sites[:, 1:])) - w[:, None]
        if n >= 2:
            part = np.partition(D, 1, axis=0)
            gap = (part[1] - part[0]) / 2
        else:
            gap = np.full(PX.shape, 1.0)
        lab = np.argmin(D, axis=0)
        clr = np.minimum(gap, bdp)
        r = np.zeros(n)
        new_sites = sites.copy()
        order = np.lexsort((clr, lab))
        labs_sorted = lab[order]
        last = np.searchsorted(labs_sorted, np.arange(n), side="right") - 1
        present = np.bincount(lab, minlength=n) > 0
        for i in range(n):
            if present[i]:
                k = order[last[i]]
                new_sites[i] = (PX[k], PY[k])
                r[i] = clr[k]
            else:
                k = int(np.argmax(clr))
                new_sites[i] = (PX[k], PY[k]) + rng.normal(0, 0.01, 2)
                r[i] = 0
                w[i] = w.max()
        sites = 0.5 * sites + 0.5 * np.clip(new_sites, 0.0, 1.0)
        w += eta * (r.mean() - r)
        w -= w.mean()
        if it % 8 == 7 or it == iters - 1:
            s = lp_sides(sites)
            v = s.sum()
            if v > best_val:
                best_val, best = v, (sites.copy(), s.copy())
            # also try snapping centres to a grid-like configuration via LP directly
    return best_val, best


# ---------------------------------------------------------------- grid tilings
def random_tiling(m, n, p, rnd):
    occ = [[False] * m for _ in range(m)]
    sq = []
    total = 0
    for r in range(m):
        for c in range(m):
            if occ[r][c]:
                continue
            t = 1
            while r + t < m + 0 and c + t < m + 0 + 0 and r + t <= m - 1 and c + t <= m - 1:
                ok = True
                for k in range(t + 1):
                    if occ[r + t][c + k] or occ[r + k][c + t]:
                        ok = False
                        break
                if not ok:
                    break
                t += 1
            if rnd.random() < p:
                s = t
            else:
                s = rnd.randint(1, t)
            for a in range(r, r + s):
                for b in range(c, c + s):
                    occ[a][b] = True
            sq.append((r, c, s))
            total += s
            if len(sq) > n:
                return None, 0
    return sq, total


def grid_search(n, deadline):
    rnd = random.Random(12345)
    best_val, best = -1.0, None
    k0 = max(1, math.isqrt(n))
    mmax = min(max(2 * k0 + 4, 6), 24)
    ms = list(range(k0, mmax + 1))
    while time.time() < deadline:
        for m in ms:
            if time.time() > deadline:
                break
            for _ in range(30):
                p = rnd.random()
                sq, total = random_tiling(m, n, p, rnd)
                if sq is None:
                    continue
                v = total / m
                if v > best_val + 1e-12:
                    best_val = v
                    best = [((c + s / 2) / m, (r + s / 2) / m, 0.0, s / m) for (r, c, s) in sq]
    return best_val, best


# ---------------------------------------------------------------- main
def solve(n):
    t0 = time.time()
    candidates = []
    k = math.isqrt(n)
    side = 1.0 / k
    base = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    candidates.append((k * side, base))

    gv, gb = grid_search(n, t0 + (14.0 if n <= 200 else 4.0))
    if gb is not None:
        candidates.append((gv, gb))

    rng = np.random.default_rng(7)
    lloyd_deadline = t0 + 40.0
    G = 90 if n <= 60 else 60
    while time.time() < lloyd_deadline and n <= 400:
        v, b = lloyd(n, rng, lloyd_deadline, G=G)
        if b is not None:
            c, s = b
            s = valid_scale(c, s)
            candidates.append((float(s.sum()),
                               [(float(c[i, 0]), float(c[i, 1]), 0.0, float(s[i])) for i in range(n)]))
        if time.time() - t0 > 25:
            break

    bv, bl = max(candidates, key=lambda x: x[0])
    out = []
    for (x, y, a, s) in bl:
        s = max(0.0, min(1.0, s * (1 - 1e-12)))
        out.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), 0.0, s))
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out[:n]
# EVOLVE-BLOCK-END
