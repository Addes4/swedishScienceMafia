# EVOLVE-BLOCK-START
"""Simulated annealing continuous packer for squares in unit square."""
import math
import random


def _sum_sides(sqs):
    return sum(s[3] for s in sqs)


def _pure_grid(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sqs = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
           for i in range(k) for j in range(k)]
    sqs += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sqs))
    return sqs[:n]


def _overlap_penalty(sqs, P=1000.0):
    """Return penalty = P * total overlap area + boundary violations."""
    n = len(sqs)
    pen = 0.0
    for i in range(n):
        cx, cy, _, s = sqs[i]
        if s <= 1e-12:
            continue
        h = s / 2.0
        # boundary
        if cx - h < 0:
            pen += P * (h - cx) * s
        if cx + h > 1:
            pen += P * (cx + h - 1) * s
        if cy - h < 0:
            pen += P * (h - cy) * s
        if cy + h > 1:
            pen += P * (cy + h - 1) * s
        for j in range(i + 1, n):
            cx2, cy2, _, s2 = sqs[j]
            if s2 <= 1e-12:
                continue
            h2 = s2 / 2.0
            ox = (h + h2) - abs(cx - cx2)
            oy = (h + h2) - abs(cy - cy2)
            if ox > 0 and oy > 0:
                pen += P * ox * oy
    return pen


def _objective(sqs):
    return _sum_sides(sqs) - _overlap_penalty(sqs)


def _clip_square(cx, cy, s):
    """Clip a square to fit in [0,1]^2 by shrinking and clamping."""
    if s <= 0:
        return 0.5, 0.5, 0.0
    h = s / 2.0
    if h > 0.5:
        s = 1.0
        h = 0.5
    cx = min(max(cx, h), 1.0 - h)
    cy = min(max(cy, h), 1.0 - h)
    return cx, cy, s


def _perturb(sqs, rng, T):
    """Apply a random perturbation to the packing."""
    n = len(sqs)
    if n == 0:
        return sqs
    new = [list(s) for s in sqs]
    move = rng.random()
    # scale of perturbation depends on temperature
    scale = 0.02 + 0.15 * min(1.0, T / 0.05)
    if move < 0.4:
        # jitter a random square's center
        i = rng.randrange(n)
        cx, cy, ang, s = new[i]
        cx += rng.gauss(0, scale * 0.5)
        cy += rng.gauss(0, scale * 0.5)
        cx, cy, s = _clip_square(cx, cy, s)
        new[i] = [cx, cy, ang, s]
    elif move < 0.75:
        # resize a random square
        i = rng.randrange(n)
        cx, cy, ang, s = new[i]
        s += rng.gauss(0, scale * 0.3)
        if s < 0:
            s = 0.0
        cx, cy, s = _clip_square(cx, cy, s)
        new[i] = [cx, cy, ang, s]
    elif move < 0.9 and n >= 2:
        # transfer size between two squares
        i = rng.randrange(n)
        j = rng.randrange(n)
        if i != j:
            d = rng.gauss(0, scale * 0.2)
            si = max(0.0, new[i][3] + d)
            sj = max(0.0, new[j][3] - d)
            cxi, cyi, ai, _ = new[i]
            cxj, cyj, aj, _ = new[j]
            cxi, cyi, si = _clip_square(cxi, cyi, si)
            cxj, cyj, sj = _clip_square(cxj, cyj, sj)
            new[i] = [cxi, cyi, ai, si]
            new[j] = [cxj, cyj, aj, sj]
    else:
        # move a square to a random location
        i = rng.randrange(n)
        cx = rng.random()
        cy = rng.random()
        s = new[i][3]
        cx, cy, s = _clip_square(cx, cy, s)
        new[i] = [cx, cy, 0.0, s]
    return [tuple(x) for x in new]


