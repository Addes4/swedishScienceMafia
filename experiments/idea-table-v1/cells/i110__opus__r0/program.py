# EVOLVE-BLOCK-START
"""Exact DP over guillotine square packings of a K x K integer board, for many K."""
import math
import time
import numpy as np


def _run_K(K, n, idx_cache):
    F = {}
    for a in range(1, K + 1):
        for b in range(a, K + 1):
            C = min(n, a * b)
            base = np.zeros(C + 1)
            kind = np.zeros(C + 1, dtype=np.int64)
            pos = np.zeros(C + 1, dtype=np.int64)
            left = np.zeros(C + 1, dtype=np.int64)
            if a == b:
                base[1:] = a
                kind[1:] = 1
            parts = []
            for p in range(1, a // 2 + 1):
                parts.append((2, p, (p, b), (a - p, b)))
            for p in range(1, b // 2 + 1):
                parts.append((3, p, (a, p), (a, b - p)))
            if parts:
                m = len(parts)
                As = np.empty((m, C + 1))
                Bs = np.empty((m, C + 1))
                for t, (_, _, d1, d2) in enumerate(parts):
                    As[t] = F[(min(d1), max(d1))][0][:C + 1]
                    Bs[t] = F[(min(d2), max(d2))][0][:C + 1]
                if C not in idx_cache:
                    cc = np.arange(C + 1)
                    idx_cache[C] = C + cc[:, None] - cc[None, :]
                IDX = idx_cache[C]
                Bp = np.concatenate([np.full((m, C), -np.inf), Bs], axis=1)
                T = Bp[:, IDX]
                S = As[:, None, :] + T
                S2 = S.transpose(1, 0, 2).reshape(C + 1, -1)
                j = S2.argmax(axis=1)
                best = S2[np.arange(C + 1), j]
                kk = j // (C + 1)
                ii = j % (C + 1)
                better = best > base + 1e-9
                for c in np.nonzero(better)[0]:
                    base[c] = best[c]
                    kind[c] = parts[kk[c]][0]
                    pos[c] = parts[kk[c]][1]
                    left[c] = ii[c]
            if C < n:
                ext = n - C
                base = np.concatenate([base, np.full(ext, base[C])])
                kind = np.concatenate([kind, np.full(ext, kind[C])])
                pos = np.concatenate([pos, np.full(ext, pos[C])])
                left = np.concatenate([left, np.full(ext, left[C])])
            F[(a, b)] = (base, kind, pos, left)
    return F


def _reconstruct(F, K, n):
    out = []
    stack = [(K, K, n, 0, 0)]
    while stack:
        w, h, c, x, y = stack.pop()
        if c <= 0:
            continue
        a, b = min(w, h), max(w, h)
        _, kind, pos, left = F[(a, b)]
        kd = int(kind[c])
        if kd == 0:
            continue
        if kd == 1:
            out.append((x, y, w))
            continue
        p = int(pos[c])
        i = int(left[c])
        if w > h:
            kd = 5 - kd
        if kd == 2:
            stack.append((p, h, i, x, y))
            stack.append((w - p, h, c - i, x + p, y))
        else:
            stack.append((w, p, i, x, y))
            stack.append((w, h - p, c - i, x, y + p))
    return out


def _cost(K, n):
    tot = 0
    for a in range(1, K + 1):
        for b in range(a, K + 1):
            C = min(n, a * b) + 1
            tot += (a // 2 + b // 2) * C * C + 50
    return tot


def solve(n):
    t0 = time.time()
    budget = 25.0
    if n <= 0:
        return []
    best_val = -1.0
    best_sq = None
    idx_cache = {}
    rate = 2e7
    for K in range(1, 121):
        el = time.time() - t0
        est = _cost(K, n) / rate
        if el + est > budget:
            if K > math.isqrt(n) + 3:
                break
            else:
                continue
        ts = time.time()
        F = _run_K(K, n, idx_cache)
        dt = time.time() - ts
        c = _cost(K, n)
        if dt > 0.05:
            rate = max(1e6, c / dt)
        val = F[(K, K)][0][n] / K
        if val > best_val + 1e-12:
            best_val = val
            cells = _reconstruct(F, K, n)
            best_sq = [((x + s / 2.0) / K, (y + s / 2.0) / K, 0.0, s / K) for (x, y, s) in cells]
    if best_sq is None:
        k = max(1, math.isqrt(n))
        side = 1.0 / k
        best_sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    best_sq = best_sq[:n]
    clean = []
    for (cx, cy, an, s) in best_sq:
        clean.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), an, min(1.0, max(0.0, s))))
    clean += [(0.5, 0.5, 0.0, 0.0)] * (n - len(clean))
    return clean
# EVOLVE-BLOCK-END
