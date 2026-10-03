import math
from fractions import Fraction
from itertools import product


def solve(n):
    """
    Use Euclidean-algorithm squared rectangles with greedy square packing.
    For various rational aspect ratios a/b, generate squared rectangle dissections,
    place them in the unit square, and fill remaining space with grid squares.
    """
    
    def squared_rectangle(a, b, max_depth=20):
        """Generate squares from Euclidean dissection of a rectangle with aspect ratio a/b."""
        squares = []
        
        def dissect(x, y, w, h, depth=0):
            if depth > max_depth or w < 1e-9 or h < 1e-9:
                return
            # Cut the largest square possible
            side = min(w, h)
            if side < 1e-9:
                return
            squares.append((x + side/2, y + side/2, side))
            if w > h:
                dissect(x + side, y, w - side, h, depth + 1)
            else:
                dissect(x, y + side, w, h - side, depth + 1)
        
        dissect(0, 0, a, b)
        return squares
    
    def normalize_and_fit(squares, target_width=1.0, target_height=1.0):
        """Normalize squares to fit in target rectangle and convert to (cx, cy, angle, side)."""
        if not squares:
            return []
        max_x = max(x + side for x, y, side in squares)
        max_y = max(y + side for x, y, side in squares)
        scale_x = target_width / max_x if max_x > 0 else 1.0
        scale_y = target_height / max_y if max_y > 0 else 1.0
        scale = min(scale_x, scale_y)
        return [(x * scale, y * scale, 0.0, side * scale) for x, y, side in squares]
    
    def fill_with_grid(remaining_space, count, base_x=0, base_y=0, base_w=1.0, base_h=1.0):
        """Fill remaining space with a regular grid of squares."""
        if count <= 0:
            return []
        k = math.isqrt(count)
        side = min(base_w, base_h) / k if k > 0 else 0
        result = []
        idx = 0
        for i in range(k):
            for j in range(k):
                if idx >= count:
                    break
                cx = base_x + (i + 0.5) * side
                cy = base_y + (j + 0.5) * side
                result.append((cx, cy, 0.0, side))
                idx += 1
            if idx >= count:
                break
        # Add zero-sized squares for remainder
        while idx < count:
            result.append((0.5, 0.5, 0.0, 0.0))
            idx += 1
        return result
    
    best_solution = None
    best_sum = 0.0
    
    # Try various rational aspect ratios with small denominators
    tried_fractions = set()
    
    for denom in range(1, min(20, n + 1)):
        for numer in range(1, min(20, n + 1)):
            frac = Fraction(numer, denom)
            key = (frac.numerator, frac.denominator)
            if key in tried_fractions:
                continue
            tried_fractions.add(key)
            
            a, b = frac.numerator, frac.denominator
            
            # Generate squared rectangle dissection
            squares_rect = squared_rectangle(a, b)
            if not squares_rect:
                continue
            
            # Normalize to fit in unit square
            normalized = normalize_and_fit(squares_rect, 1.0, 1.0)
            
            if len(normalized) >= n:
                # Already have enough squares
                current_sum = sum(side for _, _, _, side in normalized[:n])
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_solution = normalized[:n]
            else:
                # Fill remaining with grid
                remaining_count = n - len(normalized)
                grid_squares = fill_with_grid(None, remaining_count)
                combined = normalized + grid_squares
                current_sum = sum(side for _, _, _, side in combined)
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_solution = combined
            
            # Also try subdividing some squares into j×j grids
            for subdivide_idx in range(len(normalized)):
                for j in range(2, 5):
                    if len(normalized) - 1 + j*j <= n:
                        # Replace one square with j×j grid of smaller squares
                        cx, cy, angle, side = normalized[subdivide_idx]
                        modified = normalized[:subdivide_idx] + normalized[subdivide_idx+1:]
                        sub_side = side / j
                        for di in range(j):
                            for dj in range(j):
                                sub_cx = cx - side/2 + (di + 0.5) * sub_side
                                sub_cy = cy - side/2 + (dj + 0.5) * sub_side
                                if 0 <= sub_cx <= 1 and 0 <= sub_cy <= 1:
                                    modified.append((sub_cx, sub_cy, 0.0, sub_side))
                        
                        if len(modified) <= n:
                            remaining = n - len(modified)
                            modified += fill_with_grid(None, remaining)
                            current_sum = sum(side for _, _, _, side in modified[:n])
                            if current_sum > best_sum:
                                best_sum = current_sum
                                best_solution = modified[:n]
    
    # Fallback to grid if nothing worked
    if best_solution is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best_solution = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                        for i in range(k) for j in range(k)]
        best_solution += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_solution))
    
    return best_solution[:n]
