from fractions import Fraction
import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Build exhaustive DP table for axis-aligned guillotine packing
    max_cells = 2 * math.isqrt(n) + 4
    
    # T[p][q] = list of (count, sum, backpointer) sorted by count then sum
    # We'll use exact arithmetic with Fraction
    T = [[[] for _ in range(max_cells + 1)] for _ in range(max_cells + 1)]
    
    def get_pareto(entries):
        """Extract Pareto frontier: entries where no other dominates."""
        if not entries:
            return []
        entries = sorted(entries, key=lambda x: (x[0], -x[1]))
        pareto = []
        max_sum = Fraction(-1)
        for count, total_sum, bp in entries:
            if total_sum > max_sum:
                pareto.append((count, total_sum, bp))
                max_sum = total_sum
        return pareto
    
    def fill_cell(p, q):
        """Fill T[p][q] with optimal packings."""
        if p == 0 or q == 0:
            T[p][q] = [(0, Fraction(0), None)]
            return
        
        if T[p][q]:
            return
        
        candidates = []
        
        # Option 1: Cell itself is one square, plus remainder
        # Square of side min(p,q) in the cell
        side_len = Fraction(min(p, q))
        square_sum = side_len
        
        # Remainder after placing one square
        if p >= q:
            # Square takes up q×q, remainder is (p-q)×q
            fill_cell(p - q, q)
            for count_r, sum_r, bp_r in T[p - q][q]:
                candidates.append((1 + count_r, square_sum + sum_r, 
                                 ('one_square_h', p, q, bp_r)))
        else:
            # Square takes up p×p, remainder is p×(q-p)
            fill_cell(p, q - p)
            for count_r, sum_r, bp_r in T[p][q - p]:
                candidates.append((1 + count_r, square_sum + sum_r,
                                 ('one_square_v', p, q, bp_r)))
        
        # Option 2: Vertical cut at position i
        for i in range(1, p):
            fill_cell(i, q)
            fill_cell(p - i, q)
            for count_l, sum_l, bp_l in T[i][q]:
                for count_r, sum_r, bp_r in T[p - i][q]:
                    candidates.append((count_l + count_r, sum_l + sum_r,
                                     ('vcut', p, q, i, bp_l, bp_r)))
        
        # Option 3: Horizontal cut at position j
        for j in range(1, q):
            fill_cell(p, j)
            fill_cell(p, q - j)
            for count_b, sum_b, bp_b in T[p][j]:
                for count_t, sum_t, bp_t in T[p][q - j]:
                    candidates.append((count_b + count_t, sum_b + sum_t,
                                     ('hcut', p, q, j, bp_b, bp_t)))
        
        T[p][q] = get_pareto(candidates)
    
    # Fill the table for the unit square with different discretizations
    best_layout = None
    best_sum = Fraction(-1)
    
    # Try different board sizes to discretize the unit square
    for L in range(1, max_cells + 1):
        fill_cell(L, L)
        for count, total_sum, bp in T[L][L]:
            if count == n and total_sum > best_sum:
                best_sum = total_sum
                best_layout = (L, L, bp)
    
    # Reconstruct layout from backpointer
    def reconstruct(p, q, bp, scale):
        """Reconstruct squares from backpointer tree."""
        if bp is None:
            return []
        
        if bp[0] == 'one_square_h':
            _, p_orig, q_orig, bp_rest = bp
            side = Fraction(q_orig) / q_orig  # q_orig is the dimension
            square_center = (Fraction(q_orig) / 2 / p_orig, Fraction(q_orig) / 2 / q_orig)
            result = [square_center + (0.0, float(side))]
            
            # Add remainder with offset
            remainder = reconstruct(p_orig - q_orig, q_orig, bp_rest, scale)
            for x, y, angle, s in remainder:
                result.append((x + Fraction(q_orig) / p_orig, y, angle, s))
            return result
        
        elif bp[0] == 'one_square_v':
            _, p_orig, q_orig, bp_rest = bp
            side = Fraction(p_orig) / p_orig
            square_center = (Fraction(p_orig) / 2 / p_orig, Fraction(p_orig) / 2 / q_orig)
            result = [square_center + (0.0, float(side))]
            
            remainder = reconstruct(p_orig, q_orig - p_orig, bp_rest, scale)
            for x, y, angle, s in remainder:
                result.append((x, y + Fraction(p_orig) / q_orig, angle, s))
            return result
        
        elif bp[0] == 'vcut':
            _, p_orig, q_orig, i, bp_l, bp_r = bp
            left = reconstruct(i, q_orig, bp_l, scale)
            right = reconstruct(p_orig - i, q_orig, bp_r, scale)
            for x, y, angle, s in right:
                right_adjusted = [(x + Fraction(i) / p_orig, y, angle, s) for x, y, angle, s in right]
            return left + right_adjusted
        
        elif bp[0] == 'hcut':
            _, p_orig, q_orig, j, bp_b, bp_t = bp
            bottom = reconstruct(p_orig, j, bp_b, scale)
            top = reconstruct(p_orig, q_orig - j, bp_t, scale)
            for x, y, angle, s in top:
                top_adjusted = [(x, y + Fraction(j) / q_orig, angle, s) for x, y, angle, s in top]
            return bottom + top_adjusted
    
    # Simple fallback: grid layout
    if best_layout is None:
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    L, _, bp = best_layout
    squares = reconstruct(L, L, bp, L)
    
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return [(float(x), float(y), a, s) for x, y, a, s in squares[:n]]
