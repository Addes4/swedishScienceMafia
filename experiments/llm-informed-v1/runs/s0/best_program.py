# EVOLVE-BLOCK-START
"""Adaptive combo bin choice: leave residuals that arrive often, break ties by
size-aware best fit.

Capacity is 100. Items arrive online. We learn which residual values are actually
useful: the most frequent item sizes seen so far are the residuals a future item
is most likely to (nearly) fill. We score each bin by how close its post-placement
residual is to a small set of such empirically attractive values, then break
near-ties toward tighter fits, with the strength of that pressure scaled by how
large the arriving item is.

Guard 1: a residual that is nonzero but smaller than the smallest item size seen
so far can never be filled by any future item (wasted space) -> mild penalty.

Guard 2: closability. For each candidate post-placement residual r we add a
probability-weighted bonus: the empirical probability that a future item is near
r (single-item close, with a small bandwidth) plus a discounted probability that
r is hittable by two items (pair-sum table). This is smooth, so near-perfect
residuals still get partial credit.
"""
import numpy as np

_CAP = 100.0

# Histogram of observed item sizes -> drives the "good residual" targets.
_SIZE_COUNT = np.zeros(101, dtype=np.float64)
_TOTAL = 0.0
_SIZE_SUM = 0.0
_MIN_SIZE = 101.0

# Cached arrays, refreshed as the histogram grows.
_TARGETS = np.array([0.0, _CAP], dtype=np.float64)
_PAIR_SCORE = np.zeros(101, dtype=np.float64)
_EXACT_SCORE = np.zeros(101, dtype=np.float64)
_NEAR_SCORE = np.zeros(101, dtype=np.float64)
_REFRESH = 16
_N_ITEMS = 0.0  # number of items in the instance (known on first call)

# Small bandwidth kernel over residuals for "near a frequent size" credit.
_KERNEL_R = 3
_KR = np.arange(-_KERNEL_R, _KERNEL_R + 1, dtype=np.float64)
_KERNEL = np.exp(-0.5 * (_KR / 1.5) ** 2)


def _rebuild_targets():
    global _TARGETS, _PAIR_SCORE, _EXACT_SCORE, _NEAR_SCORE
    counts = _SIZE_COUNT[1:101]
    order = np.argsort(counts, kind="stable")
    top = order[::-1][:12] + 1  # item sizes with the largest counts
    top = top[counts[top - 1] > 0]
    targets = set([0.0, _CAP])
    for s in top:
        s = float(s)
        targets.add(s)          # a leftover equal to this size closes cleanly
        targets.add(_CAP - s)   # complement also leaves a fillable residual
    _TARGETS = np.array(sorted(targets), dtype=np.float64)

    # Probability-weighted two-item sum table over residuals 0..100.
    support = np.zeros(101, dtype=np.float64)
    plausible = np.nonzero(_SIZE_COUNT[1:101] > 0)[0] + 1
    if plausible.size:
        w = _SIZE_COUNT[plausible]
        support[plausible] = w / w.sum()
    conv = np.convolve(support, support)
    n = min(101, conv.size)
    pair = np.zeros(101, dtype=np.float64)
    pair[:n] = conv[:n]
    m = pair.max()
    if m > 0:
        pair = pair / m
    _PAIR_SCORE = pair

    # Smooth exact-fill score: empirical probability a future item equals r.
    exact = support.copy()
    mx = exact.max()
    if mx > 0:
        exact = exact / mx
    _EXACT_SCORE = exact

    # Smooth "near a frequent size" score: convolve the support with a small
    # Gaussian kernel so residuals within a few units of a frequent size still
    # get partial credit (items are roughly continuous, not discrete).
    near = np.convolve(support, _KERNEL, mode="same")
    near = near[:101]
    if near.size < 101:
        pad = np.zeros(101, dtype=np.float64)
        pad[: near.size] = near
        near = pad
    mn = near.max()
    if mn > 0:
        near = near / mn
    _NEAR_SCORE = near


def priority(item, bins):
    """Return a priority for every bin; the item goes to the highest (first on ties)."""
    global _TOTAL, _SIZE_SUM, _MIN_SIZE, _N_ITEMS

    if _N_ITEMS == 0.0:
        _N_ITEMS = float(len(bins))

    if _TOTAL == 0.0 or (_TOTAL % _REFRESH == 0.0):
        _rebuild_targets()

    residual_after = bins - item

    # Distance to the nearest attractive residual.
    d = np.abs(residual_after[:, None] - _TARGETS[None, :])
    best = d.min(axis=1)

    # Size-aware best-fit pressure: larger arriving items prefer snug bins.
    frac = _TOTAL / _N_ITEMS if _N_ITEMS > 0.0 else 0.0
    base_w = 0.02 + 0.06 * frac
    size_lean = (item - 50.0) / 50.0
    fit_weight = base_w * (1.0 + 0.6 * size_lean)

    score = -best - fit_weight * residual_after

    # Guard 1: penalize tiny nonzero residuals no seen item could fill.
    if _MIN_SIZE <= _CAP:
        waste = (residual_after > 0.0) & (residual_after < _MIN_SIZE)
        score -= 0.02 * waste

    # Guard 2: smooth closability bonus (single-, near- and two-item).
    ri = np.clip(residual_after, 0.0, _CAP).astype(np.int64)
    score += 0.35 * _PAIR_SCORE[ri]
    score += 0.5 * _EXACT_SCORE[ri]
    score += 0.15 * _NEAR_SCORE[ri]

    _SIZE_COUNT[item] += 1.0
    _TOTAL += 1.0
    _SIZE_SUM += item
    if item < _MIN_SIZE:
        _MIN_SIZE = float(item)
    return score
# EVOLVE-BLOCK-END

