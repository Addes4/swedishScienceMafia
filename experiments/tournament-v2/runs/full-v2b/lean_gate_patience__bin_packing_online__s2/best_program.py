# EVOLVE-BLOCK-START
"""Residual-desirability bin packing with a subset-sum fillability estimate."""
import numpy as np

_state = {
    "mean": 40.0,
    "hist": np.ones(21, dtype=np.float64),
    "cache_key": None,
    "fill_prob": None,
}


def _fill_probability(mu):
    """Estimate, for each residual r in 0..100, the probability that r can be
    exactly filled by 1..3 future items, using a discretized item-size model."""
    if mu < 1.0:
        mu = 1.0
    s = np.arange(1, 101, dtype=np.float64)
    shape_density = (s / mu) * np.exp(-((s / mu) ** (1.0 / 0.8)))
    shape_density /= shape_density.sum()
    single = shape_density

    p1 = single.copy()
    conv2 = np.convolve(single, single)
    conv3 = np.convolve(conv2, single)

    fp = np.zeros(101, dtype=np.float64)
    for r in range(1, 101):
        v = p1[r - 1]
        if r <= len(conv2):
            v += 0.55 * conv2[r - 1]
        if r <= len(conv3):
            v += 0.25 * conv3[r - 1]
        fp[r] = v
    m = fp.max()
    if m > 0:
        fp /= m
    return fp


def priority(item, bins):
    S = _state
    it = float(item)

    S["mean"] = 0.98 * S["mean"] + 0.02 * it
    mu = S["mean"]

    b = np.asarray(bins, dtype=np.float64)
    res = b - it

    # Dominant best-fit: exponentially decaying preference for small residual.
    tight = np.exp(-res * 1.5)

    key = int(mu * 4.0)
    if S["cache_key"] != key or S["fill_prob"] is None:
        S["fill_prob"] = _fill_probability(mu)
        S["cache_key"] = key
    ri = np.clip(np.round(res).astype(np.int64), 0, 100)
    fill = S["fill_prob"][ri]

    # Sharp exact-fit bonus: reward residual 0 and residuals matching a typical
    # next item size, used only to break near-ties in the best-fit ordering.
    exact0 = (res < 0.5).astype(np.float64)
    typical = np.exp(-((res - mu) ** 2) / (2.0 * (0.35 * mu) ** 2))
    match = np.exp(-np.abs(res - np.round(res)) * 4.0) * typical

    score = 12.0 * tight + 1.2 * fill + 0.6 * exact0 + 0.3 * match
    return score
# EVOLVE-BLOCK-END
