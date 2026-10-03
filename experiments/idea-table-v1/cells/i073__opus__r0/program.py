# EVOLVE-BLOCK-START
"""Guillotine DP over integer grids (several resolutions N), with rotated
multi-square tiles (found by multi-start penalty optimisation) inserted as
extra base cases for rectangles of aspect 1:1, 3:2, 2:1, 3:1."""
import math
import time
import numpy as np

try:
    from scipy.optimize import minimize
except Exception:  # pragma: no cover
    minimize = None

_TILE_CACHE = None
_TILE_WS = (1.0, 1.5, 2.0, 3.0)


# ---------------------------------------------------------------- tiles
def _tile_violation(x, y, t, s, W, I, J):
    c, sn = np.cos(t), np.sin(t)
    e = 0.5 * s * (np.abs(c) + np.abs(sn))
    v = max(0.0, float(np.max(e - x)), float(np.max(x + e - W)),
            float(np.max(e - y)), float(np.max(y + e - 1.0)))
    if len(I):
        dx = x[J] - x[I]
        dy = y[J] - y[I]
        phi = np.stack([t[I], t[I] + np.pi / 2, t[J], t[J] + np.pi / 2], 1)
        cp, sp = np.cos(phi), np.sin(phi)
        d = np.abs(dx[:, None] * cp + dy[:, None] * sp)
        ai = t[I][:, None] - phi
        aj = t[J][:, None] - phi
        ri = 0.5 * s[I][:, None] * (np.abs(np.cos(ai)) + np.abs(np.sin(ai)))
        rj = 0.5 * s[J][:, None] * (np.abs(np.cos(aj)) + np.abs(np.sin(aj)))
        ov = (ri + rj - d).min(1)
        v = max(v, float(np.max(ov)))
    return v


def _optimize_tile(W, m, rng, tmax):
    if minimize is None:
        return None
    I, J = np.triu_indices(m, 1)

    def pen(z):
        x, y, t, s = z[:m], z[m:2 * m], z[2 * m:3 * m], z[3 * m:]
        c, sn = np.cos(t), np.sin(t)
        e = 0.5 * s * (np.abs(c) + np.abs(sn))
        P = (np.sum(np.maximum(e - x, 0) ** 2) + np.sum(np.maximum(x + e - W, 0) ** 2)
             + np.sum(np.maximum(e - y, 0) ** 2) + np.sum(np.maximum(y + e - 1, 0) ** 2))
        dx = x[J] - x[I]
        dy = y[J] - y[I]
        phi = np.stack([t[I], t[I] + np.pi / 2, t[J], t[J] + np.pi / 2], 1)
        d = np.abs(dx[:, None] * np.cos(phi) + dy[:, None] * np.sin(phi))
        ai = t[I][:, None] - phi
        aj = t[J][:, None] - phi
        ri = 0.5 * s[I][:, None] * (np.abs(np.cos(ai)) + np.abs(np.sin(ai)))
        rj = 0.5 * s[J][:, None] * (np.abs(np.cos(aj)) + np.abs(np.sin(aj)))
        ov = np.maximum((ri + rj - d).min(1), 0)
        return P + np.sum(ov ** 2)

    def f(z, mu):
        return -np.sum(z[3 * m:]) + mu * pen(z)

    bounds = [(0, W)] * m + [(0, 1)] * m + [(0, np.pi / 2)] * m + [(0, 1)] * m
    best = None
    t0 = time.time()
    while time.time() - t0 < tmax:
        z = np.concatenate([rng.uniform(0, W, m), rng.uniform(0, 1, m),
                            rng.uniform(0, np.pi / 2, m), rng.uniform(0.1, 0.6, m)])
        try:
            for mu in (10.0, 100.0, 1e3, 1e4, 1e5, 1e6):
                res = minimize(f, z, args=(mu,), method='L-BFGS-B', bounds=bounds,
                               options={'maxiter': 200})
                z = res.x
                if time.time() - t0 > tmax * 1.5:
                    break
        except Exception:
            continue
        x, y, t, s = (z[:m].copy(), z[m:2 * m].copy(), z[2 * m:3 * m].copy(),
                      z[3 * m:].copy())
        ok = False
        for _ in range(30):
            v = _tile_violation(x, y, t, s, W, I, J)
            if v <= 0:
                ok = True
                break
            s = np.maximum(0.0, s - 2 * v - 1e-12)
        if not ok:
            continue
        s = s * (1 - 1e-9)
        val = float(np.sum(s))
        if best is None or val > best[0]:
            best = (val, [(float(x[i]), float(y[i]), float(t[i]), float(s[i])) for i in range(m)])
    return best


