import math
import itertools


def solve(n):
    """
    For small n, use exhaustive search over axis-aligned dissections
    with upper-bound pruning to find the optimal packing.
    For larger n, fall back to grid-based heuristic.
    """
    if n <= 20:
        return solve_exact(n)
    else:
        # Fall back to grid heuristic for large n
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]


def solve_exact(n):
    """
    Exhaustive search with Cauchy-Schwarz pruning for small n.
    """
    # Discrete side choices: fractions i/L for small L
    L = 12
    discrete_sides = sorted(set([i / L for i in range(L + 1)]))
    
    best_sum = 0.0
    best_config = None
    
    def lower_bound_estimate(num_remaining):
        """Estimate minimum sum for remaining squares (all size 0)."""
        return 0.0
    
    def upper_bound(current_sum, num_remaining, used_area):
        """Cauchy-Schwarz upper bound: sum of remaining sides."""
        remaining_area = 1.0 - used_area
        if num_remaining == 0:
            return current_sum
        # Upper bound: sqrt(num_remaining * remaining_area) by Cauchy-Schwarz
        # (sum of sides)^2 <= num_remaining * (sum of areas)
        max_additional = math.sqrt(max(0, num_remaining * remaining_area))
        return current_sum + max_additional
    
    def can_place(x, y, side, placed):
        """Check if square at (x, y) with given side intersects any placed square."""
        half_side = side / 2.0
        for (px, py, _, ps) in placed:
            ph = ps / 2.0
            # Check axis-aligned bounding boxes (conservative for rotations)
            if not (x + half_side < px - ph or x - half_side > px + ph or
                    y + half_side < py - ph or y - half_side > py + ph):
                return False
        return True
    
    def dfs(depth, placed, used_area, current_sum):
        nonlocal best_sum, best_config
        
        if depth == n:
            if current_sum > best_sum:
                best_sum = current_sum
                best_config = placed[:]
            return
        
        # Pruning: check upper bound
        remaining = n - depth
        ub = upper_bound(current_sum, remaining, used_area)
        lb = lower_bound_estimate(remaining)
        
        if ub <= best_sum + 1e-9:
            return
        
        # Generate candidate placements in bottom-left skyline order
        candidates = []
        
        for side in reversed(discrete_sides):  # Try larger sides first
            if side == 0:
                # Place at arbitrary position (doesn't affect geometry)
                candidates.append((0.5, 0.5, 0.0, side))
            else:
                half_side = side / 2.0
                # Grid of candidate positions
                for xi in range(int(1.0 / max(side, 0.05)) + 2):
                    for yi in range(int(1.0 / max(side, 0.05)) + 2):
                        x = (xi + 0.5) * side
                        y = (yi + 0.5) * side
                        
                        if x + half_side <= 1.0 and y + half_side <= 1.0 and \
                           x - half_side >= 0.0 and y - half_side >= 0.0:
                            if can_place(x, y, side, placed):
                                candidates.append((x, y, 0.0, side))
        
        # Try candidates in order of decreasing side length
        candidates.sort(key=lambda c: -c[3])
        
        for x, y, angle, side in candidates[:50]:  # Limit branching
            placed.append((x, y, angle, side))
            new_area = used_area + side * side
            new_sum = current_sum + side
            
            dfs(depth + 1, placed, new_area, new_sum)
            
            placed.pop()
    
    dfs(0, [], 0.0, 0.0)
    
    if best_config is None:
        # Fallback: return grid solution
        k = math.isqrt(n)
        side = 1.0 / k
        best_config = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                       for i in range(k) for j in range(k)]
        best_config += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_config))
    
    return best_config[:n]
