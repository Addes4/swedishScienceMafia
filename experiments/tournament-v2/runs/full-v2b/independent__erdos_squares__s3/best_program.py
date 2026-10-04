import math
import random
import numpy as np


def _corners(cx, cy, a, s):
    """Return the 4 corners of a square as complex numbers."""
    # angle a is fraction of full turn, center (cx,cy), side s
    t = 2.0 * math.pi * a
    c = math.cos(t)
    sn = math.sin(t)
    h = s / 2.0
    # local corners relative to center
    loc = [complex(-h, -h), complex(h, -h), complex(h, h), complex(-h, h)]
    return [complex(cx, cy) + complex(c * z.real - sn * z.imag,
                                      sn * z.real + c * z.imag) for z in loc]


def _inside(cx, cy, a, s):
    for z in _corners(cx, cy, a, s):
        if z.real < -1e-12 or z.real > 1 + 1e-12 or z.imag < -1e-12 or z.imag > 1 + 1e-12:
            return False
    return True


def _norm_corners(cx, cy, a, s):
    h = s / 2.0
    t = 2.0 * math.pi * a
    c = math.cos(t)
    sn = math.sin(t)
    pts = []
    for lx, ly in ((-h, -h), (h, -h), (h, h), (-h, h)):
        pts.append((cx + c * lx - sn * ly, cy + sn * lx + c * ly))
    return pts


def _sat_disjoint(r1, r2):
    """Separating Axis Theorem for two convex polygons."""
    for rect in (r1, r2):
        n = len(rect)
        for i in range(n):
            x1, y1 = rect[i]
            x2, y2 = rect[(i + 1) % n]
            ex, ey = x2 - x1, y2 - y1
            # normal
            nx, ny = -ey, ex
            ln = math.hypot(nx, ny)
            if ln < 1e-15:
                continue
            nx, ny = nx / ln, ny / ln
            min1 = max1 = None
            min2 = max2 = None
            for px, py in r1:
                d = px * nx + py * ny
                if min1 is None or d < min1:
                    min1 = d
                if max1 is None or d > max1:
                    max1 = d
            for px, py in r2:
                d = px * nx + py * ny
                if min2 is None or d < min2:
                    min2 = d
                if max2 is None or d > max2:
                    max2 = d
            if max1 <= min2 + 1e-12 or max2 <= min1 + 1e-12:
                return True
    return False


def _overlap(rects, i, j, eps=1e-12):
    return not _sat_disjoint(rects[i], rects[j], eps) if False else not _sat_disjoint(rects[i], rects[j])


def _feasible(rects, i=None):
    """Check all squares fit and are pairwise disjoint."""
    if i is not None:
        inds = [i]
    else:
        inds = list(range(len(rects)))
    # inside
    for idx in inds:
        r = rects[idx]
        for x, y in r:
            if x < -1e-12 or x > 1 + 1e-12 or y < -1e-12 or y > 1 + 1e-12:
                return False
    n = len(rects)
    if i is not None:
        for j in range(n):
            if j == i:
                continue
            if type(rects[0]) is tuple:
                # stored as (cx,cy,a,s)
                pass
            if not _sat_disjoint(rects[i], rects[j]):
                return False
    else:
        for ii in range(n):
            for jj in range(ii + 1, n):
                if not _sat_disjoint(rects[ii], rects[jj]):
                    return False
    return True


def _rects_from_squares(sqs):
    rects = []
    for cx, cy, a, s in sqs:
        if s <= 0:
            rects.append([(cx, cy)] * 4)  # degenerate
        else:
            rects.append(_norm_corners(cx, cy, a, s))
    return rects


def _greedy_layout(n):
    """Greedy: repeatedly place largest axis-aligned square in free space.
       Use a coarse grid sampling to find candidate placements."""
    if n <= 0:
        return []
    sqs = []
    occupied_rects = []

    # estimate side sizes
    # start with sqrt area target and shrink if needed
    for k in range(n):
        # remaining count
        rem = n - k
        # desired side from area packing
        desired = math.sqrt(1.0 / rem) if rem > 0 else 0.0
        best = None
        # try sizes downward
        s = desired
        tries = 0
        while tries < 60:
            # sample candidate centers
            found = False
            # coarse grid then refine
            steps = 24
            cand = []
            for ii in range(steps + 1):
                for jj in range(steps + 1):
                    cx = ii / steps
                    cy = jj / steps
                    cand.append((cx, cy))
            random.shuffle(cand)
            for cx, cy in cand:
                if not _inside(cx, cy, 0.0, s):
                    continue
                rect = _norm_corners(cx, cy, 0.0, s)
                ok = True
                for orc in occupied_rects:
                    if not _sat_disjoint(rect, orc):
                        ok = False
                        break
                if ok:
                    best = (cx, cy, 0.0, s)
                    found = True
                    break
            if found:
                break
            s *= 0.93
            tries += 1
        if best is None:
            best = (0.5, 0.5, 0.0, 0.0)
        sqs.append(best)
        cx, cy, a, s = best
        occupied_rects.append(_norm_corners(cx, cy, a, s) if s > 0 else [(cx, cy)] * 4)

    return sqs


