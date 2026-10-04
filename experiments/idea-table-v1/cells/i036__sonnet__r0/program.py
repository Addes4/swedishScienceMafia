# EVOLVE-BLOCK-START
"""Upper-bound-pruned skyline search over integer-sided axis-aligned squares."""
import math
import time
import sys


class _Timeout(Exception):
    pass


def _grid(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    return sq, k * side


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    sys.setrecursionlimit(20000)
    t0 = time.time()
    total_budget = 50.0
    end_all = t0 + total_budget

    best_sq, best_val = _grid(n)
    best = [best_val, best_sq]

    k = math.isqrt(n)
    Ls = set(range(1, 13))
    for v in (k, k + 1, 2 * k + 1):
        if 1 <= v <= 40:
            Ls.add(v)
    Ls = sorted(Ls)

    for idx, L in enumerate(Ls):
        now = time.time()
        if now >= end_all:
            break
        slice_end = min(end_all, now + (end_all - now) / (len(Ls) - idx))
        h = [0] * L
        placed = []
        state = {"cnt": 0, "bestsum": -1}
        LL = L * L

        def dfs(used, cur, filled):
            state["cnt"] += 1
            if (state["cnt"] & 1023) == 0 and time.time() > slice_end:
                raise _Timeout()
            real = cur / L
            if real > best[0] + 1e-12:
                best[0] = real
                best[1] = list(placed)
            m = n - used
            rem = LL - filled
            if rem <= 0:
                return
            if m > 0:
                if (cur + math.sqrt(m * rem)) / L <= best[0] + 1e-12:
                    return
            else:
                return
            # lowest-leftmost column
            c = 0
            hc = h[0]
            for i in range(1, L):
                if h[i] < hc:
                    hc = h[i]
                    c = i
            w = 1
            while c + w < L and h[c + w] == hc:
                w += 1
            smax = min(w, L - hc)
            for s in range(smax, 0, -1):
                for i in range(c, c + s):
                    h[i] += s
                placed.append((c, hc, s))
                dfs(used + 1, cur + s, filled + s * s)
                placed.pop()
                for i in range(c, c + s):
                    h[i] -= s
            # waste: raise run to lower neighbour
            nb = []
            if c > 0:
                nb.append(h[c - 1])
            if c + w < L:
                nb.append(h[c + w])
            if nb:
                nh = min(nb)
                for i in range(c, c + w):
                    h[i] = nh
                dfs(used, cur, filled + w * (nh - hc))
                for i in range(c, c + w):
                    h[i] = hc

        try:
            dfs(0, 0, 0)
        except _Timeout:
            pass

        # best[1] may be mixed: convert if it's a list of tuples (cx,cy,s) ints
        # (we store with L context, so convert immediately)
        if best[1] and len(best[1][0]) == 3:
            best[1] = [((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / L) for (x, y, s) in best[1]]

    res = list(best[1])
    res = res[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    out = []
    for (x, y, a, s) in res:
        s = min(max(s, 0.0), 1.0)
        out.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), a, s))
    return out
# EVOLVE-BLOCK-END
