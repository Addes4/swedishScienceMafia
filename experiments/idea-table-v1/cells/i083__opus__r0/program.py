# EVOLVE-BLOCK-START
"""Recursive grid/block construction with exact rationals, followed by an
LP refinement + active-set rational reconstruction post-processor."""
import math
import time
from fractions import Fraction


def _plan_table(n):
    F = [Fraction(0)] * (n + 1)
    P = [None] * (n + 1)
    P[0] = ('empty',)
    for m in range(1, n + 1):
        bv = F[m - 1]
        bp = ('zero',)
        r = math.isqrt(m)
        if r * r == m and Fraction(r) > bv:
            bv = Fraction(r)
            bp = ('grid', r, ())
        kmax = min((m + 1) // 2 + 1, r + 10)
        for k in range(2, kmax + 1):
            for a in range(1, k):
                base = k * k - a * a
                mm = m - base
                if mm < 0 or mm >= m:
                    continue
                val = (base + a * F[mm]) / k
                if val > bv:
                    bv = val
                    bp = ('grid', k, ((a, mm),))
            if k <= r + 4:
                for a1 in range(1, k):
                    for a2 in range(1, min(a1, k - a1) + 1):
                        base = k * k - a1 * a1 - a2 * a2
                        rest = m - base
                        if rest < 0:
                            continue
                        for m1 in range(0, rest + 1):
                            m2 = rest - m1
                            if m1 >= m or m2 >= m:
                                continue
                            val = (base + a1 * F[m1] + a2 * F[m2]) / k
                            if val > bv:
                                bv = val
                                bp = ('grid', k, ((a1, m1), (a2, m2)))
        F[m] = bv
        P[m] = bp
    return F, P


def _build(m, x0, y0, scale, P, out):
    plan = P[m]
    if plan[0] == 'empty':
        return
    if plan[0] == 'zero':
        _build(m - 1, x0, y0, scale, P, out)
        out.append((x0, y0, Fraction(0)))
        return
    _, k, blocks = plan
    cell = scale / k
    covered = set()
    o = 0
    for a, mm in blocks:
        _build(mm, x0 + o * cell, y0 + o * cell, a * cell, P, out)
        for i in range(o, o + a):
            for j in range(o, o + a):
                covered.add((i, j))
        o += a
    for i in range(k):
        for j in range(k):
            if (i, j) not in covered:
                out.append((x0 + (i + Fraction(1, 2)) * cell,
                            y0 + (j + Fraction(1, 2)) * cell, cell))


def _verify(sq):
    for (x, y, s) in sq:
        if s < 0:
            return False
        h = s / 2
        if x - h < 0 or x + h > 1 or y - h < 0 or y + h > 1:
            return False
    nz = [q for q in sq if q[2] > 0]
    for i in range(len(nz)):
        xi, yi, si = nz[i]
        for j in range(i + 1, len(nz)):
            xj, yj, sj = nz[j]
            d = (si + sj) / 2
            if abs(xi - xj) < d and abs(yi - yj) < d:
                return False
    return True


def _exact_solve(rows, nv, approx):
    """rows: list of (coeffs list of Fraction, rhs Fraction) equalities.
    Returns exact solution (free vars fixed to rationalised approx) or None."""
    M = [list(c) + [b] for c, b in rows]
    piv_cols = []
    r = 0
    nr = len(M)
    for col in range(nv):
        p = None
        for i in range(r, nr):
            if M[i][col] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][col]
        if pv != 1:
            M[r] = [v / pv for v in M[r]]
        for i in range(nr):
            if i != r and M[i][col] != 0:
                f = M[i][col]
                Mr = M[r]
                M[i] = [vi - f * vr for vi, vr in zip(M[i], Mr)]
        piv_cols.append(col)
        r += 1
        if r == nr:
            break
    for i in range(r, nr):
        if M[i][nv] != 0 and all(v == 0 for v in M[i][:nv]):
            return None
    pivset = set(piv_cols)
    sol = [None] * nv
    for c in range(nv):
        if c not in pivset:
            sol[c] = Fraction(approx[c]).limit_denominator(10000)
    for i, c in enumerate(piv_cols):
        val = M[i][nv]
        for c2 in range(nv):
            if c2 not in pivset and M[i][c2] != 0:
                val -= M[i][c2] * sol[c2]
        sol[c] = val
    return sol


