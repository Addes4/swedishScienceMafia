import math
from itertools import product


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    best_squares = None
    best_sum = 0
    
    # Try different rectangular grid configurations
    # a, b: dimensions of the rectangular block (in grid cells)
    # p, q: how to tile the block with p×q equal squares
    # This gives us p*q squares of side min(a/p, b/q)/k
    
    max_dim = min(20, n + 5)  # Reasonable upper bound for grid dimensions
    
    for k in range(1, int(math.sqrt(n)) + 2):
        # Try square grid k×k
        if k * k <= n:
            side = 1.0 / k
            squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                      for i in range(k) for j in range(k)]
            squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
            current_sum = sum(s[3] for s in squares)
            if current_sum > best_sum:
                best_sum = current_sum
                best_squares = squares[:]
    
    # Try rectangular configurations
    for a in range(1, max_dim):
        for b in range(1, max_dim):
            for p in range(1, a + 3):
                for q in range(1, b + 3):
                    count = p * q
                    if count > n:
                        continue
                    
                    # Side length of each small square in the p×q tiling
                    side = min(a / p, b / q) / max(a, b)
                    
                    # Offset to center the rectangle
                    rect_width = a * side / max(a, b)
                    rect_height = b * side / max(a, b)
                    offset_x = (1.0 - rect_width) / 2
                    offset_y = (1.0 - rect_height) / 2
                    
                    squares = []
                    for i in range(p):
                        for j in range(q):
                            cx = offset_x + (i + 0.5) * side
                            cy = offset_y + (j + 0.5) * side
                            squares.append((cx, cy, 0.0, side))
                    
                    # Pad with zero-size squares
                    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - count)
                    
                    current_sum = sum(s[3] for s in squares)
                    if current_sum > best_sum:
                        best_sum = current_sum
                        best_squares = squares[:]
    
    # Try some additional configurations with different aspect ratios
    for aspect in [0.5, 1.0, 2.0]:
        for total_cells in range(max(1, n - 2), n + 3):
            if total_cells > n:
                continue
            
            # Find a, b such that a*b >= total_cells and aspect ratio is close
            for a in range(1, int(math.sqrt(total_cells * 2)) + 1):
                b = (total_cells + a - 1) // a
                if a * b < total_cells or a * b > n:
                    continue
                
                # Try different p, q that tile this a×b rectangle
                for p in range(1, min(a + 2, 6)):
                    for q in range(1, min(b + 2, 6)):
                        count = p * q
                        if count > n or count < total_cells:
                            continue
                        
                        side = min(a / p, b / q) / max(a, b)
                        
                        rect_width = a * side / max(a, b)
                        rect_height = b * side / max(a, b)
                        offset_x = (1.0 - rect_width) / 2
                        offset_y = (1.0 - rect_height) / 2
                        
                        squares = []
                        for i in range(p):
                            for j in range(q):
                                cx = offset_x + (i + 0.5) * side
                                cy = offset_y + (j + 0.5) * side
                                squares.append((cx, cy, 0.0, side))
                        
                        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - count)
                        
                        current_sum = sum(s[3] for s in squares)
                        if current_sum > best_sum:
                            best_sum = current_sum
                            best_squares = squares[:]
    
    if best_squares is None:
        best_squares = [(0.5, 0.5, 0.0, 0.0)] * n
    
    return best_squares[:n]