def _repair(sqs):
    """Shrink overlapping squares until valid; then try to grow."""
    sqs = [list(s) for s in sqs]
    n = len(sqs)
    # iterative shrink
    for _ in range(200):
        changed = False
        for i in range(n):
            cx1, cy1, _, s1 = sqs[i]
            if s1 <= 1e-12:
                continue
            h1 = s1 / 2.0
            # boundary fix
            max_s = 2.0 * min(cx1, cy1, 1.0 - cx1, 1.0 - cy1)
            if max_s < s1 - 1e-12:
                s1 = max(0.0, max_s)
                sqs[i][3] = s1
                h1 = s1 / 2.0
                changed = True
            for j in range(i + 1, n):
                cx2, cy2, _, s2 = sqs[j]
                if s2 <= 1e-12:
                    continue
                h2 = s2 / 2.0
                ox = (h1 + h2) - abs(cx1 - cx2)
                oy = (h1 + h2) - abs(cy1 - cy2)
                if ox > 1e-12 and oy > 1e-12:
                    # shrink both proportionally
                    shrink = min(ox, oy) / 2.0
                    s1 = max(0.0, s1 - shrink)
                    s2 = max(0.0, s2 - shrink)
                    sqs[i][3] = s1
                    sqs[j][3] = s2
                    h1 = s1 / 2.0
                    h2 = s2 / 2.0
                    changed = True
        if not changed:
            break
    # greedy grow
    for _ in range(50):
        changed = False
        for i in range(n):
            cx, cy, _, s = sqs[i]
            h = s / 2.0
            max_s = 2.0 * min(cx, cy, 1.0 - cx, 1.0 - cy)
            for j in range(n):
                if i == j:
                    continue
                cx2, cy2, _, s2 = sqs[j]
                if s2 <= 1e-12:
                    continue
                h2 = s2 / 2.0
                dx = abs(cx - cx2)
                dy = abs(cy - cy2)
                # max half-size allowed in each direction
                if dx < h + h2 and dy < h + h2:
                    # need to reduce h so that either dx >= h+h2 or dy >= h+h2
                    # so h <= dx - h2 or h <= dy - h2
                    lim = max(dx - h2, dy - h2)
                    if lim > 0:
                        max_s = min(max_s, 2.0 * lim)
                    else:
                        max_s = min(max_s, 0.0)
            if max_s > s + 1e-9:
                sqs[i][3] = max_s
                changed = True
        if not changed:
            break
    return [tuple(x) for x in sqs]


def _validate(sqs):
    n = len(sqs)
    for i in range(n):
        cx1, cy1, _, s1 = sqs[i]
        if s1 <= 1e-12:
            continue
        h1 = s1 / 2.0
        if cx1 - h1 < -1e-7 or cx1 + h1 > 1 + 1e-7:
            return False
        if cy1 - h1 < -1e-7 or cy1 + h1 > 1 + 1e-7:
            return False
        for j in range(i + 1, n):
            cx2, cy2, _, s2 = sqs[j]
            if s2 <= 1e-12:
                continue
            h2 = s2 / 2.0
            if abs(cx1 - cx2) < h1 + h2 - 1e-7 and abs(cy1 - cy2) < h1 + h2 - 1e-7:
                return False
    return True


def _sa(n, seed=12345, iters=4000):
    """Simulated annealing over packing configurations."""
    rng = random.Random(seed)
    cur = _pure_grid(n)
    cur_obj = _objective(cur)
    best = list(cur)
    best_obj = cur_obj
    T0 = 0.08
    Tmin = 1e-4
    for it in range(iters):
        # geometric cooling
        frac = it / max(1, iters - 1)
        T = T0 * (Tmin / T0) ** frac
        new = _perturb(cur, rng, T)
        new_obj = _objective(new)
        delta = new_obj - cur_obj
        if delta > 0 or rng.random() < math.exp(delta / max(T, 1e-9)):
            cur = new
            cur_obj = new_obj
            if cur_obj > best_obj:
                best_obj = cur_obj
                best = list(cur)
    # repair best
    repaired = _repair(best)
    if _validate(repaired):
        return repaired
    return _pure_grid(n)


