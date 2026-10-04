"""
Hybrid approach: combine exact DP on small integer boards with greedy placement.
For small n, use dynamic programming on an integer grid to find optimal axis-aligned packings.
For larger n, fall back to grid-based heuristic.
"""

import math
from functools import lru_cache


def solve(n):
    """Return n squares with maximized sum of side lengths."""
    
    # Try DP-based solution for small n
    dp_solution = solve_with_dp(n)
    if dp_solution is not None:
        return dp_solution
    
    # Fall back to grid-based heuristic
    return solve_with_grid(n)


def solve_with_grid(n):
    """Grid-based fallback: place squares in a grid pattern."""
    k = math.isqrt(n)
    side = 1.0 / k if k > 0 else 1.0
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
               for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def solve_with_dp(n):
    """
    Use DP on an integer board (L x L) to find optimal packing.
    Board is divided into L×L unit cells. Squares can have integer side lengths 1..L.
    """
    
    # Limit DP to small n and reasonable board sizes
    if n > 30:
        return None
    
    best_board_size = min(10, n)
    
    # Try different board sizes
    best_packing = None
    best_sum = 0
    
    for L in range(2, best_board_size + 1):
        result = dp_pack(L, n)
        if result and result[0] > best_sum:
            best_sum = result[0]
            best_packing = result[1]
    
    if best_packing is None:
        return None
    
    # Convert integer grid squares to unit square coordinates
    squares = []
    for (x, y, side_len) in best_packing:
        # x, y are grid coordinates (0 to L)
        # side_len is the integer side length
        center_x = (x + side_len / 2.0) / best_board_size
        center_y = (y + side_len / 2.0) / best_board_size
        side = side_len / best_board_size
        
        # Clamp to [0, 1]
        center_x = max(0.0, min(1.0, center_x))
        center_y = max(0.0, min(1.0, center_y))
        side = min(side, 1.0)
        
        squares.append((center_x, center_y, 0.0, side))
    
    # Pad with zero-size squares if needed
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares[:n]


def dp_pack(L, target_count):
    """
    DP to pack squares on an L×L board.
    State: (occupied_set, count) -> max_sum
    occupied_set is a frozenset of occupied cells.
    Returns (max_sum, list_of_squares) or None.
    """
    from collections import deque
    
    # BFS/DP approach: state = (occupied_cells, count, sum)
    # occupied_cells represented as frozenset of (row, col) tuples
    
    initial_state = (frozenset(), 0, 0.0, [])
    queue = deque([initial_state])
    
    best_for_count = {}  # count -> (max_sum, packing)
    
    max_iterations = 100000
    iterations = 0
    
    while queue and iterations < max_iterations:
        iterations += 1
        occupied, count, current_sum, packing = queue.popleft()
        
        if count == target_count:
            if count not in best_for_count or current_sum > best_for_count[count][0]:
                best_for_count[count] = (current_sum, packing)
            continue
        
        if count > target_count:
            continue
        
        # Try placing squares of different sizes at different positions
        for side_len in range(L, 0, -1):
            for x in range(L - side_len + 1):
                for y in range(L - side_len + 1):
                    # Check if placement is valid
                    cells = [(x + dx, y + dy) for dx in range(side_len) for dy in range(side_len)]
                    if all(cell not in occupied for cell in cells):
                        new_occupied = occupied | frozenset(cells)
                        new_sum = current_sum + side_len
                        new_packing = packing + [(x, y, side_len)]
                        queue.append((new_occupied, count + 1, new_sum, new_packing))
    
    if target_count in best_for_count:
        return best_for_count[target_count]
    
    return None
