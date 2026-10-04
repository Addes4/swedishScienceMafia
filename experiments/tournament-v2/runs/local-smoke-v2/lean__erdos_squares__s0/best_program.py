# EVOLVE-BLOCK-START
"""Grid packing plus leftover squares fit into the remaining strip using a
search over several candidate strip layouts, including a rotated leftover
square for small r."""
import math


def _grid_squares(k, side, ox=0.0, oy=0.0):
    out = []
    for i in range(k):
        for j in range(k):
            out.append((ox + (i + 0.5) * side, oy + (j + 0.5) * side, 0.0, side))
    return out


def _pack_leftover(n):
    k = math.isqrt(n)
    if k == 0:
        return [(0.5, 0.5, 0.0, 0.0)] * n
    base = 1.0 / k
    squares = _grid_squares(k, base)
    r = n - k * k
    if r == 0:
        return squares

    best = squares
    best_total = k * k * base

    # 1) Column layout: grid width (1-w), extra column of r squares.
    for w_num in range(1, 40):
        w = w_num / 40.0
        if w <= 0 or w >= 1:
            continue
        grid_side = min((1.0 - w) / k, base)
        col_side = min(w, 1.0 / r)
        if col_side <= 0:
            continue
        total = k * k * grid_side + r * col_side
        if total > best_total:
            best_total = total
            sq = _grid_squares(k, grid_side)
            for t in range(r):
                cy = (t + 0.5) / r
                sq.append(((1.0 - w) + 0.5 * w, cy, 0.0, col_side))
            best = sq

    # 2) Row layout: grid height (1-h), extra row of r squares.
    for h_num in range(1, 40):
        h = h_num / 40.0
        if h <= 0 or h >= 1:
            continue
        grid_side = min((1.0 - h) / k, base)
        row_side = min(h, 1.0 / r)
        if row_side <= 0:
            continue
        total = k * k * grid_side + r * row_side
        if total > best_total:
            best_total = total
            sq = _grid_squares(k, grid_side)
            for t in range(r):
                cx = (t + 0.5) / r
                sq.append((cx, (1.0 - h) + 0.5 * h, 0.0, row_side))
            best = sq

    # 3) Block layout in the corner.
    for cols in range(1, r + 1):
        rows = (r + cols - 1) // cols
        for g_num in range(1, 60):
            g = g_num / 60.0
            if g <= 0 or g >= 1:
                continue
            grid_side = min(g / k, base)
            cellw = (1.0 - g) / cols
            cellh = 1.0 / rows
            cell_side = min(cellw, cellh)
            if cell_side <= 0:
                continue
            total = k * k * grid_side + r * cell_side
            if total > best_total:
                best_total = total
                sq = _grid_squares(k, grid_side)
                cnt = 0
                ox = g
                for i in range(cols):
                    for j in range(rows):
                        if cnt < r:
                            sq.append((ox + (i + 0.5) * cellw,
                                       (j + 0.5) * cellh, 0.0, cell_side))
                            cnt += 1
                best = sq

    # 4) Rectangle grid.
    kk = k * (k + 1)
    if n <= kk:
        cols = k + 1
        rows = (n + cols - 1) // cols
        cellw = 1.0 / cols
        cellh = 1.0 / rows
        s = min(cellw, cellh)
        sq = []
        cnt = 0
        for i in range(cols):
            for j in range(rows):
                if cnt < n:
                    sq.append(((i + 0.5) * cellw, (j + 0.5) * cellh, 0.0, s))
                    cnt += 1
        total = n * s
        if total > best_total:
            best_total = total
            best = sq

    # 5) Leftover strip with ONE rotated square. Grid shrinks to width (1-w),
    #    the strip of width w holds a single square rotated by angle a.
    #    Largest inscribed square in a w x 1 (or 1 x w) strip has side
    #    s = w / (cos a + sin a) centered, valid for any a.
    for r_single in [1]:
        if r != r_single:
            continue
        for w_num in range(1, 200):
            w = w_num / 200.0
            if w <= 0 or w >= 1:
                continue
            grid_side = min((1.0 - w) / k, base)
            # best rotation: minimize cos a + sin a -> a = 45 deg = 0.125
            a = 0.125
            side = w / (math.cos(a * 2 * math.pi) + math.sin(a * 2 * math.pi))
            # also must fit in height 1: inscribed in strip of height 1
            side = min(side, 1.0 / (math.cos(a * 2 * math.pi) + math.sin(a * 2 * math.pi)))
            total = k * k * grid_side + side
            if total > best_total:
                best_total = total
                sq = _grid_squares(k, grid_side)
                sq.append((1.0 - w / 2.0, 0.5, a, side))
                best = sq

    # 6) Leftover strip with TWO rotated/axis squares stacked or side by side.
    if r == 2:
        for w_num in range(1, 200):
            w = w_num / 200.0
            if w <= 0 or w >= 1:
                continue
            grid_side = min((1.0 - w) / k, base)
            # two squares side by side (each width w/2, height 1)
            a = 0.125
            c = math.cos(a * 2 * math.pi) + math.sin(a * 2 * math.pi)
            side = (w / 2.0) / c
            side = min(side, 1.0 / c)
            total = k * k * grid_side + 2 * side
            if total > best_total:
                best_total = total
                sq = _grid_squares(k, grid_side)
                sq.append((1.0 - w + w * 0.25, 0.5, a, side))
                sq.append((1.0 - w + w * 0.75, 0.5, a, side))
                best = sq
            # two squares stacked (each height 1/2)
            side = min(w / c, 0.5 / c)
            total = k * k * grid_side + 2 * side
            if total > best_total:
                best_total = total
                sq = _grid_squares(k, grid_side)
                sq.append((1.0 - w / 2.0, 0.25, a, side))
                sq.append((1.0 - w / 2.0, 0.75, a, side))
                best = sq

    return best


def solve(n):
    if n <= 0:
        return []
    squares = _pack_leftover(n)
    out = []
    for cx, cy, a, s in squares[:n]:
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        s = min(max(s, 0.0), 1.0)
        out.append((cx, cy, a, s))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
