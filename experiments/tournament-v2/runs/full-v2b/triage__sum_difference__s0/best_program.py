import math
import time
from itertools import product

def score_set(a):
    a = set(a)
    M = len(a)
    if M < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / M) / 100

def generate_digit_restricted(A_base, B_idx_sum, sum_val):
    """Generate numbers where a base-specific digit is restricted by sum_val.
    
    A_base = tuple of base and digit position to restrict.
    """
    result = []
    for coeffs in product(range(A_base[0]), repeat=A_base[1]):
        num = sum(coeffs[i] * (A_base[0] ** i) for i in range(len(coeffs)))
        digit_sum = sum(coeffs)
        if sum_val not in range(len(A_base[0])):
            continue
        if digit_sum % A_base[0] == sum_val:
            result.append(num)
    return result

def generate_lvl_set(base, num_digits, digit_cons):
    """Generate level sets using digit constraints.
    
    For each digit position, the sum of digits in each block is constrained.
    """
    total_options = base ** num_digits
    result = []
    for coeffs in product(range(base), repeat=num_digits):
        val = sum(coeffs[i] * (base ** i) for i in range(num_digits))
        digit_sums = [sum(coeffs[i*base:(i+1)*base]) for i in range(base)]  # simplified
        if any((s % base == digit_cons[s % base] for s in digit_sums)):
            result.append(val)
    return result

def generate_good_set(n, base=4):
    """Generate a set using construction related to sum-difference ratios."""
    # Construct: A = { i + j*n for i in I, j in J }
    # I controls sum size (make I large)
    # J controls difference size (make J large)
    I_size = 100
    J_size = 50
    
    I = list(range(I_size))
    n = 400  # multiplier spacing
    
    all_sums = []
    for i in I:
        for j in range(J_size):
            all_sums.append(i + j * n)
    
    return set(all_sums)

def construct_via_base(n, digits, choices_per_digit):
    """Construct using product of choices, carefully spaced."""
    A = []
    for coeffs in product(choices_per_digit, repeat=digits):
        val = sum(c * (n ** i) for i, c in enumerate(coeffs))
        A.append(val)
    return A

def generate_optimal_set(base, digit_sum_set, num_digits, min_digits, max_digits):
    """Generate sets using digit sum restriction with variable length."""
    results = []
    for d in range(min_digits, max_digits + 1):
        A = []
        for coeffs in product(range(base), repeat=d):
            if sum(coeffs) in digit_sum_set:
                val = sum(c * (base ** i) for i, c in enumerate(coeffs))
                A.append(val)
        if len(A) > 0:
            results.append(A)
    return results

def main_solve():
    deadline = time.time() + 110
    
    best_A = None
    best_score = 0.0
    
    # Strategy: Use structured sets with controlled digit sums
    # The construction from research uses Z_n^k with restricted digit sums
    
    # Try different configurations
    configurations = [
        # (base, digit_sum_set, min_digits, max_digits)
        (5, {2}, 4, 8),
        (5, {3}, 4, 8),
        (7, {4}, 4, 8),
        (11, {5}, 3, 8),
        (7, {3,4,5}, 5, 7),
        (9, {3,6}, 5, 9),
        (4, {1}, 5, 10),
    ]
    
    for base, digit_sum_set, min_d, max_d in configurations:
        if time.time() > deadline - 30:
            break
        
        A = []
        for d in range(min_d, max_d + 1):
            for coeffs in product(range(base), repeat=d):
                s = sum(coeffs)
                if s in digit_sum_set:
                    val = sum(c * (base ** i) for i, c in enumerate(coeffs))
                    A.append(val)
        
        if not A or len(A) < 2:
            continue
        
        # Filter to get reasonable size
        A = sorted(set(A))
        if len(A) > 4000:
            A = A[:4000]
        if len(A) < 10:
            continue
        
        score = score_set(A)
        if score > best_score:
            best_score = score
            best_A = A[:]
    
    # Additional construction: dual-sum approach
    if time.time() < deadline - 20:
        best_dual = []
        best_dual_score = 0.0
        
        # Try different multiplier spacings
        for spacing in [20, 50, 100, 200, 400, 800]:
            I_size = 60
            J_size = 60
            A = []
            for i in range(I_size):
                for j in range(J_size):
                    val = i + j * spacing
                    A.append(val)
            A = sorted(set(A))
            if len(A) < 2:
                continue
            
            score = score_set(A)
            if score > best_dual_score:
                best_dual_score = score
                best_dual = A[:]
        
        if best_dual_score > best_score:
            best_score = best_dual_score
            best_A = best_dual
    
    # Randomized search as fallback
    if time.time() < deadline - 15 and best_A is None:
        for _ in range(5):
            A = set()
            for _ in range(1000):
                base = random.randint(3, 7)
                d_sum = random.randint(1, base - 1)
                for i in range(5):
                    val = random.randint(-10000000000000, 10000000000000)
                    if val % (base ** i) != d_sum:
                        continue
                    A.add(val)
            
            if len(A) > 40:
                score = score_set(list(A))
                if score > best_score:
                    best_score = score
                    best_A = sorted(A)
    
    return sorted(set(best_A))[:4000] if best_A else [] if best_A else best_dual

