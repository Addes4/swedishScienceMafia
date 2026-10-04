import itertools
import math

import numpy as np
from scipy.optimize import minimize, Bounds, NonlinearConstraint

def _pack_squares_in_rectangle(w, h, m, rotated=True, max_iter=3):
    """
    Pack m squares of equal side s into rectangle [0,w]x[0,h].
    Return maximal s and a configuration: list of (cx, cy, angle, s), possibly with rotation.
    angle=0 means axis-aligned, angle=0.25 means rotated 90 degrees (same as 0 effectively for square).
    """
    if m == 0:
        return 0.0, []
    if m == 1:
        s = min(w, h)
        return s, [(w / 2, h / 2, 0.0, s)]

    # Simple heuristic: find max side by checking grid placements and 45-degree rotated
    best_s = 0.0
    best_config = []

    # 1. Axis-aligned grid packing
    for rows in range(1, m + 1):
        cols = max(1, math.ceil(m / rows))
        s1 = w / cols
        s2 = h / rows
        s = min(s1, s2)
        if s > best_s:
            best_s = s
            config = []
            placed = 0
            for r in range(rows):
                if placed >= m:
                    break
                for c in range(cols):
                    if placed >= m:
                        break
                    cx = (c + 0.5) * s
                    cy = (r + 0.5) * s
                    config.append((cx, cy, 0.0, s))
                    placed += 1
            best_config = config

    # 2. 45-degree rotated packing (diamond) - works well for some m
    if rotated and m >= 2:
        # Heuristic for rotated squares in rectangle:
        # Use a rectangular packing with squares rotated 45 degrees.
        # Since square side s, bounding box dimensions: s*sqrt(2) along each axis if rotation 45 deg.
        # In a row, centers spaced by s*sqrt(2) horizontally; rows spaced by s*sqrt(2) vertically.
        # But to fit in w,h we can try different rows and cols counts.
        # The packing is like a parallelogram lattice.
        diag = math.sqrt(2.0)
        for rows in range(1, m + 1):
            cols = max(1, math.ceil(m / rows))
            # horizontal spacing = s * diag, vertical = s * diag
            s_h = w / (cols * diag)
            s_v = h / (rows * diag)
            s = min(s_h, s_v)
            # Also can stagger rows to pack tighter horizontally
            if cols > 1 and rows > 1:
                # staggered: horizontal spacing = s * diag, but alternate rows shift by s*diag/2
                # total width needed = (cols - 0.5) * s * diag
                s_h_stag = w / ((cols - 0.5) * diag)
                s = max(s, min(s_h_stag, s_v))
            if s > best_s:
                best_s = s
                config = []
                placed = 0
                for r in range(rows):
                    if placed >= m:
                        break
                    y = (r + 0.5) * s * diag
                    shift = (r % 2) * s * diag / 2
                    for c in range(cols):
                        if placed >= m:
                            break
                        x = shift + (c + 0.5) * s * diag
                        if x - s * diag / 2 >= -1e-9 and x + s * diag / 2 <= w + 1e-9 and \
                           y - s * diag / 2 >= -1e-9 and y + s * diag / 2 <= h + 1e-9:
                            config.append((x, y, 0.125, s))  # 45 deg = 0.125 full turns
                            placed += 1
                if placed == m:
                    best_config = config

    return best_s, best_config


def _pack_rectangles_given_squares(rects_with_counts):
    """
    Given a list of (w, h, count) rectangular regions, each will be filled with count equal squares.
    We need to choose side lengths for each region such that the sum of sides is maximized,
    and squares are packed inside their region independently.
    This is just the sum of optimal sides from each region.
    """
    total_side = 0.0
    all_squares = []
    for w, h, m in rects_with_counts:
        s, config = _pack_squares_in_rectangle(w, h, m)
        total_side += s * m
        all_squares.extend(config)
    return total_side, all_squares


