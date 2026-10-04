# EVOLVE-BLOCK-START
"""Best-fit with usable-gap bonus, empirical future-fit term, and a
histogram-weighted residual reward that favors residuals matching common
future item sizes (likely to be completed exactly). Uses a periodically
rebuilt lookup table to stay fast."""
import numpy as np

# Module-level state (fresh per instance).
_sum = 0.0
_n = 0
_hist = np.zeros(101, dtype=np.float64)
_median = 40.0
_min_item = 1.0
_mean = 40.0
_pmax = 0.02  # max single-size probability estimate
_q25 = 25.0
_q75 = 55.0

# Cached lookup tables (rebuilt periodically, cheap).
_pfreq_tab = np.zeros(101, dtype=np.float64)   # surviving frequency prob per integer size
_band_tab = np.zeros(101, dtype=np.float64)    # band kernel per residual 0..100
_near_tab = np.zeros(101, dtype=np.float64)    # near kernel weight for integer match
_last_build = -1


def _rebuild():
    global _pfreq_tab, _band_tab, _near_tab, _median, _min_item, _mean, _pmax, _q25, _q75
    total = float(np.sum(_hist[1:101]))
    if total <= 0:
        return
    cdf = np.cumsum(_hist[1:101])
    idx = np.searchsorted(cdf, 0.5 * total)
    _median = float(idx + 1)
    i25 = np.searchsorted(cdf, 0.25 * total)
    i75 = np.searchsorted(cdf, 0.75 * total)
    _q25 = float(i25 + 1)
    _q75 = float(i75 + 1)
    nz = np.nonzero(_hist[1:101])[0]
    if nz.size > 0:
        _min_item = float(nz[0] + 1)
    _mean = _sum / _n
    _pmax = max(float(np.max(_hist[1:101]) / total), 1e-3)

    _pfreq_tab[:] = _hist / total
    # band kernel over residual integer values 0..100
    lo, hi = _q25, _q75
    width = max(hi - lo, 1.0) * 0.5 + 1.0
    mid = 0.5 * (lo + hi)
    x = np.arange(101, dtype=np.float64)
    _band_tab[:] = np.exp(-((x - mid) ** 2) / (2.0 * width * width))
    # near kernel: weight for residual matching the nearest integer (r - ri)^2
    _near_tab[:] = np.exp(-1.0)


def priority(item, bins):
    """Score each fitting bin; highest score wins (first on ties)."""
    global _sum, _n, _median, _min_item, _mean, _pmax, _q25, _q75, _last_build

    _sum += item
    _n += 1
    _hist[item] += 1.0

    if _n >= 30 and (_n - _last_build >= 200 or _last_build < 0):
        _rebuild()
        _last_build = _n

    typical = max(min(_median, 100.0), 1.0)
    mean = max(min(_mean, 100.0), 1.0)

    residual = bins.astype(np.float64) - item  # >= 0 for all shown bins
    r = residual

    # Exact fill: residual is 0 -> perfect, huge bonus.
    exact = (r < 0.5).astype(np.float64)

    # Distance of residual to multiples of a typical item size.
    t = typical
    k = np.rint(r / t)
    dk = np.abs(r - k * t)
    d0 = r
    dist = np.minimum(d0, dk)

    # Reward residuals that can host a typical (median/mean) future item well.
    fit_future = np.abs(r - mean)

    # Sliver penalty: too small to be usefully filled.
    sliver = np.where((r > 0) & (r < 0.5 * t), 0.5 * t - r, 0.0)
    tiny = np.where((r > 0) & (r < _min_item), _min_item - r, 0.0)

    # Harmonic-style waste fraction term.
    used = 100.0 - r
    frac = np.where(used > 0, r / used, 0.0)

    score = -(dist + 0.75 * sliver + 0.5 * tiny) + 5.0 * exact

    # Moderate reward for residuals that can host a future average item.
    score = score - 1.0 * fit_future * 0.05

    score = score - 1.5 * frac

    # Histogram-weighted residual reward: a residual equal to (or near) a
    # frequently observed item size is likelier to be completed exactly soon.
    if _n >= 30:
        # nearest integer size to each residual (round, clamp to 1..100)
        ri = np.clip(np.rint(r), 1.0, 100.0).astype(np.int64)
        pfreq = _pfreq_tab[ri]
        # fractional distance to that integer size, to soften the matching
        near = np.exp(-((r - ri) ** 2) / (2.0 * 1.0))
        score = score + 8.0 * pfreq * near

        # Soft residual-conservation kernel: gentle bonus for residuals in the
        # common future-item size range (25-75 percentile).
        ri2 = np.clip(r, 0.0, 100.0)
        score = score + 0.3 * np.interp(ri2, np.arange(101, dtype=np.float64), _band_tab)

    # Exact fits get extra weight proportional to how likely that item is.
    score = score + 20.0 * _pmax * exact

    # Tie-break toward fuller placements (smaller residual).
    score = score - 1e-3 * r

    return score
# EVOLVE-BLOCK-END
