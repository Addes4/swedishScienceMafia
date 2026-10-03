import math


def solve(n):
    """Return n squares using Egyptian-row construction."""
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    # Find Egyptian fraction decomposition
    decomp = find_egyptian_decomposition(n)
    
    squares = []
    y_offset = 0.0
    
    for c_i in decomp:
        side = 1.0 / c_i
        row_height = side
        
        # Place c_i squares horizontally in this row
        for j in range(c_i):
            x = (j + 0.5) * side
            y = y_offset + 0.5 * row_height
            squares.append((x, y, 0.0, side))
        
        y_offset += row_height
    
    remaining_height = 1.0 - y_offset
    remaining_count = n - len(squares)
    
    if remaining_count > 0 and remaining_height > 1e-9:
        # Recursively fill the leftover strip (transposed)
        sub_squares = solve_strip(remaining_count, remaining_height)
        squares.extend(sub_squares)
    
    # Trim or pad to exactly n
    if len(squares) > n:
        squares = squares[:n]
    elif len(squares) < n:
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    
    return squares[:n]


def solve_strip(n, height):
    """Solve for n squares in a strip of given height, rotated 90 degrees."""
    if n == 0 or height < 1e-9:
        return []
    
    decomp = find_egyptian_decomposition(n)
    
    squares = []
    x_offset = 0.0
    
    for c_i in decomp:
        side = height / c_i
        row_width = side
        
        # Place c_i squares vertically in this column
        for j in range(c_i):
            y = (j + 0.5) * side
            x = x_offset + 0.5 * row_width
            squares.append((x, y, 0.25, side))
        
        x_offset += row_width
    
    # Pad with zeros
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    
    return squares[:n]


def find_egyptian_decomposition(n):
    """Find Egyptian fraction decomposition: (c_i) where sum(c_i) ≈ n."""
    if n == 0:
        return []
    
    decomp = []
    remaining = n
    c = 2
    
    while remaining > 0:
        if c <= remaining:
            decomp.append(c)
            remaining -= c
        c += 1
        if c > 100:  # Safety limit
            break
    
    if remaining > 0:
        decomp.append(remaining)
    
    return decomp if decomp else [1]
