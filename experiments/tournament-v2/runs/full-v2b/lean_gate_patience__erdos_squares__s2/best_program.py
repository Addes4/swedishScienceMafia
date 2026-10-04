# EVOLVE-BLOCK-START
"""Deterministic strip/grid tiling enumerator + physics-relaxation refinement.

The objective is the sum of side lengths.  For most n the best layouts are
row/column (grid-like) constructions: a big rectangle tiled by an r x c grid
plus a leftover strip tiled by a secondary grid.  We enumerate these seeds
exhaustively, relax each to feasibility, then apply per-square grow-and-nudge.
A randomized greedy multi-start is kept as a fallback for irregular n.
"""
import math
import random


def _extent(ang, sz):
    t = ang * 2.0 * math.pi
    c, s = abs(math.cos(t)), abs(math.sin(t))
    h = sz * 0.5
    return h * (c + s), h * (c + s)


def _penetration(a, b):
    ax, ay, aa, asz = a
    bx, by, ba, bsz = b
    if asz <= 1e-12 or bsz <= 1e-12:
        return -1.0
    ta = aa * 2.0 * math.pi
    ca, sa = math.cos(ta), math.sin(ta)
    tb = ba * 2.0 * math.pi
    cb, sb = math.cos(tb), math.sin(tb)
    ha = asz * 0.5
    hb = bsz * 0.5
    axes = [(ca, sa), (-sa, ca), (cb, sb), (-sb, cb)]
    minov = float('inf')
    for (ux, uy) in axes:
        ea = abs(ux * ca + uy * sa) + abs(ux * (-sa) + uy * ca)
        eb = abs(ux * cb + uy * sb) + abs(ux * (-sb) + uy * cb)
        dist = abs(ux * (ax - bx) + uy * (ay - by))
        ov = ha * ea + hb * eb - dist
        if ov < minov:
            minov = ov
    return minov


def _clamp_in_unit(sq, i):
    ex, ey = _extent(sq[i][2], sq[i][3])
    lo_x, hi_x = ex, 1.0 - ex
    lo_y, hi_y = ey, 1.0 - ey
    if lo_x > hi_x:
        sq[i][0] = 0.5
    else:
        sq[i][0] = min(max(sq[i][0], lo_x), hi_x)
    if lo_y > hi_y:
        sq[i][1] = 0.5
    else:
        sq[i][1] = min(max(sq[i][1], lo_y), hi_y)


def _project(squares, iters=200):
    sq = [list(s) for s in squares]
    m = len(sq)
    for i in range(m):
        _clamp_in_unit(sq, i)
    for _ in range(iters):
        moved = False
        for i in range(m):
            if sq[i][3] <= 1e-12:
                continue
            for j in range(i + 1, m):
                if sq[j][3] <= 1e-12:
                    continue
                ov = _penetration(sq[i], sq[j])
                if ov > 1e-9:
                    moved = True
                    dx = sq[i][0] - sq[j][0]
                    dy = sq[i][1] - sq[j][1]
                    d = math.hypot(dx, dy)
                    if d < 1e-9:
                        ang = random.random() * 2.0 * math.pi
                        dx, dy, d = math.cos(ang), math.sin(ang), 1.0
                    push = ov * 0.5 + 1e-4
                    ux, uy = dx / d, dy / d
                    sq[i][0] += ux * push
                    sq[i][1] += uy * push
                    sq[j][0] -= ux * push
                    sq[j][1] -= uy * push
        for i in range(m):
            _clamp_in_unit(sq, i)
        if not moved:
            break
    return [tuple(s) for s in sq]


def _total_overlap(squares):
    tot = 0.0
    m = len(squares)
    for i in range(m):
        if squares[i][3] <= 1e-12:
            continue
        for j in range(i + 1, m):
            if squares[j][3] <= 1e-12:
                continue
            ov = _penetration(squares[i], squares[j])
            if ov > 0:
                tot += ov
    return tot


def _max_outside(squares):
    worst = 0.0
    for (cx, cy, ang, sz) in squares:
        if sz <= 1e-12:
            continue
        ex, ey = _extent(ang, sz)
        worst = max(worst, ex - cx, cx - (1.0 - ex), ey - cy, cy - (1.0 - ey))
    return worst


def _feasible(squares):
    return _max_outside(squares) <= 1e-7 and _total_overlap(squares) <= 1e-6


