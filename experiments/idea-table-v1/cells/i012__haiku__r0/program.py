import math
from functools import lru_cache


def solve(n):
    """
    Use exact tiling search on integer grids (L x L boards) to find optimal
    dissections into squares. Scale results and pad/drop to hit exactly n squares.
    """
    
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Try different board sizes and find the best dissection
    best_dissection = None
    best_score = 0
    best_L = 1
    
    # Search up to L=12 for dissections
    for L in range(1, 13):
        dissection = find_best_dissection(L, max_squares=n)
        if dissection:
            num_squares = len(dissection)
            if num_squares > 0:
                # Score is sum of side lengths
                score = sum(s for _, _, _, s in dissection)
                score_per_square = score / num_squares if num_squares > 0 else 0
                
                # Prefer dissections close to n
                adjusted_score = score_per_square
                if num_squares <= n:
                    adjusted_score *= (num_squares / n) if n > 0 else 0
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_dissection = dissection
                    best_L = L
    
    if best_dissection is None:
        # Fallback to grid layout
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    # Scale dissection by 1/best_L
    scaled = []
    for cx, cy, angle, side in best_dissection:
        scaled.append((cx / best_L, cy / best_L, angle, side / best_L))
    
    # Pad with zero-squares if needed
    while len(scaled) < n:
        scaled.append((0.5, 0.5, 0.0, 0.0))
    
    # Drop if too many
    return scaled[:n]


def find_best_dissection(L, max_squares):
    """
    Find the best dissection of an L x L board into squares.
    Returns list of (cx, cy, angle, side) in grid coordinates [0, L].
    """
    # Use backtracking to find all dissections
    board = [[False] * L for _ in range(L)]
    dissections = []
    
    def backtrack(squares_list):
        # Find first empty cell
        for y in range(L):
            for x in range(L):
                if not board[y][x]:
                    # Try placing squares of different sizes starting here
                    max_size = min(L - x, L - y)
                    for size in range(max_size, 0, -1):
                        # Check if we can place a square of this size
                        can_place = True
                        for dy in range(size):
                            for dx in range(size):
                                if board[y + dy][x + dx]:
                                    can_place = False
                                    break
                            if not can_place:
                                break
                        
                        if can_place and len(squares_list) < max_squares:
                            # Place square
                            for dy in range(size):
                                for dx in range(size):
                                    board[y + dy][x + dx] = True
                            
                            cx = x + size / 2.0
                            cy = y + size / 2.0
                            squares_list.append((cx, cy, 0.0, float(size)))
                            backtrack(squares_list)
                            squares_list.pop()
                            
                            # Remove square
                            for dy in range(size):
                                for dx in range(size):
                                    board[y + dy][x + dx] = False
                    
                    return
        
        # Board is full
        if len(squares_list) > 0:
            dissections.append(squares_list[:])
    
    backtrack([])
    
    if not dissections:
        return None
    
    # Return dissection with highest sum of sides
    best = max(dissections, key=lambda d: sum(s for _, _, _, s in d))
    return best


# Fallback for very large n or when optimization doesn't help
def solve_fallback(n):
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
