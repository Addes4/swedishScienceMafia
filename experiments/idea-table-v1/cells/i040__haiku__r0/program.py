import math
from functools import lru_cache


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Build a memoization table for the best sum of side lengths for each count
    best = {}
    
    def compute_best(count):
        """Compute the best sum of side lengths for 'count' squares."""
        if count in best:
            return best[count]
        
        if count == 0:
            best[0] = 0.0
            return 0.0
        
        if count == 1:
            best[1] = 1.0
            return 1.0
        
        # Base case: k x k grid
        k = math.isqrt(count)
        if k * k == count:
            result = float(k) / k  # k squares of side 1/k each: sum = k * (1/k) = 1
            best[count] = result
            return result
        
        # Try partitioning into j x j grids for j = 2, 3, 4
        max_sum = float(k) / k  # fallback to largest grid that fits
        
        for j in range(2, 5):
            cell_size = 1.0 / j
            cells = j * j
            
            if count < cells:
                continue
            
            # Use knapsack DP to distribute 'count' items among 'cells' cells
            # Each cell can hold any number of squares at scale 1/j
            
            # dp[i] = best sum for i squares in a single cell (at unit scale)
            dp = {}
            for i in range(count + 1):
                dp[i] = compute_best(i)
            
            # knapsack: distribute count among cells
            # ks[c][m] = best sum when filling c cells with m squares
            ks = [[0.0 for _ in range(count + 1)] for _ in range(cells + 1)]
            
            for c in range(1, cells + 1):
                for m in range(count + 1):
                    # Try putting i squares in cell c
                    for i in range(m + 1):
                        remaining = m - i
                        prev = ks[c - 1][remaining] if c > 0 else (0.0 if remaining == 0 else -float('inf'))
                        if prev >= 0:
                            # Each square in cell c is scaled by 1/j
                            contribution = dp[i] / j
                            ks[c][m] = max(ks[c][m], prev + contribution)
            
            partition_sum = ks[cells][count]
            max_sum = max(max_sum, partition_sum)
        
        best[count] = max_sum
        return max_sum
    
    # Compute the best configuration
    compute_best(n)
    
    # Now reconstruct the actual placement
    def place_squares(count, offset_x=0.0, offset_y=0.0, scale=1.0):
        """Recursively place squares and return list of (x, y, angle, side)."""
        if count == 0:
            return []
        
        if count == 1:
            return [(offset_x + 0.5 * scale, offset_y + 0.5 * scale, 0.0, scale)]
        
        k = math.isqrt(count)
        if k * k == count:
            side = scale / k
            result = []
            for i in range(k):
                for j in range(k):
                    x = offset_x + (i + 0.5) * side
                    y = offset_y + (j + 0.5) * side
                    result.append((x, y, 0.0, side))
            return result
        
        # Try partitions
        best_result = None
        best_value = best.get(count, 0.0)
        
        for j in range(2, 5):
            cell_size = scale / j
            cells = j * j
            
            if count < cells:
                continue
            
            # Greedy distribution: try to balance or use optimal knapsack
            per_cell = count // cells
            extra = count % cells
            
            # Simple greedy: first 'extra' cells get per_cell+1, rest get per_cell
            counts = [per_cell + (1 if i < extra else 0) for i in range(cells)]
            
            result = []
            cell_idx = 0
            for i in range(j):
                for jj in range(j):
                    cx = offset_x + (i + 0.5) * cell_size
                    cy = offset_y + (jj + 0.5) * cell_size
                    cell_count = counts[cell_idx]
                    result.extend(place_squares(cell_count, offset_x + i * cell_size, offset_y + jj * cell_size, cell_size))
                    cell_idx += 1
            
            if len(result) == count:
                best_result = result
                break
        
        if best_result is None:
            # Fallback to grid
            k = math.isqrt(count)
            side = scale / k
            best_result = []
            for i in range(k):
                for jj in range(k):
                    x = offset_x + (i + 0.5) * side
                    y = offset_y + (jj + 0.5) * side
                    best_result.append((x, y, 0.0, side))
            best_result += [(offset_x + 0.5, offset_y + 0.5, 0.0, 0.0)] * (count - len(best_result))
        
        return best_result[:count]
    
    result = place_squares(n)
    return result[:n]
