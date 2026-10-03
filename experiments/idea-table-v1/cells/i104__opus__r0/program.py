# EVOLVE-BLOCK-START
"""Constructions (grid / merged block / p x p + L-strip, with splitting/dropping)
plus a cross-entropy-method search over size multisets decoded by a skyline placer."""
import math
import time
import numpy as np


# ---------------- constructive families ----------------

def _grid(k):
    s = 1.0 / k
    return [(i * s, j * s, s) for i in range(k) for j in range(k)]


def _merge(k, m):
    s = 1.0 / k
    sq = [(0.0, 0.0, m * s)]
    for i in range(k):
        for j in range(k):
            if i < m and j < m:
                continue
            sq.append((i * s, j * s, s))
    return sq


def _pq(p, q):
    t = 1.0 / (q + 1)
    A = q * t
    a = A / p
    sq = [(i * a, j * a, a) for i in range(p) for j in range(p)]
    for i in range(q + 1):
        sq.append((A, i * t, t))
    for j in range(q):
        sq.append((j * t, A, t))
    return sq


def _fit(sq, n):
    sq = list(sq)
    if len(sq) > n:
        sq.sort(key=lambda z: -z[2])
        sq = sq[:n]
        return sq
    while n - len(sq) >= 3:
        idx = max(range(len(sq)), key=lambda i: sq[i][2])
        x, y, s = sq.pop(idx)
        h = s / 2.0
        sq += [(x, y, h), (x + h, y, h), (x, y + h, h), (x + h, y + h, h)]
    return sq


def _constructions(n):
    cands = []
    K = math.isqrt(n) + 3
    for k in range(1, K + 1):
        cands.append(_grid(k))
        for m in range(2, k):
            cands.append(_merge(k, m))
    for p in range(1, K + 1):
        for q in range(1, n + 2):
            if p * p + 2 * q + 1 > n + 2 * K:
                break
            cands.append(_pq(p, q))
    best, bval = None, -1.0
    for c in cands:
        f = _fit(c, n)
        v = sum(z[2] for z in f)
        if v > bval + 1e-12:
            bval, best = v, f
    return best, bval


# ---------------- skyline decoder ----------------

def _skyline(sizes, L):
    """sizes: list of integer sides (desc sorted). Returns placed list (x,y,s) and value."""
    segs = [[0, L, 0]]
    placed = []
    for s in sizes:
        if s <= 0:
            continue
        best = None
        nseg = len(segs)
        for i in range(nseg):
            x = segs[i][0]
            if x + s > L:
                break
            y = 0
            j = i
            while j < nseg and segs[j][0] < x + s:
                if segs[j][2] > y:
                    y = segs[j][2]
                j += 1
            if y + s <= L and (best is None or (y, x) < (best[0], best[1])):
                best = (y, x, i)
        if best is None:
            continue
        y, x, i = best
        placed.append((x, y, s))
        new = segs[:i]
        new.append([x, s, y + s])
        j = i
        while j < nseg:
            sx, sw, sh = segs[j]
            if sx + sw <= x + s:
                j += 1
                continue
            if sx < x + s:
                new.append([x + s, sx + sw - (x + s), sh])
            else:
                new.append([sx, sw, sh])
            j += 1
        merged = []
        for sg in new:
            if merged and merged[-1][2] == sg[2]:
                merged[-1][1] += sg[1]
            else:
                merged.append(sg)
        segs = merged
    return placed


def _cem(n, seed_sides, time_budget):
    dmax = max(4, int(3 * math.sqrt(n)))
    L = 1
    for d in range(1, dmax + 1):
        L = L * d // math.gcd(L, d)
    T = dmax + 1  # type 0 = zero, type d = side 1/d
    counts = np.full(T, 0.05)
    for s in seed_sides:
        if s <= 1e-12:
            counts[0] += 1
            continue
        d = int(math.ceil(1.0 / s - 1e-9))
        d = min(max(d, 1), dmax)
        counts[d] += 1
    p = counts / counts.sum()
    rng = np.random.default_rng(12345)
    best_val, best_pl = -1.0, None
    t0 = time.time()
    N = 160
    ne = max(4, N // 10)
    cache = {}
    while time.time() - t0 < time_budget:
        samples = rng.choice(T, size=(N, n), p=p)
        scored = []
        for row in samples:
            key = tuple(sorted(row.tolist()))
            if key in cache:
                val, pl = cache[key]
            else:
                sizes = sorted([L // d for d in row if d > 0], reverse=True)
                pl = _skyline(sizes, L)
                val = sum(z[2] for z in pl) / L
                cache[key] = (val, pl)
            # types actually used (unplaced -> zero)
            used = np.zeros(T)
            for z in pl:
                used[L // z[2]] += 1
            used[0] += n - len(pl)
            scored.append((val, used))
            if val > best_val + 1e-12:
                best_val, best_pl = val, pl
            if time.time() - t0 > time_budget:
                break
        scored.sort(key=lambda z: -z[0])
        el = scored[:ne]
        newp = sum(u for _, u in el) + 1e-3
        newp = newp / newp.sum()
        p = 0.7 * newp + 0.3 * p
        p = np.maximum(p, 1e-4)
        p = p / p.sum()
    if best_pl is None:
        return None, -1.0
    sq = [(x / L, y / L, s / L) for (x, y, s) in best_pl]
    return sq, best_val


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    best, bval = _constructions(n)
    try:
        sq, v = _cem(n, [z[2] for z in best], 6.0)
        if sq is not None and v > bval + 1e-12:
            best, bval = sq, v
    except Exception:
        pass
    out = []
    for (x, y, s) in best[:n]:
        s2 = max(0.0, s - 1e-12)
        cx = min(1.0, max(0.0, x + s / 2.0))
        cy = min(1.0, max(0.0, y + s / 2.0))
        out.append((cx, cy, 0.0, min(1.0, s2)))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
