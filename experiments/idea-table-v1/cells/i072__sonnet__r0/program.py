# EVOLVE-BLOCK-START
"""Recursive grid construction solved with a max-plus knapsack DP.

The unit square is split into an m x m grid; an optional j x j block of cells
is merged into one big cell; each cell recursively holds a scaled copy of the
best layout for some smaller count.  Counts are distributed by DP.
"""
import math
import time
import numpy as np

_NEG = -1e18
_best = [0.0, 1.0]
_struct = {0: ('empty',), 1: ('one',)}


def _compute(n_target, t0):
    while len(_best) <= n_target:
        n = len(_best)
        if time.time() - t0 > 40.0:
            _best.append(_best[n - 1])
            _struct[n] = ('pad',)
            continue
        b = np.array(_best[:n], dtype=float)  # counts 0..n-1
        ks = np.arange(n)
        Nn = np.arange(n + 1)
        idx = Nn[:, None] - ks[None, :]
        valid = idx >= 0
        idxc = np.where(valid, idx, 0)
        pen = np.where(valid, 0.0, _NEG)
        M = math.isqrt(n) + 2
        cmax = M * M
        G = [np.full(n + 1, _NEG)]
        G[0][0] = 0.0
        AM = [None]
        rows = np.arange(n + 1)
        for c in range(1, cmax + 1):
            cand = b[None, :] + G[c - 1][idxc] + pen
            am = cand.argmax(axis=1)
            G.append(cand[rows, am])
            AM.append(am)
        # baseline: pad previous
        bv = _best[n - 1]
        bs = ('pad',)
        for m in range(2, M + 1):
            for j in range(0, m):
                if j == 0:
                    c = m * m
                    v = G[c][n] / m
                    nb = 0
                else:
                    c = m * m - j * j
                    nbs = np.arange(0, n)
                    vals = (j / m) * b[nbs] + G[c][n - nbs] / m
                    t = int(vals.argmax())
                    v = float(vals[t])
                    nb = t
                if v > bv + 1e-12:
                    N = n - nb
                    counts = []
                    ok = True
                    for cc in range(c, 0, -1):
                        k = int(AM[cc][N])
                        counts.append(k)
                        N -= k
                    if N != 0:
                        ok = False
                    if ok:
                        bv = v
                        bs = ('grid', m, j, nb, counts)
        _best.append(bv)
        _struct[n] = bs


def _place(n, x0, y0, s, out):
    if n <= 0:
        return
    st = _struct[n]
    kind = st[0]
    if kind == 'one':
        sd = s * (1 - 1e-9)
        out.append((x0 + s / 2, y0 + s / 2, 0.0, sd))
    elif kind == 'pad':
        _place(n - 1, x0, y0, s, out)
    elif kind == 'grid':
        _, m, j, nb, counts = st
        cs = s / m
        if j > 0:
            _place(nb, x0, y0, cs * j, out)
        it = iter(counts)
        for r in range(m):
            for c in range(m):
                if j > 0 and r < j and c < j:
                    continue
                k = next(it, 0)
                _place(k, x0 + c * cs, y0 + r * cs, cs, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    _compute(n, t0)
    out = []
    _place(n, 0.0, 0.0, 1.0, out)
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    res = []
    for (x, y, a, s) in out:
        x = min(max(x, 0.0), 1.0)
        y = min(max(y, 0.0), 1.0)
        s = min(max(s, 0.0), 1.0)
        res.append((x, y, a, s))
    return res
# EVOLVE-BLOCK-END
