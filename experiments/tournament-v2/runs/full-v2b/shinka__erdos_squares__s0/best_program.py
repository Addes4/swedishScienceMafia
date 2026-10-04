# EVOLVE-BLOCK-START
"""Adaptive square packer: generate multiple layout candidates and pick the best.

Structure:
  - LayoutCandidate: dataclass-like tuple holding squares and score
  - grid_layout(n): best a x b grid layout (a*b <= n), extras are zero-size
  - mixed_layout(n): one large square + grid in remaining L-shaped region
  - greedy_layout(n): greedy largest-first placement in a guillotine partition
  - evaluate(layout): sum of sides (assumes validity by construction)
  - solve(n): orchestrates candidate generation and selection
"""
import math


def _grid_layout(n):
    """Best a x b grid; side = 1/max(a,b). Use min(a*b, n) cells, extras zero-size.

    Allowing a*b >= n lets us fill only n cells of a larger grid, which is
    strictly better in many cases (e.g. n=8: use 8 of 9 cells of a 3x3 grid,
    side 1/3, total 8/3 instead of the 2x4 grid's total 2).
    """
    best = None
    best_score = -1.0
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            side = 1.0 / max(a, b)
            cnt = min(a * b, n)
            score = cnt * side
            if score > best_score:
                best_score = score
                best = (a, b, side)
    a, b, side = best
    squares = []
    for i in range(a):
        for j in range(b):
            if len(squares) >= n:
                break
            squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
        if len(squares) >= n:
            break
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares[:n]


def _nested_layout(n):
    """k x k grid of side 1/k, with an m x m corner block subdivided into an
    a x b grid of smaller squares.

    Total squares used: k*k - m*m + a*b (must be <= n; extras zero-size).
    Score = (k*k - m*m)/k + a*b * (m/k)/max(a,b).

    This captures classic optimal constructions:
      n=6:  k=3,m=2,a=1,b=1 -> 5 + 1 squares, score 7/3
      n=7:  k=2,m=1,a=2,b=2 -> 3 + 4 squares, score 5/2
      n=13: k=4,m=2,a=1,b=1 -> 12 + 1 squares, score 7/2
    """
    best = None
    best_score = -1.0
    for k in range(2, n + 2):
        for m in range(1, k):
            base_cnt = k * k - m * m
            if base_cnt > n:
                continue
            for a in range(1, n + 1):
                for b in range(1, n + 1):
                    cnt = base_cnt + a * b
                    if cnt > n:
                        continue
                    s_big = 1.0 / k
                    s_small = (m * s_big) / max(a, b)
                    score = base_cnt * s_big + a * b * s_small
                    if score > best_score:
                        best_score = score
                        squares = []
                        # The subdivided m x m block in the bottom-left corner.
                        for i in range(a):
                            for j in range(b):
                                squares.append(((i + 0.5) * s_small,
                                                (j + 0.5) * s_small,
                                                0.0, s_small))
                        # Remaining full k x k cells.
                        for i in range(k):
                            for j in range(k):
                                if i < m and j < m:
                                    continue
                                squares.append(((i + 0.5) * s_big,
                                                (j + 0.5) * s_big,
                                                0.0, s_big))
                        while len(squares) < n:
                            squares.append((0.5, 0.5, 0.0, 0.0))
                        best = squares[:n]
    if best is None:
        return _grid_layout(n)
    return best


def _mixed_layout(n):
    """One large square of side s in a corner, plus a grid filling the rest.

    Try s = 1/k for various k, then fill the L-shaped remainder with a grid.
    """
    best = None
    best_score = -1.0
    # Try placing a large square of side s in bottom-left corner
    for k in range(2, n + 1):
        s = 1.0 / k
        if k > n:
            break
        remaining = n - 1
        if remaining <= 0:
            score = s
            if score > best_score:
                best_score = score
                best = [(s / 2, s / 2, 0.0, s)] + [(0.5, 0.5, 0.0, 0.0)] * (n - 1)
            continue
        # Fill remaining region: right strip of width (1-s) x 1, and top strip of width s x (1-s)
        # Right strip: place a column of squares of side (1-s)/m
        # Top strip: place a row of squares of side (1-s)/m
        # Try m columns in right strip and p rows in top strip
        for m in range(1, remaining + 1):
            for p in range(0, remaining - m + 1):
                if m + p > remaining:
                    continue
                # right strip: m squares stacked vertically, side width (1-s)/m?
                # Actually: right strip width (1-s), height 1. m squares of side (1-s)/m stacked.
                # top strip width s, height (1-s). p squares of side s/p? No, height (1-s).
                # Use side = min((1-s)/m, s/p) if p>0 else (1-s)/m
                if p > 0:
                    side2 = min((1.0 - s) / m, s / p)
                else:
                    side2 = (1.0 - s) / m
                if side2 <= 0:
                    continue
                score = s + (m + p) * side2
                if score > best_score:
                    best_score = score
                    squares = [(s / 2, s / 2, 0.0, s)]
                    # right strip squares
                    w = (1.0 - s) / m
                    for i in range(m):
                        cx = s + (i + 0.5) * w
                        cy = (i + 0.5) * (1.0 / m) if False else (i + 0.5) * (1.0 / m)
                        cy = (i + 0.5) * (1.0 / m)
                        squares.append((cx, cy, 0.0, min(w, 1.0 / m)))
                    # top strip squares
                    if p > 0:
                        h = (1.0 - s) / p
                        for j in range(p):
                            cx = (j + 0.5) * (s / p)
                            cy = s + (j + 0.5) * h
                            squares.append((cx, cy, 0.0, min(s / p, h)))
                    while len(squares) < n:
                        squares.append((0.5, 0.5, 0.0, 0.0))
                    best = squares[:n]
    if best is None:
        return _grid_layout(n)
    return best


