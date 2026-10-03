import math
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Return n squares maximizing sum of side lengths."""
    
    # Precomputed near-optimal packings for small m (count, side_length, positions)
    # Format: m -> (side_per_square, [(cx, cy, angle), ...])
    precomputed = compute_precomputed_packings()
    
    # Use dynamic programming to find best partition
    best = dynamic_partition(n, precomputed)
    
    return best


def compute_precomputed_packings():
    """Precompute optimal packings for small counts."""
    packings = {}
    
    # m=1: single square
    packings[1] = (1.0, [(0.5, 0.5, 0.0)])
    
    # m=2: two squares side by side
    packings[2] = (0.5, [(0.25, 0.5, 0.0), (0.75, 0.5, 0.0)])
    
    # m=3: L-shape or triangle
    s = 1.0 / 2.0
    packings[3] = (s, [(0.25, 0.75, 0.0), (0.75, 0.75, 0.0), (0.5, 0.25, 0.0)])
    
    # m=4: 2x2 grid
    packings[4] = (0.5, [(0.25, 0.25, 0.0), (0.75, 0.25, 0.0), (0.25, 0.75, 0.0), (0.75, 0.75, 0.0)])
    
    # m=5: optimize with tilting
    packings[5] = optimize_packing(5)
    
    # m=6: 2x3 grid
    packings[6] = (1.0/3.0, [(i/3 + 1/6, j/2 + 0.25, 0.0) for i in range(3) for j in range(2)])
    
    # m=7: optimize
    packings[7] = optimize_packing(7)
    
    # m=8: 2x4 grid
    packings[8] = (0.25, [(i/4 + 0.125, j/2 + 0.25, 0.0) for i in range(4) for j in range(2)])
    
    # m=9: 3x3 grid
    packings[9] = (1.0/3.0, [(i/3 + 1/6, j/3 + 1/6, 0.0) for i in range(3) for j in range(3)])
    
    # m=10: optimize
    packings[10] = optimize_packing(10)
    
    # m=11: optimize
    packings[11] = optimize_packing(11)
    
    return packings


def optimize_packing(m):
    """Optimize packing of m equal squares using penalty method."""
    
    def objective(x):
        # x = [side, cx1, cy1, a1, cx2, cy2, a2, ...]
        side = x[0]
        if side <= 0 or side > 1:
            return 1e10
        
        positions = []
        for i in range(m):
            cx, cy, angle = x[1 + i*3], x[1 + i*3 + 1], x[1 + i*3 + 2]
            positions.append((cx, cy, angle))
        
        # Penalty for squares outside [0,1]
        penalty = 0
        half_diag = side * math.sqrt(2) / 2
        for cx, cy, _ in positions:
            if cx - half_diag < 0 or cx + half_diag > 1 or cy - half_diag < 0 or cy + half_diag > 1:
                penalty += 100
        
        # Penalty for overlaps
        for i in range(m):
            for j in range(i + 1, m):
                cx1, cy1, a1 = positions[i]
                cx2, cy2, a2 = positions[j]
                dist = math.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
                min_dist = side * math.sqrt(2)
                if dist < min_dist * 0.95:
                    penalty += 100 * (1 - dist / (min_dist * 0.95))
        
        return -m * side + penalty
    
    # Initial guess: grid layout
    k = math.ceil(math.sqrt(m))
    side_init = 1.0 / k
    x0 = [side_init]
    for i in range(k):
        for j in range(k):
            if len(x0) // 3 < m:
                x0.extend([(i + 0.5) / k, (j + 0.5) / k, 0.0])
    x0 = x0[:1 + m*3]
    
    result = minimize(objective, x0, method='L-BFGS-B', 
                     bounds=[(0.01, 1)] + [(0, 1), (0, 1), (0, 0.25)] * m,
                     options={'maxiter': 100})
    
    side = result.x[0]
    positions = [(result.x[1 + i*3], result.x[1 + i*3 + 1], result.x[1 + i*3 + 2]) for i in range(m)]
    return (side, positions)


def dynamic_partition(n, precomputed):
    """Use DP to find best partition of n into blocks."""
    memo = {}
    
    def best_partition(remaining):
        if remaining == 0:
            return []
        if remaining in memo:
            return memo[remaining]
        
        best_config = None
        best_sum = 0
        
        for m in sorted(precomputed.keys()):
            if m <= remaining:
                side, positions = precomputed[m]
                current_sum = m * side
                sub_config = best_partition(remaining - m)
                sub_sum = sum(precomputed[len(c)][0] * len(c) for c in [sub_config] if c)
                
                total_sum = current_sum + sub_sum
                if total_sum > best_sum:
                    best_sum = total_sum
                    best_config = [m] + sub_config
        
        memo[remaining] = best_config
        return best_config
    
    partition = best_partition(n)
    
    # Build result
    result = []
    offset_y = 0
    
    for m in partition:
        side, positions = precomputed[m]
        scale = 1.0 / math.ceil(math.sqrt(len(partition)))
        
        for cx, cy, angle in positions:
            result.append((cx * scale, cy * scale + offset_y, angle, side * scale))
        
        offset_y += scale
        if offset_y >= 1.0:
            offset_y = 0
    
    # Pad with zeros if needed
    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    
    return result[:n]
