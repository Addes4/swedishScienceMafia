# EVOLVE-BLOCK-START
"""Two structural families, best one is returned:
 1) Diagonal staircase: squares s_1..s_k along the main diagonal, the column
    above square i and the row right of it filled with m_i squares of side s_i.
    For fixed integer m the side lengths are optimised exactly by an LP.
 2) Exact guillotine DP on an N x N rational grid (squares, empty cells, cuts),
    maximising the sum of sides with at most n squares.
"""
import math
import time
import numpy as np

try:
    from scipy.optimize import linprog
except Exception:  # pragma: no cover
    linprog = None


# ---------------------------------------------------------------- guillotine DP
def _dp(N, n, deadline):
    F = {}
    CH = {}
    for a in range(1, N + 1):
        for b in range(1, N + 1):
            if time.time() > deadline:
                return None
            f = np.zeros(n + 1, dtype=np.int64)
            kind = np.zeros(n + 1, dtype=np.int8)
            pos = np.zeros(n + 1, dtype=np.int64)
            c1 = np.zeros(n + 1, dtype=np.int64)
            if a == b and n >= 1:
                f[1:] = a
                kind[1:] = 1
            for direction in (2, 3):
                L = a if direction == 2 else b
                for p in range(1, L // 2 + 1):
                    if direction == 2:
                        A = F[(p, b)]
                        B = F[(a - p, b)]
                    else:
                        A = F[(a, p)]
                        B = F[(a, b - p)]
                    for i in range(0, n + 1):
                        if i > 0 and A[i] == A[i - 1]:
                            continue
                        cand = A[i] + B[:n + 1 - i]
                        seg = f[i:]
                        mask = cand > seg
                        if mask.any():
                            idx = np.nonzero(mask)[0] + i
                            f[idx] = cand[mask]
                            kind[idx] = direction
                            pos[idx] = p
                            c1[idx] = i
            F[(a, b)] = f
            CH[(a, b)] = (kind, pos, c1)
    return F, CH


def _reconstruct(N, n, CH):
    out = []
    scale = 1.0 / N

    def place(a, b, c, x, y):
        kind, pos, c1 = CH[(a, b)]
        k = int(kind[c])
        if k == 0 or c == 0:
            return
        if k == 1:
            out.append(((x + a / 2.0) * scale, (y + a / 2.0) * scale, a * scale))
            return
        p = int(pos[c])
        i = int(c1[c])
        if k == 2:
            place(p, b, i, x, y)
            place(a - p, b, c - i, x + p, y)
        else:
            place(a, p, i, x, y)
            place(a, b - p, c - i, x, y + p)

    place(N, N, n, 0, 0)
    return out


def _guillotine(n, deadline):
    best_val = -1.0
    best_sq = None
    N = 1
    while N <= 60 and time.time() < deadline:
        res = _dp(N, n, deadline)
        if res is None:
            break
        F, CH = res
        val = F[(N, N)][n] / N
        if val > best_val + 1e-12:
            best_val = val
            best_sq = _reconstruct(N, n, CH)
        N += 1
    return best_val, best_sq


# ---------------------------------------------------------------- staircase
def _stair_lp(m):
    k = len(m)
    c = -np.array([1.0 + 2.0 * mi for mi in m])
    A = []
    bvec = []
    for i in range(k):
        row = [1.0 if j <= i else 0.0 for j in range(k)]
        row[i] += m[i]
        A.append(row)
        bvec.append(1.0)
    # decreasing sizes (structure of staircase)
    for i in range(k - 1):
        row = [0.0] * k
        row[i + 1] = 1.0
        row[i] = -1.0
        A.append(row)
        bvec.append(0.0)
    try:
        r = linprog(c, A_ub=np.array(A), b_ub=np.array(bvec),
                    bounds=[(0, 1)] * k, method="highs")
    except Exception:
        return None, None
    if r is None or not r.success:
        return None, None
    return -r.fun, r.x


def _staircase(n, deadline):
    if linprog is None:
        return -1.0, None
    best = [-1.0, None, None]

    def rec(m, k, budget):
        if time.time() > deadline:
            return
        if len(m) == k:
            val, s = _stair_lp(m)
            if val is not None and val > best[0] + 1e-12:
                best[0], best[1], best[2] = val, list(m), s
            return
        for mi in range(budget // 2, -1, -1):
            m.append(mi)
            rec(m, k, budget - 2 * mi)
            m.pop()
            if time.time() > deadline:
                return

    for k in range(1, min(n, 8) + 1):
        if time.time() > deadline:
            break
        rec([], k, n - k)
    if best[1] is None:
        return -1.0, None
    m, s = best[1], best[2]
    out = []
    P = 0.0
    for i, (mi, si) in enumerate(zip(m, s)):
        si = max(0.0, float(si))
        x0 = P
        P += si
        out.append((x0 + si / 2, x0 + si / 2, si))
        for j in range(mi):
            out.append((x0 + si / 2, P + (j + 0.5) * si, si))
            out.append((P + (j + 0.5) * si, x0 + si / 2, si))
    total = sum(q[2] for q in out)
    return total, out


# ---------------------------------------------------------------- main
def solve(n):
    start = time.time()
    if n <= 0:
        return []
    candidates = []
    k = math.isqrt(n)
    side = 1.0 / k
    grid = [((i + 0.5) * side, (j + 0.5) * side, side) for i in range(k) for j in range(k)]
    candidates.append((k * side * k, grid))

    sv, ssq = _staircase(n, start + 10.0)
    if ssq is not None and len(ssq) <= n:
        candidates.append((sv, ssq))

    gv, gsq = _guillotine(n, start + 45.0)
    if gsq is not None and len(gsq) <= n:
        candidates.append((gv, gsq))

    best = max(candidates, key=lambda t: t[0])[1]
    eps = 1e-12
    res = []
    for (x, y, s) in best:
        s2 = max(0.0, s - eps)
        x = min(1.0, max(0.0, x))
        y = min(1.0, max(0.0, y))
        res.append((x, y, 0.0, min(1.0, s2)))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
