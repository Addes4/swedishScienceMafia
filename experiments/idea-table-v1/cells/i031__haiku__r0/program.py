from fractions import Fraction
from functools import lru_cache
import math


def solve(n):
    """
    Use exact rational arithmetic with memoised DP on rectangular boards.
    For the unit square, try guillotine cuts at rational positions.
    """
    
    @lru_cache(maxsize=None)
    def best_sum(p, q, m):
        """
        Best sum of side lengths for m squares in a p×q rectangle.
        p, q are Fractions representing width and height.
        Returns (best_sum_value, config) where config describes the arrangement.
        """
        if m == 0:
            return (Fraction(0), None)
        if m == 1:
            # Single square: fit the largest square possible
            side = min(p, q)
            return (side, ('single', side))
        
        # Try uniform grid packing
        best = (Fraction(0), None)
        
        # Grid arrangements
        for rows in range(1, m + 1):
            if m % rows == 0:
                cols = m // rows
                cell_w = p / cols
                cell_h = q / rows
                side = min(cell_w, cell_h)
                total = side * m
                if total > best[0]:
                    best = (total, ('grid', rows, cols, side))
        
        # Try guillotine cuts (vertical and horizontal)
        # Vertical cuts
        if p > 0:
            for k in range(1, m):
                left_sum, left_config = best_sum(Fraction(p) * Fraction(k) / Fraction(m), q, k)
                right_sum, right_config = best_sum(Fraction(p) * Fraction(m - k) / Fraction(m), q, m - k)
                total = left_sum + right_sum
                if total > best[0]:
                    best = (total, ('vcut', k, m - k, left_config, right_config))
        
        # Horizontal cuts
        if q > 0:
            for k in range(1, m):
                bottom_sum, bottom_config = best_sum(p, Fraction(q) * Fraction(k) / Fraction(m), k)
                top_sum, top_config = best_sum(p, Fraction(q) * Fraction(m - k) / Fraction(m), m - k)
                total = bottom_sum + top_sum
                if total > best[0]:
                    best = (total, ('hcut', k, m - k, bottom_config, top_config))
        
        return best
    
    def realize_config(config, x0, y0, p, q):
        """
        Convert abstract config to actual square placements.
        Returns list of (cx, cy, angle, side).
        """
        if config is None or config[0] == 'single':
            side = float(config[1])
            return [(float(x0 + p / 2), float(y0 + q / 2), 0.0, side)]
        
        if config[0] == 'grid':
            _, rows, cols, side = config
            side = float(side)
            squares = []
            cell_w = float(p) / cols
            cell_h = float(q) / rows
            for i in range(cols):
                for j in range(rows):
                    cx = float(x0) + (i + 0.5) * cell_w
                    cy = float(y0) + (j + 0.5) * cell_h
                    squares.append((cx, cy, 0.0, side))
            return squares
        
        if config[0] == 'vcut':
            _, k, m_k, left_config, right_config = config
            cut_x = x0 + p * Fraction(k) / Fraction(n)
            left_squares = realize_config(left_config, x0, y0, p * Fraction(k) / Fraction(m + m_k - k), q)
            right_squares = realize_config(right_config, cut_x, y0, p * Fraction(m_k) / Fraction(m + m_k - k), q)
            return left_squares + right_squares
        
        if config[0] == 'hcut':
            _, k, m_k, bottom_config, top_config = config
            cut_y = y0 + q * Fraction(k) / Fraction(n)
            bottom_squares = realize_config(bottom_config, x0, y0, p, q * Fraction(k) / Fraction(m + m_k - k))
            top_squares = realize_config(top_config, x0, cut_y, p, q * Fraction(m_k) / Fraction(m + m_k - k))
            return bottom_squares + top_squares
        
        return []
    
    # Solve for unit square
    best_sum_val, config = best_sum(Fraction(1), Fraction(1), n)
    squares = realize_config(config, Fraction(0), Fraction(0), Fraction(1), Fraction(1))
    
    # Clamp to [0, 1]
    result = []
    for cx, cy, angle, side in squares:
        cx = max(0.0, min(1.0, cx))
        cy = max(0.0, min(1.0, cy))
        side = max(0.0, min(1.0, side))
        result.append((cx, cy, angle, side))
    
    return result[:n]
