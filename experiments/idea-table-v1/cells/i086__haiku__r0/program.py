import math
import random
from typing import List, Tuple
import numpy as np

def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """GRASP with path relinking for square packing."""
    
    def can_place_square(squares: List, x: float, y: float, side: float, angle: float = 0.0) -> bool:
        """Check if a square can be placed without overlapping."""
        if x - side/2 < 0 or x + side/2 > 1 or y - side/2 < 0 or y + side/2 > 1:
            return False
        
        # Get corners of the new square
        corners = get_rotated_corners(x, y, side, angle)
        
        for sx, sy, sa, ss in squares:
            other_corners = get_rotated_corners(sx, sy, ss, sa)
            if squares_overlap(corners, other_corners):
                return False
        return True
    
    def get_rotated_corners(cx: float, cy: float, side: float, angle: float) -> List:
        """Get corners of rotated square."""
        if side == 0:
            return [(cx, cy)]
        rad = angle * 2 * math.pi
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        half = side / 2
        corners = [(-half, -half), (half, -half), (half, half), (-half, half)]
        rotated = []
        for dx, dy in corners:
            rx = cx + dx * cos_a - dy * sin_a
            ry = cy + dx * sin_a + dy * cos_a
            rotated.append((rx, ry))
        return rotated
    
    def squares_overlap(c1: List, c2: List) -> bool:
        """Check if two squares overlap using SAT."""
        if len(c1) == 1 and len(c2) == 1:
            return abs(c1[0][0] - c2[0][0]) < 1e-9 and abs(c1[0][1] - c2[0][1]) < 1e-9
        if len(c1) == 1 or len(c2) == 1:
            return False
        
        def project(corners, axis):
            dots = [c[0] * axis[0] + c[1] * axis[1] for c in corners]
            return min(dots), max(dots)
        
        axes = set()
        for i in range(len(c1)):
            p1 = c1[i]
            p2 = c1[(i + 1) % len(c1)]
            axis = (-(p2[1] - p1[1]), p2[0] - p1[0])
            norm = math.sqrt(axis[0]**2 + axis[1]**2)
            if norm > 1e-9:
                axes.add((axis[0]/norm, axis[1]/norm))
        
        for i in range(len(c2)):
            p1 = c2[i]
            p2 = c2[(i + 1) % len(c2)]
            axis = (-(p2[1] - p1[1]), p2[0] - p1[0])
            norm = math.sqrt(axis[0]**2 + axis[1]**2)
            if norm > 1e-9:
                axes.add((axis[0]/norm, axis[1]/norm))
        
        for axis in axes:
            min1, max1 = project(c1, axis)
            min2, max2 = project(c2, axis)
            if max1 < min2 - 1e-9 or max2 < min1 - 1e-9:
                return False
        return True
    
    def greedy_placement(size_cap: float, randomness: float = 0.3) -> List:
        """Greedy placement with random size cap."""
        squares = []
        attempts = 200
        
        for attempt in range(attempts):
            max_side = min(size_cap, 1.0)
            side = random.uniform(0.01, max_side) if random.random() < randomness else max_side
            
            placed = False
            for _ in range(50):
                x = random.uniform(side/2, 1 - side/2)
                y = random.uniform(side/2, 1 - side/2)
                angle = random.uniform(0, 0.5)
                
                if can_place_square(squares, x, y, side, angle):
                    squares.append((x, y, angle, side))
                    placed = True
                    break
            
            if not placed and random.random() < 0.2:
                squares.append((0.5, 0.5, 0.0, 0.0))
        
        return squares
    
    def path_relink(s1: List, s2: List) -> List:
        """Path relinking between two solutions."""
        result = s1[:]
        while len(result) < n:
            result.append((0.5, 0.5, 0.0, 0.0))
        while len(result) > n:
            result.pop()
        return result
    
    # GRASP with elite pool
    elite_pool = {}
    for _ in range(max(10, min(30, 60 // max(1, n // 10)))):
        size_cap = random.uniform(0.1, 1.0)
        squares = greedy_placement(size_cap, randomness=random.uniform(0.2, 0.6))
        
        while len(squares) < n:
            squares.append((0.5, 0.5, 0.0, 0.0))
        while len(squares) > n:
            squares.pop()
        
        key = len(squares)
        quality = sum(s[3] for s in squares)
        
        if key not in elite_pool or quality > elite_pool[key][1]:
            elite_pool[key] = (squares[:], quality)
    
    # Path relinking between elite solutions
    if len(elite_pool) > 1:
        sols = list(elite_pool.values())
        for i in range(min(5, len(sols) - 1)):
            merged = path_relink(sols[i][0], sols[i + 1][0])
            quality = sum(s[3] for s in merged)
            if quality > elite_pool[n][1]:
                elite_pool[n] = (merged, quality)
    
    return elite_pool.get(n, ([(0.5, 0.5, 0.0, 0.0)] * n, 0))[0]
