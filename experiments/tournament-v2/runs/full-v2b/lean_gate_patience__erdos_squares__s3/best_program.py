# EVOLVE-BLOCK-START
"""Squares in a square: grid/shelf construction + randomized local search."""
import math
import random

PI = math.pi


def _corners(cx, cy, ang, s):
    a = ang * 2.0 * PI
    c = math.cos(a)
    sn = math.sin(a)
    h = 0.5 * s
    ux, uy = c * h, sn * h
    vx, vy = -sn * h, c * h
    return [
        (cx + ux + vx, cy + uy + vy),
        (cx + ux - vx, cy + uy - vy),
        (cx - ux - vx, cy - uy - vy),
        (cx - ux + vx, cy - uy + vy),
    ]


def _overlap_pair(c1, c2, eps=1e-12):
    for poly in (c1, c2):
        m = len(poly)
        for i in range(m):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % m]
            ex, ey = x2 - x1, y2 - y1
            nx, ny = -ey, ex
            nlen = math.hypot(nx, ny)
            if nlen < eps:
                continue
            nx /= nlen
            ny /= nlen
            min1 = min(p[0] * nx + p[1] * ny for p in c1)
            max1 = max(p[0] * nx + p[1] * ny for p in c1)
            min2 = min(p[0] * nx + p[1] * ny for p in c2)
            max2 = max(p[0] * nx + p[1] * ny for p in c2)
            if max1 <= min2 + eps or max2 <= min1 + eps:
                return False
    return True


def _inside_unit(cs, eps=1e-9):
    for x, y in cs:
        if x < -eps or x > 1.0 + eps or y < -eps or y > 1.0 + eps:
            return False
    return True


def _valid(squares):
    n = len(squares)
    corners = []
    for (cx, cy, ang, s) in squares:
        cs = _corners(cx, cy, ang, s)
        if not _inside_unit(cs):
            return False
        corners.append(cs)
    for i in range(n):
        if squares[i][3] <= 0.0:
            continue
        for j in range(i + 1, n):
            if squares[j][3] <= 0.0:
                continue
            if _overlap_pair(corners[i], corners[j]):
                return False
    return True


def _score(squares):
    return sum(sq[3] for sq in squares)


# ---------- constructors ----------

def _grid_pack(n):
    best = None
    best_sc = -1.0
    for rows in range(1, n + 1):
        cols = (n + rows - 1) // rows
        w = 1.0 / cols
        h = 1.0 / rows
        s = min(w, h)
        sq = []
        cnt = 0
        for r in range(rows):
            for c in range(cols):
                if cnt >= n:
                    break
                cx = (c + 0.5) * w
                cy = (r + 0.5) * h
                sq.append((cx, cy, 0.0, s))
                cnt += 1
            if cnt >= n:
                break
        sq = sq[:n]
        while len(sq) < n:
            sq.append((0.5, 0.5, 0.0, 0.0))
        if _valid(sq):
            sc = _score(sq)
            if sc > best_sc:
                best_sc = sc
                best = sq
    return best if best is not None else [(0.5, 0.5, 0.0, s) for _ in range(n)]


def _bigrow_shelf(n):
    best = None
    best_sc = -1.0
    for k in range(1, n + 1):
        rem = n - k
        s = 1.0 / k
        if rem == 0:
            h = 0.0
        else:
            c = math.ceil(math.sqrt(rem))
            h = 1.0 / c
        sq = []
        for i in range(k):
            sq.append(((i + 0.5) * s, 0.5 * s, 0.0, s))
        if rem > 0:
            c = math.ceil(math.sqrt(rem))
            rs = min(1.0 / c, h)
            cnt = 0
            for r in range(math.ceil(rem / c)):
                for cc in range(c):
                    if cnt >= rem:
                        break
                    cx = (cc + 0.5) * (1.0 / c)
                    cy = 1.0 - h + (r + 0.5) * h
                    sq.append((cx, cy, 0.0, rs))
                    cnt += 1
                if cnt >= rem:
                    break
        sq = sq[:n]
        while len(sq) < n:
            sq.append((0.5, 0.5, 0.0, 0.0))
        if _valid(sq):
            sc = _score(sq)
            if sc > best_sc:
                best_sc = sc
                best = sq
    return best if best is not None else _grid_pack(n)


