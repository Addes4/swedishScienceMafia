import math
from functools import lru_cache


def solve(n):
    """Return n squares using column-strip construction with recursive partitioning."""
    
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Dynamic programming to find optimal strip configuration
    @lru_cache(maxsize=None)
    def dp(remaining):
        """Find best way to place 'remaining' squares.
        Returns (total_side_length, config) where config is list of (num_cols, num_rows)."""
        if remaining == 0:
            return (0.0, [])
        if remaining == 1:
            return (1.0, [(1, 1)])
        
        best_value = 0.0
        best_config = []
        
        # Try different numbers of strips (columns)
        for num_strips in range(1, remaining + 1):
            # Distribute remaining squares among strips
            # Try to balance, but also try unbalanced distributions
            base_per_strip = remaining // num_strips
            extra = remaining % num_strips
            
            # Configuration: base_per_strip in most strips, base_per_strip+1 in extra strips
            config = []
            total_value = 0.0
            squares_used = 0
            
            # Simple heuristic: wider strips get more squares vertically
            for i in range(num_strips):
                squares_in_strip = base_per_strip + (1 if i < extra else 0)
                if squares_in_strip > 0:
                    config.append(squares_in_strip)
                    squares_used += squares_in_strip
                    # Each column has width 1/num_strips
                    # Each square in that column has side = 1/num_strips / sqrt(squares_in_strip)
                    # But they stack, so side = min(1/num_strips, 1/squares_in_strip)
                    side = min(1.0 / num_strips, 1.0 / squares_in_strip)
                    total_value += squares_in_strip * side
            
            if squares_used == remaining and total_value > best_value:
                best_value = total_value
                best_config = config
        
        return (best_value, best_config)
    
    # Get configuration
    _, strip_config = dp(n)
    
    # If DP didn't work well, fall back to grid
    if not strip_config:
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    # Build result from strip configuration
    result = []
    num_strips = len(strip_config)
    strip_width = 1.0 / num_strips
    
    x_pos = 0.0
    for strip_idx, num_in_strip in enumerate(strip_config):
        side = min(strip_width, 1.0 / num_in_strip)
        strip_center_x = x_pos + strip_width / 2.0
        
        # Stack squares vertically in this strip
        y_pos = 0.0
        for j in range(num_in_strip):
            y_center = y_pos + side / 2.0
            if y_center + side / 2.0 <= 1.0:  # Ensure it fits
                result.append((strip_center_x, y_center, 0.0, side))
                y_pos += side
        
        x_pos += strip_width
    
    # Pad with zero-sized squares if needed
    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    
    return result[:n]
