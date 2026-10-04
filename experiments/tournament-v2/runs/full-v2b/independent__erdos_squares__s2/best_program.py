import math
import random
import time
from functools import lru_cache

# ---------- geometry helpers ----------

def square_vertices(cx, cy, angle, side):
    """Return the 4 corners of a square (counter-clockwise)."""
    if side <= 0.0:
        return [(cx, cy)] * 4
    a = angle * 2.0 * math.pi
    ca, sa = math.cos(a), math.sin(a)
    hs = side * 0.5
    # local corners
    pts = [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def _proj(poly, axis):
    ax, ay = axis
    vals = [x * ax + y * ay for x, y in poly]
    return min(vals), max(vals)


def overlap(sq1, sq2, eps=1e-12):
    """Separating axis test for two convex polygons. True if interiors overlap."""
    p1 = square_vertices(*sq1)
    p2 = square_vertices(*sq2)
    # edges of both polygons
    edges = []
    for poly in (p1, p2):
        m = len(poly)
        for i in range(m):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % m]
            edges.append((x2 - x1, y2 - y1))
    for ex, ey in edges:
        # normal axis
        ax, ay = -ey, ex
        if ax * ax + ay * ay < 1e-30:
            continue
        lo1, hi1 = _proj(p1, (ax, ay))
        lo2, hi2 = _proj(p2, (ax, ay))
        if hi1 <= lo2 + eps or hi2 <= lo1 + eps:
            return False
    return True


def valid_config(squares):
    """Check all squares inside [0,1]^2 and pairwise non-overlap."""
    n = len(squares)
    for cx, cy, ang, s in squares:
        if s < 0.0 or s > 1.0:
            return False
        if cx < -1e-12 or cx > 1.0 + 1e-12 or cy < -1e-12 or cy > 1.0 + 1e-12:
            return False
        # quick bounding-box check (rotated square half-extent <= s*sqrt(2)/2)
        r = s * 0.7071067811865476
        if cx - r < -1e-9 or cx + r > 1.0 + 1e-9 or cy - r < -1e-9 or cy + r > 1.0 + 1e-9:
            # may still be valid; do exact check
            pass
        vs = square_vertices(cx, cy, ang, s)
        for x, y in vs:
            if x < -1e-9 or x > 1.0 + 1e-9 or y < -1e-9 or y > 1.0 + 1e-9:
                return False
    for i in range(n):
        for j in range(i + 1, n):
            if squares[i][3] <= 0.0 or squares[j][3] <= 0.0:
                continue
            if overlap(squares[i], squares[j]):
                return False
    return True


def score(squares):
    return sum(s[3] for s in squares)


def in_unit_square(cx, cy, side, angle, eps=1e-9):
    if side < 0.0:
        return False
    vs = square_vertices(cx, cy, angle, side)
    for x, y in vs:
        if x < -eps or x > 1.0 + eps or y < -eps or y > 1.0 + eps:
            return False
    return True


def overlaps_any(sq, squares, idx=None, eps=1e-12):
    if sq[3] <= 0.0:
        return False
    for k, s in enumerate(squares):
        if idx is not None and k == idx:
            continue
        if s[3] <= 0.0:
            continue
        if overlap(sq, s, eps):
            return True
    return False


# ---------- deterministic constructions ----------

def grid_solution(n):
    k = int(math.isqrt(n))
    if k == 0:
        return [(0.5, 0.5, 0.0, 0.0)] * n
    s = 1.0 / k
    res = [((i + 0.5) * s, (j + 0.5) * s, 0.0, s) for i in range(k) for j in range(k)]
    if len(res) < n:
        # try to replace some by smaller ones in remaining gaps (simple: add zero)
        res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res[:n]


def row_solution(n):
    """Place n squares in a row-like packing, sizes decreasing."""
    if n == 0:
        return []
    # all in one row: side = 1/n
    s = 1.0 / n
    return [((i + 0.5) * s, 0.5, 0.0, s) for i in range(n)]


def tiered_rows_solution(n):
    """Guillotine-ish: split into rows, squares in each row equal size."""
    best = None
    best_score = -1.0
    for rows in range(1, n + 1):
        cols = (n + rows - 1) // rows
        if cols * rows < n:
            continue
        # find max side in a cell
        s = min(1.0 / cols, 1.0 / rows)
        # number of real squares
        cnt = min(n, cols * rows)
        sc = cnt * s
        if sc > best_score:
            best_score = sc
            best = (rows, cols, s, cnt)
    rows, cols, s, cnt = best
    res = []
    for r in range(rows):
        for c in range(cols):
            if len(res) >= n:
                break
            res.append(((c + 0.5) * (1.0 / cols), (r + 0.5) * (1.0 / rows), 0.0, s))
        if len(res) >= n:
            break
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res