def _pack_equal(n, t):
    k = math.isqrt(n)
    if (k * k >= n) and (k * t <= 1.0 + 1e-12):
        sq = []
        cnt = 0
        for r in range(k):
            for c in range(k):
                if cnt >= n:
                    break
                sq.append(((c + 0.5) * t, (r + 0.5) * t, 0.0, t))
                cnt += 1
            if cnt >= n:
                break
        return sq[:n]
    return None


def _maxmin_seed(n):
    lo, hi = 0.0, 1.0
    best = None
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        sq = _pack_equal(n, mid)
        if sq is not None and _valid(sq):
            best = sq
            lo = mid
        else:
            hi = mid
    if best is None:
        return _grid_pack(n)
    return best


def _rotate_client(n, base):
    """Rotate every square in base by the same angle about the unit-square centre,
    scaling to keep it inside, to generate rotated seed layouts."""
    ang = random.choice([0.125, 0.1, 0.15, 0.05, 0.2])
    a = ang * 2.0 * PI
    c = math.cos(a)
    sn = math.sin(a)
    sq = []
    for (cx, cy, oa, s) in base:
        x = cx - 0.5
        y = cy - 0.5
        nx = x * c - y * sn + 0.5
        ny = x * sn + y * c + 0.5
        sq.append((nx, ny, (oa + ang) % 1.0, s))
    # shrink to fit
    for _ in range(40):
        if _valid(sq):
            break
        sq = [(cx, cy, oa, s * 0.95) for (cx, cy, oa, s) in sq]
    return sq


def _pinwheel_seed(n):
    """Pinwheel-style: try several equal-side layouts with 45-ish rotation offsets,
    choosing the best valid one."""
    best = None
    best_sc = -1.0
    for t in [1.0 / max(1, math.ceil(math.sqrt(n)))]:
        for ang_off in [0.0, 0.125, 0.0625, 0.1875, 0.25]:
            # grid of size t, rotated around the whole-block centre
            k = math.isqrt(n)
            if k * k < n:
                k += 1
            sq = []
            cnt = 0
            for r in range(k):
                for cc in range(k):
                    if cnt >= n:
                        break
                    cx = (cc + 0.5) * t
                    cy = (r + 0.5) * t
                    sq.append((cx, cy, ang_off, t))
                    cnt += 1
                if cnt >= n:
                    break
            sq = sq[:n]
            while len(sq) < n:
                sq.append((0.5, 0.5, 0.0, 0.0))
            # shrink until valid
            for _ in range(60):
                if _valid(sq):
                    break
                sq = [(cx, cy, oa, s * 0.96) for (cx, cy, oa, s) in sq]
            if _valid(sq):
                sc = _score(sq)
                if sc > best_sc:
                    best_sc = sc
                    best = sq
    return best


# ---------- improvement moves ----------

def _grow_all(squares, passes=60):
    sq = list(squares)
    n = len(sq)
    for _ in range(passes):
        improved = False
        order = list(range(n))
        random.shuffle(order)
        for i in order:
            cx, cy, ang, s = sq[i]
            lo, hi = 0.0, 1.0
            best_s = s
            for _ in range(20):
                mid = 0.5 * (lo + hi)
                trial = list(sq)
                trial[i] = (cx, cy, ang, mid)
                if _valid(trial):
                    lo = mid
                    best_s = mid
                else:
                    hi = mid
            if best_s > s + 1e-9:
                sq[i] = (cx, cy, ang, best_s)
                improved = True
        if not improved:
            break
    return sq


