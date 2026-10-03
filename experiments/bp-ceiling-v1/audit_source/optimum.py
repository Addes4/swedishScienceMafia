"""Exact offline optimum for small bin-packing instances, as a headroom measure for online rules.

optimal_bins(items) solves the assignment ILP with HiGHS (scipy.optimize.milp), using best fit
as the upper bound and the Martello-Toth L2 bound as the lower bound; it skips the solver when
the bounds already meet. Items are sorted in decreasing size and item i may only use bins
0..i, a standard symmetry break. Returns (lower, upper): equal when the optimum is proven.
"""
import numpy as np

from .longpack import l2_bound, pack_rule


def optimal_bins(items, capacity=100, time_limit=20.0):
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import lil_matrix
    lower, upper = l2_bound(items, capacity), pack_rule(items, 'best_fit', capacity)
    if lower == upper:
        return lower, upper
    sizes = sorted(items, reverse=True)
    n, m = len(sizes), upper
    pairs = [(i, j) for i in range(n) for j in range(min(i + 1, m))]
    nx = len(pairs)
    index = {p: k for k, p in enumerate(pairs)}
    cost = np.concatenate([np.zeros(nx), np.ones(m)])
    rows = n + m + m - 1 + 1
    A = lil_matrix((rows, nx + m))
    lo, hi = np.zeros(rows), np.zeros(rows)
    for i in range(n):                                   # every item in exactly one bin
        for j in range(min(i + 1, m)):
            A[i, index[(i, j)]] = 1
        lo[i] = hi[i] = 1
    for j in range(m):                                   # capacity, only if the bin is used
        r = n + j
        for i in range(j, n):
            A[r, index[(i, j)]] = sizes[i]
        A[r, nx + j] = -capacity
        lo[r], hi[r] = -np.inf, 0
    for j in range(m - 1):                               # bins used in order
        r = n + m + j
        A[r, nx + j], A[r, nx + j + 1] = 1, -1
        lo[r], hi[r] = 0, np.inf
    A[rows - 1, nx:] = 1                                 # at least the lower bound
    lo[rows - 1], hi[rows - 1] = lower, np.inf
    res = milp(cost, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=np.ones(nx + m),
               bounds=Bounds(0, 1), options={'time_limit': time_limit, 'disp': False})
    if res.x is not None:
        upper = min(upper, int(round(res.fun)))
    bound = getattr(res, 'mip_dual_bound', None)
    if res.status == 0:
        lower = upper
    elif bound is not None and np.isfinite(bound):
        lower = max(lower, int(np.ceil(bound - 1e-6)))
    return lower, upper
