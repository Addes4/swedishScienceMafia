# EVOLVE-BLOCK-START
"""Dynamic programming over recursive grid tilings (with an optional merged corner block)."""
import math
import numpy as np

NEG = -1e18


def _build(n, KMAX=9):
    best = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    for m in range(1, n + 1):
        best[m] = 1.0
        choice[m] = ('sq',)
        if m >= 2 and best[m - 1] > best[m]:
            best[m] = best[m - 1]
            choice[m] = ('prev',)
        if m == 1:
            continue
        ts = np.arange(m + 1)[:, None]
        js = np.arange(m)[None, :]
        idx = ts - js
        mask = idx < 0
        idx = np.where(mask, 0, idx)
        for k in range(2, KMAX + 1):
            v = np.array(best[:m]) / k
            h = [np.zeros(m + 1)]
            args = [None]
            for c in range(1, k * k + 1):
                prev = h[-1]
                M = prev[idx] + v[None, :]
                M = np.where(mask, NEG, M)
                a = np.argmax(M, axis=1)
                new = M[np.arange(m + 1), a]
                h.append(new)
                args.append(a)
            val = h[k * k][m]
            if val > best[m] + 1e-12:
                best[m] = float(val)
                choice[m] = ('grid', k, 0, 0, args)
            for j in range(2, k):
                R = k * k - j * j
                for m1 in range(1, m):
                    val = (j / k) * best[m1] + h[R][m - m1]
                    if val > best[m] + 1e-12:
                        best[m] = float(val)
                        choice[m] = ('grid', k, j, m1, args)
    return best, choice


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    best, choice = _build(n)
    out = []

    def emit(x0, y0, s, m):
        if m <= 0:
            return
        ch = choice[m]
        while ch[0] == 'prev':
            m -= 1
            ch = choice[m]
        if ch[0] == 'sq':
            out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
            return
        _, k, j, m1, args = ch
        cs = s / k
        cells = [(r, c) for r in range(k) for c in range(k)
                 if not (r < j and c < j)]
        R = len(cells)
        t = m - m1 if j > 0 else m
        alloc = [0] * R
        c = R
        while c > 0:
            jj = int(args[c][t])
            alloc[c - 1] = jj
            t -= jj
            c -= 1
        if j > 0:
            emit(x0, y0, j * cs, m1)
        for (r, cc), a in zip(cells, alloc):
            if a > 0:
                emit(x0 + cc * cs, y0 + r * cs, cs, a)

    emit(0.0, 0.0, 1.0, n)
    res = []
    for (x, y, a, s) in out:
        s = min(max(s, 0.0), 1.0)
        x = min(max(x, 0.0), 1.0)
        y = min(max(y, 0.0), 1.0)
        res.append((x, y, a, s))
    res = res[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res
# EVOLVE-BLOCK-END
