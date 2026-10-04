# EVOLVE-BLOCK-START
"""Pack n squares in the unit square, maximising the sum of side lengths.

Approach: multi-start.  Seeds come from
  (a) k x k grids,
  (b) a "largest-first greedy" packer that repeatedly places the biggest square
      it can find (scanning a fine grid of candidate centres and several angles
      against the already-placed squares) -- this naturally discovers the
      asymmetric staircase / one-big-square-plus-remainder layouts that beat
      uniform grids,
  (c) structured staircase families along the main diagonal.
Each seed is polished by a SAT-based coordinate descent that enlarges squares one
at a time.  Best-of-restarts is returned.
"""
import math
import random

EPS = 1e-7


def _corners(sq):
    cx, cy, ang, s = sq
    if s <= 0.0:
        return [(cx, cy)] * 4
    a = 2.0 * math.pi * ang
    ca, sa = math.cos(a), math.sin(a)
    h = 0.5 * s
    pts = []
    for ux in (-h, h):
        for uy in (-h, h):
            pts.append((cx + ux * ca - uy * sa, cy + ux * sa + uy * ca))
    return pts


def _sat_overlap(a, b):
    """Separating axis test; positive = interiors overlap, <=0 disjoint."""
    pa = _corners(a)
    pb = _corners(b)
    axes = []
    for pts in (pa, pb):
        for i in range(2):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            ex, ey = x2 - x1, y2 - y1
            ln = math.hypot(ex, ey)
            if ln > 0:
                axes.append((-ey / ln, ex / ln))
    mind = float('inf')
    for ax, ay in axes:
        amin = min(ax * x + ay * y for x, y in pa)
        amax = max(ax * x + ay * y for x, y in pa)
        bmin = min(ax * x + ay * y for x, y in pb)
        bmax = max(ax * x + ay * y for x, y in pb)
        d = min(amax, bmax) - max(amin, bmin)
        if d <= 0.0:
            return -1.0
        if d < mind:
            mind = d
    return mind


def _inside(sq):
    for x, y in _corners(sq):
        if x < -1e-9 or x > 1.0 + 1e-9 or y < -1e-9 or y > 1.0 + 1e-9:
            return False
    return True


def _feasible(squares, idx):
    if not _inside(squares[idx]):
        return False
    for j in range(len(squares)):
        if j == idx:
            continue
        if _sat_overlap(squares[idx], squares[j]) > 0.0:
            return False
    return True


def _max_side_at(squares, idx, cx, cy, ang, cap):
    """Largest side (<=cap) that fits a square at (cx, cy, ang)."""
    lo, hi = 0.0, cap
    trial = squares[:idx] + [(cx, cy, ang, hi)] + squares[idx + 1:]
    if _feasible(trial, idx):
        return hi
    for _ in range(28):
        mid = 0.5 * (lo + hi)
        trial = squares[:idx] + [(cx, cy, ang, mid)] + squares[idx + 1:]
        if _feasible(trial, idx):
            lo = mid
        else:
            hi = mid
    return lo


def _refine(squares, cap, rng, iters):
    n = len(squares)
    for _ in range(iters):
        improved = False
        order = list(range(n))
        rng.shuffle(order)
        for i in order:
            cx, cy, ang, s = squares[i]
            best = s
            best_conf = None
            candidate_centers = [(cx, cy)]
            r = 0.03
            for _ in range(4):
                candidate_centers.append((min(1.0, max(0.0, cx + rng.uniform(-r, r))),
                                          min(1.0, max(0.0, cy + rng.uniform(-r, r)))))
            candidate_angles = {round(ang, 6)}
            for da in (0.0, 0.25, 0.125, 0.0625, -0.0625, 0.5):
                candidate_angles.add(round((ang + da) % 1.0, 6))
            for (ncx, ncy) in candidate_centers:
                for na in candidate_angles:
                    ns = _max_side_at(squares, i, ncx, ncy, na, cap)
                    trial = squares[:i] + [(ncx, ncy, na, ns)] + squares[i + 1:]
                    if _feasible(trial, i) and ns > best + 1e-9:
                        best = ns
                        best_conf = (ncx, ncy, na, ns)
            if best_conf is not None:
                squares[i] = best_conf
                improved = True
        if not improved:
            break
    return squares


def _seed_grid(n, k):
    side = 1.0 / k
    out = []
    for i in range(k):
        for j in range(k):
            if len(out) < n:
                out.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]


