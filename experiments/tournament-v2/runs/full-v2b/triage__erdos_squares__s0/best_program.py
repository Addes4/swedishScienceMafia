import math
import time


def _corners(cx, cy, a, s):
    th = a * 2.0 * math.pi
    co = math.cos(th)
    si = math.sin(th)
    h = s * 0.5
    return (
        (cx - h * co + h * si, cy - h * si - h * co),
        (cx + h * co + h * si, cy + h * si - h * co),
        (cx + h * co - h * si, cy + h * si + h * co),
        (cx - h * co - h * si, cy - h * si + h * co),
    )


def _sep(p1, p2):
    for poly in (p1, p2):
        for i in range(4):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) & 3]
            ax = y1 - y2
            ay = x2 - x1
            d = ax * p1[0][0] + ay * p1[0][1]
            lo1 = hi1 = d
            for k in range(1, 4):
                d = ax * p1[k][0] + ay * p1[k][1]
                if d < lo1:
                    lo1 = d
                elif d > hi1:
                    hi1 = d
            d = ax * p2[0][0] + ay * p2[0][1]
            lo2 = hi2 = d
            for k in range(1, 4):
                d = ax * p2[k][0] + ay * p2[k][1]
                if d < lo2:
                    lo2 = d
                elif d > hi2:
                    hi2 = d
            if hi1 <= lo2 + 1e-12 or hi2 <= lo1 + 1e-12:
                return True
    return False


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    # guaranteed valid baseline: smallest m x m grid holding all n squares
    m = 1
    while m * m < n:
        m += 1
    side = 1.0 / m
    base = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
            for i in range(m) for j in range(m)][:n]
    best_sol = base
    best_sum = sum(q[3] for q in best_sol)

    # assembled square of side s at (cx,cy,a) -- placed as candidate centres
    centers = set()
    for k in range(1, 7):
        for i in range(k):
            for j in range(k):
                centers.add((round((i + 0.5) / k, 6), round((j + 0.5) / k, 6)))
    G = 8
    for i in range(G + 1):
        for j in range(G + 1):
            centers.add((round((i + 0.5) / (G + 1), 6), round((j + 0.5) / (G + 1), 6)))
    centers = sorted(centers)
    angles = (0.0, 0.25, 0.125)

    # upper bound on side for each (center, angle): fits inside the unit square
    ub = {}
    for (cx, cy) in centers:
        mm = min(cx, 1.0 - cx, cy, 1.0 - cy)
        for a in angles:
            th = a * 2.0 * math.pi
            cc = abs(math.cos(th)) + abs(math.sin(th))
            ub[(cx, cy, a)] = 2.0 * mm / cc if cc > 0 else 0.0

    def best_next(placed_corners, floor):
        bs = floor
        bc = None
        for (cx, cy) in centers:
            for a in angles:
                u = ub[(cx, cy, a)]
                if u <= bs:
                    continue
                lo = bs
                hi = u
                for _ in range(11):
                    mid = (lo + hi) * 0.5
                    p1 = _corners(cx, cy, a, mid)
                    good = True
                    for pc in placed_corners:
                        if not _sep(p1, pc):
                            good = False
                            break
                    if good:
                        lo = mid
                    else:
                        hi = mid
                if lo > bs + 1e-9:
                    bs = lo
                    bc = (cx, cy, a)
        return bs, bc

    def fill(sol, budget):
        pc = [_corners(q[0], q[1], q[2], q[3]) for q in sol]
        while len(sol) < n:
            if time.time() - t0 > budget:
                break
            s, c = best_next(pc, 0.0)
            if c is None or s <= 1e-9:
                q = (0.5, 0.5, 0.0, 0.0)
            else:
                q = (c[0], c[1], c[2], s)
            sol.append(q)
            pc.append(_corners(q[0], q[1], q[2], q[3]))
        while len(sol) < n:
            sol.append((0.5, 0.5, 0.0, 0.0))
        return sol

    # strategy: n squares all of size 1/mm in an mm x mm grid
    for mm in range(1, n + 2):
        if mm * mm >= n:
            s = 1.0 / mm
            cand = [((i + 0.5) * s, (j + 0.5) * s, 0.0, s)
                    for i in range(mm) for j in range(mm)][:n]
            v = sum(q[3] for q in cand)
            if v > best_sum:
                best_sum = v
                best_sol = cand

    # strategy: k x k grid of large squares then greedily fill the rest
    for k in range(1, n + 1):
        if k * k > n:
            break
        if time.time() - t0 > 50:
            break
        gs = 1.0 / k
        sol = [((i + 0.5) * gs, (j + 0.5) * gs, 0.0, gs)
               for i in range(k) for j in range(k)]
        sol = fill(sol, 52)
        v = sum(q[3] for q in sol)
        if v > best_sum:
            best_sum = v
            best_sol = sol

    # strategy: pure largest-first greedy from empty
    if time.time() - t0 < 50:
        sol = fill([], 55)
        v = sum(q[3] for q in sol)
        if v > best_sum:
            best_sum = v
            best_sol = sol

    return best_sol[:n]
