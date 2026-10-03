import math
import time
import numpy as np


def _plan(m, n):
    K = n
    F = {}
    CH = {}
    for w in range(1, m + 1):
        for h in range(w, m + 1):
            best = np.zeros(K + 1)
            ch = [None] * (K + 1)
            if w == h:
                for k in range(1, K + 1):
                    best[k] = w
                    ch[k] = ('L',)
            # cuts
            for typ in (0, 1):
                L = w if typ == 0 else h
                for c in range(1, L // 2 + 1):
                    if typ == 0:
                        a = _get(F, c, h)
                        b = _get(F, w - c, h)
                    else:
                        a = _get(F, w, c)
                        b = _get(F, w, h - c)
                    for k1 in range(0, K + 1):
                        cand = a[k1] + b[:K + 1 - k1]
                        tgt = best[k1:]
                        mask = cand > tgt + 1e-12
                        if mask.any():
                            idx = np.nonzero(mask)[0]
                            tgt[idx] = cand[idx]
                            for i in idx:
                                kk = int(i) + k1
                                ch[kk] = (typ, c, k1)
            # at-most monotone
            for k in range(1, K + 1):
                if best[k] < best[k - 1] - 1e-12:
                    best[k] = best[k - 1]
                    ch[k] = ('P',)
            F[(w, h)] = best
            CH[(w, h)] = ch
    return F, CH


def _get(F, w, h):
    if w > h:
        w, h = h, w
    return F[(w, h)]


def _build(F, CH, w, h, k, x, y, m, out, flip=False):
    # rectangle w x h (actual orientation), offset (x,y); stored with w<=h
    if k <= 0:
        return
    sw, sh = (w, h) if w <= h else (h, w)
    ch = CH[(sw, sh)][k]
    if ch is None:
        return
    if ch[0] == 'P':
        _build(F, CH, w, h, k - 1, x, y, m, out)
        return
    if ch[0] == 'L':
        out.append(((x + w / 2.0) / m, (y + h / 2.0) / m, 0.0, w / m))
        return
    typ, c, k1 = ch
    # the stored cut is relative to stored orientation (sw x sh)
    swapped = w > h
    t = typ
    if swapped:
        t = 1 - typ
    # t==0: cut along width (actual w), t==1: along height
    if t == 0:
        _build(F, CH, c, h, k1, x, y, m, out)
        _build(F, CH, w - c, h, k - k1, x + c, y, m, out)
    else:
        _build(F, CH, w, c, k1, x, y, m, out)
        _build(F, CH, w, h - c, k - k1, x, y + c, m, out)


def solve(n):
    t0 = time.time()
    base = max(1, math.isqrt(n))
    best_val = -1.0
    best_sq = None
    for m in range(base, base + 5):
        if m > base and time.time() - t0 > 25:
            break
        F, CH = _plan(m, n)
        val = F[(m, m)][n]
        if val / m > best_val + 1e-12:
            out = []
            _build(F, CH, m, m, n, 0, 0, m, out)
            if len(out) <= n:
                best_val = val / m
                best_sq = out
    if best_sq is None:
        k = base
        s = 1.0 / k
        best_sq = [((i + 0.5) * s, (j + 0.5) * s, 0.0, s) for i in range(k) for j in range(k)]
    res = list(best_sq)[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res
