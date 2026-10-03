# EVOLVE-BLOCK-START
import math
import time
import numpy as np


def _bound(n):
    b = math.sqrt(n)
    k = math.isqrt(n)
    if k * k == n:
        b = min(b, k)
    elif n == k * k + 1 and k <= 13:
        b = min(b, k)
    return b


def _fallback(n):
    best = (0.0, 1, 0)
    m = 1
    while m * m <= n + 4 * m * m and m <= 4 * math.isqrt(n) + 4:
        for j in range(0, m):
            cnt = 1 + m * m - j * j if j > 0 else m * m
            if cnt <= n:
                v = (j + (m * m - j * j)) / m if j > 0 else m * m / m
                if v > best[0] + 1e-12:
                    best = (v, m, j)
        m += 1
    v, m, j = best
    s = 1.0 / m
    sq = []
    if j > 0:
        sq.append((j * s / 2, j * s / 2, 0.0, j * s))
    for a in range(m):
        for b in range(m):
            if j > 0 and a < j and b < j:
                continue
            sq.append(((a + 0.5) * s, (b + 0.5) * s, 0.0, s))
    sq = sq[:n]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    if n > 80:
        return _fallback(n)
    C = n
    NEG = -1e18
    ar = np.arange(C + 1)
    D = ar[:, None] - ar[None, :]
    mask = D < 0
    Dc = np.where(mask, 0, D)
    rows = ar

    tab = {}  # (w,h) w<=h -> (val, kind, pos, a)

    def key(w, h):
        return (w, h) if w <= h else (h, w)

    def combine(A, B):
        M = A[None, :] + B[Dc]
        M[mask] = NEG
        arg = M.argmax(1)
        return M[rows, arg], arg

    def compute(w, h):
        val = np.zeros(C + 1)
        kind = -np.ones(C + 1, dtype=int)
        pos = np.zeros(C + 1, dtype=int)
        aa = np.zeros(C + 1, dtype=int)
        if w == h:
            val[1:] = w
            kind[1:] = 0
        for y in range(1, h // 2 + 1):
            A = tab[key(w, y)][0]
            B = tab[key(w, h - y)][0]
            best, arg = combine(A, B)
            upd = best > val + 1e-9
            val = np.where(upd, best, val)
            kind[upd] = 1
            pos[upd] = y
            aa[upd] = arg[upd]
        for x in range(1, w // 2 + 1):
            A = tab[key(x, h)][0]
            B = tab[key(w - x, h)][0]
            best, arg = combine(A, B)
            upd = best > val + 1e-9
            val = np.where(upd, best, val)
            kind[upd] = 2
            pos[upd] = x
            aa[upd] = arg[upd]
        tab[(w, h)] = (val, kind, pos, aa)

    bound = _bound(n)
    bestv, bestm = -1.0, 1
    M = 1
    while M <= 24:
        timeout = False
        for w in range(1, M + 1):
            compute(w, M)
            if time.time() - t0 > 40:
                timeout = True
                break
        if timeout:
            break
        v = tab[(M, M)][0][n] / M
        if v > bestv + 1e-12:
            bestv, bestm = v, M
        if bestv >= bound - 1e-9:
            break
        M += 1

    m = bestm
    out = []

    def place(w, h, c, x0, y0):
        if c <= 0:
            return
        val, kind, pos, aa = tab[key(w, h)]
        k = kind[c]
        if k < 0:
            return
        if k == 0:
            out.append(((x0 + w / 2) / m, (y0 + h / 2) / m, 0.0, w / m))
            return
        a = int(aa[c])
        p = int(pos[c])
        if k == 1:
            place(w, p, a, x0, y0)
            place(w, h - p, c - a, x0, y0 + p)
        else:
            place(p, h, a, x0, y0)
            place(w - p, h, c - a, x0 + p, y0)

    place(m, m, n, 0, 0)
    out = [(min(1.0, max(0.0, a)), min(1.0, max(0.0, b)), 0.0, min(1.0, s)) for a, b, _, s in out]
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END
