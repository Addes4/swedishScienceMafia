import math
from itertools import combinations


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    def grid_packing(N):
        """Generate k x k grid packing for N squares."""
        k = math.isqrt(N)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (N - len(squares))
        return squares[:N]
    
    def erdos_soifer_packing(N):
        """Attempt Erdős–Soifer packing: place squares in alternating pattern."""
        k = math.isqrt(N)
        if k * k == N:
            return grid_packing(N)
        
        # For non-perfect squares, use grid with some optimization
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        remaining = N - len(squares)
        
        if remaining > 0:
            # Add smaller squares in remaining space
            small_side = side / 2.0
            for idx in range(remaining):
                x = (idx % 2) * (1.0 - small_side) + small_side / 2.0
                y = (idx // 2) * (1.0 - small_side) + small_side / 2.0
                if y < 1.0:
                    squares.append((x, y, 0.0, small_side))
                else:
                    squares.append((0.5, 0.5, 0.0, 0.0))
        
        return squares[:N]
    
    def squares_overlap(sq1, sq2):
        """Check if two squares have overlapping interiors."""
        x1, y1, a1, s1 = sq1
        x2, y2, a2, s2 = sq2
        
        if s1 == 0 or s2 == 0:
            return False
        
        # Simple bounding box check for axis-aligned squares (angle=0)
        if a1 == 0 and a2 == 0:
            half1 = s1 / 2.0
            half2 = s2 / 2.0
            return (abs(x1 - x2) < half1 + half2 and 
                    abs(y1 - y2) < half1 + half2)
        
        # Conservative check for rotated squares
        dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        max_radius = (s1 + s2) / math.sqrt(2)
        return dist < max_radius
    
    def is_valid_packing(squares):
        """Check if packing has no overlapping interiors."""
        for i in range(len(squares)):
            for j in range(i + 1, len(squares)):
                if squares_overlap(squares[i], squares[j]):
                    return False
        return False in [sq[3] == 0 for sq in squares] or len(squares) > 0
    
    def is_valid_packing_strict(squares):
        """Check if packing is valid (no overlaps)."""
        for i in range(len(squares)):
            for j in range(i + 1, len(squares)):
                if squares_overlap(squares[i], squares[j]):
                    return False
        return True
    
    def sum_of_sides(squares):
        """Calculate total sum of side lengths."""
        return sum(sq[3] for sq in squares)
    
    candidates = []
    
    # Try packing for N in range [n, n + 2*sqrt(n) + 2]
    max_N = min(n + max(3, int(2 * math.sqrt(n) + 2)), n + 10)
    
    for N in range(n, max_N + 1):
        # Generate base packing
        base_squares = grid_packing(N)
        
        if not is_valid_packing_strict(base_squares):
            continue
        
        # Try deleting N - n smallest squares
        sides_with_indices = [(base_squares[i][3], i) for i in range(N)]
        sides_with_indices.sort()
        
        num_to_delete = N - n
        indices_to_keep = set(range(N))
        
        for k in range(num_to_delete):
            if k < len(sides_with_indices):
                idx_to_remove = sides_with_indices[k][1]
                indices_to_keep.discard(idx_to_remove)
        
        result = [base_squares[i] for i in sorted(indices_to_keep)]
        
        if len(result) == n and is_valid_packing_strict(result):
            candidates.append((sum_of_sides(result), result))
    
    # If no valid candidates from over-building, use simple grid
    if not candidates:
        k = math.isqrt(n)
        side = 1.0 / k
        result = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                  for i in range(k) for j in range(k)]
        result += [(0.5, 0.5, 0.0, 0.0)] * (n - len(result))
        return result[:n]
    
    # Return best candidate
    candidates.sort(reverse=True)
    return candidates[0][1]
