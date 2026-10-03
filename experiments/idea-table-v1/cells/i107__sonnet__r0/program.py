import math
import numpy as np


def _plan(n, k1):
    C = k1 * k1
    NEG = -10**9
    f = np.full((C + 1, n + 1), NEG, dtype=np.int64)
    f[0][0] = 0
    ch = np.zeros((C + 1, n + 1), dtype=np.int32)
    jmax = min(k1, math.isqrt(n))
    for c in range(1, C + 1):
        prev = f[c - 1]
        best = prev.copy()
        chc = ch[c]
        for j in range(1, jmax + 1):
            s = j * j
            cand = prev[: n + 1 - s] + j
            seg = best[s:]
            mask = cand > seg
            if mask.any():
                seg[mask] = cand[mask]
                chc[s:][mask] = j
        f[c] = best
    m = int(np.argmax(f[C]))
    val = int(f[C][m])
    js = []
    for c in range(C, 0, -1):
        j = int(ch[c][m])
        js.append(j)
        if j > 0:
            m -= j * j
    return val, js


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    kb = math.isqrt(n)
    best_val = kb / kb  # baseline value = kb * (1/kb) * kb ... sum = kb
    best_val = float(kb)
    best = None  # (k1, js)
    if n <= 400:
        for k1 in range(1, kb + 3):
            val, js = _plan(n, k1)
            v = val / k1
            if v > best_val + 1e-12:
                best_val = v
                best = (k1, js)
    shrink = 1.0 - 1e-12
    squares = []
    if best is None:
        k = kb
        side = 1.0 / k
        for i in range(k):
            for j in range(k):
                squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side * shrink))
    else:
        k1, js = best
        cell = 1.0 / k1
        for idx, j in enumerate(js):
            if j <= 0:
                continue
            r, c = divmod(idx, k1)
            s = cell / j
            for a in range(j):
                for b in range(j):
                    x = c * cell + (a + 0.5) * s
                    y = r * cell + (b + 0.5) * s
                    squares.append((x, y, 0.0, s * shrink))
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
