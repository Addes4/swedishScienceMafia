import math
import random
import numpy as np

# Optional scipy is allowed but we'll stick to numpy + stdlib for speed/robustness.

# ---------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------

def _corners(cx, cy, ang, s):
    """Return the four corners of a square centre (cx,cy), angle fraction, side s."""
    t = ang * 2.0 * math.pi
    c, sn = math.cos(t), math.sin(t)
    h = s * 0.5
    # local corners
    pts = [(-h, -h), (h, -h), (h, h), (-h, h)]
    out = []
    for x, y in pts:
        out.append((cx + x * c - y * sn, cy + x * sn + y * c))
    return out


def _overlap(a, b, eps=1e-12):
    """Return True if interiors of squares a,b (cx,cy,ang,s) overlap.

    Uses separating axis theorem on the two squares.
    """
    ca = _corners(*a)
    cb = _corners(*b)
    # axes are normals of the edges of both squares
    axes = []
    for poly in (ca, cb):
        for i in range(4):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % 4]
            nx, ny = -(y2 - y1), (x2 - x1)
            L = math.hypot(nx, ny)
            if L > 1e-15:
                axes.append((nx / L, ny / L))
    for ax, ay in axes:
        amin = amax = None
        for x, y in ca:
            d = x * ax + y * ay
            if amin is None or d < amin:
                amin = d
            if amax is None or d > amax:
                amax = d
        bmin = bmax = None
        for x, y in cb:
            d = x * ax + y * ay
            if bmin is None or d < bmin:
                bmin = d
            if bmax is None or d > bmax:
                bmax = d
        # gap? use strict separation; interiors overlap iff projections overlap with positive length
        if amax <= bmin + eps or bmax <= amin + eps:
            return False
    return True


def _inside_unit(cx, cy, ang, s, eps=1e-9):
    for x, y in _corners(cx, cy, ang, s):
        if x < -eps or x > 1.0 + eps or y < -eps or y > 1.0 + eps:
            return False
    return True


def _valid_all(squares, eps=1e-9):
    n = len(squares)
    for i in range(n):
        if not _inside_unit(*squares[i], eps=eps):
            return False
    for i in range(n):
        for j in range(i + 1, n):
            if _overlap(squares[i], squares[j], eps=eps):
                return False
    return True


def _total(squares):
    return float(sum(s[3] for s in squares))


# ---------------------------------------------------------------
# Constructive packing
# ---------------------------------------------------------------

def _greedy_rect_pack(n):
    """Greedy: repeatedly place the largest square that fits in a remaining free rectangle.

    We use a simple free-rectangle list (guillotine style), which is fast and
    guarantees disjointness (axis-aligned), then we ignore rotations at this stage.
    """
    # Each free rectangle is (x0, y0, x1, y1)
    free = [(0.0, 0.0, 1.0, 1.0)]
    squares = []

    def best_in_rect(r):
        x0, y0, x1, y1 = r
        w = x1 - x0
        h = y1 - y0
        s = min(w, h)
        return s

    for _ in range(n):
        # pick rectangle with the largest possible square
        bi = -1
        bs = -1.0
        for idx, r in enumerate(free):
            x0, y0, x1, y1 = r
            w = x1 - x0
            h = y1 - y0
            s = min(w, h)
            if s > bs:
                bs = s
                bi = idx
        if bi < 0 or bs <= 1e-12:
            # place zero-size square in centre
            squares.append((0.5, 0.5, 0.0, 0.0))
            continue
        r = free.pop(bi)
        x0, y0, x1, y1 = r
        w = x1 - x0
        h = y1 - y0
        s = min(w, h)
        # place square in a corner? Place so that remaining space is as split-friendly as possible.
        # Put square in the lower-left of the rectangle, then split into two rectangles
        # (right strip and top strip).
        cx = x0 + s * 0.5
        cy = y0 + s * 0.5
        squares.append((cx, cy, 0.0, s))
        # Emit rectangles:
        # right strip: x0+s .. x1, y0 .. y1
        if (x1 - (x0 + s)) > 1e-12 and h > 1e-12:
            free.append((x0 + s, y0, x1, y1))
        # top strip: x0 .. x0+s, y0+s .. y1
        if s > 1e-12 and (y1 - (y0 + s)) > 1e-12:
            free.append((x0, y0 + s, x0 + s, y1))
    return squares


def _grid_solution(n):
    """Simple k x k grid with zeros for the rest; baseline-ish."""
    k = int(math.isqrt(n))
    if k == 0:
        return [(0.5, 0.5, 0.0, 0.0)] * n
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq[:n]


# ---------------------------------------------------------------
# Local search / optimization
# ---------------------------------------------------------------

