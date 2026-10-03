import math
from itertools import product


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    best_squares = None
    best_sum = 0.0
    
    # Try single grid layout (baseline)
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    squares = squares[:n]
    current_sum = sum(s[3] for s in squares)
    if current_sum > best_sum:
        best_sum = current_sum
        best_squares = squares
    
    # Try two-grid layouts with vertical split
    # Enumerate splits at x = p/(p+q) where p, q are small integers
    for p in range(1, 6):
        for q in range(1, 6):
            split_x = p / (p + q)
            left_width = split_x
            right_width = 1.0 - split_x
            
            # Try different grid configurations for left and right
            for a in range(1, 6):
                for b in range(1, 6):
                    for c in range(1, 6):
                        for d in range(1, 6):
                            total_squares = a * b + c * d
                            
                            if total_squares < n:
                                continue
                            
                            # Left grid: a columns, b rows
                            left_side = min(left_width / a, 1.0 / b)
                            left_squares = []
                            for i in range(a):
                                for j in range(b):
                                    cx = (i + 0.5) * (left_width / a)
                                    cy = (j + 0.5) * (1.0 / b)
                                    left_squares.append((cx, cy, 0.0, left_side))
                            
                            # Right grid: c columns, d rows
                            right_side = min(right_width / c, 1.0 / d)
                            right_squares = []
                            for i in range(c):
                                for j in range(d):
                                    cx = split_x + (i + 0.5) * (right_width / c)
                                    cy = (j + 0.5) * (1.0 / d)
                                    right_squares.append((cx, cy, 0.0, right_side))
                            
                            all_squares = left_squares + right_squares
                            
                            # Trim to exactly n squares, keeping largest
                            if len(all_squares) > n:
                                # Sort by side length descending, keep top n
                                all_squares.sort(key=lambda s: s[3], reverse=True)
                                all_squares = all_squares[:n]
                            
                            current_sum = sum(s[3] for s in all_squares)
                            if current_sum > best_sum:
                                best_sum = current_sum
                                best_squares = all_squares[:]
                            
                            # Also try horizontal split for this configuration
                            split_y = p / (p + q)
                            top_height = split_y
                            bottom_height = 1.0 - split_y
                            
                            # Top grid: a columns, b rows
                            top_side = min(1.0 / a, top_height / b)
                            top_squares = []
                            for i in range(a):
                                for j in range(b):
                                    cx = (i + 0.5) * (1.0 / a)
                                    cy = (j + 0.5) * (top_height / b)
                                    top_squares.append((cx, cy, 0.0, top_side))
                            
                            # Bottom grid: c columns, d rows
                            bottom_side = min(1.0 / c, bottom_height / d)
                            bottom_squares = []
                            for i in range(c):
                                for j in range(d):
                                    cx = (i + 0.5) * (1.0 / c)
                                    cy = split_y + (j + 0.5) * (bottom_height / d)
                                    bottom_squares.append((cx, cy, 0.0, bottom_side))
                            
                            all_squares_h = top_squares + bottom_squares
                            
                            if len(all_squares_h) > n:
                                all_squares_h.sort(key=lambda s: s[3], reverse=True)
                                all_squares_h = all_squares_h[:n]
                            
                            current_sum_h = sum(s[3] for s in all_squares_h)
                            if current_sum_h > best_sum:
                                best_sum = current_sum_h
                                best_squares = all_squares_h[:]
    
    # Pad with zero-sized squares if needed
    while len(best_squares) < n:
        best_squares.append((0.5, 0.5, 0.0, 0.0))
    
    return best_squares[:n]
