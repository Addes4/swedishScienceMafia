"""Long-instance evaluator: rule packers and linear policies in C++, FunSearch-style code in Python.

- pack_rule(items, 'best_fit' | 'first_fit' | 'worst_fit', capacity)
- pack_linear(weights, items): the 20 contextual features of contextual.py over open bins
  (20 weights), or over open bins plus one unused bin with an extra "new bin" feature (21).
- pack_priority(priority, items, capacity): FunSearch's evaluator semantics exactly: num_items
  bins of full capacity, priority(item, bins[valid]) over every bin the item fits in (unused
  bins included), argmax with first index on ties.
- weibull_items(seed, n): Weibull(scale 45, shape 3) sizes truncated to integers in 1..100.
- l1_bound, l2_bound: lower bounds on the optimal number of bins (Martello and Toth 1990).
"""
import ctypes
import hashlib
import math
import random
import subprocess
import sys
from pathlib import Path

from .contextual import CONTEXT_BEST_FIT
from .core import instance as falsify_instance

LIB = None
RULES = {'best_fit': 0, 'first_fit': 1, 'worst_fit': 2}
LINEAR_OPEN_BEST_FIT = list(CONTEXT_BEST_FIT) + [0.]


def _lib():
    global LIB
    if LIB is None:
        source = Path(__file__).with_name('longpack.cpp')
        binary = source.with_name('_longpack.dylib' if sys.platform == 'darwin' else '_longpack.so')
        if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
            subprocess.run(['c++', '-O3', '-std=c++17', '-ffp-contract=off', '-shared', '-fPIC', str(source), '-o', str(binary)],
                           check=True)
        lib = ctypes.CDLL(str(binary))
        lib.pack_rule.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int)]
        lib.pack_rule.restype = ctypes.c_int
        lib.pack_linear.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(ctypes.c_double),
                                    ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        lib.pack_linear.restype = ctypes.c_int
        LIB = lib
    return LIB


class Instance:
    """Validated item buffer for repeated native evaluations."""
    def __init__(self, items, family='', capacity=100):
        self.items = tuple(int(x) for x in items)
        self.family = family
        self.capacity = capacity
        if not all(1 <= x <= capacity for x in self.items):
            raise ValueError('items must be integers in 1..capacity')
        self.buffer = (ctypes.c_int * len(self.items))(*self.items)

    def __len__(self):
        return len(self.items)


def _as_instance(items, capacity=100):
    return items if isinstance(items, Instance) else Instance(items, capacity=capacity)


def pack_rule(items, rule='best_fit', capacity=100, trace=False):
    inst = _as_instance(items, capacity)
    out = (ctypes.c_int * len(inst))() if trace else None
    bins = _lib().pack_rule(inst.buffer, len(inst), inst.capacity, RULES[rule], out)
    if bins < 0:
        raise ValueError('invalid instance')
    return (bins, list(out)) if trace else bins


def pack_linear(weights, items, trace=False):
    if len(weights) not in (20, 21) or not all(math.isfinite(w) for w in weights):
        raise ValueError('20 or 21 finite weights required')
    inst = _as_instance(items)
    if inst.capacity != 100:
        raise ValueError('linear features assume capacity 100')
    ws = (ctypes.c_double * len(weights))(*weights)
    out = (ctypes.c_int * len(inst))() if trace else None
    bins = _lib().pack_linear(inst.buffer, len(inst), ws, len(weights), int(len(weights) == 21), out)
    if bins < 0:
        raise ValueError('invalid instance or non-finite scores')
    return (bins, list(out)) if trace else bins


def pack_priority(priority, items, capacity=100, trace=False):
    """FunSearch's online_binpack + evaluate for one instance; returns bins used."""
    import numpy as np
    items = list(items.items) if isinstance(items, Instance) else list(items)
    bins = np.array([capacity for _ in range(len(items))])
    assignment = []
    for item in items:
        valid = np.nonzero((bins - item) >= 0)[0]
        chosen = valid[np.argmax(priority(item, bins[valid]))]
        bins[chosen] -= item
        assignment.append(int(chosen))
    used = int((bins != capacity).sum())
    return (used, assignment) if trace else used


def weibull_items(seed, n, namespace='bp-ceiling-v1'):
    """Weibull(45, 3) sizes truncated to 1..100, from a salted, versioned seed."""
    digest = hashlib.sha256(f'{namespace}:{seed}'.encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], 'big'))
    return [min(100, max(1, int(rng.weibullvariate(45.0, 3.0)))) for _ in range(n)]


def falsify_items(seed, family, n=80):
    """One instance of a falsify.core family, at any length."""
    return falsify_instance(random.Random(seed), family, n)


def l1_bound(items, capacity=100):
    return math.ceil(sum(items) / capacity)


def l2_bound(items, capacity=100):
    """Martello-Toth L2: max over K <= C/2 of |N1| + |N2| + max(0, ceil((S3 - (|N2| C - S2)) / C))."""
    import numpy as np
    counts = np.bincount(np.asarray(items, dtype=np.int64), minlength=capacity + 1)
    sizes = np.arange(capacity + 1)
    half = capacity // 2
    best = l1_bound(items, capacity)
    for k in range(half + 1):
        n1 = counts[capacity - k + 1:].sum()
        mid = slice(half + 1, capacity - k + 1)
        n2, s2 = counts[mid].sum(), (sizes[mid] * counts[mid]).sum()
        small = slice(max(k, 1), half + 1)
        s3 = (sizes[small] * counts[small]).sum()
        best = max(best, int(n1 + n2 + max(0, math.ceil((s3 - (n2 * capacity - s2)) / capacity))))
    return best
