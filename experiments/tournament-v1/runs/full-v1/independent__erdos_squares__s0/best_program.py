import math
import numpy as np


def solve(n):
    if n <= 0:
        return []
    cands = set()
    for j in range(2, 80):
        cands.add(1.0 - 1.0 / j)
        cands.add(1.0 / j)
        cands.add(j / (j + 1.0))
    for i in range(1, 300):
        cands.add(i / 300.0)
    ps = sorted(c for c in cands if 0.0 < c < 1.0)
    info = []
    for p in ps:
        w = 1.0 - p
        c3 = int(math.floor(1.0 / w + 1e-9))
        c2 = int(math.floor(p / w + 1e-9))
        info.append((p, w, c2, c3, c2 + c3))

    F = np.zeros(n + 1)
    choice = [None] * (n + 1)
    if n >= 1:
        F[1] = 1.0
    for m in range(2, n + 1):
        best = F[m - 1]
        ch = None
        n1 = np.arange(0, m)
        Fn = F[:m]
        rem = m - n1
        for (p, w, c2, c3, cap) in info:
            vals = p * Fn + w * np.minimum(rem, cap)
            k = int(np.argmax(vals))
            if vals[k] > best + 1e-12:
                best = vals[k]
                ch = (p, k)
        F[m] = best
        choice[m] = ch

    out = []

    def gen(m, x0, y0, s):
        if m <= 0:
            return
        if m == 1:
            out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
            return
        ch = choice[m]
        if ch is None:
            gen(m - 1, x0, y0, s)
            return
        p, n1 = ch
        w = 1.0 - p
        c3 = int(math.floor(1.0 / w + 1e-9))
        c2 = int(math.floor(p / w + 1e-9))
        t = min(m - n1, c2 + c3)
        gen(n1, x0, y0, s * p)
        a = min(t, c3)
        for i in range(a):
            out.append((x0 + s * (i + 0.5) * w, y0 + s * (p + w / 2), 0.0, s * w))
        b = t - a
        for i in range(b):
            out.append((x0 + s * (p + w / 2), y0 + s * (i + 0.5) * w, 0.0, s * w))

    gen(n, 0.0, 0.0, 1.0)
    res = []
    for (cx, cy, a, s) in out[:n]:
        s2 = s * (1 - 1e-9)
        res.append((min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0), a, max(s2, 0.0)))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
