import time
import numpy as np


def _run(G, n):
    idx = np.arange(n + 1)[:, None] - np.arange(n + 1)[None, :]
    P = np.where((idx < 1) | (np.arange(n + 1)[None, :] < 1), -1e9, 0.0)
    IDX = np.clip(idx, 0, n)
    ar = np.arange(n + 1)
    g = np.zeros((G + 1, G + 1, n + 1))
    kind = np.zeros((G + 1, G + 1, n + 1), dtype=np.int8)
    pos = np.zeros((G + 1, G + 1, n + 1), dtype=np.int32)
    mm = np.zeros((G + 1, G + 1, n + 1), dtype=np.int32)
    for a in range(1, G + 1):
        for b in range(1, G + 1):
            arr = np.full(n + 1, float(min(a, b)))
            arr[0] = 0.0
            k = np.zeros(n + 1, dtype=np.int8)
            p = np.zeros(n + 1, dtype=np.int32)
            q = np.zeros(n + 1, dtype=np.int32)
            for a1 in range(1, a // 2 + 1):
                X = g[a1, b]
                Y = g[a - a1, b]
                C = X[None, :] + Y[IDX] + P
                bm = C.argmax(1)
                v = C[ar, bm]
                upd = v > arr + 1e-12
                if upd.any():
                    arr = np.where(upd, v, arr)
                    k[upd] = 1
                    p[upd] = a1
                    q[upd] = bm[upd]
            for b1 in range(1, b // 2 + 1):
                X = g[a, b1]
                Y = g[a, b - b1]
                C = X[None, :] + Y[IDX] + P
                bm = C.argmax(1)
                v = C[ar, bm]
                upd = v > arr + 1e-12
                if upd.any():
                    arr = np.where(upd, v, arr)
                    k[upd] = 2
                    p[upd] = b1
                    q[upd] = bm[upd]
            g[a, b] = arr
            kind[a, b] = k
            pos[a, b] = p
            mm[a, b] = q
    return g, kind, pos, mm


def _reconstruct(G, n, kind, pos, mm):
    res = []
    stack = [(0, 0, G, G, n)]
    while stack:
        x0, y0, a, b, m = stack.pop()
        if m <= 0:
            continue
        k = kind[a, b, m]
        if k == 0:
            s = min(a, b)
            res.append(((x0 + s / 2.0) / G, (y0 + s / 2.0) / G, 0.0, s / G))
        elif k == 1:
            a1 = int(pos[a, b, m])
            m1 = int(mm[a, b, m])
            stack.append((x0, y0, a1, b, m1))
            stack.append((x0 + a1, y0, a - a1, b, m - m1))
        else:
            b1 = int(pos[a, b, m])
            m1 = int(mm[a, b, m])
            stack.append((x0, y0, a, b1, m1))
            stack.append((x0, y0 + b1, a, b - b1, m - m1))
    return res


def solve(n):
    t0 = time.time()
    budget = 38.0
    best_val = -1.0
    best_sq = None
    prev_t = None
    prevG = None
    G = 1
    while G <= 60:
        if prev_t is not None:
            est = prev_t * (G / prevG) ** 3
            if time.time() - t0 + est > budget:
                break
        ts = time.time()
        g, kind, pos, mm = _run(G, n)
        val = g[G, G, n] / G
        if val > best_val + 1e-12:
            sq = _reconstruct(G, n, kind, pos, mm)
            best_val = val
            best_sq = sq
        prev_t = max(time.time() - ts, 1e-4)
        prevG = G
        G += 1
    out = []
    for (x, y, ang, s) in best_sq:
        s2 = s * (1 - 1e-9)
        out.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), 0.0, s2))
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
