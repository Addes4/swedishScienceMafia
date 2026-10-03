# EVOLVE-BLOCK-START
"""Guillotine Pareto DP on rational lattices: every rectangle keeps a
best-sum-per-count table; cuts combine tables by max-plus convolution."""
import math
import time
import numpy as np


def _dp(Q, n, deadline):
    N = n + 1
    W2 = 2 * N - 1
    rows = np.repeat(np.arange(N), N)
    cols = np.tile(np.arange(N), N)
    flat_idx = rows * W2 + rows + cols
    m = np.arange(N)
    mm = np.maximum(m, 1)
    tab = {}
    for i in range(1, Q + 1):
        for j in range(1, Q + 1):
            if time.time() > deadline:
                return None
            W = i / Q
            H = j / Q
            s = np.zeros(N)
            ga = np.ones(N, dtype=int)
            for a in range(1, n + 1):
                b = -(-mm // a)
                sa = np.minimum(W / a, H / b)
                better = sa > s + 1e-15
                s = np.where(better, sa, s)
                ga = np.where(better, a, ga)
            best = m * s
            best[0] = 0.0
            kind = np.zeros(N, dtype=int)
            pos = np.zeros(N, dtype=int)
            left = np.zeros(N, dtype=int)
            cuts = []
            for c in range(1, i // 2 + 1):
                cuts.append((1, c, tab[(c, j)][0], tab[(i - c, j)][0]))
            for c in range(1, j // 2 + 1):
                cuts.append((2, c, tab[(i, c)][0], tab[(i, j - c)][0]))
            for kd, c, A, B in cuts:
                M = A[:, None] + B[None, :]
                S = np.full(N * W2, -np.inf)
                S[flat_idx] = M.ravel()
                S = S.reshape(N, W2)[:, :N]
                res = S.max(axis=0)
                arg = S.argmax(axis=0)
                mask = res > best + 1e-12
                if mask.any():
                    best = np.where(mask, res, best)
                    kind = np.where(mask, kd, kind)
                    pos = np.where(mask, c, pos)
                    left = np.where(mask, arg, left)
            tab[(i, j)] = (best, kind, pos, left, ga)
    return tab


def _rebuild(tab, Q, i, j, k, x0, y0, out):
    if k <= 0:
        return
    best, kind, pos, left, ga = tab[(i, j)]
    kd = int(kind[k])
    if kd == 0:
        W = i / Q
        H = j / Q
        a = int(ga[k])
        b = -(-k // a)
        s = min(W / a, H / b)
        cnt = 0
        for p in range(a):
            for q in range(b):
                if cnt >= k:
                    break
                out.append((x0 + (p + 0.5) * s, y0 + (q + 0.5) * s, s))
                cnt += 1
    elif kd == 1:
        c = int(pos[k]); kl = int(left[k])
        _rebuild(tab, Q, c, j, kl, x0, y0, out)
        _rebuild(tab, Q, i - c, j, k - kl, x0 + c / Q, y0, out)
    else:
        c = int(pos[k]); kl = int(left[k])
        _rebuild(tab, Q, i, c, kl, x0, y0, out)
        _rebuild(tab, Q, i, j - c, k - kl, x0, y0 + c / Q, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    start = time.time()
    deadline = start + 40.0
    k0 = max(1, math.isqrt(n))
    best_val = -1.0
    best_sq = [((i + 0.5) / k0, (j + 0.5) / k0, k0) for i in range(k0) for j in range(k0)]
    best_sq = [(x, y, 1.0 / k0) for x, y, _ in best_sq][:n]
    best_val = len(best_sq) / k0
    Qmax = max(int(2 * math.sqrt(n)) + 2, 12)
    Q = 1
    while True:
        if Q > Qmax and time.time() - start > 15.0:
            break
        if Q > 3 * Qmax:
            break
        if time.time() > deadline:
            break
        tab = _dp(Q, n, deadline)
        if tab is None:
            break
        v = float(tab[(Q, Q)][0][n])
        if v > best_val + 1e-12:
            out = []
            _rebuild(tab, Q, Q, Q, n, 0.0, 0.0, out)
            if abs(sum(o[2] for o in out) - v) < 1e-9:
                best_val = v
                best_sq = out
        Q += 1
    res = []
    for x, y, s in best_sq[:n]:
        s2 = s * (1 - 1e-12)
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), 0.0, min(1.0, max(0.0, s2))))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
