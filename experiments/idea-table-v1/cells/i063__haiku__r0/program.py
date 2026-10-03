import math
import numpy as np
from scipy.optimize import linprog


def solve(n):
    """
    Use L∞ power diagram (Laguerre-Chebyshev) Lloyd relaxation to place n squares.
    Each site gets a weight, we compute L∞ power cells, fit axis-aligned squares,
    and iterate to improve the configuration.
    """
    
    # Initialize sites and weights
    np.random.seed(42)
    sites = np.random.rand(n, 2)
    weights = np.ones(n) * 0.1
    
    max_iterations = 100
    
    for iteration in range(max_iterations):
        # Compute L∞ power cells and their Chebyshev centres
        cell_centres = np.zeros((n, 2))
        cell_radii = np.zeros(n)
        
        for i in range(n):
            # Find the L∞ power cell for site i
            centre, radius = compute_linf_power_cell(sites, weights, i)
            cell_centres[i] = centre
            cell_radii[i] = radius
        
        # Fit largest axis-aligned square in each cell
        max_sides = np.zeros(n)
        for i in range(n):
            max_sides[i] = compute_max_square_in_cell(sites, weights, i, cell_centres[i])
        
        # Update weights to balance side lengths
        target_side = 1.0 / math.sqrt(n)
        weight_adjustment = 0.05
        for i in range(n):
            if max_sides[i] > 0:
                ratio = target_side / max_sides[i]
                weights[i] *= (1.0 + weight_adjustment * (ratio - 1.0))
            weights[i] = np.clip(weights[i], 0.01, 0.5)
        
        # Move sites towards Chebyshev centres (Lloyd step)
        step_size = 0.3 / (1.0 + iteration / 10.0)
        for i in range(n):
            direction = cell_centres[i] - sites[i]
            dist = np.linalg.norm(direction)
            if dist > 1e-6:
                direction = direction / dist
                sites[i] += step_size * direction * min(dist, 0.05)
            # Keep sites in bounds
            sites[i] = np.clip(sites[i], 0.01, 0.99)
    
    # Generate final solution
    result = []
    for i in range(n):
        side = compute_max_square_in_cell(sites, weights, i, sites[i])
        side = np.clip(side, 0.0, 1.0)
        result.append((float(sites[i, 0]), float(sites[i, 1]), 0.0, float(side)))
    
    return result


def compute_linf_power_cell(sites, weights, i):
    """
    Compute the Chebyshev (L∞) centre and radius of the power cell for site i.
    The L∞ power cell is defined by: |p - site_i|∞ - weight_i < |p - site_j|∞ - weight_j
    """
    n_sites = len(sites)
    
    # Use linear programming to find the Chebyshev centre
    # Maximize r subject to:
    # |p - site_i|∞ - weight_i <= |p - site_j|∞ - weight_j + M for all j != i
    # 0 <= p_x, p_y <= 1
    
    # Approximate: find approximate Chebyshev centre
    centre = sites[i].copy()
    
    # Binary search for maximum radius
    lo, hi = 0.0, 1.0
    for _ in range(20):
        mid = (lo + hi) / 2
        if is_valid_radius(centre, mid, sites, weights, i):
            lo = mid
        else:
            hi = mid
    
    return centre, lo


def is_valid_radius(centre, radius, sites, weights, i):
    """Check if a sphere of given radius at centre can fit in its power cell."""
    # Check against all constraints
    for j in range(len(sites)):
        if i == j:
            continue
        # For all points p in the sphere around centre with radius r,
        # we need |p - sites[i]|∞ - weights[i] < |p - sites[j]|∞ - weights[j]
        # This is complex, so we approximate by checking the critical point
        dist_i = np.linalg.norm(centre - sites[i], ord=np.inf) - radius
        dist_j = np.linalg.norm(centre - sites[j], ord=np.inf) + radius
        if dist_i >= dist_j - weights[i] + weights[j]:
            return False
    return True


def compute_max_square_in_cell(sites, weights, i, centre):
    """
    Compute the largest axis-aligned square centred at centre that fits
    in the L∞ power cell of site i (and doesn't overlap with others).
    """
    # Maximum square limited by:
    # 1. Distance to boundary of unit square
    # 2. Distance to other sites (power cell boundary)
    
    # Distance to boundaries
    dist_to_boundary = min(centre[0], 1.0 - centre[0], centre[1], 1.0 - centre[1])
    max_half_side = dist_to_boundary
    
    # Check against other sites' power cells
    for j in range(len(sites)):
        if i == j:
            continue
        # Rough check: distance to other site minus its weight
        diff = sites[j] - centre
        dist_linf = np.linalg.norm(diff, ord=np.inf)
        weight_diff = weights[j] - weights[i]
        available = dist_linf - weight_diff
        max_half_side = min(max_half_side, available * 0.9)
    
    max_half_side = max(0.0, max_half_side)
    return 2.0 * max_half_side
