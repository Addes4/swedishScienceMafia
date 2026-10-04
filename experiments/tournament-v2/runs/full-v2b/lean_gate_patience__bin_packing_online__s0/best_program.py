# EVOLVE-BLOCK-START
"""Residue-utility best fit: blend tight-fit tightness with a penalty for leaving
uselessly small leftovers, using online item-size statistics and a reuse bonus."""
import numpy as np

_state = {
    "n": 0,
    "sum": 0.0,
    "cnt_small": 0,
}


def priority(item, bins):
    """Return a priority for every bin in `bins`; item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    # Online statistics over past items (never future ones).
    n = _state["n"]
    if n > 0:
        mean_item = _state["sum"] / n
        frac_small = _state["cnt_small"] / n
    else:
        mean_item = 40.0
        frac_small = 0.5
    _state["n"] = n + 1
    _state["sum"] += item
    if item <= 20:
        _state["cnt_small"] += 1

    # "Useful item size" threshold: leftovers below this are unlikely to fit a
    # typical future item usefully.  Blend the running mean with the small-item mass.
    useful = 0.5 * mean_item + 0.5 * (1.0 - frac_small) * 20.0
    # Keep within sane bounds.
    if useful < 8.0:
        useful = 8.0
    elif useful > 45.0:
        useful = 45.0

    bins_f = bins.astype(np.float64)
    leftover = bins_f - item  # capacity left after placing this item (>= 0)

    # Tight-fit tightness: smaller leftover is better, so negate it.
    tight = -leftover

    # Residue hazard: penalize leftovers that land strictly below `useful`
    # (but not exactly zero, which is a perfect fill and should be rewarded).
    is_zero = leftover <= 0.0
    unsafe = (leftover > 0.0) & (leftover < useful)
    hazard = unsafe.astype(np.float64) * (useful - leftover + 1.0)

    # Mild reuse bonus: strongly discourage opening brand-new bins.
    is_new = bins_f >= 100.0
    reuse_bonus = np.where(is_new, -6.0, 0.0)

    # Perfect fills get extra reward.
    perfect = np.where(is_zero, 5.0, 0.0)

    return tight - 1.5 * hazard + reuse_bonus + perfect
# EVOLVE-BLOCK-END
