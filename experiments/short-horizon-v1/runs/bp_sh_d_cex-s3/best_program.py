# EVOLVE-BLOCK-START
"""Distribution-aware best fit: keep large residuals for large items (Weibull mean ~40)."""
import numpy as np


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    residual = bins - item  # remaining capacity after placing the item

    # For large items, standard best fit (pack tightly).
    # For small items, avoid wasting big residuals by prefering to place into
    # bins that are already fairly full, leaving large empty bins available for
    # future large items. Use a soft monotone score toward fuller bins.
    if item >= 40:
        return -(residual)
    # Small item: favor bins with small residual (fuller bins get filled), but
    # with a mild preference to not create tiny unusable residuals (residual
    # below item-typical sizes) -- nudge away from residuals in [1, 15].
    score = -residual.astype(np.float64)
    awkward = (residual >= 1) & (residual <= 15)
    score[awkward] -= 2.0
    return score
# EVOLVE-BLOCK-END
