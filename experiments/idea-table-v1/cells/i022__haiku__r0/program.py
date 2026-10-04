import math
from functools import lru_cache
from itertools import combinations_with_replacement
from math import gcd
from functools import reduce


def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_list(lst):
    if not lst:
        return 1
    return reduce(lcm, lst)


def solve(n):
    """Pack n squares to maximize sum of side lengths using multiset-first approach."""
    
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Generate candidate divisors
    max_d = max(3, int(3 * math.sqrt(n)) + 1)
    divisors = list(range(1, max_d + 1))
    
    # Generate multisets of divisors with their scores (sum of sides)
    candidates = []
    
    for multiset_size in range(n, 0, -1):
        # Generate all multisets of given size
        for combo in combinations_with_replacement(divisors, multiset_size):
            # Convert divisor indices to actual side lengths (1/d)
            sides = [1.0 / d for d in combo]
            total_area = sum(s * s for s in sides)
            
            # Check area constraint
            if total_area > 1.0 + 1e-9:
                continue
            
            # Pad with zeros if needed
            full_sides = sides + [0.0] * (n - len(sides))
            side_sum = sum(full_sides)
            
            # Store candidate with its properties
            candidates.append((side_sum, full_sides, combo))
    
    # Sort by side sum descending
    candidates.sort(reverse=True)
    
    # Test top candidates for packability
    for side_sum, sides, divisor_combo in candidates[:min(1000, len(candidates))]:
        result = try_pack(sides, divisor_combo)
        if result is not None:
            return result
    
    # Fallback: use the grid approach
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def try_pack(sides, divisor_combo):
    """Try to pack squares with given sides. Returns placement or None."""
    
    if not divisor_combo or not sides:
        return [(0.5, 0.5, 0.0, s) for s in sides]
    
    # Calculate board size
    board_lcm = lcm_list(list(divisor_combo))
    board_size = min(board_lcm, 1000)  # Cap to avoid huge boards
    
    # Try to pack using skyline algorithm
    placements = skyline_pack(sides, board_size)
    
    if placements is None:
        return None
    
    # Convert from board coordinates to unit square
    result = []
    for x, y, s in placements:
        if s > 1e-10:
            center_x = (x + s / 2.0) / board_size
            center_y = (y + s / 2.0) / board_size
        else:
            center_x = 0.5
            center_y = 0.5
        
        if center_x < 0 or center_x > 1 or center_y < 0 or center_y > 1:
            return None
        
        result.append((center_x, center_y, 0.0, s))
    
    return result


def skyline_pack(sides, board_size):
    """Pack squares on a board using skyline/bottom-left heuristic."""
    
    # Sort sides in descending order
    indexed_sides = [(s, i) for i, s in enumerate(sides)]
    indexed_sides.sort(reverse=True)
    
    placements = []
    skyline = [(0, 0), (board_size, 0)]  # (x, height) pairs
    
    for side, idx in indexed_sides:
        if side < 1e-10:
            placements.append((0.5 * board_size, 0.5 * board_size, side))
            continue
        
        # Find leftmost position on skyline where square fits
        placed = False
        for i in range(len(skyline) - 1):
            x = skyline[i][0]
            y = skyline[i][1]
            
            # Check if square fits
            if x + side <= board_size and y + side <= board_size:
                # Verify no overlap with current skyline
                valid = True
                for j in range(i, len(skyline) - 1):
                    if skyline[j][0] < x + side and x < skyline[j+1][0]:
                        if skyline[j][1] > y:
                            valid = False
                            break
                
                if valid:
                    placements.append((x, y, side))
                    # Update skyline
                    new_skyline = []
                    for j, (sx, sy) in enumerate(skyline):
                        if sx < x:
                            new_skyline.append((sx, sy))
                        elif sx >= x + side:
                            new_skyline.append((sx, sy))
                    new_skyline.append((x, y + side))
                    new_skyline.append((x + side, y))
                    new_skyline.sort()
                    skyline = new_skyline
                    placed = True
                    break
        
        if not placed:
            return None
    
    return placements
