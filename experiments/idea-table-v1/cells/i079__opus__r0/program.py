# EVOLVE-BLOCK-START
"""Recursive grid / L-strip construction (exact fractions) followed by an
exact-integer hill-climb ("seam slide" moves with split/merge repair) on an
L x L board."""
import math
import random
import time
from fractions import Fraction

import numpy as np


def _dp(n):
    kmax = math.isqrt(n) + 1
    C = min(kmax * kmax, 400)
    NEG = -1e18
    H = np.full((C + 1, n + 1), NEG)
    H[:, 0] = 0.0
    Hpre = H.copy()
    f = np.zeros(n + 1)
    plan = [None] * (n + 1)
    plan[0] = ('empty',)
    for m in range(1, n + 1):
        fm = f[0:m]
        for c in range(1, C + 1):
            H[c, m] = np.max(H[c - 1, m:0:-1] + fm)
        Hpre[:, m] = H[:, m]
        best = 1.0
        p = ('one',)
        if m >= 2 and f[m - 1] > best + 1e-12:
            best = f[m - 1]
            p = ('drop',)
        k = 2
        while k * k <= C:
            v = H[k * k, m] / k
            if v > best + 1e-12:
                best = v
                p = ('grid', k)
            k += 1
        k = 2
        while 2 * k - 1 <= m:
            v = (2 * k - 1) / k + (k - 1) / k * f[m - 2 * k + 1]
            if v > best + 1e-12:
                best = v
                p = ('strip', k)
            k += 1
        f[m] = best
        plan[m] = p
        H[1:, m] = np.maximum(H[1:, m], best)
    return f, H, Hpre, plan


def _grid_cells(m, k, f, H, Hpre):
    rem = m
    cells = []
    for c in range(k * k, 0, -1):
        row = Hpre if rem == m else H
        bj, bv = 0, -1e30
        for j in range(0, min(rem, m - 1) + 1):
            v = row[c - 1][rem - j] + f[j]
            if v > bv + 1e-12:
                bv, bj = v, j
        cells.append(bj)
        rem -= bj
    return cells


