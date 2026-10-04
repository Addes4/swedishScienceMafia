# EVOLVE-BLOCK-START
"""Best fit with an online penalty for stranding improbable small residuals."""
import numpy as np


# Online histogram of item sizes seen so far (updated once per call).
_HIST = np.zeros(101, dtype=np.float64)   # counts for sizes 1..100
_TOTAL = 0.0
_RECOMPUTE_EVERY = 50
_CACHED_PROB = np.zeros(101, dtype=np.float64)


def _refresh_prob():
    global _CACHED_PROB
    if _TOTAL <= 0:
        _CACHED_PROB = np.zeros(101, dtype=np.float64)
        return
    p = _HIST / _TOTAL
    # Smooth a bit and drop the empty-size probability (size 0 never arrives).
    _CACHED_PROB = p


def priority(item, bins):
    """Return a priority for every fitting bin; highest score wins (first on ties).

    Base is best fit (smallest post-placement residual).  We add a penalty when the
    residual r is a size that the empirical item distribution almost never produces,
    since such a gap is likely to be stranded forever.
    """
    global _TOTAL, _RECOMPUTE_EVERY

    # Record this item (post-decision, but item is given before we rank).
    _HIST[item] += 1.0
    _TOTAL += 1.0
    if int(_TOTAL) % _RECOMPUTE_EVERY == 0:
        _refresh_prob()

    residual = bins - item  # >= 0 for all shown bins
    base = -residual.astype(np.float64)

    # Probability that some future item exactly fills the residual.
    # Use the empirical pmf of the residual size.
    prob = _CACHED_PROB[residual]

    # Penalize residuals that are unlikely to be reused by a future item.
    # Scale so it can overturn close best-fit choices but not dominate exact fits.
    penalty = 60.0 * (1.0 - prob)

    return base - penalty
# EVOLVE-BLOCK-END
