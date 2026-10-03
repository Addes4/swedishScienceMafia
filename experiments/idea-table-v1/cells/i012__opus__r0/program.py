# EVOLVE-BLOCK-START
"""Exact skyline DP over dissections of an integer LxL board into integer squares
(with optional empty unit cells), recording the best total of sides per square count."""
import math
import sys
import time
import numpy as np


class _Timeout(Exception):
    pass


NEG = -10 ** 9


def _run(L, n, deadline, max_states=1_500_000):
    memo = {}
    term = np.full(n + 1, NEG, dtype=np.int64)
    term[0] = 0
    counter = [0]

    def f(sky):
        rev = sky[::-1]
        key = sky if sky <= rev else rev
        r = memo.get(key)
        if r is not None:
            return r
        h = min(sky)
        if h == L:
            memo[key] = term
            return term
        counter[0] += 1
        if (counter[0] & 1023) == 0:
            if time.time() > deadline or len(memo) > max_states:
                raise _Timeout()
        i = sky.index(h)
        w = 1
        while i + w < L and sky[i + w] == h:
            w += 1
        # empty cell
        nxt = sky[:i] + (h + 1,) + sky[i + 1:]
        res = f(nxt).copy()
        for s in range(1, min(w, L - h) + 1):
            nxt = sky[:i] + (h + s,) * s + sky[i + s:]
            sub = f(nxt)
            cand = np.full(n + 1, NEG, dtype=np.int64)
            cand[1:] = sub[:-1] + s
            np.maximum(res, cand, out=res)
        memo[key] = res
        return res

    start = (0,) * L
    root = f(start)
    valid = np.where(root >= 0, root, NEG)
    c = int(np.argmax(valid))
    val = int(valid[c])
    if val <= 0:
        return 0, []
    # reconstruct
    placements = []
    sky = start
    while min(sky) < L:
        h = min(sky)
        i = sky.index(h)
        w = 1
        while i + w < L and sky[i + w] == h:
            w += 1
        nxt = sky[:i] + (h + 1,) + sky[i + 1:]
        if int(f(nxt)[c]) == val:
            sky = nxt
            continue
        found = False
        for s in range(1, min(w, L - h) + 1):
            nxt = sky[:i] + (h + s,) * s + sky[i + s:]
            if c >= 1 and int(f(nxt)[c - 1]) + s == val:
                placements.append((i, h, s))
                sky = nxt
                c -= 1
                val -= s
                found = True
                break
        if not found:
            break
    total = sum(p[2] for p in placements)
    return total, placements


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    sys.setrecursionlimit(100000)
    t0 = time.time()
    deadline = t0 + 45.0

    # baseline grid
    k = math.isqrt(n)
    best_val = 1.0 * k / k if k > 0 else 0.0
    best_val = float(k)
    best = [((i + 0.5) / k, (j + 0.5) / k, 0.0, 1.0 / k) for i in range(k) for j in range(k)]

    L = 1
    while L <= 60:
        if time.time() > deadline:
            break
        try:
            total, placements = _run(L, n, deadline)
        except _Timeout:
            break
        except RecursionError:
            break
        if placements and len(placements) <= n and total / L > best_val + 1e-12:
            best_val = total / L
            best = [((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / L) for (x, y, s) in placements]
        L += 1

    squares = list(best[:n])
    squares += [(0.0, 0.0, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
