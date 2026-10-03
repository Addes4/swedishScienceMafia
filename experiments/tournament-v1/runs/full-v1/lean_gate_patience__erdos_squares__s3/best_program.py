# EVOLVE-BLOCK-START
"""DP over recursive grid / big-corner-square constructions, plus guillotine rectangle DP."""
import math
import numpy as np


def solve(n):
    M = 8
    C = M * M
    NEG = -1e18
    F = [0.0] * (n + 1)
    ch = [None] * (n + 1)
    H = [[NEG] * (n + 1) for _ in range(C + 1)]
    J = [[0] * (n + 1) for _ in range(C + 1)]
    for c in range(C + 1):
        H[c][0] = 0.0
    for t in range(1, n + 1):
        for c in range(1, C + 1):
            best = NEG
            bj = 0
            Hp = H[c - 1]
            for j in range(0, t):
                v = Hp[t - j]
                if v < -1e17:
                    continue
                v += F[j]
                if v > best:
                    best = v
                    bj = j
            H[c][t] = best
            J[c][t] = bj
        if t == 1:
            F[t] = 1.0
            ch[t] = ('one',)
        else:
            best = F[t - 1]
            bc = ('pad',)
            for k in range(2, M + 1):
                h = H[k * k][t]
                if h > -1e17 and h / k > best + 1e-12:
                    best = h / k
                    bc = ('grid', k)
            for m in range(3, M + 1):
                for a in range(2, m):
                    c = m * m - a * a
                    h = H[c][t - 1]
                    if h < -1e17:
                        continue
                    v = a / m + h / m
                    if v > best + 1e-12:
                        best = v
                        bc = ('big', m, a)
            F[t] = best
            ch[t] = bc
        for c in range(1, C + 1):
            if F[t] > H[c][t]:
                H[c][t] = F[t]
                J[c][t] = t

    out = []

    def distribute(cells, rem):
        counts = [0] * cells
        for c in range(cells, 0, -1):
            j = J[c][rem]
            counts[c - 1] = j
            rem -= j
        return counts

    def emit(t, x, y, s):
        if t <= 0:
            return
        c = ch[t]
        if c[0] == 'one':
            out.append((x + s / 2, y + s / 2, 0.0, s))
        elif c[0] == 'pad':
            emit(t - 1, x, y, s)
        elif c[0] == 'grid':
            k = c[1]
            counts = distribute(k * k, t)
            cs = s / k
            idx = 0
            for i in range(k):
                for j in range(k):
                    emit(counts[idx], x + i * cs, y + j * cs, cs)
                    idx += 1
        else:
            m, a = c[1], c[2]
            cs = s / m
            out.append((x + a * cs / 2, y + a * cs / 2, 0.0, a * cs))
            cells = [(i, j) for i in range(m) for j in range(m) if not (i < a and j < a)]
            counts = distribute(len(cells), t - 1)
            for idx, (i, j) in enumerate(cells):
                emit(counts[idx], x + i * cs, y + j * cs, cs)

    use_rect = False
    if 2 <= n <= 90:
        use_rect = True
        G = 12
        val = {}
        typ = {}   # 0 none,1 one,2 F,3 pad,4 vcut,5 hcut
        cc = {}
        kk = {}
        for w in range(1, G + 1):
            for h in range(1, G + 1):
                res = np.full(n + 1, -1e18)
                ty = np.zeros(n + 1, dtype=int)
                c_ = np.zeros(n + 1, dtype=int)
                k_ = np.zeros(n + 1, dtype=int)
                res[0] = 0.0
                res[1] = min(w, h) / G
                ty[1] = 1
                if w == h:
                    for k in range(1, n + 1):
                        v = (w / G) * F[k]
                        if v > res[k] + 1e-12:
                            res[k] = v
                            ty[k] = 2
                for kind in (4, 5):
                    total = w if kind == 4 else h
                    for c in range(1, total // 2 + 1):
                        if kind == 4:
                            A = val[(c, h)]
                            B = val[(w - c, h)]
                        else:
                            A = val[(w, c)]
                            B = val[(w, total - c)]
                        for k1 in range(0, n + 1):
                            a = A[k1]
                            if a < -1e17:
                                continue
                            cand = a + B[:n + 1 - k1]
                            sl = slice(k1, n + 1)
                            rv = res[sl]
                            mask = (cand > rv + 1e-12) & (B[:n + 1 - k1] > -1e17)
                            if mask.any():
                                rv[mask] = cand[mask]
                                ty[sl][mask] = kind
                                c_[sl][mask] = c
                                k_[sl][mask] = k1
                for k in range(1, n + 1):
                    if res[k - 1] > res[k] + 1e-12:
                        res[k] = res[k - 1]
                        ty[k] = 3
                val[(w, h)] = res
                typ[(w, h)] = ty
                cc[(w, h)] = c_
                kk[(w, h)] = k_

        def emit_rect(w, h, k, x, y):
            if k <= 0:
                return
            t = typ[(w, h)][k]
            if t == 1:
                s = min(w, h) / G
                out.append((x + s / 2, y + s / 2, 0.0, s))
            elif t == 2:
                emit(k, x, y, w / G)
            elif t == 3:
                emit_rect(w, h, k - 1, x, y)
            elif t == 4:
                c = int(cc[(w, h)][k])
                k1 = int(kk[(w, h)][k])
                emit_rect(c, h, k1, x, y)
                emit_rect(w - c, h, k - k1, x + c / G, y)
            elif t == 5:
                c = int(cc[(w, h)][k])
                k1 = int(kk[(w, h)][k])
                emit_rect(w, c, k1, x, y)
                emit_rect(w, h - c, k - k1, x, y + c / G)

        if val[(G, G)][n] > F[n] + 1e-9:
            emit_rect(G, G, n, 0.0, 0.0)
        else:
            emit(n, 0.0, 0.0, 1.0)
    else:
        emit(n, 0.0, 0.0, 1.0)

    res = []
    for (cx, cy, ang, s) in out[:n]:
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), ang, min(1.0, max(0.0, s))))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
