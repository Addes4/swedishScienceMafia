# EVOLVE-BLOCK-START
"""GRASP + path relinking on integer boards (axis-aligned tilings of an m x m board)."""
import math
import random
import time


def _fill(h, w, q, rng):
    grid = [[0] * w for _ in range(h)]
    out = []
    for r in range(h):
        for c in range(w):
            if grid[r][c]:
                continue
            s = 1
            while r + s < h and c + s < w:
                ok = True
                for i in range(r, r + s + 1):
                    if grid[i][c + s]:
                        ok = False
                        break
                if ok:
                    row = grid[r + s]
                    for j in range(c, c + s + 1):
                        if row[j]:
                            ok = False
                            break
                if not ok:
                    break
                s += 1
            smax = s
            if rng.random() < q:
                s = smax
            else:
                s = rng.randint(1, smax)
            for i in range(r, r + s):
                row = grid[i]
                for j in range(c, c + s):
                    row[j] = 1
            out.append((r, c, s))
    return out


def _split(layout, r0, c0, r1, c1):
    """Return (inside, outside) or None if some square crosses the rectangle border."""
    ins, outs = [], []
    for (r, c, s) in layout:
        if r >= r0 and c >= c0 and r + s <= r1 and c + s <= c1:
            ins.append((r, c, s))
        elif r >= r1 or c >= c1 or r + s <= r0 or c + s <= c0:
            outs.append((r, c, s))
        else:
            return None
    return ins, outs


def _add(pool, layout, n, cap=30):
    cnt = len(layout)
    if cnt > n:
        return
    tot = sum(s for _, _, s in layout)
    key = tuple(sorted(layout))
    for t, cc, lay, k in pool:
        if k == key:
            return
    if len(pool) >= cap and tot <= pool[-1][0]:
        return
    pool.append((tot, cnt, layout, key))
    pool.sort(key=lambda x: (-x[0], x[1]))
    del pool[cap:]


def solve(n):
    t0 = time.time()
    budget = 22.0
    rng = random.Random(12345 + n)
    k = max(1, math.isqrt(n))
    ms = list(range(k, min(2 * k + 3, k + 9)))
    pools = {m: [] for m in ms}
    # seed with the plain grid
    pools[k].append((k * k, k * k, [(i, j, 1) for i in range(k) for j in range(k)],
                     tuple(sorted((i, j, 1) for i in range(k) for j in range(k)))))
    it = 0
    while time.time() - t0 < budget:
        it += 1
        for m in ms:
            pool = pools[m]
            if len(pool) < 6 or rng.random() < 0.15:
                lay = _fill(m, m, rng.random(), rng)
                _add(pool, lay, n)
                continue
            a = pool[int(len(pool) * rng.random() ** 2)][2]
            b = pool[rng.randrange(len(pool))][2]
            done = False
            for _ in range(8):
                h = rng.randint(1, m)
                w = rng.randint(1, m)
                r0 = rng.randint(0, m - h)
                c0 = rng.randint(0, m - w)
                r1, c1 = r0 + h, c0 + w
                sa = _split(a, r0, c0, r1, c1)
                if sa is None:
                    continue
                if rng.random() < 0.5:
                    sb = _split(b, r0, c0, r1, c1)
                    if sb is not None:
                        new = sa[1] + sb[0]
                        _add(pool, new, n)
                        done = True
                        break
                sub = _fill(h, w, rng.random(), rng)
                new = sa[1] + [(r0 + r, c0 + c, s) for r, c, s in sub]
                _add(pool, new, n)
                done = True
                break
            if not done:
                lay = _fill(m, m, rng.random(), rng)
                _add(pool, lay, n)
    best = None
    bv = float(k)
    for m in ms:
        if pools[m]:
            tot, cnt, lay, _ = pools[m][0]
            v = tot / m
            if v > bv + 1e-12:
                bv = v
                best = (m, lay)
    if best is None:
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                   for i in range(k) for j in range(k)]
    else:
        m, lay = best
        squares = [((c + s / 2.0) / m, (r + s / 2.0) / m, 0.0, s / m) for r, c, s in lay]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END
