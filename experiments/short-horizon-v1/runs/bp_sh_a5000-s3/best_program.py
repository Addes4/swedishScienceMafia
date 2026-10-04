# EVOLVE-BLOCK-START
"""Distribution-adaptive best-fit with a learned residual-value estimate."""
import numpy as np


_COUNTS = np.ones(101, dtype=np.float64)
_TOTAL = 101.0

_UTIL = np.zeros(101, dtype=np.float64)
_REACH = np.zeros(101, dtype=np.float64)
_DIRTY = True


def _smooth(arr, sigma=1.0):
    """Small Gaussian smoothing over the integer residual axis."""
    k = int(3 * sigma)
    xs = np.arange(-k, k + 1, dtype=np.float64)
    w = np.exp(-0.5 * (xs / sigma) ** 2)
    w /= w.sum()
    padded = np.concatenate([np.full(k, arr[0], dtype=np.float64), arr,
                             np.full(k, arr[-1], dtype=np.float64)])
    return np.convolve(padded, w, mode='valid')


def _rebuild_util():
    global _UTIL, _DIRTY, _REACH
    probs = _COUNTS / _TOTAL

    top = np.argsort(probs)[::-1][:14]
    top = [int(t) for t in top if probs[t] > probs.mean()]

    util = probs.copy()

    # reach[s]: probability-like weight that residual s can be exactly closed
    # by 1..3 future items drawn from the observed (top) support.
    reach = np.zeros(101, dtype=np.float64)
    reach[0] = 1.0
    for s in top:
        if 0 < s <= 100:
            reach[s] = max(reach[s], probs[s])

    for a in top:
        if a <= 0 or a > 100:
            continue
        pa = probs[a]
        for b in top:
            s = a + b
            if 0 < s <= 100:
                w = pa * probs[b]
                util[s] += w
                reach[s] = max(reach[s], w)
            for c in top:
                t = a + b + c
                if 0 < t <= 100:
                    reach[t] = max(reach[t], pa * probs[b] * probs[c])

    _UTIL = _smooth(util)
    _REACH = _smooth(reach)
    _DIRTY = False


def priority(item, bins):
    global _COUNTS, _TOTAL, _DIRTY

    residual = (bins - item).astype(np.float64)

    if _DIRTY:
        _rebuild_util()

    ri = np.clip(np.round(residual).astype(np.int64), 0, 100)

    # Value of a leftover: how easily it can be exactly closed later.
    val = _UTIL[ri]
    score = np.log(val + 1e-9)

    score += 0.15 * _REACH[ri]

    m = _COUNTS / _TOTAL
    anchor = int(np.argmax(m[1:]) + 1)
    modal_p = m[anchor]

    # Sharp, strongly-weighted best-fit: residual exactly 0 is by far the most
    # valuable, so bins that can be closed now are decisively preferred.
    score += (residual == 0.0).astype(np.float64) * (6.0 + 3.0 * modal_p)

    # Narrow Gaussian best-fit term centered at 0 so small leftovers are
    # favored without the noisy anchor-shift.
    score += (0.6 + 0.8 * modal_p) * np.exp(-0.5 * (residual / 3.0) ** 2)

    _COUNTS[item] += 1.0
    _TOTAL += 1.0
    _DIRTY = True

    return score
# EVOLVE-BLOCK-END