def _get_tiles(budget):
    global _TILE_CACHE
    if _TILE_CACHE is not None:
        return _TILE_CACHE
    rng = np.random.default_rng(12345)
    tiles = []
    combos = [(W, m) for W in _TILE_WS for m in range(2, 7)]
    per = budget / len(combos)
    for W, m in combos:
        b = _optimize_tile(W, m, rng, per)
        if b is not None and b[0] > 0:
            tiles.append((W, m, b[0], b[1]))
    _TILE_CACHE = tiles
    return tiles


# ---------------------------------------------------------------- DP
def _canon(a, b):
    return (a, b) if a <= b else (b, a)


def _vec(arr, L):
    if len(arr) >= L:
        return arr[:L]
    return np.concatenate([arr, np.full(L - len(arr), arr[-1])])


def _run_dp(N, M, tiles, deadline):
    F, K, PA, PB = {}, {}, {}, {}
    idx_cache = {}
    for w in range(1, N + 1):
        if time.time() > deadline:
            return None
        for h in range(w, N + 1):
            L = min(M, w * h) + 1
            val = np.zeros(L)
            kind = np.zeros(L, dtype=np.int64)
            pa = np.zeros(L, dtype=np.int64)
            pb = np.zeros(L, dtype=np.int64)
            if w == h:
                val[1:] = w
            cuts = []
            for a in range(1, w // 2 + 1):
                cuts.append((1, a, (a, h), (w - a, h)))
            for b in range(1, h // 2 + 1):
                cuts.append((2, b, _canon(w, b), _canon(w, h - b)))
            if cuts and L > 1:
                if L not in idx_cache:
                    mm = np.arange(L)[:, None]
                    m1 = np.arange(L)[None, :]
                    idx_cache[L] = (np.maximum(mm - m1, 0), m1 > mm)
                IDX, MASK = idx_cache[L]
                types = np.array([c[0] for c in cuts])
                poss = np.array([c[1] for c in cuts])
                A = np.stack([_vec(F[c[2]], L) for c in cuts])
                B = np.stack([_vec(F[c[3]], L) for c in cuts])
                chunk = max(1, int(3e6 // (L * L)))
                ar = np.arange(L)
                gbv = np.full(L, -np.inf)
                gcb = np.zeros(L, dtype=np.int64)
                gm1 = np.zeros(L, dtype=np.int64)
                for s0 in range(0, len(cuts), chunk):
                    Ac = A[s0:s0 + chunk]
                    Bc = B[s0:s0 + chunk]
                    C = Bc[:, IDX] + Ac[:, None, :]
                    C[:, MASK] = -np.inf
                    am = C.argmax(2)
                    mx = np.take_along_axis(C, am[:, :, None], 2)[:, :, 0]
                    cb = mx.argmax(0)
                    bv = mx[cb, ar]
                    better = bv > gbv
                    gbv[better] = bv[better]
                    gcb[better] = cb[better] + s0
                    gm1[better] = am[cb, ar][better]
                upd = gbv > val + 1e-9
                if np.any(upd):
                    val[upd] = gbv[upd]
                    kind[upd] = types[gcb[upd]]
                    pa[upd] = poss[gcb[upd]]
                    pb[upd] = gm1[upd]
            for ti, (Wt, mt, sm, _) in enumerate(tiles):
                if mt < L and abs(w * Wt - h) < 1e-9:
                    v = sm * w
                    for m in range(mt, L):
                        if v > val[m] + 1e-9:
                            val[m] = v
                            kind[m] = 3
                            pa[m] = ti
            F[(w, h)] = val
            K[(w, h)] = kind
            PA[(w, h)] = pa
            PB[(w, h)] = pb
    return F, K, PA, PB


def _build(tab, tiles, w, h, m):
    F, K, PA, PB = tab
    L = len(F[(w, h)])
    out = []
    if m >= L:
        out += [(0.0, 0.0, 0.0, 0.0)] * (m - L + 1)
        m = L - 1
    k = int(K[(w, h)][m])
    if k == 0:
        if w == h and m >= 1:
            out.append((w / 2.0, h / 2.0, 0.0, float(w)))
            out += [(0.0, 0.0, 0.0, 0.0)] * (m - 1)
        else:
            out += [(0.0, 0.0, 0.0, 0.0)] * m
    elif k == 1:
        a = int(PA[(w, h)][m])
        m1 = int(PB[(w, h)][m])
        out += _place(tab, tiles, a, h, m1, 0.0, 0.0)
        out += _place(tab, tiles, w - a, h, m - m1, float(a), 0.0)
    elif k == 2:
        b = int(PA[(w, h)][m])
        m1 = int(PB[(w, h)][m])
        out += _place(tab, tiles, w, b, m1, 0.0, 0.0)
        out += _place(tab, tiles, w, h - b, m - m1, 0.0, float(b))
    else:
        Wt, mt, sm, sq = tiles[int(PA[(w, h)][m])]
        for (x, y, t, s) in sq:
            ang = (-(t / (2 * math.pi))) % 0.25
            out.append((y * w, x * w, ang, s * w))
        out += [(0.0, 0.0, 0.0, 0.0)] * (m - mt)
    return out


def _place(tab, tiles, pw, ph, m, ox, oy):
    a, b = _canon(pw, ph)
    sq = _build(tab, tiles, a, b, m)
    res = []
    flip = (pw != a)
    for (x, y, t, s) in sq:
        if flip:
            x, y, t = y, x, (-t) % 0.25
        res.append((x + ox, y + oy, t, s))
    return res


def solve(n):
    start = time.time()
    if n <= 0:
        return []
    tiles = _get_tiles(9.0)
    deadline = start + 48.0
    M = n
    k = max(1, math.isqrt(n))
    Ns = set(range(1, 25)) | {30, 36, 40, 42, 48, 60, 72, 84, 90, 120}
    for a in (k - 1, k, k + 1, k + 2):
        if a >= 1:
            Ns.add(a)
            Ns.add(2 * a)
            if a + 1 >= 1:
                Ns.add(a * (a + 1) // math.gcd(a, a + 1))
    Ns = sorted(x for x in Ns if x >= 1)
    best_val, best_N, best_tab = -1.0, None, None
    last_N, last_t = None, None
    for N in Ns:
        now = time.time()
        if last_N is not None:
            pred = last_t * (N / last_N) ** 3 * 1.3
            if now + pred > deadline:
                break
        tab = _run_dp(N, M, tiles, deadline)
        el = time.time() - now
        if tab is None:
            break
        last_N, last_t = N, max(el, 1e-4)
        arr = tab[0][(N, N)]
        v = float(arr[min(n, len(arr) - 1)]) / N
        if v > best_val + 1e-12:
            best_val, best_N, best_tab = v, N, tab
    if best_tab is None:
        side = 1.0 / k
        sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
        return sq[:n]
    raw = _build(best_tab, tiles, best_N, best_N, n)
    N = float(best_N)
    out = []
    for (x, y, t, s) in raw:
        cx = min(1.0, max(0.0, x / N))
        cy = min(1.0, max(0.0, y / N))
        sd = min(1.0, max(0.0, s / N * (1 - 1e-12)))
        ang = t % 0.25
        if not (0.0 <= ang <= 1.0):
            ang = 0.0
        out.append((cx, cy, ang, sd))
    out = out[:n]
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
