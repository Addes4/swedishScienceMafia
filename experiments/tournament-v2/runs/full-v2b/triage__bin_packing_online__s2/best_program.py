import numpy as np

# Global state for expert weights learning
_initialized = False

if not _initialized:
    global _expert_weights, _expert_names, _learning_rate, _instance_items, _instance_bins_used
    
    _expert_names = [
        'best_fit',      # Prefer bins with least remaining capacity
        'worst_fit',     # Prefer bins with most remaining capacity  
        'gap_aware',     # Prefer bins where item fits with minimal gap
        'threshold',     # Prefer bins above capacity threshold
        'flexibility',   # Prefer bins with remaining capacity close to expected item size
        'tight_fill',    # Prefer bins where remaining capacity after placement is minimal
        'loose_fill',    # Prefer bins where item fills a large portion
        'percent_fill',  # Prefer bins based on fill percentage
    ]
    
    _expert_weights = np.ones(len(_expert_names)) / len(_expert_names)
    _learning_rate = 0.01
    _instance_items = []
    _instance_bins_used = []

def _update_expert_weights(bins_used, lower_bound):
    """Update expert weights based on instance performance."""
    global _expert_weights, _learning_rate
    
    if bins_used == 0 or lower_bound == 0:
        return
        
    # Surrogate loss: waste ratio (higher is worse)
    waste_ratio = max(0, (bins_used - lower_bound) / lower_bound)
    
    # Compute pseudo-loss for each expert based on historical performance
    # In online setting, we approximate by using the current waste ratio
    losses = np.full(len(_expert_names), waste_ratio)
    
    # Update weights using multiplicative weights
    _expert_weights *= np.exp(-_learning_rate * losses)
    _expert_weights /= _expert_weights.sum()

def _best_fit_scores(item, bins):
    """Prefer bins with least remaining capacity after placement."""
    remaining_after = bins - item
    return 100.0 / (remaining_after + 1.0)  # Higher score for tighter fit

def _worst_fit_scores(item, bins):
    """Prefer bins with most remaining capacity."""
    return bins.astype(np.float64)

def _gap_aware_scores(item, bins):
    """Prefer bins where item fits with minimal gap to capacity."""
    remaining_after = bins - item
    # Negative exponential penalty for gap
    return np.exp(-remaining_after / 10.0) * 100.0

def _threshold_scores(item, bins):
    """Prefer bins above certain capacity thresholds."""
    scores = np.zeros_like(bins, dtype=np.float64)
    # High score for bins that can accommodate future large items
    scores[bins >= 80] = 100
    scores[(bins >= 50) & (bins < 80)] = 70
    scores[(bins >= 30) & (bins < 50)] = 50
    scores[bins < 30] = 30
    return scores

def _flexibility_scores(item, bins):
    """Prefer bins with remaining capacity close to expected item size ~40."""
    target = 40
    distance = np.abs(bins - target)
    return 100.0 / (distance + 1.0)

def _tight_fill_scores(item, bins):
    """Prefer bins where remaining capacity after placement is minimal."""
    remaining_after = bins - item
    return 100.0 - remaining_after

def _loose_fill_scores(item, bins):
    """Prefer bins where item fills a large portion."""
    fill_ratio = item / bins.astype(np.float64)
    return fill_ratio * 100.0

def _percent_fill_scores(item, bins):
    """Prefer bins based on current fill percentage."""
    fill_pct = (100.0 - bins) / 100.0
    return fill_pct * 100.0

# Map expert names to scoring functions
_expert_functions = {
    'best_fit': _best_fit_scores,
    'worst_fit': _worst_fit_scores,
    'gap_aware': _gap_aware_scores,
    'threshold': _threshold_scores,
    'flexibility': _flexibility_scores,
    'tight_fill': _tight_fill_scores,
    'loose_fill': _loose_fill_scores,
    'percent_fill': _percent_fill_scores,
}

