# EVOLVE-BLOCK-START
"""Egyptian-row / guillotine family.

Rows of c_i squares of side 1/c_i (each full row contributes 1) with the
leftover strip filled by the transposed construction are all guillotine
packings on an integer grid of size lcm(c_i).  We therefore run an exact
guillotine DP on integer rectangles (which contains every such recursive
Egyptian-row/column construction, plus merged-cell variants), together with
an explicit Egyptian-fraction enumeration, and keep the best.
"""
import math
import time
from fractions import Fraction
import numpy as np


def _egyptian_candidates(n, t_end):
    """Explicit Egyptian rows + transposed leftover strip (2 levels)."""
    best_val = Fraction(0)
    best_sq = []
    cmax = min(n, 40)
    seqs = []

    def rec(start, seq, tot, cnt):
        if time.time() > t_end or len(seqs) > 20000:
            return
        if seq:
            seqs.append((tuple(seq), tot, cnt))
        if len(seq) >= 5:
            return
        for c in range(start, cmax + 1):
            if cnt + c > n:
                break
            nt = tot + Fraction(1, c)
            if nt > 1:
                continue
            seq.append(c)
            rec(c, seq, nt, cnt + c)
            seq.pop()

    rec(1, [], Fraction(0), 0)
    for seq, tot, cnt in seqs:
        h = 1 - tot
        rem = n - cnt
        val = Fraction(len(seq))
        extra = []
        if h > 0 and rem > 0:
            # transposed level: columns of d squares of side h/d in strip 1 x h
            bestx = (Fraction(0), [])
            for d in range(1, rem + 1):
                s = h / d
                ncol = min(int(1 / s), rem // d)
                if ncol <= 0:
                    continue
                v = ncol * h
                used_w = ncol * s
                left_cnt = rem - ncol * d
                sq = [(j, i, d) for j in range(ncol) for i in range(d)]
                # second-level leftover: rectangle (1-used_w) x h -> squares of side (1-used_w)? use side min
                w2 = 1 - used_w
                add2 = []
                if w2 > 0 and left_cnt > 0:
                    s2 = min(w2, h)
                    k2 = min(left_cnt, int(max(w2, h) / s2))
                    add2 = [(s2, q) for q in range(k2)]
                    v += k2 * s2
                if v > bestx[0]:
                    bestx = (v, (s, ncol, d, w2, add2, used_w))
            if bestx[1]:
                val += bestx[0]
                extra = bestx[1]
        if val > best_val:
            best_val = val
            sqs = []
            y = Fraction(0)
            for c in seq:
                s = Fraction(1, c)
                for j in range(c):
                    sqs.append((float(j * s + s / 2), float(y + s / 2), float(s)))
                y += s
            if extra:
                s, ncol, d, w2, add2, used_w = extra
                for j in range(ncol):
                    for i in range(d):
                        sqs.append((float(j * s + s / 2), float(y + i * s + s / 2), float(s)))
                for s2, q in add2:
                    if w2 >= h:
                        sqs.append((float(used_w + q * s2 + s2 / 2), float(y + s2 / 2), float(s2)))
                    else:
                        sqs.append((float(used_w + s2 / 2), float(y + q * s2 + s2 / 2), float(s2)))
            best_sq = sqs
    return float(best_val), best_sq


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    N = n + 1
    F = {}

    def get(a, b):
        return F[(a, b)] if a <= b else F[(b, a)]

    def conv(x, y):
        res = np.full(N, -1, dtype=np.int64)
        prev = -1
        for i in range(N):
            if x[i] == prev:
                continue
            prev = x[i]
            np.maximum(res[i:], x[i] + y[:N - i], out=res[i:])
        return res

    best_val = -1.0
    best_L = None
    L = 0
    Lcap = 60
    while L < Lcap:
        if time.time() - t0 > 30.0:
            break
        L += 1
        for a in range(1, L + 1):
            b = L
            if a == b:
                f = np.full(N, a, dtype=np.int64)
                f[0] = 0
            else:
                f = np.zeros(N, dtype=np.int64)
            for b1 in range(1, b // 2 + 1):
                np.maximum(f, conv(get(a, b1), get(a, b - b1)), out=f)
            for a1 in range(1, a // 2 + 1):
                np.maximum(f, conv(get(a1, b), get(a - a1, b)), out=f)
            F[(a, b)] = f
        v = F[(L, L)][n] / L
        if v > best_val + 1e-12:
            best_val = v
            best_L = L

    out = []

    def rec(x0, y0, a, b, m, val):
        if val == 0:
            return
        if a == b and val == a and m >= 1:
            out.append((x0 + a / 2.0, y0 + b / 2.0, a))
            return
        for b1 in range(1, b // 2 + 1):
            p, q = get(a, b1), get(a, b - b1)
            for i in range(m + 1):
                if p[i] + q[m - i] == val:
                    rec(x0, y0, a, b1, i, int(p[i]))
                    rec(x0, y0 + b1, a, b - b1, m - i, int(q[m - i]))
                    return
        for a1 in range(1, a // 2 + 1):
            p, q = get(a1, b), get(a - a1, b)
            for i in range(m + 1):
                if p[i] + q[m - i] == val:
                    rec(x0, y0, a1, b, i, int(p[i]))
                    rec(x0 + a1, y0, a - a1, b, m - i, int(q[m - i]))
                    return
        raise RuntimeError("reconstruction failed")

    squares = []
    if best_L is not None:
        Lb = best_L
        rec(0, 0, Lb, Lb, n, int(F[(Lb, Lb)][n]))
        squares = [(cx / Lb, cy / Lb, s / Lb) for cx, cy, s in out]

    try:
        ev, esq = _egyptian_candidates(n, time.time() + 10.0)
        if ev > best_val + 1e-12 and len(esq) <= n:
            squares = esq
            best_val = ev
    except Exception:
        pass

    squares.sort(key=lambda t: -t[2])
    squares = squares[:n]
    res = [(min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, min(1.0, max(0.0, s)))
           for cx, cy, s in squares]
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
