# EVOLVE-BLOCK-START
"""Target-residual fit: prefer bins whose leftover after placement is closest to a running mean."""
import numpy as np

_TARGET_SHORT = 30.0
_WARMUP = 35

_count = 0
_sum = 0.0


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _count, _sum

    leftover = bins - item

    # Adapt the target residual to the running mean item size; fall back to a fixed
    # short-stream target until enough items have been observed.
    if _count < _WARMUP:
        target = _TARGET_SHORT
    else:
        target = _sum / _count

    _count += 1
    _sum += item

    # Strongly reward near-perfect fits (small leftovers), otherwise steer toward the target residual.
    exact_bonus = np.where(leftover == 0, 1e6, 0.0)
    tight_bonus = np.maximum(0.0, 5.0 - leftover) * 1000.0
    return exact_bonus + tight_bonus - np.abs(leftover - target)
# EVOLVE-BLOCK-END

