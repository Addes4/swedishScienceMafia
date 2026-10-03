import time
import numpy as np


def _run(G, n):
    NEG = -10**9
    dp = [[None] * (G + 1) for _ in range(G + 1)]
    for w in range(1, G + 1):
        for h in range(1, w + 1):
            res = np.zeros(n + 1, dtype=np.int64)
            res[1:] = min(w, h)
            for i in range(1, w // 2 + 1):
                A = dp[i][h]
                B = dp[w - i][h]
                for m1 in range(1, n):
                    cand = A[m1] + B[:n + 1 - m1]
                    np.maximum(res[m1:], cand, out=res[m1:])
            for j in range(1, h // 2 + 1):
                A = dp[w][j]
                B = dp[w][h - j]
                for m1 in range(1, n):
                    cand = A[m1] + B[:n + 1 - m1]
                    np.maximum(res[m1:], cand, out=res[m1:])
            dp[w][h] = res
            dp[h][w] = res
    return dp


def _build(dp, w, h, m, x, y, out):
    if m <= 0:
        return
    val = dp[w][h][m]
    if val == min(w, h):
        out.append((x + min(w, h) / 2.0, y + min(w, h) / 2.0, min(w, h)))
        return
    for i in range(1, w):
        if i > w - i:
            break
        A = dp[i][h]
        B = dp[w - i][h]
        for m1 in range(0, m + 1):
            if A[m1] + B[m - m1] == val:
                _build(dp, i, h, m1, x, y, out)
                _build(dp, w - i, h, m - m1, x + i, y, out)
                return
    for j in range(1, h):
        if j > h - j:
            break
        A = dp[w][j]
        B = dp[w][h - j]
        for m1 in range(0, m + 1):
            if A[m1] + B[m - m1] == val:
                _build(dp, w, j, m1, x, y, out)
                _build(dp, w, h - j, m - m1, x, y + j, out)
                return
    # fallback (should not happen)
    out.append((x + min(w, h) / 2.0, y + min(w, h) / 2.0, min(w, h)))


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    best_val = -1.0
    best_sq = None
    G = 1
    last = 0.0
    maxG = 40 if n <= 40 else 20
    while G <= maxG:
        ts = time.time()
        if ts - t0 + last * 2.5 > 35:
            break
        dp = _run(G, n)
        val = dp[G][G][n] / G
        if val > best_val + 1e-12:
            out = []
            _build(dp, G, G, n, 0, 0, out)
            best_val = val
            best_sq = [(cx / G, cy / G, s / G) for cx, cy, s in out]
        last = time.time() - ts
        G += 1
    res = []
    for cx, cy, s in best_sq:
        s2 = s * (1 - 1e-9)
        res.append((cx, cy, 0.0, s2))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
