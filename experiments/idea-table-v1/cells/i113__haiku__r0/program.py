import math
from fractions import Fraction

def solve(n):
    """
    Pareto-front substitution DP with corner sub-squares.
    Split the unit square into one corner sub-square of side t and two rectangles
    in the L-shaped complement. Use uniform grids for each region.
    """
    
    def grid_packing(width, height, count):
        """Return Pareto front of (total_side_length, actual_count) for a w x h rectangle
        using uniform grid packing."""
        if count == 0:
            return {0: 0.0}  # {actual_count: total_side_length}
        
        best = {}
        
        # Try all possible grid configurations
        for nx in range(1, count + 1):
            for ny in range(1, count + 1):
                if nx * ny > count:
                    continue
                
                actual_count = nx * ny
                side_x = width / nx
                side_y = height / ny
                side = min(side_x, side_y)
                
                total_side = side * actual_count
                
                # Keep only Pareto-optimal solutions
                if actual_count not in best or best[actual_count] < total_side:
                    best[actual_count] = total_side
        
        return best
    
    def merge_fronts(front1, front2, max_count):
        """Merge two Pareto fronts, keeping only solutions with count <= max_count."""
        result = {}
        for c1, s1 in front1.items():
            for c2, s2 in front2.items():
                total_count = c1 + c2
                if total_count <= max_count:
                    total_side = s1 + s2
                    if total_count not in result or result[total_count] < total_side:
                        result[total_count] = total_side
        return result
    
    # Try different values of t (corner square side length)
    max_q = int(2 * math.sqrt(n) + 2) + 1
    best_solution = None
    best_total_side = -1
    
    tested_t = set()
    
    # Try rational values of t
    for q in range(1, max_q + 1):
        for p in range(q + 1):
            t = Fraction(p, q)
            if t <= 0 or t > 1:
                continue
            
            t_float = float(t)
            if t_float in tested_t:
                continue
            tested_t.add(t_float)
            
            # Split into corner square and two rectangles
            # Corner square: side = t
            # Rectangle 1 (right): width = (1-t), height = t
            # Rectangle 2 (bottom): width = 1, height = (1-t)
            
            corner_front = grid_packing(t_float, t_float, n)
            rect1_front = grid_packing(1 - t_float, t_float, n)
            rect2_front = grid_packing(1, 1 - t_float, n)
            
            # Merge fronts to find all valid combinations
            merged = merge_fronts(corner_front, rect1_front, n)
            merged = merge_fronts(merged, rect2_front, n)
            
            # Find the solution with exactly n squares
            if n in merged:
                total_side = merged[n]
                if total_side > best_total_side:
                    best_total_side = total_side
                    
                    # Reconstruct the solution
                    best_t = t_float
                    best_rect1_side = None
                    best_rect2_side = None
                    
                    # Find the best configuration
                    for c1, s1 in corner_front.items():
                        for c2, s2 in rect1_front.items():
                            if c1 + c2 in rect2_front:
                                if s1 + s2 + rect2_front[c1 + c2] == total_side:
                                    for c3, s3 in rect2_front.items():
                                        if c1 + c2 + c3 == n:
                                            best_rect1_side = (c1, s1, best_t, best_t)
                                            break
    
    # Fallback to simple grid
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    
    if best_solution is not None:
        return best_solution[:n]
    
    return squares[:n]
