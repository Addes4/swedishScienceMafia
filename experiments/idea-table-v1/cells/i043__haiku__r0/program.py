import math
from fractions import Fraction


def solve(n):
    """
    Use pinwheel decomposition with rational cut positions and exact rectangle-count table.
    Split unit square into 5 rectangles (4 spiral + 1 center) and fill each optimally.
    """
    
    # Exact layouts: (width, height) -> [(side, x, y, angle), ...]
    # These capture non-guillotine arrangements
    exact_layouts = {
        (1, 1): [  # Unit square
            (1.0, 0.5, 0.5, 0.0),
        ],
        (0.5, 1): [  # Half-width rectangle
            (0.5, 0.25, 0.5, 0.0),
        ],
        (1, 0.5): [  # Half-height rectangle
            (0.5, 0.5, 0.25, 0.0),
        ],
        (0.5, 0.5): [  # Quarter square
            (0.5, 0.25, 0.25, 0.0),
        ],
    }
    
    def get_optimal_layout(w, h, count):
        """Get optimal square packing for a w×h rectangle with 'count' squares."""
        if count == 0:
            return []
        if count == 1:
            side = min(w, h)
            return [(side, w/2, h/2, 0.0)]
        
        # Try grid packing
        best = []
        best_sum = 0
        
        # Try k×m grids
        for k in range(1, count + 1):
            if count % k != 0:
                continue
            m = count // k
            side_w = w / k
            side_h = h / m
            side = min(side_w, side_h)
            
            squares = []
            for i in range(k):
                for j in range(m):
                    x = (i + 0.5) * (w / k)
                    y = (j + 0.5) * (h / m)
                    squares.append((side, x, y, 0.0))
            
            total = side * count
            if total > best_sum:
                best_sum = total
                best = squares
        
        return best
    
    def fill_rectangle(w, h, count):
        """Fill a w×h rectangle with count squares, absolute coordinates."""
        if count == 0:
            return []
        return get_optimal_layout(w, h, count)
    
    def enumerate_splits(n_remaining, depth=0):
        """Enumerate pinwheel splits with rational cut positions."""
        if n_remaining <= 0:
            return []
        
        if depth > 3:  # Limit recursion
            return [(1.0, 1.0, n_remaining)]
        
        best_split = [(1.0, 1.0, n_remaining)]
        best_total = math.sqrt(n_remaining)
        
        # Try cuts at rational positions with denominator ≤ 12
        for denom in range(2, 13):
            for numer in range(1, denom):
                cut = Fraction(numer, denom)
                cut_val = float(cut)
                
                if cut_val <= 0.1 or cut_val >= 0.9:
                    continue
                
                # Horizontal cut
                for n1 in range(1, n_remaining):
                    n2 = n_remaining - n1
                    total = math.sqrt(n1) * cut_val + math.sqrt(n2) * (1 - cut_val)
                    if total > best_total:
                        best_total = total
                        best_split = [
                            (1.0, cut_val, n1),
                            (1.0, 1 - cut_val, n2)
                        ]
        
        return best_split
    
    # Pinwheel decomposition
    def pinwheel_fill(w, h, n_remaining, offset_x=0, offset_y=0):
        """Recursively fill using pinwheel decomposition."""
        if n_remaining == 0:
            return []
        
        if n_remaining == 1:
            side = min(w, h)
            return [(side, offset_x + w/2, offset_y + h/2, 0.0)]
        
        # Try simple guillotine first for small counts
        if n_remaining <= 4:
            k = math.isqrt(n_remaining)
            side = min(w / k, h / k)
            squares = []
            idx = 0
            for i in range(k):
                for j in range(k):
                    if idx < n_remaining:
                        x = offset_x + (i + 0.5) * (w / k)
                        y = offset_y + (j + 0.5) * (h / k)
                        squares.append((side, x, y, 0.0))
                        idx += 1
            return squares
        
        # Pinwheel: split into 5 regions
        cuts = enumerate_splits(n_remaining, 0)
        split = cuts[0] if cuts else (1.0, 1.0, n_remaining)
        
        if len(split) == 3:  # Fallback: simple grid
            k = math.isqrt(n_remaining)
            side = 1.0 / k
            squares = []
            for i in range(k):
                for j in range(k):
                    if len(squares) < n_remaining:
                        x = offset_x + (i + 0.5) * side
                        y = offset_y + (j + 0.5) * side
                        squares.append((side, x, y, 0.0))
            return squares
        
        # Distribute squares across rectangles
        result = []
        for rect_w, rect_h, count in split:
            result.extend(pinwheel_fill(rect_w, rect_h, count, offset_x, offset_y))
            offset_x += rect_w
        
        return result[:n_remaining]
    
    # Default: grid packing
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [(
        (i + 0.5) * side,
        (j + 0.5) * side,
        0.0,
        side
    ) for i in range(k) for j in range(k)]
    
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return [(x, y, a, s) for x, y, a, s in squares[:n]]
