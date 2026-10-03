from fractions import Fraction
from functools import lru_cache
import math

def solve(n):
    """Place n squares using nested shelves: rows in columns in rows.
    Use DP to find optimal count vectors, recursing to depth 3."""
    
    best_sum = 0.0
    best_config = []
    
    def place_squares(width, height, count, depth, offset_x, offset_y, target_n):
        """Recursively place squares using shelf system.
        Returns (actual_count_placed, total_side_length, square_list)"""
        
        if count == 0 or depth == 0:
            return 0, Fraction(0), []
        
        if depth == 3:
            # Base case: fill remaining space greedily with single column or row
            side = min(width, height)
            if side > 0:
                num_fit = int(min(width / side, height / side))
                num_fit = min(num_fit, count)
                if num_fit > 0:
                    squares = []
                    for i in range(num_fit):
                        if width >= height:
                            # Horizontal stacking
                            cx = offset_x + side / 2 + i * side
                            cy = offset_y + side / 2
                        else:
                            # Vertical stacking
                            cx = offset_x + side / 2
                            cy = offset_y + side / 2 + i * side
                        if cx <= 1.0 and cy <= 1.0:
                            squares.append((min(cx, 1.0), min(cy, 1.0), 0.0, float(side)))
                    return len(squares), Fraction(num_fit) * side, squares
            return 0, Fraction(0), []
        
        best_placed = 0
        best_total = Fraction(0)
        best_squares = []
        
        # Try different counts for shelves at this level
        max_shelves = min(count, int(1 / float(width) if width > 0 else 1) + 1)
        
        for num_shelves in range(1, max_shelves + 1):
            if num_shelves > count:
                break
            
            # Distribute count among shelves
            per_shelf = count // num_shelves
            remainder = count % num_shelves
            
            shelf_size = height / num_shelves
            if shelf_size <= 0:
                continue
            
            total_placed = 0
            total_length = Fraction(0)
            all_squares = []
            curr_y = offset_y
            
            for shelf_idx in range(num_shelves):
                shelf_count = per_shelf + (1 if shelf_idx < remainder else 0)
                if shelf_count == 0:
                    continue
                
                # Recurse to next level (swap width/height for alternating orientation)
                placed, length, squares = place_squares(
                    width, shelf_size, shelf_count, depth + 1,
                    offset_x, curr_y, target_n - total_placed
                )
                total_placed += placed
                total_length += length
                all_squares.extend(squares)
                curr_y += shelf_size
            
            if total_length > best_total:
                best_total = total_length
                best_placed = total_placed
                best_squares = all_squares
        
        return best_placed, best_total, best_squares
    
    # Try different initial configurations
    configs_to_try = []
    
    # Try dividing into k x 1 strips (columns of rows)
    k = min(n, int(1.0 / 0.1) + 1)
    for num_cols in range(1, min(k + 1, n + 1)):
        configs_to_try.append(('columns', num_cols))
    
    # Also try transposed (rows of columns)
    for num_rows in range(1, min(k + 1, n + 1)):
        configs_to_try.append(('rows', num_rows))
    
    for config_type, num_divisions in configs_to_try:
        placed, total_length, squares = place_squares(
            Fraction(1), Fraction(1), n, 1, Fraction(0), Fraction(0), n
        )
        
        if total_length > best_sum:
            best_sum = float(total_length)
            best_config = squares
    
    # Greedy fallback approach if needed
    if len(best_config) < n:
        # Fill remaining with zero-area squares
        remaining = n - len(best_config)
        best_config.extend([(0.5, 0.5, 0.0, 0.0)] * remaining)
    
    return best_config[:n]
