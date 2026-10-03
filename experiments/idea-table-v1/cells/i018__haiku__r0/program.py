"""Tilted-band approach: k×k grid with one tilted row of k+1 squares for n = k²+1."""
import math
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square."""
    
    # Special cases
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    if n == 2:
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    
    # Find k such that k² < n ≤ k² + k
    k = math.isqrt(n)
    if k * k >= n:
        k -= 1
    
    # n = k² + m, where 1 ≤ m ≤ 2k
    m = n - k * k
    
    # Standard grid solution
    base_side = 1.0 / k
    
    if m == 0:
        # Perfect square: k×k grid
        squares = []
        for i in range(k):
            for j in range(k):
                x = (i + 0.5) * base_side
                y = (j + 0.5) * base_side
                squares.append((x, y, 0.0, base_side))
        return squares
    
    if m <= k:
        # Try tilted-band approach: (k-1)×k grid + 1 tilted row with k squares
        # Or: k×(k-1) grid + 1 tilted column with k squares
        return _solve_tilted_band(n, k, m)
    else:
        # m > k: use k×k grid + m size-zero squares
        squares = []
        for i in range(k):
            for j in range(k):
                x = (i + 0.5) * base_side
                y = (j + 0.5) * base_side
                squares.append((x, y, 0.0, base_side))
        squares += [(0.5, 0.5, 0.0, 0.0)] * m
        return squares


def _solve_tilted_band(n, k, m):
    """Tilted-band optimization for n = k² + m."""
    
    # Place (k-1) × k grid + m tilted squares in a horizontal strip
    base_side = 1.0 / k
    grid_height = (k - 1) * base_side
    
    def evaluate(params):
        """params = [theta, strip_top, tilted_side]"""
        theta, strip_top, side_tilted = params
        
        if side_tilted <= 0 or side_tilted > 0.5:
            return 1e10
        if strip_top < 0 or strip_top > 1:
            return 1e10
        if strip_top + 0.1 > 1:  # rough bound
            return 1e10
        
        # Grid squares in rows 0..k-2
        grid_squares = []
        for i in range(k):
            for j in range(k - 1):
                x = (i + 0.5) * base_side
                y = (j + 0.5) * base_side
                grid_squares.append((x, y, 0.0, base_side))
        
        # Tilted row of m squares
        strip_height = side_tilted * (math.cos(2 * math.pi * theta) + math.sin(2 * math.pi * theta))
        strip_height = max(0.05, min(0.3, abs(strip_height) + side_tilted))
        
        if strip_top + strip_height > 1.0:
            return 1e10
        
        # Space m squares along the strip
        spacing = 1.0 / (m + 1) if m > 0 else 0.5
        tilted_squares = []
        for i in range(m):
            x = (i + 1) * spacing
            y = strip_top + strip_height / 2
            tilted_squares.append((x, y, theta, side_tilted))
        
        # Check feasibility with SAT
        all_squares = grid_squares + tilted_squares
        if not _check_feasible(all_squares):
            return 1e10
        
        # Objective: sum of side lengths
        total = sum(s[3] for s in all_squares)
        return -total  # minimize negative sum
    
    # Initial guess
    x0 = [0.05, grid_height + 0.01, base_side * 0.8]
    
    # Optimize
    result = minimize(evaluate, x0, method='Nelder-Mead',
                     options={'maxiter': 200, 'xatol': 1e-4, 'fatol': 1e-6})
    
    params_opt = result.x
    theta_opt, strip_top_opt, side_tilted_opt = params_opt
    
    # Build final solution
    squares = []
    for i in range(k):
        for j in range(k - 1):
            x = (i + 0.5) * base_side
            y = (j + 0.5) * base_side
            squares.append((x, y, 0.0, base_side))
    
    strip_height = side_tilted_opt * (abs(math.cos(2 * math.pi * theta_opt)) + abs(math.sin(2 * math.pi * theta_opt)))
    strip_height = max(0.05, min(0.3, strip_height + side_tilted_opt))
    spacing = 1.0 / (m + 1)
    
    for i in range(m):
        x = (i + 1) * spacing
        y = strip_top_opt + strip_height / 2
        squares.append((x, y, theta_opt, side_tilted_opt))
    
    # Pad with size-zero squares
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares[:n]


def _check_feasible(squares):
    """Check if squares don't overlap using separating axis theorem."""
    for i in range(len(squares)):
        for j in range(i + 1, len(squares)):
            if _squares_overlap(squares[i], squares[j]):
                return False
    return True


def _squares_overlap(sq1, sq2):
    """Check if two squares overlap (interiors)."""
    x1, y1, a1, s1 = sq1
    x2, y2, a2, s2 = sq2
    
    if s1 < 1e-9 or s2 < 1e-9:
        return False
    
    # Corners of sq1
    corners1 = _get_corners(x1, y1, a1, s1)
    corners2 = _get_corners(x2, y2, a2, s2)
    
    # SAT: check projections on axes
    axes = _get_axes(corners1) + _get_axes(corners2)
    
    for axis in axes:
        proj1 = [np.dot(c, axis) for c in corners1]
        proj2 = [np.dot(c, axis) for c in corners2]
        
        if max(proj1) < min(proj2) + 1e-6 or max(proj2) < min(proj1) + 1e-6:
            return False
    
    return True


def _get_corners(cx, cy, angle, side):
    """Get corners of a rotated square."""
    a = 2 * math.pi * angle
    cos_a, sin_a = math.cos(a), math.sin(a)
    half = side / 2
    
    corners = [
        (-half, -half), (half, -half), (half, half), (-half, half)
    ]
    
    rotated = [
        (c[0] * cos_a - c[1] * sin_a + cx, c[0] * sin_a + c[1] * cos_a + cy)
        for c in corners
    ]
    return [np.array(c) for c in rotated]


def _get_axes(corners):
    """Get normal axes for SAT."""
    axes = []
    for i in range(len(corners)):
        edge = np.array(corners[(i + 1) % len(corners)]) - np.array(corners[i])
        normal = np.array([-edge[1], edge[0]])
        norm = np.linalg.norm(normal)
        if norm > 1e-9:
            axes.append(normal / norm)
    return axes
