# EVOLVE-BLOCK-START
"""Best-fit with residual-aware tie-break to avoid tiny unusable slivers."""
import numpy as np

_state = {"min_item": 100}


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    global _state
    if item < _state["min_item"]:
        _state["min_item"] = item

    residual = bins - item  # remaining capacity after placing the item

    # Best-fit primary: tighter fit (smaller residual) is better.
    primary = -residual.astype(np.float64)

    # Sliver penalty: residuals in [1, min_item-1) can never be reused.
    # Also give a slight bonus to exact fills (residual 0).
    sliver_thresh = _state["min_item"]
    sliver = (residual > 0) & (residual < sliver_thresh)
    penalty = np.where(sliver, 1.0, 0.0)
    bonus = np.where(residual == 0, 0.5, 0.0)

    # Scale primary so the small secondary terms only matter near ties.
    return primary - penalty + bonus
# EVOLVE-BLOCK-END
