# EVOLVE-BLOCK-START
"""Sum-of-Squares rule with a flexibility-preserving tie-break.

Each item goes where it minimises sum_g N(g)^2 (the SS rule), which is asymptotically optimal
for this class of online bin packing. The SS delta is an exact integer, so it is used as the
dominant criterion; among placements with equal SS delta we prefer the placement that leaves
the *larger* residual, keeping flexible free space available for future large items (instead
of fragmenting bins to chase tight/perfect fits). The function is shown only the bins the
item fits in, so it keeps its own record of every opened bin. Used bins are a prefix of the
bin array; each instance runs in a fresh process.
"""
import numpy as np

CAP = 100
_caps = []                     # remaining capacity of every opened bin, in bin-index order
_N = [0] * (CAP + 1)           # N[g]: open bins with remaining capacity g, 0 < g < CAP


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

    for k, j in enumerate(fitting):
        g = _caps[j]
        r = g - s
        delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)
        # Dominant: exact SS delta (as large negative as possible).
        # Tie-break: prefer the larger residual (more flexible free space).
        scores[k] = -(float(delta) * 1000.0 - r)

    r_new = CAP - s
    delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
    scores[len(fitting):] = -(float(delta_new) * 1000.0 - r_new)

    choice = int(np.argmax(scores))          # the harness's choice: first highest score
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
