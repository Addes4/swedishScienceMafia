import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    best_sum = 0.0
    best_config = None
    
    # Try different k1 (coarse grid size)
    for k1 in range(1, min(int(math.sqrt(n)) + 3, 30)):
        total_cells = k1 * k1
        
        # Try different j (sub-grid size)
        for j in range(1, k1 + 1):
            # Try different numbers of subdivided cells (b)
            for b in range(0, total_cells + 1):
                # Count of squares: a full cells + b*j^2 subdivided cells
                subgrid_count = b * j * j
                
                # For a given b and j, we need a such that a + subgrid_count = n
                a = n - subgrid_count
                
                if a < 0:
                    continue
                
                e = total_cells - a - b
                if e < 0:
                    continue
                
                # Calculate sum of side lengths
                # Each full cell contributes 1/k1, each subdivided cell contributes 1/(k1*j)
                current_sum = (a + b * j) / k1
                
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_config = (k1, j, a, b)
    
    if best_config is None:
        # Fallback to simple grid
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    k1, j, a, b, = best_config
    
    # Build the placement
    squares = []
    cell_idx = 0
    
    # Place full cells
    for i in range(k1):
        for j_cell in range(k1):
            if cell_idx >= a:
                break
            x = (i + 0.5) / k1
            y = (j_cell + 0.5) / k1
            side = 1.0 / k1
            squares.append((x, y, 0.0, side))
            cell_idx += 1
        if cell_idx >= a:
            break
    
    # Place subdivided cells (b cells, each containing j x j subgrid)
    subdivided_placed = 0
    cell_idx = 0
    for i in range(k1):
        for j_cell in range(k1):
            if cell_idx >= a:
                if subdivided_placed >= b:
                    break
                # This cell is subdivided
                cell_x_base = i / k1
                cell_y_base = j_cell / k1
                cell_side = 1.0 / k1
                sub_side = cell_side / j
                
                for si in range(j):
                    for sj in range(j):
                        x = cell_x_base + (si + 0.5) * sub_side
                        y = cell_y_base + (sj + 0.5) * sub_side
                        squares.append((x, y, 0.0, sub_side))
                
                subdivided_placed += 1
            cell_idx += 1
        if subdivided_placed >= b:
            break
    
    return squares[:n]
