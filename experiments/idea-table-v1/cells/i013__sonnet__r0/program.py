# EVOLVE-BLOCK-START
"""ILP on a k x k cell grid: choose axis-aligned a x a blocks, each cell covered at most once,
at most n blocks, maximise sum of a/k. Loop over k near sqrt(n)."""
import math
import time
import numpy as np


def _baseline(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    return sq, k * side * k


def _ilp(n, k, tlimit):
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import coo_matrix
    cands = []
    rows = []
    cols = []
    for a in range(1, k + 1):
        for i in range(k - a + 1):
            for j in range(k - a + 1):
                idx = len(cands)
                cands.append((i, j, a))
                for x in range(i, i + a):
                    base = x * k
                    for y in range(j, j + a):
                        rows.append(base + y)
                        cols.append(idx)
    m = len(cands)
    # count row
    for idx in range(m):
        rows.append(k * k)
        cols.append(idx)
    data = np.ones(len(rows))
    A = coo_matrix((data, (rows, cols)), shape=(k * k + 1, m)).tocsr()
    ub = np.ones(k * k + 1)
    ub[-1] = n
    c = -np.array([a / k for (_, _, a) in cands])
    res = milp(c, constraints=LinearConstraint(A, -np.inf, ub),
               integrality=np.ones(m), bounds=Bounds(0, 1),
               options={"time_limit": max(0.5, tlimit), "disp": False})
    if res.x is None:
        return None, 0.0
    sel = [cands[t] for t in range(m) if res.x[t] > 0.5]
    if len(sel) > n:
        return None, 0.0
    sq = [((i + a / 2.0) / k, (j + a / 2.0) / k, 0.0, a / k) for (i, j, a) in sel]
    return sq, sum(s[3] for s in sq)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    best, bestv = _baseline(n)
    r = math.sqrt(n)
    lo = max(1, math.isqrt(n) - 2)
    hi = 2 * math.isqrt(n)
    ks = sorted(range(lo, hi + 1), key=lambda k: abs(k - r))
    for k in ks:
        rem = 45.0 - (time.time() - t0)
        if rem <= 1:
            break
        try:
            sq, v = _ilp(n, k, min(10.0, rem))
        except Exception:
            continue
        if sq is not None and v > bestv + 1e-12:
            best, bestv = sq, v
    best = list(best)[:n]
    best += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best))
    return best
# EVOLVE-BLOCK-END
