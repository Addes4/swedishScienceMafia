# EVOLVE-BLOCK-START
"""General square packing method.

Strategy: a square can be subdivided into a set of axis-aligned rectangles arranged
in a "guillotine" layout (recursively cut a rectangle by a vertical or horizontal
line).  Within each leaf rectangle we may also place smaller axis-aligned squares.

We search over several structured families:
  1. The best equal-grid (b rows, c columns) layout.
  2. "One big square" layouts: a large square in a corner plus a grid in the
     remaining L-shaped region (split into two rectangles).
  3. Random guillotine partitions, tiled per leaf.
  4. Randomized multi-size greedy packing (bottom-left).
  5. Rotation-aware big corner (45 degrees).
Finally a coordinate-descent inflation refinement is applied.
"""
import math
import random


def _grid_solution(n):
    best_total = -1.0
    best = None
    for b in range(1, n + 1):
        c = (n + b - 1) // b
        side = min(1.0 / c, 1.0 / b)
        total = side * n
        if total > best_total:
            best_total = total
            best = (b, c, side)
    b, c, side = best
    squares = []
    count = 0
    for j in range(b):
        for i in range(c):
            if count >= n:
                break
            cx = (i + 0.5) * (1.0 / c)
            cy = (j + 0.5) * (1.0 / b)
            squares.append((cx, cy, 0.0, side))
            count += 1
    return squares[:n]


def _can_place(rect, others, tol=1e-12):
    x0, y0, s = rect
    if x0 < -tol or y0 < -tol or x0 + s > 1 + tol or y0 + s > 1 + tol:
        return False
    x1, y1 = x0 + s, y0 + s
    for (a, b, t) in others:
        ax1, by1 = a + t, b + t
        if x0 < ax1 - tol and a < x1 - tol and y0 < by1 - tol and b < y1 - tol:
            return False
    return True


def _greedy_pack(sizes):
    placed = []
    for s in sizes:
        if s <= 1e-12:
            continue
        xs = {0.0}
        ys = {0.0}
        for (a, b, t) in placed:
            xs.add(a + t)
            ys.add(b + t)
            xs.add(a)
            ys.add(b)
        cand = []
        for X in xs:
            for Y in ys:
                if _can_place((X, Y, s), placed):
                    cand.append((X, Y))
        if not cand:
            return None
        cand.sort(key=lambda p: (p[1], p[0]))
        X, Y = cand[0]
        placed.append((X, Y, s))
    return placed


def _seq_to_squares(placed):
    return [(x0 + s / 2.0, y0 + s / 2.0, 0.0, s) for (x0, y0, s) in placed]


def _valid(placed):
    for i in range(len(placed)):
        x0, y0, s = placed[i]
        if x0 < -1e-9 or y0 < -1e-9 or x0 + s > 1 + 1e-9 or y0 + s > 1 + 1e-9:
            return False
        for j in range(i + 1, len(placed)):
            a, b, t = placed[j]
            if x0 < a + t - 1e-9 and a < x0 + s - 1e-9 and y0 < b + t - 1e-9 and b < y0 + s - 1e-9:
                return False
    return True


def _tile_rect(w, h, count):
    """Place `count` axis-aligned squares inside a w x h rectangle, offset (0,0).
    Return list of (x0, y0, s) or None.  Use a grid of equal squares."""
    if count <= 0:
        return []
    best = None
    best_s = -1.0
    for cols in range(1, count + 1):
        rows = (count + cols - 1) // cols
        s = min(w / cols, h / rows)
        if s > best_s:
            best_s = s
            best = (cols, rows, s)
    cols, rows, s = best
    out = []
    cnt = 0
    for j in range(rows):
        for i in range(cols):
            if cnt >= count:
                break
            out.append((i * s, j * s, s))
            cnt += 1
    return out


def _guillotine_search(n, best_so_far, rng, budget=400):
    """Random guillotine partition of the unit square into leaves, tile leaves."""
    best = None
    best_total = best_so_far
    for _ in range(budget):
        leaves = [(0.0, 0.0, 1.0, 1.0, 0)]
        target_leaves = rng.randint(2, min(n, 6))
        for _ in range(target_leaves - 1):
            idx = rng.randrange(len(leaves))
            x, y, w, h, d = leaves.pop(idx)
            if w >= h:
                if w < 1e-6:
                    leaves.append((x, y, w, h, d))
                    continue
                f = rng.uniform(0.3, 0.7)
                leaves.append((x, y, w * f, h, d + 1))
                leaves.append((x + w * f, y, w * (1 - f), h, d + 1))
            else:
                if h < 1e-6:
                    leaves.append((x, y, w, h, d))
                    continue
                f = rng.uniform(0.3, 0.7)
                leaves.append((x, y, w, h * f, d + 1))
                leaves.append((x, y + h * f, w, h * (1 - f), d + 1))
        if len(leaves) > n:
            continue
        cnts = [1] * len(leaves)
        rem = n - len(leaves)
        if rem < 0:
            continue
        while rem > 0:
            idx = rng.randrange(len(leaves))
            cnts[idx] += 1
            rem -= 1
        placed = []
        ok = True
        total = 0.0
        for (x, y, w, h, d), cnt in zip(leaves, cnts):
            tiles = _tile_rect(w, h, cnt)
            if tiles is None:
                ok = False
                break
            for (tx, ty, s) in tiles:
                placed.append((x + tx, y + ty, s))
                total += s
        if not ok or len(placed) != n:
            continue
        if total > best_total and _valid(placed):
            best_total = total
            best = placed
    return best


