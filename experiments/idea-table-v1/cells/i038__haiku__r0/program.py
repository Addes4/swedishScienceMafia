import math
from functools import lru_cache


def solve(n):
    """Return n squares with maximized sum of side lengths using grid-based packing with retiling."""
    
    # Base case: single square
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Find base grid size
    k = math.isqrt(n)
    base_count = k * k
    remainder = n - base_count
    
    # If perfect square, use regular grid
    if remainder == 0:
        side = 1.0 / k
        return [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                for i in range(k) for j in range(k)]
    
    # Precomputed retiling options: (delta_count, delta_sum, squares_to_add)
    # Each option describes how to retile a block and what squares result
    retile_options = {
        # 1×2 block (2 cells of side 1/k) → 3 squares
        # Replace with: two squares of side 1/(2k) stacked + one square of side 1/k
        (1, 2): [
            (1, 1.0 / (2 * k) + 1.0 / (2 * k) - 1.0 / k, 'stack_1x2')
        ],
        # 2×2 block (4 cells) → enhanced with 1x2 retile
        (2, 2): [
            (1, 1.0 / (2 * k) + 1.0 / (2 * k) - 1.0 / k, 'stack_1x2_in_2x2')
        ],
    }
    
    # Start with k×k grid
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    
    # Simple greedy retiling strategy for remainder
    # Try to split cells to add more squares
    if remainder > 0:
        # Strategy: replace some 1/k squares with smaller ones
        # For each additional square needed, split one grid cell
        
        cells_to_split = []
        for _ in range(remainder):
            if len(cells_to_split) < k * k:
                cells_to_split.append(len(cells_to_split))
        
        # Perform splits: replace cell with two half-sized squares
        removed_cells = set(cells_to_split[:remainder])
        
        new_squares = []
        cell_idx = 0
        for i in range(k):
            for j in range(k):
                if cell_idx not in removed_cells:
                    new_squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
                else:
                    # Split into two squares of side 1/(2k)
                    half_side = side / 2
                    new_squares.append(((i + 0.25) * side, (j + 0.5) * side, 0.0, half_side))
                    new_squares.append(((i + 0.75) * side, (j + 0.5) * side, 0.0, half_side))
                cell_idx += 1
        
        # Trim or pad to exactly n squares
        if len(new_squares) > n:
            new_squares = new_squares[:n]
        elif len(new_squares) < n:
            # Add zero-sized squares
            new_squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(new_squares))
        
        return new_squares
    
    return squares[:n]
