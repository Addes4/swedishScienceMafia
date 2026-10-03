import math
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # For n <= 4, use MILP optimization
    if n <= 4:
        return solve_milp(n)
    
    # For larger n, use grid-based construction
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def solve_milp(n):
    """Solve the packing problem using MILP for small n."""
    
    # Warm start from grid solution
    k = math.isqrt(n)
    side_init = 1.0 / k
    x_init = []
    y_init = []
    s_init = []
    
    for i in range(k):
        for j in range(k):
            x_init.append((i + 0.5) * side_init)
            y_init.append((j + 0.5) * side_init)
            s_init.append(side_init)
    
    # Pad with zeros
    while len(x_init) < n:
        x_init.append(0.5)
        y_init.append(0.5)
        s_init.append(0.0)
    
    # Variables: x_i, y_i, s_i for each square (3n continuous)
    # Plus separation indicators: b_ij_d for each pair i<j and direction d in {L,R,B,T} (6*n*(n-1) binary)
    
    num_continuous = 3 * n
    num_pairs = n * (n - 1) // 2
    num_binary = 4 * num_pairs
    
    # Objective: maximize sum of sides
    c = np.zeros(num_continuous + num_binary)
    c[:3*n:3] = 0  # x coefficients
    c[1:3*n:3] = 0  # y coefficients
    c[2:3*n:3] = -1  # s coefficients (negative for maximization)
    
    # Bounds
    bounds = Bounds(
        lb=np.concatenate([np.zeros(num_continuous), np.zeros(num_binary)]),
        ub=np.concatenate([np.ones(num_continuous), np.ones(num_binary)])
    )
    
    # Constraints
    A_rows = []
    A_cols = []
    A_data = []
    A_lb = []
    A_ub = []
    
    M = 2.0  # Big M value
    
    pair_idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            # b_ij_L + b_ij_R + b_ij_B + b_ij_T >= 1 (at least one separation)
            row_idx = len(A_lb)
            for d in range(4):
                A_rows.append(row_idx)
                A_cols.append(num_continuous + pair_idx * 4 + d)
                A_data.append(1.0)
            A_lb.append(1.0)
            A_ub.append(4.0)
            
            # Separation constraints with big M
            s_i_idx = 2 + i * 3
            s_j_idx = 2 + j * 3
            x_i_idx = i * 3
            x_j_idx = j * 3
            y_i_idx = 1 + i * 3
            y_j_idx = 1 + j * 3
            
            # Left: x_i + s_i/2 <= x_j - s_j/2 OR b_L = 0
            # x_i - x_j + s_i/2 + s_j/2 <= M*(1 - b_L)
            row_idx = len(A_lb)
            A_rows.extend([row_idx, row_idx, row_idx, row_idx])
            A_cols.extend([x_i_idx, x_j_idx, s_i_idx, s_j_idx])
            A_data.extend([1.0, -1.0, 0.5, 0.5])
            A_rows.append(row_idx)
            A_cols.append(num_continuous + pair_idx * 4 + 0)
            A_data.append(M)
            A_lb.append(-np.inf)
            A_ub.append(M)
            
            # Right: x_j + s_j/2 <= x_i - s_i/2 OR b_R = 0
            # x_j - x_i + s_j/2 + s_i/2 <= M*(1 - b_R)
            row_idx = len(A_lb)
            A_rows.extend([row_idx, row_idx, row_idx, row_idx])
            A_cols.extend([x_j_idx, x_i_idx, s_j_idx, s_i_idx])
            A_data.extend([1.0, -1.0, 0.5, 0.5])
            A_rows.append(row_idx)
            A_cols.append(num_continuous + pair_idx * 4 + 1)
            A_data.append(M)
            A_lb.append(-np.inf)
            A_ub.append(M)
            
            # Below: y_i + s_i/2 <= y_j - s_j/2 OR b_B = 0
            row_idx = len(A_lb)
            A_rows.extend([row_idx, row_idx, row_idx, row_idx])
            A_cols.extend([y_i_idx, y_j_idx, s_i_idx, s_j_idx])
            A_data.extend([1.0, -1.0, 0.5, 0.5])
            A_rows.append(row_idx)
            A_cols.append(num_continuous + pair_idx * 4 + 2)
            A_data.append(M)
            A_lb.append(-np.inf)
            A_ub.append(M)
            
            # Top: y_j + s_j/2 <= y_i - s_i/2 OR b_T = 0
            row_idx = len(A_lb)
            A_rows.extend([row_idx, row_idx, row_idx, row_idx])
            A_cols.extend([y_j_idx, y_i_idx, s_j_idx, s_i_idx])
            A_data.extend([1.0, -1.0, 0.5, 0.5])
            A_rows.append(row_idx)
            A_cols.append(num_continuous + pair_idx * 4 + 3)
            A_data.append(M)
            A_lb.append(-np.inf)
            A_ub.append(M)
            
            pair_idx += 1
    
    # Bounds constraints for squares within unit square
    for i in range(n):
        x_idx = i * 3
        y_idx = 1 + i * 3
        s_idx = 2 + i * 3
        
        # x - s/2 >= 0
        row_idx = len(A_lb)
        A_rows.extend([row_idx, row_idx])
        A_cols.extend([x_idx, s_idx])
        A_data.extend([1.0, -0.5])
        A_lb.append(0.0)
        A_ub.append(np.inf)
        
        # x + s/2 <= 1
        row_idx = len(A_lb)
        A_rows.extend([row_idx, row_idx])
        A_cols.extend([x_idx, s_idx])
        A_data.extend([1.0, 0.5])
        A_lb.append(-np.inf)
        A_ub.append(1.0)
        
        # y - s/2 >= 0
        row_idx = len(A_lb)
        A_rows.extend([row_idx, row_idx])
        A_cols.extend([y_idx, s_idx])
        A_data.append([1.0, -0.5])
        A_lb.append(0.0)
        A_ub.append(np.inf)
        
        # y + s/2 <= 1
        row_idx = len(A_lb)
        A_rows.extend([row_idx, row_idx])
        A_cols.extend([y_idx, s_idx])
        A_data.extend([1.0, 0.5])
        A_lb.append(-np.inf)
        A_ub.append(1.0)
    
    A_sparse = (np.array(A_data), (np.array(A_rows), np.array(A_cols)))
    constraint = LinearConstraint(A_sparse, np.array(A_lb), np.array(A_ub))
    
    # Initial solution
    x0 = np.concatenate([x_init, y_init, s_init, np.zeros(num_binary)])
    
    # Solve
    result = milp(c=c, constraints=constraint, bounds=bounds, integrality=np.concatenate([np.zeros(num_continuous), np.ones(num_binary)]),
                  options={'time_limit': 55})
    
    sol = result.x if result.success else x0
    
    # Extract solution
    squares = []
    for i in range(n):
        x = sol[i * 3]
        y = sol[1 + i * 3]
        s = sol[2 + i * 3]
        squares.append((x, y, 0.0, max(0, s)))
    
    return squares
