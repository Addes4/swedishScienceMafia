import math
import random


def _overlap_area(s1, s2):
    cx1, cy1, a1, L1 = s1
    cx2, cy2, a2, L2 = s2
    h1 = 0.5 * L1
    h2 = 0.5 * L2
    if h1 <= 1e-15 or h2 <= 1e-15:
        return 0.0

    t1 = a1 * 2.0 * math.pi
    t2 = a2 * 2.0 * math.pi
    c1 = math.cos(t1)
    s1v = math.sin(t1)
    c2 = math.cos(t2)
    s2v = math.sin(t2)

    ax1 = c1 * h1
    ay1 = s1v * h1
    bx1 = -s1v * h1
    by1 = c1 * h1

    ax2 = c2 * h2
    ay2 = s2v * h2
    bx2 = -s2v * h2
    by2 = c2 * h2

    dx = cx1 - cx2
    dy = cy1 - cy2

    pts = [
        (cx1 + ax1 + bx1, cy1 + ay1 + by1),
        (cx1 + ax1 - bx1, cy1 + ay1 - by1),
        (cx1 - ax1 + bx1, cy1 - ay1 + by1),
        (cx1 - ax1 - bx1, cy1 - ay1 - by1),
    ]
    qts = [
        (cx2 + ax2 + bx2, cy2 + ay2 + by2),
        (cx2 + ax2 - bx2, cy2 + ay2 - by2),
        (cx2 - ax2 + bx2, cy2 - ay2 + by2),
        (cx2 - ax2 - bx2, cy2 - ay2 - by2),
    ]

    axes = [
        (ax1, ay1),
        (bx1, by1),
        (ax2, ay2),
        (bx2, by2),
    ]

    minov = 1e18
    for ax, ay in axes:
        nrm = math.hypot(ax, ay)
        if nrm <= 1e-15:
            continue
        ux = ax / nrm
        uy = ay / nrm

        p1 = [px * ux + py * uy for px, py in pts]
        p2 = [px * ux + py * uy for px, py in qts]
        mx1, mn1 = max(p1), min(p1)
        mx2, mn2 = max(p2), min(p2)
        ov = min(mx1, mx2) - max(mn1, mn2)
        if ov <= 0.0:
            return 0.0
        if ov < minov:
            minov = ov

    return minov * minov


def _inside(s):
    cx, cy, a, L = s
    h = 0.5 * L
    if h <= 1e-15:
        return 0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0
    t = a * 2.0 * math.pi
    c = math.cos(t)
    si = math.sin(t)
    ax = c * h
    ay = si * h
    bx = -si * h
    by = c * h
    r = abs(ax) + abs(bx)
    rr = abs(ay) + abs(by)
    if cx - r < -1e-12 or cx + r > 1.0 + 1e-12:
        return False
    if cy - rr < -1e-12 or cy + rr > 1.0 + 1e-12:
        return False
    return True


def _valid(sqs):
    for s in sqs:
        if not _inside(s):
            return False
    m = len(sqs)
    for i in range(m):
        for j in range(i + 1, m):
            if _overlap_area(sqs[i], sqs[j]) > 1e-12:
                return False
    return True


def _score(sqs):
    return sum(s[3] for s in sqs)


def _initial(n):
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    best = None
    bestv = -1.0

    k = int(math.isqrt(n))
    while k >= 1:
        if k * k <= n:
            s = 1.0 / k
            sqs = []
            for i in range(k):
                for j in range(k):
                    sqs.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
            rem = n - k * k
            col = (k + 1) if k > 0 else 1
            # try to put leftover into rows of smaller strip
            v = _score(sqs)
            if v > bestv:
                bestv = v
                best = sqs
        k -= 1

    # row-based packing: choose height profile
    r = int(math.isqrt(n))
    for rows in range(1, n + 1):
        base = n // rows
        rem = n % rows
        # try all splits
        heights = []
        for i in range(rows):
            heights.append(base + (1 if i < rem else 0))
        if max(heights) == 0:
            continue
        # widths by rows: each row has h_i squares, each side = 1/h_i? no
        # row packing: divide unit width among squares in row, height per row
        # choose row heights proportional to 1/ max? Just uniform split.
        h = 1.0 / rows
        sqs = []
        for i, cnt in enumerate(heights):
            if cnt == 0:
                continue
            w = 1.0 / cnt
            side = min(w, h)
            for j in range(cnt):
                sqs.append(((j + 0.5) * w, (i + 0.5) * h, 0.0, side))
        v = _score(sqs)
        if v > bestv:
            bestv = v
            best = sqs

    # fill to n
    res = list(best)
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]


def solve(n):
    if n <= 0:
        return []
    random.seed(12345 + n)
    sqs = _initial(n)
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    best = [tuple(s) for s in sqs]
    bestv = _score(sqs)

    cur = [list(s) for s in sqs]
    curv = bestv

    T0 = 0.02
    iters = 200000 if n <= 20 else (120000 if n <= 50 else 60000)

    for it in range(iters):
        T = T0 * (1.0 - it / iters) + 1e-5
        i = random.randrange(n)
        old = tuple(cur[i])
        cx, cy, a, L = old

        typ = random.random()
        if typ < 0.45:
            nc = cx + random.gauss(0, 0.02 * T / T0 + 0.001)
            ny = cy + random.gauss(0, 0.02 * T / T0 + 0.001)
            na = a
            nL = L
        elif typ < 0.7:
            na = a + random.gauss(0, 0.05)
            na = na % 1.0
            nc = cx
            ny = cy
            nL = L
        elif typ < 0.95:
            nL = L + random.gauss(0, 0.03 * T / T0 + 0.001)
            nL = max(0.0, min(1.0, nL))
            nc = cx
            ny = cy
            na = a
        else:
            nc = cx + random.gauss(0, 0.01)
            ny = cy + random.gauss(0, 0.01)
            na = a + random.gauss(0, 0.03)
            na = na % 1.0
            nL = L + random.gauss(0, 0.01)
            nL = max(0.0, min(1.0, nL))

        if nc < 0.0 or nc > 1.0:
            continue
        if ny < 0.0 or ny > 1.0:
            continue
        if nL < 0.0 or nL > 1.0:
            continue

        new = (nc, ny, na, nL)
        if not _inside(new):
            continue

        ok = True
        for j in range(n):
            if j == i:
                continue
            if _overlap_area(new, cur[j]) > 1e-12:
                ok = False
                break
        if not ok:
            continue

        dscore = nL - L
        if dscore >= 0 or random.random() < math.exp(dscore / T):
            cur[i] = list(new)
            curv += dscore
            if curv > bestv:
                bestv = curv
                best = [tuple(s) for s in cur]

    # final polish: try to grow each square
    for _ in range(3000):
        improved = False
        order = list(range(n))
        random.shuffle(order)
        for i in order:
            cx, cy, a, L = cur[i]
            best_l = L
            new_sq = None
            for delta in [0.05, 0.02, 0.01, 0.005, 0.002, 0.001]:
                nL = L + delta
                if nL > 1.0:
                    continue
                cand = (cx, cy, a, nL)
                if not _inside(cand):
                    continue
                ok = True
                for j in range(n):
                    if j == i:
                        continue
                    if _overlap_area(cand, cur[j]) > 1e-12:
                        ok = False
                        break
                if ok:
                    best_l = nL
                    new_sq = cand
                    break
            if new_sq is not None:
                curv += best_l - L
                cur[i] = list(new_sq)
                improved = True
        if curv > bestv:
            bestv = curv
            best = [tuple(s) for s in cur]
        if not improved:
            break

    return best
