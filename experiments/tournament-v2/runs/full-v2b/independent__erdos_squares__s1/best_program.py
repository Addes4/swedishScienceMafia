import math
import random
import numpy as np
from scipy.optimize import minimize

# -------------------------------------------------------------
# Geometry helpers for rotated squares
# -------------------------------------------------------------

def _corners(cx, cy, angle, side):
    """Return the 4 corners of a square, angle in turns."""
    a = 2.0 * math.pi * angle
    ca, sa = math.cos(a), math.sin(a)
    h = 0.5 * side
    pts = []
    for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return pts


def _sep_axis(axis, poly1, poly2):
    """Project polygons onto axis, return overlap amount (positive = overlapping)."""
    a1 = [p[0] * axis[0] + p[1] * axis[1] for p in poly1]
    a2 = [p[0] * axis[0] + p[1] * axis[1] for p in poly2]
    return min(max(a1), max(a2)) - max(min(a1), min(a2))


def _overlap_amount(cx1, cy1, a1, s1, cx2, cy2, a2, s2):
    """Positive if squares overlap, negative if separated (approx via SAT)."""
    if s1 <= 1e-12 or s2 <= 1e-12:
        return -1e9
    p1 = _corners(cx1, cy1, a1, s1)
    p2 = _corners(cx2, cy2, a2, s2)
    # axes: normals of edges of both squares
    axes = []
    for poly in (p1, p2):
        for i in range(4):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % 4]
            ex, ey = x2 - x1, y2 - y1
            ln = math.hypot(ex, ey)
            if ln > 1e-15:
                axes.append((-ey / ln, ex / ln))
    best = 1e18
    for ax, ay in axes:
        ov = _sep_axis((ax, ay), p1, p2)
        if ov < best:
            best = ov
    return best


# -------------------------------------------------------------
# Constraint / objective functions for SLSQP
# -------------------------------------------------------------

def _build_params(squares):
    """squares: list of (cx, cy, angle, side) -> flat array x."""
    x = []
    for cx, cy, ang, s in squares:
        x.extend([cx, cy, ang, s])
    return np.array(x, dtype=float)


def _unpack(x):
    n = len(x) // 4
    out = []
    for i in range(n):
        out.append((x[4 * i], x[4 * i + 1], x[4 * i + 2], x[4 * i + 3]))
    return out


def _make_constraints(n, active):
    """Return list of dicts for SLSQP. 'active' is indices of squares with side > 0."""
    m = len(active)

    def cons_fun(x):
        vals = []
        # containment constraints: each corner inside [0,1]^2
        for i in range(n):
            cx, cy, ang, s = x[4 * i], x[4 * i + 1], x[4 * i + 2], x[4 * i + 3]
            if s <= 1e-12:
                continue
            corners = _corners(cx, cy, ang, s)
            for (px, py) in corners:
                vals.append(px)          # >= 0
                vals.append(1.0 - px)    # >= 0
                vals.append(py)
                vals.append(1.0 - py)
        # non-overlap: overlap amount <= 0
        for ii in range(m):
            i = active[ii]
            for jj in range(ii + 1, m):
                j = active[jj]
                ov = _overlap_amount(
                    x[4 * i], x[4 * i + 1], x[4 * i + 2], x[4 * i + 3],
                    x[4 * j], x[4 * j + 1], x[4 * j + 2], x[4 * j + 3])
                vals.append(-ov)  # >= 0
        return np.array(vals)

    return [{'type': 'ineq', 'fun': cons_fun}]


def _obj(x):
    n = len(x) // 4
    return -sum(x[4 * i + 3] for i in range(n))


# -------------------------------------------------------------
# Local refinement
# -------------------------------------------------------------

def _refine(squares, maxiter=120, active_frac=1.0):
    n = len(squares)
    active = [i for i in range(n) if squares[i][3] > 1e-9]
    if len(active) < 1:
        return squares
    x0 = _build_params(squares)
    # bounds: centres and angles and sides
    bounds = []
    for i in range(n):
        bounds.append((0.0, 1.0))   # cx
        bounds.append((0.0, 1.0))   # cy
        bounds.append((-2.0, 2.0))  # angle (allow wrapping, will normalise)
        bounds.append((0.0, 1.5))   # side
    cons = _make_constraints(n, active)
    try:
        res = minimize(_obj, x0, method='SLSQP', bounds=bounds,
                       constraints=cons, options={'maxiter': maxiter,
                                                  'ftol': 1e-12, 'disp': False})
        xr = res.x
    except Exception:
        xr = x0
    out = []
    for i in range(n):
        cx = min(1.0, max(0.0, xr[4 * i]))
        cy = min(1.0, max(0.0, xr[4 * i + 1]))
        ang = xr[4 * i + 2] % 1.0
        s = max(0.0, min(1.5, xr[4 * i + 3]))
        out.append((cx, cy, ang, s))
    return _clean(out)


def _clean(squares):
    """Remove tiny overlaps / fix containment approximately by shrinking."""
    n = len(squares)
    sq = [list(t) for t in squares]
    # shrink overlapping squares iteratively
    for _ in range(6):
        changed = False
        for i in range(n):
            if sq[i][3] <= 1e-12:
                continue
            for j in range(i + 1, n):
                if sq[j][3] <= 1e-12:
                    continue
                ov = _overlap_amount(sq[i][0], sq[i][1], sq[i][2], sq[i][3],
                                     sq[j][0], sq[j][1], sq[j][2], sq[j][3])
                if ov > 1e-9:
                    # shrink both a little
                    shrink = min(ov * 0.6, 0.02)
                    sq[i][3] = max(0.0, sq[i][3] - shrink)
                    sq[j][3] = max(0.0, sq[j][3] - shrink)
                    changed = True
            # containment
            corners = _corners(sq[i][0], sq[i][1], sq[i][2], sq[i][3])
            for (px, py) in corners:
                if px < -1e-9 or px > 1 + 1e-9 or py < -1e-9 or py > 1 + 1e-9:
                    sq[i][3] *= 0.95
                    changed = True
                    break
        if not changed:
            break
    # clip centres
    res = []
    for cx, cy, ang, s in sq:
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)),
                    ang % 1.0, max(0.0, s)))
    return res


