# EVOLVE-BLOCK-START
"""Best-fit with mean-adaptive sliver penalty, empirical small-item floor,
a multi-item capacity bonus, recent-item pair-complement signals, and a
histogram-based pair-sum complement signal."""
import numpy as np

# State: smoothed histogram of item sizes seen so far (indices 1..100),
# running sum and count for the mean, the previous item size, and a short
# rolling window of recent item sizes.
_hist = np.zeros(101, dtype=np.float64)
_n = 0.0
_sum = 0.0
_mean = 40.0
_prev = 0.0
_recent = np.zeros(8, dtype=np.float64)  # ring of last few items
_recent_idx = 0
_cum = None  # cached cumulative distribution of past items


def priority(item, bins):
    global _hist, _n, _sum, _mean, _prev, _cum, _recent, _recent_idx
    # Update smoothed histogram / running statistics of past items.
    _hist *= 0.999
    _hist[item] += 1.0
    _n += 1.0
    _sum += item
    _mean = _sum / _n

    residual = bins - item  # leftover capacity if placed here
    score = -residual.astype(np.float64)

    total_hist = _hist.sum() + 1e-9

    # Exact-fill reward: placing here wastes nothing, strictly best outcome.
    # Weight it by how common the just-filled size is, so that closing a bin
    # on a frequent item size is valued more than on a rare one.
    exact = (residual == 0)
    if exact.any():
        freq_here = float(_hist[min(max(item, 0), 100)]) / total_hist
        score += (10.0 + 12.0 * freq_here * 100.0 / 5000.0) * exact

    # Empirical "smallest plausible item": the 15th-percentile item size seen
    # so far. A residual below this is unlikely to ever be exactly refilled and
    # should be treated as wasted capacity.
    if _n > 30.0:
        total = _hist.sum() + 1e-9
        cum = np.cumsum(_hist)
        small_thr = float(np.searchsorted(cum, 0.15 * total))
        if small_thr < 1.0:
            small_thr = 1.0
        sliver_thr = float(np.searchsorted(cum, 0.20 * total))
        if sliver_thr < 1.0:
            sliver_thr = 1.0
    else:
        small_thr = max(1.0, 0.5 * _mean)
        sliver_thr = max(1.0, 0.5 * _mean)

    # Data-driven sliver penalty: residual too small to likely be refilled
    # wastes capacity. Threshold is the empirical 20th-percentile item size.
    thr = sliver_thr
    if thr < 1.0:
        thr = 1.0
    sliver = (residual >= 1) & (residual < thr)
    score -= 8.0 * sliver

    # Residuals below the empirical smallest plausible item are truly
    # unfillable; penalize in proportion to how far below they fall.
    unfillable = (residual >= 1) & (residual < small_thr)
    if unfillable.any():
        score -= 3.0 * unfillable * (small_thr - residual)

    # Bonus when the residual equals the current item: encourages stacking
    # identical sizes in the same bin.
    same = (residual == item)
    if same.any():
        score += 1.5 * same

    # Multi-item capacity bonus: a bin whose residual can still hold several
    # typical (mean-sized) items is more reusable than one that can hold only
    # a single one, so prefer keeping such bins in play. Best-fit still
    # dominates via the -residual term.
    typical = 0.5 * _mean
    if typical < 1.0:
        typical = 1.0
    kfit = np.floor(np.maximum(residual, 0) / typical)
    # Diminishing returns: only modestly reward extra item capacity.
    score += 1.2 * np.sqrt(kfit)

    # Stateful complement bonus: reward residuals that can be filled exactly
    # by a recently common item size (wider +/-2 window).
    if _n > 20.0:
        res_clipped = np.clip(residual, 0, 100).astype(np.int64)
        total = _hist.sum() + 1e-9
        freq = _hist[res_clipped]
        lo1 = _hist[np.clip(res_clipped - 1, 0, 100)]
        hi1 = _hist[np.clip(res_clipped + 1, 0, 100)]
        lo2 = _hist[np.clip(res_clipped - 2, 0, 100)]
        hi2 = _hist[np.clip(res_clipped + 2, 0, 100)]
        nearby = freq + 0.6 * (lo1 + hi1) + 0.3 * (lo2 + hi2)
        score += 4.0 * (nearby / total) * 100.0
        # Sharper bonus for an exact match to a common item size.
        score += 3.0 * (freq / total) * 100.0

        # Pair-complement bonus: placing the current item into a bin leaves a
        # residual that a pair of a recent item plus a fresh one could fill
        # exactly. Use a short rolling window of recent items for robustness.
        if _n > 8.0:
            accum = np.zeros_like(res_clipped, dtype=np.float64)
            for w in range(_recent.shape[0]):
                want = int(round(_recent[w]))
                if want < 1:
                    continue
                cand = np.clip(res_clipped - want, 0, 100).astype(np.int64)
                accum += _hist[cand]
            score += 1.8 * (accum / total) * 100.0

            # Direct exact pair-match bonus: the residual equals the current
            # item plus one of the recent item sizes. This is the sharpest
            # signal that the leftover can be closed on the very next item.
            for w in range(_recent.shape[0]):
                want = int(round(_recent[w]))
                if want < 1:
                    continue
                target = item + want
                hit = (residual == target)
                if hit.any():
                    score += 7.0 * hit

        # Pair-sum complement bonus: reward a residual when it is close to
        # (current item + a common past item size), i.e. the leftover could be
        # exactly closed by the next item plus a typical item.
        comp = res_clipped - int(item)
        if comp.size:
            cclip = np.clip(comp, 0, 100).astype(np.int64)
            pair_sum = _hist[cclip]
            score += 1.5 * (pair_sum / total) * 100.0

    # Critical small-item reserve: residuals that are too small to ever hold a
    # mean-sized item are dead space unless a rare small item fits them exactly.
    if _n > 50.0:
        dead = (residual >= 1) & (residual < typical)
        score -= 1.0 * dead * np.maximum(0.0, 1.0 - 0.5 * _mean / np.maximum(_mean, 1.0))

    # Expected-waste penalty: for each residual r, the probability that a
    # future item is strictly larger than r is the chance that this leftover
    # capacity can never be used by a single upcoming item.
    if _n > 40.0:
        cum = np.cumsum(_hist)
        total_hist2 = cum[-1] + 1e-9
        res_int = np.clip(residual, 0, 100).astype(np.int64)
        p_larger = 1.0 - cum[np.clip(res_int - 1, 0, 100)] / total_hist2
        p_larger = np.clip(p_larger, 0.0, 1.0)
        score -= 2.0 * p_larger * (residual > 0)

    _prev = float(item)
    _recent[_recent_idx % _recent.shape[0]] = float(item)
    _recent_idx += 1
    return score
# EVOLVE-BLOCK-END
