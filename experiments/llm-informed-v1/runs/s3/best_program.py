# EVOLVE-BLOCK-START
"""Best fit with exact-fill preference, empirical future-fill lookahead
scaled by the number of items left, complementary pairing, and a
pair-closure signal, with exponential forgetting of past items."""
import numpy as np

_state = {
    "n": 0.0,
    "hist": np.zeros(101, dtype=np.float64),   # decayed counts of items seen
}

_DECAY = 0.999


def priority(item, bins):
    """Rank bins by best-fit, exact fill, and probability of a future fill.

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    st = _state
    st["n"] += 1.0
    hist = st["hist"]
    # exponential forgetting so the distribution reflects recent items
    hist *= _DECAY
    hist[item] += 1.0
    total = float(hist.sum())

    n_items = float(len(bins))

    post = bins - item  # residual after placing item here

    # Base: best fit -> prefer the smallest post-placement residual.
    score = -post.astype(np.float64)

    # Scale best-fit strength with fragmentation: when many open bins have
    # small residuals, consolidating (best-fit) matters more.
    mean_item = float((hist * np.arange(101, dtype=np.float64)).sum() / max(total, 1.0))
    if mean_item < 1.0:
        mean_item = 40.0
    small_resid = np.count_nonzero((bins > 0) & (bins < mean_item))
    frac_small = small_resid / max(len(bins), 1)
    score *= (1.0 + 3.0 * frac_small)

    # Exact fill: perfect, strongly preferred.
    score += (post == 0).astype(np.float64) * 10000.0

    # Laplace-smoothed item-size distribution.
    prob = (hist + 1.0) / (total + 100.0)

    post_idx = post.astype(np.int64)
    valid = (post_idx >= 1) & (post_idx <= 100)
    p_fill = np.zeros_like(score)
    if valid.any():
        idx = post_idx[valid]
        p_fill[valid] = prob[idx]

    # Expected number of future exact single-item fills for this residual.
    remaining = max(n_items - st["n"], 0.0)
    exp_fill = remaining * p_fill

    score += p_fill * 300.0

    # Reward placing into a bin whose residual before placement == item,
    # closing the bin exactly.
    score += (bins == item).astype(np.float64) * 400.0

    score += exp_fill * 60.0

    # Pair-closure lookahead: probability that this residual can be exactly
    # filled by a *pair* of typical future items (convolution of prob with
    # itself), which consolidates leftovers that a single item cannot close.
    pair_prob = np.zeros(101, dtype=np.float64)
    p = prob[1:101]
    conv = np.convolve(p, p)
    pair_prob[1:101] = conv[:100]
    p_pair = np.zeros_like(score)
    if valid.any():
        p_pair[valid] = pair_prob[post_idx[valid]]

    # Scale by estimated number of future item-pairs available.
    n_pairs = remaining * max(remaining - 1.0, 0.0) * 0.5
    # Only meaningful while plenty of items remain; shrink near the end.
    pair_weight = min(n_pairs / max(n_items, 1.0), 5.0)
    score += p_pair * pair_weight * 4000.0

    # Mode-residual bonus: prefer leaving a residual equal to the most common
    # recent item size, weighted by how common it is.
    mode_idx = int(np.argmax(prob[1:101])) + 1
    p_mode = float(prob[mode_idx])
    score += (post_idx == mode_idx).astype(np.float64) * p_mode * 800.0

    return score
# EVOLVE-BLOCK-END

