import math
from functools import lru_cache

def solve(n):
    """
    Recursive construction: place one large square in a corner, split the L-shape
    into two rectangles, and fill each recursively with optimal configurations.
    """
    
    @lru_cache(maxsize=None)
    def fill_rectangle(width, height, count, depth=0):
        """
        Fill a rectangle of dimensions width x height with count squares.
        Returns (total_side_sum, list_of_squares_as_relative_coords).
        Coordinates are relative to rectangle origin (0,0) to (width, height).
        Each square is (rel_x, rel_y, angle, side).
        """
        if count == 0:
            return (0.0, ())
        if count == 1:
            # Single square: fit it optimally in the rectangle
            side = min(width, height)
            x = width / 2
            y = height / 2
            return (side, ((x, y, 0.0, side),))
        
        # Try grid packing along the longer dimension
        if width >= height:
            # Try vertical columns
            cols = max(1, int(width / height))
            if cols * height <= width and cols > 0:
                col_width = width / cols
                per_col = count // cols
                remainder = count % cols
                
                total_side = 0.0
                squares = []
                for c in range(cols):
                    col_count = per_col + (1 if c < remainder else 0)
                    if col_count > 0:
                        col_x = (c + 0.5) * col_width
                        side = col_width
                        rows = max(1, int(height / side))
                        actual_side = height / rows if rows > 0 else side
                        
                        for r in range(col_count):
                            y = (r + 0.5) * actual_side
                            if y < height:
                                total_side += actual_side
                                squares.append((col_x, y, 0.0, actual_side))
                
                if len(squares) == count:
                    return (total_side, tuple(squares))
        else:
            # Try horizontal rows
            rows = max(1, int(height / width))
            if rows * width <= height and rows > 0:
                row_height = height / rows
                per_row = count // rows
                remainder = count % rows
                
                total_side = 0.0
                squares = []
                for r in range(rows):
                    row_count = per_row + (1 if r < remainder else 0)
                    if row_count > 0:
                        row_y = (r + 0.5) * row_height
                        side = row_height
                        cols = max(1, int(width / side))
                        actual_side = width / cols if cols > 0 else side
                        
                        for c in range(row_count):
                            x = (c + 0.5) * actual_side
                            if x < width:
                                total_side += actual_side
                                squares.append((x, row_y, 0.0, actual_side))
                
                if len(squares) == count:
                    return (total_side, tuple(squares))
        
        # Fallback: simple grid
        cols = max(1, int(math.sqrt(count * width / height)))
        rows = (count + cols - 1) // cols
        col_width = width / cols
        row_height = height / rows
        side = min(col_width, row_height)
        
        total_side = 0.0
        squares = []
        for i in range(count):
            c = i % cols
            r = i // cols
            x = (c + 0.5) * col_width
            y = (r + 0.5) * row_height
            if x < width and y < height:
                total_side += side
                squares.append((x, y, 0.0, side))
        
        return (total_side, tuple(squares[:count]))
    
    @lru_cache(maxsize=None)
    def fill_lshape(width, height, count):
        """
        Fill an L-shape (full rectangle minus top-right corner square).
        Rectangle is width x height. Top-right square has side s.
        Returns best configuration.
        """
        if count == 0:
            return (0.0, ())
        
        best_sum = 0.0
        best_config = ()
        
        # Try different split points (rationals with small denominators)
        for denom in range(2, 12):
            for numer in range(1, denom):
                s = (numer / denom) * min(width, height)
                if s <= 0:
                    continue
                
                # Split into two rectangles
                # Rectangle 1: bottom, full width, height - s
                # Rectangle 2: right, width - s, height - s
                r1_w, r1_h = width, height - s
                r2_w, r2_h = width - s, height - s
                
                for c1 in range(count + 1):
                    c2 = count - c1
                    sum1, sq1 = fill_rectangle(r1_w, r1_h, c1)
                    sum2, sq2 = fill_rectangle(r2_w, r2_h, c2)
                    total = sum1 + sum2
                    
                    if total > best_sum:
                        best_sum = total
                        best_config = (sq1, sq2)
        
        return (best_sum, best_config)
    
    total_side, (sq1, sq2) = fill_lshape(1.0, 1.0, n)
    
    # Convert back to absolute coordinates
    result = []
    for x, y, angle, side in sq1:
        result.append((x, y, angle, side))
    for x, y, angle, side in sq2:
        result.append((x, y, angle, side))
    
    return result[:n]
