# EVOLVE-BLOCK-START
"""Best fit with a small penalty for leaving unusable tiny residuals."""
import numpy as np


def priority(item, bins):
    """Rank bins by best fit, but penalize residuals too small to be useful.

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in.
    """
    residual = bins - item  # >= 0 for all shown bins

    # Base best-fit preference: smaller residual is better.
    score = -residual.astype(np.float64)

    # Tiny nonzero residuals are likely stranded capacity; add a mild penalty so that
    # when a slightly looser bin is available, we prefer it (reduces fragmentation).
    # A residual of 0 (exact fill) is ideal and must NOT be penalized.
    tiny = (residual > 0) & (residual < 5)
    score -= tiny.astype(np.float64) * 1.5

    return score
# EVOLVE-BLOCK-END
