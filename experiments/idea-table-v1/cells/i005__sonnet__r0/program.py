import math
import time
import numpy as np


def _grid(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq[:n], float(k)


def _dp(n, D):
    F = [[None] * (D + 1) for _ in range(D + 1)]
    C = [[None] * (D + 1) for _ in range(D + 1)]
    for w in range(1, D + 1):
        for h in range(1, D + 1):
            best = np.zeros(n + 1, dtype=np.int64)
            ch = np.zeros((n + 1, 3), dtype=np.int64)
            if n >= 1:
                best[1] = min(w, h)
                ch[1] = (3, 0, 0)
            if n >= 2:
                for typ in (1, 2):
                    if typ == 1:
                        lim = w // 2
                    else:
                        lim = h // 2
                    for c in range(1, lim + 1):
                        if typ == 1:
                            A = F[c][h]
                            B = F[w - c][h]
                        else:
                            A = F[w][c]
                            B = F[w][h - c]
                        for k in range(1, n):
                            cand = A[k] + B[1:n - k + 1]
                            cur = best[k + 1:]
                            mask = cand > cur
                            if mask.any():
                                cur[mask] = cand[mask]
                                sub = ch[k + 1:]
                                sub[mask, 0] = typ
                                sub[mask, 1] = c
                                sub[mask, 2] = k
                for m in range(2, n + 1):
                    if best[m - 1] > best[m]:
                        best[m] = best[m - 1]
                        ch[m] = (0, 0, 0)
            F[w][h] = best
            C[w][h] = ch
    # reconstruct
    out = []
    stack = [(0, 0, D, D, n)]
    while stack:
        x, y, w, h, m = stack.pop()
        if m <= 0:
            continue
        t, c, k = C[w][h][m]
        if t == 3:
            s = min(w, h)
            out.append((x, y, s))
        elif t == 0:
            stack.append((x, y, w, h, m - 1))
        elif t == 1:
            stack.append((x, y, c, h, k))
            stack.append((x + c, y, w - c, h, m - k))
        else:
            stack.append((x, y, w, c, k))
            stack.append((x, y + c, w, h - c, m - k))
    return int(F[D][D][n]), out


def solve(n):
    grid, gval = _grid(n)
    if n > 200 or n < 2:
        return grid
    t0 = time.time()
    budget = 40.0
    best_val = gval
    best_res = None
    last = None
    for D in range(1, 41):
        if last is not None:
            est = last * ((D / (D - 1.0)) ** 3) * 1.3
            if time.time() - t0 + est > budget:
                break
        ts = time.time()
        val, out = _dp(n, D)
        last = time.time() - ts
        v = val / D
        if v > best_val + 1e-12:
            best_val = v
            best_res = (D, out)
    if best_res is None:
        return grid
    D, out = best_res
    res = []
    shrink = 1.0 - 1e-9
    for (x, y, s) in out:
        side = s / D
        cx = (x + s / 2.0) / D
        cy = (y + s / 2.0) / D
        res.append((cx, cy, 0.0, side * shrink))
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res[:n]
