import math
import numpy as np
from scipy.optimize import linprog

def solve(n):
    """Column generation for strip-based packings.
    
    Each column pattern is a vertical strip of width w holding a mixed stack.
    We use DP to find good strip patterns, solve the master LP via column generation,
    then round to a feasible integer solution.
    """
    
    if n == 0:
        return []
    
    # Generate candidate strip patterns via DP
    # Pattern: (width, [(side1, count1), (side2, count2), ...], total_side_sum)
    patterns = []
    
    # Pattern 1: Single square of side w (width = w)
    for w_num in range(1, 101):
        w = w_num / 100.0
        patterns.append({
            'width': w,
            'squares': [(w, 1)],
            'total_sum': w,
            'count': 1
        })
    
    # Pattern 2: One square of side w + pairs of w/2 stacked
    for w_num in range(2, 101, 2):
        w = w_num / 100.0
        w_half = w / 2.0
        # Stack: one w×w square, then pairs of w/2×w/2
        for num_pairs in range(1, 10):
            total_height = w + num_pairs * w_half
            if total_height <= 1.0 + 1e-9:
                patterns.append({
                    'width': w,
                    'squares': [(w, 1), (w_half, 2 * num_pairs)],
                    'total_sum': w + 2 * num_pairs * w_half,
                    'count': 1 + 2 * num_pairs
                })
    
    # Pattern 3: Stack of k squares of side w
    for w_num in range(1, 101):
        w = w_num / 100.0
        for k in range(2, 20):
            if k * w <= 1.0 + 1e-9:
                patterns.append({
                    'width': w,
                    'squares': [(w, k)],
                    'total_sum': k * w,
                    'count': k
                })
    
    # Remove duplicates and sort by efficiency
    unique_patterns = {}
    for p in patterns:
        key = (round(p['width'] * 10000), tuple(sorted(p['squares'])))
        if key not in unique_patterns or unique_patterns[key]['total_sum'] < p['total_sum']:
            unique_patterns[key] = p
    
    patterns = list(unique_patterns.values())
    patterns.sort(key=lambda p: -p['total_sum'] / (p['width'] * p['count'] + 1e-10))
    patterns = patterns[:500]  # Keep top patterns
    
    # Master LP: minimize -sum (maximize sum)
    # Variables: x_i = number of times to use pattern i
    # Constraints: sum(width_i * x_i) <= 1, sum(count_i * x_i) = n
    
    num_patterns = len(patterns)
    widths = np.array([p['width'] for p in patterns])
    counts = np.array([p['count'] for p in patterns])
    sums = np.array([p['total_sum'] for p in patterns])
    
    # LP: min c^T x, subject to A_ub @ x <= b_ub, A_eq @ x == b_eq
    c = -sums  # Negative because linprog minimizes
    
    A_ub = [widths]
    b_ub = [1.0]
    
    A_eq = [counts]
    b_eq = [n]
    
    bounds = [(0, None) for _ in range(num_patterns)]
    
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method='highs')
    
    if not result.success or result.x is None:
        # Fallback to grid
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    # Round to integer solution
    x = result.x
    used_patterns = [(i, max(0, int(round(x[i])))) for i in range(num_patterns)]
    used_patterns = [(i, cnt) for i, cnt in used_patterns if cnt > 0]
    
    total_count = sum(cnt for _, cnt in used_patterns)
    if total_count != n:
        # Adjust: find best pattern and scale
        best_idx = np.argmax(sums / (counts + 1e-10))
        best_count = n
        used_patterns = [(best_idx, best_count)]
    
    # Place squares in strips
    result_squares = []
    x_pos = 0.0
    
    for pat_idx, num_uses in used_patterns:
        pattern = patterns[pat_idx]
        w = pattern['width']
        
        for _ in range(num_uses):
            y_pos = 0.0
            for side, count in pattern['squares']:
                step = side
                for j in range(count):
                    cx = x_pos + w / 2.0
                    cy = y_pos + side / 2.0
                    result_squares.append((cx, cy, 0.0, side))
                    y_pos += step
            x_pos += w
    
    # Ensure we have exactly n squares
    while len(result_squares) < n:
        result_squares.append((0.5, 0.5, 0.0, 0.0))
    
    return result_squares[:n]