def _score(sqs):
    return sum(s for _, _, _, s in sqs)


def _local_search(sqs, iters=20000, time_budget=None):
    """Random local search: perturb one square, accept if better and feasible."""
    import time
    t0 = time.time()
    cur = [list(x) for x in sqs]
    cur_rects = _rects_from_squares(cur)
    cur_score = _score(cur)
    best = [list(x) for x in cur]
    best_score = cur_score
    n = len(cur)
    if n == 0:
        return best

    def rebuild(i):
        cx, cy, a, s = cur[i]
        if s <= 0:
            return [(cx, cy)] * 4
        return _norm_corners(cx, cy, a, s)

    it = 0
    while it < iters:
        if time_budget is not None and time.time() - t0 > time_budget:
            break
        it += 1
        i = random.randrange(n)
        old = cur[i][:]
        # perturbations
        mode = random.random()
        cx, cy, a, s = old
        if mode < 0.35:
            # move
            d = random.uniform(-0.05, 0.05)
            th = random.uniform(0, 2 * math.pi)
            cx += d * math.cos(th)
            cy += d * math.sin(th)
        elif mode < 0.55:
            # rotate
            a += random.uniform(-0.1, 0.1)
            a %= 1.0
        elif mode < 0.85:
            # resize
            s *= random.uniform(0.95, 1.08)
            if s < 1e-6:
                s = 0.0
        else:
            # combined
            cx += random.uniform(-0.03, 0.03)
            cy += random.uniform(-0.03, 0.03)
            a += random.uniform(-0.05, 0.05)
            a %= 1.0
            s *= random.uniform(0.97, 1.05)

        # clamp inside
        if s > 0:
            # try to adjust center to be inside
            for _ in range(3):
                if _inside(cx, cy, a, s):
                    break
                cx = min(max(cx, 0.0), 1.0)
                cy = min(max(cy, 0.0), 1.0)
                if not _inside(cx, cy, a, s):
                    # shrink
                    s *= 0.98
            if not _inside(cx, cy, a, s):
                cur[i] = old
                continue
        else:
            cx = min(max(cx, 0.0), 1.0)
            cy = min(max(cy, 0.0), 1.0)
            a = 0.0
        cur[i] = [cx, cy, a, s]
        # check feasibility
        new_rect = rebuild(i)
        ok = True
        for j in range(n):
            if j == i:
                continue
            rj = cur_rects[j]
            if not _sat_disjoint(new_rect, rj):
                ok = False
                break
        if not ok:
            cur[i] = old
            continue
        # inside check
        inside = True
        for x, y in new_rect:
            if x < -1e-12 or x > 1 + 1e-12 or y < -1e-12 or y > 1 + 1e-12:
                inside = False
                break
        if not inside:
            cur[i] = old
            continue
        new_score = _score(cur)
        if new_score > cur_score - 1e-15:
            cur_rects[i] = new_rect
            cur_score = new_score
            if new_score > best_score + 1e-15:
                best_score = new_score
                best = [list(x) for x in cur]
        else:
            # sometimes accept worse
            if random.random() < 0.001:
                cur_rects[i] = new_rect
                cur_score = new_score
            else:
                cur[i] = old
    return best


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    random.seed(12345 + n)
    best = None
    best_score = -1.0
    # multiple attempts
    attempts = 1 if n <= 4 else 3
    for _ in range(attempts):
        start = _greedy_layout(n)
        improved = _local_search(start, iters=30000, time_budget=8.0 / attempts)
        sc = _score(improved)
        if sc > best_score:
            best_score = sc
            best = improved
    # ensure correct length and format
    out = []
    for cx, cy, a, s in best[:n]:
        out.append((float(min(max(cx, 0.0), 1.0)),
                    float(min(max(cy, 0.0), 1.0)),
                    float(a % 1.0),
                    float(max(0.0, s))))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
