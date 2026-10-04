# EVOLVE-BLOCK-START
"""Online bin-choice rule: tight packing with reusable-gap awareness.

Strongly reward exact fills.  Among non-exact placements, prefer the smallest
residual (best fit) so gaps are concentrated, but boost residuals that can
still hold future items.  Two usability tiers (small and typical) let the
rule favor gaps that remain broadly reusable across the size distribution.
Additionally, track an empirical histogram of past item sizes so residuals
that are likely to be exactly filled by a future item are favored.
Empty bins are kept slightly less attractive so they stay free for large
items.
"""
import numpy as np

SMALL = 20.0
TYPICAL = 40.0

# Empirical histogram of past item sizes, accumulated across calls.
_HIST = np.zeros(101, dtype=np.float64)
_COUNT = 0

# Gaussian-like smoothing weights for window offsets -8..8.
_OFFS = np.arange(-8, 9)
_W = np.exp(-(_OFFS.astype(np.float64) ** 2) / (2.0 * 3.0 ** 2))


def priority(item, bins):
    """Score every bin; highest score wins, ties to first."""
    global _HIST, _COUNT

    residual = bins - item  # remaining capacity after placing the item

    r = np.clip(residual.astype(np.float64), 0.0, None)
    score = -np.sqrt(r)

    # Exact fill: no waste at all.
    score += np.where(residual == 0, 1000.0, 0.0)

    # Residual can host at least a small item: valuable.
    small_ok = residual >= SMALL
    score += np.where(small_ok, 4.0, 0.0)

    # Residual can host a typical item: even more valuable.
    typical_ok = residual >= TYPICAL
    bonus = 6.0 - 0.03 * np.clip(residual - TYPICAL, 0.0, None)
    score += np.where(typical_ok, bonus, 0.0)

    # Penalize slivers: positive but too small to ever be useful.
    sliver = (residual > 0) & (residual < SMALL)
    score -= np.where(sliver, 30.0, 0.0)

    # Empirical-fill bonus: if a residual equals a size we've seen often,
    # a future item may fill it exactly, so favor such residuals.
    if _COUNT > 50:
        prob = _HIST / _COUNT
        ri = np.clip(residual, 0, 100).astype(np.int64)
        smoothed = np.zeros_like(r)
        for off, wt in zip(_OFFS, _W):
            idx = np.clip(ri + off, 0, 100)
            smoothed += wt * prob[idx]
        # Scale by the peak probability so common residuals dominate.
        peak = smoothed.max()
        if peak > 0:
            smoothed = smoothed / peak
        score += 120.0 * smoothed

    # Gently prefer already-used bins (keeps empty bins for large items).
    used = bins < 100
    score += np.where(used, 2.0, 0.0)

    # Update histogram with the current item (after scoring).
    if 1 <= item <= 100:
        _HIST[item] += 1.0
        _COUNT += 1

    return score
# EVOLVE-BLOCK-END
