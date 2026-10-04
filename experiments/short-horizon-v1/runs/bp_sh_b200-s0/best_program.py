# EVOLVE-BLOCK-START
"""Best-fit primary, with item-size-scaled empty-bin promotion for large items
and a stateful consolidation nudge for typical-size items."""
import numpy as np

# Per-stream running statistics (reset when a fresh stream starts).
_state = {"n": 0, "sum": 0.0, "last_size": -1}


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    # Update running statistics; detect a new stream by a capacity jump to 100
    # combined with a small item after a large previous item is unreliable, so
    # just keep a soft running mean that adapts across the stream.
    _state["n"] += 1
    _state["sum"] += item
    mean_item = _state["sum"] / _state["n"]

    rem = bins - item  # leftover capacity after placing the item
    # Primary criterion: best fit (prefer smallest leftover).
    score = -rem.astype(np.float64)

    is_empty = bins == 100

    # Absolute wasteful-gap test: a used bin that would leave a residual larger
    # than the item itself is a poor fit.
    wasteful = (rem > item) & (~is_empty)
    score += wasteful.astype(np.float64) * (item + 1)

    # Item-size-scaled empty-bin promotion: reserve a fresh bin mainly for
    # large items, while letting smaller items consolidate into used bins.
    scale = (item - 50.0) / 50.0  # <=0 for items up to 50, up to 1.0 at 100
    if scale > 0:
        bonus = scale * (item + 1) * is_empty.astype(np.float64)
        score += bonus

    # Consolidation nudge: for typical-size items, prefer a used bin whose
    # residual stays useful (>= half the running mean item size) over opening a
    # fresh bin, cutting needless bin openings without harming large items.
    if scale <= 0:
        half_mean = 0.5 * mean_item
        useful_used = (rem >= half_mean) & (rem <= item) & (~is_empty)
        score += 0.5 * (item + 1) * useful_used.astype(np.float64)

    return score
# EVOLVE-BLOCK-END
