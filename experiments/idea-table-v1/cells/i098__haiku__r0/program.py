import math
from fractions import Fraction
from functools import lru_cache


def solve(n):
    """Recursive frame-peeling search with Pareto optimization."""
    
    memo = {}
    
    def fill_rectangle(w, h, count, depth):
        """
        Fill a rectangle of dimensions w x h with `count` squares.
        Returns list of (centre_x, centre_y, angle, side) tuples.
        depth limits recursion.
        """
        if count == 0:
            return []
        if count == 1:
            return [(w/2, h/2, 0.0, min(w, h))]
        
        key = (w, h, count, depth)
        if key in memo:
            return memo[key]
        
        result = None
        best_sum = -1
        
        # Try grid packings first (simple baseline)
        if depth > 0:
            # Try k x m grid
            for k in range(1, count + 1):
                if count % k == 0:
                    m = count // k
                    side_w = w / k
                    side_h = h / m
                    side = min(side_w, side_h)
                    if side > 0:
                        total = side * count
                        if total > best_sum:
                            best_sum = total
                            result = [(
                                (i + 0.5) * side_w,
                                (j + 0.5) * side_h,
                                0.0,
                                side
                            ) for i in range(k) for j in range(m)]
        
        # Try frame-peeling: place one large square in corner, fill L-border
        if depth > 0 and count >= 2:
            # Try different frame widths t as fractions p/q
            for q in range(1, 13):
                for p in range(1, q + 1):
                    t = p / q
                    if t >= 1.0 or t <= 0:
                        continue
                    
                    corner_side = 1.0 - t
                    
                    # Try filling L-border with stacked squares
                    for j in range(1, 5):  # depth of stacking
                        arm_side = t / j
                        if arm_side <= 0:
                            continue
                        
                        # Horizontal arm: fits floor(w / arm_side) squares
                        horiz_count = int((w - corner_side * min(w, h) / min(w, h)) / arm_side) if w > corner_side else 0
                        # Vertical arm: fits floor(h / arm_side) squares  
                        vert_count = int((h - corner_side * min(w, h) / min(w, h)) / arm_side) if h > corner_side else 0
                        
                        # Simpler approach: try to fit j squares of size arm_side along each arm
                        if j <= count - 1:
                            remaining = count - 1 - 2 * j
                            if remaining >= 0:
                                # Estimate: place one corner square, j along each arm
                                total = corner_side + 2 * j * arm_side
                                if total > best_sum:
                                    best_sum = total
                                    squares = [(corner_side/2, corner_side/2, 0.0, corner_side)]
                                    for i in range(j):
                                        squares.append((corner_side + (i+0.5)*arm_side, (i+0.5)*arm_side, 0.0, arm_side))
                                        squares.append(((i+0.5)*arm_side, corner_side + (i+0.5)*arm_side, 0.0, arm_side))
                                    # Fill remaining with zero-sized squares at center
                                    for _ in range(remaining):
                                        squares.append((0.5, 0.5, 0.0, 0.0))
                                    result = squares[:count]
        
        if result is None:
            # Fallback: place squares of equal size
            side = min(w, h) / math.ceil(math.sqrt(count))
            result = []
            placed = 0
            cols = int(w / side) if side > 0 else 1
            cols = max(1, cols)
            for i in range(cols):
                for j in range(count - placed):
                    if i * count // cols + j < count:
                        result.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
                        placed += 1
                        if placed >= count:
                            break
            while len(result) < count:
                result.append((0.5, 0.5, 0.0, 0.0))
        
        memo[key] = result
        return result
    
    return fill_rectangle(1.0, 1.0, n, 3)
