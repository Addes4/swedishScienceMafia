import math
from fractions import Fraction
from typing import List, Tuple


def solve(n: int) -> List[Tuple[float, float, float, float]]:
    """
    Place n squares in unit square using unequal L-frame peeling.
    
    Strategy: Peel frames with unequal sides using rational dimensions,
    then recursively solve for the remaining inner square.
    """
    
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    squares = []
    remaining = n
    offset_x, offset_y = 0.0, 0.0
    size = 1.0
    
    while remaining > 0 and size > 1e-9:
        # Try to peel an L-frame with unequal rational dimensions
        best_frame = None
        best_inner_size = 0
        best_squares_in_frame = 0
        
        # Try different frame configurations with small denominators
        for a_num in range(1, 6):
            for a_den in range(1, 6):
                for b_num in range(1, 6):
                    for b_den in range(1, 6):
                        for c_num in range(1, 6):
                            for c_den in range(1, 6):
                                a = Fraction(a_num, a_den)
                                b = Fraction(b_num, b_den)
                                c = Fraction(c_num, c_den)
                                
                                if a >= 1 or b >= 1 or c >= 1:
                                    continue
                                
                                # Check if frame tiles exactly
                                # Frame along two edges: corner square a×a,
                                # one arm with b's, other with c's
                                if a + b != 1 or a + c != 1:
                                    continue
                                
                                inner_size = Fraction(1) - a - b  # Should equal 1 - a - c too
                                if inner_size < 0:
                                    continue
                                
                                # Count squares in this frame
                                # One corner, then arm1 and arm2
                                arm1_count = int((Fraction(1) - a) / b) if b > 0 else 0
                                arm2_count = int((Fraction(1) - a) / c) if c > 0 else 0
                                frame_count = 1 + arm1_count + arm2_count
                                
                                if frame_count <= remaining and float(inner_size) > best_inner_size:
                                    best_frame = (a, b, c, arm1_count, arm2_count, frame_count)
                                    best_inner_size = float(inner_size)
                                    best_squares_in_frame = frame_count
        
        # If we found a good frame, use it
        if best_frame is not None:
            a, b, c, arm1_count, arm2_count, frame_count = best_frame
            a_f = float(a)
            b_f = float(b)
            c_f = float(c)
            inner_size_f = float(Fraction(1) - a)
            
            # Place corner square
            squares.append((offset_x + a_f/2, offset_y + a_f/2, 0.0, a_f))
            
            # Place arm1 squares (along x direction)
            for i in range(arm1_count):
                sx = offset_x + a_f + (i + 0.5) * b_f
                sy = offset_y + b_f/2
                squares.append((sx, sy, 0.0, b_f))
            
            # Place arm2 squares (along y direction)
            for j in range(arm2_count):
                sx = offset_x + c_f/2
                sy = offset_y + a_f + (j + 0.5) * c_f
                squares.append((sx, sy, 0.0, c_f))
            
            remaining -= frame_count
            offset_x += inner_size_f
            offset_y += inner_size_f
            size = inner_size_f
        else:
            # Fallback: use grid packing for remaining squares
            k = math.isqrt(remaining)
            if k == 0:
                k = 1
            side = size / k
            
            for i in range(k):
                for j in range(k):
                    if len(squares) >= n:
                        break
                    sx = offset_x + (i + 0.5) * side
                    sy = offset_y + (j + 0.5) * side
                    squares.append((sx, sy, 0.0, side))
                if len(squares) >= n:
                    break
            
            remaining = n - len(squares)
            if remaining > 0:
                squares.extend([(0.5, 0.5, 0.0, 0.0)] * remaining)
            break
    
    return squares[:n]
