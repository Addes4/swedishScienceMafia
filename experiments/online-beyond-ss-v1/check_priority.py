"""Check that priority_fss.priority, run through FunSearch's full evaluator, gives the same bin
counts as the C packer (fast.pack_fss), on several instances in one process (state reset works)."""
import importlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import priority_fss  # noqa: E402
from fast import pack_fss  # noqa: E402
from sim import weibull_items  # noqa: E402


def funsearch_full(items, C, priority):
    """FunSearch's evaluator verbatim in effect: num_items bins, all passed when the item fits."""
    bins = np.array([C for _ in range(len(items))])
    for item in items:
        valid = np.nonzero((bins - item) >= 0)[0]
        j = valid[np.argmax(priority(item, bins[valid]))]
        bins[j] -= item
    return int((bins != C).sum())


if __name__ == "__main__":
    for beta, alpha, c in [(1.0, 0.0, 1.1), (2.0, 0.5, 1.5)]:
        priority_fss.BETA, priority_fss.ALPHA, priority_fss.SWITCH_C = beta, alpha, c
        priority_fss._state = None
        for seed in range(97200, 97203):
            for C in (100, 150):
                items = [min(x, C) for x in weibull_items(seed, 1500)]
                a = funsearch_full(items, C, priority_fss.priority)
                b = pack_fss(items, C, beta, c, alpha)
                assert a == b, (beta, alpha, c, seed, C, a, b)
    print("priority_fss through FunSearch's evaluator matches fast.pack_fss on 12 instances")
