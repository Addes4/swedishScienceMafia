# EVOLVE-BLOCK-START
"""Portfolio (sequential, deadline-guarded): closed-form grid families
(Erdos-Soifer style block replacements) + guillotine DP on rational lattices.
Best validated packing is returned."""
import math
import time
import numpy as np

_EPS_SHRINK = 1e-12


# ---------------------------------------------------------------- validation
def _valid(sq, n):
    if len(sq) != n:
        return False
    for (x, y, a, s) in sq:
        for v in (x, y, a, s):
            if not (0.0 <= v <= 1.0) or v != v:
                return False
        if s > 0:
            if x - s / 2 < -1e-12 or x + s / 2 > 1 + 1e-12:
                return False
            if y - s / 2 < -1e-12 or y + s / 2 > 1 + 1e-12:
                return False
            if a != 0.0:
                return False
    pos = [(x, y, s) for (x, y, a, s) in sq if s > 0]
    m = len(pos)
    for i in range(m):
        xi, yi, si = pos[i]
        for j in range(i + 1, m):
            xj, yj, sj = pos[j]
            h = (si + sj) / 2 - 1e-12
            if abs(xi - xj) < h and abs(yi - yj) < h:
                return False
    return True


def _score(sq):
    return sum(t[3] for t in sq)


def _finish(rects, n):
    """rects: list of (x0, y0, side) lower-left corners. Pad to n."""
    out = []
    for (x0, y0, s) in rects:
        s2 = max(0.0, s - _EPS_SHRINK)
        cx = min(1.0, max(0.0, x0 + s / 2))
        cy = min(1.0, max(0.0, y0 + s / 2))
        out.append((cx, cy, 0.0, s2))
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out


# ---------------------------------------------------------- closed-form family
def _family(n):
    best_val, best_cfg = -1.0, None
    kmax = min(n, math.isqrt(n) + 4)
    for k in range(1, kmax + 1):
        items = []
        for m in range(1, k + 1):
            for j in range(1, 4 * k + 4):
                if j == m:
                    continue
                if j * j - m * m > n:
                    break
                items.append((m, j))
        # states: (u, delta) -> (gain, sumsq, blocks)
        states = {(0, 0): (0, 0, ())}
        frontier = [(0, 0)]
        while frontier:
            newf = []
            for key in frontier:
                u, dl = key
                g, ss, bl = states[key]
                for (m, j) in items:
                    if u + m > k:
                        continue
                    nd = dl + j * j - m * m
                    if k * k + nd > 4 * n + 4 or k * k + nd < 0:
                        continue
                    nk = (u + m, nd)
                    ng = g + m * (j - m)
                    nss = ss + m * m
                    old = states.get(nk)
                    if old is None or ng > old[0] or (ng == old[0] and nss < old[1]):
                        states[nk] = (ng, nss, bl + ((m, j),))
                        newf.append(nk)
            frontier = list(set(newf))
        for (u, dl), (g, ss, bl) in states.items():
            cnt = k * k + dl
            free = k * k - ss
            r = max(0, cnt - n)
            if r > free:
                continue
            val = (k * k + g - r) / k
            if val > best_val + 1e-12:
                best_val, best_cfg = val, (k, bl, r)
    k, bl, r = best_cfg
    rects = []
    used = set()
    p = 0
    for (m, j) in bl:
        s = m / (k * j)
        for a in range(j):
            for b in range(j):
                rects.append((p / k + a * s, p / k + b * s, s))
        for a in range(p, p + m):
            for b in range(p, p + m):
                used.add((a, b))
        p += m
    free_cells = [(a, b) for a in range(k) for b in range(k) if (a, b) not in used]
    free_cells = free_cells[r:]
    for (a, b) in free_cells:
        rects.append((a / k, b / k, 1.0 / k))
    return _finish(rects, n)


