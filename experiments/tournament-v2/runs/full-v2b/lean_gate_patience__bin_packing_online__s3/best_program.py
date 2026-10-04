# EVOLVE-BLOCK-START
"""Adaptive fit using a running histogram of past item sizes to value residual capacity."""
import numpy as np

_SIZE = 101
_HIST = np.ones(_SIZE, dtype=np.float64)
_COUNT = float(_SIZE)
_DECAY = 0.995


def priority(item, bins):
    global _HIST, _COUNT
    # update running distribution of past item sizes (decayed histogram)
    _HIST *= _DECAY
    _HIST[item] += 1.0
    _COUNT = _COUNT * _DECAY + 1.0
    hist = _HIST / _COUNT

    # expected "usefulness" u(r) of a residual capacity r:
    # probability that some future item fits in r, weighted by how well it fills r.
    # Precompute as cumulative counts scaled by match quality.
    fit_prob = np.cumsum(hist[:101])  # P(size <= r)
    # expected fill fraction when packing a residual of size r with one random item
    weights = np.arange(101, dtype=np.float64)
    cum_w = np.cumsum(hist * weights)
    # mean item size that fits r, conditional
    with np.errstate(divide='ignore', invalid='ignore'):
        mean_fit = np.where(fit_prob > 1e-9, cum_w / np.maximum(fit_prob, 1e-9), 0.0)

    residual = bins - item  # remaining capacity after placing
    # value of residual: chance next items can use it, plus tightness of placement
    use = fit_prob[np.clip(residual, 0, 100)]
    # prefer residuals that are likely to be nearly filled by a typical future item
    near = 1.0 - np.abs(residual - mean_fit[np.clip(residual, 0, 100)]) / np.maximum(
        residual, 1.0)
    score = 0.5 * use + 0.5 * near
    # primary factor: tightest fit (least residual)
    return score * 10.0 - residual * 0.05
# EVOLVE-BLOCK-END
