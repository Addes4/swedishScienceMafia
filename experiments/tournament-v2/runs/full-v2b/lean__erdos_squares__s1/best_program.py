# EVOLVE-BLOCK-START
"""Greedy packing plus structured slicing layouts and local refinement."""
import math


def _grid_layout(n, cols):
    rows = (n + cols - 1) // cols
    side = min(1.0 / cols, 1.0 / rows)
    squares = []
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= n:
                break
            squares.append(((c + 0.5) * side, (r + 0.5) * side, 0.0, side))
            idx += 1
        if idx >= n:
            break
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares


def _best_grid(n):
    best = None
    for cols in range(1, n + 1):
        sq = _grid_layout(n, cols)
        tot = sum(s[3] for s in sq)
        if best is None or tot > best[0]:
            best = (tot, sq)
    return best


def _overlap(a, b):
    ax, ay, aa, asz = a
    bx, by, ba, bsz = b
    if asz <= 0 or bsz <= 0:
        return False
    dx = abs(ax - bx)
    dy = abs(ay - by)
    ha = asz / 2.0
    hb = bsz / 2.0
    return dx < ha + hb - 1e-12 and dy < ha + hb - 1e-12


def _inside(s):
    x, y, a, sz = s
    h = sz / 2.0
    return x - h >= -1e-9 and x + h <= 1 + 1e-9 and y - h >= -1e-9 and y + h <= 1 + 1e-9


def _valid(layout):
    for s in layout:
        if s[3] < -1e-9:
            return False
        if not _inside(s):
            return False
    for i in range(len(layout)):
        for j in range(i + 1, len(layout)):
            if _overlap(layout[i], layout[j]):
                return False
    return True


def _largest_fit(others, gridres=14):
    cands = [(0.5, 0.5)]
    for o in others:
        cands.append((o[0], o[1]))
        cands.append((o[0] + o[3] / 2.0, o[1]))
        cands.append((o[0] - o[3] / 2.0, o[1]))
        cands.append((o[0], o[1] + o[3] / 2.0))
        cands.append((o[0], o[1] - o[3] / 2.0))
        cands.append((o[0] + o[3] / 2.0, o[1] + o[3] / 2.0))
        cands.append((o[0] - o[3] / 2.0, o[1] - o[3] / 2.0))
        cands.append((o[0] + o[3] / 2.0, o[1] - o[3] / 2.0))
        cands.append((o[0] - o[3] / 2.0, o[1] + o[3] / 2.0))
    for gx in range(1, gridres):
        for gy in range(1, gridres):
            cands.append((gx / float(gridres), gy / float(gridres)))
    best = None
    for cx, cy in cands:
        lim = min(cx, 1 - cx, cy, 1 - cy)
        if lim <= 0:
            continue
        s = lim * 2.0
        for o in others:
            if o[3] <= 0:
                continue
            dx = abs(cx - o[0])
            dy = abs(cy - o[1])
            ho = o[3] / 2.0
            mx = dx - ho
            my = dy - ho
            if mx < 0 and my < 0:
                s = 0.0
                break
            allowed = max(mx, my)
            if allowed < s / 2.0:
                s = 2.0 * allowed
                if s <= 0:
                    s = 0.0
                    break
        if s > 0:
            sq = (cx, cy, 0.0, s)
            if _inside(sq):
                if best is None or s > best[3]:
                    best = sq
    if best is None:
        best = (0.5, 0.5, 0.0, 0.0)
    return best


def _refine(layout, rounds=25):
    layout = [list(s) for s in layout]
    n = len(layout)
    for _ in range(rounds):
        improved = False
        for i in range(n):
            removed = layout[i]
            others = [layout[j] for j in range(n) if j != i]
            best = _largest_fit(others)
            if best is not None and best[3] > removed[3] + 1e-9:
                layout[i] = list(best)
                improved = True
        if not improved:
            break
    return [tuple(s) for s in layout]


def _greedy_largest(n):
    layout = []
    for _ in range(n):
        sq = _largest_fit(layout)
        layout.append(list(sq))
    return [tuple(s) for s in layout]


# -------- Slicing (guillotine) layouts --------

