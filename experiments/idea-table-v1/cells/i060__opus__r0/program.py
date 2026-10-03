# EVOLVE-BLOCK-START
"""Maximum-weight independent set ILP over axis-aligned lattice squares on
mixed-denominator boards (L = 12, 24, 20, ...)."""
import math
import time
import numpy as np

try:
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import csc_matrix
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY = False


def _grid_solution(n):
    k = max(1, math.isqrt(n))
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    return sq[:n]


def _build(L):
    rows, cols, sides, xs_all, ys_all = [], [], [], [], []
    idx = 0
    for s in range(1, L + 1):
        m = L - s + 1
        gx, gy = np.meshgrid(np.arange(m), np.arange(m), indexing="ij")
        gx = gx.ravel()
        gy = gy.ravel()
        nc = m * m
        di, dj = np.meshgrid(np.arange(s), np.arange(s), indexing="ij")
        di = di.ravel()
        dj = dj.ravel()
        cells = (gx[:, None] + di[None, :]) * L + (gy[:, None] + dj[None, :])
        rows.append(cells.ravel())
        cols.append(np.repeat(idx + np.arange(nc), s * s))
        sides.append(np.full(nc, s))
        xs_all.append(gx)
        ys_all.append(gy)
        idx += nc
    nv = idx
    rows.append(np.full(nv, L * L))
    cols.append(np.arange(nv))
    r = np.concatenate(rows)
    c = np.concatenate(cols)
    data = np.ones(len(r))
    A = csc_matrix((data, (r, c)), shape=(L * L + 1, nv))
    return A, np.concatenate(sides), np.concatenate(xs_all), np.concatenate(ys_all)


def _solve_L(n, L, tlimit):
    A, sides, xs, ys = _build(L)
    nv = len(sides)
    c = -sides.astype(float) / L
    ub = np.ones(L * L + 1)
    ub[-1] = n
    lb = np.full(L * L + 1, -np.inf)
    cons = LinearConstraint(A, lb, ub)
    res = milp(c, constraints=[cons], integrality=np.ones(nv),
               bounds=Bounds(np.zeros(nv), np.ones(nv)),
               options={"time_limit": max(1.0, tlimit), "disp": False})
    if res.x is None:
        return None, 0.0
    sel = np.where(res.x > 0.5)[0]
    if len(sel) > n:
        return None, 0.0
    # verify
    cover = np.zeros((L, L), dtype=int)
    for v in sel:
        s, x, y = sides[v], xs[v], ys[v]
        cover[x:x + s, y:y + s] += 1
    if cover.max() > 1:
        return None, 0.0
    sq = []
    for v in sel:
        s, x, y = int(sides[v]), int(xs[v]), int(ys[v])
        sq.append(((x + s / 2.0) / L, (y + s / 2.0) / L, 0.0, s / float(L)))
    val = sum(t[3] for t in sq)
    return sq, val


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    start = time.time()
    best = _grid_solution(n)
    best_val = sum(t[3] for t in best)
    if _HAVE_SCIPY and n > 1:
        budget = 50.0
        Ls = [12, 24, 20, 18, 16, 30]
        for i, L in enumerate(Ls):
            elapsed = time.time() - start
            remaining = budget - elapsed
            if remaining < 2.0:
                break
            tl = remaining / max(1, (len(Ls) - i)) * 1.5
            tl = min(tl, remaining - 0.5)
            try:
                sq, val = _solve_L(n, L, tl)
            except Exception:
                sq, val = None, 0.0
            if sq is not None and val > best_val + 1e-9:
                best, best_val = sq, val
            # upper bound sqrt(n) (Cauchy-Schwarz with area<=1)
            if best_val >= math.sqrt(n) - 1e-9:
                break
    best = list(best)
    best += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best))
    return best[:n]
# EVOLVE-BLOCK-END
