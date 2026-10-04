# EVOLVE-BLOCK-START
"""Distribution-aware best-fit with a waste-probability penalty.

For each candidate bin we compute the resulting residual r = bins - item.
Base is classic best-fit (-r).  We subtract a penalty proportional to the
probability that future items are too large to fit in r (stranded space),
and add a bounded "perfect refill" bonus when r can be exactly decomposed
into one or two frequently observed item sizes.  A usability term rewards
residuals likely to fit at least one more future item.

To reduce early-game noise, the empirical CDF is lightly smoothed by a
Gaussian kernel and the distribution terms fade in as more items are seen.
"""
import numpy as np


class _Stats:
    def __init__(self):
        self.count = 0
        self.total = 0.0
        self.sizes = np.zeros(101, dtype=np.float64)

    def update(self, item):
        self.count += 1
        self.total += item
        self.sizes[item] += 1.0


_stats = _Stats()
_freq = None
_cdf = None
_two = None
_last_count = -1


def _smooth(freq):
    """Gaussian-smooth the size distribution over integer sizes 1..100."""
    k = np.arange(1, 101, dtype=np.float64)
    w = freq[1:101]
    sigma = 1.5
    d = k[:, None] - k[None, :]
    K = np.exp(-0.5 * (d / sigma) ** 2)
    K /= K.sum(axis=1, keepdims=True)
    sw = K.dot(w)
    return sw


def _ensure_tables():
    global _freq, _cdf, _two, _last_count
    n = _stats.count
    if n == _last_count:
        return
    if n == 0:
        return
    freq = _stats.sizes / n  # freq[s] = P(item == s)

    sw = _smooth(freq)
    sm = np.zeros(101, dtype=np.float64)
    sm[1:101] = sw

    cdf = np.zeros(101, dtype=np.float64)
    cdf[1:101] = np.cumsum(sw)
    cdf[100] = 1.0

    # two[s] = P(two independent items sum exactly to s), using smoothed freq
    two = np.zeros(101, dtype=np.float64)
    k = np.arange(1, 101, dtype=np.float64)
    for s in range(2, 101):
        idx = np.arange(1, s)
        if idx.size:
            two[s] = float(np.dot(sm[idx], sm[s - idx]))

    _freq = sm
    _cdf = cdf
    _two = two
    _last_count = n


def priority(item, bins):
    _stats.update(item)

    residual = bins - item
    r = residual.astype(np.float64)

    # Base: best fit -> smaller resulting residual is better.
    score = -r

    _ensure_tables()

    if _freq is not None:
        freq = _freq
        cdf = _cdf
        two = _two

        rr = np.clip(residual, 0, 100).astype(np.int64)
        # P(item > r): for r>=100 it's 0; else 1 - CDF(r).
        prob_too_big = np.where(residual >= 100, 0.0, 1.0 - cdf[rr])
        score -= prob_too_big * 55.0

        # Perfect-refill bonus: residual exactly equal to a common size,
        # or decomposable into two common sizes.
        one = freq[rr]
        match = np.maximum(one, two[rr])
        score += match * 32.0

        # Second-fit: probability residual can be el
        # (r - s) for some common item size s.  This rewards residuals that
        # pair well with typical items, encouraging denser packing.
        second = np.zeros_like(r)
        for s in range(1, 101):
            ps = freq[s]
            if ps <= 1e-6:
                continue
            rr2 = np.clip(residual - s, 0, 100).astype(np.int64)
            valid = residual - s >= 0
            contrib = np.where(valid, freq[rr2], 0.0)
            second += ps * contrib
        score += np.minimum(second, 1.0) * 12.0

        # Usability: probability that at least one future item fits in r.
        usability = np.where(residual >= 100, 1.0, cdf[rr])
        score += usability * 8.0

    # Small tiebreak: reuse already-open bins over fresh ones.
    fresh = (bins >= 100).astype(np.float64)
    score -= fresh * 0.1

    return score
# EVOLVE-BLOCK-END
