"""
Rotated-insert perturbation: optimize axis-aligned grids by replacing strips
of equal squares with rotated ones to fit more squares.
"""
import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Start with axis-aligned grid
    k = math.isqrt(n)
    side = 1.0 / k
    
    # Build initial grid of k x k squares
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    
    # Pad with zero-size squares
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    squares = squares[:n]
    
    # Try perturbations: replace strips with rotated configurations
    best_sum = sum(s[3] for s in squares)
    best_squares = squares[:]
    
    # For small n, try simple optimizations
    if n <= 30:
        # Try replacing horizontal strips with rotated squares
        remaining = n - k * k
        
        if remaining > 0 and k > 0:
            # Attempt to fit remaining squares in the leftover space
            # Using rotation to pack more efficiently
            for strip_idx in range(k):
                for angle_deg in [15, 22.5, 30, 45]:
                    angle = angle_deg / 360.0
                    test_squares = best_squares[:]
                    
                    # Try adding a rotated square in remaining space
                    # Find available positions near the grid
                    for attempt_x in [side * (k + 0.5), 1.0 - side/2]:
                        for attempt_y in [side * (strip_idx + 0.5)]:
                            if 0 <= attempt_x <= 1 and 0 <= attempt_y <= 1:
                                # Calculate max side for this rotated square
                                rotated_side = compute_max_rotated_side(
                                    attempt_x, attempt_y, angle, test_squares
                                )
                                
                                if rotated_side > 1e-6:
                                    test_sum = sum(s[3] for s in test_squares) + rotated_side
                                    if test_sum > best_sum:
                                        test_squares.append((attempt_x, attempt_y, angle, rotated_side))
                                        best_sum = test_sum
                                        best_squares = test_squares[:]
    
    # Secondary optimization: local perturbations
    best_squares = local_optimize(best_squares, n)
    
    return best_squares[:n]


def compute_max_rotated_side(cx, cy, angle, existing_squares):
    """Compute maximum side length for a rotated square that doesn't overlap."""
    # Binary search for maximum side
    low, high = 0.0, 0.8
    
    for _ in range(20):  # Binary search iterations
        mid = (low + high) / 2.0
        if can_place_square(cx, cy, angle, mid, existing_squares):
            low = mid
        else:
            high = mid
    
    return low


def can_place_square(cx, cy, angle, side, existing_squares):
    """Check if a rotated square at (cx, cy) with given angle and side fits."""
    if side < 1e-9:
        return True
    
    # Get corners of rotated square
    corners = get_rotated_square_corners(cx, cy, angle, side)
    
    # Check bounds
    for x, y in corners:
        if x < 0 or x > 1 or y < 0 or y > 1:
            return False
    
    # Check overlap with existing squares
    for ex, ey, eangle, eside in existing_squares:
        if eside < 1e-9:
            continue
        if rectangles_overlap_rotated(cx, cy, angle, side, ex, ey, eangle, eside):
            return False
    
    return True


def get_rotated_square_corners(cx, cy, angle_frac, side):
    """Get corners of rotated square."""
    angle = angle_frac * 2 * math.pi
    half = side / 2.0
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    corners = []
    for dx, dy in [(-half, -half), (half, -half), (half, half), (-half, half)]:
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        corners.append((cx + rx, cy + ry))
    
    return corners


def rectangles_overlap_rotated(x1, y1, a1, s1, x2, y2, a2, s2):
    """Check if two rotated squares overlap using SAT."""
    corners1 = get_rotated_square_corners(x1, y1, a1, s1)
    corners2 = get_rotated_square_corners(x2, y2, a2, s2)
    
    # Separating Axis Theorem - check projections on axes
    all_corners = corners1 + corners2
    axes = set()
    
    for i in range(len(corners1)):
        p1 = corners1[i]
        p2 = corners1[(i + 1) % len(corners1)]
        axes.add((-(p2[1] - p1[1]), p2[0] - p1[0]))
    
    for i in range(len(corners2)):
        p1 = corners2[i]
        p2 = corners2[(i + 1) % len(corners2)]
        axes.add((-(p2[1] - p1[1]), p2[0] - p1[0]))
    
    for ax, ay in axes:
        len_sq = ax * ax + ay * ay
        if len_sq < 1e-9:
            continue
        
        proj1 = [p[0] * ax + p[1] * ay for p in corners1]
        proj2 = [p[0] * ax + p[1] * ay for p in corners2]
        
        if max(proj1) < min(proj2) - 1e-9 or max(proj2) < min(proj1) - 1e-9:
            return False
    
    return True


def local_optimize(squares, n):
    """Apply local optimizations."""
    result = squares[:n]
    return result
