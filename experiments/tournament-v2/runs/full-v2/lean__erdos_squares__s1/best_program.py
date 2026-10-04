# EVOLVE-BLOCK-START
"""Packing n squares in the unit square to maximise the sum of side lengths.

Approach: build a good grid-based candidate, then refine sizes/locations with a
continuous local optimizer (SLSQP) that keeps squares disjoint (axis-aligned
separation constraints between every pair).  Continuous rebalancing recovers
slack left by rigid row/column layouts, especially for small n.
"""

import math

try:
    import numpy as np
    from scipy.optimize import minimize
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False


def _best_for_ab(n, a, b):
    """n = a*b + c : b rows of a squares plus a partial row of c squares."""
    c = n - a * b
    if c < 0:
        return None
    if c == 0:
        s2 = min(1.0 / a, 1.0 / b)
        sq = [((i + 0.5) / a, (j + 0.5) / b, 0.0, s2)
              for i in range(a) for j in range(b)]
        return (n * s2, sq)
    best = None
    for hb_choice in (1.0 / a, 1.0 / (b + 1), 1.0 / (a + 1)):
        if hb_choice <= 0 or hb_choice > 1.0 / b:
            continue
        hp = 1.0 - b * hb_choice
        if hp < 0:
            continue
        sb = min(hb_choice, 1.0 / a)
        sp = min(hp, 1.0 / c) if c > 0 else 0.0
        total = a * b * sb + c * sp
        if best is None or total > best[0]:
            best = (total, hb_choice, sb, sp)
    if best is None:
        return None
    total, hb, sb, sp = best
    sq = []
    for i in range(a):
        for j in range(b):
            sq.append(((i + 0.5) / a, (j + 0.5) * hb, 0.0, sb))
    hp = 1.0 - b * hb
    for i in range(c):
        sq.append(((i + 0.5) / c, 1.0 - hp / 2.0, 0.0, sp))
    return (total, sq)


def _grid_candidates(n):
    best = None
    cands = set()
    for a in range(1, n + 1):
        b = n // a
        if b >= 1:
            cands.add((a, b))
            cands.add((b, a))
    for a in range(1, int(math.isqrt(n)) + 3):
        for b in range(1, int(math.isqrt(n)) + 3):
            if a * b <= n:
                cands.add((a, b))
    for (a, b) in cands:
        r = _best_for_ab(n, a, b)
        if r is not None and (best is None or r[0] > best[0]):
            best = r
    return best


def _refine(n, squares):
    """SLSQP refinement of sizes + positions for axis-aligned squares."""
    if not _HAVE_SCIPY or n < 2:
        return squares
    m = len(squares)
    # variables: cx, cy, s for each square (angles fixed at 0)
    x0 = np.zeros(3 * m)
    for i, (cx, cy, ang, s) in enumerate(squares):
        x0[3 * i] = min(max(cx, s / 2), 1 - s / 2)
        x0[3 * i + 1] = min(max(cy, s / 2), 1 - s / 2)
        x0[3 * i + 2] = max(s, 1e-9)

    eps = 1e-9

    def neg_sum(v):
        return -np.sum(v[2::3])

    def bounds():
        b = []
        for i in range(m):
            b.append((eps, 1 - eps))       # cx loosely; will be constrained vs s
            b.append((eps, 1 - eps))       # cy
            b.append((eps, 1.0))
        return b

    # constraints
    cons = []
    for i in range(m):
        # keep inside unit square: cx - s/2 >= 0 etc. expressed as >= 0
        cons.append({'type': 'ineq',
                     'fun': (lambda v, i=i: v[3*i] - v[3*i+2]/2)})
        cons.append({'type': 'ineq',
                     'fun': (lambda v, i=i: 1 - v[3*i] - v[3*i+2]/2)})
        cons.append({'type': 'ineq',
                     'fun': (lambda v, i=i: v[3*i+1] - v[3*i+2]/2)})
        cons.append({'type': 'ineq',
                     'fun': (lambda v, i=i: 1 - v[3*i+1] - v[3*i+2]/2)})
    for i in range(m):
        for j in range(i + 1, m):
            def sep(v, i=i, j=j):
                cx_i, cy_i, si = v[3*i], v[3*i+1], v[3*i+2]
                cx_j, cy_j, sj = v[3*j], v[3*j+1], v[3*j+2]
                gap_x = abs(cx_i - cx_j) - (si + sj) / 2
                gap_y = abs(cy_i - cy_j) - (si + sj) / 2
                return max(gap_x, gap_y)
            cons.append({'type': 'ineq', 'fun': sep})

    try:
        res = minimize(neg_sum, x0, method='SLSQP', bounds=bounds(),
                       constraints=cons,
                       options={'maxiter': 300, 'ftol': 1e-9})
        if res.success or res.fun < -sum(s[3] for s in squares):
            v = res.x
            out = []
            for i in range(m):
                out.append((v[3*i], v[3*i+1], 0.0, v[3*i+2]))
            return out
    except Exception:
        pass
    return squares


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square."""
    if n <= 0:
        return []
    best = _grid_candidates(n)
    if best is None:
        return [(0.5, 0.5, 0.0, 0.0)] * n
    total, squares = best
    squares = squares[:n]
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    squares = squares[:n]
    if n <= 60:
        squares = _refine(n, squares)
    # final safety: clamp and validate
    safe = []
    for (cx, cy, ang, s) in squares:
        s = max(0.0, min(s, 1.0))
        cx = min(max(cx, s / 2), 1 - s / 2)
        cy = min(max(cy, s / 2), 1 - s / 2)
        safe.append((cx, cy, ang, s))
    return safe
# EVOLVE-BLOCK-END
