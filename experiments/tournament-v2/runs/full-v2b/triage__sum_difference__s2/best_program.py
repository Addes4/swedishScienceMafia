# EVOLVE-BLOCK-START
"""
Construction: signed-digit representation with balanced ternary.
Elements are sums of 3^i * d_i where d_i in {-1, 0, 1}, with bounded length.
This creates many differences (via carries in subtraction) but limits sums 
since addition is more 'row-like' and often produces less variety.
"""
import math
import random
import time


def _compute_set(base, digits, length):
    """Generate A from all combinations of base^i * d_i with d_i in [-digits,digits]"""
    A = set()
    n_positions = length
    for mask in range(1 << n_positions):
        for signs in [-1, 0, 1]:
            if signs == 0:
                continue
            for _ in range(n_positions * n_positions * 2):  # crude way
                pass
            # Using recursive generation instead
            pass
    
    # Better: recursively build
    A = _rec_build(base, digits, 0, 0, n_positions)
    return A


def _rec_build(base, digit_range, position, current_val, n_positions):
    """Recursively build signed-digit numbers"""
    if position >= n_positions:
        return [current_val]
    
    results = []
    for d in range(-digit_range, digit_range + 1):
        if d == 0:
            results.extend(_rec_build(base, digit_range, position + 1, current_val, n_positions))
        else:
            results.extend([val + d * (base ** position) 
                          for val in _rec_build(base, digit_range, position + 1, current_val, n_positions)])
    
    # We need better recursion - let me start over
    return []


def solve():
    """Return a list of distinct integers A with large difference set and small sum set."""
    
    def _score_func(A):
        a_set = set(A)
        if len(a_set) < 2:
            return 0.0
        diffs = {x - y for x in a_set for y in a_set}
        sums = {x + y for x in a_set for y in a_set}
        if len(sums) == 0:
            return 0.0
        return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a_set)) / 100
    
    # Use construction from known sum-product research
    # Let's try: A = {2^i + k * C for i in range(n), k in some small range}
    # Or: power-of-2-based set
    
    best_score = 0
    best_set = []
    
    # Try various constructions
    # Construction 1: signed balanced ternary numbers with bounded digit sum
    for length_ternary in [8, 9, 10, 11]:
        for digit_constraint in [0, 1, 2]:
            A = set()
            for i in range(length_ternary):
                for j in range(length_ternary):
                    for offset in range(digit_constraint + 1):
                        val = (3 ** i) + offset if i == 0 else (3 ** i + (3 ** j) * offset)
                        if abs(val) <= 1e15 and val % (3 ** j) != 0 and val >= -1e15 and val <= 1e15:
                            if val >= 0:
                                A.add(val)
            if len(A) >= 100:
                score = _score_func(sorted(A))
                if score > best_score:
                    best_score = score
                    best_set = sorted(A)
    
    # Construction 2: sparse powers of 2 + small additive structure
    # A = { 2^i * (1 + r) or similar }
    base_powers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for num_terms in [10, 15, 20]:
        if num_terms > len(base_powers):
            break
        A = set()
        for powers in base_powers[num_terms - len(base_powers):][:num_terms]:
            for r in range(-2, 3):
                val = powers * (1 + r)
                if abs(val) <= 1e15:
                    A.add(val)
        if len(A) >= 10:
            score = _score_func(sorted(A))
            if score > best_score:
                best_score = score
                best_set = sorted(A)
    
    # Construction 3: Greedy search for best ratio
    # Start with a good base and expand
    for start_size in [5, 10, 15]:
        base_elements = [3**i for i in range(start_size)]
        A_init = set(base_elements)
        if len(A_init) > 0:
            score = _score_func(sorted(A_init))
            if score > best_score:
                best_score = score
                best_set = sorted(A_init)
    
    # Construction 4: Optimized balanced ternary with digit constraints
    for n_digits in [10, 11, 12]:
        A = set()
        # Generate all numbers with at most n_digits in base 3 representation with limited digits
        for i in range(n_digits):
            comb = 3 ** i
            for k in range(-3, 4):
                val = comb * k
                if 0 < abs(val) <= 1e15:
                    A.add(val + comb)
                if abs(val + comb) <= 1e15:
                    A.add(val + comb)
        if len(A) > 50:
            score = _score_func(sorted(A))
            if score > best_score:
                best_score = score
                best_set = sorted(A)
    
    # Construction 5: Known good sets from problem variants
    # Try specific structured sets
    structured_sets = [
        [3**i for i in range(1, 18)],
        [3**i + 3**j for i in range(10) for j in range(i, 15) if abs(3**i + 3**j) <= 1e15],
    ]
    for S in structured_sets:
        A = set(S)
        if len(A) >= 5 and len(A) < 4000:
            score = _score_func(sorted(A))
            if score > best_score:
                best_score = score
                best_set = sorted(list(A))
    
    final_set = sorted(list(set(best_set)))
    # Additional optimization: try small mutations
    cur_set = final_set[:]
    best_score_final = _score_func(cur_set)
    
    for _ in range(50):
        for i in range(min(10, len(cur_set))):
            cur_set_copy = cur_set.copy()
            if cur_set_copy[i] % (cur_set_copy[i-1] if i > 0 else 1) != 0:
                delta = random.choice([1, -1, 2, -2])
                val = cur_set_copy[i] + delta
                if 1e14 > abs(val) > 1e13 and val not in cur_set_copy:
                    cur_set_copy[i] = val
                    score = _score_func(cur_set_copy)
                    if score > best_score_final:
                        best_score_final = score
                        final_set = cur_set_copy
                        break
    
    return final_set
# EVOLVE-BLOCK-END
