# EVOLVE-BLOCK-START
"""Best fit biased so that the residual left behind is likely reusable."""
import numpy as np

_state = {"sizes": []}


def priority(item, bins):
    sizes = _state["sizes"]
    sizes.append(int(item))
    if len(sizes) > 2000:
        del sizes[:1000]

    # Estimate the typical item size band from observed history.
    if len(sizes) >= 20:
        arr = np.array(sizes, dtype=np.float64)
        mu = arr.mean()
        sd = arr.std()
    else:
        mu = 40.0
        sd = 20.0

    tmp = int(mu)
    if tmp < 1:
        tmp = 1
    if tmp > 100:
        tmp = 100
    band = tmp
    # Tolerance around the typical size: residual in [band - tol, band + tol]
    tol = int(0.25 * band) + 1

    resid = bins - item  # remaining capacity after placing (>= 0 for shown bins)

    # Base: prefer tightest fit (smallest residual).
    score = -(resid.astype(np.float64))

    # Bonus if residual is a "useful" leftover: big enough to hold a typical item
    # but not so big we waste it by fragmenting (i.e., close to a typical size).
    useful = (resid >= 0) & (resid <= 100)
    near_band = useful & (np.abs(resid - band) <= tol)
    score += np.where(near_band, 6.0, 0.0)

    # Smaller bonus if residual is at least one typical item (reusable later).
    reusable = useful & (resid >= band - tol) & (resid <= 100)
    score += np.where(reusable, 1.0, 0.0)

    # Mild penalty for leaving slivers too small for anything meaningful.
    sliver = useful & (resid > 0) & (resid < max(1, band - tol))
    score -= np.where(sliver, 1.0, 0.0)

    # Strong preference not to open a fresh bin when a valid partial fill exists.
    empty = bins == 100
    score -= np.where(empty, 0.5, 0.0)

    return score
# EVOLVE-BLOCK-END
