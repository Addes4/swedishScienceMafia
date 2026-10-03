"""Improved baseline: largest k x k grid plus size-zero squares at boundary positions."""
import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    k = math.isqrt(n)
    side = 1.0 / k
    
    # Generate the k x k grid of squares
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    
    # Generate padding squares with size 0 at boundary positions
    # Use grid-line vertices and corners on the boundary of the unit square
    padding_count = n - len(squares)
    padding_positions = []
    
    if padding_count > 0:
        # Generate positions on the boundary (never interior to any square)
        # Bottom edge: (i/k, 0) for i in 0 to k
        for i in range(k + 1):
            padding_positions.append((i / k, 0.0))
        
        # Right edge: (1, j/k) for j in 1 to k
        for j in range(1, k + 1):
            padding_positions.append((1.0, j / k))
        
        # Top edge: (i/k, 1) for i in k-1 down to 0
        for i in range(k - 1, -1, -1):
            padding_positions.append((i / k, 1.0))
        
        # Left edge: (0, j/k) for j in k-1 down to 1
        for j in range(k - 1, 0, -1):
            padding_positions.append((0.0, j / k))
    
    # Add padding squares with size 0
    for i in range(padding_count):
        x, y = padding_positions[i % len(padding_positions)] if padding_positions else (0.5, 0.5)
        squares.append((x, y, 0.0, 0.0))
    
    return squares[:n]
