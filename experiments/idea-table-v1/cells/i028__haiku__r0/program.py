import math
from typing import List, Tuple

def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """Return n squares maximizing the sum of side lengths."""
    
    # For small n or perfect squares, use the grid approach
    k = math.isqrt(n)
    if k * k == n:
        side = 1.0 / k
        return [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                for i in range(k) for j in range(k)]
    
    # Try tilted lattice with border filling
    best_result = None
    best_sum = 0.0
    
    # Try different rotation angles (Pythagorean angles)
    angles_to_try = [
        math.atan(0.5) / (2 * math.pi),  # atan(1/2)
        math.atan(0.75) / (2 * math.pi),  # atan(3/4)
        math.atan(1.0) / (2 * math.pi),  # 45 degrees
        math.atan(2.0) / (2 * math.pi),  # atan(2)
    ]
    
    for angle in angles_to_try:
        # Try different grid sizes for the core
        for core_k in range(1, k + 1):
            result = try_tilted_lattice(n, core_k, angle)
            if result:
                current_sum = sum(s[3] for s in result)
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_result = result
    
    # Fallback to axis-aligned grid
    if best_result is None:
        side = 1.0 / k
        best_result = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                       for i in range(k) for j in range(k)]
        best_result += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_result))
    
    return best_result[:n]


def try_tilted_lattice(n: int, core_k: int, angle: float) -> List[Tuple[float, float, float, float]]:
    """Try to place a tilted k×k lattice in center with border squares."""
    
    core_count = core_k * core_k
    if core_count > n:
        return None
    
    border_count = n - core_count
    
    # Calculate lattice side for the core
    # For a rotated square lattice, we need to fit it within [0,1]×[0,1]
    # Heuristic: try to use most of the space
    cos_a = math.cos(2 * math.pi * angle)
    sin_a = math.sin(2 * math.pi * angle)
    
    # Estimate maximum lattice side
    max_extent = 1.0 / (abs(cos_a) + abs(sin_a)) if (abs(cos_a) + abs(sin_a)) > 0.1 else 1.0
    lattice_side = max_extent / core_k * 0.95
    
    if lattice_side <= 0:
        return None
    
    squares = []
    
    # Place tilted core lattice centered at (0.5, 0.5)
    center_x, center_y = 0.5, 0.5
    half_span = (core_k - 1) * lattice_side / 2
    
    for i in range(core_k):
        for j in range(core_k):
            # Position in lattice coordinates
            dx = (i - (core_k - 1) / 2) * lattice_side
            dy = (j - (core_k - 1) / 2) * lattice_side
            
            # Rotate
            x = center_x + dx * cos_a - dy * sin_a
            y = center_y + dx * sin_a + dy * cos_a
            
            # Check bounds with safety margin
            if 0 <= x <= 1 and 0 <= y <= 1:
                squares.append((x, y, angle, lattice_side))
    
    if len(squares) < core_count:
        return None
    
    # Fill border with axis-aligned small squares
    border_side = lattice_side * 0.4
    remaining = border_count
    
    # Try to place small squares in border regions
    positions = [
        (border_side/2, border_side/2),
        (1 - border_side/2, border_side/2),
        (border_side/2, 1 - border_side/2),
        (1 - border_side/2, 1 - border_side/2),
    ]
    
    for pos in positions:
        if remaining <= 0:
            break
        if not any(squares_overlap(pos[0], pos[1], border_side, s) for s in squares):
            squares.append((pos[0], pos[1], 0.0, border_side))
            remaining -= 1
    
    # Add remaining as zero-size squares
    for _ in range(remaining):
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares


def squares_overlap(x1: float, y1: float, s1: float, sq2: Tuple) -> bool:
    """Check if two squares overlap (with interior)."""
    x2, y2, angle2, s2 = sq2
    
    # Simple AABB check for axis-aligned vs rotated
    # For now, use conservative estimate
    dist = math.hypot(x1 - x2, y1 - y2)
    return dist < (s1 + s2) / 2 * 1.5