def _try_sequences(n, rng, tries):
    best = None
    best_total = -1.0
    for _ in range(tries):
        sizes = []
        k_big = rng.randint(0, max(0, min(3, n)))
        for _ in range(k_big):
            sizes.append(rng.uniform(0.3, 1.0))
        while len(sizes) < n:
            sizes.append(rng.uniform(0.05, 0.6))
        sizes = sizes[:n]
        sizes.sort(reverse=True)
        placed = _greedy_pack(sizes)
        if placed is None:
            continue
        total = sum(p[2] for p in placed)
        if total > best_total:
            best_total = total
            best = placed
    return best


# ---------- rotation-aware validity ----------

def _corners(cx, cy, ang, s):
    th = ang * 2.0 * math.pi
    ct = abs(math.cos(th))
    st = abs(math.sin(th))
    hx = 0.5 * s * (ct + st)
    hy = 0.5 * s * (ct + st)
    return cx - hx, cy - hy, cx + hx, cy + hy


def _rot_valid(sqs, tol=1e-9):
    """Check squares (cx,cy,ang,s) are in unit box and non-overlapping (SAT)."""
    boxes = []
    for (cx, cy, ang, s) in sqs:
        th = ang * 2.0 * math.pi
        ct = math.cos(th)
        st = math.sin(th)
        d = s * 0.5
        pts = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x = cx + sx * d * ct - sy * d * st
            y = cy + sx * d * st + sy * d * ct
            if x < -tol or x > 1 + tol or y < -tol or y > 1 + tol:
                return False
            pts.append((x, y))
        axes = [(ct, st), (-st, ct)]
        boxes.append((pts, axes, cx, cy, s))
    m = len(boxes)
    for i in range(m):
        pi, ai, cxi, cyi, si = boxes[i]
        for j in range(i + 1, m):
            pj, aj, cxj, cyj, sj = boxes[j]
            if abs(cxi - cxj) > (si + sj) * 0.75:
                continue
            if abs(cyi - cyj) > (si + sj) * 0.75:
                continue
            sep = False
            for (ax, ay) in ai + aj:
                mini = min(px * ax + py * ay for (px, py) in pi)
                maxi = max(px * ax + py * ay for (px, py) in pi)
                minj = min(px * ax + py * ay for (px, py) in pj)
                maxj = max(px * ax + py * ay for (px, py) in pj)
                if maxi <= minj + tol or maxj <= mini + tol:
                    sep = True
                    break
            if not sep:
                return False
    return True


def _inflate_local(sqs, rounds=400, seed=0):
    """Coordinate-descent: try to grow each square; accept if still valid."""
    sqs = [list(s) for s in sqs]
    rng = random.Random(seed)
    improved = True
    it = 0
    while improved and it < rounds:
        improved = False
        it += 1
        order = list(range(len(sqs)))
        rng.shuffle(order)
        for k in order:
            cx, cy, ang, s = sqs[k]
            lo, hi = 1.0, 4.0
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                trial = [list(t) for t in sqs]
                trial[k][3] = s * mid
                if _rot_valid(trial):
                    lo = mid
                else:
                    hi = mid
            if lo > 1.0 + 1e-7:
                sqs[k][3] = s * lo
                improved = True
        for k in order:
            cx, cy, ang, s = sqs[k]
            for dx, dy in ((0.002, 0), (-0.002, 0), (0, 0.002), (0, -0.002)):
                trial = [list(t) for t in sqs]
                trial[k][0] = cx + dx
                trial[k][1] = cy + dy
                if _rot_valid(trial):
                    lo, hi = 1.0, 4.0
                    for _ in range(20):
                        mid = 0.5 * (lo + hi)
                        t2 = [list(t) for t in trial]
                        t2[k][3] = s * mid
                        if _rot_valid(t2):
                            lo = mid
                        else:
                            hi = mid
                    if lo > 1.0 + 1e-7:
                        trial[k][3] = s * lo
                        sqs = trial
                        improved = True
                        break
    return [tuple(t) for t in sqs]


