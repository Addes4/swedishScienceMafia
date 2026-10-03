# EVOLVE-BLOCK-START
import math
import random
import time
import numpy as np


def _dp(M, n):
    L = n + 1
    best = np.zeros((M + 1, M + 1, L), dtype=np.int64)
    for w in range(1, M + 1):
        for h in range(w, M + 1):
            cur = np.zeros(L, dtype=np.int64)
            if w == h and L > 1:
                cur[1:] = w
            # vertical splits
            k = w // 2
            if k >= 1:
                A = best[1:k + 1, h, :]
                B = best[w - np.arange(1, k + 1), h, :]
                C = np.zeros((k, L), dtype=np.int64)
                for i in range(L):
                    np.maximum(C[:, i:], A[:, i:i + 1] + B[:, :L - i], out=C[:, i:])
                cur = np.maximum(cur, C.max(axis=0))
            k = h // 2
            if k >= 1:
                idx1 = np.arange(1, k + 1)
                A = best[w, idx1, :]
                B = best[w, h - idx1, :]
                C = np.zeros((k, L), dtype=np.int64)
                for i in range(L):
                    np.maximum(C[:, i:], A[:, i:i + 1] + B[:, :L - i], out=C[:, i:])
                cur = np.maximum(cur, C.max(axis=0))
            cur = np.maximum.accumulate(cur)
            best[w, h, :] = cur
            best[h, w, :] = cur
    return best


def _build(best, x0, y0, w, h, c, out):
    T = int(best[w, h, c])
    if T == 0 or c == 0:
        return
    if w == h and T == w:
        out.append((x0, y0, w))
        return
    for w1 in range(1, w):
        arr = best[w1, h, 0:c + 1] + best[w - w1, h, c::-1]
        hits = np.nonzero(arr == T)[0]
        if len(hits):
            c1 = int(hits[0])
            _build(best, x0, y0, w1, h, c1, out)
            _build(best, x0 + w1, y0, w - w1, h, c - c1, out)
            return
    for h1 in range(1, h):
        arr = best[w, h1, 0:c + 1] + best[w, h - h1, c::-1]
        hits = np.nonzero(arr == T)[0]
        if len(hits):
            c1 = int(hits[0])
            _build(best, x0, y0, w, h1, c1, out)
            _build(best, x0, y0 + h1, w, h - h1, c - c1, out)
            return
    # should not happen; fallback leaf
    s = min(w, h)
    out.append((x0, y0, s))


def _valid(sq, tol=1e-12):
    k = len(sq)
    for (x, y, s) in sq:
        if x < -tol or y < -tol or x + s > 1 + tol or y + s > 1 + tol or s < 0:
            return False
    for i in range(k):
        xi, yi, si = sq[i]
        if si <= 0:
            continue
        for j in range(i + 1, k):
            xj, yj, sj = sq[j]
            if sj <= 0:
                continue
            ox = min(xi + si, xj + sj) - max(xi, xj)
            oy = min(yi + si, yj + sj) - max(yi, yj)
            if ox > tol and oy > tol:
                return False
    return True


def _lp_compact(sq, deadline):
    try:
        from scipy.optimize import linprog
        from scipy.sparse import coo_matrix
    except Exception:
        return None
    k = len(sq)
    if k < 2:
        return None
    base = sum(s for _, _, s in sq)
    bestsq, bestval = None, base
    trials = 0
    rng = random.Random(1)
    while trials < 6 and time.time() < deadline:
        rows, cols, vals = [], [], []
        r = 0
        for i in range(k):
            # x_i + s_i <= 1 ; y_i + s_i <= 1
            rows += [r, r]; cols += [3 * i, 3 * i + 2]; vals += [1, 1]; r += 1
            rows += [r, r]; cols += [3 * i + 1, 3 * i + 2]; vals += [1, 1]; r += 1
        for i in range(k):
            xi, yi, si = sq[i]
            for j in range(i + 1, k):
                xj, yj, sj = sq[j]
                gx = max(xj - (xi + si), xi - (xj + sj))
                gy = max(yj - (yi + si), yi - (yj + sj))
                if abs(gx - gy) < 1e-9:
                    usex = True if trials == 0 else (rng.random() < 0.5)
                else:
                    usex = gx > gy
                if usex:
                    if xi + si <= xj + 1e-9 and not (xj + sj <= xi + 1e-9 and xi > xj):
                        a, b = i, j
                    else:
                        a, b = j, i
                    d = 0
                else:
                    if yi + si <= yj + 1e-9 and not (yj + sj <= yi + 1e-9 and yi > yj):
                        a, b = i, j
                    else:
                        a, b = j, i
                    d = 1
                # pos_a + s_a - pos_b <= 0
                rows += [r, r, r]
                cols += [3 * a + d, 3 * a + 2, 3 * b + d]
                vals += [1, 1, -1]
                r += 1
        A = coo_matrix((vals, (rows, cols)), shape=(r, 3 * k)).tocsr()
        bub = np.zeros(r)
        bub[:2 * k] = 1.0
        c = np.zeros(3 * k)
        c[2::3] = -1.0
        try:
            res = linprog(c, A_ub=A, b_ub=bub, bounds=[(0, 1)] * (3 * k), method="highs")
        except Exception:
            res = None
        trials += 1
        if res is None or res.status != 0:
            continue
        z = res.x
        cand = [(max(0.0, z[3 * i]), max(0.0, z[3 * i + 1]), max(0.0, z[3 * i + 2])) for i in range(k)]
        val = sum(s for _, _, s in cand)
        if val > bestval + 1e-9 and _valid(cand, 1e-9):
            bestval, bestsq = val, cand
    return bestsq


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    M = min(44, max(20, 3 * math.isqrt(n) + 6))
    best = _dp(M, n)
    bm, bv = 1, -1.0
    for m in range(1, M + 1):
        v = best[m, m, n] / m
        if v > bv + 1e-12:
            bv, bm = v, m
    cells = []
    _build(best, 0, 0, bm, bm, n, cells)
    sq = [(x / bm, y / bm, s / bm) for (x, y, s) in cells]
    sq = sq[:n]
    if len(sq) <= 150:
        imp = _lp_compact(sq, t0 + 40)
        if imp is not None:
            sq = imp
    eps = 1e-11
    out = []
    for (x, y, s) in sq:
        s2 = max(0.0, s - 2 * eps)
        cx = min(1.0, max(0.0, x + s / 2))
        cy = min(1.0, max(0.0, y + s / 2))
        out.append((cx, cy, 0.0, s2))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