def _score_delta(squares, idx, new_sq, others_cache=None):
    """Return change in total side length if square idx is replaced by new_sq, keeping
    validity (inside unit + no overlap with all others).  Returns -inf if invalid."""
    old = squares[idx]
    if new_sq[3] <= 1e-12:
        # shrinking to zero: allowed if inside (yes, centre inside) - simplest
        if new_sq[0] < 0 or new_sq[0] > 1 or new_sq[1] < 0 or new_sq[1] > 1:
            return -float("inf")
        return 0.0 - old[3]
    if not _inside_unit(*new_sq):
        return -float("inf")
    n = len(squares)
    for j in range(n):
        if j == idx:
            continue
        if _overlap(new_sq, squares[j]):
            return -float("inf")
    return new_sq[3] - old[3]


def _local_optimize(squares, time_budget=1.0, rng=None, max_iter=2000):
    """Coordinate descent: for each square, try to grow side (and shift) while keeping validity.

    Also tries small rotations.  This is a simple hill-climb.
    """
    if rng is None:
        rng = random.Random(12345)
    import time
    t0 = time.time()
    sq = [list(s) for s in squares]
    n = len(sq)
    if n == 0:
        return squares
    # Sort indices by current side (largest first) to focus effort.
    order = list(range(n))
    order.sort(key=lambda i: -sq[i][3])

    # Try growing each square.
    improved = True
    it = 0
    while improved and (time.time() - t0) < time_budget and it < max_iter:
        improved = False
        it += 1
        for i in order:
            cur = sq[i]
            if cur[3] <= 1e-12:
                # Try giving it a small positive size if there is room.
                best_new = None
                best_gain = 0.0
                # random attempts
                for _ in range(8):
                    s = rng.uniform(0.001, 0.05)
                    cx = rng.uniform(s / 2, 1 - s / 2)
                    cy = rng.uniform(s / 2, 1 - s / 2)
                    ang = rng.choice([0.0, 0.25, 0.125, 0.375, rng.random()])
                    cand = [cx, cy, ang, s]
                    g = _score_delta(sq, i, cand)
                    if g > best_gain:
                        best_gain = g
                        best_new = cand
                if best_new is not None and best_gain > 1e-15:
                    sq[i] = best_new
                    improved = True
                continue

            cx, cy, ang, s = cur
            base = s
            best = None
            best_gain = 0.0
            # Try perturbations: grow side, shift, rotate.
            tries = []
            # pure growth
            tries.append((cx, cy, ang, s * 1.02 + 1e-4))
            tries.append((cx, cy, ang, s * 1.05 + 1e-4))
            # shifts
            step = max(s * 0.1, 0.001)
            for dx, dy in [(step, 0), (-step, 0), (0, step), (0, -step),
                           (step, step), (-step, step), (step, -step), (-step, -step)]:
                tries.append((cx + dx, cy + dy, ang, s))
                tries.append((cx + dx, cy + dy, ang, s * 1.01))
            # rotations
            for da in (-0.02, 0.02, -0.05, 0.05, -0.1, 0.1):
                tries.append((cx, cy, ang + da, s))
            # random tries
            for _ in range(12):
                tries.append((cx + rng.uniform(-0.05, 0.05),
                              cy + rng.uniform(-0.05, 0.05),
                              ang + rng.uniform(-0.15, 0.15),
                              s * rng.uniform(1.0, 1.08)))
            for cand in tries:
                g = _score_delta(sq, i, cand)
                if g > best_gain:
                    best_gain = g
                    best = cand
            if best is not None and best_gain > 1e-15:
                sq[i] = list(best)
                improved = True
        # end for
    return [tuple(x) for x in sq]


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

