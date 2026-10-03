# EVOLVE-BLOCK-START
import math
import time
import numpy as np


# ---------------------------------------------------------------- geometry
def _corners(sq):
    cx, cy, ang, s = sq
    th = 2 * math.pi * ang
    c, si = math.cos(th), math.sin(th)
    h = s / 2
    pts = []
    for ux, uy in ((h, h), (-h, h), (-h, -h), (h, -h)):
        pts.append((cx + ux * c - uy * si, cy + ux * si + uy * c))
    return pts, th


def _sep(p1, t1, p2, t2, tol=1e-9):
    for th in (t1, t2):
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            a = [x * ax[0] + y * ax[1] for x, y in p1]
            b = [x * ax[0] + y * ax[1] for x, y in p2]
            if max(a) <= min(b) + tol or max(b) <= min(a) + tol:
                return True
    return False


def _verify(sqs):
    data = []
    for sq in sqs:
        for v in sq:
            if v < -1e-12 or v > 1 + 1e-12:
                return False
        if sq[3] <= 1e-15:
            continue
        pts, th = _corners(sq)
        for x, y in pts:
            if x < -1e-9 or x > 1 + 1e-9 or y < -1e-9 or y > 1 + 1e-9:
                return False
        data.append((pts, th))
    if len(data) > 400:
        return True
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if not _sep(data[i][0], data[i][1], data[j][0], data[j][1]):
                return False
    return True


def _clamp(v):
    return min(1.0, max(0.0, v))


def _finish(sqs, n):
    out = [(_clamp(a), _clamp(b), _clamp(c), _clamp(d)) for a, b, c, d in sqs]
    out.sort(key=lambda q: -q[3])
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out


# ---------------------------------------------------------------- explicit family
def _family(n):
    best_val, best_cfg = -1.0, None
    K = math.isqrt(n) + 2
    for k in range(1, K + 1):
        for m in range(0, k + 1):
            jr = [0] if m == 0 else range(0, math.isqrt(n) + 3)
            for j in jr:
                sizes = [1.0 / k] * (k * k - m * m)
                if m > 0 and j > 0:
                    sizes += [m / (k * j)] * (j * j)
                if not sizes:
                    continue
                sizes.sort(reverse=True)
                val = sum(sizes[:n])
                if val > best_val + 1e-12:
                    best_val, best_cfg = val, (k, m, j)
    k, m, j = best_cfg
    sqs = []
    s = 1.0 / k
    for a in range(k):
        for b in range(k):
            if m > 0 and a < m and b < m:
                continue
            sqs.append(((a + 0.5) * s, (b + 0.5) * s, 0.0, s))
    if m > 0 and j > 0:
        t = m / (k * j)
        for a in range(j):
            for b in range(j):
                sqs.append(((a + 0.5) * t, (b + 0.5) * t, 0.0, t))
    return _finish(sqs, n)


