import math
import random
from typing import List, Tuple

def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """
    Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides.
    
    Uses random-restart integer perturbation on a discretized board.
    """
    
    def grid_layout(n: int, L: int) -> List[List[int]]:
        """Create initial grid layout on L×L board with n squares."""
        squares = []
        k = math.isqrt(n)
        side = L // k
        count = 0
        for i in range(k):
            for j in range(k):
                if count < n:
                    squares.append([i * side, j * side, side, side])
                    count += 1
        while count < n:
            squares.append([L // 2, L // 2, 0, 0])
            count += 1
        return squares
    
    def total_side(squares: List[List[int]]) -> int:
        """Calculate total side length (sum of all square sides)."""
        return sum(s[2] + s[3] for s in squares)
    
    def is_valid(squares: List[List[int]], L: int) -> bool:
        """Check if all squares fit in [0, L] × [0, L]."""
        for x1, y1, w1, h1 in squares:
            if x1 < 0 or y1 < 0 or x1 + w1 > L or y1 + h1 > L:
                return False
        return True
    
    def squares_overlap(s1: List[int], s2: List[int]) -> bool:
        """Check if two axis-aligned rectangles have overlapping interiors."""
        x1, y1, w1, h1 = s1
        x2, y2, w2, h2 = s2
        return (x1 < x2 + w2 and x1 + w1 > x2 and 
                y1 < y2 + h2 and y1 + h1 > y2)
    
    def has_overlap(squares: List[List[int]]) -> bool:
        """Check if any two squares have overlapping interiors."""
        for i in range(len(squares)):
            for j in range(i + 1, len(squares)):
                if squares_overlap(squares[i], squares[j]):
                    return False
        return True
    
    def random_move(squares: List[List[int]], L: int) -> List[List[int]]:
        """Apply a random seam-slide move."""
        new_squares = [s[:] for s in squares]
        
        if not new_squares or random.random() < 0.3:
            return new_squares
        
        # Pick a random square
        idx = random.randint(0, len(new_squares) - 1)
        
        # Try to move it or resize it slightly
        move_type = random.choice(['left', 'right', 'up', 'down', 'grow', 'shrink'])
        delta = random.choice([-1, 1]) if random.random() < 0.7 else random.randint(-2, 2)
        
        if move_type == 'left':
            new_squares[idx][0] = max(0, new_squares[idx][0] + delta)
        elif move_type == 'right':
            new_squares[idx][0] = min(L - new_squares[idx][2], new_squares[idx][0] + delta)
        elif move_type == 'up':
            new_squares[idx][1] = max(0, new_squares[idx][1] + delta)
        elif move_type == 'down':
            new_squares[idx][1] = min(L - new_squares[idx][3], new_squares[idx][1] + delta)
        elif move_type == 'grow':
            new_squares[idx][2] = min(L - new_squares[idx][0], new_squares[idx][2] + abs(delta))
        elif move_type == 'shrink':
            new_squares[idx][2] = max(0, new_squares[idx][2] - abs(delta))
        
        return new_squares
    
    def hill_climb(squares: List[List[int]], L: int, steps: int) -> List[List[int]]:
        """Local hill climbing."""
        best = [s[:] for s in squares]
        best_score = total_side(best)
        
        for _ in range(steps):
            candidate = random_move(best, L)
            
            if not is_valid(candidate, L):
                continue
            if not has_overlap(candidate):
                continue
            
            score = total_side(candidate)
            if score > best_score:
                best = candidate
                best_score = score
        
        return best
    
    # Main optimization
    L = max(10, math.isqrt(n) * 3)
    best_solution = grid_layout(n, L)
    best_score = total_side(best_solution)
    
    num_restarts = max(5, min(50, 200 // math.isqrt(n)))
    steps_per_restart = max(100, min(5000, 10000 // math.isqrt(n)))
    
    for restart in range(num_restarts):
        if restart == 0:
            current = best_solution
        else:
            current = grid_layout(n, L)
            # Add randomness
            for sq in current:
                sq[0] += random.randint(-2, 2)
                sq[1] += random.randint(-2, 2)
                sq[2] = max(0, sq[2] + random.randint(-1, 1))
                sq[3] = max(0, sq[3] + random.randint(-1, 1))
        
        current = hill_climb(current, L, steps_per_restart)
        score = total_side(current)
        
        if score > best_score:
            best_score = score
            best_solution = current
    
    # Convert to normalized coordinates
    result = []
    for x, y, w, h in best_solution:
        cx = (x + w / 2.0) / L
        cy = (y + h / 2.0) / L
        side = w / L
        result.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, min(1.0, side)))
    
    return result[:n]
