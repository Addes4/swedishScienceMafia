# EVOLVE-BLOCK-START
"""Best fit with a "reusable residual" objective.

Exact fills are strongly preferred. Otherwise, prefer leaving a residual that
matches a recently-seen item size (so the next few arrivals can fill it exactly),
falling back toward a mild preference for residuals near the running mean.
"""
import numpy as np

_hist = np.zeros(101, dtype=np.float64)
_count = 0.0
_sum = 0.0
# Cached array of item sizes seen recently (weighted by recency via decay)
_seen = np.zeros(101, dtype=np.float64)


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _hist, _count, _sum, _seen
    _hist[item] += 1.0
    _count += 1.0
    _sum += item
    # Recency-weighted presence: decay all, then boost this item.
    _seen *= 0.999
    _seen[item] += 1.0

    residual = bins - item  # >= 0 for all bins shown
    res = residual.astype(np.float64)

    if _count > 0:
        mean_item = _sum / _count
    else:
        mean_item = 40.0

    # Distance to the closest recently-seen item size (0 if residual is an observed size).
    # Build distance-to-nearest-seen-size for each possible residual value 0..100.
    seen_present = _seen > 0.0
    # positions of seen sizes
    # distance from any residual r to nearest seen size
    # compute via cumulative approach
    idx = np.nonzero(seen_present)[0]
    if idx.size > 0:
        # For each residual value 0..100, min distance to a seen size.
        vals = np.arange(101, dtype=np.float64)
        d = np.abs(vals[:, None] - idx[None, :].astype(np.float64))
        nearest = d.min(axis=1)  # shape (101,)
    else:
        nearest = np.abs(np.arange(101, dtype=np.float64) - mean_item)

    # Score: closer to a reusable residual is better; exact fills dominant.
    score = -nearest[residual.astype(np.int64)]

    # Mild preference for residuals near the running mean as a fallback.
    score += -0.05 * np.abs(res - mean_item)

    # Strongly prefer exact fills.
    score += np.where(residual == 0, 1000.0, 0.0)

    return score
# EVOLVE-BLOCK-END
