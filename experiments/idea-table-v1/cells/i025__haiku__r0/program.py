"""
Symmetry-constrained continuous search with mirror and rotational symmetry.
Imposes symmetry to reduce variables and enable more restarts in SLSQP optimization.
"""

import math
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Return n squares maximizing sum of side lengths using symmetry-constrained optimization."""
    
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    if n == 2:
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    
    # Determine symmetry configuration
    has_center = n % 2 == 1
    num_pairs = (n - 1) // 2 if has_center else n // 2
    
    best_result = None
    best_score = -float('inf')
    
    # Multiple random restarts for global search
    num_restarts = min(40, max(10, 200 // (n + 1)))
    
    for restart in range(num_restarts):
        try:
            result = optimize_with_symmetry(n, has_center, num_pairs, restart)
            score = -result['penalty']
            
            if score > best_score:
                best_score = score
                best_result = result['squares']
        except:
            continue
    
    if best_result is None:
        # Fallback to grid
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    return best_result


def optimize_with_symmetry(n, has_center, num_pairs, seed):
    """Optimize square placement with symmetry constraints."""
    
    np.random.seed(seed)
    
    # Variables per pair: (cx, cy, angle, side)
    # If has_center: add (cx, cy, angle, side) for center square
    var_count = num_pairs * 4
    if has_center:
        var_count += 4
    
    def pack_squares(x):
        """Convert variables to square list with symmetry."""
        squares = []
        
        idx = 0
        for pair_idx in range(num_pairs):
            cx, cy, angle, side = x[idx:idx+4]
            idx += 4
            
            cx = max(0, min(1, cx))
            cy = max(0, min(1, cy))
            angle = angle % 1.0
            side = max(0, side)
            
            # Add pair with 180° rotational symmetry
            squares.append((cx, cy, angle, side))
            squares.append((1.0 - cx, 1.0 - cy, (angle + 0.5) % 1.0, side))
        
        if has_center:
            cx, cy, angle, side = x[idx:idx+4]
            cx = max(0, min(1, cx))
            cy = max(0, min(1, cy))
            angle = angle % 1.0
            side = max(0, side)
            squares.append((cx, cy, angle, side))
        
        return squares
    
    def get_corners(cx, cy, angle, side):
        """Get corners of rotated square."""
        angle_rad = angle * 2 * math.pi
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        half = side / 2.0
        
        corners = [
            (-half, -half), (half, -half),
            (half, half), (-half, half)
        ]
        
        rotated = [
            (cos_a * dx - sin_a * dy + cx, sin_a * dx + cos_a * dy + cy)
            for dx, dy in corners
        ]
        return rotated
    
    def check_overlap(sq1, sq2):
        """Check if two rotated squares overlap significantly."""
        cx1, cy1, ang1, side1 = sq1
        cx2, cy2, ang2, side2 = sq2
        
        if side1 < 1e-6 or side2 < 1e-6:
            return 0.0
        
        corners1 = get_corners(cx1, cy1, ang1, side1)
        corners2 = get_corners(cx2, cy2, ang2, side2)
        
        # Simplified overlap penalty using bounding box
        min_x1 = min(c[0] for c in corners1)
        max_x1 = max(c[0] for c in corners1)
        min_y1 = min(c[1] for c in corners1)
        max_y1 = max(c[1] for c in corners1)
        
        min_x2 = min(c[0] for c in corners2)
        max_x2 = max(c[0] for c in corners2)
        min_y2 = min(c[1] for c in corners2)
        max_y2 = max(c[1] for c in corners2)
        
        dx = min(max_x1, max_x2) - max(min_x1, min_x2)
        dy = min(max_y1, max_y2) - max(min_y1, min_y2)
        
        return max(0.0, dx * dy)
    
    def objective(x):
        """Minimize negative sum of sides minus overlap penalty."""
        squares = pack_squares(x)
        
        total_side = sum(s[3] for s in squares)
        overlap_penalty = 0.0
        
        for i in range(len(squares)):
            for j in range(i + 1, len(squares)):
                overlap = check_overlap(squares[i], squares[j])
                overlap_penalty += overlap * 1000.0
        
        # Boundary penalty
        boundary_penalty = 0.0
        for cx, cy, angle, side in squares:
            half = side / 2.0
            if cx - half < -0.01 or cx + half > 1.01:
                boundary_penalty += 100.0
            if cy - half < -0.01 or cy + half > 1.01:
                boundary_penalty += 100.0
        
        return -total_side + overlap_penalty + boundary_penalty
    
    # Initial guess
    x0 = np.random.uniform(0.0, 1.0, var_count)
    x0[3::4] = np.random.uniform(0.1, 0.3, len(x0[3::4]))  # initial sides
    
    result = minimize(objective, x0, method='SLSQP', 
                     options={'maxiter': 500, 'ftol': 1e-8})
    
    squares = pack_squares(result.x)
    
    return {
        'squares': squares,
        'penalty': result.fun
    }
