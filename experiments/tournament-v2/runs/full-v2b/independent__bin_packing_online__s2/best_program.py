import numpy as np

# Global state for online learning
counts = np.zeros(101, dtype=np.int64)
total = 0

def priority(item, bins):
    global total, counts
    
    # Update histogram with the current item
    total += 1
    counts[item] += 1
    
    # Compute the 10th percentile of item sizes seen so far
    target = 0.1 * total
    cum = 0
    T = 10  # default
    for s in range(1, 101):
        cum += counts[s]
        if cum >= target:
            T = s
            break
    T = max(1, T)
    
    # Compute new residual after placing the item in each bin
    new_res = bins - item
    
    # Base score: best fit (prefer smaller new residual)
    # We'll use float for scores
    scores = -new_res.astype(np.float64)
    
    # Penalize residuals that are small but not zero (unlikely to be filled later)
    small = (new_res > 0) & (new_res < T)
    scores[small] = -1000.0 - new_res[small]
    
    # Exact fill gets the highest priority
    exact = (new_res == 0)
    scores[exact] = 0.0
    
    # Penalize empty bins so we only use them when necessary
    empty = (bins == 100)
    scores[empty] -= 1000.0
    
    return scores
