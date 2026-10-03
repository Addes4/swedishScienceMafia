# EVOLVE-BLOCK-START
"""Multiset-first packing: enumerate multisets of integer sides on a D x D board,
rank by sum of sides, and test packability with a skyline backtracking search."""
import math
import time
import heapq
import sys
from fractions import Fraction


class _Abort(Exception):
    pass


def _gen_candidates(n, D, K, deadline):
    """Top-K multisets (count vector indexed by size 1..D) maximising sum of sides,
    with count <= n and sum of squares <= D^2."""
    heap = []
    counts = [0] * (D + 1)
    cnt = [0]

    def push(val):
        item = (val, tuple(counts))
        if len(heap) < K:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)

    def dfs(s, cnt_left, area_left, value):
        cnt[0] += 1
        if (cnt[0] & 1023) == 0 and time.time() > deadline:
            return
        if len(heap) >= K and value + math.sqrt(cnt_left * area_left) < heap[0][0] - 1e-9:
            return
        if s == 1:
            c = min(cnt_left, area_left)
            counts[1] = c
            push(value + c)
            counts[1] = 0
            return
        mx = min(cnt_left, area_left // (s * s))
        for c in range(mx, -1, -1):
            counts[s] = c
            dfs(s - 1, cnt_left - c, area_left - c * s * s, value + c * s)
        counts[s] = 0

    dfs(D, n, D * D, 0)
    return [(v, c) for v, c in heap]


def _pack(D, counts, node_limit, deadline):
    """Skyline backtracking. counts[s] = number of squares of side s.
    Returns list of (x, y, s) or None; raises _Abort on node limit."""
    rem = list(counts)
    sizes = [s for s in range(D, 0, -1) if rem[s] > 0]
    total = sum(rem)
    area = sum(rem[s] * s * s for s in sizes)
    allowed_waste = D * D - area
    h = [0] * D
    placed = []
    failed = set()
    nodes = [0]
    INF = 10 ** 9

    def rec(left, waste):
        if left == 0:
            return True
        nodes[0] += 1
        if nodes[0] > node_limit or ((nodes[0] & 255) == 0 and time.time() > deadline):
            raise _Abort()
        key = (tuple(h), tuple(rem))
        if key in failed:
            return False
        hmin = min(h)
        i = h.index(hmin)
        j = i
        while j < D and h[j] == hmin:
            j += 1
        w = j - i
        for s in sizes:
            if rem[s] > 0 and s <= w and hmin + s <= D:
                rem[s] -= 1
                for t in range(i, i + s):
                    h[t] += s
                placed.append((i, hmin, s))
                if rec(left - 1, waste):
                    return True
                placed.pop()
                for t in range(i, i + s):
                    h[t] -= s
                rem[s] += 1
        # waste option
        lh = h[i - 1] if i > 0 else INF
        rh = h[j] if j < D else INF
        nh = min(lh, rh, D)
        if nh > hmin:
            nw = waste + w * (nh - hmin)
            if nw <= allowed_waste:
                for t in range(i, j):
                    h[t] = nh
                if rec(left, nw):
                    return True
                for t in range(i, j):
                    h[t] = hmin
        failed.add(key)
        return False

    if rec(total, 0):
        return list(placed)
    return None


def _grid(n):
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    sys.setrecursionlimit(20000)
    t0 = time.time()
    gen_end = t0 + 15.0
    total_end = t0 + 48.0
    maxD = 12
    if n <= 1:
        return [(0.5, 0.5, 0.0, 1.0)] * n
    cands = []
    seen = set()
    for D in range(1, maxD + 1):
        now = time.time()
        if now > gen_end:
            break
        dl = min(gen_end, now + 2.0)
        for val, c in _gen_candidates(n, D, 60, dl):
            key = tuple(sorted(
                (Fraction(s, D), c[s]) for s in range(1, D + 1) if c[s] > 0))
            if key in seen:
                continue
            seen.add(key)
            cands.append((val / D, D, c))
    cands.sort(key=lambda t: -t[0])

    best = None
    for val, D, c in cands:
        if time.time() > total_end:
            break
        try:
            res = _pack(D, c, 30000, total_end)
        except _Abort:
            continue
        if res is not None:
            best = (D, res)
            break

    if best is None:
        return _grid(n)
    D, res = best
    out = []
    for x, y, s in res:
        out.append(((x + s / 2.0) / D, (y + s / 2.0) / D, 0.0, s / D))
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out[:n]
# EVOLVE-BLOCK-END
