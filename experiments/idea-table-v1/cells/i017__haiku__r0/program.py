import math
from scipy.optimize import linprog
import numpy as np


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Initial construction: grid layout
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    squares = squares[:n]
    
    # Gap-filling post-processor
    squares = gap_filling_optimization(squares, n)
    
    return squares


def gap_filling_optimization(squares, n):
    """Apply gap-filling optimization to improve the solution."""
    squares = list(squares)
    max_iterations = 50
    
    for iteration in range(max_iterations):
        improved = False
        
        # Find free rectangles
        free_rects = compute_free_rectangles(squares)
        if not free_rects:
            break
        
        # Find the largest square that fits in any free rectangle
        best_rect = None
        best_size = 0
        best_idx = -1
        
        for idx, (cx, cy, angle, side) in enumerate(squares):
            if side < 1e-6:  # This is a padding square
                for rect in free_rects:
                    x0, y0, x1, y1 = rect
                    max_side = min(x1 - x0, y1 - y0)
                    if max_side > best_size:
                        best_size = max_side
                        best_rect = rect
                        best_idx = idx
        
        # If we found a good placement for a zero-square, use it
        if best_idx >= 0 and best_size > 1e-6:
            x0, y0, x1, y1 = best_rect
            new_side = best_size * 0.99  # Slightly smaller to avoid boundary issues
            new_cx = (x0 + x1) / 2
            new_cy = (y0 + y1) / 2
            squares[best_idx] = (new_cx, new_cy, 0.0, new_side)
            improved = True
        
        if improved:
            # Try to enlarge existing non-zero squares
            squares = enlarge_squares(squares)
        else:
            break
    
    return squares


def compute_free_rectangles(squares):
    """Compute maximal axis-aligned free rectangles using sweep line approach."""
    # Build occupancy grid
    events = []
    
    # Add boundary events
    for cx, cy, angle, side in squares:
        if side < 1e-6:
            continue
        # For axis-aligned squares, compute bounds
        half = side / 2
        x_min = max(0, cx - half)
        x_max = min(1, cx + half)
        y_min = max(0, cy - half)
        y_max = min(1, cy + half)
        events.append((x_min, 'start', y_min, y_max))
        events.append((x_max, 'end', y_min, y_max))
    
    if not events:
        return [(0, 0, 1, 1)]
    
    events.sort()
    
    rectangles = []
    active_intervals = []
    
    for x, event_type, y_min, y_max in events:
        if event_type == 'start':
            active_intervals.append((y_min, y_max))
        else:
            if (y_min, y_max) in active_intervals:
                active_intervals.remove((y_min, y_max))
    
    # Simple approach: find gaps at regular x positions
    x_positions = [0] + sorted(set([e[0] for e in events])) + [1]
    rectangles = []
    
    for i in range(len(x_positions) - 1):
        x0 = x_positions[i]
        x1 = x_positions[i + 1]
        
        # Check for free vertical gaps
        occupied_y = []
        for cx, cy, angle, side in squares:
            if side < 1e-6:
                continue
            half = side / 2
            sx_min = max(0, cx - half)
            sx_max = min(1, cx + half)
            
            if sx_min < x1 and sx_max > x0:
                sy_min = max(0, cy - half)
                sy_max = min(1, cy + half)
                occupied_y.append((sy_min, sy_max))
        
        occupied_y.sort()
        
        # Find gaps
        y_prev = 0
        for y_min, y_max in occupied_y:
            if y_prev < y_min and x0 < x1 and y_prev < y_min:
                rectangles.append((x0, y_prev, x1, y_min))
            y_prev = max(y_prev, y_max)
        
        if y_prev < 1 and x0 < x1:
            rectangles.append((x0, y_prev, x1, 1))
    
    return [(x0, y0, x1, y1) for x0, y0, x1, y1 in rectangles 
            if x1 - x0 > 1e-6 and y1 - y0 > 1e-6]


def enlarge_squares(squares):
    """Try to enlarge existing squares into adjacent free space."""
    squares = list(squares)
    
    for idx in range(len(squares)):
        cx, cy, angle, side = squares[idx]
        if side < 1e-6:
            continue
        
        # Try to enlarge slightly
        new_side = side * 1.05
        half = new_side / 2
        
        # Check if enlarged square fits
        if cx - half >= 0 and cx + half <= 1 and cy - half >= 0 and cy + half <= 1:
            # Check for overlaps
            valid = True
            for jdx in range(len(squares)):
                if jdx == idx:
                    continue
                cx2, cy2, angle2, side2 = squares[jdx]
                if side2 < 1e-6:
                    continue
                
                if squares_overlap(cx, cy, new_side, cx2, cy2, side2):
                    valid = False
                    break
            
            if valid:
                squares[idx] = (cx, cy, angle, new_side)
    
    return squares


def squares_overlap(cx1, cy1, side1, cx2, cy2, side2):
    """Check if two axis-aligned squares overlap (interiors)."""
    half1 = side1 / 2
    half2 = side2 / 2
    
    x1_min, x1_max = cx1 - half1, cx1 + half1
    y1_min, y1_max = cy1 - half1, cy1 + half1
    x2_min, x2_max = cx2 - half2, cx2 + half2
    y2_min, y2_max = cy2 - half2, cy2 + half2
    
    return x1_min < x2_max and x1_max > x2_min and y1_min < y2_max and y1_max > y2_min
