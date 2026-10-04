# EVOLVE-BLOCK-START
"""Pack n squares using grids, strips, shelf (guillotine) layouts,
corner-dominant layouts and recursive guillotine partitions with
continuous split-ratio optimisation.

For perfect squares a plain grid is optimal. For other n we exploit the
leftover space: grids of equal squares, "strip" layouts, guillotine/shelf
layouts where the unit square is recursively split into rectangles each
filled with a grid of equal squares, or corner-dominant layouts.
"""
import math


def _equal_grid(n, rows, cols):
    side = min(1.0 / cols, 1.0 / rows)
    squares = []
    for i in range(rows):
        for j in range(cols):
            squares.append(((j + 0.5) * side, (i + 0.5) * side, 0.0, side))
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares[:n], side * n


def _strip_layout(n, rows, cols):
    best = None
    best_sum = -1.0
    full_cols = cols - 1
    if full_cols < 1:
        return None, -1.0
    grid_cells = rows * full_cols
    k = n - grid_cells
    if k < 1 or k > rows:
        return _strip_layout_row(n, rows, cols)
    s = min(1.0 / full_cols, 1.0 / rows)
    strip_w = 1.0 - full_cols * s
    if strip_w <= 1e-12:
        return None, -1.0
    ss = min(strip_w, 1.0 / k)
    if ss <= 0:
        return None, -1.0
    squares = []
    for i in range(rows):
        for j in range(full_cols):
            squares.append(((j + 0.5) * s, (i + 0.5) * s, 0.0, s))
    used_h = k * ss
    y0 = (1.0 - used_h) / 2.0
    xc = full_cols * s + strip_w / 2.0
    for i in range(k):
        squares.append((xc, y0 + (i + 0.5) * ss, 0.0, ss))
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    squares = squares[:n]
    total = full_cols * rows * s + k * ss
    return squares, total


def _strip_layout_row(n, rows, cols):
    full_rows = rows - 1
    if full_rows < 1:
        return None, -1.0
    grid_cells = full_rows * cols
    k = n - grid_cells
    if k < 1 or k > cols:
        return None, -1.0
    s = min(1.0 / cols, 1.0 / full_rows)
    strip_h = 1.0 - full_rows * s
    if strip_h <= 1e-12:
        return None, -1.0
    ss = min(strip_h, 1.0 / k)
    if ss <= 0:
        return None, -1.0
    squares = []
    for i in range(full_rows):
        for j in range(cols):
            squares.append(((j + 0.5) * s, (i + 0.5) * s, 0.0, s))
    used_w = k * ss
    x0 = (1.0 - used_w) / 2.0
    yc = full_rows * s + strip_h / 2.0
    for j in range(k):
        squares.append((x0 + (j + 0.5) * ss, yc, 0.0, ss))
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    squares = squares[:n]
    total = full_rows * cols * s + k * ss
    return squares, total


def _centered_positions(k, span):
    if k <= 0:
        return []
    step = span / k
    return [(i + 0.5) * step for i in range(k)]


def _corner_layout(n, big_index):
    m = n - 1
    best = None
    best_sum = -1.0
    for kr in range(0, m + 1):
        kt = m - kr
        s = 1.0
        if kr > 0:
            s = min(s, 1.0 / (kr + 1))
        if kt > 0:
            s = min(s, 1.0 / kt)
        s = min(s, 0.5)
        t = 1.0 - s
        if kr > 0 and kr * s > t + 1e-12:
            continue
        if kt > 0 and kt * s > 1.0 + 1e-12:
            continue
        if t <= 0 or s <= 0:
            continue
        total = t + m * s
        if total > best_sum:
            squares = [(t / 2.0, t / 2.0, 0.0, t)]
            for y in _centered_positions(kr, t):
                squares.append((t + s / 2.0, y, 0.0, s))
            for j in range(kt):
                squares.append(((j + 0.5) / max(kt, 1), t + s / 2.0, 0.0, s))
            best_sum = total
            best = squares
    if best is None:
        return None, -1.0
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))
    return best[:n], best_sum


def _corner_layout_v(n, big_index):
    return _corner_layout(n, big_index)


def _shelf_layout(n, shelves):
    k = len(shelves)
    if k == 0:
        return None, -1.0
    best = None
    best_sum = -1.0
    for mask in range(1 << k):
        widths = [1.0] * k
        fixed = 0.0
        free = 0
        for i in range(k):
            if mask >> i & 1:
                widths[i] = 1.0 / shelves[i]
                fixed += widths[i]
            else:
                free += 1
        rem = 1.0 - fixed
        if rem < -1e-9:
            continue
        if free > 0:
            h = rem / free
            if h < -1e-9:
                continue
            for i in range(k):
                if not (mask >> i & 1):
                    widths[i] = h
        sizes = []
        ok = True
        for i in range(k):
            c = shelves[i]
            if c <= 0:
                ok = False
                break
            if mask >> i & 1:
                sizes.append(1.0 / c)
            else:
                if widths[i] > 1.0 / c + 1e-9:
                    ok = False
                    break
                sizes.append(widths[i])
        if not ok:
            continue
        total = sum(c * s for c, s in zip(shelves, sizes))
        if total > best_sum:
            squares = []
            y = 1.0
            for i in range(k):
                c = shelves[i]
                s = sizes[i]
                h = widths[i]
                y -= h
                yc = y + h / 2.0
                for j in range(c):
                    xc = (j + 0.5) / c
                    squares.append((xc, yc, 0.0, s))
            best_sum = total
            best = squares
    if best is None:
        return None, -1.0
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))
    return best[:n], best_sum