# ---------------------------------------------------------------- guillotine DP
def _dp(N, n, deadline):
    C = n + 1
    I = np.arange(C)
    Imat = I[None, :]
    J = I[:, None] - Imat
    mask = J < 0
    Jc = np.clip(J, 0, None)
    F, typ, par, spl = {}, {}, {}, {}
    for a in range(1, N + 1):
        for b in range(a, N + 1):
            if time.time() > deadline:
                return None
            best = np.zeros(C)
            ty = np.zeros(C, dtype=np.int64)
            pa = np.zeros(C, dtype=np.int64)
            sp = np.zeros(C, dtype=np.int64)
            if a == b:
                best[1:] = a
                ty[1:] = 1
            cuts = [(2, b1) for b1 in range(1, b // 2 + 1)] + \
                   [(3, a1) for a1 in range(1, a // 2 + 1)]
            for kind, q in cuts:
                if kind == 2:
                    r1, r2 = (a, q), (a, b - q)
                else:
                    r1, r2 = (q, b), (a - q, b)
                G1 = F[(min(r1), max(r1))]
                G2 = F[(min(r2), max(r2))]
                A = G1[Imat] + G2[Jc]
                A[mask] = -1.0
                mv = A.max(1)
                am = A.argmax(1)
                upd = mv > best + 1e-9
                if upd.any():
                    best[upd] = mv[upd]
                    ty[upd] = kind
                    pa[upd] = q
                    sp[upd] = am[upd]
            F[(a, b)] = best
            typ[(a, b)] = ty
            par[(a, b)] = pa
            spl[(a, b)] = sp

    def rec(w, h, c):
        if w <= h:
            return rec_c(w, h, c)
        return [(y, x, s) for (x, y, s) in rec_c(h, w, c)]

    def rec_c(a, b, c):
        t = typ[(a, b)][c]
        if t == 0:
            return []
        if t == 1:
            return [(a / 2.0, a / 2.0, a)]
        q = int(par[(a, b)][c])
        i = int(spl[(a, b)][c])
        if t == 2:
            lo = rec(a, q, i)
            hi = [(x, y + q, s) for (x, y, s) in rec(a, b - q, c - i)]
            return lo + hi
        le = rec(q, b, i)
        ri = [(x + q, y, s) for (x, y, s) in rec(a - q, b, c - i)]
        return le + ri

    val = F[(N, N)][n] / N
    sq = [(x / N, y / N, 0.0, s / N) for (x, y, s) in rec(N, N, n)]
    return val, sq


# ---------------------------------------------------------------- tilted band
def _mindx(t, d, th):
    c, s = math.cos(th), math.sin(th)
    if d * c >= t:
        return 0.0
    dx1 = max(0.0, (t - d * s) / c)
    dx2 = (t + d * c) / s if s > 1e-12 else float("inf")
    return min(dx1, dx2)


def _tilted_band(n, deadline):
    if n < 2:
        return None
    k = math.isqrt(n - 1)
    if k < 1:
        return None
    best = None
    hs = [1.0] if k == 1 else list(np.linspace(1.0 / k, 1.6 / k, 13))
    for h in hs:
        s_row = 0.0 if k == 1 else min(1.0 / k, (1 - h) / (k - 1))
        for th in np.linspace(0.002, math.pi / 4, 30):
            if time.time() > deadline:
                return best
            cs = math.cos(th) + math.sin(th)
            for df in np.linspace(0, 1, 9):
                def feas(t):
                    e = t * cs / 2
                    if 2 * e > h + 1e-15:
                        return None
                    d = df * (h - 2 * e)
                    dx = _mindx(t, d, th)
                    if k * dx + 2 * e > 1 + 1e-15:
                        return None
                    return (e, d, dx)
                lo, hi = 0.0, h
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if feas(mid) is not None:
                        lo = mid
                    else:
                        hi = mid
                t = lo * (1 - 1e-9)
                r = feas(t)
                if r is None:
                    continue
                val = k * (k - 1) * s_row + (k + 1) * t
                if best is None or val > best[0]:
                    best = (val, h, s_row, th, t, r)
    if best is None:
        return None
    val, h, s_row, th, t, (e, d, dx) = best
    sqs = []
    ang = (th / (2 * math.pi)) % 1.0
    for i in range(k + 1):
        sqs.append((e + i * dx, e + (d if i % 2 else 0.0), ang, t))
    for r in range(k - 1):
        for cidx in range(k):
            sqs.append(((cidx + 0.5) * s_row, h + (r + 0.5) * s_row, 0.0, s_row))
    return sqs


# ---------------------------------------------------------------- main
def _score(sqs):
    return sum(q[3] for q in sqs)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    start = time.time()
    k0 = math.isqrt(n)
    base = [((i + 0.5) / k0, (j + 0.5) / k0, 0.0, 1.0 / k0)
            for i in range(k0) for j in range(k0)]
    cands = [_finish(base, n)]
    try:
        cands.append(_family(n))
    except Exception:
        pass

    # guillotine DP on several resolutions
    if n <= 120:
        deadline = start + 35.0
        N = 1
        while N <= 40 and time.time() < deadline:
            est = (N ** 3) * ((n + 1) ** 2) / 4e7 + (N ** 3) * 2e-5
            if time.time() + est > deadline:
                break
            try:
                res = _dp(N, n, deadline)
            except Exception:
                res = None
            if res is not None:
                cands.append(_finish(res[1], n))
            N += 1

    # tilted band long shot
    try:
        tb = _tilted_band(n, start + 45.0)
        if tb is not None and len(tb) <= n:
            cands.append(_finish(tb, n))
    except Exception:
        pass

    cands.sort(key=lambda c: -_score(c))
    for c in cands:
        if len(c) == n and _verify(c):
            return c
    return _finish(base, n)
# EVOLVE-BLOCK-END
