# EVOLVE-BLOCK-START
"""Large-neighbourhood search on integer-grid square layouts.

For several grid resolutions m, squares have integer sides (in cells of 1/m).
A window of the layout is freed and re-solved exactly by branch and bound,
keeping the total square count <= n.
"""
import math
import random
import time


def _lns(m, n, deadline, rng):
    # state
    occ = [[0] * m for _ in range(m)]
    sq = {}  # id -> (x, y, a)
    nid = 1
    cnt = 0
    for idx in range(min(n, m * m)):
        x, y = idx % m, idx // m
        occ[y][x] = nid
        sq[nid] = (x, y, 1)
        nid += 1
    total = len(sq)

    sqrt = math.sqrt
    while time.time() < deadline:
        w = rng.randint(2, min(m, 5))
        h = rng.randint(2, min(m, 5))
        wx = rng.randint(0, m - w)
        wy = rng.randint(0, m - h)
        rem = set()
        for yy in range(wy, wy + h):
            for xx in range(wx, wx + w):
                v = occ[yy][xx]
                if v:
                    rem.add(v)
        x0, y0, x1, y1 = wx, wy, wx + w, wy + h
        oldsum = 0
        for r in rem:
            x, y, a = sq[r]
            oldsum += a
            x0 = min(x0, x)
            y0 = min(y0, y)
            x1 = max(x1, x + a)
            y1 = max(y1, y + a)
        c = n - (len(sq) - len(rem))
        # blocked grid
        blocked = [[True] * m for _ in range(m)]
        cells = []
        F = 0
        for yy in range(y0, y1):
            row = occ[yy]
            brow = blocked[yy]
            for xx in range(x0, x1):
                v = row[xx]
                if v == 0 or v in rem:
                    brow[xx] = False
                    cells.append((xx, yy))
                    F += 1
        ncell = len(cells)
        best = [oldsum - 1e-9]
        bestsol = [None]
        sol = []
        nodes = [0]
        limit = 6000
        shuffle_tie = rng.random() < 0.3

        def dfs(i, cur, c, F):
            nodes[0] += 1
            if nodes[0] > limit:
                return
            while i < ncell and blocked[cells[i][1]][cells[i][0]]:
                i += 1
            if i == ncell:
                if cur > best[0]:
                    best[0] = cur
                    bestsol[0] = list(sol)
                return
            if cur + sqrt(c * F) <= best[0]:
                return
            x, y = cells[i]
            if c > 0:
                s = 0
                while True:
                    t = s + 1
                    if x + t > x1 or y + t > y1:
                        break
                    ok = not blocked[y + s][x + s]
                    if ok:
                        for k in range(t):
                            if blocked[y + k][x + s] or blocked[y + s][x + k]:
                                ok = False
                                break
                    if not ok:
                        break
                    s = t
                smax = s
                sizes = list(range(smax, 0, -1))
                if shuffle_tie and len(sizes) > 1 and rng.random() < 0.5:
                    j = rng.randrange(len(sizes) - 1)
                    sizes[j], sizes[j + 1] = sizes[j + 1], sizes[j]
                for s in sizes:
                    for yy in range(y, y + s):
                        br = blocked[yy]
                        for xx in range(x, x + s):
                            br[xx] = True
                    sol.append((x, y, s))
                    dfs(i + 1, cur + s, c - 1, F - s * s)
                    sol.pop()
                    for yy in range(y, y + s):
                        br = blocked[yy]
                        for xx in range(x, x + s):
                            br[xx] = False
                    if nodes[0] > limit:
                        return
            blocked[y][x] = True
            dfs(i + 1, cur, c, F - 1)
            blocked[y][x] = False

        dfs(0, 0, c, F)
        if bestsol[0] is None:
            continue
        # apply
        for r in rem:
            x, y, a = sq.pop(r)
            for yy in range(y, y + a):
                for xx in range(x, x + a):
                    occ[yy][xx] = 0
        for (x, y, a) in bestsol[0]:
            sq[nid] = (x, y, a)
            for yy in range(y, y + a):
                for xx in range(x, x + a):
                    occ[yy][xx] = nid
            nid += 1
    val = sum(a for (_, _, a) in sq.values()) / m
    return val, [(x, y, a) for (x, y, a) in sq.values()]


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    budget = 45.0
    rng = random.Random(12345)
    k = max(1, math.isqrt(n))
    hi = min(14, 2 * k + 2)
    ms = list(range(k, hi + 1))
    if n > 400:
        ms = [k]
    best_val = -1.0
    best_sq = None
    for idx, m in enumerate(ms):
        remaining = budget - (time.time() - t0)
        if remaining <= 0.5:
            break
        slice_t = remaining / (len(ms) - idx)
        val, sqs = _lns(m, n, time.time() + slice_t, rng)
        if val > best_val + 1e-12:
            best_val = val
            best_sq = (m, sqs)
    m, sqs = best_sq
    out = []
    eps = 1e-9
    for (x, y, a) in sqs:
        if len(out) >= n:
            break
        side = a / m - eps
        cx = (x + a / 2.0) / m
        cy = (y + a / 2.0) / m
        out.append((cx, cy, 0.0, side))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
