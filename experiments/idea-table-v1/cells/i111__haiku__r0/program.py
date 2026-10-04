import math

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Memoization for best configurations by count
    best = {}
    
    def get_best_config(m):
        """Get the best configuration for m squares, memoized."""
        if m in best:
            return best[m]
        
        if m == 0:
            return []
        if m == 1:
            result = [(0.5, 0.5, 0.0, 1.0)]
            best[m] = result
            return result
        
        best_config = None
        best_sum = -1
        
        # Try L-frame recursion with different j values
        for j in range(1, int(math.sqrt(m)) + 2):
            # Bottom arm: j squares of side 1/j
            # Left arm: j-1 squares of side 1/j
            # Remaining: (1 - 1/j) x (1 - 1/j) square for recursion
            
            used = 2 * j - 1
            if used > m:
                continue
            
            remaining = m - used
            
            # Calculate the sum for this j
            arm_sum = (2 * j - 1) / j
            
            if remaining == 0:
                total_sum = arm_sum
                config = build_l_frame(j, [])
            else:
                # Recursively solve for remaining squares
                recursive_config = get_best_config(remaining)
                recursive_sum = sum(sq[3] for sq in recursive_config)
                
                # Scale the recursive config to fit in (1-1/j) x (1-1/j) square
                scale = 1.0 - 1.0 / j
                scaled_recursive_sum = recursive_sum * scale
                
                total_sum = arm_sum + scaled_recursive_sum
                config = build_l_frame(j, recursive_config, scale)
            
            if total_sum > best_sum:
                best_sum = total_sum
                best_config = config
        
        # Also try the grid approach as fallback
        k = math.isqrt(m)
        if k * k == m:
            side = 1.0 / k
            grid_config = [(
                (i + 0.5) * side,
                (j_idx + 0.5) * side,
                0.0,
                side
            ) for i in range(k) for j_idx in range(k)]
            grid_sum = m * side
            if grid_sum > best_sum:
                best_sum = grid_sum
                best_config = grid_config
        
        best[m] = best_config if best_config else []
        return best[m]
    
    def build_l_frame(j, recursive_config, scale=1.0):
        """Build an L-frame with j squares on each arm plus recursive config."""
        config = []
        side = 1.0 / j
        
        # Bottom arm: j squares of side 1/j, positioned at y = side/2
        for i in range(j):
            x = (i + 0.5) * side
            y = side / 2
            config.append((x, y, 0.0, side))
        
        # Left arm: j-1 squares of side 1/j, positioned at x = side/2
        for i in range(1, j):
            x = side / 2
            y = (j + i - 0.5) * side
            config.append((x, y, 0.0, side))
        
        # Recursive config in the remaining (1-1/j) x (1-1/j) square
        # positioned at (1/j, 1/j) with scaling
        offset = 1.0 / j
        for cx, cy, angle, s in recursive_config:
            new_cx = offset + cx * scale
            new_cy = offset + cy * scale
            new_s = s * scale
            config.append((new_cx, new_cy, angle, new_s))
        
        return config
    
    return get_best_config(n)
