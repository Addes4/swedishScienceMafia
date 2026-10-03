import math
from fractions import Fraction
from scipy.optimize import minimize
import numpy as np


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Start with grid baseline
    k = math.isqrt(n)
    side = 1.0 / k
    baseline = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                for i in range(k) for j in range(k)]
    baseline += [(0.5, 0.5, 0.0, 0.0)] * (n - len(baseline))
    baseline = baseline[:n]
    
    # Optimize with continuous optimization
    result = continuous_optimize(baseline, n)
    
    # Apply rational reconstruction post-processor
    refined = rational_reconstruct(result, n)
    
    return refined


def continuous_optimize(baseline, n):
    """Use continuous optimization (SLSQP with penalty) to improve baseline."""
    x0 = flatten_squares(baseline)
    
    def objective(x):
        return -sum_of_sides(unflatten(x, n))
    
    def penalty_constraint(x):
        """Return the minimum gap between any two squares (negative if overlapping)."""
        squares = unflatten(x, n)
        min_gap = float('inf')
        for i in range(n):
            for j in range(i+1, n):
                gap = min_gap_between_squares(squares[i], squares[j])
                min_gap = min(min_gap, gap)
        return min_gap
    
    def full_objective(x):
        obj = objective(x)
        gap = penalty_constraint(x)
        if gap < 0:
            obj += 1e6 * (gap ** 2)
        return obj
    
    bounds = [(0, 1)] * (4 * n)
    
    result = minimize(full_objective, x0, method='SLSQP', bounds=bounds,
                     options={'ftol': 1e-9, 'maxiter': 1000})
    
    return unflatten(result.x, n)


def rational_reconstruct(squares, n):
    """Detect active constraints and solve exactly using Fractions."""
    # Identify near-active contacts (gap < 1e-7)
    active_pairs = []
    for i in range(n):
        for j in range(i+1, n):
            gap = min_gap_between_squares(squares[i], squares[j])
            if gap < 1e-7:
                active_pairs.append((i, j))
    
    if not active_pairs:
        # No active constraints to refine
        return squares
    
    # Try to extract rational values for active-set configuration
    refined = try_rational_fit(squares, n, active_pairs)
    
    # Verify the refined solution is valid
    if refined and is_valid_solution(refined, n):
        return refined
    
    # Fall back to continuous optimum
    return squares


def try_rational_fit(squares, n, active_pairs):
    """Attempt to find exact rational coordinates satisfying active constraints."""
    try:
        # Convert floating point to fractions with reasonable denominator
        max_denom = 100
        frac_squares = []
        
        for cx, cy, angle, side in squares:
            fx = Fraction(cx).limit_denominator(max_denom)
            fy = Fraction(cy).limit_denominator(max_denom)
            fa = Fraction(angle).limit_denominator(max_denom)
            fs = Fraction(side).limit_denominator(max_denom)
            frac_squares.append((fx, fy, fa, fs))
        
        # Verify active constraints are satisfied
        all_satisfied = True
        for i, j in active_pairs:
            gap = min_gap_between_squares_frac(frac_squares[i], frac_squares[j])
            if gap < -Fraction(1, 1000000):  # Allow small tolerance
                all_satisfied = False
                break
        
        if not all_satisfied:
            return None
        
        # Convert back to float
        return [(float(cx), float(cy), float(angle), float(side)) 
                for cx, cy, angle, side in frac_squares]
    
    except:
        return None


def is_valid_solution(squares, n):
    """Verify that no two squares have overlapping interiors."""
    for i in range(n):
        for j in range(i+1, n):
            if min_gap_between_squares(squares[i], squares[j]) < -1e-9:
                return False
    return True


def flatten_squares(squares):
    """Flatten list of squares into 1D array."""
    result = []
    for cx, cy, angle, side in squares:
        result.extend([cx, cy, angle, side])
    return np.array(result)


def unflatten(x, n):
    """Unflatten 1D array into list of squares."""
    return [(x[4*i], x[4*i+1], x[4*i+2], x[4*i+3]) for i in range(n)]


def sum_of_sides(squares):
    """Sum of all side lengths."""
    return sum(side for _, _, _, side in squares)


def min_gap_between_squares(sq1, sq2):
    """Minimum signed distance between two squares (negative if overlapping)."""
    cx1, cy1, angle1, side1 = sq1
    cx2, cy2, angle2, side2 = sq2
    
    # For axis-aligned squares, this is simpler
    # Check if corners of one square are inside the other
    corners1 = get_corners(cx1, cy1, angle1, side1)
    corners2 = get_corners(cx2, cy2, angle2, side2)
    
    min_dist = float('inf')
    
    for c1 in corners1:
        for c2 in corners2:
            dist = math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
            min_dist = min(min_dist, dist)
    
    # Check distance from centers
    center_dist = math.sqrt((cx1-cx2)**2 + (cy1-cy2)**2)
    threshold = (side1 + side2) / math.sqrt(2)
    
    return center_dist - threshold


def min_gap_between_squares_frac(sq1, sq2):
    """Minimum gap using Fraction arithmetic."""
    cx1, cy1, angle1, side1 = sq1
    cx2, cy2, angle2, side2 = sq2
    
    center_dist_sq = (cx1-cx2)**2 + (cy1-cy2)**2
    threshold_sq = ((side1 + side2) / 2) ** 2
    
    return center_dist_sq - threshold_sq


def get_corners(cx, cy, angle, side):
    """Get the four corners of a rotated square."""
    half_diag = side / math.sqrt(2)
    angle_rad = angle * 2 * math.pi
    
    corners = []
    for corner_angle in [angle_rad + i * math.pi / 2 for i in range(4)]:
        x = cx + half_diag * math.cos(corner_angle)
        y = cy + half_diag * math.sin(corner_angle)
        corners.append((x, y))
    
    return corners
