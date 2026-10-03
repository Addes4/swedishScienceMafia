import math


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Find k such that k^2 <= n < (k+1)^2
    k = math.isqrt(n)
    
    # Start with a (k-1) x (k-1) grid of squares with side 1/k
    # This gives us (k-1)^2 squares
    base_count = (k - 1) ** 2
    base_side = 1.0 / k
    
    squares = []
    
    # Place the (k-1) x (k-1) grid in the corner [0, 1/k] x [0, 1/k]
    for i in range(k - 1):
        for j in range(k - 1):
            cx = (i + 0.5) * base_side
            cy = (j + 0.5) * base_side
            squares.append((cx, cy, 0.0, base_side))
    
    # Remaining squares to place
    remaining = n - base_count
    
    if remaining == 0:
        return squares
    
    # Fill the L-shaped strip with width 1/k
    # The L-shaped strip consists of:
    # 1. Right strip: [1/k, 1] x [0, 1/k] - width 1/k, height 1/k
    # 2. Top strip: [0, 1/k] x [1/k, 1] - width 1/k, height 1/k
    # 3. Top-right corner: [1/k, 1] x [1/k, 1] - width (k-1)/k, height (k-1)/k
    
    # Strategy: fill the L-strip and corner with squares of decreasing sizes
    # arranged in a staircase pattern
    
    # Right strip: place squares along x from 1/k to 1, y from 0 to 1/k
    x_pos = 1.0 / k
    y_pos = 0.5 / k
    
    j = 0
    while len(squares) < n and x_pos < 1.0:
        # Calculate remaining space in x direction
        remaining_x = 1.0 - x_pos
        # Calculate side length for this square
        side = min(remaining_x, 1.0 / k, 0.5)  # Constrain to fit in strip
        
        if side > 1e-10:
            cx = x_pos + side / 2.0
            cy = y_pos
            if cx + side / 2.0 <= 1.0 and cx - side / 2.0 >= 0:
                squares.append((cx, cy, 0.0, side))
                x_pos += side
        else:
            break
        j += 1
    
    # Top strip: place squares along y from 1/k to 1, x from 0 to 1/k
    x_pos = 0.5 / k
    y_pos = 1.0 / k
    
    while len(squares) < n and y_pos < 1.0:
        remaining_y = 1.0 - y_pos
        side = min(remaining_y, 1.0 / k, 0.5)
        
        if side > 1e-10:
            cx = x_pos
            cy = y_pos + side / 2.0
            if cy + side / 2.0 <= 1.0 and cy - side / 2.0 >= 0:
                squares.append((cx, cy, 0.0, side))
                y_pos += side
        else:
            break
    
    # Top-right corner: [1/k, 1] x [1/k, 1]
    corner_size = 1.0 - 1.0 / k  # Size of the corner region
    
    # Fill corner with a grid if needed
    if len(squares) < n:
        corner_k = math.isqrt(n - len(squares))
        if corner_k > 0:
            corner_side = corner_size / (corner_k + 1)
            for i in range(corner_k):
                for j in range(corner_k):
                    if len(squares) >= n:
                        break
                    cx = 1.0 / k + (i + 0.5) * corner_side
                    cy = 1.0 / k + (j + 0.5) * corner_side
                    if cx + corner_side / 2.0 <= 1.0 and cy + corner_side / 2.0 <= 1.0:
                        squares.append((cx, cy, 0.0, corner_side))
    
    # Fill remaining slots with zero-area squares at center
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares[:n]
