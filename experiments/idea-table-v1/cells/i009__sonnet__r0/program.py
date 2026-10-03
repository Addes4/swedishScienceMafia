import math
import numpy as np


def solve(n):
    K = min(math.isqrt(n) + 3, 14)
    C = K * K
    F = np.zeros(n + 1)
    fch = [None] * (n + 1)
    G = np.zeros((C + 1, n + 1))
    ch = np.zeros((C + 1, n + 1), dtype=np.int64)

    def column(m, Fm):
        for c in range(1, C + 1):
            prev = G[c - 1]
            best = prev[m]
            bj = 0
            if Fm > best:
                best = Fm
                bj = m
            if m >= 2:
                vals = prev[m - 1:0:-1] + F[1:m]
                i = int(np.argmax(vals))
                if vals[i] > best:
                    best = vals[i]
                    bj = i + 1
            G[c][m] = best
            ch[c][m] = bj

    for m in range(1, n + 1):
        if m == 1:
            F[1] = 1.0
            fch[1] = None
            column(1, 1.0)
            continue
        column(m, -1e18)  # temporary, without j=m
        best = 1.0
        bc = None
        for k in range(2, K + 1):
            v = G[k * k][m] / k
            if v > best + 1e-12:
                best = v
                bc = (k, 0, 0)
            for a in range(1, k):
                c = k * k - a * a
                vals = (a / k) * F[1:m] + G[c][m - 1:0:-1] / k
                i = int(np.argmax(vals))
                if vals[i] > best + 1e-12:
                    best = vals[i]
                    bc = (k, a, i + 1)
        F[m] = best
        fch[m] = bc
        column(m, best)

    out = []

    def emit(m, x, y, s):
        if m <= 0:
            return
        d = fch[m]
        if d is None:
            out.append((x + s / 2, y + s / 2, 0.0, s))
            return
        k, a, m0 = d
        cell = s / k
        if a > 0:
            emit(m0, x, y, a * cell)
            c = k * k - a * a
            mm = m - m0
        else:
            c = k * k
            mm = m
        bud = [0] * (c + 1)
        cc = c
        while cc > 0 and mm > 0:
            j = int(ch[cc][mm])
            bud[cc] = j
            mm -= j
            cc -= 1
        cells = []
        for i in range(k):
            for j in range(k):
                if i < a and j < a:
                    continue
                cells.append((i, j))
        for idx, (i, j) in enumerate(cells, start=1):
            if bud[idx] > 0:
                emit(bud[idx], x + i * cell, y + j * cell, cell)

    emit(n, 0.0, 0.0, 1.0)
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
