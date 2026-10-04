import math
import numpy as np
from scipy.optimize import linprog

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Start with grid baseline
    k = math.isqrt(n)
    side = 1.0 / k
    
    # Initial grid configuration
    squares = []
    grid_positions = []
    for i in range(k):
        for j in range(k):
            x = (i + 0.5) * side
            y = (j + 0.5) * side
            squares.append((x, y, 0.0, side))
            grid_positions.append((i, j))
    
    # Pad with zero-size squares
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
        grid_positions.append(None)
    
    squares = squares[:n]
    grid_positions = grid_positions[:n]
    
    # Try to optimize with LP if we have a grid
    if k > 0 and k * k <= n:
        result = optimize_grid_lp(k, n, grid_positions)
        if result is not None:
            return result
    
    return squares

def optimize_grid_lp(k, n, grid_positions):
    """Use LP to optimize grid-based topology."""
    try:
        # Variables: x[i], y[i], s[i] for each square i (position and side)
        # Only optimize the first k*k squares that form the grid
        num_grid = k * k
        if num_grid > n:
            return None
        
        num_vars = num_grid * 3  # x, y, s for each grid square
        
        # Objective: maximize sum of sides = minimize negative sum
        c = np.zeros(num_vars)
        for i in range(num_grid):
            c[num_grid * 2 + i] = -1.0  # Negative because linprog minimizes
        
        # Constraints
        constraints_A = []
        constraints_b = []
        bounds = []
        
        # Bounds for each variable
        for i in range(num_grid):
            # x in [0, 1]
            bounds.append((0, 1))
            # y in [0, 1]
            bounds.append((0, 1))
            # s in [0, 1]
            bounds.append((0, 1))
        
        # Extract grid topology: which squares are neighbors
        # For a k x k grid: square at (i,j) has index i*k + j
        for idx in range(num_grid):
            i = idx // k
            j = idx % k
            
            # Containment: x - s/2 >= 0 and x + s/2 <= 1
            constraint = np.zeros(num_vars)
            constraint[idx * 3] = 1
            constraint[idx * 3 + 2] = -0.5
            constraints_A.append(constraint)
            constraints_b.append(0)
            
            constraint = np.zeros(num_vars)
            constraint[idx * 3] = -1
            constraint[idx * 3 + 2] = -0.5
            constraints_A.append(constraint)
            constraints_b.append(-1)
            
            constraint = np.zeros(num_vars)
            constraint[idx * 3 + 1] = 1
            constraint[idx * 3 + 2] = -0.5
            constraints_A.append(constraint)
            constraints_b.append(0)
            
            constraint = np.zeros(num_vars)
            constraint[idx * 3 + 1] = -1
            constraint[idx * 3 + 2] = -0.5
            constraints_A.append(constraint)
            constraints_b.append(-1)
            
            # Contact constraints with neighbors
            # Right neighbor
            if j + 1 < k:
                next_idx = i * k + (j + 1)
                constraint = np.zeros(num_vars)
                constraint[idx * 3] = 1
                constraint[idx * 3 + 2] = 0.5
                constraint[next_idx * 3] = -1
                constraint[next_idx * 3 + 2] = -0.5
                constraints_A.append(constraint)
                constraints_b.append(0)
            
            # Top neighbor
            if i + 1 < k:
                next_idx = (i + 1) * k + j
                constraint = np.zeros(num_vars)
                constraint[idx * 3 + 1] = 1
                constraint[idx * 3 + 2] = 0.5
                constraint[next_idx * 3 + 1] = -1
                constraint[next_idx * 3 + 2] = -0.5
                constraints_A.append(constraint)
                constraints_b.append(0)
        
        if constraints_A:
            A_ub = np.array(constraints_A)
            b_ub = np.array(constraints_b)
            
            result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs', 
                           options={'maxiter': 1000})
            
            if result.success and result.fun < -2.0:  # Better than grid baseline
                squares = []
                for i in range(num_grid):
                    x = result.x[i * 3]
                    y = result.x[i * 3 + 1]
                    s = result.x[i * 3 + 2]
                    squares.append((x, y, 0.0, s))
                
                # Add padding
                for i in range(num_grid, n):
                    squares.append((0.5, 0.5, 0.0, 0.0))
                
                return squares
    except:
        pass
    
    return None