def _seed_greedy(n, rng, angles, grid=11):
    """Largest-first greedy: repeatedly place the biggest findable square."""
    placed = []
    for k in range(n):
        best_s = -1.0
        best_cfg = (0.5, 0.5, 0.0, 0.0)
        cand_pts = []
        step = 1.0 / (grid - 1)
        for gi in range(grid):
            for gj in range(grid):
                cand_pts.append((gi * step, gj * step))
        for _ in range(6):
            cand_pts.append((rng.random(), rng.random()))
        for (cx, cy) in cand_pts:
            for ang in angles:
                # quick check that centre can host at least some square
                s = _max_side_at(placed + [(0.5, 0.5, 0.0, 0.0)] * 0, 0, cx, cy, ang, 1.0) if False else None
                # compute max side directly
                lo, hi = 0.0, 1.0
                cfg_hi = (cx, cy, ang, hi)
                if _inside(cfg_hi):
                    # binary search using feasibility vs placed
                    lo = 0.0
                    for _ in range(26):
                        mid = 0.5 * (lo + hi)
                        cfg = (cx, cy, ang, mid)
                        trial = placed + [cfg]
                        if _feasible(trial, len(trial) - 1):
                            lo = mid
                        else:
                            hi = mid
                    if lo > best_s:
                        best_s = lo
                        best_cfg = (cx, cy, ang, lo)
        placed.append(best_cfg)
    return placed


def _seed_staircase(n, rng, angles):
    """Place squares of decreasing size along a diagonal-ish path."""
    out = []
    s = 1.0 / max(1.0, math.sqrt(n)) * rng.uniform(1.0, 1.6)
    s = min(s, 1.0)
    x, y = 0.0, 0.0
    for i in range(n):
        si = max(0.0, s * (rng.uniform(0.85, 1.0) ** i))
        if si <= 0.0:
            out.append((0.5, 0.5, 0.0, 0.0))
            continue
        ang = rng.choice(angles)
        out.append((min(0.999, max(0.001, x + si / 2)),
                    min(0.999, max(0.001, y + si / 2)),
                    ang, si))
        x += si * rng.uniform(0.6, 1.0)
        y += si * rng.uniform(0.2, 0.9)
        if x > 0.9 or y > 0.9:
            x = rng.uniform(0.0, 0.2)
            y = rng.uniform(0.0, 0.2)
    return out


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    rng = random.Random(12345 + n)

    base_angles = [0.0, 0.25, 0.125, 0.0625, -0.0625, 0.5, 0.375]

    seeds = []
    for k in range(max(1, math.isqrt(n) - 1), math.isqrt(n) + 2):
        seeds.append(_seed_grid(n, k))

    # greedy largest-first seedings (the key new ingredient)
    for _ in range(4):
        angles = base_angles if _ % 2 == 0 else [0.0]
        seeds.append(_seed_greedy(n, rng, angles, grid=11 if _ % 2 == 0 else 9))

    # staircase seedings
    for _ in range(4):
        angles = [0.0] if _ % 2 == 0 else base_angles
        seeds.append(_seed_staircase(n, rng, angles))

    # perturbed-grid seeds
    base = _seed_grid(n, max(1, math.isqrt(n)))
    for _ in range(3):
        s = [list(b) for b in base]
        for row in s:
            row[3] *= rng.uniform(0.85, 1.0)
        seeds.append([tuple(r) for r in s])

    # "one big square" seeds
    for _ in range(3):
        big = rng.uniform(0.45, 0.62)
        cx = rng.choice([big / 2, 1 - big / 2])
        cy = rng.choice([big / 2, 1 - big / 2])
        cfg = [(cx, cy, 0.0, big)]
        k = max(1, math.ceil(math.sqrt(n)))
        side = 1.0 / k
        i = 0
        while len(cfg) < n:
            i += 1
            x = (i % k + 0.5) * side
            y = (i // k + 0.5) * side
            cfg.append((x, y, 0.0, side * 0.8))
        seeds.append(cfg[:n])

    cap = 1.0
    best = None
    best_score = -1.0

    for sd in seeds:
        squares = [tuple(x) for x in sd]
        squares = _refine(squares, cap, rng, 25)
        for _ in range(2):
            squares = _refine(squares, cap, rng, 15)
        ok = True
        for i in range(n):
            if not _feasible(squares, i):
                ok = False
                break
        if not ok:
            continue
        total = sum(max(0.0, sq[3]) for sq in squares)
        if total > best_score:
            best_score = total
            best = [tuple(sq) for sq in squares]

    if best is None:
        return _seed_grid(n, max(1, math.isqrt(n)))

    for i in range(n):
        cx, cy, ang, s = best[i]
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        best[i] = (cx, cy, ang % 1.0, max(0.0, min(s, 1.0)))
    return best
# EVOLVE-BLOCK-END
