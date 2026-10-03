# EVOLVE-BLOCK-START
import math
import time

import numpy as np


def _dp(N):
    f = [0.0] * (N + 1)
    ch = [None] * (N + 1)
    for t in range(1, N + 1):
        best, bc = f[t - 1], ('pad',)
        mmax = (t + 1) // 2 + 1
        for m in range(1, mmax + 1):
            # j = 0: plain grid
            if m * m <= t and m > best + 1e-12:
                best, bc = float(m), ('grid', m)
            jlo = int(math.isqrt(max(0, m * m - t)))
            while jlo * jlo < m * m - t:
                jlo += 1
            for j in range(max(1, jlo), m):
                base = m * m - j * j
                if base > t:
                    continue
                k = t - base
                v = base / m + (j / m) * f[k]
                if v > best + 1e-12:
                    best, bc = v, ('block', m, j, k)
        f[t] = best
        ch[t] = bc
    return f, ch


def _build(t, ch, x0, y0, L, out):
    while t > 0 and ch[t][0] == 'pad':
        t -= 1
    if t <= 0:
        return
    c = ch[t]
    if c[0] == 'grid':
        m = c[1]
        s = L / m
        for a in range(m):
            for b in range(m):
                out.append((x0 + a * s, y0 + b * s, s))
        return
    _, m, j, k = c
    s = L / m
    for a in range(m):
        for b in range(m):
            if a < j and b < j:
                continue
            out.append((x0 + a * s, y0 + b * s, s))
    _build(k, ch, x0, y0, L * j / m, out)


def _relations(sq):
    n = len(sq)
    rel = {}
    alts = {}
    for i in range(n):
        xi, yi, si = sq[i]
        for j in range(i + 1, n):
            xj, yj, sj = sq[j]
            c = [(xj - (xi + si), i, j, 0), (xi - (xj + sj), j, i, 0),
                 (yj - (yi + si), i, j, 1), (yi - (yj + sj), j, i, 1)]
            c.sort(key=lambda z: -z[0])
            rel[(i, j)] = c[0][1:]
            a = [z[1:] for z in c[1:] if z[0] >= c[0][0] - 1e-9 and z[0] >= -1e-9]
            if a:
                alts[(i, j)] = a
    return rel, alts


def _lp(n, rel):
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    rows, cols, vals = [], [], []
    r = 0
    for (a, b, d) in rel.values():
        off = 0 if d == 0 else n
        rows += [r, r, r]
        cols += [off + a, 2 * n + a, off + b]
        vals += [1.0, 1.0, -1.0]
        r += 1
    for i in range(n):
        rows += [r, r]; cols += [i, 2 * n + i]; vals += [1.0, 1.0]; r += 1
        rows += [r, r]; cols += [n + i, 2 * n + i]; vals += [1.0, 1.0]; r += 1
    A = coo_matrix((vals, (rows, cols)), shape=(r, 3 * n)).tocsr()
    bvec = np.zeros(r)
    bvec[r - 2 * n:] = 1.0
    c = np.zeros(3 * n)
    c[2 * n:] = -1.0
    try:
        res = linprog(c, A_ub=A, b_ub=bvec, bounds=[(0, 1)] * (3 * n), method='highs')
    except Exception:
        return None, -1
    if res.status != 0:
        return None, -1
    x = res.x
    sq = [(x[i], x[n + i], x[2 * n + i]) for i in range(n)]
    return sq, -res.fun


def _valid(sq, tol=1e-12):
    n = len(sq)
    for i in range(n):
        x, y, s = sq[i]
        if s < 0 or x < -tol or y < -tol or x + s > 1 + tol or y + s > 1 + tol:
            return False
    for i in range(n):
        xi, yi, si = sq[i]
        if si <= 0:
            continue
        for j in range(i + 1, n):
            xj, yj, sj = sq[j]
            if sj <= 0:
                continue
            ox = min(xi + si, xj + sj) - max(xi, xj)
            oy = min(yi + si, yj + sj) - max(yi, yj)
            if ox > tol and oy > tol:
                return False
    return True


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    f, ch = _dp(n)
    sq = []
    _build(n, ch, 0.0, 0.0, 1.0, sq)
    sq = sq[:n]
    while len(sq) < n:
        sq.append((0.0, 0.0, 0.0))
    base_sq = list(sq)
    base_val = sum(s for _, _, s in sq)

    best_sq, best_val = base_sq, base_val
    if n <= 60:
        try:
            deadline = t0 + 20.0
            cur, cur_val = list(sq), base_val
            rel, alts = _relations(cur)
            s2, v2 = _lp(n, rel)
            if s2 is not None and v2 > cur_val + 1e-7:
                cur, cur_val = s2, v2
                rel, alts = _relations(cur)
            improved = True
            while improved and time.time() < deadline:
                improved = False
                for key, al in list(alts.items()):
                    if time.time() > deadline:
                        break
                    for alt in al:
                        r2 = dict(rel)
                        r2[key] = alt
                        s2, v2 = _lp(n, r2)
                        if s2 is not None and v2 > cur_val + 1e-7:
                            cur, cur_val = s2, v2
                            improved = True
                            break
                    if improved:
                        rel, alts = _relations(cur)
                        break
            if cur_val > best_val + 1e-7:
                eps = 1e-9
                shr = []
                for (x, y, s) in cur:
                    if s > 2 * eps:
                        shr.append((x + eps, y + eps, s - 2 * eps))
                    else:
                        shr.append((0.0, 0.0, 0.0))
                if _valid(shr):
                    best_sq, best_val = shr, sum(s for _, _, s in shr)
        except Exception:
            pass

    out = []
    for (x, y, s) in best_sq:
        if s <= 0:
            out.append((0.0, 0.0, 0.0, 0.0))
        else:
            cx = min(1.0, max(0.0, x + s / 2))
            cy = min(1.0, max(0.0, y + s / 2))
            out.append((cx, cy, 0.0, min(1.0, max(0.0, s))))
    return out
# EVOLVE-BLOCK-END