def _greedy_layout(n):
    """Greedy: repeatedly split the largest free rectangle and place a square."""
    # Simple guillotine: start with unit square, place squares in a binary split tree.
    # Candidate: place squares of equal size in best a x b arrangement, but try
    # also one square slightly larger than grid side in a corner.
    best = None
    best_score = -1.0
    # Try: one square of side s, remaining n-1 in grid of a x b where a*b <= n-1
    for k in range(1, n + 1):
        s = 1.0 / k
        rem = n - 1
        if rem == 0:
            score = s
            if score > best_score:
                best_score = score
                best = [(s / 2, s / 2, 0.0, s)] + [(0.5, 0.5, 0.0, 0.0)] * (n - 1)
            continue
        # remaining squares in region [0,1-s] x [0,1] (left strip) or similar
        # Use grid in strip of width (1-s): a x b with a*b <= rem, side = min((1-s)/a, 1/b)
        for a in range(1, rem + 1):
            for b in range(1, rem + 1):
                if a * b > rem:
                    continue
                side2 = min((1.0 - s) / a, 1.0 / b)
                score = s + (a * b) * side2
                if score > best_score:
                    best_score = score
                    squares = [(s / 2, s / 2, 0.0, s)]
                    for i in range(a):
                        for j in range(b):
                            cx = s + (i + 0.5) * ((1.0 - s) / a)
                            cy = (j + 0.5) * (1.0 / b)
                            squares.append((cx, cy, 0.0, side2))
                    while len(squares) < n:
                        squares.append((0.5, 0.5, 0.0, 0.0))
                    best = squares[:n]
    if best is None:
        return _grid_layout(n)
    return best


def _corner_layout(n):
    """Place a large square in one corner and pack the L-shaped remainder with
    two rectangular grids (right strip and top strip), independently sized."""
    best = None
    best_score = -1.0
    for k in range(1, n + 1):
        s = 1.0 / k
        rem = n - 1
        if rem <= 0:
            score = s
            if score > best_score:
                best_score = score
                best = [(s / 2, s / 2, 0.0, s)] + [(0.5, 0.5, 0.0, 0.0)] * (n - 1)
            continue
        # right strip: width (1-s), height 1 -> m squares of side (1-s)/m
        # top strip: width s, height (1-s) -> p squares of side (1-s)/p?
        # Actually top strip height is (1-s), so p squares in a row: side = (1-s)/p
        # But width s limits: side <= s
        for m in range(1, rem + 1):
            for p in range(0, rem - m + 1):
                if m + p > rem:
                    continue
                side_r = (1.0 - s) / m
                side_t = (1.0 - s) / p if p > 0 else 0.0
                side_t = min(side_t, s) if p > 0 else 0.0
                side_r = min(side_r, 1.0)
                if p > 0 and side_t <= 0:
                    continue
                score = s + m * side_r + p * side_t
                if score > best_score:
                    best_score = score
                    squares = [(s / 2, s / 2, 0.0, s)]
                    for i in range(m):
                        cx = s + (i + 0.5) * ((1.0 - s) / m)
                        cy = (i + 0.5) * (1.0 / m)
                        squares.append((cx, cy, 0.0, side_r))
                    if p > 0:
                        for j in range(p):
                            cx = (j + 0.5) * (s / p)
                            cy = s + (j + 0.5) * ((1.0 - s) / p)
                            squares.append((cx, cy, 0.0, side_t))
                    while len(squares) < n:
                        squares.append((0.5, 0.5, 0.0, 0.0))
                    best = squares[:n]
    if best is None:
        return _grid_layout(n)
    return best


def _score(layout):
    return sum(sq[3] for sq in layout)


def _sanitize(layout, n):
    """Clamp to [0,1] and ensure n squares."""
    out = []
    for sq in layout[:n]:
        cx, cy, ang, side = sq
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        side = max(side, 0.0)
        out.append((cx, cy, ang, side))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out


def solve(n):
    """Generate candidates, pick the best-scoring layout."""
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    candidates = [
        _grid_layout(n),
        _nested_layout(n),
        _mixed_layout(n),
        _greedy_layout(n),
        _corner_layout(n),
    ]
    best = max(candidates, key=_score)
    return _sanitize(best, n)
# EVOLVE-BLOCK-END