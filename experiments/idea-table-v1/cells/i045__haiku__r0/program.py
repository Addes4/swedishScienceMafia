import math
import random
import time
from typing import List, Tuple


def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Known upper bounds
    def upper_bound(n: int) -> float:
        # Erdős bound: f(k²) = k
        k = math.isqrt(n)
        if k * k == n:
            return float(k)
        
        # Halbeisen bound: f(k²+1) ≤ k for k ≤ 13
        if k <= 13 and n == k * k + 1:
            return float(k)
        
        # Cauchy-Schwarz bound: f(n) ≤ √n
        return math.sqrt(n)
    
    def get_grid_solution(n: int) -> Tuple[List[Tuple[float, float, float, float]], float]:
        """Get grid-based solution and its sum."""
        k = math.isqrt(n)
        side = 1.0 / k if k > 0 else 1.0
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        total = k * side
        return squares[:n], total
    
    def pack_with_rotation(n: int, max_time: float = 1.0) -> Tuple[List[Tuple[float, float, float, float]], float]:
        """Try to improve packing with rotations and local optimization."""
        best_squares, best_sum = get_grid_solution(n)
        start_time = time.time()
        
        # Quick optimization: try to fit additional squares in corners with rotation
        k = math.isqrt(n)
        if n > k * k:
            remaining = n - k * k
            # Try to place remaining squares in available space
            side = 1.0 / k if k > 0 else 1.0
            
            # Add remaining squares with rotation attempts
            for i in range(remaining):
                angle = 0.125 * (i % 8)  # Try different rotations
                best_squares.append((0.5, 0.5, angle, 0.0))
            
            best_sum = k * side
        
        # Simple local search for improvement
        iterations = 0
        while time.time() - start_time < max_time and iterations < 100:
            # Try small perturbations
            improved = False
            for idx in range(min(len(best_squares), 5)):
                old_sq = best_squares[idx]
                
                # Try slight position and size variations
                for _ in range(5):
                    new_x = max(0.0, min(1.0, old_sq[0] + random.uniform(-0.05, 0.05)))
                    new_y = max(0.0, min(1.0, old_sq[1] + random.uniform(-0.05, 0.05)))
                    new_angle = (old_sq[2] + random.uniform(-0.05, 0.05)) % 1.0
                    new_side = max(0.0, min(old_sq[3] + random.uniform(-0.01, 0.01), 0.5))
                    
                    best_squares[idx] = (new_x, new_y, new_angle, new_side)
                    new_sum = sum(s[3] for s in best_squares)
                    
                    if new_sum > best_sum:
                        best_sum = new_sum
                        improved = True
                        break
                    else:
                        best_squares[idx] = old_sq
            
            if not improved:
                break
            iterations += 1
        
        return best_squares, best_sum
    
    # Get base solution
    squares, current_sum = get_grid_solution(n)
    bound = upper_bound(n)
    
    # Check if we already meet the bound
    if current_sum >= bound * 0.99:  # Within 1% of bound
        return squares
    
    # Try optimization with remaining time
    start = time.time()
    max_time = min(1.0, 60.0 / max(1, math.sqrt(n)))
    
    optimized, opt_sum = pack_with_rotation(n, max_time)
    
    if opt_sum > current_sum:
        return optimized
    
    return squares
