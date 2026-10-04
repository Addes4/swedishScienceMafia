# EVOLVE-BLOCK-START
"""Multiset-first packing: for each integer board size D, enumerate multisets of
integer sides (sum S, count n, area <= D^2) in decreasing S, and test each for
exact packability with a bottom-left backtracking search on the D x D grid."""
import math
import sys
import time


class _Limit(Exception):
    pass


def _gen(n, D, S):
    """Yield descending lists of positive integer sides, length <= n,
    sum exactly S, sum of squares <= D*D, each side <= D."""
    out = []

    def rec(k, m, R, A):
        if R == 0:
            yield list(out)
            return
        if k == 0:
            return
        if R > k * m:
            return
        if R * R > k * A:
            return
        lo = -(-R // k)
        hi = min(m, R)
        for s in range(hi, lo - 1, -1):
            if s * s > A:
                continue
            out.append(s)
            yield from rec(k - 1, s, R - s, A - s * s)
            out.pop()

    yield from rec(n, D, S, D * D)


def _can_pack(sides, D, node_limit, deadline):
    counts = {}
    for s in sides:
        counts[s] = counts.get(s, 0) + 1
    sizes = sorted(counts.keys(), reverse=True)
    full = (1 << D) - 1
    rows = [0] * D
    waste = [D * D - sum(s * s for s in sides)]
    remaining = [len(sides)]
    pos = []
    nodes = [0]

    def rec(r):
        if remaining[0] == 0:
            return True
        nodes[0] += 1
        if nodes[0] > node_limit:
            raise _Limit()
        if (nodes[0] & 1023) == 0 and time.time() > deadline:
            raise _Limit()
        while r < D and rows[r] == full:
            r += 1
        if r == D:
            return False
        free = ~rows[r] & full
        c = (free & -free).bit_length() - 1
        for s in sizes:
            if counts[s] == 0:
                continue
            if r + s > D or c + s > D:
                continue
            mask = ((1 << s) - 1) << c
            ok = True
            for rr in range(r, r + s):
                if rows[rr] & mask:
                    ok = False
                    break
            if not ok:
                continue
            for rr in range(r, r + s):
                rows[rr] |= mask
            counts[s] -= 1
            remaining[0] -= 1
            pos.append((c, r, s))
            if rec(r):
                return True
            pos.pop()
            remaining[0] += 1
            counts[s] += 1
            for rr in range(r, r + s):
                rows[rr] &= ~mask
        if waste[0] > 0:
            bit = 1 << c
            rows[r] |= bit
            waste[0] -= 1
            if rec(r):
                return True
            waste[0] += 1
            rows[r] &= ~bit
        return False

    try:
        if rec(0):
            return list(pos)
    except _Limit:
        return None
    return None


def solve(n):
    sys.setrecursionlimit(10000)
    t0 = time.time()
    total_deadline = t0 + 45.0
    if n <= 0:
        return []
    # baseline grid
    k = math.isqrt(n)
    best_val = float(k)
    best_D = k
    best_pos = [(i, j, 1) for i in range(k) for j in range(k)]

    Dmax = max(4, int(math.ceil(3 * math.sqrt(n))) + 2)
    Dmax = min(Dmax, 30)
    Ds = list(range(1, Dmax + 1))
    for idx, D in enumerate(Ds):
        now = time.time()
        if now > total_deadline:
            break
        remD = len(Ds) - idx
        d_deadline = min(total_deadline, now + (total_deadline - now) / remD * 1.5)
        Smax = min(n * D, int(math.floor(math.sqrt(n) * D + 1e-9)))
        Smin = int(math.floor(best_val * D + 1e-9)) + 1
        done = False
        for S in range(Smax, Smin - 1, -1):
            if done or time.time() > d_deadline:
                break
            tested = 0
            for ms in _gen(n, D, S):
                if time.time() > d_deadline:
                    break
                tested += 1
                if tested > 3000:
                    break
                p = _can_pack(ms, D, 60000, d_deadline)
                if p is not None:
                    best_val = S / D
                    best_D = D
                    best_pos = p
                    done = True
                    break

    D = best_D
    res = []
    for (x, y, s) in best_pos:
        res.append(((x + s / 2.0) / D, (y + s / 2.0) / D, 0.0, s / D))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