def _layout_strip_right(k, r, a):
    """k x k grid of side a, plus r squares of side b in a right strip."""
    if a <= 0 or k * a > 1.0 + 1e-12:
        return None
    strip_w = 1.0 - k * a
    if strip_w <= 1e-12:
        return None
    b1 = min(strip_w, 1.0 / r) if r > 0 else 0.0
    best = (b1, 1, r)
    if r >= 2:
        for cols in range(2, min(r, 4) + 1):
            rows = (r + cols - 1) // cols
            b = min(strip_w / cols, 1.0 / rows)
            if b > best[0]:
                best = (b, cols, rows)
    b, cols, rows = best
    if b <= 1e-12:
        return None
    sqs = []
    for i in range(k):
        for j in range(k):
            sqs.append(((i + 0.5) * a, (j + 0.5) * a, 0.0, a))
    cnt = 0
    for c in range(cols):
        for rr in range(rows):
            if cnt >= r:
                break
            cx = k * a + (c + 0.5) * (strip_w / cols)
            cy = (rr + 0.5) * (1.0 / rows)
            sqs.append((cx, cy, 0.0, b))
            cnt += 1
    return sqs


def _layout_strip_top(k, r, a):
    """k x k grid of side a in bottom-left, r squares in top strip."""
    if a <= 0 or k * a > 1.0 + 1e-12:
        return None
    strip_h = 1.0 - k * a
    if strip_h <= 1e-12:
        return None
    b1 = min(strip_h, 1.0 / r) if r > 0 else 0.0
    best = (b1, 1, r)
    if r >= 2:
        for rows in range(2, min(r, 4) + 1):
            cols = (r + rows - 1) // rows
            b = min(strip_h / rows, 1.0 / cols)
            if b > best[0]:
                best = (b, rows, cols)
    b, rows, cols = best
    if b <= 1e-12:
        return None
    sqs = []
    for i in range(k):
        for j in range(k):
            sqs.append(((i + 0.5) * a, (j + 0.5) * a, 0.0, a))
    cnt = 0
    for rr in range(rows):
        for c in range(cols):
            if cnt >= r:
                break
            cx = (c + 0.5) * (1.0 / cols)
            cy = k * a + (rr + 0.5) * (strip_h / rows)
            sqs.append((cx, cy, 0.0, b))
            cnt += 1
    return sqs


def _layout_L_corner(k, r, a):
    """k x k grid of side a, plus r squares filling an L-shaped corner region."""
    if a <= 0 or k * a > 1.0 + 1e-12:
        return None
    strip_w = 1.0 - k * a
    strip_h = 1.0 - k * a
    if strip_w <= 1e-12:
        return None
    best = None
    best_val = -1
    for r1 in range(0, r + 1):
        r2 = r - r1
        b1 = 0.0
        if r1 > 0:
            b1 = min(strip_w, k * a / r1)
            for cols in range(2, min(r1, 4) + 1):
                rows = (r1 + cols - 1) // cols
                bb = min(strip_w / cols, k * a / rows)
                if bb > b1:
                    b1 = bb
        b2 = 0.0
        if r2 > 0:
            b2 = min(strip_h, 1.0 / r2)
            for rows in range(2, min(r2, 4) + 1):
                cols = (r2 + rows - 1) // rows
                bb = min(strip_h / rows, 1.0 / cols)
                if bb > b2:
                    b2 = bb
        val = r1 * b1 + r2 * b2
        if val > best_val:
            best_val = val
            best = (r1, b1, r2, b2)
    if best is None:
        return None
    r1, b1, r2, b2 = best
    sqs = []
    for i in range(k):
        for j in range(k):
            sqs.append(((i + 0.5) * a, (j + 0.5) * a, 0.0, a))
    if r1 > 0 and b1 > 1e-12:
        cols = 1
        for cc in range(2, min(r1, 4) + 1):
            rr = (r1 + cc - 1) // cc
            bb = min(strip_w / cc, k * a / rr)
            if abs(bb - b1) < 1e-9:
                cols = cc
                break
        rows = (r1 + cols - 1) // cols
        cnt = 0
        for c in range(cols):
            for rr in range(rows):
                if cnt >= r1:
                    break
                cx = k * a + (c + 0.5) * (strip_w / cols)
                cy = (rr + 0.5) * (k * a / rows)
                sqs.append((cx, cy, 0.0, b1))
                cnt += 1
    if r2 > 0 and b2 > 1e-12:
        rows = 1
        for rr in range(2, min(r2, 4) + 1):
            cc = (r2 + rr - 1) // rr
            bb = min(strip_h / rr, 1.0 / cc)
            if abs(bb - b2) < 1e-9:
                rows = rr
                break
        cols = (r2 + rows - 1) // rows
        cnt = 0
        for rr in range(rows):
            for c in range(cols):
                if cnt >= r2:
                    break
                cx = (c + 0.5) * (1.0 / cols)
                cy = k * a + (rr + 0.5) * (strip_h / rows)
                sqs.append((cx, cy, 0.0, b2))
                cnt += 1
    return sqs


