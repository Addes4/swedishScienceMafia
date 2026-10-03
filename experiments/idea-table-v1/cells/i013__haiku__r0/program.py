import math
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def solve(n):
    """Return n squares maximizing sum of side lengths using ILP on k×k grid."""
    
    best_solution = None
    best_score = 0
    
    # Try different grid sizes
    sqrt_n = math.sqrt(n)
    k_min = max(2, int(sqrt_n - 2))
    k_max = max(3, int(2 * sqrt_n) + 1)
    
    for k in range(k_min, k_max + 1):
        solution = solve_for_grid_size(n, k)
        if solution is not None:
            score = sum(s[3] for s in solution)
            if score > best_score:
                best_score = score
                best_solution = solution
    
    # Fallback to simple grid
    if best_solution is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best_solution = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                         for i in range(k) for j in range(k)]
        best_solution += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_solution))
    
    return best_solution[:n]


def solve_for_grid_size(n, k):
    """Solve using ILP for a k×k grid."""
    
    # Generate candidates: axis-aligned blocks of various sizes at valid positions
    candidates = []
    
    for block_size in range(1, k + 1):
        for start_i in range(k - block_size + 1):
            for start_j in range(k - block_size + 1):
                # Cells occupied by this block
                cells = set()
                for i in range(start_i, start_i + block_size):
                    for j in range(start_j, start_j + block_size):
                        cells.add((i, j))
                
                # Side length in unit square coordinates
                side = block_size / k
                
                # Center position
                center_i = start_i + block_size / 2
                center_j = start_j + block_size / 2
                center_x = center_i / k
                center_y = center_j / k
                
                candidates.append({
                    'cells': cells,
                    'side': side,
                    'center_x': center_x,
                    'center_y': center_y
                })
    
    if not candidates:
        return None
    
    num_candidates = len(candidates)
    num_cells = k * k
    
    # Objective: maximize sum of side lengths
    c = np.array([-cand['side'] for cand in candidates], dtype=float)
    
    # Constraint 1: each cell covered at most once
    A_cells = np.zeros((num_cells, num_candidates), dtype=float)
    cell_list = [(i, j) for i in range(k) for j in range(k)]
    cell_to_idx = {cell: idx for idx, cell in enumerate(cell_list)}
    
    for cand_idx, cand in enumerate(candidates):
        for cell in cand['cells']:
            cell_idx = cell_to_idx[cell]
            A_cells[cell_idx, cand_idx] = 1.0
    
    # Constraint 2: exactly n squares chosen
    A_count = np.ones((1, num_candidates), dtype=float)
    
    A = np.vstack([A_cells, A_count])
    
    # Cell coverage: at most 1
    # Square count: exactly n
    b_lower = np.zeros(num_cells + 1, dtype=float)
    b_upper = np.ones(num_cells + 1, dtype=float)
    b_upper[-1] = n
    b_lower[-1] = n
    
    constraints = LinearConstraint(A, b_lower, b_upper)
    bounds = Bounds(lb=np.zeros(num_candidates), ub=np.ones(num_candidates))
    
    try:
        result = milp(c=c, constraints=constraints, bounds=bounds, 
                     integrality=np.ones(num_candidates))
        
        if not result.success or result.x is None:
            return None
        
        # Extract solution
        x = result.x
        selected = [i for i in range(num_candidates) if x[i] > 0.5]
        
        if len(selected) != n:
            return None
        
        solution = []
        for idx in selected:
            cand = candidates[idx]
            solution.append((
                cand['center_x'],
                cand['center_y'],
                0.0,  # angle
                cand['side']
            ))
        
        # Pad with zero-size squares if needed
        while len(solution) < n:
            solution.append((0.5, 0.5, 0.0, 0.0))
        
        return solution[:n]
    
    except Exception:
        return None
