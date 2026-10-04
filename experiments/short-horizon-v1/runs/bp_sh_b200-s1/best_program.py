# EVOLVE-BLOCK-START
"""Best-fit packing enhanced with an online item-size histogram that rewards
leaving residuals which are likely to be exactly fillable by a future item."""
import numpy as np

# Module-level state: a coarse histogram of item sizes (1..100).
_HIST = np.zeros(101, dtype=np.float64)
_COUNT = 0


def priority(item, bins):
    """Rank bins; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    global _HIST, _COUNT

    residual = bins - item  # remaining capacity after placing the item here

    # ---- Primary: tight best-fit (residual near 0 is best). ----
    score = -residual.astype(np.float64)

    # ---- Dead-zone penalty: residuals in (0, 25) are likely stranded. ----
    dead = (residual > 0) & (residual < 25)
    score -= np.where(dead, 30.0, 0.0)

    # ---- Mild bonus for unused bins. ----
    empty = bins == 100
    score += np.where(empty, 5.0, 0.0)

    # ---- Distribution-aware friendliness bonus ----
    # Estimated probability that a residual equals some common item size, i.e.
    # that a future item could exactly fill the leftover.  Scale by the mean
    # item size so it never dominates best-fit.
    if _COUNT > 20:
        total = _HIST.sum()
        if total > 0:
            # probability mass of each residual as a future item size
            probs = np.zeros(residual.shape, dtype=np.float64)
            valid = residual >= 1
            idx = np.where(valid, residual, 0).astype(np.int64)
            idx = np.clip(idx, 0, 100)
            probs = _HIST[idx] / total
            probs = np.where(valid & (residual <= 100), probs, 0.0)
            # weight chosen to be a gentle nudge vs. best-fit's unit steps
            score += probs * 3.0

    # ---- Record this item into the histogram ----
    if 1 <= item <= 100:
        _HIST[item] += 1.0
        _COUNT += 1

    return score
# EVOLVE-BLOCK-END
