import math
from itertools import combinations

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Choose lattice denominator (highly composite number)
    L = 12 if n <= 20 else (24 if n <= 50 else 60)
    
    # Generate candidate squares: axis-aligned, corners on L×L lattice
    candidates = []
    
    # Try all possible side lengths that are fractions with denominator L
    for denom in [L, L//2, L//3, L//4, L//6]:
        if denom <= 0:
            continue
        for numerator in range(1, denom + 1):
            side = numerator / denom
            if side > 1.0:
                break
            
            # Try all positions on the lattice
            step = 1 / L
            for i in range(L):
                for j in range(L):
                    x_corner = i * step
                    y_corner = j * step
                    x_center = x_corner + side / 2
                    y_center = y_corner + side / 2
                    
                    # Check if square fits in unit square
                    if x_center - side/2 >= -1e-9 and x_center + side/2 <= 1 + 1e-9 and \
                       y_center - side/2 >= -1e-9 and y_center + side/2 <= 1 + 1e-9:
                        candidates.append((x_center, y_center, side))
    
    # Remove duplicates
    candidates = list(set(candidates))
    candidates.sort(key=lambda x: -x[2])  # Sort by side length descending
    
    # Build conflict graph: two squares conflict if they share interior points
    def squares_overlap(sq1, sq2, tol=1e-9):
        x1, y1, s1 = sq1
        x2, y2, s2 = sq2
        
        # Check if interiors overlap (strictly)
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        min_dist = (s1 + s2) / 2
        
        # Interior overlap if centers closer than sum of half-sides
        return dx < min_dist - tol and dy < min_dist - tol
    
    # Greedy selection with conflict avoidance
    selected = []
    for cand in candidates:
        if len(selected) >= n:
            break
        # Check if this candidate conflicts with any selected square
        conflicts = False
        for sel in selected:
            if squares_overlap(cand, sel):
                conflicts = True
                break
        if not conflicts:
            selected.append(cand)
    
    # Pad with zero-size squares if needed
    while len(selected) < n:
        selected.append((0.5, 0.5, 0.0))
    
    # Convert to required format (centre_x, centre_y, angle, side)
    result = [(x, y, 0.0, s) for x, y, s in selected[:n]]
    
    return result
