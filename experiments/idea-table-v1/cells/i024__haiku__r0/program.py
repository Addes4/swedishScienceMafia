import math
import random
import numpy as np
from scipy.optimize import minimize, LinearConstraint, NonlinearConstraint
from scipy.spatial.distance import cdist


def solve(n):
    """Place n squares in [0,1]x[0,1] maximizing sum of side lengths."""
    
    best_solution = None
    best_score = 0.0
    
    # Try multiple random starts
    num_starts = min(5, max(2, 20 // max(1, n // 10)))
    
    for start_idx in range(num_starts):
        random.seed(42 + start_idx)
        np.random.seed(42 + start_idx)
        
        # Initialize with random positions, angles, and tiny sides
        centers = np.random.uniform(0, 1, (n, 2))
        angles = np.random.uniform(0, 1, n)
        sides = np.ones(n) * 0.001
        
        # Growth phase with overlap resolution
        solution = growth_phase(centers, angles, sides, n)
        
        # Polish with optimization
        solution = polish_solution(solution, n)
        
        # Evaluate score
        score = sum(s[3] for s in solution)
        if score > best_score:
            best_score = score
            best_solution = solution
    
    # Fallback to grid if nothing worked
    if best_solution is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best_solution = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                        for i in range(k) for j in range(k)]
        best_solution += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_solution))
    
    return best_solution[:n]


def growth_phase(centers, angles, sides, n, max_iterations=100):
    """Grow squares with overlap resolution."""
    centers = centers.copy()
    angles = angles.copy()
    sides = sides.copy()
    
    for iteration in range(max_iterations):
        # Grow each square proportionally to slack
        for i in range(n):
            slack = compute_slack(i, centers, angles, sides, n)
            growth_rate = max(0.001, slack * 0.05)
            sides[i] += growth_rate
            sides[i] = min(sides[i], 0.9)
        
        # Resolve overlaps
        resolve_overlaps(centers, angles, sides, n)
        
        # Enforce bounds
        enforce_bounds(centers, sides)
    
    # Convert to tuples
    return [(centers[i, 0], centers[i, 1], angles[i], sides[i]) for i in range(n)]


def compute_slack(idx, centers, angles, sides, n):
    """Compute slack (space available) for square idx."""
    cx, cy = centers[idx]
    half_side = sides[idx] / 2.0
    
    # Distance to boundary
    dist_to_boundary = min(cx - half_side, 1.0 - cx - half_side, 
                          cy - half_side, 1.0 - cy - half_side)
    
    # Distance to nearest other square
    min_dist_to_other = float('inf')
    for j in range(n):
        if i != j:
            dx = centers[j, 0] - cx
            dy = centers[j, 1] - cy
            dist = math.sqrt(dx*dx + dy*dy)
            min_dist_to_other = min(min_dist_to_other, 
                                   dist - sides[idx]/2 - sides[j]/2)
    
    slack = max(0, min(dist_to_boundary, min_dist_to_other / 2.0))
    return slack


def resolve_overlaps(centers, angles, sides, n, max_inner=10):
    """Resolve overlaps using separating axis push-apart."""
    for _ in range(max_inner):
        max_overlap = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                overlap, push_dir = separating_axis_overlap(
                    centers[i], angles[i], sides[i],
                    centers[j], angles[j], sides[j])
                
                if overlap > 1e-6:
                    max_overlap = max(max_overlap, overlap)
                    # Push apart
                    push = (overlap / 2.0 + 1e-4) * np.array(push_dir)
                    centers[i] += push
                    centers[j] -= push
        
        enforce_bounds(centers, sides)
        if max_overlap < 1e-5:
            break


def separating_axis_overlap(c1, a1, s1, c2, a2, s2):
    """Compute overlap and separating direction using separating axis."""
    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]
    dist = math.sqrt(dx*dx + dy*dy)
    
    if dist < 1e-9:
        return s1/2 + s2/2, np.array([1.0, 0.0])
    
    # Simple circular approximation for separating axis
    direction = np.array([dx, dy]) / dist
    
    # Effective radii (half-sides for axis-aligned approximation)
    r1 = s1 / math.sqrt(2)
    r2 = s2 / math.sqrt(2)
    
    overlap = r1 + r2 - dist
    return max(0, overlap), direction


def enforce_bounds(centers, sides):
    """Keep squares inside [0,1]x[0,1]."""
    for i in range(len(centers)):
        half_s = sides[i] / 2.0
        centers[i, 0] = np.clip(centers[i, 0], half_s, 1.0 - half_s)
        centers[i, 1] = np.clip(centers[i, 1], half_s, 1.0 - half_s)


def polish_solution(solution, n):
    """Polish with SLSQP optimization."""
    if n <= 2:
        return solution
    
    # Flatten representation
    x0 = np.array([v for sq in solution for v in sq])
    
    def objective(x):
        sides = x[3::4]
        return -np.sum(sides)
    
    def constraint_bounds(x):
        """Constraint: all values in valid ranges."""
        centers = x[:].reshape(n, 4)[:, :2]
        sides = x[3::4]
        penalties = []
        for i in range(n):
            half_s = sides[i] / 2.0
            penalties.append(max(0, half_s - centers[i, 0]))
            penalties.append(max(0, centers[i, 0] + half_s - 1.0))
            penalties.append(max(0, half_s - centers[i, 1]))
            penalties.append(max(0, centers[i, 1] + half_s - 1.0))
        return -np.array(penalties)
    
    bounds = [(0, 1) if i % 4 < 3 else (0, 1) for i in range(4*n)]
    
    try:
        res = minimize(objective, x0, method='SLSQP', 
                      bounds=bounds, constraints={'type': 'ineq', 'fun': constraint_bounds},
                      options={'maxiter': 50, 'ftol': 1e-6})
        x_opt = res.x
    except:
        x_opt = x0
    
    return [(x_opt[4*i], x_opt[4*i+1], x_opt[4*i+2], x_opt[4*i+3]) for i in range(n)]
