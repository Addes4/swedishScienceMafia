import math
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Place n squares using a diagonal staircase pattern with optimization."""
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Try to find optimal staircase configuration
    result = optimize_staircase(n)
    if result is not None:
        return result
    
    # Fallback to grid-based solution
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def optimize_staircase(n):
    """Optimize staircase configuration of decreasing squares along diagonal."""
    
    # Determine how many "steps" (main diagonal squares)
    # Start with a reasonable number of steps
    num_steps = min(n, max(2, int(math.sqrt(n * 0.6))))
    
    def generate_squares(sides):
        """Generate square positions from side lengths."""
        squares = []
        
        # Place main diagonal squares
        x_pos = 0.0
        y_pos = 0.0
        
        for i, s in enumerate(sides):
            if s <= 0:
                continue
            # Place square center on diagonal
            cx = x_pos + s / 2
            cy = y_pos + s / 2
            
            if cx + s / 2 > 1.0 or cy + s / 2 > 1.0:
                return None  # Out of bounds
            
            squares.append((cx, cy, 0.0, s))
            x_pos += s
            y_pos += s
        
        # Fill remaining squares in upper and lower regions
        remaining = n - len(squares)
        if remaining > 0:
            # Use small squares in available space
            # Upper right region
            for i in range(remaining):
                small_side = 0.05 / math.sqrt(remaining)
                cx = 0.7 + 0.25 * (i % 3) / 3
                cy = 0.7 + 0.25 * (i // 3) / (remaining // 3 + 1)
                if cx + small_side / 2 <= 1.0 and cy + small_side / 2 <= 1.0:
                    squares.append((cx, cy, 0.0, small_side))
                else:
                    squares.append((0.5, 0.5, 0.0, 0.0))
        
        return squares
    
    # Objective: maximize sum of sides (minimize negative sum)
    def objective(sides_array):
        # Ensure sides are valid
        sides = np.clip(sides_array, 0, 1)
        squares = generate_squares(sides)
        
        if squares is None:
            return 1e10
        
        # Check for overlaps on diagonal
        total_on_diagonal = sum(sides)
        if total_on_diagonal > 1.0:
            return 1e10 + (total_on_diagonal - 1.0) * 100
        
        # Return negative sum (for minimization)
        return -sum(s for _, _, _, s in squares)
    
    # Try different numbers of steps
    best_result = None
    best_score = -float('inf')
    
    for num_steps in range(max(1, n // 3), min(n, int(math.sqrt(n)) + 3)):
        # Initial guess: geometric sequence
        initial_sides = []
        remaining_space = 0.95
        for i in range(num_steps):
            if i < n:
                s = remaining_space * (0.6 ** i)
                initial_sides.append(s)
        
        if len(initial_sides) < num_steps:
            initial_sides += [0.0] * (num_steps - len(initial_sides))
        
        initial_sides = np.array(initial_sides[:num_steps])
        
        # Optimize
        bounds = [(0, 1.0) for _ in range(num_steps)]
        constraint_sum = {'type': 'ineq', 'fun': lambda x: 1.0 - np.sum(x)}
        
        try:
            opt_result = minimize(
                objective,
                initial_sides,
                method='SLSQP',
                bounds=bounds,
                constraints=constraint_sum,
                options={'ftol': 1e-6, 'maxiter': 100}
            )
            
            opt_sides = np.clip(opt_result.x, 0, 1)
            squares = generate_squares(opt_sides)
            
            if squares is not None:
                score = sum(s for _, _, _, s in squares)
                if score > best_score:
                    best_score = score
                    best_result = squares
        except:
            pass
    
    if best_result is not None and len(best_result) >= n:
        return best_result[:n]
    
    return None
