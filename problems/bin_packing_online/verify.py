"""Online bin packing on Weibull instances (the FunSearch setting, Romera-Paredes et al., Nature 2024).

Candidate interface (FunSearch's, github.com/google-deepmind/funsearch bin_packing notebook):
priority(item, bins) returns one score per bin; `bins` holds the remaining capacity of every
bin the item fits in, including unused bins, in bin order; the item goes to the highest score
(first on ties). There are num_items bins of capacity 100, as in FunSearch's evaluator.

Online constraint: the gate's online protocol (autoresearch/sandbox.run_online) reveals items
one at a time and waits for the decision before sending the next, so the candidate never
holds future items. DRIVER below is the trusted per-item loop that runs in the child.

Instances: item sizes drawn from Weibull(scale 45, shape 3) and clipped to 1..100, as in
FunSearch Supplementary Information E.4; 5,000 items per instance. The SI says sizes were
rounded to the nearest integer, but FunSearch's released Weibull 5k test items fit truncation
(int()) instead: mean 39.75 against 40.18 expected with rounding (z = -4.7) and 39.68 with
truncation. We truncate. Items come from salted seeds so that knowing a label does not let a
candidate regenerate the sequence.

Score per instance: L2 / bins_used, where L2 is the Martello-Toth lower bound on the optimal
number of bins. Higher is better; 1.0 would mean the lower bound was met. combined_score is the
mean over PUBLIC. Reference combined scores on PUBLIC (see experiments/bp-ceiling-v1): best
fit 0.9616, FunSearch's OR heuristic 0.9699, FunSearch's Weibull heuristic 0.9925. No
best_known is set, so nothing is flagged as a record; compare against initial.py instead.
"""
import hashlib
import math
import random
from functools import lru_cache

FUNCTION = "priority"
CAPACITY = 100
N_ITEMS = 5000
_SALT = "bin_packing_online/v1/7f3c9e"
# Two public and two hidden instances keep one evaluation under about 30 s even for a
# candidate that loops over bins in Python (about 7 s per instance); vectorised numpy
# candidates take about 0.7 s per instance.
PUBLIC = [{"name": f"instance {k}", "seed": 100 + k, "n": N_ITEMS} for k in (1, 2)]
HIDDEN = [{"name": f"hidden {k}", "seed": 900 + k, "n": N_ITEMS} for k in (1, 2)]
TIMEOUT_S = 30

DRIVER = r'''
import numpy as np

def drive(priority, header, next_input, emit):
    bins = np.full(header["num_items"], header["capacity"], dtype=np.int64)
    while True:
        item = next_input()
        if item is None:
            return
        valid = np.nonzero((bins - item) >= 0)[0]
        scores = np.asarray(priority(item, bins[valid]), dtype=np.float64)
        if scores.shape != valid.shape:
            raise ValueError(f"priority returned shape {scores.shape}; expected {valid.shape}")
        if np.isnan(scores).any():
            raise ValueError("priority returned NaN")
        chosen = int(valid[np.argmax(scores)])
        bins[chosen] -= item
        emit(chosen)
'''


@lru_cache(maxsize=64)
def items_for(seed: int, n: int) -> tuple:
    digest = hashlib.sha256(f"{_SALT}:{seed}".encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    return tuple(min(CAPACITY, max(1, int(rng.weibullvariate(45.0, 3.0)))) for _ in range(n))


def l2_bound(items, capacity=CAPACITY) -> int:
    """Martello-Toth (1990) L2 lower bound for integer item sizes."""
    counts = [0] * (capacity + 1)
    for x in items:
        counts[x] += 1
    best = math.ceil(sum(items) / capacity)
    for k in range(0, capacity // 2 + 1):
        n1 = sum(counts[capacity - k + 1:])                       # size > C - K
        j2 = range(capacity // 2 + 1, capacity - k + 1)           # C/2 < size <= C - K
        n2 = sum(counts[s] for s in j2)
        s2 = sum(s * counts[s] for s in j2)
        s3 = sum(s * counts[s] for s in range(max(k, 1), capacity // 2 + 1))   # K <= size <= C/2
        best = max(best, n1 + n2 + max(0, math.ceil((s3 - (n2 * capacity - s2)) / capacity)))
    return best


def online(instance):
    items = items_for(instance["seed"], instance["n"])
    return {"capacity": CAPACITY, "num_items": len(items)}, list(items)


def label(instance):
    items = items_for(instance["seed"], instance["n"])
    return f"{instance['name']} ({len(items)} items, lower bound {l2_bound(items)} bins)"


def best_known(instance):
    return None


def bins_used(construction, items, capacity=CAPACITY) -> int:
    if not isinstance(construction, list) or len(construction) != len(items):
        raise ValueError(f"expected one bin index per item ({len(items)})")
    load = {}
    for k, (b, x) in enumerate(zip(construction, items)):
        if not isinstance(b, int) or isinstance(b, bool) or not 0 <= b < len(items):
            raise ValueError(f"item {k}: invalid bin index")
        load[b] = load.get(b, 0) + x
        if load[b] > capacity:
            raise ValueError(f"item {k}: bin {b} over capacity")
    return len(load)


def check(construction, instance):
    items = items_for(instance["seed"], instance["n"])
    try:
        used = bins_used(construction, items)
    except ValueError as e:
        return {"valid": False, "score": None, "reason": str(e)}
    return {"valid": True, "score": l2_bound(items) / used, "reason": f"{used} bins"}
