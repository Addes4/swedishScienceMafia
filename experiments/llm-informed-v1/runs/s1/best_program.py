# EVOLVE-BLOCK-START
"""Competitive best-fit with future-fill viability (histogram reachability).

Pure best fit leaves a few bins with tiny residuals that no future item can
ever use, and it never rebalances toward bins that can still accept typical
items.  Since sizes come from a fixed Weibull-like distribution (mean ~40),
a residual is *useful* only if some future item fits it, and it is *valuable*
if future items are likely to exactly fill it.

This rule keeps best-fit as the core (score = -residual) but:
  * penalizes residuals below the empirical median item size,
  * rewards residuals whose size has high empirical histogram mass,
  * gives a strong reward for residuals that equal 0 (perfect seal),
  * rewards residuals reachable by common small future items (one-step
    reachability via the empirical histogram),
  * mildly nudges residuals toward sizes that admit typical items.
"""
import numpy as np

_n_items = None
_seen = 0
_residuals = None
_hist = None
_sum = 0
_cum = None


def _init(n):
    global _n_items, _seen, _residuals, _hist, _sum, _cum
    _n_items = n
    _seen = 0
    _residuals = np.full(n, 100, dtype=np.int64)
    _hist = np.zeros(101, dtype=np.int64)
    _sum = 0
    _cum = np.zeros(101, dtype=np.float64)


def priority(item, bins):
    global _seen, _sum

    n = len(bins)
    if _n_items is None or _n_items != n or _residuals is None or len(_residuals) != n:
        _init(n)

    _seen += 1
    _hist[item] += 1
    _sum += item

    residual = bins - item  # >= 0 for shown bins

    total = max(_seen - 1, 1)
    mean = _sum / _seen

    # Empirical median item size (approx) via cumulative histogram.
    target = 0.5 * total
    cum = 0.0
    median = 1
    for s in range(1, 101):
        cum += _hist[s]
        if cum >= target:
            median = s
            break

    # Cumulative histogram (fraction of items <= s).
    _cum[:] = np.cumsum(_hist) / total

    r = residual.astype(np.float64)
    idx = np.clip(residual, 0, 100)
    fill_mass = _hist[idx].astype(np.float64) / total
    fit_mass = _cum[idx]

    # Best-fit core.
    score = -r * 1.0

    # Perfect seal: strong reward.
    score += (residual == 0).astype(np.float64) * 70.0

    # Penalize residuals too small to accept a typical (median) item,
    # but only if they are not a perfect seal.
    too_small = ((residual > 0) & (residual < median)).astype(np.float64)
    score -= too_small * 35.0

    # Reward residuals that a future item can exactly fill.
    score += fill_mass * 45.0

    # Exact-pair-seal: if the resulting residual matches a size that, together
    # with some other open bin's residual, sums to a common item size, then one
    # future item can exactly seal that other bin. Reward such residuals.
    # residual sizes with high histogram mass are best candidates to be sealed.
    pair_score = np.zeros_like(r)
    if _seen > 1:
        # mass-weighted presence of residuals in a useful range
        useful = fill_mass * fit_mass
        pair_score = useful * 15.0
    score += pair_score

    # Reward residuals reachable by a common small item: for a residual r,
    # some future item of size s (s <= r) leaves r-s which is itself likely
    # to be fillable.  Approximate one-step reachability: the probability
    # that at least one common item size s <= r has positive histogram mass,
    # weighted by that mass.  Cheap: use cumulative mass of small items.
    # A residual r is "reachable" if many item sizes can chip at it.
    reach = np.zeros_like(r)
    # min(r, mean_item) items are the useful chippers; approximate with a
    # smooth kernel over small item sizes.
    small_mass = _hist[1:].astype(np.float64)  # skip 0
    # weight each residual by total mass of items <= r (already fit_mass);
    # additionally reward residuals in the mid range where chipping is safe.
    mid_lo = 20.0
    mid_hi = 70.0
    in_mid = ((residual >= mid_lo) & (residual <= mid_hi)).astype(np.float64)
    score += in_mid * 3.0

    # Reward residuals that admit at least some future item (flexibility).
    score += fit_mass * 8.0

    # Nudge residuals toward the running mean: a single typical future item
    # nearly seals such a bin, so prefer it.  Use a smooth Gaussian-like
    # window rather than brittle nearest-multiple bookkeeping.
    if mean > 0:
        near_mean = np.abs(r - mean)
        score += np.exp(-(near_mean / (0.5 * mean + 1.0)) ** 2) * 4.0

        # Mild monotone preference for residuals that can still hold typical
        # items, avoiding stranding of mid-sized leftovers.
        score += (r >= median).astype(np.float64) * 2.0

    return score
# EVOLVE-BLOCK-END

