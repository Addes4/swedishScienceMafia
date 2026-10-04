import math
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Baseline: k x k grid
    k = math.isqrt(n)
    baseline_side = 1.0 / k
    baseline_sum = k * baseline_side
    baseline = [((i + 0.5) * baseline_side, (j + 0.5) * baseline_side, 0.0, baseline_side) 
                for i in range(k) for j in range(k)]
    baseline += [(0.5, 0.5, 0.0, 0.0)] * (n - len(baseline))
    
    # Try tilted strip configuration: k-1 rows of grid + 1 tilted strip with k+1 squares
    if n >= k + 1:
        best_config = baseline
        best_sum = baseline_sum
        
        # Try tilted strip with k+1 squares in the bottom row
        num_tilted = min(k + 1, n - (k - 1) * k)
        if num_tilted > 0 and n >= (k - 1) * k + num_tilted:
            try:
                result = _optimize_tilted_strip(n, k, num_tilted)
                if result is not None and len(result) == n:
                    config_sum = sum(s[3] for s in result)
                    if config_sum > best_sum:
                        best_config = result
                        best_sum = config_sum
            except:
                pass
    else:
        best_config = baseline
    
    return best_config[:n]


def _optimize_tilted_strip(n, k, num_tilted):
    """Optimize tilted strip: k-1 grid rows + num_tilted rotated squares in a strip."""
    
    def objective(params):
        h, theta = params
        if h <= 0 or h >= 1:
            return 1e10
        if theta < 0 or theta >= 0.5:
            return 1e10
        
        # Remaining height for k-1 rows
        remaining_h = 1.0 - h
        if remaining_h <= 0:
            return 1e10
        
        row_h = remaining_h / (k - 1) if k > 1 else 0
        if row_h <= 0:
            return 1e10
        
        grid_side = row_h
        if grid_side * k > 1.0:
            return 1e10
        
        # Check if tilted squares fit in strip of height h
        tilted_side = _max_tilted_square_side(h, theta, num_tilted)
        if tilted_side <= 0:
            return 1e10
        
        # Total side length: (k-1)*k grid squares + num_tilted rotated squares
        num_grid = (k - 1) * k
        total = num_grid * grid_side + num_tilted * tilted_side
        
        # Return negative (we minimize)
        return -total
    
    # Grid search followed by optimization
    best_params = None
    best_val = float('inf')
    
    for h in np.linspace(0.1, 0.9, 9):
        for theta in np.linspace(0.01, 0.49, 9):
            try:
                res = minimize(objective, [h, theta], method='Nelder-Mead',
                              options={'maxiter': 200, 'xatol': 1e-6, 'fatol': 1e-6})
                if res.fun < best_val:
                    best_val = res.fun
                    best_params = res.x
            except:
                pass
    
    if best_params is None or best_val >= 0:
        return None
    
    h, theta = best_params
    remaining_h = 1.0 - h
    row_h = remaining_h / (k - 1) if k > 1 else 0
    grid_side = row_h
    
    # Build configuration
    config = []
    
    # Add grid squares (k-1 rows)
    for row in range(k - 1):
        y = (row + 0.5) * grid_side
        for col in range(k):
            x = (col + 0.5) * grid_side
            config.append((x, y, 0.0, grid_side))
    
    # Add tilted squares
    tilted_side = _max_tilted_square_side(h, theta, num_tilted)
    strip_y = 1.0 - h / 2.0
    spacing = 1.0 / num_tilted
    
    for i in range(num_tilted):
        x = (i + 0.5) * spacing
        config.append((x, strip_y, theta, tilted_side))
    
    # Pad with zero-size squares
    while len(config) < n:
        config.append((0.5, 0.5, 0.0, 0.0))
    
    return config[:n]


def _max_tilted_square_side(h, theta, num_squares):
    """Compute maximum side length of rotated squares in a strip of height h."""
    
    angle_rad = theta * 2 * math.pi
    cos_a = abs(math.cos(angle_rad))
    sin_a = abs(math.sin(angle_rad))
    
    # Height constraint: diagonal projection must fit
    diag_h = cos_a + sin_a
    if diag_h <= 0:
        return 0
    
    s = h / diag_h
    
    # Width constraint: k squares must fit horizontally
    if num_squares <= 0:
        return 0
    
    diag_w = cos_a + sin_a
    total_w = num_squares * diag_w * s
    
    if total_w > 1.0:
        s = 1.0 / (num_squares * diag_w)
    
    return max(0, s)
