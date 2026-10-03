# EVOLVE-BLOCK-START
"""Guillotine-packing DP on an integer grid (strip/column patterns are special cases)."""
import math
import time
import numpy as np


def _dp(D, n):
    m = min(n, D * D)
    NEG = -10 ** 9
    G = np.zeros((D + 1, D + 1, m + 1), dtype=np.int64)
    kind = np.zeros((D + 1, D + 1, m + 1), dtype=np.int8)
    cut = np.zeros((D + 1, D + 1, m + 1), dtype=np.int32)
    cc = np.zeros((D + 1, D + 1, m + 1), dtype=np.int32)
    ar = np.arange(m + 1)
    I2 = ar[:, None] - ar[None, :]
    mask = np.where(I2 < 0, NEG, 0).astype(np.int64)
    I2 = np.clip(I2, 0, None)
    for a in range(1, D + 1):
        for b in range(1, D + 1):
            best = np.full(m + 1, min(a, b), dtype=np.int64)
            best[0] = 0
            kd = np.zeros(m + 1, dtype=np.int8)
            ct = np.zeros(m + 1, dtype=np.int32)
            c1s = np.zeros(m + 1, dtype=np.int32)
            for direction in (1, 2):
                if direction == 1:
                    h = a // 2
                    if h < 1:
                        continue
                    xs = np.arange(1, h + 1)
                    A = G[xs, b]
                    B = G[a - xs, b]
                else:
                    h = b // 2
                    if h < 1:
                        continue
                    xs = np.arange(1, h + 1)
                    A = G[a, xs]
                    B = G[a, b - xs]
                T = A[:, None, :] + B[:, I2] + mask[None, :, :]
                T = T.transpose(1, 0, 2).reshape(m + 1, -1)
                idx = T.argmax(axis=1)
                val = T[ar, idx]
                better = val > best
                better[0] = False
                if better.any():
                    best = np.where(better, val, best)
                    kd = np.where(better, direction, kd).astype(np.int8)
                    ct = np.where(better, xs[idx // (m + 1)], ct).astype(np.int32)
                    c1s = np.where(better, idx % (m + 1), c1s).astype(np.int32)
            G[a, b] = best
            kind[a, b] = kd
            cut[a, b] = ct
            cc[a, b] = c1s
    return m, G, kind, cut, cc


def _build(D, n):
    m, G, kind, cut, cc = _dp(D, n)
    val = G[D, D, m] / D
    out = []
    stack = [(D, D, m, 0, 0)]
    while stack:
        a, b, c, x0, y0 = stack.pop()
        if c <= 0 or a <= 0 or b <= 0:
            continue
        k = kind[a, b, c]
        if k == 0:
            s = min(a, b)
            out.append(((x0 + s / 2) / D, (y0 + s / 2) / D, 0.0, s / D))
        elif k == 1:
            x = int(cut[a, b, c]); c1 = int(cc[a, b, c])
            stack.append((x, b, c1, x0, y0))
            stack.append((a - x, b, c - c1, x0 + x, y0))
        else:
            y = int(cut[a, b, c]); c1 = int(cc[a, b, c])
            stack.append((a, y, c1, x0, y0))
            stack.append((a, b - y, c - c1, x0, y0 + y))
    return val, out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    k = math.isqrt(n)
    side = 1.0 / k
    best_sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    best_val = float(k)
    Ds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 24, 30, 36, 42, 48, 60]
    last_t, last_D = None, None
    for D in Ds:
        el = time.time() - t0
        if last_t is not None:
            pred = last_t * (D / last_D) ** 2.5
            if el + pred > 40:
                break
        ts = time.time()
        try:
            v, sq = _build(D, n)
        except MemoryError:
            break
        last_t = max(time.time() - ts, 1e-3)
        last_D = D
        if v > best_val + 1e-12 and len(sq) <= n:
            best_val, best_sq = v, sq
    res = list(best_sq)[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res
# EVOLVE-BLOCK-END
