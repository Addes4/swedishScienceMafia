# EVOLVE-BLOCK-START
"""Capacity-weighted sum-of-squares rule with exact-fit override and fuller-bin tie-break.

Each item goes where it minimises the potential P = sum_g (100/g)^p * N(g)^2, where N(g) counts
open bins with remaining capacity g (0 < g < 100). The weighting exponent p balances how much the
rule penalizes multiplying near-full residual classes versus counts of large-residual classes.
If some fitting bin can take the item exactly (residual 0), that bin is chosen instead, since
closing a bin is always at least as good as any other placement. Ties on the potential delta go to
the placement whose resulting residual matches a more common existing open class (graded by count),
and then to the bin leaving the smaller residual (fuller bin first). The function is shown only the
bins the item fits in, so it keeps its own record of every opened bin; used bins are always a prefix
of the bin array. Each instance runs in a fresh process, so module-level state starts empty.
"""
import numpy as np

CAP = 100
_P = 0.8
_caps = []                     # remaining capacity of every opened bin, in bin-index order
_N = [0] * (CAP + 1)           # N[g]: open bins with remaining capacity g, 0 < g < CAP
_W = [((CAP / g) ** _P) if g > 0 else 0.0 for g in range(CAP + 1)]  # class weight


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    global _caps, _N
    s = int(item)
    fitting = [j for j, g in enumerate(_caps) if g >= s]
    n_unused = len(bins) - len(fitting)
    scores = np.empty(len(bins), dtype=np.float64)

    # Exact-fit override: only when an existing fitting bin's residual after placement is 0.
    exact_pos = -1
    for k, j in enumerate(fitting):
        if _caps[j] == s:
            exact_pos = k
            break
    if exact_pos >= 0:
        scores[:] = 0.0
        scores[exact_pos] = 1.0
        choice = exact_pos
    else:
        for k, j in enumerate(fitting):
            g = _caps[j]
            r = g - s
            # weighted potential delta: -w_g*(2N[g]-1) + (w_r*(2N[r]+1) if r>0 else 0)
            delta = -_W[g] * (2 * _N[g] - 1)
            if r > 0:
                delta += _W[r] * (2 * _N[r] + 1)
            # graded match bonus: reward residuals matching a more common open class
            match = _N[r] if r > 0 else 0
            # tie-break prefers fuller bins (smaller residual)
            scores[k] = -(delta * 100000.0 + match * 100.0 + r)
        r_new = CAP - s
        delta_new = _W[r_new] * (2 * _N[r_new] + 1) if r_new > 0 else 0.0
        match_new = _N[r_new] if r_new > 0 else 0
        scores[len(fitting):] = -(delta_new * 100000.0 + match_new * 100.0 + r_new)
        choice = int(np.argmax(scores))

    if choice < len(fitting):
        j = fitting[choice]
        g = _caps[j]
        _N[g] -= 1
        _caps[j] = g - s
        if g - s > 0:
            _N[g - s] += 1
    elif n_unused > 0:
        _caps.append(CAP - s)
        if CAP - s > 0:
            _N[CAP - s] += 1
    return scores
# EVOLVE-BLOCK-END
