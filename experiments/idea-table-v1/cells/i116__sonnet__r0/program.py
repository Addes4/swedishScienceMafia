# EVOLVE-BLOCK-START
"""Exact integer-board skyline DP (L <= 10) over axis-aligned square dissections,
with a k x k grid fallback."""
import math
import time
import sys


class _Timeout(Exception):
    pass


def _grid(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    return float(k), sq


def _dp_board(L, n, deadline):
    """Best tiling of LxL board with at most n integer squares. Returns (sum, list) or None."""
    memo = {}
    counter = [0]
    NEG = -1

    def F(state, rem, area):
        # area = remaining area
        if area == 0:
            return 0
        if rem <= 0:
            return NEG
        if rem > area:
            rem = area
        key = (state, rem)
        r = memo.get(key)
        if r is not None:
            return r
        counter[0] += 1
        if (counter[0] & 1023) == 0 and time.time() > deadline:
            raise _Timeout()
        h = min(state)
        i = state.index(h)
        w = 1
        while i + w < L and state[i + w] == h:
            w += 1
        smax = min(w, L - h)
        if rem * smax * smax < area:
            memo[key] = NEG
            return NEG
        best = NEG
        for s in range(smax, 0, -1):
            ns = state[:i] + (h + s,) * s + state[i + s:]
            v = F(ns, rem - 1, area - s * s)
            if v >= 0 and v + s > best:
                best = v + s
        memo[key] = best
        return best

    start = tuple([0] * L)
    total = L * L
    best = F(start, n, total)
    if best < 0:
        return None
    # reconstruct
    out = []
    state = start
    rem = n
    area = total
    while area > 0:
        h = min(state)
        i = state.index(h)
        w = 1
        while i + w < L and state[i + w] == h:
            w += 1
        smax = min(w, L - h)
        target = F(state, rem, area)
        chosen = None
        for s in range(smax, 1 - 1, -1):
            if s < 1:
                break
            ns = state[:i] + (h + s,) * s + state[i + s:]
            v = F(ns, rem - 1, area - s * s)
            if v >= 0 and v + s == target:
                chosen = (s, ns)
                break
        if chosen is None:
            return None
        s, ns = chosen
        out.append((i, h, s))
        state = ns
        rem -= 1
        area -= s * s
    return best, out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    deadline_total = t0 + 40.0
    best_val, best_sq = _grid(n)
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, 10000))
    try:
        for L in range(1, 11):
            if time.time() > deadline_total:
                break
            try:
                res = _dp_board(L, n, deadline_total)
            except _Timeout:
                break
            except RecursionError:
                break
            if res is None:
                continue
            tot, pieces = res
            val = tot / L
            if val > best_val + 1e-12:
                best_val = val
                best_sq = [((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / L)
                           for (x, y, s) in pieces]
    finally:
        sys.setrecursionlimit(old)
    squares = list(best_sq)
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END
