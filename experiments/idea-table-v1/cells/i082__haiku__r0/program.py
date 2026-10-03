import math
from collections import defaultdict


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # DP with Pareto fronts
    # Key: number of squares, Value: list of (sum_of_sides, layout)
    # We keep layouts that are on the Pareto front for (sum, max_side) and (sum, min_side)
    dp = defaultdict(list)
    
    # Base case: single square of size 1
    base_layout = [(0.5, 0.5, 0.0, 1.0)]
    dp[1].append((1.0, base_layout))
    
    # Build up to n
    for count in range(2, n + 1):
        candidates = []
        
        # Try combining two smaller counts
        for k in range(1, count):
            for sum1, layout1 in dp[k]:
                for sum2, layout2 in dp[count - k]:
                    # Try to place layout2 next to layout1
                    combined = try_combine_layouts(layout1, layout2)
                    if combined is not None:
                        total_sum = sum1 + sum2
                        candidates.append((total_sum, combined))
        
        # Try splitting: take layouts from count-1 and subdivide the largest square
        if count - 1 in dp:
            for sum_prev, layout_prev in dp[count - 1]:
                # Find the largest square
                max_idx = max(range(len(layout_prev)), 
                             key=lambda i: layout_prev[i][3])
                max_side = layout_prev[max_idx][3]
                
                if max_side > 1e-9:
                    # Try subdividing into 2 or 4 smaller squares
                    for num_subs in [2, 4]:
                        new_layout = subdivide_square(layout_prev, max_idx, num_subs)
                        if new_layout is not None and len(new_layout) == count:
                            new_sum = sum(sq[3] for sq in new_layout)
                            candidates.append((new_sum, new_layout))
        
        # Keep Pareto front
        if candidates:
            pareto = compute_pareto_front(candidates)
            dp[count] = pareto[:100]  # Keep top candidates
    
    if n in dp and dp[n]:
        best_sum, best_layout = max(dp[n], key=lambda x: x[0])
        return best_layout
    
    # Fallback: grid layout
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def try_combine_layouts(layout1, layout2):
    """Try to combine two layouts by scaling and positioning."""
    # Simple approach: scale layout2 to fit in remaining space
    if not layout1 or not layout2:
        return None
    
    max_side1 = max(sq[3] for sq in layout1) if layout1 else 0
    max_side2 = max(sq[3] for sq in layout2) if layout2 else 0
    
    # Try scaling layout2 to fit beside layout1
    scale = (1.0 - max_side1) / (1.0 + max_side2) if max_side2 > 1e-9 else 0.5
    
    if scale <= 0 or scale > 1:
        return None
    
    offset_x = max_side1 + scale * max_side2
    if offset_x > 1.0:
        return None
    
    scaled_layout2 = [(sq[0] * scale + offset_x, sq[1] * scale, sq[2], sq[3] * scale) 
                     for sq in layout2]
    
    return layout1 + scaled_layout2


def subdivide_square(layout, idx, num_subs):
    """Subdivide the square at layout[idx] into num_subs smaller squares."""
    x, y, angle, side = layout[idx]
    
    if side < 1e-9:
        return None
    
    if num_subs == 2:
        new_side = side / 2.0
        new_squares = [
            (x - new_side / 2, y, angle, new_side),
            (x + new_side / 2, y, angle, new_side)
        ]
    elif num_subs == 4:
        new_side = side / 2.0
        new_squares = [
            (x - new_side / 2, y - new_side / 2, angle, new_side),
            (x + new_side / 2, y - new_side / 2, angle, new_side),
            (x - new_side / 2, y + new_side / 2, angle, new_side),
            (x + new_side / 2, y + new_side / 2, angle, new_side)
        ]
    else:
        return None
    
    new_layout = layout[:idx] + new_squares + layout[idx+1:]
    
    # Check bounds
    for sx, sy, sa, ss in new_layout:
        if sx - ss/2 < 0 or sx + ss/2 > 1 or sy - ss/2 < 0 or sy + ss/2 > 1:
            return None
    
    return new_layout


def compute_pareto_front(candidates):
    """Compute Pareto front on (sum, max_side) and (sum, min_side)."""
    if not candidates:
        return []
    
    # Compute stats for each candidate
    enriched = []
    for total_sum, layout in candidates:
        sides = [sq[3] for sq in layout]
        max_side = max(sides) if sides else 0
        min_side = min(sides) if sides else 0
        enriched.append((total_sum, max_side, min_side, layout))
    
    # Sort by sum descending
    enriched.sort(key=lambda x: x[0], reverse=True)
    
    # Pareto filter
    pareto = []
    for item in enriched:
        dominated = False
        for p in pareto:
            if p[1] >= item[1] and p[2] <= item[2]:
                dominated = True
                break
        if not dominated:
            pareto = [p for p in pareto 
                     if not (item[1] >= p[1] and item[2] <= p[2])]
            pareto.append(item)
    
    return [(item[0], item[3]) for item in pareto]
