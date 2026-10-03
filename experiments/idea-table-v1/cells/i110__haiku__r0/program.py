import math
from itertools import product

def solve(n):
    """Return n squares maximizing sum of side lengths using grid dissection."""
    
    def grid_dissection_sum(k, a, splits):
        """Calculate sum of side lengths for a k×k grid with corner square of side a
        and 'splits' number of cells split into 2×2."""
        total = 0.0
        
        # k×k grid of unit squares
        grid_cells = k * k
        covered_by_corner = math.ceil(a * k) ** 2 if a > 0 else 0
        remaining_cells = grid_cells - covered_by_corner
        
        # Count unit squares and split cells
        split_cells = min(splits, remaining_cells)
        unit_squares = remaining_cells - split_cells
        
        # Unit squares contribute side length 1.0 each
        total += unit_squares * 1.0
        
        # Each 2×2 split becomes 4 squares of side 0.5
        total += split_cells * 4 * 0.5
        
        # Corner square of side a contributes a
        if a > 0:
            total += a
        
        return total, unit_squares + split_cells * 4 + (1 if a > 0 else 0)
    
    def generate_configs(n):
        """Generate candidate configurations."""
        candidates = []
        
        # Try different base grid sizes
        k_min = max(1, math.isqrt(n) - 1)
        k_max = math.isqrt(n) + 3
        
        for k in range(k_min, k_max + 1):
            grid_cells = k * k
            
            # Try without corner square
            sum_val, count = grid_dissection_sum(k, 0, 0)
            if count == n:
                candidates.append((sum_val, (k, 0.0, 0)))
            
            # Try with corner squares of various sizes
            for a_num in range(1, k + 1):
                for a_den in range(1, 5):
                    a = a_num / (a_den * k)
                    if a >= 1.0:
                        break
                    
                    covered = math.ceil(a * k) ** 2
                    remaining = grid_cells - covered
                    
                    # Try different numbers of 2×2 splits
                    for splits in range(0, remaining + 1):
                        sum_val, count = grid_dissection_sum(k, a, splits)
                        if count == n:
                            candidates.append((sum_val, (k, a, splits)))
                            break
        
        return candidates
    
    def grid_placement(k, a, splits):
        """Generate actual square placements for a configuration."""
        squares = []
        side_unit = 1.0 / k
        
        # Track which cells are covered
        covered = [[False] * k for _ in range(k)]
        
        # Place corner square if present
        if a > 0:
            cx = a / 2.0
            cy = a / 2.0
            squares.append((cx, cy, 0.0, a))
            
            # Mark covered cells
            cells_covered = math.ceil(a * k)
            for i in range(cells_covered):
                for j in range(cells_covered):
                    if i < k and j < k:
                        covered[i][j] = True
        
        # Place remaining squares in grid
        split_count = 0
        for i in range(k):
            for j in range(k):
                if covered[i][j]:
                    continue
                
                cx = (i + 0.5) * side_unit
                cy = (j + 0.5) * side_unit
                
                if split_count < splits:
                    # Place 2×2 grid of smaller squares
                    small_side = side_unit / 2.0
                    for di, dj in product([0, 1], repeat=2):
                        scx = (i + (di + 0.5) / 2.0) * side_unit
                        scy = (j + (dj + 0.5) / 2.0) * side_unit
                        squares.append((scx, scy, 0.0, small_side))
                    split_count += 1
                else:
                    squares.append((cx, cy, 0.0, side_unit))
        
        # Pad with zero squares if needed
        while len(squares) < n:
            squares.append((0.5, 0.5, 0.0, 0.0))
        
        return squares[:n]
    
    # Find best configuration
    candidates = generate_configs(n)
    
    if not candidates:
        # Fallback to simple grid
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    best_sum, best_config = max(candidates, key=lambda x: x[0])
    k, a, splits = best_config
    
    return grid_placement(k, a, splits)
