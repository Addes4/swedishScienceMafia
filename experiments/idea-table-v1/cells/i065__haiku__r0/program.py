import math
from fractions import Fraction


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    best_squares = None
    best_sum = -1.0
    
    # Try different grid configurations with sheared staircase
    # k is the number of rows/columns in the base grid
    for k in range(1, int(math.sqrt(n)) + 3):
        # Try rational deltas that make sense geometrically
        # Delta represents the horizontal shift and gap width
        for denom in range(1, k + 3):
            for numer in range(1, denom + 1):
                delta = numer / denom
                
                squares = []
                used = 0
                
                # First, place the main k×k grid with shearing
                base_side = 1.0 / k
                reduction = delta * (k - 1) / 2  # Shrink rows to fit
                
                if reduction >= base_side:
                    continue
                
                row_side = base_side - reduction
                if row_side <= 0:
                    continue
                
                for i in range(k):
                    for j in range(k):
                        if used >= n:
                            break
                        # Shift row i by i*delta horizontally
                        x = (i + 0.5) * delta + (j + 0.5) * row_side
                        y = (i + 0.5) * base_side
                        
                        # Check bounds
                        half_diag = row_side * math.sqrt(2) / 2
                        if x - half_diag < 0 or x + half_diag > 1:
                            continue
                        if y - half_diag < 0 or y + half_diag > 1:
                            continue
                        
                        squares.append((x, y, 0.0, row_side))
                        used += 1
                    if used >= n:
                        break
                
                # Fill staircase gaps on the left with smaller squares
                gap_y = base_side / 2
                for i in range(1, k):
                    if used >= n:
                        break
                    gap_width = i * delta
                    gap_size = gap_width
                    
                    # Try to fit squares of size gap_size in gap
                    if gap_size > 0:
                        x = gap_size / 2
                        y = (i + 0.5) * base_side
                        
                        if x + gap_size / 2 <= 1 and y - gap_size / 2 >= 0 and y + gap_size / 2 <= 1:
                            squares.append((x, y, 0.0, gap_size))
                            used += 1
                
                # Fill remaining with zero-sized squares
                while used < n:
                    squares.append((0.5, 0.5, 0.0, 0.0))
                    used += 1
                
                if len(squares) >= n:
                    current_sum = sum(s[3] for s in squares[:n])
                    if current_sum > best_sum:
                        best_sum = current_sum
                        best_squares = squares[:n]
    
    # Fallback to grid if nothing worked well
    if best_squares is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best_squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                       for i in range(k) for j in range(k)]
        best_squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_squares))
    
    return best_squares[:n]
