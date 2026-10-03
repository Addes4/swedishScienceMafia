# EVOLVE-BLOCK-START
"""Exact integer tiling DP (skyline) on L x L boards, scaled by 1/L, padded with zero squares."""
import math
import time


def _tile(L, n, deadline):
    start = tuple([0] * L)
    # best[state] = {cnt: (sum, prev_state, side)}
    best = {start: {0: (0, None, 0)}}
    buckets = [[] for _ in range(L * L + 1)]
    buckets[0].append(start)
    full = tuple([L] * L)
    it = 0
    for area in range(L * L):
        for st in buckets[area]:
            it += 1
            if (it & 255) == 0 and time.time() > deadline:
                return None
            d = best[st]
            m = min(st)
            i = st.index(m)
            w = 1
            while i + w < L and st[i + w] == m:
                w += 1
            smax = min(w, L - m)
            for s in range(1, smax + 1):
                ns = list(st)
                for j in range(i, i + s):
                    ns[j] = m + s
                ns = tuple(ns)
                nd = best.get(ns)
                if nd is None:
                    nd = {}
                    best[ns] = nd
                    buckets[area + s * s].append(ns)
                for c, (v, _, _) in d.items():
                    if c + 1 > n:
                        continue
                    nv = v + s
                    old = nd.get(c + 1)
                    if old is None or nv > old[0]:
                        nd[c + 1] = (nv, st, s)
        # free memory not needed for bookkeeping of backpointers
    if full not in best:
        return None
    d = best[full]
    if not d:
        return None
    c = max(d, key=lambda k: d[k][0])
    total = d[c][0]
    # reconstruct
    sq = []
    st = full
    while c > 0:
        v, prev, s = best[st][c]
        m = min(prev)
        i = prev.index(m)
        sq.append((i, m, s))
        st = prev
        c -= 1
    return total, sq


def solve(n):
    t0 = time.time()
    deadline = t0 + 40.0
    k = math.isqrt(n)
    bestval = float(k)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    for L in range(2, 14):
        if time.time() > deadline:
            break
        r = _tile(L, n, deadline)
        if r is None:
            break
        total, sq = r
        val = total / L
        if val > bestval + 1e-12:
            bestval = val
            squares = [((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / L) for (x, y, s) in sq]
    squares = list(squares)
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END
