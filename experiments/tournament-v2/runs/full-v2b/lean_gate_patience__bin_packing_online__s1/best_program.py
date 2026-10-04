# EVOLVE-BLOCK-START
"""Best-fit packing rule with a sharp online learned residual-value bonus.

The dominant term is classic best-fit: place the item into the bin with the
smallest non-negative residual (score ~ 1/(residual+1)).  A secondary term
uses an online histogram of the item sizes seen so far to reward placements
whose leftover residual matches a common future item size.  Because the size
distribution is concentrated around ~40, using a *sharp* kernel focused on the
modal residual reduces fragmentation more effectively than a broad kernel.
"""
import numpy as np

# Running histogram of item sizes seen so far (index 1..100).
_HIST = np.zeros(101, dtype=np.float64)
_COUNT = 0.0

# Weight of the learned residual-value term relative to the best-fit term.
_W = 0.35

# Bandwidth of the sharp Gaussian kernel used for residual value.
_BW = 5.0


def priority(item, bins):
    """Return a priority for every bin in `bins`; item goes to the highest score."""
    global _COUNT
    r = bins - item  # residual capacity if placed in each bin (>= 0 by contract)

    # Classic best-fit term: tightest residual wins.
    scores = 1.0 / (r + 1.0)

    # Learned expected-value term: reward residuals that match a common future
    # item size (so the leftover space is likely to be useful again).
    if _COUNT > 0.0:
        weights = _HIST / _COUNT
        vals = np.zeros_like(r, dtype=np.float64)
        for s in range(1, 101):
            w = weights[s]
            if w > 0.0:
                vals += w * np.exp(-((r - s) ** 2) / (2.0 * _BW * _BW))
        # Focus on the dominant residual value and reward residuals that can fit
        # at least one more typical item.
        maxv = vals.max()
        if maxv > 0.0:
            vals = vals / maxv
        # Reward residuals that could still hold the current item's size again.
        fit_bonus = 0.05 * (r >= item)
        # Extra reward when the residual exactly equals the current item size,
        # encouraging leftover space to be reused by the same item size.
        pair_bonus = 0.03 * (r == item)
        scores = scores + _W * vals + fit_bonus + pair_bonus

    # Mild preference for already-open (less empty) bins.
    scores = scores - 0.0001 * bins

    # Update statistics with the current item.
    _HIST[item] += 1.0
    _COUNT += 1.0

    return scores
# EVOLVE-BLOCK-END
