"""Structured construction using simplex lattice points with Freiman-isomorphic encoding."""
import math
import time


def _score(a):
    """Compute the score: log|A - A| / log|A + A| + bonus."""
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def generate_simplex_points(d, k):
    """Generate all lattice points in {x ∈ Z_≥0^d : Σx_i ≤ k}."""
    if d == 0:
        return [[]] if k >= 0 else []
    if d == 1:
        return [[i] for i in range(k + 1)]
    
    points = []
    
    def backtrack(point, remaining_sum, remaining_dims):
        if remaining_dims == 1:
            points.append(point + [remaining_sum])
            return
        for i in range(remaining_sum + 1):
            backtrack(point + [i], remaining_sum - i, remaining_dims - 1)
    
    backtrack([], k, d)
    return points


def encode_simplex(points, k):
    """Encode simplex lattice points using base B = 2k+1 for Freiman-isomorphism."""
    B = 2 * k + 1
    encoded = []
    for point in points:
        value = 0
        for i, x in enumerate(point):
            value += x * (B ** i)
        encoded.append(value)
    return encoded


def solve():
    """Generate sets from simplex lattice points and return the best."""
    best_set = [0]
    best_score = 0.0
    deadline = time.time() + 115
    
    # We'll enumerate (d, k) pairs such that the number of simplex points is manageable
    # Number of points in simplex: C(d+k, d) = (d+k)! / (d! * k!)
    
    max_size = 4000
    
    # Try different dimensions and levels
    for d in range(1, 25):
        if time.time() >= deadline:
            break
        
        for k in range(0, 100):
            if time.time() >= deadline:
                break
            
            # Estimate number of points: C(d+k, d)
            # For large values, this grows quickly
            points = generate_simplex_points(d, k)
            num_points = len(points)
            
            if num_points > max_size:
                break
            
            if num_points < 2:
                continue
            
            # Encode the points
            encoded = encode_simplex(points, k)
            
            # Compute score
            score = _score(encoded)
            
            if score > best_score:
                best_score = score
                best_set = encoded[:]
    
    return sorted(set(best_set))
