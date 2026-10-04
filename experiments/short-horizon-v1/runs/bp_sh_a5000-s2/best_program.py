# EVOLVE-BLOCK-START
"""Empirical-residual best fit with completion-aware future-fillability.

Strongly prefer exact perfect fits. Otherwise score a placement by how
likely its resulting residual can be consumed by future items, using a
smoothed online estimate of the item-size distribution:
  - probability a single future item exactly equals the residual,
  - probability a pair of future items sums to the residual,
plus a mild best-fit tie-break and a softened stranding penalty.
"""
import numpy as np

# Parametric prior: Weibull-ish shape with mean ~40, over sizes 1..100.
_sizes = np.arange(101, dtype=np.float64)
_shape = 2.0
_scale = 45.0
_w_prior = (_sizes[1:] / _scale) ** (_shape - 1.0) * np.exp(-(_sizes[1:] / _scale) ** _shape)
_w_prior = _w_prior / _w_prior.sum()
_prior = np.zeros(101, dtype=np.float64)
_prior[1:] = _w_prior
_prior_scale = 30.0  # weight of prior relative to observed counts

# Empirical distribution over item sizes 1..100, updated online.
_hist = 1.0 + _prior_scale * _prior
_seen = 0.0

_min_item = 100.0  # smallest item size observed so far in this stream

_DECAY = 0.999  # mild recency weighting to adapt within a stream

# Precomputed smoothing kernel (over residual distance).
_kdist = np.arange(-2, 3, dtype=np.float64)
_ksmooth = np.exp(-0.5 * (_kdist / 1.0) ** 2)
_ksmooth /= _ksmooth.sum()


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _hist, _seen, _min_item

    residual = bins - item

    # Strongly prefer an exact perfect fit.
    perfect = residual == 0

    # Current estimate of the item-size distribution over 1..100.
    h = _hist / _hist.sum()

    r_idx = np.clip(residual, 0, 100).astype(np.int64)

    # Smoothed density at the residual (robustness to small sampling gaps).
    dens = np.zeros(101, dtype=np.float64)
    for k, w in enumerate(_ksmooth):
        shift = k - 2
        src = np.clip(np.arange(101) + shift, 0, 100)
        dens += w * h[src]

    # Probability a single future item exactly equals this residual.
    exact = dens[r_idx]

    # Pair-completion probability via self-convolution of the empirical hist.
    conv2 = np.convolve(_hist[1:], _hist[1:])  # conv2[k] for sum k+2
    total2 = _hist.sum() * _hist.sum()
    pair = np.zeros(101, dtype=np.float64)
    k = min(101, conv2.size)
    pair[2:2 + k] = conv2[:101 - 2] / total2

    # Complementary fit: residual that pairs with the *current* item size to
    # leave a small reusable leftover, or that the current item can help fill
    # toward a common bin total. Reward residuals that equal a typical item.
    mean_size = float(np.dot(np.arange(101), h))

    # Combined usefulness: exact single > exact pair.
    usefulness = (
        5000.0 * exact
        + 1000.0 * pair[r_idx]
    )

    # Mild bonus for residuals close to the typical item size.
    usefulness += 40.0 * np.exp(-np.abs(residual - mean_size) / 10.0)

    # Sharp complement bonus: residual likely to be filled exactly by a single
    # future item of the current item's size class (encourages pairing like items).
    cur_dens = float(dens[item]) if 0 <= item <= 100 else 0.0
    usefulness += 300.0 * cur_dens * np.exp(-np.abs(residual - item) / 6.0)

    # Mild best-fit tie-break: prefer smaller residuals.
    score = usefulness - residual.astype(np.float64) * 0.02

    # Penalize residuals that can never be filled again (below smallest seen).
    min_obs = max(1.0, _min_item)
    unusable = (residual > 0) & (residual < min_obs)
    deficit = np.clip(min_obs - residual, 0.0, None)
    score -= unusable * (20.0 + 8.0 * deficit)

    # Update histogram for future items, with mild decay for recency.
    _hist *= _DECAY
    _hist[item] += 1.0
    _seen += 1.0
    if item < _min_item:
        _min_item = float(item)

    return score + perfect * 1e9
# EVOLVE-BLOCK-END

