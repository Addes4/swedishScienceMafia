# EVOLVE-BLOCK-START
"""Substitution DP: build best layouts bottom-up from grid-based bases, then
replace the largest/smallest square of a layout by a scaled copy of another."""
import math
import time


def _value(layout):
    return sum(s for (_, _, s) in layout)


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    M = n + 3  # small margin so "drop smallest" from larger counts can help
    best = {}  # count -> (value, layout as list of (x0, y0, s))

    def offer(layout):
        c = len(layout)
        if c < 1 or c > M:
            return False
        v = _value(layout)
        cur = best.get(c)
        if cur is None or v > cur[0] + 1e-12:
            best[c] = (v, layout)
            return True
        return False

    # ---- base layouts ----
    K = math.isqrt(M) + 2
    for k in range(1, K + 1):
        sd = 1.0 / k
        grid = [(i * sd, j * sd, sd) for i in range(k) for j in range(k)]
        offer(grid[:M])
        # merged b x b block in a corner
        for b in range(2, k):
            lay = [(0.0, 0.0, b * sd)]
            for i in range(k):
                for j in range(k):
                    if i < b and j < b:
                        continue
                    lay.append((i * sd, j * sd, sd))
            offer(lay)

    def substitute(layout, idx, sub):
        x0, y0, s = layout[idx]
        new = layout[:idx] + layout[idx + 1:]
        for (a, b, c) in sub:
            new.append((x0 + s * a, y0 + s * b, s * c))
        return new

    # cache of largest / smallest positive square indices
    def extremes(layout):
        imax = -1
        imin = -1
        for i, (_, _, s) in enumerate(layout):
            if s <= 0:
                continue
            if imax < 0 or s > layout[imax][2]:
                imax = i
            if imin < 0 or s < layout[imin][2]:
                imin = i
        return imax, imin

    for _pass in range(8):
        changed = False
        for N in range(1, M + 1):
            if time.time() - t0 > 50:
                break
            # add a point
            if N - 1 in best:
                v, lay = best[N - 1]
                cur = best.get(N)
                if cur is None or v > cur[0] + 1e-12:
                    best[N] = (v, lay + [(0.0, 0.0, 0.0)])
                    changed = True
            # drop smallest from N+1
            if N + 1 in best:
                v, lay = best[N + 1]
                imax, imin = extremes(lay)
                if imin >= 0:
                    nv = v - lay[imin][2]
                    cur = best.get(N)
                    if cur is None or nv > cur[0] + 1e-12:
                        best[N] = (nv, lay[:imin] + lay[imin + 1:])
                        changed = True
                else:
                    cur = best.get(N)
                    if cur is None or v > cur[0] + 1e-12:
                        best[N] = (v, lay[:-1])
                        changed = True
            # substitutions
            for a in range(1, N):
                m = N - a + 1
                if a not in best or m not in best or m < 2:
                    continue
                va, la = best[a]
                vm, lm = best[m]
                imax, imin = extremes(la)
                for idx in {imax, imin}:
                    if idx < 0:
                        continue
                    s = la[idx][2]
                    nv = va - s + s * vm
                    cur = best.get(N)
                    if cur is None or nv > cur[0] + 1e-12:
                        best[N] = (nv, substitute(la, idx, lm))
                        changed = True
        if not changed or time.time() - t0 > 50:
            break

    if n in best:
        lay = best[n][1]
    else:
        k = math.isqrt(n)
        sd = 1.0 / k
        lay = [(i * sd, j * sd, sd) for i in range(k) for j in range(k)]
        lay += [(0.0, 0.0, 0.0)] * (n - len(lay))

    shrink = 1.0 - 1e-11
    out = []
    for (x0, y0, s) in lay[:n]:
        cx = min(1.0, max(0.0, x0 + s / 2.0))
        cy = min(1.0, max(0.0, y0 + s / 2.0))
        ss = max(0.0, min(1.0, s * shrink))
        out.append((cx, cy, 0.0, ss))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
