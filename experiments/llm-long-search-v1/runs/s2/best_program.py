# EVOLVE-BLOCK-START
"""Log-penalty best fit with neighbor-blended frequency lookup and reuse bonus."""
import numpy as np

_counts = np.zeros(101, dtype=np.float64)
_n = 0.0
_sum = 0.0


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _n, _sum
    residual = bins - item  # >= 0 for all bins shown
    rf = residual.astype(np.float64)
    r = residual.astype(np.int64)

    freq = _counts
    # neighbor-blended frequency lookup: raw frequency plus half-weight neighbors
    use = freq[r]
    use = use + 0.5 * np.where(r > 0, freq[np.clip(r - 1, 0, 100)], 0.0)
    use = use + 0.5 * np.where(r < 100, freq[np.clip(r + 1, 0, 100)], 0.0)

    # log penalty preserves best-fit dominance (monotone decreasing in residual)
    tight = -np.log1p(rf)
    score = 4.0 * tight + 0.4 * use

    if _n > 0.0:
        mean_item = _sum / _n
        reuse = 0.25 * np.exp(-((rf - mean_item) ** 2) /
                              (2.0 * (0.25 * mean_item + 1.0) ** 2))
        score = score + reuse

    score[residual == 0] += 1000.0

    _counts[item] += 1.0
    _n += 1.0
    _sum += item

    return score
# EVOLVE-BLOCK-END
