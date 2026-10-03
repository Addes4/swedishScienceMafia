import time
import sys
from fractions import Fraction
import numpy as np

# EVOLVE-BLOCK-START


class _Timeout(Exception):
    pass


def _build(n, Q, deadline):
    memo = {}
    inprog = set()
    zeros = np.zeros(n + 1)

    def cands(r):
        S = set()
        for q in range(1, Q + 1):
            for p in range(1, q + 1):
                s = Fraction(p, q)
                if s <= 1:
                    S.add(s)
                s2 = r - s
                if 0 < s2 <= 1:
                    S.add(s2)
        if r <= 1:
            S.add(r)
        return sorted(S)

    def val(w, h):
        if w <= 0 or h <= 0:
            return zeros
        if w >= h:
            sh, lo = h, w
        else:
            sh, lo = w, h
        return G(lo / sh)[0] * float(sh)

    def G(r):
        if r in memo:
            return memo[r]
        if r in inprog:
            return (zeros, [None] * (n + 1))
        if time.time() > deadline:
            raise _Timeout()
        inprog.add(r)
        best = np.zeros(n + 1)
        choice = [None] * (n + 1)
        for s in cands(r):
            fs = float(s)
            for orient in (0, 1):
                if orient == 0:
                    A = val(r - s, Fraction(1))
                    B = val(s, 1 - s)
                else:
                    A = val(r, 1 - s)
                    B = val(r - s, s)
                C = np.empty(n)
                I = np.empty(n, dtype=int)
                for k in range(n):
                    v = A[:k + 1] + B[k::-1]
                    i = int(np.argmax(v))
                    C[k] = v[i]
                    I[k] = i
                for m in range(1, n + 1):
                    c = fs + C[m - 1]
                    if c > best[m] + 1e-12:
                        best[m] = c
                        choice[m] = (s, orient, int(I[m - 1]))
        for m in range(1, n + 1):
            if best[m - 1] > best[m] + 1e-12:
                best[m] = best[m - 1]
                choice[m] = None
        inprog.discard(r)
        memo[r] = (best, choice)
        return memo[r]

    top = G(Fraction(1))
    return top[0][n], memo


def _place(memo, x, y, w, h, m, out):
    if m <= 0:
        return
    if w <= 0 or h <= 0:
        out.extend([(x, y, Fraction(0))] * m)
        return
    if w < h:
        sub = []
        _place(memo, y, x, h, w, m, sub)
        out.extend((b, a, s) for (a, b, s) in sub)
        return
    r = w / h
    if r not in memo:
        out.extend([(x, y, Fraction(0))] * m)
        return
    arr, choice = memo[r]
    while m > 0 and choice[m] is None:
        out.append((x, y, Fraction(0)))
        m -= 1
    if m <= 0:
        return
    s, orient, m1 = choice[m]
    sc = s * h
    out.append((x + sc / 2, y + sc / 2, sc))
    m2 = m - 1 - m1
    if orient == 0:
        _place(memo, x + sc, y, w - sc, h, m1, out)
        _place(memo, x, y + sc, sc, h - sc, m2, out)
    else:
        _place(memo, x, y + sc, w, h - sc, m1, out)
        _place(memo, x + sc, y, w - sc, sc, m2, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    sys.setrecursionlimit(100000)
    t0 = time.time()
    budget = 40.0
    best_val = -1.0
    best_memo = None
    Q = 1
    last_dt = 0.0
    while Q <= 40:
        ts = time.time()
        if best_memo is not None and (ts - t0) + last_dt * 4 > budget:
            break
        try:
            v, memo = _build(n, Q, t0 + budget)
        except _Timeout:
            break
        last_dt = time.time() - ts
        if v > best_val + 1e-12:
            best_val, best_memo = v, memo
        Q += 1
    out = []
    if best_memo is not None:
        _place(best_memo, Fraction(0), Fraction(0), Fraction(1), Fraction(1), n, out)
    res = []
    for (cx, cy, s) in out:
        sd = float(s) * (1 - 1e-9)
        res.append((min(1.0, max(0.0, float(cx))), min(1.0, max(0.0, float(cy))), 0.0, max(0.0, sd)))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
