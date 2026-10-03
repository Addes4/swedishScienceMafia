import math
import sys

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return _fallback_solve(n)
    
    best_objective = 0
    best_solution = None
    
    # Try different grid resolutions
    for L in range(6, 17):
        model = cp_model.CpModel()
        
        # We'll discretize positions and sizes on an L×L grid
        # Each square position (x, y) and size s
        num_squares = min(L * L, n + 10)  # candidate pool
        
        positions_x = [model.NewIntVar(0, L - 1, f'x_{i}') for i in range(num_squares)]
        positions_y = [model.NewIntVar(0, L - 1, f'y_{i}') for i in range(num_squares)]
        sizes = [model.NewIntVar(0, L, f'size_{i}') for i in range(num_squares)]
        presence = [model.NewBoolVar(f'present_{i}') for i in range(num_squares)]
        
        # Exactly n squares must be present
        model.Add(sum(presence) == n)
        
        # Add non-overlap constraints using 2D intervals if available
        intervals_x = []
        intervals_y = []
        
        for i in range(num_squares):
            # A square at (x, y) with size s occupies [x, x+s) × [y, y+s)
            # We need to ensure squares don't overlap
            interval_x = model.NewIntervalVar(
                positions_x[i], sizes[i], 
                model.NewConstant(L),
                f'interval_x_{i}'
            )
            interval_y = model.NewIntervalVar(
                positions_y[i], sizes[i],
                model.NewConstant(L),
                f'interval_y_{i}'
            )
            intervals_x.append(interval_x)
            intervals_y.append(interval_y)
        
        # No overlaps constraint
        model.AddNoOverlap2D(intervals_x, intervals_y)
        
        # Objective: maximize sum of sizes
        total_size = sum(sizes[i] * presence[i] for i in range(num_squares))
        model.Maximize(total_size)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 8.0 / (17 - 6)
        solver.parameters.log_search_progress = False
        
        status = solver.Solve(model)
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            obj_value = solver.ObjectiveValue()
            if obj_value > best_objective:
                best_objective = obj_value
                best_solution = (solver, positions_x, positions_y, sizes, presence, L)
    
    if best_solution is not None:
        solver, positions_x, positions_y, sizes, presence, L = best_solution
        result = []
        for i in range(num_squares):
            if solver.Value(presence[i]):
                x = solver.Value(positions_x[i])
                y = solver.Value(positions_y[i])
                s = solver.Value(sizes[i])
                
                # Convert from grid to [0, 1]
                centre_x = (x + s / 2.0) / L
                centre_y = (y + s / 2.0) / L
                side = s / L
                
                result.append((centre_x, centre_y, 0.0, side))
                
                if len(result) == n:
                    break
        
        # Pad with zero-size squares if needed
        while len(result) < n:
            result.append((0.5, 0.5, 0.0, 0.0))
        
        return result[:n]
    
    return _fallback_solve(n)


def _fallback_solve(n):
    """Fallback greedy construction."""
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
