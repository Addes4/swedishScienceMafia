import math
from typing import List, Tuple

def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """
    Substitution DP approach: build up solutions by replacing squares with scaled packings.
    """
    
    # Memoization: best[n] = (total_side_sum, layout_tree)
    # layout_tree is either a single square or a substitution of a square with a packing
    best = {}
    
    def get_grid_solution(k: int) -> Tuple[float, List]:
        """Get k×k grid packing and return (sum_of_sides, layout)."""
        side = 1.0 / k
        total = k * side
        squares = [(i + 0.5, j + 0.5, 0.0, side) for i in range(k) for j in range(k)]
        return total, ("grid", k, squares)
    
    def realize_layout(tree, scale=1.0, offset_x=0.5, offset_y=0.5) -> List[Tuple[float, float, float, float]]:
        """Convert layout tree to actual square positions."""
        if tree[0] == "grid":
            k = tree[1]
            side_scaled = scale / k
            result = []
            for i in range(k):
                for j in range(k):
                    cx = offset_x + (i + 0.5 - k/2) * side_scaled
                    cy = offset_y + (j + 0.5 - k/2) * side_scaled
                    result.append((cx, cy, 0.0, side_scaled))
            return result
        elif tree[0] == "substitution":
            parent_tree = tree[1]
            sub_idx = tree[2]
            sub_tree = tree[3]
            sub_scale = tree[4]
            
            parent_squares = realize_layout(parent_tree, scale, offset_x, offset_y)
            if sub_idx < len(parent_squares):
                cx, cy, angle, side = parent_squares[sub_idx]
                parent_squares.pop(sub_idx)
                new_scale = side * sub_scale
                sub_squares = realize_layout(sub_tree, new_scale, cx, cy)
                parent_squares.extend(sub_squares)
            return parent_squares
        return []
    
    def count_squares(tree) -> int:
        """Count total number of squares in layout."""
        if tree[0] == "grid":
            k = tree[1]
            return k * k
        elif tree[0] == "substitution":
            parent_tree = tree[1]
            sub_tree = tree[3]
            return count_squares(parent_tree) - 1 + count_squares(sub_tree)
        return 0
    
    def get_sum(tree) -> float:
        """Get sum of side lengths from tree."""
        if tree[0] == "grid":
            k = tree[1]
            return k / k  # k squares of side 1/k
        elif tree[0] == "substitution":
            parent_tree = tree[1]
            parent_sum = get_sum(parent_tree)
            sub_sum = get_sum(tree[3])
            sub_scale = tree[4]
            # Remove old square, add scaled new packing
            old_side = 1.0 / tree[1][1]  # Approximate
            return parent_sum - old_side + sub_scale * sub_sum
        return 0.0
    
    # Start with grid solutions
    max_k = math.isqrt(n) + 2
    for k in range(1, max_k + 1):
        m = k * k
        if m <= n + 10:
            total, tree = get_grid_solution(k)
            best[m] = (total, tree)
    
    # Build up via substitutions
    for target in range(1, n + 1):
        if target in best:
            continue
        
        best_score = 0.0
        best_tree = None
        
        # Try substituting into existing solutions
        for parent_n in sorted(best.keys()):
            if parent_n < target:
                parent_sum, parent_tree = best[parent_n]
                
                # Try substituting with solutions of various sizes
                for sub_n in sorted(best.keys()):
                    if sub_n > 0:
                        new_n = parent_n - 1 + sub_n
                        if new_n == target:
                            sub_sum, sub_tree = best[sub_n]
                            # Estimate: replacing a square of side 1/sqrt(parent_n)
                            # with scaled packing
                            parent_k = int(math.sqrt(parent_n))
                            if parent_k * parent_k == parent_n:
                                old_side = 1.0 / parent_k
                                new_score = parent_sum - old_side + old_side * sub_sum
                                if new_score > best_score:
                                    best_score = new_score
                                    best_tree = ("substitution", parent_tree, 0, sub_tree, old_side)
        
        if best_tree is not None:
            best[target] = (best_score, best_tree)
    
    # Get result for n
    if n in best:
        _, tree = best[n]
        result = realize_layout(tree)
        # Pad with zero squares if needed
        while len(result) < n:
            result.append((0.5, 0.5, 0.0, 0.0))
        return result[:n]
    
    # Fallback to grid if no solution found
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
