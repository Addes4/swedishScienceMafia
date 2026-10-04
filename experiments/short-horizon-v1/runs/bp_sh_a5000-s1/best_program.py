# EVOLVE-BLOCK-START
"""Best fit with an exact-residual-match fast path driven by the recent small-item mode."""
import numpy as np


class _State:
    def __init__(self):
        self.small = 10.0   # running estimate of a "small" item size
        self.n = 0
        self.counts = {}    # recent counts of small item sizes (for mode)

    def update(self, item):
        self.n += 1
        s = float(min(item, 40))
        self.small = 0.98 * self.small + 0.02 * s
        if self.small < 3.0:
            self.small = 3.0
        # track mode of small item sizes seen recently (bounded memory)
        if item <= 40:
            self.counts[item] = self.counts.get(item, 0) + 1
            if self.n % 500 == 0:
                # decay counts to keep it "recent"
                for k in list(self.counts.keys()):
                    self.counts[k] = self.counts[k] // 2
                    if self.counts[k] == 0:
                        del self.counts[k]

    def mode_small(self):
        best_k, best_v = 0, 0
        for k, v in self.counts.items():
            if v > best_v:
                best_v, best_k = v, k
        return best_k


_state = _State()


def priority(item, bins):
    """Return a priority per bin: prefer an exact residual match, else best fit with a guard."""
    _state.update(item)
    bins = np.asarray(bins)
    residual = bins - item  # post-placement residual per bin

    # Fast path: an existing used bin whose residual exactly matches a common small item.
    m = _state.mode_small()
    if m > 0:
        match = np.where((residual == m) & (bins < 100))[0]
        if match.size > 0:
            score = np.full(bins.shape, -1e9, dtype=np.float64)
            score[match[0]] = 1.0
            return score

    residual = bins - item
    thresh = 0.6 * _state.small  # residual below this is hard to reuse

    order = np.argsort(residual, kind="stable")
    best = order[0]
    best_res = residual[best]

    if best_res <= 0 or best_res >= thresh:
        score = -residual.astype(np.float64)
        return score

    usable = np.where((residual >= thresh) & (bins < 100))[0]
    if usable.size > 0:
        j = usable[np.argmin(residual[usable])]
        score = np.full(bins.shape, -1e9, dtype=np.float64)
        score[j] = 1.0
        return score

    return -residual.astype(np.float64)
# EVOLVE-BLOCK-END

