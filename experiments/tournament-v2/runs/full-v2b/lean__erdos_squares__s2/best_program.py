# EVOLVE-BLOCK-START
"""Squares in a square: multi-start row/grid/diagonal layouts + a bitmap
corner-occupancy constructor + strong inflate refiner with basin-hopping."""
import math
import random


def _make_layout(n, counts):
    k = len(counts)
    caps = [1.0 / c for c in counts]
    total_cap = sum(caps)
    if total_cap <= 1.0:
        heights = caps[:]
    else:
        lo, hi = 0.0, max(caps)
        for _ in range(60):
            t = 0.5 * (lo + hi)
            if sum(min(c, t) for c in caps) < 1.0:
                lo = t
            else:
                hi = t
        t = 0.5 * (lo + hi)
        heights = [min(c, t) for c in caps]
        s = sum(heights)
        if s > 0:
            heights = [h / s for h in heights]
    squares = []
    y = 0.0
    for i, c in enumerate(counts):
        h = heights[i]
        s = min(h, 1.0 / c)
        xoff = (1.0 - c * s) / 2.0
        cy = y + h / 2.0
        for j in range(c):
            cx = xoff + (j + 0.5) * s
            squares.append((cx, cy, 0.0, s))
        y += h
    return squares


def _column_layout(n, counts):
    sq = _make_layout(n, counts)
    return [(cy, cx, 0.25, s) for (cx, cy, a, s) in sq]


def _diagonal_layout(n, counts):
    k = len(counts)
    caps = [1.0 / c for c in counts]
    total_cap = sum(caps)
    if total_cap <= 1.0:
        heights = caps[:]
    else:
        lo, hi = 0.0, max(caps)
        for _ in range(60):
            t = 0.5 * (lo + hi)
            if sum(min(c, t) for c in caps) < 1.0:
                lo = t
            else:
                hi = t
        t = 0.5 * (lo + hi)
        heights = [min(c, t) for c in caps]
        s = sum(heights)
        if s > 0:
            heights = [h / s for h in heights]
    squares = []
    y = 0.0
    total_h = sum(heights)
    for i, c in enumerate(counts):
        h = heights[i]
        s = min(h, 1.0 / c)
        shift = (y / max(total_h, 1e-9)) * (1.0 - c * s)
        xoff = shift
        cy = y + h / 2.0
        for j in range(c):
            cx = xoff + (j + 0.5) * s
            if cx - s / 2 < -1e-9 or cx + s / 2 > 1 + 1e-9:
                cx = min(max(cx, s / 2), 1 - s / 2)
            squares.append((cx, cy, 0.0, s))
        y += h
    return squares


def _feasible(s):
    m = len(s)
    for (cx, cy, a, si) in s:
        if si < -1e-12 or cx - si / 2 < -1e-9 or cx + si / 2 > 1 + 1e-9 \
           or cy - si / 2 < -1e-9 or cy + si / 2 > 1 + 1e-9:
            return False
    for i in range(m):
        x1, y1, _, s1 = s[i]
        for j in range(i + 1, m):
            x2, y2, _, s2 = s[j]
            if abs(x1 - x2) < (s1 + s2) / 2 - 1e-9 and \
               abs(y1 - y2) < (s1 + s2) / 2 - 1e-9:
                return False
    return True


def _total(s):
    return sum(q[3] for q in s)


def _refine(sq, n, rounds=80, seed=12345):
    rnd = random.Random(seed)
    cur = [list(q) for q in sq]
    for _ in range(rounds):
        improved = False
        order = sorted(range(n), key=lambda i: -cur[i][3])
        for i in order:
            cx, cy, a, si = cur[i]
            grew = False
            for grow in (0.05, 0.025, 0.012, 0.006, 0.003, 0.0015, 0.0007):
                ns = si + grow
                cands = [(0, 0), (grow/2, 0), (-grow/2, 0),
                         (0, grow/2), (0, -grow/2),
                         (grow/2, grow/2), (-grow/2, -grow/2),
                         (grow/2, -grow/2), (-grow/2, grow/2)]
                for _r in range(3):
                    ang = rnd.uniform(0, 2 * math.pi)
                    cands.append((grow * math.cos(ang), grow * math.sin(ang)))
                for dx, dy in cands:
                    ncx = min(max(cx + dx, ns / 2), 1 - ns / 2)
                    ncy = min(max(cy + dy, ns / 2), 1 - ns / 2)
                    cand = cur[:i] + [[ncx, ncy, a, ns]] + cur[i + 1:]
                    if _feasible(cand):
                        cur = cand
                        grew = True
                        improved = True
                        break
                if grew:
                    break
            if not grew:
                for dx, dy in ((0.004, 0), (-0.004, 0), (0, 0.004), (0, -0.004),
                               (0.003, 0.003), (-0.003, -0.003),
                               (0.003, -0.003), (-0.003, 0.003)):
                    ncx = min(max(cx + dx, si / 2), 1 - si / 2)
                    ncy = min(max(cy + dy, si / 2), 1 - si / 2)
                    cand = cur[:i] + [[ncx, ncy, a, si]] + cur[i + 1:]
                    if _feasible(cand):
                        cur = cand
                        improved = True
                        break
        if not improved:
            break
    return [tuple(q) for q in cur]