def _rotated_big_corner(n):
    """One big square rotated 45 degrees in a corner, then fill the rest with
    axis-aligned squares in the leftover region."""
    best = None
    best_total = -1.0
    rem = n - 1
    if rem < 0:
        return None
    for i in range(1, 150):
        s = i / 100.0
        half = s / math.sqrt(2.0)
        if 2 * half > 1.0:
            break
        bx = half
        by = half
        placed = [(bx, by, 0.125, s)]
        total = s
        for c2 in range(1, rem + 1):
            w2 = (1 - 2 * half) / c2
            if w2 <= 0:
                break
            r2 = int(1.0 / w2 + 1e-9)
            cap2 = c2 * r2
            need2 = min(rem, cap2)
            need3 = rem - need2
            if need3 < 0:
                continue
            if need3 == 0:
                tot = total + w2 * need2
                if tot > best_total:
                    cand = list(placed)
                    cnt = 0
                    for j in range(r2):
                        for ii in range(c2):
                            if cnt >= need2:
                                break
                            cand.append((2 * half + ii * w2 + w2 / 2.0,
                                         j * w2 + w2 / 2.0, 0.0, w2))
                            cnt += 1
                    if len(cand) == n and _rot_valid(cand):
                        best_total = tot
                        best = cand
                continue
            for c3 in range(1, need3 + 1):
                w3 = (2 * half) / c3
                r3 = int((1 - 2 * half) / w3 + 1e-9)
                if r3 < 1 or c3 * r3 < need3:
                    continue
                tot = total + w2 * need2 + w3 * need3
                if tot > best_total:
                    cand = list(placed)
                    cnt = 0
                    for j in range(r2):
                        for ii in range(c2):
                            if cnt >= need2:
                                break
                            cand.append((2 * half + ii * w2 + w2 / 2.0,
                                         j * w2 + w2 / 2.0, 0.0, w2))
                            cnt += 1
                    cnt = 0
                    for j in range(r3):
                        for ii in range(c3):
                            if cnt >= need3:
                                break
                            cand.append((ii * w3 + w3 / 2.0,
                                         2 * half + j * w3 + w3 / 2.0, 0.0, w3))
                            cnt += 1
                    if len(cand) == n and _rot_valid(cand):
                        best_total = tot
                        best = cand
                break
    return best


def _big_square_corner(n):
    """One big axis-aligned square S in a corner; the remaining L-shaped region
    (right rectangle + top rectangle) is tiled by grids of squares.  Enumerate
    the big-square side, split counts between the two rectangles, and pick the
    best total."""
    best = None
    best_total = -1.0
    rem = n - 1
    if rem < 0:
        return None
    for i in range(1, 200):
        s = i / 200.0
        if s >= 1.0:
            break
        wR = 1.0 - s   # width of right rectangle (height 1)
        hT = 1.0 - s   # height of top rectangle (width s)
        # distribute rem into kR (right) and kT = rem - kR (top)
        for kR in range(0, rem + 1):
            kT = rem - kR
            total = s
            cells = []
            if kR > 0:
                t = _tile_rect(wR, 1.0, kR)
                if t is None:
                    continue
                for (tx, ty, ts) in t:
                    cells.append((s + tx + ts / 2.0, ty + ts / 2.0, 0.0, ts))
                    total += ts
            if kT > 0:
                t = _tile_rect(s, hT, kT)
                if t is None:
                    continue
                for (tx, ty, ts) in t:
                    cells.append((tx + ts / 2.0, s + ty + ts / 2.0, 0.0, ts))
                    total += ts
            if len(cells) != rem:
                continue
            if total > best_total:
                cand = [(s / 2.0, s / 2.0, 0.0, s)] + cells
                if len(cand) == n and _rot_valid(cand):
                    best_total = total
                    best = cand
    return best


def solve(n):
    if n <= 0:
        return []
    squares = _grid_solution(n)
    best_total = sum(s[3] for s in squares)

    rng = random.Random(12345 + n)

    placed = _guillotine_search(n, best_total, rng, budget=600)
    if placed is not None:
        total = sum(p[2] for p in placed)
        if total > best_total:
            best_total = total
            squares = _seq_to_squares(placed)

    for tries in (300, 300):
        placed = _try_sequences(n, rng, tries)
        if placed is not None:
            total = sum(p[2] for p in placed)
            if total > best_total:
                best_total = total
                squares = _seq_to_squares(placed)

    # one big square in a corner + L-shaped remainder tiled by grids
    cand = _big_square_corner(n)
    if cand is not None:
        tot = sum(c[3] for c in cand)
        if tot > best_total:
            best_total = tot
            squares = cand

    # rotation-aware big-corner family
    cand = _rotated_big_corner(n)
    if cand is not None:
        tot = sum(c[3] for c in cand)
        if tot > best_total:
            best_total = tot
            squares = cand

    # local inflation refinement on current best
    try:
        refined = _inflate_local(squares, rounds=80, seed=n)
        rt = sum(c[3] for c in refined)
        if rt > best_total + 1e-9 and _rot_valid(refined):
            best_total = rt
            squares = refined
    except Exception:
        pass

    return squares[:n]
# EVOLVE-BLOCK-END
