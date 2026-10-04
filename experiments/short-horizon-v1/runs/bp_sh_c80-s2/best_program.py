# EVOLVE-BLOCK-START
"""Target-residual best fit with a distribution-derived sweet spot."""
import numpy as np

_TOTAL = 0
_COUNT = 0
_SQ = 0.0


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _TOTAL, _COUNT, _SQ

    _TOTAL += item
    _COUNT += 1
    _SQ += float(item) * item
    mean = _TOTAL / _COUNT
    var = max(_SQ / _COUNT - mean * mean, 0.0)
    sd = var ** 0.5

    residual = bins - item

    if _COUNT >= 30:
        # Target residual: aim to leave a gap a typical item can fill.  A slightly
        # sub-mean target reduces large residual waste for skewed (Weibull) sizes.
        target = 0.90 * mean + 0.15 * sd
    else:
        target = 38.0

    score = -np.abs(residual - target)

    # Gentle completion bonus: reward small residuals, but with a softer slope so
    # medium bins aren't starved of items that would land near the sweet spot.
    tight = np.where(residual <= 10, 4e4 - residual * 2e3, 0.0)
    return score + tight
# EVOLVE-BLOCK-END