def mixed_grid_solution(n):
    """Try grids with a few smaller squares filling gaps, greedy row/col splits."""
    # Generate several candidate guillotine layouts: recursive partition of unit square
    # into rectangles, each filled with squares of max size. Choose best.
    candidates = []

    def rec_partition(rect, remaining, out):
        if remaining <= 0:
            return
        x, y, w, h = rect
        # fill rectangle with maximum grid of identical squares
        # choose k so that k*k <= remaining and side maximized
        best = None
        for a in range(1, remaining + 1):
            b = (remaining + a - 1) // a
            s = min(w / a, h / b)
            used = min(remaining, a * b)
            val = used * s
            if best is None or val > best[0]:
                best = (val, a, b, s, used)
        val, a, b, s, used = best
        # place a x b squares
        cnt = 0
        for i in range(a):
            for j in range(b):
                if cnt >= remaining:
                    break
                out.append((x + (i + 0.5) * (w / a), y + (j + 0.5) * (h / b), 0.0, s))
                cnt += 1
            if cnt >= remaining:
                break
        # leftover uses tiny zero squares, but maybe there is space; ignore for now
        while len(out) < n:
            out.append((0.5, 0.5, 0.0, 0.0))

    # Try a few partitions by splitting along x or y at 0.5, 0.4, etc.
    for split_x in (0.5, 0.618, 0.382, 0.4, 0.6):
        for split_y in (0.5, 0.618, 0.382, 0.4, 0.6):
            for n_left in range(1, n):
                out = []
                # left rectangle
                rec_partition((0.0, 0.0, split_x, split_y), n_left, out)
                # right rectangle
                rec_partition((split_x, 0.0, 1.0 - split_x, split_y), n - n_left, out)
                # bottom rectangle
                # actually simpler: split horizontally
                out2 = []
                rec_partition((0.0, 0.0, 1.0, split_y), n_left, out2)
                rec_partition((0.0, split_y, 1.0, 1.0 - split_y), n - n_left, out2)
                if len(out2) == n and valid_config(out2):
                    candidates.append(out2)
                if len(out) == n and valid_config(out):
                    candidates.append(out)
    # Also simple vertical split partitions with grid in each part
    for k in range(1, 11):
        for n_left in range(1, n):
            f = k / 11.0
            out = []
            rec_partition((0.0, 0.0, f, 1.0), n_left, out)
            rec_partition((f, 0.0, 1.0 - f, 1.0), n - n_left, out)
            if len(out) == n and valid_config(out):
                candidates.append(out)
    if not candidates:
        return tiered_rows_solution(n)
    return max(candidates, key=score)


# ---------- local search / optimization ----------

def repair(squares, iters=30):
    """Push squares inside and remove overlaps by shrinking the smallest offender."""
    n = len(squares)
    for _ in range(iters):
        changed = False
        # push inside
        for i in range(n):
            cx, cy, ang, s = squares[i]
            if s <= 0.0:
                continue
            vs = square_vertices(cx, cy, ang, s)
            minx = min(p[0] for p in vs)
            maxx = max(p[0] for p in vs)
            miny = min(p[1] for p in vs)
            maxy = max(p[1] for p in vs)
            dx = 0.0
            if minx < 0.0:
                dx = -minx
            elif maxx > 1.0:
                dx = 1.0 - maxx
            dy = 0.0
            if miny < 0.0:
                dy = -miny
            elif maxy > 1.0:
                dy = 1.0 - maxy
            if abs(dx) > 1e-12 or abs(dy) > 1e-12:
                squares[i] = (cx + dx, cy + dy, ang, s)
                changed = True
        # fix overlaps by shrinking
        for i in range(n):
            if squares[i][3] <= 0.0:
                continue
            for j in range(i + 1, n):
                if squares[j][3] <= 0.0:
                    continue
                if overlap(squares[i], squares[j]):
                    # shrink both a bit
                    si = squares[i]
                    sj = squares[j]
                    ns_i = max(0.0, si[3] * 0.98 - 1e-4)
                    ns_j = max(0.0, sj[3] * 0.98 - 1e-4)
                    squares[i] = (si[0], si[1], si[2], ns_i)
                    squares[j] = (sj[0], sj[1], sj[2], ns_j)
                    changed = True
        if not changed:
            break
    return squares


