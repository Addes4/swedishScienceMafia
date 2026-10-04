import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    best_squares = None
    best_sum = -1
    
    # Try all feasible (k, m) pairs for the Erdős–Soifer family
    # n = k^2 + 2*m + 1 gives sum = k + m/k
    # So for given n, we try all k where k^2 < n
    
    for k in range(1, int(math.sqrt(n)) + 1):
        # From n = k^2 + 2*m + 1, we get m = (n - k^2 - 1) / 2
        if (n - k*k - 1) % 2 == 0:
            m = (n - k*k - 1) // 2
            if m >= 0 and m < k:  # m must be in valid range
                # This (k, m) pair is feasible
                sum_sides = k + m / k
                
                if sum_sides > best_sum:
                    best_sum = sum_sides
                    best_squares = construct_erdos_soifer(k, m, n)
    
    # Also try the pure k×k grid (m=0)
    k = math.isqrt(n)
    if k * k <= n:
        sum_sides = float(k)
        if sum_sides >= best_sum:
            best_sum = sum_sides
            side = 1.0 / k
            squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                      for i in range(k) for j in range(k)]
            squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
            best_squares = squares[:n]
    
    # Fallback to grid if nothing found
    if best_squares is None:
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                  for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        best_squares = squares[:n]
    
    return best_squares


def construct_erdos_soifer(k, m, n):
    """Construct Erdős–Soifer configuration with k×k grid and m×m replacement block."""
    squares = []
    
    # Cell size in the k×k grid
    cell_size = 1.0 / k
    
    # Size of squares in the (m+1)×(m+1) replacement grid
    replacement_side = m / ((m + 1) * k)
    
    # Place the k×k grid, but skip cells in the first m×m block
    for i in range(k):
        for j in range(k):
            if i < m and j < m:
                # This cell will be replaced
                continue
            # Regular grid cell
            cx = (i + 0.5) * cell_size
            cy = (j + 0.5) * cell_size
            side = cell_size
            squares.append((cx, cy, 0.0, side))
    
    # Place the (m+1)×(m+1) grid in the first m×m block of cells
    block_size = m * cell_size  # Total size of the m×m block of cells
    block_cell_size = block_size / (m + 1)  # Size of each cell in the (m+1)×(m+1) grid
    
    for i in range(m + 1):
        for j in range(m + 1):
            cx = (i + 0.5) * block_cell_size
            cy = (j + 0.5) * block_cell_size
            side = replacement_side
            squares.append((cx, cy, 0.0, side))
    
    # Pad with size-zero squares if needed
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares[:n]
