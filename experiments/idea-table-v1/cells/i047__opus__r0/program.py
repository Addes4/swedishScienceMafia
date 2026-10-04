# EVOLVE-BLOCK-START
"""Strip / guillotine column-generation style packing.

Patterns (strips / sub-rectangles of the 1/L grid) are priced by an exact
max-plus dynamic program over (width, height, count); the master problem
"choose strips of total width <= 1 with exactly n squares maximising the
sum of sides" is solved exactly as an integer knapsack inside the same DP
(vertical splits of the unit square).  We try many grid resolutions L and
keep the best packing.
"""
import math
import time
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

NEG = -10 ** 9


def _maxplus(x, y):
    m1, m2 = len(x), len(y)
    if m1 > m2:
        x, y = y, x
        m1, m2 = m2, m1
    pad = np.full(m1 - 1, NEG, dtype=np.int64)
    yp = np.concatenate([pad, y, pad])
    win = sliding_window_view(yp, m1)  # shape (m1+m2-1, m1)
    res = (win + x[::-1][None, :]).max(axis=1)
    np.maximum(res, NEG, out=res)
    return res


def _compute(L, n):
    best = {}

    def get(a, b):
        return best[(a, b)] if a <= b else best[(b, a)]

    for a in range(1, L + 1):
        for b in range(a, L + 1):
            cap = min(n, a * b)
            v = np.full(cap + 1, NEG, dtype=np.int64)
            v[0] = 0
            if a == b and cap >= 1:
                v[1] = a
            for a1 in range(1, a // 2 + 1):
                r = _maxplus(get(a1, b), get(a - a1, b))
                k = min(len(r), cap + 1)
                np.maximum(v[:k], r[:k], out=v[:k])
            for b1 in range(1, b // 2 + 1):
                r = _maxplus(get(a, b1), get(a, b - b1))
                k = min(len(r), cap + 1)
                np.maximum(v[:k], r[:k], out=v[:k])
            best[(a, b)] = v
    return best


def _reconstruct(best, L, c, out):
    def get(a, b):
        return best[(a, b)] if a <= b else best[(b, a)]

    def val(a, b, cc):
        v = get(a, b)
        if cc < 0 or cc >= len(v):
            return NEG
        return int(v[cc])

    stack = [(0, 0, L, L, c)]
    while stack:
        x0, y0, a, b, cc = stack.pop()
        if cc == 0:
            continue
        target = val(a, b, cc)
        if a == b and cc == 1 and target == a:
            out.append((x0, y0, a))
            continue
        done = False
        for a1 in range(1, a // 2 + 1):
            a2 = a - a1
            v1 = get(a1, b)
            v2 = get(a2, b)
            for c1 in range(0, min(cc, len(v1) - 1) + 1):
                c2 = cc - c1
                if c2 >= len(v2):
                    continue
                if int(v1[c1]) + int(v2[c2]) == target and v1[c1] > NEG // 2 and v2[c2] > NEG // 2:
                    stack.append((x0, y0, a1, b, c1))
                    stack.append((x0 + a1, y0, a2, b, c2))
                    done = True
                    break
            if done:
                break
        if done:
            continue
        for b1 in range(1, b // 2 + 1):
            b2 = b - b1
            v1 = get(a, b1)
            v2 = get(a, b2)
            for c1 in range(0, min(cc, len(v1) - 1) + 1):
                c2 = cc - c1
                if c2 >= len(v2):
                    continue
                if int(v1[c1]) + int(v2[c2]) == target and v1[c1] > NEG // 2 and v2[c2] > NEG // 2:
                    stack.append((x0, y0, a, b1, c1))
                    stack.append((x0, y0 + b1, a, b2, c2))
                    done = True
                    break
            if done:
                break
        # if not done (should not happen), drop squares


def solve(n):
    t0 = time.time()
    budget = 35.0
    best_num, best_den = 0, 1
    best_sol = None
    Lmax = 90
    last_t = 0.0
    L = 1
    while L <= Lmax:
        el = time.time() - t0
        if L > 2 and el + last_t * ((L / (L - 1.0)) ** 3) * 1.3 > budget:
            break
        ts = time.time()
        bt = _compute(L, n)
        last_t = time.time() - ts
        v = bt[(L, L)]
        c = int(np.argmax(v))
        num = int(v[c])
        if num * best_den > best_num * L:
            out = []
            _reconstruct(bt, L, c, out)
            if len(out) == c and sum(s for _, _, s in out) == num:
                best_num, best_den = num, L
                best_sol = [((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / float(L))
                            for x, y, s in out]
        L += 1

    if best_sol is None:
        k = max(1, math.isqrt(n))
        side = 1.0 / k
        best_sol = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                    for i in range(k) for j in range(k)]
    sol = []
    for (cx, cy, ang, s) in best_sol[:n]:
        sol.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), ang, min(1.0, max(0.0, s))))
    while len(sol) < n:
        sol.append((0.0, 0.0, 0.0, 0.0))
    return sol
# EVOLVE-BLOCK-END