def _rect_grid_best_squares(rw, rh, k):
    best = None
    for cols in range(1, k + 1):
        rows = (k + cols - 1) // cols
        if cols * rows < k:
            continue
        s = min(rw / cols, rh / rows)
        tot = k * s
        if best is None or tot > best[0]:
            placements = []
            idx = 0
            for r in range(rows):
                for c in range(cols):
                    if idx >= k:
                        break
                    cx = (c + 0.5) * (rw / cols)
                    cy = (r + 0.5) * (rh / rows)
                    placements.append((cx, cy, 0.0, s))
                    idx += 1
                if idx >= k:
                    break
            best = (tot, placements)
    return best


def _tile_rect(rw, rh, k, ox, oy):
    r = _rect_grid_best_squares(rw, rh, k)
    if r is None:
        return None
    tot, placements = r
    out = [(px + ox, py + oy, a, s) for (px, py, a, s) in placements]
    return tot, out


def _slicing_layouts(n, fs_steps=200):
    results = []
    fs = [i / float(fs_steps) for i in range(1, fs_steps)]

    # Vertical splits
    for k1 in range(1, n):
        k2 = n - k1
        best_for = None
        for f in fs:
            r1 = _tile_rect(f, 1.0, k1, 0.0, 0.0)
            if r1 is None:
                continue
            r2 = _tile_rect(1.0 - f, 1.0, k2, f, 0.0)
            if r2 is None:
                continue
            tot = r1[0] + r2[0]
            if best_for is None or tot > best_for[0]:
                best_for = (tot, r1[1] + r2[1])
        if best_for is not None:
            results.append(best_for[1])

    # Horizontal splits
    for k1 in range(1, n):
        k2 = n - k1
        best_for = None
        for f in fs:
            r1 = _tile_rect(1.0, f, k1, 0.0, 0.0)
            if r1 is None:
                continue
            r2 = _tile_rect(1.0, 1.0 - f, k2, 0.0, f)
            if r2 is None:
                continue
            tot = r1[0] + r2[0]
            if best_for is None or tot > best_for[0]:
                best_for = (tot, r1[1] + r2[1])
        if best_for is not None:
            results.append(best_for[1])

    # Three-rectangle: vertical split then horizontal split of one side (and vice versa)
    for ka in range(1, n - 1):
        for kb in range(1, n - ka):
            kc = n - ka - kb
            if kc < 1:
                continue
            best_for = None
            for f in fs[::4]:
                for g in fs[::4]:
                    # Left column width f split into top(ka) / bottom(kb), right(kc)
                    r1 = _tile_rect(f, g, ka, 0.0, 0.0)
                    r2 = _tile_rect(f, 1.0 - g, kb, 0.0, g)
                    r3 = _tile_rect(1.0 - f, 1.0, kc, f, 0.0)
                    if None in (r1, r2, r3):
                        continue
                    tot = r1[0] + r2[0] + r3[0]
                    if best_for is None or tot > best_for[0]:
                        best_for = (tot, r1[1] + r2[1] + r3[1])
            if best_for is not None:
                results.append(best_for[1])
    return results


def _big_plus_strip(n):
    """One big square in a corner, remaining n-1 packed by greedy largest-fit."""
    results = []
    if n < 2:
        return results
    k = n - 1
    for bi in range(1, 400):
        b = bi / 400.0
        if b >= 1.0:
            break
        layout = [(b / 2.0, b / 2.0, 0.0, b)]
        others = list(layout)
        ok = True
        for _ in range(k):
            sq = _largest_fit(others)
            if sq[3] <= 0:
                ok = False
                break
            others.append(list(sq))
        if ok and len(others) == n and _valid(others):
            results.append([tuple(s) for s in others])
    return results


