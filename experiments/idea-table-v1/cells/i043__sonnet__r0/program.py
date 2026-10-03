# EVOLVE-BLOCK-START
"""Guillotine DP over integer rectangles plus top-level pinwheel decomposition."""
import math
import time
import numpy as np

NEG = -1e18


def _conv(A, B, n):
    res = np.full(n + 1, NEG)
    arg = np.zeros(n + 1, dtype=np.int64)
    for i in range(n + 1):
        cand = A[i] + B[:n + 1 - i]
        sl = res[i:]
        mask = cand > sl + 1e-12
        sl[mask] = cand[mask]
        arg[i:][mask] = i
    return res, arg


def _build(D, n):
    F = {}
    dec = {}
    for a in range(1, D + 1):
        for b in range(1, D + 1):
            best = np.full(n + 1, NEG)
            best[0] = 0.0
            d = [None] * (n + 1)
            d[0] = ('z',)
            cur = np.zeros(n + 1)
            cur_dec = [('z',)] * (n + 1)
            s = min(a, b)
            for m in range(1, n + 1):
                cur[m] = float(s)
                cur_dec[m] = ('sq',)
            for c in range(1, a // 2 + 1):
                res, arg = _conv(F[(c, b)], F[(a - c, b)], n)
                for m in range(1, n + 1):
                    if res[m] > cur[m] + 1e-12:
                        cur[m] = res[m]
                        cur_dec[m] = ('v', c, int(arg[m]))
            for c in range(1, b // 2 + 1):
                res, arg = _conv(F[(a, c)], F[(a, b - c)], n)
                for m in range(1, n + 1):
                    if res[m] > cur[m] + 1e-12:
                        cur[m] = res[m]
                        cur_dec[m] = ('h', c, int(arg[m]))
            for m in range(1, n + 1):
                if cur[m - 1] >= cur[m]:
                    cur[m] = cur[m - 1]
                    cur_dec[m] = ('less',)
            F[(a, b)] = cur
            dec[(a, b)] = cur_dec
    return F, dec


def _place(dec, a, b, m, x0, y0, out):
    while m > 0:
        d = dec[(a, b)][m]
        if d[0] == 'z':
            return
        if d[0] == 'less':
            m -= 1
            continue
        if d[0] == 'sq':
            s = min(a, b)
            out.append((x0 + s / 2.0, y0 + s / 2.0, s))
            return
        if d[0] == 'v':
            c, i = d[1], d[2]
            _place(dec, c, b, i, x0, y0, out)
            _place(dec, a - c, b, m - i, x0 + c, y0, out)
            return
        c, i = d[1], d[2]
        _place(dec, a, c, i, x0, y0, out)
        _place(dec, a, b - c, m - i, x0, y0 + c, out)
        return


def _pin_rects(D, a, b, c, d):
    # (x0, y0, w, h)
    return [(0, 0, a, c), (a, 0, D - a, d), (b, d, D - b, D - d),
            (0, c, b, D - c), (b, c, a - b, d - c)]


def _pin_val(F, D, n, p, deadline_check=None):
    a, b, c, d = p
    rs = _pin_rects(D, a, b, c, d)
    Fs = [F[(r[2], r[3])] for r in rs]
    P, _ = _conv(Fs[0], Fs[1], n)
    P, _ = _conv(P, Fs[2], n)
    P, _ = _conv(P, Fs[3], n)
    return float(np.max(P + Fs[4][::-1]))


def _pin_build(F, dec, D, n, p):
    a, b, c, d = p
    rs = _pin_rects(D, a, b, c, d)
    Fs = [F[(r[2], r[3])] for r in rs]
    P1, g1 = _conv(Fs[0], Fs[1], n)
    P2, g2 = _conv(P1, Fs[2], n)
    P3, g3 = _conv(P2, Fs[3], n)
    tot = P3 + Fs[4][::-1]
    m3 = int(np.argmax(tot))
    m5 = n - m3
    m4 = int(g3[m3]); m3b = m3 - m4
    m3c = int(g2[m3b]); m3d = m3b - m3c
    m1 = int(g1[m3d]); m2 = m3d - m1
    counts = [m1, m2, m3c, m4, m5]
    out = []
    for r, cnt in zip(rs, counts):
        _place(dec, r[2], r[3], cnt, r[0], r[1], out)
    return out


def solve(n):
    t0 = time.time()
    budget = 45.0
    best_val = -1.0
    best_sq = None
    Ds = [12, 10, 8, 9, 7, 6, 11, 5, 14, 15, 16]
    for D in Ds:
        if time.time() - t0 > budget * 0.5 and best_sq is not None:
            break
        F, dec = _build(D, n)
        val = F[(D, D)][n] / D
        out = []
        _place(dec, D, D, n, 0, 0, out)
        if val > best_val + 1e-12:
            best_val = val
            best_sq = [(x / D, y / D, 0.0, s / D) for x, y, s in out]
        # pinwheel search
        if D <= 12:
            bp = None
            bv = F[(D, D)][n]
            stop = False
            for a in range(2, D):
                for b in range(1, a):
                    for c in range(1, D - 1):
                        for d in range(c + 1, D):
                            v = _pin_val(F, D, n, (a, b, c, d))
                            if v > bv + 1e-9:
                                bv = v
                                bp = (a, b, c, d)
                    if time.time() - t0 > budget:
                        stop = True
                        break
                if stop:
                    break
            if bp is not None and bv / D > best_val + 1e-12:
                out = _pin_build(F, dec, D, n, bp)
                best_val = bv / D
                best_sq = [(x / D, y / D, 0.0, s / D) for x, y, s in out]
            if stop:
                break
    res = list(best_sq)[:n]
    res = [(min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), 0.0, min(1.0, max(0.0, s)))
           for x, y, _, s in res]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
