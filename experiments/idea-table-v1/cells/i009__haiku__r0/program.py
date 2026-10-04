import math
import random
from typing import List, Tuple
import time

def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """
    Place n squares inside [0,1]x[0,1] to maximize sum of side lengths.
    Uses simulated annealing over discrete configurations.
    """
    
    def squares_overlap(s1: Tuple, s2: Tuple, eps: float = 1e-9) -> bool:
        """Check if two squares have overlapping interiors."""
        cx1, cy1, angle1, side1 = s1
        cx2, cy2, angle2, side2 = s2
        
        if side1 < eps or side2 < eps:
            return False
        
        # For axis-aligned squares (angle 0 or 0.5)
        if abs(angle1) < eps or abs(angle1 - 0.5) < eps:
            angle1 = 0
        if abs(angle2) < eps or abs(angle2 - 0.5) < eps:
            angle2 = 0
        
        if angle1 == 0 and angle2 == 0:
            h1, h2 = side1 / 2, side2 / 2
            dx = abs(cx1 - cx2)
            dy = abs(cy1 - cy2)
            return dx < h1 + h2 - eps and dy < h1 + h2 - eps
        
        # Rotated squares - use conservative bounding box check
        d_sq = (cx1 - cx2) ** 2 + (cy1 - cy2) ** 2
        max_dist = (side1 + side2) / math.sqrt(2)
        return d_sq < max_dist ** 2
    
    def is_valid_packing(squares: List[Tuple]) -> bool:
        """Check if packing is valid (no overlaps, all in bounds)."""
        for sq in squares:
            cx, cy, angle, side = sq
            h = side / 2
            # Check bounds (with margin for rotation)
            if cx - h < -0.01 or cx + h > 1.01 or cy - h < -0.01 or cy + h > 1.01:
                return False
        
        for i in range(len(squares)):
            for j in range(i + 1, len(squares)):
                if squares_overlap(squares[i], squares[j]):
                    return False
        return True
    
    def score(squares: List[Tuple]) -> float:
        """Sum of side lengths."""
        return sum(sq[3] for sq in squares)
    
    def random_grid_config(n: int):
        """Generate initial grid configuration."""
        k = math.isqrt(n)
        side = 1.0 / k
        squares = []
        for i in range(k):
            for j in range(k):
                x = (i + 0.5) * side
                y = (j + 0.5) * side
                squares.append((x, y, 0.0, side))
        
        # Add remaining as zero-size squares
        while len(squares) < n:
            squares.append((0.5, 0.5, 0.0, 0.0))
        return squares[:n]
    
    def mutate(squares: List[Tuple], temperature: float) -> List[Tuple]:
        """Apply a random mutation."""
        squares = list(squares)
        mutation_type = random.random()
        
        if mutation_type < 0.3:  # Move a square
            idx = random.randint(0, n - 1)
            cx, cy, angle, side = squares[idx]
            cx = max(0, min(1, cx + random.gauss(0, temperature * 0.1)))
            cy = max(0, min(1, cy + random.gauss(0, temperature * 0.1)))
            squares[idx] = (cx, cy, angle, side)
        
        elif mutation_type < 0.6:  # Change size
            idx = random.randint(0, n - 1)
            cx, cy, angle, side = squares[idx]
            delta = random.gauss(0, temperature * 0.05)
            side = max(0, min(1, side + delta))
            squares[idx] = (cx, cy, angle, side)
        
        elif mutation_type < 0.85:  # Rotate
            idx = random.randint(0, n - 1)
            cx, cy, angle, side = squares[idx]
            angle = (angle + random.gauss(0, temperature * 0.1)) % 1.0
            squares[idx] = (cx, cy, angle, side)
        
        else:  # Redistribute sizes among random subset
            if n > 1:
                indices = random.sample(range(n), min(3, n))
                total = sum(squares[i][3] for i in indices)
                for idx in indices:
                    cx, cy, angle, _ = squares[idx]
                    new_side = max(0, total / len(indices) + random.gauss(0, temperature * 0.02))
                    squares[idx] = (cx, cy, angle, new_side)
        
        return squares
    
    best_squares = random_grid_config(n)
    best_score = score(best_squares)
    
    if not is_valid_packing(best_squares):
        best_score = 0
    
    current = best_squares
    current_score = best_score
    
    start_time = time.time()
    max_time = 5.0  # 5 seconds for search
    iteration = 0
    
    while time.time() - start_time < max_time:
        temperature = max(0.01, 1.0 - (time.time() - start_time) / max_time)
        
        candidate = mutate(current, temperature)
        
        if is_valid_packing(candidate):
            candidate_score = score(candidate)
            
            delta = candidate_score - current_score
            if delta > 0 or random.random() < math.exp(delta * 10 / temperature):
                current = candidate
                current_score = candidate_score
                
                if candidate_score > best_score:
                    best_squares = candidate
                    best_score = candidate_score
        
        iteration += 1
    
    return best_squares
