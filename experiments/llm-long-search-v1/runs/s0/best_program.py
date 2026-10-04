# EVOLVE-BLOCK-START
"""Best fit with a residual-usability tie-break based on a running mean and a
histogram of seen item sizes (to nudge residuals toward frequently reusable sizes)."""
import numpy as np

_mean = 40.0
_count = 0
# Histogram of seen item sizes (1..100), used to reward residuals that match
# a common leftover size.
_hist = np.zeros(101, dtype=np.float64)


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    global _mean, _count, _hist

    # Update running mean and histogram of past items (before scoring this one).
    _mean = (_mean * _count + item) / (_count + 1)
    _count += 1
    _hist[item] += 1.0

    residual = bins - item  # remaining capacity after placing the item here

    # Best-fit tightness: prefer smaller residual.
    tightness = -residual.astype(np.float64)

    # Penalize residuals that are positive but smaller than a typical item:
    # such slivers are effectively wasted capacity.
    m = _mean
    sliver = (residual > 0) & (residual < m)
    penalty = np.where(sliver, (m - residual) * 2.0, 0.0)

    # Small bonus for very tight fits (residual 0) to strongly prefer exact fills.
    exact = (residual == 0).astype(np.float64) * 5.0

    # Data-driven complement bonus: reward residuals that equal the most
    # frequently seen item size so far, since such a leftover is the size most
    # likely to be reusable by a future item.
    r = residual
    valid = r >= 1
    if _count > 0:
        modal = int(np.argmax(_hist[1:])) + 1
        match = (valid & (r == modal)).astype(np.float64)
    else:
        match = np.zeros_like(r, dtype=np.float64)
    complement = match * 3.0

    # Waste-aware term: a residual that is just below the mean item size will
    # likely never be reused and is effectively lost capacity, so add a mild
    # extra penalty scaled by how close it is to the mean (larger residual =
    # more recoverable, smaller residual = more dead).
    near_full = (residual > 0) & (residual < m)
    waste = np.where(near_full, (1.0 - residual / m) * 1.0, 0.0)

    return tightness - penalty + exact + complement - waste
# EVOLVE-BLOCK-END
