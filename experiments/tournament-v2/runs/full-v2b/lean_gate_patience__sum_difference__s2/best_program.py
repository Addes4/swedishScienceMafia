"""Approach: structured 'digit-sum' sets (numbers with exactly k ones in binary)
have small sum sets and large difference sets. To evaluate many/large candidates
fast, score with numpy bitset shifts instead of O(n^2) Python sets. Scan a wide
range of (m, k), including larger sets up to the 4000 limit, plus some derived
variants, and pick the best."""
import math
import time
from itertools import combinations
import numpy as np


def _bitset_pair(a):
    """Given list of ints, return counts of distinct differences and sums using
    numpy bit packing."""
    a = np.array(sorted(set(a)), dtype=np.int64)
    n = a.shape[0]
    dmin = int(a[0] - a[-1])
    dmax = int(a[-1] - a[0])
    smin = int(a[0] + a[0])
    smax = int(a[-1] + a[-1])

    def make_bits(vals, lo, hi):
        width = hi - lo + 1
        words = (width + 63) // 64
        bits = np.zeros(words, dtype=np.int64)
        idx = vals - lo
        w = idx >> 6
        b = idx & 63
        np.bitwise_or.at(bits, w, (np.int64(1) << b).astype(np.int64))
        return bits

    diff = (a[:, None] - a[None, :]).ravel()
    dbits = make_bits(diff.astype(np.int64), dmin, dmax)
    ndistinct_d = int(np.unpackbits(dbits.view(np.uint8)).sum())

    ssum = (a[:, None] + a[None, :]).ravel()
    sbits = make_bits(ssum.astype(np.int64), smin, smax)
    ndistinct_s = int(np.unpackbits(sbits.view(np.uint8)).sum())

    return ndistinct_d, ndistinct_s


def _score(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _bitset_pair(a)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / n) / 100


def _digit_set(m, k):
    out = []
    for comb in combinations(range(m), k):
        v = 0
        for b in comb:
            v |= (1 << b)
        out.append(v)
    return out


def _digit_set_complement(m, k):
    """Numbers with exactly m-k ones among m bits = bitwise complement within m bits."""
    full = (1 << m) - 1
    return [full ^ v for v in _digit_set(m, m - k)]


def solve():
    deadline = time.time() + 100
    best = None
    best_s = -1.0
    NMAX = 4000

    def consider(A):
        nonlocal best, best_s
        A = sorted(set(A))
        n = len(A)
        if n < 2 or n > NMAX:
            return
        s = _score(A)
        if s > best_s:
            best_s = s
            best = A

    # Digit-sum sets: numbers with exactly k ones in m bits.
    for m in range(6, 30):
        for k in range(1, m):
            size = math.comb(m, k)
            if size < 2 or size > NMAX:
                continue
            consider(_digit_set(m, k))
        if time.time() > deadline:
            break

    # Also try multiples/affine offsets and small dilations of the best, which
    # leave the ratio almost unchanged but can pad the size bonus slightly.
    if best is not None:
        for off in (0, 1, -1, 2, -2):
            candidate = [v + off for v in best]
            # respect absolute bound
            if max(abs(v) for v in candidate) <= 10**15:
                consider(candidate)
            if time.time() > deadline:
                break

    return best if best else [0, 1]