def _slide_polish(sq, n, rounds=40):
    """Analytic polish: for each square try to slide it in axis-aligned and
    diagonal directions to exact contact positions, and try single-square
    growth to the maximal feasible radius computed against neighbors/walls."""
    cur = [list(q) for q in sq]
    for _ in range(rounds):
        improved = False
        order = sorted(range(n), key=lambda i: cur[i][3])
        for i in order:
            cx, cy, a, si = cur[i]
            # Max feasible half-gap in +x, -x, +y, -y, and both diagonals.
            hx = min(1.0 - cx, cx)
            hy = min(1.0 - cy, cy)
            for j in range(n):
                if j == i:
                    continue
                ox, oy, _, os = cur[j]
                dx = ox - cx
                dy = oy - cy
                need = (si + os) / 2.0
                # free x-half-extent limited by neighbor (if overlapping in y)
                if abs(dy) < need:
                    lim = abs(dx) - need
                    if dx >= 0:
                        hx = min(hx, lim) if lim < 0 else hx
                    else:
                        hx = min(hx, lim) if lim < 0 else hx
                if abs(dx) < need:
                    lim = abs(dy) - need
                    if dy >= 0:
                        hy = min(hy, lim) if lim < 0 else hy
                    else:
                        hy = min(hy, lim) if lim < 0 else hy
            # Max growth keeping centre fixed (must not overlap neighbors)
            maxhalf = min(1.0 - cx, cx, 1.0 - cy, cy)
            for j in range(n):
                if j == i:
                    continue
                ox, oy, _, os = cur[j]
                need = (si + os) / 2.0
                if abs(ox - cx) < need and abs(oy - cy) < need:
                    # overlap; cannot grow here at all — skip growth
                    maxhalf = si / 2.0
                    break
                dx = abs(ox - cx)
                dy = abs(oy - cy)
                # growing si changes need; growth feasible until dx >= (ns+os)/2
                # or dy >= (ns+os)/2, whichever triggers first
                lim = max(dx, dy) - os / 2.0
                if lim < maxhalf:
                    maxhalf = lim
            maxhalf = min(maxhalf, 2.0)
            if maxhalf > si / 2.0 + 1e-12:
                ns = 2.0 * maxhalf - 1e-9
                cand = cur[:i] + [[cx, cy, a, ns]] + cur[i + 1:]
                if _feasible(cand):
                    cur = cand
                    si = ns
                    improved = True
                    continue
            # try analytic slides of the current square to contact
            for (dxs, dys) in ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (0.7071, 0.7071), (-0.7071, -0.7071),
                               (0.7071, -0.7071), (-0.7071, 0.7071)):
                # find max t so that move stays feasible, then step to it
                lo, hi = 0.0, 0.2
                for _ in range(18):
                    mid = 0.5 * (lo + hi)
                    ncx = cx + dxs * mid
                    ncy = cy + dys * mid
                    if (ncx - si / 2 >= -1e-9 and ncx + si / 2 <= 1 + 1e-9 and
                        ncy - si / 2 >= -1e-9 and ncy + si / 2 <= 1 + 1e-9):
                        ok = True
                        for j in range(n):
                            if j == i:
                                continue
                            ox, oy, _, os = cur[j]
                            if abs(ox - ncx) < (si + os) / 2 - 1e-9 and \
                               abs(oy - ncy) < (si + os) / 2 - 1e-9:
                                ok = False
                                break
                        if ok:
                            lo = mid
                            continue
                    hi = mid
                if lo > 1e-7:
                    ncx = cx + dxs * lo
                    ncy = cy + dys * lo
                    cand = cur[:i] + [[ncx, ncy, a, si]] + cur[i + 1:]
                    if _feasible(cand):
                        cur = cand
                        cx, cy = ncx, ncy
                        improved = True
        if not improved:
            break
    return [tuple(q) for q in cur]