def _lp_refine(sq, deadline):
    try:
        import numpy as np
        from scipy.optimize import linprog
    except Exception:
        return None
    nz = [q for q in sq if q[2] > 0]
    zeros = [q for q in sq if q[2] == 0]
    m = len(nz)
    if m == 0 or m > 40:
        return None
    nv = 3 * m
    H = Fraction(1, 2)
    rows = []  # (dict col->Fraction, rhs)
    for i in range(m):
        xi, yi, si = i, m + i, 2 * m + i
        rows.append(({si: H, xi: Fraction(-1)}, Fraction(0)))
        rows.append(({si: H, xi: Fraction(1)}, Fraction(1)))
        rows.append(({si: H, yi: Fraction(-1)}, Fraction(0)))
        rows.append(({si: H, yi: Fraction(1)}, Fraction(1)))
        rows.append(({si: Fraction(-1)}, Fraction(0)))
    for i in range(m):
        for j in range(i + 1, m):
            xi, yi, si = nz[i]
            xj, yj, sj = nz[j]
            cands = [
                ((xj - sj / 2) - (xi + si / 2), (i, j, 0)),
                ((xi - si / 2) - (xj + sj / 2), (j, i, 0)),
                ((yj - sj / 2) - (yi + si / 2), (i, j, 1)),
                ((yi - si / 2) - (yj + sj / 2), (j, i, 1)),
            ]
            g, (a, b, ax) = max(cands, key=lambda t: t[0])
            off = 0 if ax == 0 else m
            # pos_a + s_a/2 - pos_b + s_b/2 <= 0
            d = {off + a: Fraction(1), off + b: Fraction(-1),
                 2 * m + a: H, 2 * m + b: H}
            rows.append((d, Fraction(0)))
    if time.time() > deadline:
        return None
    A = np.zeros((len(rows), nv))
    bvec = np.zeros(len(rows))
    for r, (d, rhs) in enumerate(rows):
        for c, v in d.items():
            A[r, c] = float(v)
        bvec[r] = float(rhs)
    c = np.zeros(nv)
    c[2 * m:] = -1.0
    try:
        res = linprog(c, A_ub=A, b_ub=bvec, bounds=[(0, 1)] * nv, method='highs')
    except Exception:
        return None
    if res.status != 0:
        return None
    v = res.x
    slack = bvec - A @ v
    active = [r for r in range(len(rows)) if slack[r] < 1e-7]
    eq = []
    for r in active:
        d, rhs = rows[r]
        coeffs = [Fraction(0)] * nv
        for cc, val in d.items():
            coeffs[cc] = val
        eq.append((coeffs, rhs))
    if time.time() > deadline:
        return None
    sol = _exact_solve(eq, nv, v)
    if sol is None:
        return None
    new = [(sol[i], sol[m + i], sol[2 * m + i]) for i in range(m)] + zeros
    return new


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    if n <= 0:
        return []
    F, P = _plan_table(n)
    sq = []
    _build(n, Fraction(0), Fraction(0), Fraction(1), P, sq)
    sq = sq[:n]
    while len(sq) < n:
        sq.append((Fraction(0), Fraction(0), Fraction(0)))
    if not _verify(sq):
        k = math.isqrt(n)
        sq = [((i + Fraction(1, 2)) / k, (j + Fraction(1, 2)) / k, Fraction(1, k))
              for i in range(k) for j in range(k)]
        sq += [(Fraction(0), Fraction(0), Fraction(0))] * (n - len(sq))
    best_sum = sum(q[2] for q in sq)
    try:
        nzc = sum(1 for q in sq if q[2] > 0)
        if 1 < nzc <= 40:
            new = _lp_refine(sq, t0 + 20.0)
            if new is not None and len(new) == n and _verify(new):
                ns = sum(q[2] for q in new)
                if ns > best_sum:
                    sq, best_sum = new, ns
    except Exception:
        pass
    out = []
    for (x, y, s) in sq:
        out.append((min(1.0, max(0.0, float(x))), min(1.0, max(0.0, float(y))),
                    0.0, min(1.0, max(0.0, float(s)))))
    return out
# EVOLVE-BLOCK-END