def optimize(n, time_limit):
    start_time = time.time()

    candidates = []
    candidates.append(grid_solution(n))
    candidates.append(row_solution(n))
    candidates.append(tiered_rows_solution(n))
    try:
        candidates.append(mixed_grid_solution(n))
    except Exception:
        pass

    best = None
    best_score = -1.0
    for c in candidates:
        if len(c) != n:
            continue
        c = [(x, y, a % 1.0, s) for (x, y, a, s) in c]
        if valid_config(c):
            sc = score(c)
            if sc > best_score:
                best_score = sc
                best = [list(t) for t in c]

    if best is None:
        # fallback: all zeros
        return [(0.5, 0.5, 0.0, 0.0)] * n

    best = [list(t) for t in best]

    # Simulated-annealing / random restart local search
    # Use adaptive moves: try to increase sizes, adjust positions/angles.
    # We keep the configuration feasible throughout by rejecting infeasible moves.

    current = [list(t) for t in best]
    current_score = best_score
    temp0 = 0.05
    it = 0
    # max steps based on time
    while time.time() - start_time < time_limit * 0.95:
        it += 1
        temp = temp0 * max(0.0, 1.0 - (time.time() - start_time) / time_limit)

        # pick a random square (non-zero preferably)
        for _try in range(10):
            i = random.randrange(n)
            if current[i][3] > 0.0 or random.random() < 0.2:
                break
        old = current[i][:]
        mode = random.random()
        if mode < 0.45:
            # change size
            delta = random.gauss(0.0, 0.02) * (1.0 + current_score / n)
            ns = old[3] + delta
            if ns < 0.0:
                ns = 0.0
            if ns > 1.0:
                ns = 1.0
            current[i][3] = ns
        elif mode < 0.75:
            # move position
            dx = random.gauss(0.0, 0.01)
            dy = random.gauss(0.0, 0.01)
            current[i][0] = old[0] + dx
            current[i][1] = old[1] + dy
        elif mode < 0.9:
            # rotate
            current[i][2] = (old[2] + random.gauss(0.0, 0.02)) % 1.0
        else:
            # change size significantly (try to grow)
            ns = old[3] * (1.0 + abs(random.gauss(0.0, 0.05)))
            if ns > 1.0:
                ns = 1.0
            current[i][3] = ns

        # clamp inside unit square by repair (cheap adjust)
        cur = current[i]
        if not in_unit_square(cur[0], cur[1], cur[3], cur[2]):
            # revert or push inside
            current[i] = old[:]
            continue

        if overlaps_any(current[i], current, idx=i):
            current[i] = old[:]
            continue

        new_score = current_score - old[3] + current[i][3]
        # accept if improved or with probability
        if new_score >= current_score or random.random() < math.exp((new_score - current_score) / max(temp, 1e-9)):
            current_score = new_score
            if new_score > best_score + 1e-12:
                # validate fully sometimes
                if valid_config([tuple(t) for t in current]):
                    best_score = new_score
                    best = [t[:] for t in current]
        else:
            current[i] = old[:]

        # Occasionally try a bigger coordinated move: enlarge one and shrink neighbors
        if it % 500 == 0:
            i = random.randrange(n)
            if current[i][3] > 0.0:
                # try to grow this square and shrink any overlapping
                grow = 1.0 + random.uniform(0.01, 0.1)
                ns = min(1.0, current[i][3] * grow)
                trial = [t[:] for t in current]
                trial[i][3] = ns
                # repair overlaps by shrinking others involved
                for j in range(n):
                    if j == i:
                        continue
                    if trial[j][3] <= 0.0:
                        continue
                    if overlap(tuple(trial[i]), tuple(trial[j])):
                        trial[j][3] *= 0.95
                if valid_config([tuple(t) for t in trial]):
                    sc = score(trial)
                    if sc > best_score:
                        best_score = sc
                        best = [t[:] for t in trial]
                        current = [t[:] for t in trial]
                        current_score = sc

        # periodic restart from best
        if it % 5000 == 0:
            current = [t[:] for t in best]
            current_score = best_score

    # final greedy polish: try to increase each square size as much as possible
    for _ in range(50):
        improved = False
        for i in range(n):
            if best[i][3] <= 0.0:
                continue
            lo, hi = best[i][3], 1.0
            # binary search max size without collision
            for _bs in range(30):
                mid = (lo + hi) * 0.5
                trial = [t[:] for t in best]
                trial[i][3] = mid
                if in_unit_square(trial[i][0], trial[i][1], mid, trial[i][2]) and not overlaps_any(trial[i], trial, idx=i):
                    lo = mid
                    improved = True
                else:
                    hi = mid
            if lo > best[i][3] + 1e-12:
                best[i][3] = lo
                improved = True
        if not improved:
            break

    # ensure valid output
    out = [tuple(t) for t in best]
    # final clamp: if invalid, shrink until valid
    if not valid_config(out):
        out = [(0.5, 0.5, 0.0, 0.0)] * n

    return out[:n]


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    if n == 2:
        # two squares side by side, each 0.5 wide -> sum 1.0
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    # time budget: 60 seconds total, allocate adaptively but keep under
    time_limit = 55.0
    # For very small n we can spend less time
    if n <= 5:
        time_limit = 20.0
    elif n <= 20:
        time_limit = 40.0
    try:
        return optimize(n, time_limit)
    except Exception:
        # safe fallback
        k = int(math.isqrt(n))
        if k == 0:
            return [(0.5, 0.5, 0.0, 0.0)] * n
        s = 1.0 / k
        res = [((i + 0.5) * s, (j + 0.5) * s, 0.0, s) for i in range(k) for j in range(k)]
        res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
        return res[:n]
