# EVOLVE-BLOCK-START
"""Harmonic-flavored best fit: concentrate items into the fullest fitting bin."""
import numpy as np


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    # Use best fit as the base ranking, but bias toward bins that stay fullest after
    # placing the item, so we concentrate packing into fewer, tighter bins.
    remaining = bins - item
    best_fit = -remaining  # higher is tighter fit
    # Penalize leaving small leftover residuals (hard-to-reuse capacity).
    # Residual <= some threshold is considered waste.
    waste = np.where((remaining > 0) & (remaining <= 19), remaining, 0)
    return best_fit.astype(np.float64) - 2.0 * waste
# EVOLVE-BLOCK-END
