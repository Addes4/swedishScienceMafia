import math
import random
from itertools import combinations, product
import numpy as np

def solve(n):
    """Solve using large-neighbourhood search with local optimization windows."""
    
    # Initialize with the baseline grid
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    squares = squares[:n]
    
    best_solution = squares[:]
    best_score = sum(s[3] for s in best_solution)
    
    # Convert to grid representation for easier manipulation
    grid_size = max(k + 2, 3)
    time_budget = 55  # seconds, conservative estimate
    
    import time
    start_time = time.time()
    
    iteration = 0
    while time.time() - start_time < time_budget:
        iteration += 1
        
        # Pick a random window size (2x2 to min(4x4, grid_size x grid_size))
        window_size = random.randint(2, min(4, grid_size - 1))
        
        # Pick a random position for the window
        if grid_size <= window_size:
            start_row, start_col = 0, 0
            actual_window_size = grid_size
        else:
            start_row = random.randint(0, grid_size - window_size)
            start_col = random.randint(0, grid_size - window_size)
            actual_window_size = window_size
        
        # Identify squares in the window
        window_squares_idx = []
        outside_squares = []
        
        cell_size = 1.0 / grid_size
        window_bounds = (
            start_col * cell_size,
            start_row * cell_size,
            (start_col + actual_window_size) * cell_size,
            (start_row + actual_window_size) * cell_size
        )
        
        for idx, (cx, cy, angle, side_len) in enumerate(best_solution):
            # Check if centre is roughly in window
            if (window_bounds[0] <= cx < window_bounds[2] and
                window_bounds[1] <= cy < window_bounds[3]):
                window_squares_idx.append(idx)
            else:
                outside_squares.append(idx)
        
        if not window_squares_idx:
            continue
            
        # Try to repack the window squares more efficiently
        window_count = len(window_squares_idx)
        
        # Simple repacking strategy: try different configurations
        best_window_config = None
        best_window_score = sum(best_solution[i][3] for i in window_squares_idx)
        
        # Try axis-aligned grid arrangements
        for k_try in range(1, window_count + 1):
            if k_try * k_try > window_count:
                break
            
            # Can we fit k_try x k_try grid?
            cell_width = (window_bounds[2] - window_bounds[0]) / k_try
            cell_height = (window_bounds[3] - window_bounds[1]) / k_try
            side_try = min(cell_width, cell_height)
            
            if side_try > 0:
                score_try = side_try * window_count
                if score_try > best_window_score:
                    config = []
                    idx_in_window = 0
                    for i in range(k_try):
                        for j in range(k_try):
                            if idx_in_window < window_count:
                                cx = window_bounds[0] + (i + 0.5) * cell_width
                                cy = window_bounds[1] + (j + 0.5) * cell_height
                                config.append((cx, cy, 0.0, side_try))
                                idx_in_window += 1
                    
                    # Pad with zeros if needed
                    while len(config) < window_count:
                        config.append((window_bounds[0] + 0.5 * (window_bounds[2] - window_bounds[0]),
                                     window_bounds[1] + 0.5 * (window_bounds[3] - window_bounds[1]),
                                     0.0, 0.0))
                    
                    best_window_config = config
                    best_window_score = score_try
        
        # Apply the best window configuration if improved
        if best_window_config:
            new_solution = best_solution[:]
            for i, idx in enumerate(window_squares_idx):
                new_solution[idx] = best_window_config[i]
            
            new_score = sum(s[3] for s in new_solution)
            if new_score > best_score:
                best_solution = new_solution[:]
                best_score = new_score
    
    return best_solution
