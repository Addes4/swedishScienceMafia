# EVOLVE-BLOCK-START
"""Upper-bound-pruned exhaustive search over axis-aligned packings on L x L grids,
in bottom-left skyline order, with waste cells allowed (holes)."""
import math
import sys
import time


class _Timeout(Exception):
    pass


def _search(n, L, best_val, deadline):
    """Search packings of the L x L grid with at most n squares.
    Returns (value, placements) if something strictly better than best_val is found,
    else (best_val, None)."""
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
    heights = [0] * L
    placed = []
    LL = L * L
    state = {"best": best_val * L, "sol": None, "nodes": 0}
    sq = [math.sqrt(i) for i in range(n * LL + 1)]
    eps = 1e-9

    def dfs(c, S, F):
        if S > state["best"] + eps:
            state["best"] = float(S)
            state["sol"] = list(placed)
        r = n - c
        A = LL - F
        if r == 0 or A == 0:
            return
        if S + sq[r * A] <= state["best"] + eps:
            return
        state["nodes"] += 1
        if (state["nodes"] & 2047) == 0 and time.time() > deadline:
            raise _Timeout()
        # lowest, leftmost position
        h = L + 1
        x = 0
        for i in range(L):
            if heights[i] < h:
                h = heights[i]
                x = i
        if h >= L:
            return
        w = 1
        while x + w < L and heights[x + w] == h:
            w += 1
        maxs = min(w, L - h)
        for s in range(maxs, 0, -1):
            # bound with this square placed
            nA = A - s * s
            nS = S + s
            if r - 1 > 0 and nA > 0:
                if nS + sq[(r - 1) * nA] <= state["best"] + eps:
                    # smaller s may still be ok (bound not monotone), continue
                    if nS <= state["best"] + eps:
                        continue
            for k in range(x, x + s):
                heights[k] += s
            placed.append((x, h, s))
            dfs(c + 1, nS, F + s * s)
            placed.pop()
            for k in range(x, x + s):
                heights[k] -= s
        # waste one cell
        if S + sq[r * (A - 1)] > state["best"] + eps:
            heights[x] += 1
            dfs(c, S, F + 1)
            heights[x] -= 1

    try:
        dfs(0, 0, 0)
    except _Timeout:
        pass
    if state["sol"] is not None:
        return state["best"] / L, state["sol"]
    return best_val, None


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    start = time.time()
    budget = 46.0
    # baseline grid
    k = math.isqrt(n)
    best_val = float(k)
    best_sol = [(i, j, 1) for i in range(k) for j in range(k)]
    best_L = k

    Ls = list(range(1, 17))
    for idx, L in enumerate(Ls):
        now = time.time()
        remaining = budget - (now - start)
        if remaining <= 0.05:
            break
        left = len(Ls) - idx
        cap = max(remaining / max(1, min(left, 5)), 0.5)
        deadline = min(start + budget, now + cap)
        val, sol = _search(n, L, best_val, deadline)
        if sol is not None and val > best_val + 1e-12:
            best_val = val
            best_sol = sol
            best_L = L

    L = best_L
    shrink = 1.0 - 1e-12
    squares = []
    for (x, y, s) in best_sol:
        cx = (x + s / 2.0) / L
        cy = (y + s / 2.0) / L
        squares.append((cx, cy, 0.0, (s / L) * shrink))
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
