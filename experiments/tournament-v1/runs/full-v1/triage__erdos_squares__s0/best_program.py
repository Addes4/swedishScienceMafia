# EVOLVE-BLOCK-START
"""Recursive corner/grid constructions with knapsack allocation over cells."""
import math
import time
import numpy as np

NEG = -1e18


def _knap(vals, C, m):
    """vals: array v[j] j=0..m (v[m] = NEG allowed). C identical cells.
    Returns final h (best total with at most t squares) and arg arrays."""
    h = np.zeros(m + 1)
    args = []
    for _ in range(C):
        new = np.full(m + 1, NEG)
        arg = np.zeros(m + 1, dtype=np.int64)
        for j in range(m + 1):
            if vals[j] <= NEG / 2:
                continue
            cand = h[: m + 1 - j] + vals[j]
            seg = new[j:]
            better = cand > seg
            if better.any():
                seg[better] = cand[better]
                arg[j:][better] = j
        h = new
        args.append(arg)
    return h, args


def _solve_all(n, tlimit=40.0):
    t0 = time.time()
    f = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    if n >= 1:
        f[1] = 1.0
        choice[1] = ('one',)
    for m in range(2, n + 1):
        f[m] = f[m - 1]
        choice[m] = ('copy',)
        if time.time() - t0 > tlimit:
            continue
        for q in range(2, 8):
            if q * q > 4 * m + 4 and q > 3:
                break
            v = np.array([f[j] / q for j in range(m)] + [NEG])
            for b in range(0, q):
                C = q * q - b * b
                h, _ = _knap(v, C, m)
                if b == 0:
                    val = h[m]
                    n1 = 0
                else:
                    val = NEG
                    n1 = 0
                    for k in range(1, m):
                        c = f[k] * b / q + h[m - k]
                        if c > val:
                            val = c
                            n1 = k
                if val > f[m] + 1e-12:
                    f[m] = val
                    choice[m] = ('grid', q, b, n1)
    return f, choice


def _build(m, x0, y0, size, f, choice, out):
    if m <= 0:
        return
    ch = choice[m]
    if ch[0] == 'one':
        s = size * (1 - 1e-9)
        out.append((x0 + size / 2, y0 + size / 2, 0.0, s))
        return
    if ch[0] == 'copy':
        _build(m - 1, x0, y0, size, f, choice, out)
        return
    _, q, b, n1 = ch
    v = np.array([f[j] / q for j in range(m)] + [NEG])
    C = q * q - b * b
    _, args = _knap(v, C, m)
    t = m - n1
    alloc = []
    for c in range(C - 1, -1, -1):
        j = int(args[c][t])
        alloc.append(j)
        t -= j
    alloc.reverse()
    cs = size / q
    if b > 0:
        _build(n1, x0, y0, size * b / q, f, choice, out)
    cells = [(i, j) for i in range(q) for j in range(q) if i >= b or j >= b]
    for (i, j), a in zip(cells, alloc):
        _build(a, x0 + i * cs, y0 + j * cs, cs, f, choice, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    f, choice = _solve_all(n)
    out = []
    _build(n, 0.0, 0.0, 1.0, f, choice, out)
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    res = []
    for (x, y, a, s) in out:
        x = min(max(x, 0.0), 1.0)
        y = min(max(y, 0.0), 1.0)
        res.append((x, y, a, min(max(s, 0.0), 1.0)))
    return res
# EVOLVE-BLOCK-END
