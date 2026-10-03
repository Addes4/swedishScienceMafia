"""Sum-difference problem II (problem 43, Georgiev, Gómez-Serrano, Tao, Wagner 2025).

Score (official): log|A - A| / log|A + A| + (1 - 1/|A|) / 100 for a finite set A of integers.
Best known lower bound for the underlying constant: log(1 + sqrt 2) / log 2 = 1.2715...,
from a high-dimensional simplex construction; AlphaEvolve without hints reached about 1.21.
Note the 1.2715 is an asymptotic value: finite sets approach it from below.
"""
import math

import numpy as np

FUNCTION = "solve"
PUBLIC = [{}]
HIDDEN = []
TIMEOUT_S = 120
MAX_SIZE = 4000
BEST_KNOWN = math.log(1 + math.sqrt(2)) / math.log(2)


def label(instance):
    return "sum-difference"


def best_known(instance):
    return BEST_KNOWN


def _parse(construction):
    if not isinstance(construction, list) or len(construction) < 2:
        raise ValueError("expected a list of at least 2 integers")
    if len(construction) > MAX_SIZE:
        raise ValueError(f"more than {MAX_SIZE} elements")
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in construction):
        raise ValueError("every element must be an integer")
    if max(abs(v) for v in construction) > 10 ** 15:
        raise ValueError("elements must have absolute value at most 1e15")
    return sorted(set(construction))


def _score(a):
    v = np.array(a, dtype=np.int64)
    diffs = np.unique((v[:, None] - v[None, :]).ravel()).size
    sums = np.unique((v[:, None] + v[None, :]).ravel()).size
    return math.log(diffs) / math.log(sums) + (1.0 - 1.0 / len(a)) / 100.0


def check(construction, instance):
    try:
        a = _parse(construction)
    except ValueError as e:
        return {"valid": False, "score": None, "reason": str(e)}
    if len(a) < 2:
        return {"valid": False, "score": None, "reason": "need at least 2 distinct integers"}
    return {"valid": True, "score": _score(a), "reason": ""}


def check_strict(construction, instance):
    """Independent recomputation with Python sets (no numpy)."""
    try:
        a = _parse(construction)
    except ValueError:
        return False
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    score = math.log(len(diffs)) / math.log(len(sums)) + (1.0 - 1.0 / len(a)) / 100.0
    return abs(score - _score(a)) < 1e-12
