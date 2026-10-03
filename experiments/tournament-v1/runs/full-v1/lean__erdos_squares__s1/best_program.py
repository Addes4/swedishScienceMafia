# EVOLVE-BLOCK-START
"""Recursive grid / merged-block construction found by dynamic programming."""
import math
import numpy as np

_G = [0.0, 1.0]
_DESC = {}


def _compute(n):
    NEG = -1e18
    Gt = np.array(_G[:n] + [NEG], dtype=float)
    K = math.isqrt(n) + 2
    C = K * K
    h = np.full((C + 1, n + 1), NEG)
    h[0, 0] = 0.0
    ch = np.zeros((C + 1, n + 1), dtype=int)
    m_idx = np.arange(n + 1)[:, None]
    t_idx = np.arange(n + 1)[None, :]
    idx = m_idx - t_idx
    mask = idx >= 0
    idxc = np.where(mask, idx, 0)
    for c in range(1, C + 1):
        M = np.where(mask, h[c - 1][idxc] + Gt[None, :], NEG)
        h[c] = M.max(axis=1)
        ch[c] = M.argmax(axis=1)
    best = (_G[n - 1], None)
    for k in range(2, K + 1):
        v = h[k * k][n] / k
        if v > best[0] + 1e-12:
            best = (v, (k, 0, 0))
        for j in range(2, k):
            c = k * k - j * j
            mbs = np.arange(1, n)
            if len(mbs) == 0:
                continue
            vals = np.array(_G)[mbs] * j / k + h[c][n - mbs] / k
            i = int(vals.argmax())
            if vals[i] > best[0] + 1e-12:
                best = (float(vals[i]), (k, j, int(mbs[i])))
    val, opt = best
    if opt is None:
        _G.append(_G[n - 1])
        _DESC[n] = ("copy",)
        return
    k, j, mb = opt
    c = k * k - j * j if j else k * k
    m = n - mb
    assign = []
    while c > 0:
        t = int(ch[c][m])
        assign.append(t)
        m -= t
        c -= 1
    _G.append(val)
    _DESC[n] = ("grid", k, j, mb, assign)


def _gen(n, x0, y0, s, out):
    if n <= 0:
        return
    if n == 1:
        sd = s * (1 - 1e-10)
        out.append((x0 + s / 2, y0 + s / 2, 0.0, sd))
        return
    d = _DESC[n]
    if d[0] == "copy":
        _gen(n - 1, x0, y0, s, out)
        return
    _, k, j, mb, assign = d
    cs = s / k
    if j:
        _gen(mb, x0, y0, cs * j, out)
    it = iter(assign)
    for a in range(k):
        for b in range(k):
            if j and a < j and b < j:
                continue
            t = next(it, 0)
            _gen(t, x0 + a * cs, y0 + b * cs, cs, out)


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    while len(_G) <= n:
        _compute(len(_G))
    out = []
    _gen(n, 0.0, 0.0, 1.0, out)
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