def _compositions(n, k):
    if k == 1:
        yield (n,)
        return
    for first in range(1, n - k + 2):
        for rest in _compositions(n - first, k - 1):
            yield (first,) + rest


def _grid_rect(rect, count):
    """Fill axis-aligned rectangle rect=(x0,y0,w,h) with a grid of `count`
    equal squares.  Returns (list_of_squares, total_side)."""
    if count <= 0:
        return [], 0.0
    x0, y0, w, h = rect
    best = None
    best_total = -1.0
    best_side = 0.0
    lim = int(math.isqrt(count)) + 2
    for r in range(1, lim + 1):
        for c in range(1, lim + 1):
            if r * c < count:
                continue
            s = min(w / c, h / r)
            total = s * count
            if total > best_total:
                best_total = total
                best_side = s
                best = (r, c)
    if best is None:
        return [], 0.0
    r, c = best
    s = best_side
    squares = []
    for i in range(r):
        for j in range(c):
            if len(squares) >= count:
                break
            squares.append((x0 + (j + 0.5) * s, y0 + (i + 0.5) * s, 0.0, s))
    return squares, best_total


def _guillotine_value(n, w, h, depth):
    """Best total side length when packing n equal-grid squares (recursively
    guillotine) into a w x h rectangle.  Returns (value, squares, rect)."""
    sq, total = _grid_rect((0.0, 0.0, w, h), n)
    if depth <= 0 or n <= 1:
        return total, sq, (0.0, 0.0, w, h)
    best_total = total
    best_sq = sq
    for k in range(1, n):
        rest = n - k
        for orient in (0, 1):
            if orient == 0:
                # vertical split, left width = w * ratio
                def val(ratio):
                    lw = w * ratio
                    rw = w - lw
                    t1, _, _ = _guillotine_value(k, lw, h, depth - 1)
                    t2, _, _ = _guillotine_value(rest, rw, h, depth - 1)
                    return t1 + t2
            else:
                def val(ratio):
                    lh = h * ratio
                    rh = h - lh
                    t1, _, _ = _guillotine_value(k, w, lh, depth - 1)
                    t2, _, _ = _guillotine_value(rest, w, rh, depth - 1)
                    return t1 + t2
            lo, hi = 0.02, 0.98
            for _ in range(40):
                m1 = lo + (hi - lo) / 3.0
                m2 = hi - (hi - lo) / 3.0
                if val(m1) < val(m2):
                    lo = m1
                else:
                    hi = m2
            ratio = (lo + hi) / 2.0
            if orient == 0:
                lw = w * ratio
                rw = w - lw
                t1, s1, _ = _guillotine_value(k, lw, h, depth - 1)
                t2, s2, _ = _guillotine_value(rest, rw, h, depth - 1)
                if t1 + t2 > best_total:
                    best_total = t1 + t2
                    shifted = [(x + lw, y, a, si) for (x, y, a, si) in s2]
                    best_sq = s1 + shifted
            else:
                lh = h * ratio
                rh = h - lh
                t1, s1, _ = _guillotine_value(k, w, lh, depth - 1)
                t2, s2, _ = _guillotine_value(rest, w, rh, depth - 1)
                if t1 + t2 > best_total:
                    best_total = t1 + t2
                    shifted = [(x, y + lh, a, si) for (x, y, a, si) in s2]
                    best_sq = s1 + shifted
    return best_total, best_sq, (0.0, 0.0, w, h)


def _guillotine(n, rect, depth):
    x0, y0, w, h = rect
    total, sq, _ = _guillotine_value(n, w, h, depth)
    shifted = [(x + x0, y + y0, a, si) for (x, y, a, si) in sq]
    return shifted, total


def solve(n):
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    best = None
    best_sum = -1.0

    limit = int(math.isqrt(n)) + 3
    for r in range(1, limit + 1):
        for c in range(1, limit + 1):
            if r * c < n:
                continue
            sq, total = _equal_grid(n, r, c)
            if total > best_sum:
                best_sum = total
                best = sq

    for r in range(1, limit + 2):
        for c in range(2, limit + 2):
            for fn in (_strip_layout, _strip_layout_row):
                sq, total = fn(n, r, c)
                if sq is not None and total > best_sum:
                    best_sum = total
                    best = sq

    for fn in (_corner_layout, _corner_layout_v):
        sq, total = fn(n, 0)
        if sq is not None and total > best_sum:
            best_sum = total
            best = sq

    max_shelves = min(n, 5)
    for k in range(1, max_shelves + 1):
        for comp in _compositions(n, k):
            sq, total = _shelf_layout(n, list(comp))
            if sq is not None and total > best_sum:
                best_sum = total
                best = sq

    # recursive guillotine partitions with continuous split optimisation
    for depth in (1, 2):
        sq, total = _guillotine(n, (0.0, 0.0, 1.0, 1.0), depth)
        if sq is not None and total > best_sum:
            best_sum = total
            best = sq

    if best is None:
        best = [(0.5, 0.5, 0.0, 0.0)] * n
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))
    return best[:n]
# EVOLVE-BLOCK-END
