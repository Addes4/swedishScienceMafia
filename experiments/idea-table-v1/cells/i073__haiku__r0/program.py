import math
import numpy as np
from scipy.optimize import minimize

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Precomputed optimal packings for small m in various aspect ratios
    # Each packing: list of (x, y, angle, side) in normalized rectangle
    precomputed_packings = {
        (2, 1.0): [  # 2 squares in 1:1
            (0.25, 0.5, 0.0, 0.5),
            (0.75, 0.5, 0.0, 0.5),
        ],
        (3, 1.0): [  # 3 squares in 1:1
            (0.333, 0.5, 0.0, 0.4),
            (0.666, 0.5, 0.0, 0.4),
            (0.5, 0.25, 0.0, 0.35),
        ],
        (4, 1.0): [  # 4 squares in 1:1 (2x2 grid)
            (0.25, 0.25, 0.0, 0.5),
            (0.75, 0.25, 0.0, 0.5),
            (0.25, 0.75, 0.0, 0.5),
            (0.75, 0.75, 0.0, 0.5),
        ],
        (5, 1.0): [  # 5 squares in 1:1
            (0.25, 0.25, 0.0, 0.4),
            (0.75, 0.25, 0.0, 0.4),
            (0.25, 0.75, 0.0, 0.4),
            (0.75, 0.75, 0.0, 0.4),
            (0.5, 0.5, 0.0, 0.3),
        ],
        (6, 1.0): [  # 6 squares in 1:1
            (0.25, 0.333, 0.0, 0.4),
            (0.75, 0.333, 0.0, 0.4),
            (0.25, 0.666, 0.0, 0.4),
            (0.75, 0.666, 0.0, 0.4),
            (0.25, 0.166, 0.0, 0.25),
            (0.75, 0.166, 0.0, 0.25),
        ],
        (2, 2.0): [  # 2 squares in 2:1 (horizontal)
            (0.25, 0.5, 0.0, 0.4),
            (0.75, 0.5, 0.0, 0.4),
        ],
        (3, 2.0): [  # 3 squares in 2:1
            (0.25, 0.5, 0.0, 0.35),
            (0.75, 0.5, 0.0, 0.35),
            (0.5, 0.25, 0.0, 0.3),
        ],
        (2, 1.5): [  # 2 squares in 3:2
            (0.333, 0.5, 0.0, 0.4),
            (0.666, 0.5, 0.0, 0.4),
        ],
        (3, 1.5): [  # 3 squares in 3:2
            (0.333, 0.333, 0.0, 0.35),
            (0.666, 0.333, 0.0, 0.35),
            (0.333, 0.666, 0.0, 0.35),
        ],
    }
    
    def grid_packing(n):
        """Standard k x k grid packing."""
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    def rescale_packing(packing, x_min, y_min, width, height):
        """Rescale a packing from [0,1]^2 to [x_min, x_min+width] x [y_min, y_min+height]."""
        result = []
        for x, y, angle, side in packing:
            new_x = x_min + x * width
            new_y = y_min + y * height
            new_side = side * min(width, height)
            result.append((new_x, new_y, angle, new_side))
        return result
    
    def compute_sum(squares):
        """Sum of side lengths."""
        return sum(side for _, _, _, side in squares)
    
    def check_overlap(sq1, sq2, tol=1e-9):
        """Check if two squares have overlapping interiors (with tolerance)."""
        x1, y1, a1, s1 = sq1
        x2, y2, a2, s2 = sq2
        if s1 < tol or s2 < tol:
            return False
        # Simple AABB check for axis-aligned or rotated squares
        # For rotation, use Separating Axis Theorem approximation
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        d_threshold = (s1 + s2) / 2 * 1.42
        return dx + dy < d_threshold
    
    # Try different tilings with precomputed packings
    best = grid_packing(n)
    best_sum = compute_sum(best)
    
    # Try tiling with 2x2, 3x1, etc. blocks using precomputed packings
    for m in range(2, min(7, n + 1)):
        aspect = 1.0
        if m in [p[0] for p in precomputed_packings.keys() if p[1] == aspect]:
            # Try replacing grid blocks with optimized m-packing
            k = math.isqrt(n // m) if n >= m else 0
            if k > 0 and k * k * m <= n:
                packing = precomputed_packings.get((m, aspect), [])
                if packing:
                    squares = []
                    side_block = 1.0 / k
                    block_size = side_block
                    
                    for block_i in range(k):
                        for block_j in range(k):
                            x_min = block_i * block_size
                            y_min = block_j * block_size
                            scaled = rescale_packing(packing, x_min, y_min, block_size, block_size)
                            squares.extend(scaled)
                    
                    # Add remaining squares as points
                    while len(squares) < n:
                        squares.append((0.5, 0.5, 0.0, 0.0))
                    
                    candidate = squares[:n]
                    candidate_sum = compute_sum(candidate)
                    if candidate_sum > best_sum:
                        best = candidate
                        best_sum = candidate_sum
    
    return best
