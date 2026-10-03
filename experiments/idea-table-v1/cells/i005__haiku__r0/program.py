import math
from functools import lru_cache

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Use recursive guillotine DP to find best packing
    # Discretize dimensions for DP
    k = max(3, math.ceil(math.sqrt(n)))
    L = 2
    granularity = 1.0 / (k * L)
    
    # Quantize to nearest multiple of granularity
    def quantize(x):
        return round(x / granularity) * granularity
    
    @lru_cache(maxsize=10000)
    def best_packing(width, height, count):
        """Returns (total_side_length, list of (x, y, angle, side)) for packing count squares in width×height rectangle."""
        width = round(width * 1000000) / 1000000
        height = round(height * 1000000) / 1000000
        
        if count == 0:
            return (0.0, [])
        
        if count == 1:
            side = min(width, height)
            return (side, [(width/2, height/2, 0.0, side)])
        
        best_result = (0.0, [])
        
        # Try vertical cuts
        if width > granularity:
            for i in range(1, count):
                for cut_x in [j * granularity for j in range(1, int(width/granularity))]:
                    cut_x = quantize(cut_x)
                    if cut_x > 0 and cut_x < width:
                        left_score, left_squares = best_packing(cut_x, height, i)
                        right_score, right_squares = best_packing(width - cut_x, height, count - i)
                        
                        total = left_score + right_score
                        if total > best_result[0]:
                            # Offset right squares
                            offset_right = [(x + cut_x, y, a, s) for x, y, a, s in right_squares]
                            best_result = (total, left_squares + offset_right)
        
        # Try horizontal cuts
        if height > granularity:
            for i in range(1, count):
                for cut_y in [j * granularity for j in range(1, int(height/granularity))]:
                    cut_y = quantize(cut_y)
                    if cut_y > 0 and cut_y < height:
                        bottom_score, bottom_squares = best_packing(width, cut_y, i)
                        top_score, top_squares = best_packing(width, height - cut_y, count - i)
                        
                        total = bottom_score + top_score
                        if total > best_result[0]:
                            # Offset top squares
                            offset_top = [(x, y + cut_y, a, s) for x, y, a, s in top_squares]
                            best_result = (total, bottom_squares + offset_top)
        
        # Try single square filling (axis-aligned, centered)
        side = min(width, height)
        single_score = side
        if single_score > best_result[0]:
            best_result = (single_score, [(width/2, height/2, 0.0, side)])
        
        return best_result
    
    _, squares = best_packing(1.0, 1.0, n)
    
    # Pad with zero-size squares if needed
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares[:n]
