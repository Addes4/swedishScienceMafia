import math
import time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix


def _grid(n):
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq[:n], k * side


def _ilp(n, L, tl):
    cand = []
    rows = []
    cols = []
    idx = 0
    for i in range(1, L + 1):
        m = L - i + 1
        A, B = np.meshgrid(np.arange(m), np.arange(m), indexing="ij")
        A = A.ravel()
        B = B.ravel()
        di, dj = np.meshgrid(np.arange(i), np.arange(i), indexing="ij")
        di = di.ravel()
        dj = dj.ravel()
        cells = (A[:, None] + di[None, :]) * L + (B[:, None] + dj[None, :])
        c = len(A)
        ids = np.arange(idx, idx + c)
        rows.append(cells.ravel())
        cols.append(np.repeat(ids, i * i))
        for a, b in zip(A.tolist(), B.tolist()):
            cand.append((a, b, i))
        idx += c
    rows = np.concatenate(rows)
    cols = np.concatenate(cols)
    N = idx
    data = np.ones(len(rows))
    M = coo_matrix((data, (rows, cols)), shape=(L * L, N)).tocsr()
    cnt = coo_matrix((np.ones(N), (np.zeros(N, dtype=int), np.arange(N))), shape=(1, N)).tocsr()
    from scipy.sparse import vstack
    Afull = vstack([M, cnt]).tocsr()
    ub = np.ones(L * L + 1)
    ub[-1] = n
    cvec = -np.array([i / L for (_, _, i) in cand])
    res = milp(cvec, constraints=LinearConstraint(Afull, -np.inf, ub),
               integrality=np.ones(N), bounds=Bounds(0, 1),
               options={"time_limit": max(1.0, tl), "mip_rel_gap": 1e-6})
    if res.x is None:
        return None, 0.0
    sel = np.where(res.x > 0.5)[0]
    sq = []
    tot = 0.0
    for s in sel[:n]:
        a, b, i = cand[s]
        sq.append(((a + i / 2.0) / L, (b + i / 2.0) / L, 0.0, i / L))
        tot += i / L
    sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sq))
    return sq, tot


def solve(n):
    t0 = time.time()
    best, bs = _grid(n)
    budget = 48.0
    plan = [(12, 0.2), (20, 0.35), (24, 1.0)]
    for L, frac in plan:
        remaining = budget - (time.time() - t0)
        if remaining < 2:
            break
        tl = remaining * frac if frac < 1.0 else remaining
        try:
            sq, tot = _ilp(n, L, tl)
        except Exception:
            continue
        if sq is not None and tot > bs + 1e-9:
            best, bs = sq, tot
    return best
