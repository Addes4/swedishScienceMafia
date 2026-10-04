# EVOLVE-BLOCK-START
"""Distribution-aware best fit: prefer placements that either nearly seal the bin (residual
close to 0) or leave a leftover matching a common upcoming item size (so the bin stays
reusable). Uses a running estimate of item statistics to set these targets adaptively."""
import numpy as np

_state = {"n": 0, "sum": 0.0, "full_hist": np.zeros(101, dtype=np.float64),
          "recent": np.zeros(256, dtype=np.int64), "ptr": 0, "filled": 0,
          "recent_hist": np.zeros(101, dtype=np.float64)}


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    st = _state
    st["n"] += 1
    st["sum"] += item
    st["full_hist"][item] += 1

    # Rolling window of recent items for a responsive local distribution estimate.
    r = st["recent"]
    if st["filled"] < r.size:
        r[st["filled"]] = item
        st["filled"] += 1
    else:
        old = r[st["ptr"]]
        st["recent_hist"][old] -= 1
        r[st["ptr"]] = item
        st["ptr"] = (st["ptr"] + 1) % r.size
    st["recent_hist"][item] += 1

    mean_all = st["sum"] / st["n"]

    if st["filled"] >= 32:
        window = r[:st["filled"]]
        mean_recent = float(window.mean())
        med_recent = float(np.median(window))
    else:
        mean_recent = mean_all
        med_recent = mean_all

    residual = bins - item

    # Base best-fit gradient: gently prefer smaller usable leftovers.
    score = -0.08 * residual

    # Seal: strong monotone preference toward exact fill; residual 0 dominates.
    score = score + 2.0 * np.clip(4.0 - residual, 0.0, None)
    score = np.where(residual == 0, score + 100000.0, score)

    # Reusability target: leftover close to a typical item size keeps the bin productive.
    target = max(mean_recent, 1.0)
    score = score - 0.6 * np.abs(residual - target)

    # Anti-sliver: continuous penalty as residual falls below the usable target.
    sliver = np.clip(target - residual, 0.0, None)
    score = score - 0.5 * sliver

    # Reusability bonus from recent-window histogram, smoothed for stability.
    total_recent = float(max(st["filled"], 1))
    frac = st["recent_hist"] / total_recent
    kern = np.array([0.15, 0.7, 0.15])
    smoothed = np.convolve(frac, kern, mode="same")
    in_range = (residual >= 0) & (residual <= 100)
    rr = np.where(in_range, residual, 0).astype(np.int64)
    reuse = smoothed[rr] * in_range
    score = score + 18.0 * reuse

    # Sharp lifetime-histogram match: reward residuals that are themselves a very
    # common item size in the full distribution seen so far.
    full_total = float(max(st["n"], 1))
    ffrac = st["full_hist"] / full_total
    fpeak = ffrac[rr] * in_range
    score = score + 6.0 * fpeak

    return score
# EVOLVE-BLOCK-END