def _compositions(n, k):
    if k == 1:
        yield (n,)
        return
    def rec(remaining, parts, maxv):
        if len(parts) == k - 1:
            if 1 <= remaining <= maxv:
                yield tuple(parts + [remaining])
            return
        for v in range(min(maxv, remaining - (k - 1 - len(parts))), 0, -1):
            yield from rec(remaining - v, parts + [v], v)
    yield from rec(n, [], n)


def _shelf_layout(n, counts):
    k = len(counts)
    caps = [1.0 / c for c in counts]
    total_cap = sum(caps)
    if total_cap <= 1.0:
        heights = caps[:]
    else:
        lo, hi = 0.0, max(caps)
        for _ in range(60):
            t = 0.5 * (lo + hi)
            if sum(min(c, t) for c in caps) < 1.0:
                lo = t
            else:
                hi = t
        t = 0.5 * (lo + hi)
        heights = [min(c, t) for c in caps]
        s = sum(heights)
        if s > 0:
            heights = [h / s for h in heights]
    squares = []
    y = 0.0
    for i, c in enumerate(counts):
        h = heights[i]
        s = min(h, 1.0 / c)
        x = 0.0
        cy = y + h / 2.0
        for j in range(c):
            cx = min(x + s / 2.0, 1 - s / 2.0)
            squares.append((cx, cy, 0.0, s))
            x += s
        y += h
    return squares


def _corner_layout(n, seed=0):
    rnd = random.Random(seed)
    first = 1.0
    squares = [(0.5, 0.5, 0.0, first)]
    remaining = n - 1
    if remaining <= 0:
        return squares
    squares = []
    big = 0.5
    squares.append((big / 2.0, big / 2.0, 0.0, big))
    x = big
    y = 0.0
    row_h = 0.0
    for i in range(n - 1):
        s = 0.5 / (i + 2.0)
        if x + s > 1.0 + 1e-9:
            x = 0.0
            y += row_h if row_h > 0 else s
            row_h = 0.0
        cy = min(y + s / 2.0, 1 - s / 2.0)
        cx = min(x + s / 2.0, 1 - s / 2.0)
        squares.append((cx, cy, 0.0, s))
        x += s
        row_h = max(row_h, s)
    return squares


def _bitmap_layout(n, seed=0, grid=140):
    rnd = random.Random(seed)
    G = grid
    occ = [bytearray(G) for _ in range(G)]
    squares = []

    req = []
    for i in range(n):
        req.append(1.0 / (i + 1.7))
    mx = max(req)
    req = [r / max(mx, 1e-9) for r in req]

    def free(cx, cy, s):
        half = s / 2.0
        x0 = int(math.floor((cx - half) * G))
        x1 = int(math.ceil((cx + half) * G))
        y0 = int(math.floor((cy - half) * G))
        y1 = int(math.ceil((cy + half) * G))
        if x0 < 0 or y0 < 0 or x1 > G or y1 > G:
            return False
        for yy in range(y0, y1):
            row = occ[yy]
            for xx in range(x0, x1):
                if row[xx]:
                    return False
        return True

    def mark(cx, cy, s):
        half = s / 2.0
        x0 = max(0, int(math.floor((cx - half) * G)))
        x1 = min(G, int(math.ceil((cx + half) * G)))
        y0 = max(0, int(math.floor((cy - half) * G)))
        y1 = min(G, int(math.ceil((cy + half) * G)))
        for yy in range(y0, y1):
            row = occ[yy]
            for xx in range(x0, x1):
                row[xx] = 1

    anchors = []
    step = 0.1
    kk = 0
    while kk <= 10 + 1e-9:
        ll = 0
        while ll <= 10 + 1e-9:
            anchors.append((kk * step, ll * step))
            ll += 1
        kk += 1

    for i in range(n):
        target = req[i]
        best = None
        order = anchors[:]
        rnd.shuffle(order)
        for (ax, ay) in order:
            s = target
            tries = 0
            while s > 1e-3 and tries < 6:
                cx = min(max(ax + s / 2.0, s / 2.0), 1 - s / 2.0)
                cy = min(max(ay + s / 2.0, s / 2.0), 1 - s / 2.0)
                if free(cx, cy, s):
                    score = s + 0.01 * rnd.random()
                    if best is None or score > best[0]:
                        best = (score, cx, cy, s)
                    break
                s *= 0.8
                tries += 1
        if best is None:
            placed = False
            for yy in range(G):
                if placed:
                    break
                for xx in range(G):
                    if not occ[yy][xx]:
                        mark((xx + 0.5) / G, (yy + 0.5) / G, 1.0 / G)
                        squares.append(((xx + 0.5) / G, (yy + 0.5) / G, 0.0,
                                        1.0 / G))
                        placed = True
                        break
            if not placed:
                squares.append((0.5, 0.5, 0.0, 0.0))
            continue
        _, cx, cy, s = best
        mark(cx, cy, s)
        squares.append((cx, cy, 0.0, s))
        half = s / 2.0
        for (px, py) in ((cx + half, cy + half), (cx - half, cy + half),
                         (cx + half, cy - half), (cx - half, cy - half),
                         (cx + half, cy), (cx - half, cy),
                         (cx, cy + half), (cx, cy - half)):
            if -1e-9 <= px <= 1 + 1e-9 and -1e-9 <= py <= 1 + 1e-9:
                anchors.append((px, py))
    return squares


