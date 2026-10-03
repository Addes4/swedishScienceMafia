# EVOLVE-BLOCK-START
"""Packing unit squares inside the unit square maximising the sum of side lengths.

Approach
--------
For a fixed total "budget" the problem is highly non-convex.  We use a
two-stage strategy:

1.  Build a good starting configuration with a *layer / slicing* heuristic
    that generalises the plain k x k grid (which is the main source of
    sub-optimality for the baseline).  The number of slices in x and y is
    chosen to match n as closely as possible.

2.  Refine with a projected-gradient / penalty local optimisation on the
    side lengths and positions, honouring the non-overlap constraints via a
    smooth penalty.  The refinement is deliberately cheap so that many
    restarts fit inside the time budget.

All geometry uses the separating-axis idea: two convex polygons (squares)
overlap in their interiors iff their projections overlap on every candidate
axis.  For squares the candidate axes are their four edges' normals, i.e.
two axes per square.  We evaluate the overlap measure as the minimum over
these axes of the projection overlap, which is a smooth function of the
parameters wherever it is positive.
"""

import math
import random

import numpy as np


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------
def _corners(cx, cy, ang, side):
    """Corners of a square (fraction of a turn for the angle)."""
    t = 2.0 * math.pi * ang
    c, s = math.cos(t), math.sin(t)
    h = 0.5 * side
    return (
        (cx - h * c + h * s, cy - h * s - h * c),
        (cx + h * c + h * s, cy + h * s - h * c),
        (cx + h * c - h * s, cy + h * s + h * c),
        (cx - h * c - h * s, cy - h * s + h * c),
    )


def _axes(ang):
    """Two unit axes (edge normals) of a square with the given angle."""
    t = 2.0 * math.pi * ang
    c, s = math.cos(t), math.sin(t)
    return ((c, s), (-s, c))


def _overlap_amount(sq1, sq2):
    """Return a positive number when the two squares overlap, else <= 0.

    The value is the minimum *interpenetration depth* over the four
    separating axes (two per square).  It is positive iff the interiors
    overlap.
    """
    c1 = _corners(*sq1)
    c2 = _corners(*sq2)

    ax = _axes(sq1[2]) + _axes(sq2[2])

    best = float("inf")
    for (ux, uy) in ax:
        p1 = [x * ux + y * uy for (x, y) in c1]
        p2 = [x * ux + y * uy for (x, y) in c2]
        lo1, hi1 = min(p1), max(p1)
        lo2, hi2 = min(p2), max(p2)
        # positive == overlap on this axis
        ov = min(hi1, hi2) - max(lo1, lo2)
        if ov <= 0.0:
            return ov  # separated: no need to look further
        if ov < best:
            best = ov
    return best


def _squares_overlap(sq1, sq2, tol=1e-9):
    return _overlap_amount(sq1, sq2) > tol


# --------------------------------------------------------------------------
# feasibility / objective
# --------------------------------------------------------------------------
def _total_side(sqs):
    return sum(s[3] for s in sqs)


def _is_feasible(sqs, tol=1e-7):
    for sq in sqs:
        cx, cy, ang, side = sq
        if side < -tol:
            return False
        if side == 0:
            continue
        cs = _corners(cx, cy, ang, side)
        for (x, y) in cs:
            if x < -tol or x > 1.0 + tol or y < -tol or y > 1.0 + tol:
                return False
    m = len(sqs)
    for i in range(m):
        if sqs[i][3] == 0:
            continue
        for j in range(i + 1, m):
            if sqs[j][3] == 0:
                continue
            if _squares_overlap(sqs[i], sqs[j], tol):
                return False
    return True


def _penalty(sqs):
    """Large value when the configuration is infeasible."""
    pen = 0.0
    m = len(sqs)
    for sq in sqs:
        cx, cy, ang, side = sq
        if side == 0:
            continue
        cs = _corners(cx, cy, ang, side)
        for (x, y) in cs:
            pen += max(0.0, -x) ** 2 + max(0.0, x - 1.0) ** 2
            pen += max(0.0, -y) ** 2 + max(0.0, y - 1.0) ** 2
    for i in range(m):
        if sqs[i][3] == 0:
            continue
        for j in range(i + 1, m):
            if sqs[j][3] == 0:
                continue
            ov = _overlap_amount(sqs[i], sqs[j])
            if ov > 0:
                pen += ov ** 2
    return pen


