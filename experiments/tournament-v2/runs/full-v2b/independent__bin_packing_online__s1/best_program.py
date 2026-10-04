import numpy as np

# We maintain an online estimate of item size distribution to score candidate residual gaps.
# The idea: placing into a bin leaves a residual capacity r = bins[i] - item.
# A residual r is "good" if it is close to some item size (so it will likely be filled soon),
# and "bad" if it is a size unlikely to be matched (wasted space).
# We score bins by how likely their residual will be used, approximating best-fit with lookahead
# via a histogram of observed item sizes.

_count = None
_value = None

def _init():
    global _count, _value
    # Histogram over sizes 1..100, smoothed prior so early decisions are sane.
    _count = np.ones(101, dtype=np.float64)
    _value = np.arange(101, dtype=np.float64)


def _match_prob(r):
    """Estimate probability that a future item can fit exactly or nearly fill a residual r."""
    # Probability mass of observed sizes in a small window around r, scaled by total.
    if r <= 0:
        return 0.0
    r = int(r)
    lo = max(1, r - 2)
    hi = min(100, r + 2)
    window = _count[lo:hi + 1].sum()
    total = _count[1:101].sum()
    return window / total


def priority(item, bins):
    global _count, _value
    if _count is None:
        _init()

    # Record this item to update distribution (do it here so we use past items only).
    item_int = int(item)
    if 1 <= item_int <= 100:
        _count[item_int] += 1.0

    n = bins.shape[0]
    scores = np.empty(n, dtype=np.float64)

    # Precompute match probability for each possible residual 0..100 once.
    residuals = bins - item_int
    # clip residuals
    residuals_clipped = np.clip(residuals, 0, 100).astype(np.int64)

    total = _count[1:101].sum()
    # Build fixed-size probability array for residuals
    prob_cache = np.zeros(101, dtype=np.float64)
    for r in range(0, 101):
        if r == 0:
            prob_cache[r] = 1e9  # perfect fit, huge reward
        else:
            lo = max(1, r - 2)
            hi = min(100, r + 2)
            prob_cache[r] = _count[lo:hi + 1].sum() / total

    # Score: favor residuals that are likely to be filled by future items.
    # Also favor smaller residuals (waste less) when match probabilities are similar.
    # Use bin index implicitly via tiny ordering-preserving perturbation? 
    # Better to keep determinism based on bin index by using stable tie-break: 
    # we add a tiny negative offset proportional to index, but that fights score ordering.
    # Instead rely on numpy argmax picking first max; we return scores directly.
    probs = prob_cache[residuals_clipped]
    # Small residual preference: subtract normalized residual
    scores = probs * 1e6 - residuals_clipped.astype(np.float64) * 1.0

    return scores
