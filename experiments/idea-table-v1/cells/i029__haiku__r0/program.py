import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    best_squares = None
    best_sum = -1
    
    # Try all combinations of nested grid configurations
    # Level 1: k×k grid with side length 1/k
    # Level 2: within one of those cells, place m×m or (m±1)×(m±1) grid
    
    for k in range(1, int(math.sqrt(n)) + 2):
        side_k = 1.0 / k
        
        # Try not replacing any cell (just k×k grid)
        if k * k <= n:
            squares = []
            for i in range(k):
                for j in range(k):
                    squares.append(((i + 0.5) * side_k, (j + 0.5) * side_k, 0.0, side_k))
            
            if len(squares) == n:
                s = sum(sq[3] for sq in squares)
                if s > best_sum:
                    best_sum = s
                    best_squares = squares
            
            # Fill remaining with zero-area squares
            if len(squares) < n:
                squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
                s = sum(sq[3] for sq in squares)
                if s > best_sum:
                    best_sum = s
                    best_squares = squares[:n]
        
        # Try replacing one cell with m×m or (m±1)×(m±1) grid
        if k * k > 0:
            for m in range(1, k + 1):
                side_m = side_k / m
                
                for m2 in range(max(1, m - 1), m + 2):
                    side_m2 = side_k / m2
                    
                    # Count: k² - 1 cells of size side_k + m2² cells of size side_m2
                    count = k * k - 1 + m2 * m2
                    
                    if count == n:
                        squares = []
                        
                        # Add k×k grid minus one cell
                        cell_idx = 0
                        for i in range(k):
                            for j in range(k):
                                if cell_idx == 0:
                                    # Replace this cell with m2×m2 grid
                                    base_x = (i + 0.5) * side_k
                                    base_y = (j + 0.5) * side_k
                                    for mi in range(m2):
                                        for mj in range(m2):
                                            x = base_x + (mi + 0.5 - m2 / 2.0) * side_m2
                                            y = base_y + (mj + 0.5 - m2 / 2.0) * side_m2
                                            x = max(0.0, min(1.0, x))
                                            y = max(0.0, min(1.0, y))
                                            squares.append((x, y, 0.0, side_m2))
                                else:
                                    # Regular cell
                                    squares.append(((i + 0.5) * side_k, (j + 0.5) * side_k, 0.0, side_k))
                                cell_idx += 1
                        
                        s = sum(sq[3] for sq in squares)
                        if s > best_sum:
                            best_sum = s
                            best_squares = squares
    
    # Fallback to simple grid if nothing found
    if best_squares is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best_squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        best_squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_squares))
    
    return best_squares[:n]