# --------------------------------------------------------------------------
# initial configurations
# --------------------------------------------------------------------------
def _grid_config(n):
    """Largest k x k grid plus zero-size squares."""
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    sqs = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
           for i in range(k) for j in range(k)]
    while len(sqs) < n:
        sqs.append((0.5, 0.5, 0.0, 0.0))
    return sqs[:n]


def _slice_config(n, tiles):
    """Rectangular tiling with `tiles` columns and rows of squares."""
    kx, ky = tiles
    side_x = 1.0 / kx
    side_y = 1.0 / ky
    side = min(side_x, side_y)
    sqs = []
    for i in range(kx):
        for j in range(ky):
            if len(sqs) >= n:
                break
            sqs.append(((i + 0.5) * side_x, (j + 0.5) * side_y, 0.0, side))
        if len(sqs) >= n:
            break
    while len(sqs) < n:
        sqs.append((0.5, 0.5, 0.0, 0.0))
    return sqs[:n]


def _candidate_starts(n):
    """Return a list of promising initial configurations."""
    cands = []
    cands.append(_grid_config(n))

    # all tilings whose product is close to n
    best_prod = []
    for kx in range(1, n + 1):
        for ky in range(1, n + 1):
            if kx * ky >= n and kx * ky <= n + 2 * max(kx, ky):
                best_prod.append((abs(kx * ky - n), kx, ky))
    best_prod.sort()
    for (_, kx, ky) in best_prod[:6]:
        cands.append(_slice_config(n, (kx, ky)))

    # a dense packing where all squares share the same (maximum) size
    r = math.sqrt(1.0 / n)
    sqs = [((i + 0.5) * r, (j + 0.5) * r, 0.0, r)
           for i in range(int(math.ceil(1.0 / r)))
           for j in range(int(math.ceil(1.0 / r)))]
    sqs = sqs[:n]
    while len(sqs) < n:
        sqs.append((0.5, 0.5, 0.0, 0.0))
    cands.append(sqs)

    # deduplicate roughly
    uniq = []
    for c in cands:
        if not any(_allclose(c, u) for u in uniq):
            uniq.append(c)
    return uniq


def _allclose(a, b, tol=1e-9):
    if len(a) != len(b):
        return False
    for p, q in zip(a, b):
        for x, y in zip(p, q):
            if abs(x - y) > tol:
                return False
    return True


