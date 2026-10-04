import math
import numpy as np
from scipy.optimize import minimize_scalar


def solve(n):
    """
    Hybrid two-orientation approach:
    - Use a 45°-rotated diamond grid in a central block
    - Fill corner triangles with axis-aligned staircases
    - Use knapsack-style packing to choose which blocks to use
    """
    
    def grid_packing(n):
        """Standard k×k grid packing."""
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    def diamond_block_with_staircases(block_side, num_diamonds, corner_levels=2):
        """
        Create a diamond grid block (45° rotated) with corner triangles filled by staircases.
        Returns list of (center_x, center_y, angle, side) in block-local coordinates [0,1]×[0,1].
        """
        squares = []
        
        # Diamond grid: diamonds of side s arranged in a grid
        # For num_diamonds per side, we need spacing
        if num_diamonds == 0:
            return squares
            
        s = 1.0 / (num_diamonds + 1)  # Diamond side length
        spacing = s * math.sqrt(2)  # Distance between diamond centers
        
        # Place diamonds in 45° rotated grid
        offset = 0.5 - (num_diamonds - 1) * spacing / 2
        for i in range(num_diamonds):
            for j in range(num_diamonds):
                cx = offset + i * spacing
                cy = offset + j * spacing
                if 0 <= cx <= 1 and 0 <= cy <= 1:
                    # Clip to valid region
                    cx = max(s/2, min(1 - s/2, cx))
                    cy = max(s/2, min(1 - s/2, cy))
                    squares.append((cx, cy, 0.25, s))  # 0.25 = 90 degrees / 4
        
        # Fill corner triangles with tiny axis-aligned staircases
        tiny_side = 1.0 / (4 * corner_levels) if corner_levels > 0 else 0
        
        # Bottom-left corner staircase
        for level in range(corner_levels):
            x = tiny_side * (level + 0.5)
            y = tiny_side * (level + 0.5)
            if x < 0.5 and y < 0.5:
                squares.append((x, y, 0.0, tiny_side))
        
        # Bottom-right corner staircase
        for level in range(corner_levels):
            x = 1.0 - tiny_side * (level + 0.5)
            y = tiny_side * (level + 0.5)
            if x > 0.5 and y < 0.5:
                squares.append((x, y, 0.0, tiny_side))
        
        # Top-left corner staircase
        for level in range(corner_levels):
            x = tiny_side * (level + 0.5)
            y = 1.0 - tiny_side * (level + 0.5)
            if x < 0.5 and y > 0.5:
                squares.append((x, y, 0.0, tiny_side))
        
        # Top-right corner staircase
        for level in range(corner_levels):
            x = 1.0 - tiny_side * (level + 0.5)
            y = 1.0 - tiny_side * (level + 0.5)
            if x > 0.5 and y > 0.5:
                squares.append((x, y, 0.0, tiny_side))
        
        return squares
    
    # Try different strategies and pick the best
    best_squares = grid_packing(n)
    best_sum = sum(s[3] for s in best_squares)
    
    # Try diamond blocks with different parameters
    for num_diamonds in range(1, min(6, n + 1)):
        for corner_levels in [0, 1, 2]:
            block = diamond_block_with_staircases(1.0, num_diamonds, corner_levels)
            count = len(block)
            
            if count >= n:
                # Use this block directly if it has enough squares
                squares = block[:n]
                # Pad with zeros if needed
                squares += [(0.5, 0.5, 0.0, 0.0)] * (n - count)
                current_sum = sum(s[3] for s in squares)
                
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_squares = squares
            elif count < n:
                # Hybrid: use part of the block and fill rest with grid
                remaining = n - count
                grid = grid_packing(remaining)
                
                # Scale and position block and grid
                squares = block + [(x * 0.5, y * 0.5 + 0.5, angle, side * 0.5) 
                                   for x, y, angle, side in grid]
                squares = squares[:n]
                current_sum = sum(s[3] for s in squares)
                
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_squares = squares
    
    return best_squares
