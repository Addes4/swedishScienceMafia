# EVOLVE-BLOCK-START
"""Maximise sum of side lengths: shelf rows OR big-corner-square + L-strip grids."""
import math


def _gen(n, maxp):
    if n == 0:
        yield []
        return
    for p in range(min(n, maxp), 0, -1):
        for rest in _gen(n - p, p):
            yield [p] + rest


def _shelf(n):
    """Rows of equal squares (non-increasing row counts). Returns list of squares."""
    best_t = -1.0
    best_rows = None
    for part in _gen(n, n):
        rem = 1.0
        total = 0.0
        rows = []
        for c in part:
            h = 1.0 / c
            if h > rem:
                h = rem
            if h < 0.0:
                h = 0.0
            rem -= h
            total += c * h
            rows.append((c, h))
        if total > best_t:
            best_t = total
            best_rows = rows
    out = []
    y = 0.0
    for c, h in best_rows:
        for j in range(c):
            out.append(((j + 0.5) * h, y + 0.5 * h, 0.0, h))
        y += h
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]


def _corner_L(n):
    """One big square side a at bottom-left; fill right strip (width 1-a) and
    top strip (width a, height 1-a) each with a uniform grid of side b."""
    best_sq = None
    best_score = -1.0
    A = 120
    B = 120
    for ia in range(1, A):
        a = ia / A
        # right strip: cols = floor((1-a)/b), rows = floor(1/b)
        for ib in range(1, B):
            b = ib / B
            if b > a or b > 1.0 - a:
                continue
            cols_r = int((1.0 - a + 1e-9) / b)
            rows_r = int((1.0 + 1e-9) / b)
            cols_t = int((a + 1e-9) / b)
            rows_t = int((1.0 - a + 1e-9) / b)
            cap = cols_r * rows_r + cols_t * rows_t
            if cap < n - 1:
                continue
            use = n - 1
            score = a + use * b
            if score > best_score:
                best_score = score
                best_sq = (a, b, cols_r, rows_r, cols_t, rows_t, cap)
    if best_sq is None:
        return None
    a, b, cols_r, rows_r, cols_t, rows_t, cap = best_sq
    out = [(a / 2.0, a / 2.0, 0.0, a)]
    need = n - 1
    # right strip
    placed = 0
    for i in range(cols_r):
        for j in range(rows_r):
            if placed >= need:
                break
            cx = a + (i + 0.5) * b
            cy = (j + 0.5) * b
            out.append((cx, cy, 0.0, b))
            placed += 1
        if placed >= need:
            break
    # top strip
    for i in range(cols_t):
        for j in range(rows_t):
            if placed >= need:
                break
            cx = (i + 0.5) * b
            cy = a + (j + 0.5) * b
            out.append((cx, cy, 0.0, b))
            placed += 1
        if placed >= need:
            break
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    if n > 55:
        k = math.isqrt(n)
        side = 1.0 / k
        out = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
               for i in range(k) for j in range(k)]
        out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
        return out[:n]

    cands = [_shelf(n)]
    cl = _corner_L(n)
    if cl is not None:
        cands.append(cl)
    best = None
    best_s = -1.0
    for c in cands:
        s = sum(t[3] for t in c)
        if s > best_s:
            best_s = s
            best = c
    return best
# EVOLVE-BLOCK-END