def _candidate_layouts(n):
    cands = []
    seen = set()
    for k in range(1, n + 1):
        comps = list(_compositions(n, k))
        if len(comps) > 300:
            step = len(comps) // 300 + 1
            comps = comps[::step]
        for counts in comps:
            if counts in seen:
                continue
            seen.add(counts)
            sq = _make_layout(n, counts)
            if len(sq) == n and _feasible(sq):
                cands.append(sq)
            cq = _column_layout(n, counts)
            if len(cq) == n and _feasible(cq):
                cands.append(cq)
            dq = _diagonal_layout(n, counts)
            if len(dq) == n and _feasible(dq):
                cands.append(dq)
            shq = _shelf_layout(n, counts)
            if len(shq) == n and _feasible(shq):
                cands.append(shq)
    return cands


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    cands = _candidate_layouts(n)
    if not cands:
        cands = [_make_layout(n, [n])]

    for sd in range(4):
        cq = _corner_layout(n, seed=sd)
        if len(cq) == n and _feasible(cq):
            cands.append(cq)

    for sd in range(6):
        try:
            bq = _bitmap_layout(n, seed=sd, grid=140)
        except Exception:
            bq = []
        if len(bq) == n and _feasible(bq):
            cands.append(bq)

    cands.sort(key=_total, reverse=True)
    pool = cands[:min(len(cands), 26)]

    best = None
    best_s = -1.0
    for sq in pool:
        r = _refine(sq, n, rounds=60)
        r = _slide_polish(r, n, rounds=30)
        r = _refine(r, n, rounds=30)
        sc = _total(r)
        if sc > best_s:
            best_s = sc
            best = r

    rnd = random.Random(777)
    for restart in range(60):
        cur = [list(q) for q in best]
        for i in range(n):
            cx, cy, a, si = cur[i]
            amp = 0.03 * (0.3 + rnd.random())
            ncx = min(max(cx + rnd.uniform(-amp, amp), si / 2), 1 - si / 2)
            ncy = min(max(cy + rnd.uniform(-amp, amp), si / 2), 1 - si / 2)
            cur[i] = [ncx, ncy, a, si]
        for i in rnd.sample(range(n), max(1, n // 3)):
            cur[i][3] *= rnd.uniform(0.75, 0.96)
        if not _feasible(cur):
            cur = [list(q) for q in best]
            continue
        r = _refine([tuple(q) for q in cur], n, rounds=50, seed=restart * 13 + 1)
        r = _slide_polish(r, n, rounds=20)
        r = _refine(r, n, rounds=25, seed=restart * 13 + 1)
        sc = _total(r)
        if sc > best_s:
            best_s = sc
            best = r

    best = _refine(best, n, rounds=40, seed=999)
    best = _slide_polish(best, n, rounds=40)
    best = _refine(best, n, rounds=40, seed=998)
    return best[:n]
# EVOLVE-BLOCK-END
