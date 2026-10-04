# EVOLVE-BLOCK-START
"""ILP on k x k cell grids: choose axis-aligned a x a blocks, each cell covered at
most once, at most n blocks (rest are size-zero squares). Maximise sum a/k."""
import math
import time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix


def _grid_solution(n):
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    sq = sq[:n]
    return sum(s[3] for s in sq), sq


def _solve_k(n, k, tlim):
    cands = []
    rows, cols = [], []
    idx = 0
    for a in range(1, k + 1):
        for x in range(k - a + 1):
            for y in range(k - a + 1):
                cands.append((a, x, y))
                for i in range(x, x + a):
                    for j in range(y, y + a):
                        rows.append(i * k + j)
                        cols.append(idx)
                idx += 1
    m = len(cands)
    data = np.ones(len(rows))
    A_cells = coo_matrix((data, (rows, cols)), shape=(k * k, m)).tocsr()
    A_cnt = np.ones((1, m))
    c = -np.array([a for a, _, _ in cands], dtype=float)
    cons = [LinearConstraint(A_cells, -np.inf, 1.0),
            LinearConstraint(A_cnt, -np.inf, float(n))]
    try:
        res = milp(c, constraints=cons, integrality=np.ones(m),
                   bounds=Bounds(0, 1), options={"time_limit": max(0.5, tlim)})
    except Exception:
        return None
    if res.x is None:
        return None
    sel = [cands[i] for i in range(m) if res.x[i] > 0.5]
    if len(sel) > n:
        return None
    sq = []
    for a, x, y in sel:
        s = a / k
        sq.append(((x + a / 2.0) / k, (y + a / 2.0) / k, 0.0, s))
    return sum(s[3] for s in sq), sq


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    start = time.time()
    best_val, best = _grid_solution(n)
    r = math.sqrt(n)
    kmin = max(1, int(math.floor(r)) - 2)
    kmax = int(math.ceil(2 * r)) + 2
    budget = 45.0
    for k in range(kmin, kmax + 1):
        elapsed = time.time() - start
        if elapsed > budget:
            break
        remaining = budget - elapsed
        out = _solve_k(n, k, min(15.0, remaining))
        if out is not None and out[0] > best_val + 1e-12:
            best_val, best = out
    squares = list(best)
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    squares = [(min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), a, min(1.0, max(0.0, s)))
               for cx, cy, a, s in squares]
    return squares[:n]
# EVOLVE-BLOCK-END