def solve(n):
    """Return list of n squares (cx, cy, angle, side)."""
    if n <= 0:
        return []
    # For very small n, exact-ish best-known packings.
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    if n == 2:
        # Two 0.5x0.5 squares: total 1.0  (can't do better: sum <= 1? Actually can be slightly >1 with rotated? but 0.5+0.5 = 1.0 is optimal known)
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    if n == 3:
        # known good: three squares total ~1.1716? Actually 1/3 grid gives 1.0.  Known packing: two 0.5 at bottom? 
        # Use grid-ish plus grow.
        base = [(0.25, 0.25, 0.0, 0.5), (0.75, 0.25, 0.0, 0.5), (0.5, 0.75, 0.0, 0.5)]
        return base
    if n == 4:
        return [(0.25, 0.25, 0.0, 0.5), (0.75, 0.25, 0.0, 0.5),
                (0.25, 0.75, 0.0, 0.5), (0.75, 0.75, 0.0, 0.5)]

    # General approach: try greedy rectangle packing and grid, pick better, then local optimize.
    candidates = []
    candidates.append(_grid_solution(n))
    candidates.append(_greedy_rect_pack(n))

    # Also try a variant: fill with rows of equal squares (like a strip layout)
    def row_layout(n):
        # Try rows counts
        best = None
        best_sum = -1
        for rows in range(1, n + 1):
            cols = (n + rows - 1) // rows
            s_h = 1.0 / rows
            s_w = 1.0 / cols
            s = min(s_h, s_w)
            # how many fit
            # simple: fill cols per row
            sq = []
            count = 0
            for r in range(rows):
                for c in range(cols):
                    if count >= n:
                        break
                    cx = (c + 0.5) * (1.0 / cols)
                    cy = (r + 0.5) * (1.0 / rows)
                    # ensure inside
                    ss = min(s, 1.0 / cols, 1.0 / rows)
                    # Actually place centred in cell
                    sq.append((cx, cy, 0.0, ss))
                    count += 1
                if count >= n:
                    break
            while len(sq) < n:
                sq.append((0.5, 0.5, 0.0, 0.0))
            sm = sum(x[3] for x in sq[:n])
            if sm > best_sum:
                best_sum = sm
                best = sq[:n]
        return best

    candidates.append(row_layout(n))

    # pick best candidate
    best_sq = None
    best_score = -1.0
    for cand in candidates:
        if cand is None:
            continue
        # sanitize: ensure validity
        if len(cand) != n:
            continue
        if _valid_all(cand):
            sc = _total(cand)
            if sc > best_score:
                best_score = sc
                best_sq = cand
        else:
            # repair: just use grid
            pass

    if best_sq is None:
        best_sq = _grid_solution(n)

    # Local optimization with time limit.
    import time
    t_start = time.time()
    time_limit = 10.0  # seconds; total program limit is 60 but we are safe
    # Multiple restarts with different seeds for better results.
    seeds = [1, 2, 3, 7, 11, 42, 123, 2024]
    best_sq = _local_optimize(best_sq, time_budget=min(3.0, time_limit / len(seeds)), rng=random.Random(1))
    best_sc = _total(best_sq)
    for k, sd in enumerate(seeds):
        if time.time() - t_start > time_limit:
            break
        rng = random.Random(sd)
        # perturb
        pert = []
        for (cx, cy, ang, s) in best_sq:
            if s <= 1e-12:
                pert.append((0.5, 0.5, 0.0, 0.0))
                continue
            nc = min(max(cx + rng.uniform(-0.02, 0.02), 0.0), 1.0)
            ny = min(max(cy + rng.uniform(-0.02, 0.02), 0.0), 1.0)
            na = ang + rng.uniform(-0.05, 0.05)
            ns = s * rng.uniform(0.98, 1.02)
            pert.append((nc, ny, na, ns))
        if not _valid_all(pert):
            # fix by shrinking
            pert = []
            cur = [list(b) for b in best_sq]
            for i in range(n):
                nx = cur[i]
                # try shrink until valid with others
                for j in range(100):
                    cand = (nx[0], nx[1], nx[2], nx[3] * (1.0 - 0.01 * j))
                    if _inside_unit(*cand):
                        ok = True
                        for kk in range(i):
                            if _overlap(cand, tuple(cur[kk])):
                                ok = False
                                break
                        if ok:
                            cur[i] = list(cand)
                            break
                else:
                    cur[i] = [nx[0], nx[1], nx[2], 0.0]
            pert = [tuple(x) for x in cur]
        opt = _local_optimize(pert, time_budget=min(2.0, max(0.5, (time_limit - (time.time() - t_start)) / (len(seeds) - k))), rng=rng)
        sc = _total(opt)
        if sc > best_sc:
            best_sc = sc
            best_sq = opt

    # Final safety: return n tuples
    result = []
    for i in range(n):
        if i < len(best_sq):
            cx, cy, ang, s = best_sq[i]
            cx = min(max(cx, 0.0), 1.0)
            cy = min(max(cy, 0.0), 1.0)
            s = max(0.0, min(s, 1.0))
            result.append((float(cx), float(cy), float(ang % 1.0), float(s)))
        else:
            result.append((0.5, 0.5, 0.0, 0.0))
    # Ensure valid: if not, fall back to grid.
    if not _valid_all(result):
        result = _grid_solution(n)
        # shrink/clamp
        result = [(min(max(a, 0.0), 1.0), min(max(b, 0.0), 1.0), c % 1.0, min(max(d, 0.0), 1.0))
                  for (a, b, c, d) in result]
    return result
