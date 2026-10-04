# EVOLVE-BLOCK-START
"""Sum-of-Squares rule with largest-residual tie-breaking.

Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining
capacity g (0 < g < 100). Exact-delta ties are broken by preferring the placement that
leaves the largest post-placement residual, which keeps more usable free space available
for future items.
The function is shown only the bins the item fits in, so it keeps its own record of every
opened bin. Used bins are always a prefix of the bin array (harness opens unused bins in
index order and ties go to the first bin). Each instance runs in a fresh process, so the
module-level state starts empty for every instance.
"""
import numpy as np

CAP = 100
_caps = []                     # remaining capacity of every opened bin, in bin-index order
_N = [0] * (CAP + 1)           # N[g]: open bins with remaining capacity g, 0 < g < CAP


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _caps, _N
    s = int(item)
    n_bins = len(bins)
    fitting = [j for j, g in enumerate(_caps) if g >= s]
    n_unused = n_bins - len(fitting)
    scores = np.empty(n_bins, dtype=np.float64)

    def rank(r):
        if r > 0:
            delta = -2 * _N[g_ref] + 1 + (2 * _N[r] + 1)
        else:
            delta = -2 * _N[g_ref] + 1
        return (-delta, r)

    for k, j in enumerate(fitting):
        g_ref = _caps[j]
        r = g_ref - s
        key = rank(r)
        scores[k] = key[0] * 1e9 + key[1]

    r_new = CAP - s
    g_ref = CAP
    if r_new > 0:
        delta_new = 2 * _N[r_new] + 1
    else:
        delta_new = 0
    scores[len(fitting):] = -delta_new * 1e9 + r_new

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