def _best_split_into_regions(n):
    """
    Try splitting the unit square into up to 4 rectangular regions using axis-aligned cuts.
    Assign a number of squares to each region, and pack each region independently.
    Return best configuration.
    """
    unit = 1.0
    best_total_side = 0.0
    best_squares = None

    # For small n, default grid is fine; for n > 4, try decompositions.
    if n <= 4:
        s, config = _pack_squares_in_rectangle(unit, unit, n)
        return s * n, config

    # Try one region (no split)
    s, config = _pack_squares_in_rectangle(unit, unit, n)
    best_total_side = s * n
    best_squares = config

    # Try splitting with one horizontal or vertical cut: 2 regions
    for cut in np.linspace(0.1, 0.9, 9):
        # horizontal cut: bottom region h=cut, top region h=1-cut, w=1
        w = unit
        h1 = cut
        h2 = unit - cut
        for m1 in range(1, n):
            m2 = n - m1
            s1, c1 = _pack_squares_in_rectangle(w, h1, m1)
            s2, c2 = _pack_squares_in_rectangle(w, h2, m2)
            total = m1 * s1 + m2 * s2
            if total > best_total_side:
                best_total_side = total
                # shift coordinates of top region
                c2_shifted = [(x, y + h1, a, s) for (x, y, a, s) in c2]
                best_squares = c1 + c2_shifted
        # vertical cut
        w1 = cut
        w2 = unit - cut
        h = unit
        for m1 in range(1, n):
            m2 = n - m1
            s1, c1 = _pack_squares_in_rectangle(w1, h, m1)
            s2, c2 = _pack_squares_in_rectangle(w2, h, m2)
            total = m1 * s1 + m2 * s2
            if total > best_total_side:
                best_total_side = total
                c2_shifted = [(x + w1, y, a, s) for (x, y, a, s) in c2]
                best_squares = c1 + c2_shifted

    # Try 4 regions via two cuts (horizontal then vertical)
    # This forms a grid of sizes:  hcut x vcut, (1-hcut) x vcut, hcut x (1-vcut), (1-hcut) x (1-vcut)
    for hcut in np.linspace(0.2, 0.8, 5):
        for vcut in np.linspace(0.2, 0.8, 5):
            ws = [vcut, unit - vcut, vcut, unit - vcut]
            hs = [hcut, hcut, unit - hcut, unit - hcut]
            offsets_x = [0, vcut, 0, vcut]
            offsets_y = [0, 0, hcut, hcut]
            # assign numbers of squares to each region, total n
            # limit possibilities: each region at least 1 if n>=4
            # brute force over partitions of n into 4 nonnegative integers
            # But n up to maybe 50 => too large for brute force, but we can do heuristic: try proportional to area
            # Use a grid search over integer allocations around area proportional.
            # For speed, try a few discrete allocations.
            areas = [ws[i]*hs[i] for i in range(4)]
            total_area = sum(areas)
            base_counts = [max(1, int(round(n * a / total_area))) for a in areas]
            # Adjust to sum to n
            diff = n - sum(base_counts)
            # simple adjustment
            for i in range(diff):
                base_counts[i % 4] += 1
            for i in range(-diff):
                idx = 3 - (i % 4)
                if base_counts[idx] > 1:
                    base_counts[idx] -= 1
            # now base_counts sums to n. Also try variants by moving 1 square between regions.
            counts_variants = [base_counts]
            # optionally try shifting 1 from region with max count to min count
            # We'll just use base_counts; might miss optimal but okay.
            for counts in counts_variants:
                if any(c < 0 for c in counts):
                    continue
                region_squares = []
                total = 0.0
                valid = True
                for i in range(4):
                    w, h = ws[i], hs[i]
                    m = counts[i]
                    s, config = _pack_squares_in_rectangle(w, h, m)
                    if len(config) != m:
                        valid = False
                        break
                    total += m * s
                    # shift config
                    ox, oy = offsets_x[i], offsets_y[i]
                    shifted = [(x + ox, y + oy, a, s) for (x, y, a, s) in config]
                    region_squares.extend(shifted)
                if valid and total > best_total_side:
                    best_total_side = total
                    best_squares = region_squares

    return best_total_side, best_squares


def solve(n):
    """
    Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    maximizing sum of side lengths.
    """
    _, squares = _best_split_into_regions(n)
    # If not enough squares (should not happen), pad with zero-size squares.
    if len(squares) < n:
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
