# EVOLVE-BLOCK-START
"""Distribution-aware best fit with reservoir-based residual matching.

Items come from a fixed Weibull-shaped distribution (mean ~40). Pure best fit
minimizes the immediate remainder but leaves tiny unusable gaps. Here we:
  1. Strongly prefer exact fills (remainder 0).
  2. Otherwise prefer the post-placement remainder closest to a robust estimate
     of a typical future item size (an online reservoir median), so leftover
     gaps stay reusable.
"""
import numpy as np
import random

_state = {"n": 0.0, "mean": 40.0, "res": [], "seen": 0}


def priority(item, bins):
    """Return a priority for every bin in `bins`; highest wins, ties to first."""
    # Online estimates of the item size distribution.
    n = _state["n"]
    m = _state["mean"]
    _state["mean"] = (m * n + float(item)) / (n + 1.0)
    _state["n"] = n + 1.0

    # Reservoir sample of past item sizes to estimate a robust typical size.
    _state["seen"] += 1
    res = _state["res"]
    if len(res) < 128:
        res.append(float(item))
    else:
        j = random.randint(0, _state["seen"] - 1)
        if j < 128:
            res[j] = float(item)

    if res:
        target = float(np.median(res))
        if target < 1.0:
            target = 1.0
    else:
        target = _state["mean"]

    rem = (bins - item).astype(np.float64)  # capacity left after placing

    # Distance of the leftover gap from a typical future item size.
    gap_score = -np.abs(rem - target)

    # Strong bonus for exact fills (fully closed bins).
    exact_bonus = np.where(rem <= 0.0, 1000.0, 0.0)

    return gap_score + exact_bonus
# EVOLVE-BLOCK-END