# -------------------------------------------------------------
# Initial constructions
# -------------------------------------------------------------

def _grid_init(n):
    """k x k grid + leftovers as tiny squares."""
    k = max(1, int(math.floor(math.sqrt(n))))
    while (k + 1) ** 2 <= n:
        k += 1
    while k * k > n:
        k -= 1
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
          for i in range(k) for j in range(k)]
    # fill remainder with zero-size
    while len(sq) < n:
        sq.append((0.5, 0.5, 0.0, 0.0))
    return sq[:n]


def _rows_init(n):
    """Row packing with varying widths, some rotation."""
    if n == 0:
        return []
    k = max(1, int(round(math.sqrt(n))))
    sq = []
    # try to make k rows, distribute squares
    remaining = n
    y = 0.0
    row = 0
    while remaining > 0:
        cnt = min(remaining, max(1, n // k + (1 if row < n % k else 0)))
        if cnt == 0:
            cnt = 1
        remaining -= cnt
        h = 1.0 / (k if k > 0 else 1)
        w = 1.0 / cnt
        s = min(h, w)
        for i in range(cnt):
            sq.append(((i + 0.5) * w, y + h * 0.5, 0.0, s))
        y += h
        row += 1
        if y > 1.0:
            y = 1.0
    while len(sq) < n:
        sq.append((0.5, 0.5, 0.0, 0.0))
    return sq[:n]


# -------------------------------------------------------------
# Random perturbation for multi-start
# -------------------------------------------------------------

def _perturb(squares, strength=1.0, rng=None):
    if rng is None:
        rng = random
    n = len(squares)
    out = []
    for cx, cy, ang, s in squares:
        if s > 1e-9:
            cx2 = cx + rng.gauss(0, 0.03 * strength)
            cy2 = cy + rng.gauss(0, 0.03 * strength)
            cx2 = min(0.98, max(0.02, cx2))
            cy2 = min(0.98, max(0.02, cy2))
            ang2 = (ang + rng.gauss(0, 0.05 * strength)) % 1.0
            s2 = s * (1.0 + rng.gauss(0, 0.15 * strength))
            s2 = max(1e-4, min(1.4, s2))
            out.append((cx2, cy2, ang2, s2))
        else:
            out.append((cx, cy, ang, s))
    return out


def _score(squares):
    """Sum of side lengths, penalised for overlaps/violations."""
    n = len(squares)
    total = sum(s for _, _, _, s in squares)
    pen = 0.0
    for i in range(n):
        cx, cy, ang, s = squares[i]
        if s <= 1e-12:
            continue
        # containment penalty
        for (px, py) in _corners(cx, cy, ang, s):
            if px < 0:
                pen += -px * 50
            if px > 1:
                pen += (px - 1) * 50
            if py < 0:
                pen += -py * 50
            if py > 1:
                pen += (py - 1) * 50
        for j in range(i + 1, n):
            if squares[j][3] <= 1e-12:
                continue
            ov = _overlap_amount(cx, cy, ang, s,
                                 squares[j][0], squares[j][1],
                                 squares[j][2], squares[j][3])
            if ov > 0:
                pen += ov * 200
    return total - pen


# -------------------------------------------------------------
# Main solve
# -------------------------------------------------------------

def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    if n == 2:
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    if n == 3:
        # two on bottom, one on top
        return [(0.25, 0.25, 0.0, 0.5), (0.75, 0.25, 0.0, 0.5),
                (0.5, 0.75, 0.0, 0.5)]
    if n == 4:
        return [(0.25, 0.25, 0.0, 0.5), (0.75, 0.25, 0.0, 0.5),
                (0.25, 0.75, 0.0, 0.5), (0.75, 0.75, 0.0, 0.5)]

    # For larger n, use grid as a robust warm start, then local search.
    best = None
    best_val = -1e18
    rng = random.Random(12345 + n)

    # candidate initial layouts
    inits = []
    inits.append(_grid_init(n))
    try:
        inits.append(_rows_init(n))
    except Exception:
        pass
    # perturbed grids
    base = _grid_init(n)
    for _ in range(6):
        inits.append(_perturb(base, strength=1.0, rng=rng))

    # time budget guard
    import time
    t0 = time.time()
    time_limit = 50.0

    for init in inits:
        if time.time() - t0 > time_limit:
            break
        cand = _refine(init, maxiter=200)
        val = _score(cand)
        if val > best_val:
            best_val = val
            best = cand
        # extra random perturbations from current best
        for _ in range(4):
            if time.time() - t0 > time_limit:
                break
            pert = _perturb(best, strength=0.5, rng=rng)
            cand2 = _refine(pert, maxiter=150)
            v2 = _score(cand2)
            if v2 > best_val:
                best_val = v2
                best = cand2

    if best is None:
        best = _grid_init(n)
    # final cleanup
    best = _clean(best)
    # ensure exactly n
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))
    best = best[:n]
    # normalise output types
    out = []
    for cx, cy, ang, s in best:
        out.append((float(min(1.0, max(0.0, cx))),
                    float(min(1.0, max(0.0, cy))),
                    float(ang % 1.0),
                    float(max(0.0, s))))
    return out