# --------------------------------------------------------------------------
# local optimisation
# --------------------------------------------------------------------------
def _pocket(sqs, steps, rng, alpha0=0.02, temp0=5e-4, temp1=1e-7):
    """Penalty-driven stochastic local search on positions, angles and sides."""
    m = len(sqs)
    # parameter vector: for each square cx, cy, ang, side
    x = np.array([[s[0], s[1], s[2], s[3]] for s in sqs], dtype=float)

    def unpack(v):
        return [(float(v[i, 0]), float(v[i, 1]), float(v[i, 2]),
                 float(v[i, 3])) for i in range(m)]

    def cost(v):
        sq = unpack(v)
        return -_total_side(sq) + 1e4 * _penalty(sq)

    best = x.copy()
    best_c = cost(best)
    cur = x.copy()
    cur_c = best_c

    for it in range(steps):
        frac = it / max(1, steps - 1)
        temp = temp0 * (temp1 / temp0) ** frac
        scale = alpha0 * (1.0 - 0.9 * frac)

        new = cur.copy()
        # perturb a random subset of squares
        for _ in range(1 + rng.randrange(max(1, m // 3))):
            i = rng.randrange(m)
            new[i, 0] += rng.gauss(0.0, scale)
            new[i, 1] += rng.gauss(0.0, scale)
            new[i, 2] += rng.gauss(0.0, scale * 2.0)
            new[i, 3] += rng.gauss(0.0, scale)

        # keep the parameters in a sane box
        np.clip(new[:, 0], 0.0, 1.0, out=new[:, 0])
        np.clip(new[:, 1], 0.0, 1.0, out=new[:, 1])
        np.clip(new[:, 2], 0.0, 1.0, out=new[:, 2])
        np.clip(new[:, 3], 0.0, 1.0, out=new[:, 3])

        nc = cost(new)
        if nc < cur_c or rng.random() < math.exp(-(nc - cur_c) / max(temp, 1e-12)):
            cur, cur_c = new, nc
            if nc < best_c:
                best, best_c = new.copy(), nc

    return unpack(best), -best_c, best_c


def _project_feasible(sqs, rng, rounds=6):
    """Greedy repair: shrink offending squares until feasible."""
    sqs = [(float(a), float(b), float(c), max(0.0, float(d))) for (a, b, c, d) in sqs]
    for _ in range(rounds):
        changed = False
        # shrink squares that stick out
        for i, (cx, cy, ang, side) in enumerate(sqs):
            if side <= 0:
                continue
            cs = _corners(cx, cy, ang, side)
            over = 0.0
            for (x, y) in cs:
                over = max(over, -x, x - 1.0, -y, y - 1.0)
            if over > 1e-12:
                # shrink by an amount that removes the violation
                scale = max(0.0, 1.0 - over / max(side, 1e-12))
                sqs[i] = (cx, cy, ang, side * min(1.0, 0.999 * scale))
                changed = True
        # shrink squares that overlap
        n = len(sqs)
        for i in range(n):
            for j in range(i + 1, n):
                if sqs[i][3] <= 0 or sqs[j][3] <= 0:
                    continue
                ov = _overlap_amount(sqs[i], sqs[j])
                if ov > 1e-12:
                    s = 1.0 - min(0.5, ov / max(min(sqs[i][3], sqs[j][3]), 1e-12))
                    s = max(0.0, s)
                    a = sqs[i]
                    b = sqs[j]
                    sqs[i] = (a[0], a[1], a[2], a[3] * s)
                    sqs[j] = (b[0], b[1], b[2], b[3] * s)
                    changed = True
        if not changed:
            break
    return sqs


# --------------------------------------------------------------------------
# main entry
# --------------------------------------------------------------------------
def solve(n):
    if n <= 0:
        return []

    rng = random.Random(1234567 + n)

    best = None
    best_val = -1.0

    starts = _candidate_starts(n)

    # number of local-search steps: scale with n but keep the budget bounded
    steps = int(max(400, min(6000, 400 + 60 * n)))

    for s in starts:
        # a quick refinement with a decreasing temperature schedule
        cur, val, _ = _pocket(s, steps, rng)

        # repair feasibility and recompute the true value
        cur = _project_feasible(cur, rng)
        if _is_feasible(cur, tol=1e-6):
            v = _total_side(cur)
        else:
            # fall back on the grid if we cannot repair
            cur = _grid_config(n)
            v = _total_side(cur)

        if v > best_val:
            best_val = v
            best = cur

    # final safety pass: force feasibility
    if best is None:
        best = _grid_config(n)
        best_val = _total_side(best)

    if not _is_feasible(best, tol=1e-6):
        best = _grid_config(n)

    # clip to the unit square to satisfy the interface contract
    out = []
    for (cx, cy, ang, side) in best:
        cx = min(1.0, max(0.0, cx))
        cy = min(1.0, max(0.0, cy))
        ang = ang % 1.0 if ang == ang else 0.0
        side = min(1.0, max(0.0, side))
        out.append((cx, cy, ang, side))

    # ensure exactly n entries
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    out = out[:n]

    # last-resort feasibility check (never expected to trigger)
    if not _is_feasible(out, tol=1e-6):
        out = _grid_config(n)
        out = [(c[0], c[1], c[2], c[3]) for c in out]
        out = out[:n]
        while len(out) < n:
            out.append((0.5, 0.5, 0.0, 0.0))

    return out
# EVOLVE-BLOCK-END
