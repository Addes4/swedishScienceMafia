# EVOLVE-BLOCK-START
import math
import time
import random
import numpy as np

try:
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def _grid_layout(k, blocks):
    """blocks: list of (ox, oy, m, j) in cell units. Returns rects (x,y,s)."""
    c = 1.0 / k
    covered = set()
    rects = []
    for (ox, oy, m, j) in blocks:
        for a in range(ox, ox + m):
            for b in range(oy, oy + m):
                covered.add((a, b))
        if j > 0:
            s = m * c / j
            for a in range(j):
                for b in range(j):
                    rects.append((ox * c + a * s, oy * c + b * s, s))
    for a in range(k):
        for b in range(k):
            if (a, b) not in covered:
                rects.append((a * c, b * c, c))
    return rects


def _family(n):
    best = (-1.0, None)
    if n <= 0:
        return []
    r = math.isqrt(n)
    K = 2 * r + 3
    J = r + 2
    for k in range(1, K + 1):
        for m in range(0, k + 1):
            for j in range(0, J + 1):
                if m == 0 and j > 0:
                    continue
                cnt = k * k - m * m + j * j
                if cnt > n or cnt <= 0:
                    continue
                val = (k * k - m * m + m * j) / k
                if val > best[0] + 1e-12:
                    best = (val, (k, [(0, 0, m, j)] if m > 0 else []))
    # two blocks
    if K ** 3 * J * J <= 3_000_000:
        for k in range(2, K + 1):
            for m1 in range(1, k):
                for m2 in range(1, min(m1, k - m1) + 1):
                    for j1 in range(0, J + 1):
                        for j2 in range(0, J + 1):
                            cnt = k * k - m1 * m1 - m2 * m2 + j1 * j1 + j2 * j2
                            if cnt > n or cnt <= 0:
                                continue
                            val = (k * k - m1 * m1 - m2 * m2 + m1 * j1 + m2 * j2) / k
                            if val > best[0] + 1e-12:
                                best = (val, (k, [(0, 0, m1, j1), (k - m2, k - m2, m2, j2)]))
    k, blocks = best[1]
    rects = _grid_layout(k, blocks)
    return rects[:n]


def _topology(rects, rng=None):
    n = len(rects)
    rel = []
    for i in range(n):
        xi, yi, si = rects[i]
        for j in range(i + 1, n):
            xj, yj, sj = rects[j]
            opts = [
                (xj - (xi + si), i, j, 0),
                (xi - (xj + sj), j, i, 0),
                (yj - (yi + si), i, j, 1),
                (yi - (yj + sj), j, i, 1),
            ]
            if rng is not None:
                opts = [(g + rng.random() * 1e-9, a, b, ax) for (g, a, b, ax) in opts]
            g, a, b, ax = max(opts)
            rel.append((a, b, ax))
    return rel


def _lp(rects, rel, lbs):
    n = len(rects)
    rows, cols, vals = [], [], []
    rhs = []
    r = 0
    for (a, b, ax) in rel:
        off = 0 if ax == 0 else n
        rows += [r, r, r]
        cols += [off + a, 2 * n + a, off + b]
        vals += [1.0, 1.0, -1.0]
        rhs.append(0.0)
        r += 1
    for i in range(n):
        for off in (0, n):
            rows += [r, r]
            cols += [off + i, 2 * n + i]
            vals += [1.0, 1.0]
            rhs.append(1.0)
            r += 1
    A = coo_matrix((vals, (rows, cols)), shape=(r, 3 * n)).tocsr()
    c = np.zeros(3 * n)
    c[2 * n:] = -1.0
    bounds = [(0.0, 1.0)] * (2 * n) + [(lbs[i], 1.0) for i in range(n)]
    try:
        res = linprog(c, A_ub=A, b_ub=np.array(rhs), bounds=bounds, method="highs")
    except Exception:
        return None
    if res.status != 0:
        return None
    v = res.x
    out = [(float(v[i]), float(v[n + i]), max(0.0, float(v[2 * n + i]))) for i in range(n)]
    return out


