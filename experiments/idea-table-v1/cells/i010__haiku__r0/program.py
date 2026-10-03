import math
from scipy.optimize import minimize
import numpy as np


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    best_score = 0
    best_squares = None
    
    # Try grid with k = floor(sqrt(n))
    k = math.isqrt(n)
    if k > 0:
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        squares = squares[:n]
        score = sum(s[3] for s in squares)
        if score > best_score:
            best_score = score
            best_squares = squares
    
    # Try grid with k = ceil(sqrt(n)) - use n cells of k×k grid with side 1/k
    k = math.ceil(math.sqrt(n))
    if k > 0:
        side = 1.0 / k
        squares = []
        count = 0
        for i in range(k):
            for j in range(k):
                if count < n:
                    squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
                    count += 1
        score = sum(s[3] for s in squares)
        if score > best_score:
            best_score = score
            best_squares = squares
    
    # Try single large square
    if n >= 1:
        squares = [(0.5, 0.5, 0.0, 1.0)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - 1)
        score = sum(s[3] for s in squares)
        if score > best_score:
            best_score = score
            best_squares = squares
    
    # Try rectangular grids for certain n values
    for rows in range(1, n + 1):
        if n % rows == 0:
            cols = n // rows
            if rows <= cols:
                side_h = 1.0 / rows
                side_w = 1.0 / cols
                side = min(side_h, side_w)
                squares = [((j + 0.5) * (1.0 / cols), (i + 0.5) * (1.0 / rows), 0.0, side) 
                          for i in range(rows) for j in range(cols)]
                score = sum(s[3] for s in squares)
                if score > best_score:
                    best_score = score
                    best_squares = squares
    
    # Try packing with some larger squares and fill rest with small ones
    if n >= 2:
        for num_large in range(1, min(n, 5)):
            k_large = math.isqrt(num_large)
            if k_large > 0 and num_large == k_large * k_large:
                side_large = 1.0 / (k_large + 1)
                squares = [((i + 0.5) * side_large, (j + 0.5) * side_large, 0.0, side_large) 
                          for i in range(k_large) for j in range(k_large)]
                squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
                score = sum(s[3] for s in squares)
                if score > best_score:
                    best_score = score
                    best_squares = squares
    
    if best_squares is None:
        best_squares = [(0.5, 0.5, 0.0, 0.0)] * n
    
    return best_squares[:n]