def _score_layout(k, r, a, layout_fn):
    sqs = layout_fn(k, r, a)
    if sqs is None or len(sqs) < k * k + r:
        return -1.0
    return _sum_sides(sqs)


def _optimize_a(k, r, layout_fn):
    """Golden-section search over a in (0, 1/k) to maximize sum of sides."""
    lo = 1e-6
    hi = 1.0 / k - 1e-9
    if hi <= lo:
        return hi
    N = 60
    best_a = lo
    best_v = -1.0
    for i in range(N + 1):
        a = lo + (hi - lo) * i / N
        v = _score_layout(k, r, a, layout_fn)
        if v > best_v:
            best_v = v
            best_a = a
    gr = (math.sqrt(5) - 1) / 2
    left = max(lo, best_a - (hi - lo) / N)
    right = min(hi, best_a + (hi - lo) / N)
    c = right - gr * (right - left)
    d = left + gr * (right - left)
    fc = _score_layout(k, r, c, layout_fn)
    fd = _score_layout(k, r, d, layout_fn)
    for _ in range(50):
        if right - left < 1e-12:
            break
        if fc > fd:
            right = d
            d = c
            fd = fc
            c = right - gr * (right - left)
            fc = _score_layout(k, r, c, layout_fn)
        else:
            left = c
            c = d
            fc = fd
            d = left + gr * (right - left)
            fd = _score_layout(k, r, d, layout_fn)
    return (left + right) / 2


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    # Baseline candidates
    candidates = [_pure_grid(n)]

    # Parametric layout families (grid + strip/L-corner) for several k
    for kk in (max(1, math.isqrt(n) - 1), math.isqrt(n)):
        if kk * kk > n:
            continue
        rr = n - kk * kk
        if rr <= 0:
            continue
        for fn in (_layout_strip_right, _layout_strip_top, _layout_L_corner):
            try:
                a_star = _optimize_a(kk, rr, fn)
                sqs = fn(kk, rr, a_star)
                if sqs is not None and len(sqs) >= n:
                    candidates.append(sqs[:n])
            except Exception:
                pass

    # Try SA with several seeds and iteration budgets
    seeds = [1, 7, 42, 123, 999]
    iters_list = [3000, 6000]
    for seed in seeds:
        for iters in iters_list:
            try:
                cand = _sa(n, seed=seed, iters=iters)
                candidates.append(cand)
            except Exception:
                pass

    # Also try a (k+1) partial grid
    k = math.isqrt(n)
    k2 = k + 1
    side2 = 1.0 / k2
    sqs_k2 = [((i + 0.5) * side2, (j + 0.5) * side2, 0.0, side2)
              for i in range(k2) for j in range(k2)]
    if len(sqs_k2) >= n:
        candidates.append(sqs_k2[:n])
    else:
        sqs_k2 += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sqs_k2))
        candidates.append(sqs_k2[:n])

    # Pick best valid candidate
    best = None
    best_val = -1.0
    for c in candidates:
        if len(c) != n:
            continue
        if not _validate(c):
            continue
        v = _sum_sides(c)
        if v > best_val:
            best_val = v
            best = c

    if best is None:
        return _pure_grid(n)
    return best
# EVOLVE-BLOCK-END