def _corner_two_strips(n):
    """Big square in a corner; remaining L-shape (right strip + top strip)
    tiled by uniform grids sharing cell-size determined per configuration."""
    results = []
    if n < 2:
        return results
    k = n - 1
    bs = [i / 600.0 for i in range(1, 600)]
    for ka in range(0, k + 1):
        kb = k - ka
        if ka == 0 or kb == 0:
            continue
        best_for = None
        for b in bs:
            rw = 1.0 - b          # right strip width
            rh = 1.0              # right strip height
            tw = b                # top strip width
            th = 1.0 - b          # top strip height
            if ka > 0:
                ra = _rect_grid_best_squares(rw, rh, ka)
                if ra is None:
                    continue
            else:
                ra = (0.0, [])
            if kb > 0:
                rb = _rect_grid_best_squares(tw, th, kb)
                if rb is None:
                    continue
            else:
                rb = (0.0, [])
            tot = b + ra[0] + rb[0]
            if best_for is None or tot > best_for[0]:
                pls = [(b / 2.0, b / 2.0, 0.0, b)]
                for (px, py, a, s) in ra[1]:
                    pls.append((b + px, py, a, s))
                for (px, py, a, s) in rb[1]:
                    pls.append((px, b + py, a, s))
                best_for = (tot, pls)
        if best_for is not None:
            results.append(best_for[1])
    out = []
    for lay in results:
        out.append(lay)
        out.append([(1.0 - x, y, a, s) for (x, y, a, s) in lay])
        out.append([(x, 1.0 - y, a, s) for (x, y, a, s) in lay])
        out.append([(1.0 - x, 1.0 - y, a, s) for (x, y, a, s) in lay])
    return out


def _recursive_slice(n, depth=2, fs_steps=60):
    """Guillotine splits applied recursively: choose a cut fraction and split
    the rectangle into two sub-rectangles, each tiled by the best uniform
    grid of squares.  Explores asymmetric patterns missed by one-shot splits."""
    results = []

    def tile_fracs(lo, hi, steps):
        return [lo + (hi - lo) * i / float(steps) for i in range(1, steps)]

    # depth-1: single split, already in _slicing_layouts; here depth-2 nested.
    mid = [i / float(fs_steps) for i in range(1, fs_steps)]

    for k1 in range(1, n):
        k2 = n - k1
        for f in mid:
            # left column width f, right column width 1-f
            # left column: split into top/bottom sub-rects (ka, k1-ka)
            for ka in range(1, k1):
                kb = k1 - ka
                for g in mid:
                    r1 = _tile_rect(f, g, ka, 0.0, 0.0)
                    r2 = _tile_rect(f, 1.0 - g, kb, 0.0, g)
                    r3 = _tile_rect(1.0 - f, 1.0, k2, f, 0.0)
                    if None in (r1, r2, r3):
                        continue
                    tot = r1[0] + r2[0] + r3[0]
                    results.append((tot, r1[1] + r2[1] + r3[1]))
            # right column: split
            for ka in range(1, k2):
                kb = k2 - ka
                for g in mid:
                    r1 = _tile_rect(f, 1.0, k1, 0.0, 0.0)
                    r2 = _tile_rect(1.0 - f, g, ka, f, 0.0)
                    r3 = _tile_rect(1.0 - f, 1.0 - g, kb, f, g)
                    if None in (r1, r2, r3):
                        continue
                    tot = r1[0] + r2[0] + r3[0]
                    results.append((tot, r1[1] + r2[1] + r3[1]))

    results.sort(key=lambda t: -t[0])
    out = []
    seen = 0
    for tot, lay in results:
        out.append(lay)
        seen += 1
        if seen >= 8:
            break
    return out


def solve(n):
    if n <= 0:
        return []

    candidates = []
    candidates.append(_best_grid(n)[1])
    candidates.append(_greedy_largest(n))
    for lay in _big_plus_strip(n):
        candidates.append(lay)
    for lay in _slicing_layouts(n):
        candidates.append(lay)
    for lay in _corner_two_strips(n):
        candidates.append(lay)
    for lay in _recursive_slice(n):
        candidates.append(lay)

    # Score without expensive refinement first, keep the best few for refine.
    scored = []
    for cand in candidates:
        if len(cand) != n:
            continue
        tot = sum(s[3] for s in cand)
        scored.append((tot, cand))
    scored.sort(key=lambda t: -t[0])

    best = None
    for tot0, cand in scored[:6]:
        refined = _refine(cand)
        if not _valid(refined):
            refined = cand
        tot = sum(s[3] for s in refined)
        if best is None or tot > best[0]:
            best = (tot, refined)

    if best is None:
        # fall back to plain grid
        return _best_grid(n)[1]

    return best[1]
# EVOLVE-BLOCK-END

