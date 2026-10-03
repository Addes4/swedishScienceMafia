import math
import numpy as np


def solve(n):
    NEG = -1e18
    K = 6
    J = K * K

    def flat(c):
        k = max(1, math.isqrt(c - 1) + 1) if c > 0 else 1
        s = 1.0 / k
        out = []
        for i in range(c):
            out.append(((i % k + 0.5) * s, (i // k + 0.5) * s, 0.0, s))
        return out

    if n > 400:
        sq = flat(n)
        return sq[:n]

    N = n
    f = np.zeros(N + 1)
    desc = [None] * (N + 1)
    h = np.zeros((J + 1, N + 1))
    arg = np.zeros((J + 1, N + 1), dtype=int)

    for c in range(1, N + 1):
        if c == 1:
            f[1] = 1.0
            desc[1] = ('flat',)
        else:
            best = f[c - 1]
            d = ('prev',)
            k0 = math.isqrt(c - 1) + 1
            v = c / k0
            if v > best + 1e-12:
                best = v
                d = ('flat',)
            a_arr = np.arange(1, c)
            for k in range(2, K + 1):
                vals = (f[1:c] + h[k * k - 1][c - 1:0:-1]) / k
                i = int(np.argmax(vals))
                if vals[i] > best + 1e-12:
                    best = float(vals[i])
                    d = ('grid', k, int(a_arr[i]))
                for m in range(2, k):
                    s = k * k - m * m
                    vals = (f[1:c] * m + h[s][c - 1:0:-1]) / k
                    i = int(np.argmax(vals))
                    if vals[i] > best + 1e-12:
                        best = float(vals[i])
                        d = ('merged', k, m, int(a_arr[i]))
            f[c] = best
            desc[c] = d
        for j in range(1, J + 1):
            vals = f[0:c + 1] + h[j - 1][c::-1]
            i = int(np.argmax(vals))
            h[j][c] = vals[i]
            arg[j][c] = i

    def rest(j, c):
        counts = [0] * j
        while j > 0 and c > 0:
            a = int(arg[j][c])
            counts[j - 1] = a
            c -= a
            j -= 1
        return counts

    def place(cnt, x0, y0, size):
        if cnt <= 0:
            return []
        return [(x0 + size * x, y0 + size * y, 0.0, size * s) for (x, y, _, s) in rec(cnt)]

    def rec(c):
        if c <= 0:
            return []
        if c == 1:
            return [(0.5, 0.5, 0.0, 1.0)]
        d = desc[c]
        if d[0] == 'prev':
            return rec(c - 1)
        if d[0] == 'flat':
            return flat(c)
        out = []
        if d[0] == 'grid':
            k, a = d[1], d[2]
            counts = [a] + rest(k * k - 1, c - a)
            s = 1.0 / k
            for idx, cnt in enumerate(counts):
                i, j = idx % k, idx // k
                out += place(cnt, i * s, j * s, s)
            return out
        k, m, b = d[1], d[2], d[3]
        s = 1.0 / k
        sm = k * k - m * m
        counts = rest(sm, c - b)
        out += place(b, 0.0, 0.0, m * s)
        idx = 0
        for j in range(k):
            for i in range(k):
                if i < m and j < m:
                    continue
                out += place(counts[idx], i * s, j * s, s)
                idx += 1
        return out

    sq = rec(N)
    sq = [(min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), 0.0, min(1.0, max(0.0, s)))
          for (x, y, _, s) in sq]
    sq = sq[:n]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq
