import math
import numpy as np
from scipy.optimize import linprog
import heapq


def solve(n):
    """Return n squares inside the unit square, maximizing sum of side lengths."""
    
    # Start with a good baseline solution
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Try to build up from smaller solutions
    best_solution = None
    best_sum = -1
    
    # Start with a k x k grid solution
    k = math.isqrt(n)
    if k * k == n:
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        return squares
    
    # For non-perfect squares, try building from k x k grid
    k = math.isqrt(n)
    base_side = 1.0 / k
    
    # Start with k x k grid
    squares = [((i + 0.5) * base_side, (j + 0.5) * base_side, 0.0, base_side) 
               for i in range(k) for j in range(k)]
    
    # Add remaining squares as small squares in available space
    remaining = n - len(squares)
    
    if remaining > 0:
        # Try to fit remaining squares in the gaps
        # Allocate them around the edges with decreasing size
        extra_side = (1.0 - k * base_side) / 2
        
        if remaining == 1:
            # One extra square: place in corner or edge gap
            squares.append((1.0 - extra_side/2, 0.5, 0.0, extra_side))
        elif remaining == 2:
            # Two extra squares
            sq = extra_side / 2
            squares.append((extra_side/2, 1.0 - extra_side/2, 0.0, sq))
            squares.append((1.0 - extra_side/2, 1.0 - extra_side/2, 0.0, sq))
        elif remaining == 3:
            # Three extra squares
            sq = extra_side / 2
            squares.append((extra_side/2, 1.0 - extra_side/2, 0.0, sq))
            squares.append((1.0 - extra_side/2, 1.0 - extra_side/2, 0.0, sq))
            squares.append((0.5, 1.0 - extra_side/2, 0.0, sq))
        else:
            # More extras: use zero-size squares
            for i in range(remaining):
                angle = i / remaining * 0.25  # Vary angles slightly
                squares.append((0.5, 0.5, angle, 0.0))
    
    # Optimize greedily: try growing zero-size squares
    # This is a simplified version without full LP solving
    max_iterations = min(100, n * 5)
    for iteration in range(max_iterations):
        improved = False
        
        # Find zero-size squares
        zero_indices = [i for i, sq in enumerate(squares) if sq[3] < 1e-10]
        
        if not zero_indices:
            break
        
        # Try growing the first zero-size square
        idx = zero_indices[0]
        cx, cy, angle, _ = squares[idx]
        
        # Try different sizes
        best_local_size = 0.0
        for test_size in np.linspace(0.001, 0.2, 20):
            # Check if this size is feasible (very simplified check)
            if cx + test_size/2 <= 1.0 and cy + test_size/2 <= 1.0:
                # Scale down a random neighbor if exists
                valid = True
                test_squares = squares.copy()
                test_squares[idx] = (cx, cy, angle, test_size)
                
                # Simple validity: just check bounds
                if is_valid_configuration(test_squares):
                    total = sum(sq[3] for sq in test_squares)
                    if total > sum(sq[3] for sq in squares):
                        best_local_size = test_size
                        improved = True
        
        if improved:
            cx, cy, angle, _ = squares[idx]
            squares[idx] = (cx, cy, angle, best_local_size)
    
    return squares[:n]


def is_valid_configuration(squares):
    """Simple validity check: all squares in bounds."""
    for cx, cy, angle, side in squares:
        if cx < 0 or cy < 0 or cx > 1.0 or cy > 1.0:
            return False
        if side < 0:
            return False
        # Rough bound check
        if cx + side/2 > 1.0 or cy + side/2 > 1.0:
            return False
    return True
