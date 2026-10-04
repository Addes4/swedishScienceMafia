# EVOLVE-BLOCK-START
"""Best fit with adaptive modulo-consolidation diversion.

Pure best fit leaves many small slivers for this distribution. On some steps we
divert to the bin whose residual after placement is closest to a multiple of
the mean item size (~40), which consolidates leftovers into fuller slots.
Best-fit stays dominant otherwise. Diversion fires only for smaller items
(where slivers form) and uses a fractional-phase period so consolidation is
spread evenly rather than in bursts.
"""
import numpy as np

_state = {"n": 0}
_MEAN = 40.0


def priority(item, bins):
    """Return a priority for every bin; highest score wins (first on ties)."""
    n = _state["n"]
    _state["n"] = n + 1

    # Base: best-fit priority (tighter residual -> higher score).
    better_fit = -(bins - item)

    # Divert mainly when small items are arriving (these create slivers),
    # using a fractional phase to spread consolidation evenly.
    if item < 60 and (n % 3 == 0):
        resid = bins - item  # remaining after placing (>= 0)
        m = np.round(resid / _MEAN)
        dist = np.abs(resid - m * _MEAN)
        return -dist * 100.0 + better_fit

    return better_fit
# EVOLVE-BLOCK-END
