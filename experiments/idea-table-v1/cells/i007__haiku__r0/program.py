import math
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square."""
    
    # Start with best constructive solution: k x k grid
    k = math.isqrt(n)
    side_grid = 1.0 / k
    squares = []
    for i in range(k):
        for j in range(k):
            squares.append(((i + 0.5) * side_grid, (j + 0.5) * side_grid, 0.0, side_grid))
    
    # Fill remaining with zero-size squares at grid positions
    remaining = n - len(squares)
    if remaining > 0:
        # Try to place small rotated squares in gaps
        gap_positions = get_gap_positions(k, side_grid, remaining)
        for x, y in gap_positions[:remaining]:
            squares.append((x, y, 0.25, 0.0))  # 45 degrees, zero initial size
        # Fill any remaining with center point
        for _ in range(n - len(squares)):
            squares.append((0.5, 0.5, 0.0, 0.0))
    
    if len(squares) > n:
        squares = squares[:n]
    
    # Optimize using penalty-based approach
    squares = optimize_squares(squares)
    
    return squares[:n]


def get_gap_positions(k, side_grid, count):
    """Get positions in gaps between grid cells for rotated squares."""
    positions = []
    shrink = 0.05  # Shrink cells slightly to create gaps
    cell_side = side_grid * (1 - shrink)
    
    for i in range(k):
        for j in range(k):
            # Gap at top-right corner of cell
            x = (i + 1) * side_grid - shrink * side_grid / 2
            y = (j + 1) * side_grid - shrink * side_grid / 2
            if x <= 1.0 and y <= 1.0:
                positions.append((min(x, 0.99), min(y, 0.99)))
            if len(positions) >= count:
                return positions
    
    # Add corner and edge positions
    for offset in np.linspace(0.1, 0.9, 5):
        positions.append((offset, 0.95))
        positions.append((0.95, offset))
        if len(positions) >= count:
            return positions
    
    return positions


def optimize_squares(initial_squares):
    """Optimize squares to maximize sum of sides using penalty-based optimization."""
    
    def penalty_overlap(sq1, sq2):
        """Compute overlap penalty between two squares using SAT."""
        x1, y1, a1, s1 = sq1
        x2, y2, a2, s2 = sq2
        
        if s1 <= 1e-6 or s2 <= 1e-6:
            return 0
        
        # Get corners for both squares
        corners1 = get_corners(x1, y1, a1, s1)
        corners2 = get_corners(x2, y2, a2, s2)
        
        # Check separation along multiple axes
        penalty = 0
        axes = get_separating_axes(corners1, corners2)
        
        for axis in axes:
            proj1 = [np.dot(c, axis) for c in corners1]
            proj2 = [np.dot(c, axis) for c in corners2]
            
            min1, max1 = min(proj1), max(proj1)
            min2, max2 = min(proj2), max(proj2)
            
            overlap = max(0, min(max1, max2) - max(min1, min2))
            penalty += overlap * overlap
        
        return penalty
    
    def containment_penalty(x, y, side):
        """Penalty for square outside unit square."""
        if side <= 1e-6:
            return 0
        
        # For axis-aligned: simple check
        # For rotated: check corners
        corners = get_corners(x, y, 0, side)
        penalty = 0
        for cx, cy in corners:
            if cx < 0:
                penalty += cx * cx
            elif cx > 1:
                penalty += (cx - 1) ** 2
            if cy < 0:
                penalty += cy * cy
            elif cy > 1:
                penalty += (cy - 1) ** 2
        return penalty
    
    def objective(x):
        """Maximize sum of sides (minimize negative sum) with penalties."""
        squares = [(x[i*4], x[i*4+1], x[i*4+2], x[i*4+3]) for i in range(len(x)//4)]
        
        # Sum of sides (we maximize this, so negate for minimization)
        total_side = sum(s for _, _, _, s in squares)
        
        # Overlap penalties
        overlap_penalty = 0
        for i in range(len(squares)):
            for j in range(i + 1, len(squares)):
                overlap_penalty += penalty_overlap(squares[i], squares[j])
        
        # Containment penalties
        contain_penalty = sum(containment_penalty(x, y, s) for x, y, _, s in squares)
        
        return -total_side + 100 * overlap_penalty + 50 * contain_penalty
    
    # Prepare initial state
    x0 = np.array([(c, y, a, s) for c, y, a, s in initial_squares]).flatten()
    
    # Bounds: all values in [0, 1]
    bounds = [(0, 1) for _ in x0]
    
    # Optimize with limited iterations due to time constraint
    result = minimize(objective, x0, method='L-BFGS-B', bounds=bounds,
                     options={'maxiter': 200, 'ftol': 1e-4})
    
    optimized = result.x
    return [(optimized[i*4], optimized[i*4+1], optimized[i*4+2], optimized[i*4+3])
            for i in range(len(optimized)//4)]


def get_corners(cx, cy, angle, side):
    """Get corners of a square given center, rotation angle, and side length."""
    theta = angle * 2 * np.pi
    cos_a = np.cos(theta)
    sin_a = np.sin(theta)
    
    half_side = side / 2
    local_corners = [
        (-half_side, -half_side),
        (half_side, -half_side),
        (half_side, half_side),
        (-half_side, half_side),
    ]
    
    corners = []
    for lx, ly in local_corners:
        rx = lx * cos_a - ly * sin_a
        ry = lx * sin_a + ly * cos_a
        corners.append((cx + rx, cy + ry))
    
    return corners


def get_separating_axes(corners1, corners2):
    """Get potential separating axes from edges of both polygons."""
    axes = []
    for corners in [corners1, corners2]:
        for i in range(len(corners)):
            p1 = corners[i]
            p2 = corners[(i + 1) % len(corners)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            # Perpendicular to edge
            axis = (-edge[1], edge[0])
            length = np.sqrt(axis[0]**2 + axis[1]**2)
            if length > 1e-6:
                axes.append((axis[0]/length, axis[1]/length))
    
    return axes