def solve():
    deadline = time.time() + 110
    
    best_A = None
    best_score = 0.0
    
    # Primary: Digit-sum restricted construction
    configs = [
        (5, {2}, 4, 8),
        (5, {1,2}, 4, 8),
        (5, {1,2,3}, 5, 8),
        (7, {3}, 4, 8),
        (7, {2,3,4}, 4, 8),
        (7, {4,5}, 5, 7),
        (9, {3,6}, 5, 6),
        (11, {5}, 3, 8),
        (13, {6}, 4, 7),
        (3, {1}, 6, 9),
        (4, {2}, 5, 7),
        (6, {2,4}, 5, 7),
        (8, {4}, 5, 8),
    ]
    
    for base, digit_sums, min_d, max_d in configs:
        if time.time() > deadline - 25:
            break
        
        A = []
        for d in range(min_d, max_d + 1):
            for coeffs in product(range(base), repeat=d):
                s = sum(coeffs)
                if s in digit_sums:
                    val = sum(c * (base ** i) for i, c in enumerate(coeffs))
                    A.append(val)
        
        if not A:
            continue
        
        A = sorted(set(A))
        if len(A) > 4000:
            A = A[:4000]
        if len(A) < 15:
            continue
        
        s = score_set(A)
        if s > best_score:
            best_score = s
            best_A = A[:]
    
    # Secondary: Base-product construction with spacing
    if time.time() < deadline - 15:
        best_alt = []
        best_alt_score = 0.0
        
        for spacing in [100, 250, 500, 1000, 2000, 5000, 10000]:
            base = 4
            I_size = 50
            J_size = 50
            
            A = set()
            for i in range(I_size):
                for j in range(J_size):
                    A.add(i + j * spacing)
            
            A = sorted(A)
            if len(A) < 2:
                continue
            
            score = score_set(A)
            if score > best_alt_score:
                best_alt_score = score
                best_alt = A[:]
        
        if best_alt_score > best_score:
            best_score = best_alt_score
            best_A = best_alt
    
    # Tertiary: Digging deeper with more configs
    if time.time() < deadline - 5 and best_A is not None:
        # Try refined digit restrictions
        refined_configs = [
            (5, {2, 7}, 5, 7),
            (7, {3, 4, 5}, 5, 6),
            (9, {4, 13}, 5, 7),
            (11, {5, 16}, 4, 6),
            (3, {1, 2}, 5, 8),
            (5, {3, 4, 5}, 4, 6),
        ]
        
        for base, digit_sums, min_d, max_d in refined_configs:
            if time.time() > deadline - 3:
                break
            
            A = []
            for d in range(min_d, max_d + 1):
                for coeffs in product(range(base), repeat=d):
                    s = sum(coeffs)
                    if s in digit_sums:
                        val = sum(c * (base ** i) for i, c in enumerate(coeffs))
                        A.append(val)
            
            if not A:
                continue
            
            A = sorted(set(A))
            if len(A) > 4000:
                A = A[:4000]
            if len(A) < 15:
                continue
            
            score = score_set(A)
            if score > best_score:
                best_score = score
                best_A = A[:]
    
    return sorted(set(best_A))[:4000] if best_A else []
