# EVOLVE-BLOCK-START
"""Grid/merge construction for every n, plus an exact big-M MILP (axis-aligned) for small n."""
import math
import time
import numpy as np


def _pack(k, sizes):
    occ = [[False] * k for _ in range(k)]
    pos = []
    for m in sizes:
        found = False
        for r in range(k - m + 1):
            for c in range(k - m + 1):
                if all(not occ[r + a][c + b] for a in range(m) for b in range(m)):
                    for a in range(m):
                        for b in range(m):
                            occ[r + a][c + b] = True
                    pos.append((r, c, m))
                    found = True
                    break
            if found:
                break
        if not found:
            return None
    for r in range(k):
        for c in range(k):
            if not occ[r][c]:
                pos.append((r, c, 1))
    return pos


def _construct(n):
    best = (-1.0, None, None)
    kmax = min(40, math.isqrt(n) + 4)
    for k in range(1, kmax + 1):
        cands = []

        def rec(start, cur, area):
            cands.append(list(cur))
            if len(cur) >= 4:
                return
            for m in range(start, 0, -1):
                if m < 2:
                    break
                if area + m * m <= k * k:
                    cur.append(m)
                    rec(m, cur, area + m * m)
                    cur.pop()

        rec(k, [], 0)
        for sizes in cands:
            units = k * k - sum(m * m for m in sizes)
            count = len(sizes) + units
            drop = count - n
            if drop > units:
                continue
            if drop < 0:
                drop = 0
            val = (sum(sizes) + units - drop) / k
            if val > best[0] + 1e-12:
                pos = _pack(k, sizes)
                if pos is None:
                    continue
                best = (val, k, pos, drop)
    val, k, pos, drop = best[0], best[1], best[2], best[3]
    res = []
    big = [p for p in pos if p[2] > 1]
    unit = [p for p in pos if p[2] == 1]
    unit = unit[:len(unit) - drop] if drop else unit
    for r, c, m in big + unit:
        res.append(((c + m / 2) / k, (r + m / 2) / k, 0.0, m / k))
    res = res[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return val, res


def _valid(sq, tol=1e-12):
    for i in range(len(sq)):
        xi, yi, _, si = sq[i]
        if si < 0 or xi - si / 2 < -tol or xi + si / 2 > 1 + tol or yi - si / 2 < -tol or yi + si / 2 > 1 + tol:
            return False
        for j in range(i):
            xj, yj, _, sj = sq[j]
            ox = (si + sj) / 2 - abs(xi - xj)
            oy = (si + sj) / 2 - abs(yi - yj)
            if ox > tol and oy > tol:
                return False
    return True


def _milp(n, target, tlimit):
    from scipy.optimize import milp, LinearConstraint, Bounds
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    P = len(pairs)
    nv = 3 * n + 4 * P
    # vars: x_i (0..n), y_i (n..2n), s_i (2n..3n), b (3n + 4p + t)
    rows, lo, hi = [], [], []

    def add(coefs, l, u):
        r = np.zeros(nv)
        for k_, v in coefs:
            r[k_] += v
        rows.append(r)
        lo.append(l)
        hi.append(u)

    for i in range(n):
        add([(i, 1), (2 * n + i, 1)], -np.inf, 1.0)
        add([(n + i, 1), (2 * n + i, 1)], -np.inf, 1.0)
    for i in range(n - 1):
        add([(2 * n + i, 1), (2 * n + i + 1, -1)], 0.0, np.inf)
    add([(0, 1), (2 * n, 0.5)], -np.inf, 0.5)
    add([(n, 1), (2 * n, 0.5)], -np.inf, 0.5)
    for p, (i, j) in enumerate(pairs):
        b = 3 * n + 4 * p
        # x_i + s_i <= x_j + (1-b0)
        add([(i, 1), (2 * n + i, 1), (j, -1), (b, 1)], -np.inf, 1.0)
        add([(j, 1), (2 * n + j, 1), (i, -1), (b + 1, 1)], -np.inf, 1.0)
        add([(n + i, 1), (2 * n + i, 1), (n + j, -1), (b + 2, 1)], -np.inf, 1.0)
        add([(n + j, 1), (2 * n + j, 1), (n + i, -1), (b + 3, 1)], -np.inf, 1.0)
        add([(b, 1), (b + 1, 1), (b + 2, 1), (b + 3, 1)], 1.0, np.inf)
    add([(2 * n + i, 1) for i in range(n)], target, np.inf)
    A = np.array(rows)
    c = np.zeros(nv)
    c[2 * n:3 * n] = -1.0
    integrality = np.zeros(nv)
    integrality[3 * n:] = 1
    res = milp(c, constraints=LinearConstraint(A, lo, hi), integrality=integrality,
               bounds=Bounds(np.zeros(nv), np.ones(nv)),
               options={"time_limit": tlimit, "disp": False})
    if res.x is None:
        return None
    x = res.x
    out = []
    eps = 2e-6
    for i in range(n):
        s = max(0.0, x[2 * n + i] - eps)
        cx = min(max(x[i] + x[2 * n + i] / 2, s / 2), 1 - s / 2)
        cy = min(max(x[n + i] + x[2 * n + i] / 2, s / 2), 1 - s / 2)
        out.append((cx, cy, 0.0, s))
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    val, best = _construct(n)
    if 2 <= n <= 16:
        try:
            remaining = 45 - (time.time() - t0)
            sol = _milp(n, val + 1e-6, remaining)
            if sol is not None and _valid(sol):
                if sum(s[3] for s in sol) > sum(s[3] for s in best):
                    best = sol
        except Exception:
            pass
    return best
# EVOLVE-BLOCK-END