# --------------------------------------------------------------- guillotine DP
def _guillotine(n, d, idx):
    L = n + 1
    NEG = -10 ** 9
    best = np.zeros((d + 1, d + 1, L), dtype=np.int64)
    negcol = None
    for a in range(1, d + 1):
        for b in range(1, d + 1):
            if b < a:
                best[a, b] = best[b, a]
                continue
            cur = np.zeros(L, dtype=np.int64)
            if a == b and L > 1:
                cur[1:] = a
            As, Bs = [], []
            if a >= 2:
                xs = np.arange(1, a // 2 + 1)
                As.append(best[xs, b])
                Bs.append(best[a - xs, b])
            if b >= 2:
                ys = np.arange(1, b // 2 + 1)
                As.append(best[a, ys])
                Bs.append(best[a, b - ys])
            if As:
                A = np.concatenate(As, axis=0)
                B = np.concatenate(Bs, axis=0)
                C = A.shape[0]
                Bp = np.concatenate([B, np.full((C, 1), NEG, dtype=np.int64)], axis=1)
                T = A[:, :, None] + Bp[:, idx]
                cand = T.max(axis=(0, 1))
                cur = np.maximum(cur, cand)
            best[a, b] = cur
    return best


def _reconstruct(best, d, n):
    rects = []
    stack = [(d, d, n, 0, 0)]
    while stack:
        a, b, c, x0, y0 = stack.pop()
        v = int(best[a, b, c])
        if v == 0 or c == 0:
            continue
        if a == b and v == a:
            rects.append((x0, y0, a))
            continue
        done = False
        for x in range(1, a // 2 + 1):
            A = best[x, b]
            B = best[a - x, b]
            for i in range(c + 1):
                if int(A[i]) + int(B[c - i]) == v:
                    stack.append((x, b, i, x0, y0))
                    stack.append((a - x, b, c - i, x0 + x, y0))
                    done = True
                    break
            if done:
                break
        if done:
            continue
        for y in range(1, b // 2 + 1):
            A = best[a, y]
            B = best[a, b - y]
            for i in range(c + 1):
                if int(A[i]) + int(B[c - i]) == v:
                    stack.append((a, y, i, x0, y0))
                    stack.append((a, b - y, c - i, x0, y0 + y))
                    done = True
                    break
            if done:
                break
    return [(x / d, y / d, s / d) for (x, y, s) in rects]


def _dp_portfolio(n, t_end, cur_best):
    L = n + 1
    ii = np.arange(L)[:, None]
    cc = np.arange(L)[None, :]
    idx = np.where(cc >= ii, cc - ii, L)
    kr = math.isqrt(n) + 3
    pri = sorted(set(k * j for k in range(1, kr + 1) for j in range(1, k + 4) if k * j <= 200))
    rest = [d for d in range(1, 201) if d not in pri]
    order = pri + rest
    best_sq, best_val = None, cur_best
    rate = None
    for d in order:
        now = time.time()
        if now >= t_end:
            break
        work = float(d) ** 3 * L * L + 1.0
        if rate is not None and now + rate * work * 1.3 > t_end:
            continue
        t0 = time.time()
        tab = _guillotine(n, d, idx)
        el = time.time() - t0
        if work > 1e5:
            r = el / work
            rate = r if rate is None else max(rate * 0.7, r)
        val = tab[d, d, n] / d
        if val > best_val + 1e-9:
            rects = _reconstruct(tab, d, n)
            sq = _finish(rects, n)
            if _valid(sq, n):
                best_val, best_sq = _score(sq), sq
    return best_sq


# --------------------------------------------------------------------- solve
def solve(n):
    t_start = time.time()
    k = max(1, math.isqrt(n))
    base = _finish([(i / k, j / k, 1.0 / k) for i in range(k) for j in range(k)], n)
    best_sq = base if _valid(base, n) else [(0.5, 0.5, 0.0, 0.0)] * n
    best_val = _score(best_sq)

    try:
        fam = _family(n)
        if _valid(fam, n) and _score(fam) > best_val:
            best_sq, best_val = fam, _score(fam)
    except Exception:
        pass

    try:
        t_end = t_start + 40.0
        sq = _dp_portfolio(n, t_end, best_val)
        if sq is not None and _valid(sq, n) and _score(sq) > best_val:
            best_sq, best_val = sq, _score(sq)
    except Exception:
        pass

    return best_sq
# EVOLVE-BLOCK-END