def _grow_all_with_rot(squares, passes=40):
    """Grow, and occasionally try to grow a square with a small rotation at the same time."""
    sq = list(squares)
    n = len(sq)
    for _ in range(passes):
        improved = False
        order = list(range(n))
        random.shuffle(order)
        for i in order:
            cx, cy, ang, s = sq[i]
            # try a few nearby angles
            best_local = (ang, s)
            bs = s
            for da in (0.0, 0.02, -0.02, 0.05, -0.05, 0.01, -0.01):
                a2 = (ang + da) % 1.0
                lo, hi = 0.0, 1.0
                bb = 0.0
                for _ in range(16):
                    mid = 0.5 * (lo + hi)
                    trial = list(sq)
                    trial[i] = (cx, cy, a2, mid)
                    if _valid(trial):
                        lo = mid
                        bb = mid
                    else:
                        hi = mid
                if bb > bs + 1e-9:
                    bs = bb
                    best_local = (a2, bb)
            if bs > s + 1e-9:
                sq[i] = (cx, cy, best_local[0], bs)
                improved = True
        if not improved:
            break
    return sq


def _local_search(n, squares, iters=20000):
    if n == 0:
        return squares
    best = list(squares)
    best_score = _score(best)
    cur = list(best)
    cur_score = best_score
    no_improve = 0
    for _ in range(iters):
        i = random.randrange(n)
        cx, cy, ang, s = cur[i]
        move = random.random()
        if move < 0.40:
            ds = random.uniform(0.0, 0.03)
            nc = (cx, cy, ang, min(1.0, s + ds))
        elif move < 0.65:
            a = random.random() * 2 * PI
            d = random.uniform(0.0, 0.02)
            nc = (min(1.0, max(0.0, cx + math.cos(a) * d)),
                  min(1.0, max(0.0, cy + math.sin(a) * d)), ang, s)
        elif move < 0.85:
            nc = (cx, cy, (ang + random.uniform(-0.15, 0.15)) % 1.0, s)
        else:
            bx, by = cx, cy
            for _ in range(8):
                tx = random.random()
                ty = random.random()
                trial = list(cur)
                trial[i] = (tx, ty, ang, s)
                if _valid(trial) and _score(trial) >= cur_score:
                    bx, by = tx, ty
                    break
            nc = (bx, by, ang, s)
        old = cur[i]
        cur[i] = nc
        if _valid(cur):
            sc = _score(cur)
            if sc >= cur_score - 1e-12:
                cur_score = sc
                if sc > best_score:
                    best_score = sc
                    best = list(cur)
                no_improve = 0
            elif random.random() < 0.03:
                cur_score = sc
                no_improve += 1
            else:
                cur[i] = old
                no_improve += 1
        else:
            cur[i] = old
            no_improve += 1
        if no_improve > 4000:
            cur = list(best)
            k = random.randrange(n)
            cx, cy, ang, s = cur[k]
            a = random.random() * 2 * PI
            d = random.uniform(0.0, 0.02)
            cur[k] = (min(1.0, max(0.0, cx + math.cos(a) * d)),
                      min(1.0, max(0.0, cy + math.sin(a) * d)), ang, s)
            if not _valid(cur):
                cur = list(best)
            cur_score = _score(cur)
            no_improve = 0
    return best


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    candidates = [_grid_pack(n), _bigrow_shelf(n), _maxmin_seed(n)]
    pw = _pinwheel_seed(n)
    if pw is not None and _valid(pw):
        candidates.append(pw)
    # rotated variants of the axis-aligned seeds
    base_for_rot = _grid_pack(n)
    for _ in range(3):
        r = _rotate_client(n, base_for_rot)
        if r is not None and _valid(r):
            candidates.append(r)

    seeds = [c for c in candidates if c is not None and _valid(c)]
    if not seeds:
        seeds = [_grid_pack(n)]

    iters = 8000 if n <= 10 else (14000 if n <= 50 else 8000)
    best = None
    best_sc = -1.0
    random.shuffle(seeds)
    for seed in seeds:
        cand = _grow_all_with_rot(seed)
        cand = _local_search(n, cand, iters=iters)
        cand = _grow_all_with_rot(cand)
        if _valid(cand):
            sc = _score(cand)
            if sc > best_sc:
                best_sc = sc
                best = cand
    if best is None:
        best = _grid_pack(n)

    if not _valid(best):
        result = []
        for sq in best:
            if _valid(result + [sq]):
                result.append(sq)
            else:
                result.append((0.5, 0.5, 0.0, 0.0))
        best = result
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))
    return best[:n]
# EVOLVE-BLOCK-END
