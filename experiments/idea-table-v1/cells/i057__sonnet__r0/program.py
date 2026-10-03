# EVOLVE-BLOCK-START
"""Guillotine DP on integer grids of increasing resolution (single process, time-guarded)."""
import math
import time
import numpy as np


def _dp(m, n, deadline):
    res = {}
    ch = {}
    for w in range(1, m + 1):
        for h in range(1, m + 1):
            if time.time() > deadline:
                return None
            r = np.zeros(n + 1)
            c_ = [None] * (n + 1)
            if w == h:
                r[1:] = w
                for c in range(1, n + 1):
                    c_[c] = ('s',)
            for kind, L in (('v', w), ('h', h)):
                for pos in range(1, L // 2 + 1):
                    if kind == 'v':
                        A = res[(pos, h)]
                        B = res[(w - pos, h)]
                    else:
                        A = res[(w, pos)]
                        B = res[(w, h - pos)]
                    for i in range(0, n + 1):
                        cand = A[i] + B[:n + 1 - i]
                        cur = r[i:]
                        mask = cand > cur + 1e-12
                        if mask.any():
                            idx = np.nonzero(mask)[0]
                            cur[idx] = cand[idx]
                            for j in idx:
                                c_[i + j] = (kind, pos, i)
            res[(w, h)] = r
            ch[(w, h)] = c_
    return res, ch


def _build(m, ch, n):
    out = []
    stack = [(0, 0, m, m, n)]
    while stack:
        x, y, w, h, c = stack.pop()
        t = ch[(w, h)][c]
        if t is None:
            continue
        if t[0] == 's':
            out.append((x, y, w))
        elif t[0] == 'v':
            _, pos, i = t
            stack.append((x, y, pos, h, i))
            stack.append((x + pos, y, w - pos, h, c - i))
        else:
            _, pos, i = t
            stack.append((x, y, w, pos, i))
            stack.append((x, y + pos, w, h - pos, c - i))
    return out


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    budget = 40.0
    deadline = t0 + budget
    k = math.isqrt(n)
    best_val = float(k)
    best = [((i + 0.5) / k, (j + 0.5) / k, 0.0, 1.0 / k) for i in range(k) for j in range(k)]
    last_t = None
    last_m = None
    m = 1
    while m <= 30:
        now = time.time()
        if last_t is not None:
            proj = last_t * (m / last_m) ** 3.2
            if now + proj > deadline:
                break
        if now > deadline:
            break
        ts = time.time()
        r = _dp(m, n, deadline)
        if r is None:
            break
        res, ch = r
        last_t = max(time.time() - ts, 1e-3)
        last_m = m
        val = res[(m, m)][n] / m
        if val > best_val + 1e-12:
            sq = _build(m, ch, n)
            best = [((x + s / 2.0) / m, (y + s / 2.0) / m, 0.0, s / m * (1 - 1e-12))
                    for (x, y, s) in sq]
            best_val = val
        m += 1
    squares = list(best)
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
# EVOLVE-BLOCK-END
