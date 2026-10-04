import math
import time
import numpy as np


def solve(n):
    t0 = time.time()
    TL = 40.0
    MAXM = 60
    F = {}

    def get(p, q):
        return F[(p, q)] if p >= q else F[(q, p)]

    def getval(p, q):
        return get(p, q)[0]

    M = 0
    stop = False
    for m in range(1, MAXM + 1):
        for b in range(1, m + 1):
            a = m
            L = min(n, a * b) + 1
            val = np.zeros(L)
            typ = np.zeros(L, dtype=np.int8)
            cut = np.zeros(L, dtype=np.int64)
            c1a = np.zeros(L, dtype=np.int64)
            if a == b and L > 1:
                val[1:] = a
                typ[1:] = 1
            cands = []
            for a1 in range(1, a // 2 + 1):
                cands.append((getval(a1, b), getval(a - a1, b), 2, a1))
            for b1 in range(1, b // 2 + 1):
                cands.append((getval(a, b1), getval(a, b - b1), 3, b1))
            for A, B, t, cv in cands:
                la = len(A)
                lb = len(B)
                if la <= lb:
                    for i in range(la):
                        end = min(L, i + lb)
                        k = end - i
                        if k <= 0:
                            break
                        cand = A[i] + B[:k]
                        v = val[i:end]
                        mask = cand > v + 1e-12
                        if mask.any():
                            v[mask] = cand[mask]
                            typ[i:end][mask] = t
                            cut[i:end][mask] = cv
                            c1a[i:end][mask] = i
                else:
                    ar = np.arange(L)
                    for j in range(lb):
                        end = min(L, j + la)
                        k = end - j
                        if k <= 0:
                            break
                        cand = A[:k] + B[j]
                        v = val[j:end]
                        mask = cand > v + 1e-12
                        if mask.any():
                            v[mask] = cand[mask]
                            typ[j:end][mask] = t
                            cut[j:end][mask] = cv
                            c1a[j:end][mask] = ar[:k][mask]
            F[(a, b)] = (val, typ, cut, c1a)
            if time.time() - t0 > TL:
                stop = True
                break
        if stop:
            break
        M = m
    # choose best m
    best = -1.0
    bm = 0
    for m in range(1, M + 1):
        v = F[(m, m)][0]
        c = min(n, m * m)
        s = v[c] / m
        if s > best + 1e-12:
            best = s
            bm = m

    k = math.isqrt(n)
    if bm == 0 or best < k - 1e-12:
        side = 1.0 / k
        sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side * (1 - 1e-9))
              for i in range(k) for j in range(k)]
        sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
        return sq[:n]

    import sys
    sys.setrecursionlimit(10000)

    def gen(a, b, c):
        # actual orientation a x b, returns list (x, y, s)
        if a < b:
            r = gen(b, a, c)
            return [(y, x, s) for (x, y, s) in r]
        val, typ, cut, c1a = F[(a, b)]
        c = min(c, len(val) - 1)
        t = typ[c]
        if t == 0:
            return []
        if t == 1:
            return [(0, 0, a)]
        c1 = int(c1a[c])
        cv = int(cut[c])
        c2 = c - c1
        out = []
        if t == 2:
            for (x, y, s) in gen(cv, b, c1):
                out.append((x, y, s))
            for (x, y, s) in gen(a - cv, b, c2):
                out.append((x + cv, y, s))
        else:
            for (x, y, s) in gen(a, cv, c1):
                out.append((x, y, s))
            for (x, y, s) in gen(a, b - cv, c2):
                out.append((x, y + cv, s))
        return out

    raw = gen(bm, bm, n)
    res = []
    for (x, y, s) in raw:
        if s <= 0:
            continue
        res.append(((x + s / 2.0) / bm, (y + s / 2.0) / bm, 0.0, s / bm * (1 - 1e-9)))
    res = res[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res
