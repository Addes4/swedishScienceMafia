import math
from scipy.optimize import minimize_scalar
import heapq


def solve(n):
    """
    Use Lagrangian relaxation with different prices λ to find high-quality
    layouts, then repair to exactly n squares.
    """
    
    def compute_layout_dp(price):
        """
        DP over guillotine/grid-tree recursions with cost = sum_sides - price * count.
        Returns (cost, count, layout) for the best layout at this price.
        """
        memo = {}
        
        def dp(x0, y0, x1, y1, depth=0):
            key = (x0, y0, x1, y1)
            if key in memo:
                return memo[key]
            
            width = x1 - x0
            height = y1 - y0
            side = min(width, height)
            
            # Base case: single square filling as much as possible
            if depth > 8 or side < 1e-6:
                if side > 1e-8:
                    cost = side - price
                    result = (cost, 1, [(x0 + width/2, y0 + height/2, 0.0, side)])
                else:
                    result = (0, 0, [])
                memo[key] = result
                return result
            
            best = (0, 0, [])
            
            # Option 1: place a single axis-aligned square
            if side > 1e-8:
                cost = side - price
                layout = [(x0 + width/2, y0 + height/2, 0.0, side)]
                best = max(best, (cost, 1, layout))
            
            # Option 2: guillotine cuts (horizontal and vertical)
            # Horizontal cuts
            if height > side * 1.5:
                for frac in [0.3, 0.5, 0.7]:
                    y_cut = y0 + height * frac
                    top = dp(x0, y_cut, x1, y1, depth + 1)
                    bot = dp(x0, y0, x1, y_cut, depth + 1)
                    combined_cost = top[0] + bot[0]
                    combined_count = top[1] + bot[1]
                    if combined_cost > best[0] or (combined_cost == best[0] and combined_count > best[1]):
                        best = (combined_cost, combined_count, top[2] + bot[2])
            
            # Vertical cuts
            if width > side * 1.5:
                for frac in [0.3, 0.5, 0.7]:
                    x_cut = x0 + width * frac
                    left = dp(x0, y0, x_cut, y1, depth + 1)
                    right = dp(x_cut, y0, x1, y1, depth + 1)
                    combined_cost = left[0] + right[0]
                    combined_count = left[1] + right[1]
                    if combined_cost > best[0] or (combined_cost == best[0] and combined_count > best[1]):
                        best = (combined_cost, combined_count, left[2] + right[2])
            
            # Option 3: grid layouts (2x2, 3x3, etc.)
            for grid_k in range(2, min(4, int(side * 10) + 1)):
                grid_side = min(width, height) / grid_k
                if grid_side > 1e-8:
                    layout = []
                    total_cost = 0
                    total_count = 0
                    for i in range(grid_k):
                        for j in range(grid_k):
                            cx = x0 + (i + 0.5) * width / grid_k
                            cy = y0 + (j + 0.5) * height / grid_k
                            layout.append((cx, cy, 0.0, grid_side))
                            total_cost += grid_side - price
                            total_count += 1
                    if total_cost > best[0] or (total_cost == best[0] and total_count > best[1]):
                        best = (total_cost, total_count, layout)
            
            memo[key] = best
            return best
        
        return dp(0, 0, 1, 1)
    
    # Try a range of prices to find layouts
    candidates = []
    prices = [0.01 * i for i in range(1, 101)] + [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
    
    for price in sorted(set(prices)):
        try:
            cost, count, layout = compute_layout_dp(price)
            if layout and count > 0:
                total_side = sum(s[3] for s in layout)
                candidates.append((count, total_side, layout))
        except:
            pass
    
    # Find best candidate close to n
    if candidates:
        candidates = list({(c, t): l for c, t, l in candidates}.items())
        candidates.sort(key=lambda x: (abs(x[0][0] - n), -x[0][1]))
        best_layout = candidates[0][1]
    else:
        k = max(1, math.isqrt(n))
        side = 1.0 / k
        best_layout = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                       for i in range(k) for j in range(k)]
    
    # Repair to exactly n
    if len(best_layout) < n:
        current_side = min(s[3] for s in best_layout) if best_layout else 0.1
        best_layout += [(0.5, 0.5, 0.0, current_side * 0.1)] * (n - len(best_layout))
    elif len(best_layout) > n:
        best_layout = sorted(best_layout, key=lambda s: s[3])[:n]
    
    # Validate and return
    result = best_layout[:n]
    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    
    return result[:n]