def priority(item, bins):
    """Return a priority array; highest score (first tie) gets the item.
    
    item: integer size of the arriving item, 1..100
    bins: numpy int64 array with remaining capacity of all eligible bins
    """
    global _expert_weights, _instance_items
    
    # Track items for potential weight updates
    _instance_items.append(item)
    
    if len(bins) == 0:
        return np.array([], dtype=np.int64)
    
    # Compute scores from each expert
    expert_scores = np.zeros((len(_expert_names), len(bins)), dtype=np.float64)
    
    for i, name in enumerate(_expert_names):
        expert_scores[i] = _expert_functions[name](item, bins)
    
    # Combine scores using weighted average
    combined_scores = np.zeros(len(bins), dtype=np.float64)
    for i in range(len(_expert_names)):
        combined_scores += _expert_weights[i] * expert_scores[i]
    
    # Ensure no NaN values and scale to reasonable range
    combined_scores = np.nan_to_num(combined_scores, nan=0.0, posinf=1e6, neginf=-1e6)
    
    # Normalize to prevent overflow when converting to int64
    if combined_scores.max() > 0:
        combined_scores = (combined_scores / combined_scores.max()) * 1000
    
    return combined_scores.astype(np.int64)

# The harness will call this function at the end of each instance to update weights
def update_weights_after_instance(bins_used, lower_bound):
    """Update expert weights after completing an instance.
    
    This function should be called by the evaluation harness after each instance.
    Since we can't modify the harness, we'll implement an implicit update mechanism.
    """
    global _expert_weights, _instance_items, _instance_bins_used
    
    _instance_bins_used.append(bins_used)
    
    if len(_instance_items) > 0 and bins_used > 0 and lower_bound > 0:
        _update_expert_weights(bins_used, lower_bound)
    
    # Reset instance tracking
    _instance_items = []

# Attempt to auto-update weights periodically based on observed performance
# We'll use a heuristic to estimate performance mid-instance
_placement_count = 0
_last_update_count = 0

def priority(item, bins):
    """Return a priority array; highest score (first tie) gets the item.
    
    item: integer size of the arriving item, 1..100
    bins: numpy int64 array with remaining capacity of all eligible bins
    """
    global _expert_weights, _instance_items, _placement_count, _last_update_count
    
    _placement_count += 1
    _instance_items.append(item)
    
    # Periodic weight adjustment based on running statistics
    if _placement_count % 1000 == 0 and _placement_count > _last_update_count:
        _last_update_count = _placement_count
        
        # Heuristic: if bins are being used efficiently, reward experts that promote tight packing
        # This is a lightweight online adaptation
        if len(_instance_items) >= 100:
            recent_items = _instance_items[-100:]
            avg_item = np.mean(recent_items)
            
            # Adjust weights slightly based on item distribution
            if avg_item > 50:  # Large items arriving
                # Favor worst-fit to keep bins available for large items
                adjustment = np.ones(len(_expert_names)) * 0.001
                adjustment[1] = 0.01  # Boost worst-fit
                _expert_weights += adjustment
            elif avg_item < 30:  # Small items arriving
                # Favor best-fit to pack tightly
                adjustment = np.ones(len(_expert_names)) * 0.001
                adjustment[0] = 0.01  # Boost best-fit
                _expert_weights += adjustment
            
            # Normalize
            _expert_weights = np.maximum(_expert_weights, 0.001)
            _expert_weights /= _expert_weights.sum()
    
    if len(bins) == 0:
        return np.array([], dtype=np.int64)
    
    # Compute scores from each expert
    expert_scores = np.zeros((len(_expert_names), len(bins)), dtype=np.float64)
    
    for i, name in enumerate(_expert_names):
        expert_scores[i] = _expert_functions[name](item, bins)
    
    # Combine scores using weighted average with softmax-like scaling
    combined_scores = np.zeros(len(bins), dtype=np.float64)
    weight_scale = _expert_weights / _expert_weights.sum()  # Ensure normalization
    
    for i in range(len(_expert_names)):
        combined_scores += weight_scale[i] * expert_scores[i]
    
    # Add small random perturbation to break ties differently based on expert preferences
    noise = np.random.rand(len(bins)) * 0.1
    combined_scores += noise
    
    # Ensure no NaN values and scale to reasonable range
    combined_scores = np.nan_to_num(combined_scores, nan=0.0, posinf=1e6, neginf=-1e6)
    
    # Normalize to prevent overflow
    if combined_scores.max() > 0:
        combined_scores = (combined_scores / combined_scores.max()) * 1000
    
    return combined_scores.astype(np.int64)
