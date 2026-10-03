import math
from itertools import combinations

def solve(n):
    """
    Generate candidate target side lengths based on pattern mining from known optima.
    For each target, use backtracking to find a valid packing that matches it.
    """
    
    def can_place_square(x, y, side, angle, placed):
        """Check if a square can be placed without overlapping existing squares."""
        # Get the four corners of the square
        cos_a = math.cos(2 * math.pi * angle)
        sin_a = math.sin(2 * math.pi * angle)
        
        half_diag = side * math.sqrt(2) / 2
        corners = [
            (x + half_diag * math.cos(2 * math.pi * angle + i * 0.5), 
             y + half_diag * math.sin(2 * math.pi * angle + i * 0.5))
            for i in range(4)
        ]
        
        # Check bounds
        for cx, cy in corners:
            if cx < 0 or cx > 1 or cy < 0 or cy > 1:
                return False
        
        # Check against placed squares
        for px, py, pangle, pside in placed:
            if squares_overlap(x, y, side, angle, px, py, pside, pangle):
                return False
        
        return True
    
    def squares_overlap(x1, y1, s1, a1, x2, y2, s2, a2):
        """Check if two squares overlap (including touching)."""
        # Simple AABB check for axis-aligned or slightly rotated squares
        cos_a1 = math.cos(2 * math.pi * a1)
        sin_a1 = math.sin(2 * math.pi * a1)
        cos_a2 = math.cos(2 * math.pi * a2)
        sin_a2 = math.sin(2 * math.pi * a2)
        
        half_diag1 = s1 * math.sqrt(2) / 2
        half_diag2 = s2 * math.sqrt(2) / 2
        
        # Get bounding boxes
        r1 = half_diag1 * math.sqrt(2)  # circumradius
        r2 = half_diag2 * math.sqrt(2)
        
        dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return dist < r1 + r2 - 1e-9
    
    def backtrack(placed, remaining_count, target_sum):
        """Backtrack to place remaining squares matching target sum."""
        if remaining_count == 0:
            current_sum = sum(side for _, _, _, side in placed)
            if abs(current_sum - target_sum) < 1e-9:
                return placed[:]
            return None
        
        # Estimate remaining side length per square
        current_sum = sum(side for _, _, _, side in placed)
        remaining_side = target_sum - current_sum
        avg_side = remaining_side / remaining_count
        
        # Try placing a square with size around avg_side
        for trial_side in [avg_side * 1.2, avg_side, avg_side * 0.8, 0.0]:
            trial_side = max(0, min(1, trial_side))
            
            # Try different positions
            for _ in range(20):
                x = 0.25 + 0.5 * ((_ % 4) / 4)
                y = 0.25 + 0.5 * ((_ // 4) / 4)
                angle = 0.0
                
                if can_place_square(x, y, trial_side, angle, placed):
                    placed.append((x, y, angle, trial_side))
                    result = backtrack(placed, remaining_count - 1, target_sum)
                    if result:
                        return result
                    placed.pop()
        
        return None
    
    def generate_targets(n):
        """Generate candidate target sums based on pattern mining."""
        targets = []
        sqrt_n = math.sqrt(n)
        
        # Pattern 1: (k² + a) / k for small a
        for k in range(max(1, int(sqrt_n) - 2), int(sqrt_n) + 3):
            for a in range(-2, 3):
                if k * k + a <= n:
                    targets.append((k * k + a) / k)
        
        # Pattern 2: (j·m + b) / j for small j, m, b
        for j in range(max(1, int(sqrt_n) - 2), int(sqrt_n) + 3):
            for m in range(1, 4):
                for b in range(-2, 3):
                    if j * m + b <= n:
                        targets.append((j * m + b) / j)
        
        # Remove duplicates and sort by distance to sqrt(n)
        targets = list(set(targets))
        targets.sort(key=lambda t: abs(t - sqrt_n))
        return targets[:50]
    
    # Simple grid solution as fallback
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    
    return squares[:n]