def _build(m, x0, y0, size, out, f, H, Hpre, plan):
    p = plan[m]
    if p[0] == 'empty' or m == 0:
        return
    if p[0] == 'one':
        out.append((x0, y0, size))
    elif p[0] == 'drop':
        _build(m - 1, x0, y0, size, out, f, H, Hpre, plan)
    elif p[0] == 'grid':
        k = p[1]
        cells = _grid_cells(m, k, f, H, Hpre)
        cs = size / k
        for idx, j in enumerate(cells):
            if j > 0:
                _build(j, x0 + (idx % k) * cs, y0 + (idx // k) * cs, cs,
                       out, f, H, Hpre, plan)
    elif p[0] == 'strip':
        k = p[1]
        b = size / k
        inner = size - b
        _build(m - 2 * k + 1, x0, y0, inner, out, f, H, Hpre, plan)
        for i in range(k):
            out.append((x0 + i * b, y0 + inner, b))
        for i in range(k - 1):
            out.append((x0 + inner, y0 + i * b, b))


def _ov(a, b):
    return (a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and
            a[1] < b[1] + b[2] and b[1] < a[1] + a[2])


def _climb(sq, L, n, tend, rng):
    cur = [list(q) for q in sq if q[2] > 0]
    cursum = sum(q[2] for q in cur)
    best = [list(q) for q in cur]
    bestsum = cursum
    it = 0
    while time.time() < tend:
        it += 1
        if it % 3000 == 0:
            cur = [list(q) for q in best]
            cursum = bestsum
        if not cur:
            break
        cnt = len(cur)
        r = rng.random()
        if r < 0.08 and cnt < n:
            # repair: split an even square or add a unit square
            if cnt + 3 <= n and rng.random() < 0.5:
                cand = [i for i, q in enumerate(cur) if q[2] >= 2 and q[2] % 2 == 0]
                if cand:
                    i = rng.choice(cand)
                    x, y, s = cur[i]
                    h = s // 2
                    cur[i] = [x, y, h]
                    cur.append([x + h, y, h])
                    cur.append([x, y + h, h])
                    cur.append([x + h, y + h, h])
                    cursum += s
            else:
                for _ in range(10):
                    x = rng.randrange(L)
                    y = rng.randrange(L)
                    a = (x, y, 1)
                    if all(not _ov(a, q) for q in cur):
                        cur.append([x, y, 1])
                        cursum += 1
                        break
        else:
            i = rng.randrange(cnt)
            x, y, s = cur[i]
            ax = rng.randrange(2)
            ay = rng.randrange(2)
            nx, ny, ns = x - ax, y - ay, s + 1
            if nx < 0 or ny < 0 or nx + ns > L or ny + ns > L:
                continue
            A = (nx, ny, ns)
            ovs = [j for j in range(cnt) if j != i and _ov(A, cur[j])]
            net = 1 - len(ovs)
            if net < 0:
                continue
            newq = {}
            ok = True
            for j in ovs:
                xj, yj, sj = cur[j]
                if sj == 1:
                    newq[j] = None
                    continue
                anchors = [(0, 0), (0, 1), (1, 0), (1, 1)]
                rng.shuffle(anchors)
                found = None
                for bx, by in anchors:
                    B = (xj + bx, yj + by, sj - 1)
                    if not _ov(A, B):
                        found = B
                        break
                if found is None:
                    ok = False
                    break
                newq[j] = list(found)
            if not ok:
                continue
            cur[i] = [nx, ny, ns]
            for j, q in newq.items():
                cur[j] = q
            cur = [q for q in cur if q is not None]
            cursum += net
        if cursum > bestsum:
            bestsum = cursum
            best = [list(q) for q in cur]
    return best, bestsum


def _valid(sq, L):
    for q in sq:
        if q[0] < 0 or q[1] < 0 or q[0] + q[2] > L or q[1] + q[2] > L:
            return False
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            if sq[i][2] > 0 and sq[j][2] > 0 and _ov(sq[i], sq[j]):
                return False
    return True


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    t0 = time.time()
    f, H, Hpre, plan = _dp(n)
    out = []
    _build(n, Fraction(0), Fraction(0), Fraction(1), out, f, H, Hpre, plan)
    out = out[:n]
    base_sum = sum(q[2] for q in out)
    result = [(float(x + s / 2), float(y + s / 2), 0.0, float(s)) for (x, y, s) in out]

    # integer hill climbing on an L x L board
    try:
        L = 1
        for (x, y, s) in out:
            for v in (x, y, s):
                L = L * v.denominator // math.gcd(L, v.denominator)
        if L <= 200 and n <= 300:
            rng = random.Random(12345)
            budget = min(9.0, max(0.0, 40.0 - (time.time() - t0)))
            mults = [m for m in (1, 2, 3) if L * m <= 400]
            per = budget / max(1, len(mults))
            best_val = base_sum
            best_layout = None
            for mlt in mults:
                LL = L * mlt
                sq = [[int(x * LL), int(y * LL), int(s * LL)] for (x, y, s) in out]
                tend = time.time() + per
                b, bs = _climb(sq, LL, n, tend, rng)
                if len(b) <= n and Fraction(bs, LL) > best_val and _valid(b, LL):
                    best_val = Fraction(bs, LL)
                    best_layout = (b, LL)
            if best_layout is not None:
                b, LL = best_layout
                result = [((x + s / 2) / LL, (y + s / 2) / LL, 0.0, s / LL)
                          for (x, y, s) in b]
    except Exception:
        pass

    result = result[:n]
    result += [(0.0, 0.0, 0.0, 0.0)] * (n - len(result))
    return result
# EVOLVE-BLOCK-END
