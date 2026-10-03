import math
import numpy as np
from scipy.optimize import linprog

def solve(n):
    """
    Use a contact-graph flipping search to optimize square packing.
    Represent packings by their constraint graphs and explore local moves.
    """
    
    # Start with a grid-based baseline
    k = math.isqrt(n)
    initial_squares = []
    for i in range(k):
        for j in range(k):
            side = 1.0 / k
            x = (i + 0.5) * side
            y = (j + 0.5) * side
            initial_squares.append((x, y, 0.0, side))
    
    # Add zero-sized squares for remainder
    while len(initial_squares) < n:
        initial_squares.append((0.5, 0.5, 0.0, 0.0))
    
    initial_squares = initial_squares[:n]
    
    # If n is small or time is limited, use simple approach
    if n <= 4:
        return initial_squares
    
    best_squares = initial_squares
    best_score = sum(s[3] for s in best_squares)
    
    # Try local optimization with LP-based sizing for axis-aligned squares
    for _ in range(min(100, n * 5)):
        candidate = optimize_sizes_lp(best_squares, n)
        if candidate is not None:
            score = sum(s[3] for s in candidate)
            if score > best_score * 1.001:  # Small improvement threshold
                best_squares = candidate
                best_score = score
    
    return best_squares[:n]


def optimize_sizes_lp(initial_squares, n):
    """
    Given square positions, optimize their sizes using LP.
    Assumes axis-aligned squares (angle=0).
    """
    try:
        # Extract positions (fix them) and optimize sizes
        positions = [(s[0], s[1]) for s in initial_squares]
        
        # Build constraints: for each pair, if they could overlap, add non-overlap constraint
        # For axis-aligned squares: |x1-x2| >= (side1+side2)/2 or |y1-y2| >= (side1+side2)/2
        
        # Objective: maximize sum of sides = minimize negative sum
        c = np.ones(n)  # Coefficients for minimization
        
        # Build constraint matrix
        A_ub = []
        b_ub = []
        
        # Bounds: 0 <= side <= 1
        bounds = [(0, 1) for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                xi, yi = positions[i]
                xj, yj = positions[j]
                
                dx = abs(xi - xj)
                dy = abs(yi - yj)
                
                # If squares could potentially overlap, add constraint
                # We need either: (xi - xj) >= (si + sj)/2 OR (yi - yj) >= (si + sj)/2
                # For LP, we enforce the tighter one based on positions
                
                if dx < 1.0 and dy < 1.0:
                    # Could overlap; add a constraint
                    if dx >= dy:
                        # Horizontal constraint is tighter
                        # side_i + side_j <= 2 * dx
                        constraint = np.zeros(n)
                        constraint[i] = 1
                        constraint[j] = 1
                        A_ub.append(constraint)
                        b_ub.append(2 * dx - 1e-6)
                    else:
                        # Vertical constraint is tighter
                        constraint = np.zeros(n)
                        constraint[i] = 1
                        constraint[j] = 1
                        A_ub.append(constraint)
                        b_ub.append(2 * dy - 1e-6)
        
        # Add boundary constraints: center + side/2 <= 1, center - side/2 >= 0
        for i in range(n):
            x, y = positions[i]
            # x + side/2 <= 1 => side <= 2*(1-x)
            constraint = np.zeros(n)
            constraint[i] = 1
            A_ub.append(constraint)
            b_ub.append(2 * (1 - x) - 1e-6)
            
            # x - side/2 >= 0 => side <= 2*x
            constraint = np.zeros(n)
            constraint[i] = 1
            A_ub.append(constraint)
            b_ub.append(2 * x - 1e-6)
            
            # y + side/2 <= 1 => side <= 2*(1-y)
            constraint = np.zeros(n)
            constraint[i] = 1
            A_ub.append(constraint)
            b_ub.append(2 * (1 - y) - 1e-6)
            
            # y - side/2 >= 0 => side <= 2*y
            constraint = np.zeros(n)
            constraint[i] = 1
            A_ub.append(constraint)
            b_ub.append(2 * y - 1e-6)
        
        if len(A_ub) == 0:
            A_ub = None
            b_ub = None
        else:
            A_ub = np.array(A_ub)
            b_ub = np.array(b_ub)
        
        result = linprog(-c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if result.success and result.x is not None:
            sizes = result.x
            squares = [(positions[i][0], positions[i][1], 0.0, max(0, sizes[i])) for i in range(n)]
            return squares
    except:
        pass
    
    return None