def _valid(rects, tol=1e-9):
    n = len(rects)
    for (x, y, s) in rects:
        if x < -tol or y < -tol or x + s > 1 + tol or y + s > 1 + tol:
            return False
    for i in range(n):
        xi, yi, si = rects[i]
        if si <= tol:
            continue
        for j in range(i + 1, n):
            xj, yj, sj = rects[j]
            if sj <= tol:
                continue
            ox = min(xi + si, xj + sj) - max(xi, xj)
            oy = min(yi + si, yj + sj) - max(yi, yj)
            if ox > 1e-7 and oy > 1e-7:
                return False
    return True


def _total(rects):
    return sum(s for _, _, s in rects)


def _insert(base, deadline, rng):
    n1 = len(base) + 1
    pts = set()
    for (x, y, s) in base:
        for px in (x, x + s):
            for py in (y, y + s):
                pts.add((round(px, 9), round(py, 9)))
    for p in [(0, 0), (0, 1), (1, 0), (1, 1), (0.5, 0), (0, 0.5), (1, 0.5), (0.5, 1)]:
        pts.add(p)
    pts = [p for p in pts if 0 <= p[0] <= 1 and 0 <= p[1] <= 1]
    rng.shuffle(pts)
    best_val, best = -1.0, None
    steps = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5]
    for (px, py) in pts:
        for trial in range(2):
            if time.time() > deadline:
                return best_val, best
            cur = list(base) + [(min(px, 1.0), min(py, 1.0), 0.0)]
            for t in steps:
                rel = _topology(cur, rng if trial else None)
                lbs = [0.0] * n1
                lbs[-1] = t
                sol = _lp(cur, rel, lbs)
                if sol is None:
                    break
                cur = sol
                val = _total(cur)
                if val > best_val + 1e-9 and _valid(cur):
                    best_val, best = val, cur
    return best_val, best


def _delete(big, deadline, rng):
    best_val, best = -1.0, None
    for i in range(len(big)):
        if time.time() > deadline:
            break
        cur = big[:i] + big[i + 1:]
        for _ in range(3):
            rel = _topology(cur)
            sol = _lp(cur, rel, [0.0] * len(cur))
            if sol is None:
                break
            cur = sol
        val = _total(cur)
        if val > best_val + 1e-9 and _valid(cur):
            best_val, best = val, cur
    return best_val, best


def solve(n):
    t0 = time.time()
    deadline = t0 + 40.0
    rng = random.Random(1)
    rects = _family(n)
    rects = rects + [(0.5, 0.5, 0.0)] * (n - len(rects))
    best = rects
    best_val = _total(rects)

    if HAVE_SCIPY and n >= 2 and n <= 60:
        try:
            # polish
            sol = _lp(best, _topology(best), [0.0] * n)
            if sol is not None and _total(sol) > best_val + 1e-9 and _valid(sol):
                best, best_val = sol, _total(sol)
            # insertion homotopy from n-1
            base = _family(n - 1)
            base = base + [(0.5, 0.5, 0.0)] * (n - 1 - len(base))
            v, r = _insert(base, t0 + 25.0, rng)
            if r is not None and v > best_val + 1e-9:
                best, best_val = r, v
            # deletion path from n+1
            big = _family(n + 1)
            big = big + [(0.5, 0.5, 0.0)] * (n + 1 - len(big))
            v, r = _delete(big, deadline, rng)
            if r is not None and v > best_val + 1e-9:
                best, best_val = r, v
        except Exception:
            pass

    out = []
    for (x, y, s) in best[:n]:
        s2 = max(0.0, s * (1 - 1e-9) - 1e-12)
        cx = min(1.0, max(0.0, x + s / 2))
        cy = min(1.0, max(0.0, y + s / 2))
        out.append((cx, cy, 0.0, min(1.0, s2)))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
