import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    def fill_rect(x_min, y_min, x_max, y_max, p, q, count):
        """Fill a rectangle with p x q grid of squares, returning (squares_list, used_count)."""
        width = x_max - x_min
        height = y_max - y_min
        side = min(width / q, height / p)
        
        if side <= 0 or count <= 0:
            return [], 0
        
        squares = []
        used = 0
        for i in range(p):
            for j in range(q):
                if used >= count:
                    break
                cx = x_min + (j + 0.5) * side
                cy = y_min + (i + 0.5) * side
                squares.append((cx, cy, 0.0, side))
                used += 1
            if used >= count:
                break
        
        return squares, used
    
    def compute_objective(t, p, q, pp, qp):
        """Compute sum of side lengths for a horizontal split at height t."""
        # Bottom rectangle: 1 × t, grid p × q
        side1 = min(t / q, 1.0 / p)
        count1 = p * q
        sum1 = count1 * side1
        
        # Top rectangle: 1 × (1-t), grid pp × qp
        side2 = min((1.0 - t) / qp, (1.0 - t) / pp)
        count2 = pp * qp
        sum2 = count2 * side2
        
        return sum1 + sum2
    
    def find_optimal_t(p, q, pp, qp):
        """Find optimal split height t analytically."""
        # Objective: p*q*min(t/q, 1/p) + pp*qp*min((1-t)/qp, (1-t)/pp)
        # = p*q*min(t/q, 1/p) + pp*qp*min((1-t)/qp, (1-t)/pp)
        
        # Breakpoints where min() changes
        t_break1 = q / p if q / p <= 1 else 1.0
        t_break2 = 1.0 - qp / pp if 1.0 - qp / pp >= 0 else 0.0
        
        candidates = [0.0, t_break1, t_break2, 1.0]
        candidates = [t for t in candidates if 0.0 <= t <= 1.0]
        candidates = list(set(candidates))
        
        best_t = 0.5
        best_obj = compute_objective(0.5, p, q, pp, qp)
        
        for t in candidates:
            obj = compute_objective(t, p, q, pp, qp)
            if obj > best_obj:
                best_obj = obj
                best_t = t
        
        return best_t, best_obj
    
    def solve_recursive(x_min, y_min, x_max, y_max, remaining):
        """Recursively pack squares using two-rectangle split."""
        if remaining <= 0:
            return []
        
        width = x_max - x_min
        height = y_max - y_min
        
        # Base case: fill with a single grid
        best_squares = []
        best_sum = 0.0
        
        # Try different grid configurations for a single rectangle
        for p in range(1, remaining + 1):
            for q in range(1, remaining + 1):
                if p * q > remaining:
                    continue
                if p * q == remaining:
                    sq, _ = fill_rect(x_min, y_min, x_max, y_max, p, q, remaining)
                    total_sum = sum(s[3] for s in sq)
                    if total_sum > best_sum:
                        best_sum = total_sum
                        best_squares = sq
        
        # Try two-rectangle splits (horizontal)
        for p in range(1, remaining + 1):
            for q in range(1, remaining + 1):
                for pp in range(1, remaining + 1):
                    for qp in range(1, remaining + 1):
                        if p * q + pp * qp > remaining:
                            continue
                        if p * q + pp * qp < remaining and remaining > 4:
                            continue  # Only try if it fills n or close to it
                        
                        t_opt, obj = find_optimal_t(p, q, pp, qp)
                        
                        count1 = min(p * q, remaining)
                        count2 = min(pp * qp, remaining - count1)
                        
                        if obj > best_sum:
                            sq1, used1 = fill_rect(x_min, y_min, x_max, y_min + t_opt * height, p, q, count1)
                            sq2, used2 = fill_rect(x_min, y_min + t_opt * height, x_max, y_max, pp, qp, count2)
                            
                            if len(sq1) + len(sq2) == remaining or (len(sq1) + len(sq2) > best_sum):
                                best_sum = obj
                                best_squares = sq1 + sq2
        
        # Pad with zero-size squares if needed
        while len(best_squares) < remaining:
            best_squares.append((0.5, 0.5, 0.0, 0.0))
        
        return best_squares[:remaining]
    
    return solve_recursive(0.0, 0.0, 1.0, 1.0, n)
