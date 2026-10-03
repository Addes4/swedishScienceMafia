import math
from itertools import product


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    best_config = None
    best_sum = 0.0
    
    # Try different two-scale mixed lattice configurations
    # p: main grid size, q: subgrid size, band_rows: number of rows in subgrid band
    for p in range(1, min(n + 1, 8)):
        for q in range(1, min(n + 1, 8)):
            # Try different band configurations
            for num_band_rows in range(1, p + 1):
                # Calculate how many squares we get
                # Rows in band: num_band_rows with q columns each
                # Remaining rows: (p - num_band_rows) with 1 square each
                band_squares = num_band_rows * q
                remaining_squares = p - num_band_rows
                total_squares = band_squares + remaining_squares
                
                if total_squares < n:
                    continue
                
                # Calculate sum of side lengths
                side_p = 1.0 / p
                side_q = side_p / q
                
                # Use min(n, total_squares) squares
                squares_to_place = min(n, total_squares)
                
                # Place band squares first
                band_placed = min(squares_to_place, band_squares)
                remaining_placed = max(0, squares_to_place - band_placed)
                
                current_sum = band_placed * side_q + remaining_placed * side_p
                
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_config = (p, q, num_band_rows, band_placed, remaining_placed)
    
    # If no good config found, fall back to simple grid
    if best_config is None:
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    p, q, num_band_rows, band_placed, remaining_placed = best_config
    
    # Build the configuration
    result = []
    side_p = 1.0 / p
    side_q = side_p / q
    
    # Place squares in band (subgrid region)
    placed = 0
    for row in range(num_band_rows):
        for col in range(q):
            if placed >= band_placed:
                break
            y = (row + 0.5) * side_q
            x = (col + 0.5) * side_q
            result.append((x, y, 0.0, side_q))
            placed += 1
        if placed >= band_placed:
            break
    
    # Place remaining squares in non-band rows
    placed = 0
    for row in range(num_band_rows, p):
        if placed >= remaining_placed:
            break
        y = (row + 0.5) * side_p
        x = 0.5
        result.append((x, y, 0.0, side_p))
        placed += 1
    
    # Pad with size-zero squares if needed
    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    
    return result[:n]
