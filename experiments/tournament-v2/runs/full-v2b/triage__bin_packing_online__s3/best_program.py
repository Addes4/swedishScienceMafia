# EVOLVE-BLOCK-START
"""Regret-weighted best-fit with an adaptive reserve floor.

The core ranking is a linear blend of two quantities:

1. `slack = residual_capacity - item`  -- how much room is left in the chosen
   bin after placing the item.  Preferring small slack is classic best fit.

2. `regret = q90(residual_capacity) - residual_capacity`  -- how far this bin's
   remaining capacity sits below the 90th percentile of all currently open bins.
   A large positive regret means the bin is comparatively full (close to the
   historically "full enough" region), so filling it further keeps the pool of
   genuinely empty bins intact for future large arrivals.  A negative regret
   means the bin is unusually empty: repeatedly dumping small items there would
   waste a valuable large slot, so such bins get a weaker score.

The blend `-slack + w * regret` therefore actively pulls the most-empty bins
down toward the "full enough" band while never cheating a nearly-full bin out
of a small item (slack keeps the fit tight).  The weight `w` and a soft
large-item floor are tuned from the observed large-item rate, all online.
"""
import numpy as np


_state = {
    "count": 0,
    "large": 0,
    "w": 0.9,          # regret weight, adapted online
    "floor": 58.0,     # size above which we shift to "roomy bin" mode
}


def priority(item, bins):
    st = _state
    st["count"] += 1

    if item >= 60:
        st["large"] += 1

    n = st["count"]
    f_large = st["large"] / n

    # If large items are rarer than ~10% we can be greedy; the more common they
    # are, the more we must protect empty bins (raise weight, lower floor so
    # medium items also get the room-preserving treatment).
    st["w"] += 0.01 * (0.10 - f_large)
    if st["w"] < 0.4:
        st["w"] = 0.4
    elif st["w"] > 1.6:
        st["w"] = 1.6

    st["floor"] += 0.05 * (0.10 - f_large)
    if st["floor"] < 50.0:
        st["floor"] = 50.0
    elif st["floor"] > 78.0:
        st["floor"] = 78.0

    cap = bins.astype(np.float64)
    slack = cap - item
    q90 = np.percentile(cap, 90.0)
    regret = q90 - cap  # positive => bin is comparatively full

    if item >= st["floor"]:
        # Large item: push it toward the emptiest viable bins so it lands in a
        # roomy slot; regret weighting already discourages fragmentation here,
        # so simply favour large residual capacity.
        return slack + 0.05 * regret

    return -slack + st["w"] * regret
# EVOLVE-BLOCK-END
