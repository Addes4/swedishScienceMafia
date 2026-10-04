# EVOLVE-BLOCK-START
import math
import numpy as np


def _rect_table(w, h, N):
    g = np.zeros(N + 1)
    ch = [None] * (N + 1)
    for m in range(1, N + 1):
        c = np.arange(1, m + 1)
        r = (m + c - 1) // c
        s = np.minimum(w / c, h / r)
        v = m * s
        i = int(np.argmax(v))
        if v[i] <= g[m - 1] and m > 1:
            g[m] = g[m - 1]
            ch[m] = ch[m - 1]
        else:
            g[m] = v[i]
            ch[m] = (int(c[i]), int(r[i]), m)
    return g, ch


def _place_rect(ch, x0, y0, w, h, out):
    if ch is None:
        return
    c, r, used = ch
    cw = w / c
    chh = h / r
    s = min(cw, chh)
    for i in range(used):
        col = i % c
        row = i // c
        out.append((x0 + (col + 0.5) * cw, y0 + (row + 0.5) * chh, 0.0, s))


def solve(n):
    N = n
    qmax = int(2 * math.sqrt(n) + 2)
    if n > 200:
        qmax = min(qmax, 12)
    ts = sorted(set(p / q for q in range(2, qmax + 1) for p in range(1, q)))
    # dedupe floats
    uniq = []
    for t in ts:
        if not uniq or abs(t - uniq[-1]) > 1e-12:
            uniq.append(t)
    ts = uniq
    T = len(ts)

    tabs = []
    H = np.zeros((T, N + 1))
    for ti, t in enumerate(ts):
        gA, chA = _rect_table(1 - t, 1.0, N)
        gB, chB = _rect_table(t, 1 - t, N)
        tabs.append((gA, chA, gB, chB))
        h = np.zeros(N + 1)
        for m in range(1, N + 1):
            h[m] = np.max(gA[:m + 1] + gB[m::-1][:m + 1])
        H[ti] = h

    tarr = np.array(ts)
    g1, ch1 = _rect_table(1.0, 1.0, N)
    F = g1.copy()
    Fch = [None] * (N + 1)
    for m in range(1, N + 1):
        Fch[m] = ('grid', ch1[m])
    for m in range(2, N + 1):
        best = F[m]
        bc = None
        if m - 1 >= 1:
            vals = tarr[:, None] * F[1:m][None, :] + H[:, m - 1:0:-1]
            idx = int(np.argmax(vals))
            ti, j = divmod(idx, m - 1)
            v = vals[ti, j]
            if v > best + 1e-12:
                best = v
                bc = (ti, j + 1)
        if bc is not None:
            F[m] = best
            Fch[m] = ('split', bc[0], bc[1])
        if F[m] < F[m - 1]:
            F[m] = F[m - 1]
            Fch[m] = Fch[m - 1]

    out = []

    def build(m, x0, y0, S):
        if m <= 0:
            return
        ch = Fch[m]
        if ch[0] == 'grid':
            c, r, used = ch[1]
            cw = S / c
            chh = S / r
            s = min(cw, chh)
            for i in range(used):
                col = i % c
                row = i // c
                out.append((x0 + (col + 0.5) * cw, y0 + (row + 0.5) * chh, 0.0, s))
            return
        _, ti, n1 = ch
        t = ts[ti]
        gA, chA, gB, chB = tabs[ti]
        rem = m - n1
        k = int(np.argmax(gA[:rem + 1] + gB[rem::-1][:rem + 1]))
        n2, n3 = k, rem - k
        # square of side t in the corner
        build(n1, x0, y0, S * t)
        _place_rect(chA[n2], x0 + S * t, y0, S * (1 - t), S, out) if n2 > 0 else None
        _place_rect(chB[n3], x0, y0 + S * t, S * t, S * (1 - t), out) if n3 > 0 else None

    build(n, 0.0, 0.0, 1.0)

    res = []
    for (x, y, a, s) in out:
        s2 = max(0.0, s * (1 - 1e-9))
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), 0.0, min(1.0, s2)))
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