def _grid_tiling(n, r, c, horiz, cap=None):
    """Seed: unit square split into a main rectangle (r x c grid) and a strip.

    horiz=True: main rectangle occupies the bottom band of height h, tiled by
    r rows x c cols; the top strip (height 1-h) holds the remaining squares in
    a single-row/single-column packing.  Returns a list of squares or None.
    """
    if r < 1 or c < 1:
        return None
    main = r * c
    if main > n:
        return None
    rem = n - main
    # main rectangle tiling: choose width to match strip width
    # Option A: main rectangle spans full width, height = c/r ratio band.
    # We parameterize a band of height h at the bottom, main grid c cols x r rows.
    # side = min(h/r, 1.0/c); extra leftover handled by leaving unused area.
    # Simple: side_main = min(h / r, 1.0 / c) but h unknown -> use full width.
    # Use: col width = 1/c (full width). Then row height = side; need r rows fit.
    # Let side = 1/c (grid uses full width).  Height used = r/c.
    s_main = 1.0 / c
    used_h = r * s_main
    if used_h > 1.0 + 1e-12:
        return None
    squares = []

    if horiz:
        # bottom band of height r/c filled with r x c grid
        for j in range(r):
            for i in range(c):
                squares.append((i * s_main + s_main / 2,
                                j * s_main + s_main / 2, 0.0, s_main))
        # top strip: height 1 - r/c, width 1.  fill `rem` squares as a row.
        strip_h = 1.0 - used_h
        if strip_h < -1e-9:
            return None
        if rem > 0:
            if strip_h <= 1e-12:
                # no room: place rem as tiny points on the top edge
                for _ in range(rem):
                    squares.append((0.5, 1.0, 0.0, 0.0))
            else:
                # try to pack rem squares in the strip: single row of `rem`
                s = min(strip_h, 1.0 / rem)
                total_w = rem * s
                x0 = (1.0 - total_w) / 2.0
                yc = used_h + strip_h / 2.0
                for i in range(rem):
                    squares.append((x0 + i * s + s / 2, yc, 0.0, s))
    else:
        # vertical: left band of width r/c filled with r x c grid (r cols)
        s_main = 1.0 / c
        used_w = r * s_main
        if used_w > 1.0 + 1e-12:
            return None
        for j in range(c):
            for i in range(r):
                squares.append((i * s_main + s_main / 2,
                                j * s_main + s_main / 2, 0.0, s_main))
        strip_w = 1.0 - used_w
        if rem > 0:
            if strip_w <= 1e-12:
                for _ in range(rem):
                    squares.append((1.0, 0.5, 0.0, 0.0))
            else:
                s = min(strip_w, 1.0 / rem)
                total_h = rem * s
                y0 = (1.0 - total_h) / 2.0
                xc = used_w + strip_w / 2.0
                for i in range(rem):
                    squares.append((xc, y0 + i * s + s / 2, 0.0, s))
    if len(squares) != n:
        return None
    return squares


def _grow_and_nudge(squares, rng, rounds=8):
    best = [list(s) for s in squares]
    for _ in range(rounds):
        improved = False
        order = list(range(len(best)))
        rng.shuffle(order)
        for i in order:
            if best[i][3] <= 1e-12:
                continue
            delta = 0.01 * (1.0 - best[i][3]) + 1e-4
            trial = [s[:] for s in best]
            trial[i][3] = min(0.999, best[i][3] + delta)
            trial = _project(trial, iters=80)
            if _feasible(trial) and sum(s[3] for s in trial) > sum(s[3] for s in best) + 1e-12:
                best = [list(s) for s in trial]
                improved = True
        if not improved:
            break
    return [tuple(s) for s in best]


def _greedy_start(n, rng):
    base = 1.0 / max(1.0, math.sqrt(n))
    sizes = []
    for _ in range(n):
        f = rng.uniform(0.55, 1.35)
        sizes.append(min(0.999, base * f * rng.uniform(0.8, 1.2)))
    order = list(range(n))
    rng.shuffle(order)
    placed = []
    for idx in order:
        sz = sizes[idx]
        best = None
        best_score = -1e18
        for _try in range(40):
            ang = rng.choice([0.0, 0.25, rng.random()])
            ex, ey = _extent(ang, sz)
            lo_x, hi_x = ex, 1.0 - ex
            lo_y, hi_y = ey, 1.0 - ey
            if lo_x > hi_x or lo_y > hi_y:
                continue
            cx = rng.uniform(lo_x, hi_x)
            cy = rng.uniform(lo_y, hi_y)
            cand = (cx, cy, ang, sz)
            ov = 0.0
            ok = True
            for p in placed:
                ov += _penetration(cand, p)
                if ov > 0.25 * sz:
                    ok = False
                    break
            score = -ov
            if ok and score > best_score:
                best_score = score
                best = cand
        if best is None:
            ex, ey = _extent(0.0, sz)
            cx = min(max(0.5, ex), 1.0 - ex) if ex <= 0.5 else 0.5
            cy = min(max(0.5, ey), 1.0 - ey) if ey <= 0.5 else 0.5
            best = (cx, cy, 0.0, sz)
        placed.append(best)
    return placed


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    rng = random.Random(987654321)
    best = None
    best_score = -1e18

    def consider(squares):
        nonlocal best, best_score
        if squares is None:
            return
        rel = _project(squares, iters=150)
        if _feasible(rel):
            sc = sum(s[3] for s in rel)
            if sc > best_score:
                best_score = sc
                best = rel

    # Structured double-grid strip tilings (deterministic enumeration).
    rng_top = random.Random(12345)
    for r in range(1, n + 1):
        for c in range(1, n + 1):
            if r * c > n:
                continue
            for horiz in (True, False):
                seed = _grid_tiling(n, r, c, horiz)
                consider(seed)

    # sqrt grid.
    k = math.isqrt(n)
    if k >= 1:
        side = 1.0 / k
        grid = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                for i in range(k) for j in range(k)]
        grid += [(0.5, 0.5, 0.0, 0.0)] * (n - len(grid))
        consider(grid[:n])

    # Randomized multi-start fallback.
    tries = 30 if n <= 12 else (16 if n <= 30 else 8)
    for t in range(tries):
        start = _greedy_start(n, rng)
        consider(start)

    # Refine the best feasible configuration.
    if best is not None and _feasible(best):
        for _ in range(3):
            grown = _grow_and_nudge(best, rng)
            if _feasible(grown) and sum(s[3] for s in grown) > best_score + 1e-12:
                best = grown
                best_score = sum(s[3] for s in grown)
            else:
                break

    if best is None:
        best = [(0.5, 0.5, 0.0, 0.0)] * n

    result = list(best)
    if len(result) < n:
        result += [(0.5, 0.5, 0.0, 0.0)] * (n - len(result))
    return result[:n]
# EVOLVE-BLOCK-END
