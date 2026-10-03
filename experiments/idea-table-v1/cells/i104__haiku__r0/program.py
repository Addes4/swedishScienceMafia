import math
from fractions import Fraction
from collections import defaultdict
import numpy as np
from scipy.special import comb


def solve(n):
    """Cross-entropy method search over size multisets with skyline packing."""
    
    # Erdős–Soifier baseline: squares of size 1/k for k in range [1, ceil(sqrt(n))]
    max_d = min(int(3 * math.sqrt(n)) + 1, n + 1)
    
    # State: probability distribution over number of squares of each size 1/d
    # We'll use integers from 1 to max_d
    num_sizes = max_d
    
    # CEM parameters
    num_samples = max(50, min(200, 2 * n))
    elite_ratio = 0.1
    num_elite = max(2, int(num_samples * elite_ratio))
    max_iterations = 30
    
    # Initialize: Erdős–Soifier seed
    seed_counts = np.zeros(num_sizes, dtype=int)
    for d in range(1, min(int(math.sqrt(n)) + 2, max_d + 1)):
        if d <= num_sizes:
            seed_counts[d - 1] = 1
    
    # Probability of including a square of size 1/d
    probs = np.ones(num_sizes) * 0.5
    for d in range(1, min(int(math.sqrt(n)) + 2, max_d + 1)):
        if d <= num_sizes:
            probs[d - 1] = 0.8
    probs /= probs.sum()
    
    best_objective = 0
    best_solution = None
    
    for iteration in range(max_iterations):
        samples = []
        objectives = []
        
        for _ in range(num_samples):
            # Sample multiset: Poisson-like with geometric decay
            counts = np.zeros(num_sizes, dtype=int)
            remaining = n
            
            for d in range(num_sizes):
                if remaining <= 0:
                    break
                # Sample number of squares of size 1/(d+1)
                max_of_this_size = min(remaining, n)
                p = probs[d]
                count = np.random.binomial(max_of_this_size, p * 0.1)
                counts[d] = min(count, remaining)
                remaining -= counts[d]
            
            # Fill remaining with smallest squares
            if remaining > 0 and num_sizes > 0:
                counts[-1] += remaining
            
            # Try to pack this multiset
            solution = pack_multiset(counts, n)
            
            if solution is not None and len(solution) == n:
                obj = sum(s[3] for s in solution)
                samples.append(counts)
                objectives.append(obj)
                
                if obj > best_objective:
                    best_objective = obj
                    best_solution = solution
        
        if not objectives:
            break
        
        # Keep elite samples
        if len(objectives) > 0:
            elite_indices = np.argsort(objectives)[-num_elite:]
            elite_samples = [samples[i] for i in elite_indices]
            
            # Update probability distribution
            elite_counts = np.sum([s for s in elite_samples], axis=0)
            elite_sum = elite_counts.sum()
            if elite_sum > 0:
                new_probs = elite_counts / elite_sum
                probs = 0.7 * new_probs + 0.3 * probs
                probs /= probs.sum()
    
    if best_solution is None:
        # Fallback to grid
        k = math.isqrt(n)
        side = 1.0 / k
        best_solution = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                        for i in range(k) for j in range(k)]
        best_solution += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_solution))
    
    return best_solution[:n]


def pack_multiset(counts, target_n):
    """Pack squares using skyline method on LCM board."""
    sizes = []
    for d in range(len(counts)):
        if counts[d] > 0:
            sizes.extend([1.0 / (d + 1)] * counts[d])
    
    if sum(counts) != target_n:
        # Pad with zeros
        sizes.extend([0.0] * (target_n - sum(counts)))
    
    sizes.sort(reverse=True)
    
    # Simple skyline packing
    placed = []
    skyline = {0.0: 0.0}  # x -> max_y at that x
    
    for side in sizes:
        if side < 1e-9:
            # Place at arbitrary location for zero-size squares
            placed.append((0.5, 0.5, 0.0, side))
            continue
        
        # Find leftmost position on skyline
        best_x = None
        best_y = None
        
        for x in sorted(skyline.keys()):
            y = skyline[x]
            if x + side <= 1.0 and y + side <= 1.0:
                best_x, best_y = x, y
                break
        
        if best_x is None:
            # Cannot pack
            return None
        
        placed.append((best_x + side / 2, best_y + side / 2, 0.0, side))
        
        # Update skyline
        new_skyline = {k: v for k, v in skyline.items() if k > best_x + side}
        new_skyline[best_x] = max(skyline.get(best_x, 0), best_y + side)
        new_skyline[best_x + side] = best_y
        skyline = new_skyline
    
    return placed if len(placed) == target_n else None
