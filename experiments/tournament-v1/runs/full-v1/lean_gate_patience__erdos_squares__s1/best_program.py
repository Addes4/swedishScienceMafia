# EVOLVE-BLOCK-START
"""DP over recursive grid layouts: m x m grid, a j x j corner block merged into one
sub-square (recursively filled), remaining cells recursively filled."""
import math
import numpy as np

_cache = {}


def _prepare(N):
    M = math.isqrt(N) + 3
    Cmax = M * M
    NEG = -1e18
    f = np.zeros(N + 1)
    choice = [None] * (N + 1)
    h = np.full((Cmax + 1, N + 1), NEG)
    harg = np.zeros((Cmax + 1, N + 1), dtype=int)
    h[:, 0] = 0.0

    def fill(n, upto):
        for c in range(1, Cmax + 1):
            u = np.arange(0, upto + 1)
            cand = f[u] + h[c - 1][n - u]
            k = int(np.argmax(cand))
            h[c][n] = cand[k]
            harg[c][n] = k

    f[0] = 0.0
    choice[0] = ('zero',)
    for n in range(1, N + 1):
        if n == 1:
            f[1] = 1.0
            choice[1] = ('one',)
            fill(1, 1)
            continue
        fill(n, n - 1)
        best = f[n - 1]
        ch = ('zero',)
        idx = np.arange(0, n)
        for m in range(2, M + 1):
            for j in range(1, m):
                c = m * m - j * j
                vals = f[idx] * j / m + h[c][n - idx] / m
                k = int(np.argmax(vals))
                if vals[k] > best + 1e-12:
                    best = vals[k]
                    ch = ('grid', m, j, k)
        f[n] = best
        choice[n] = ch
        fill(n, n)
    return f, choice, harg


def _build(n, x0, y0, size, choice, harg, out):
    if n <= 0 or size <= 0:
        return
    ch = choice[n]
    if ch[0] == 'one':
        out.append((x0 + size / 2, y0 + size / 2, 0.0, size))
        return
    if ch[0] == 'zero':
        _build(n - 1, x0, y0, size, choice, harg, out)
        return
    _, m, j, n1 = ch
    cs = size / m
    _build(n1, x0, y0, cs * j, choice, harg, out)
    cells = [(r, c) for r in range(m) for c in range(m) if not (r < j and c < j)]
    cc = len(cells)
    t = n - n1
    while cc > 0 and t > 0:
        u = int(harg[cc][t])
        r, c = cells[cc - 1]
        if u > 0:
            _build(u, x0 + c * cs, y0 + r * cs, cs, choice, harg, out)
        t -= u
        cc -= 1


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    if n not in _cache:
        _cache[n] = _prepare(n)
    f, choice, harg = _cache[n]
    out = []
    _build(n, 0.0, 0.0, 1.0, choice, harg, out)
    res = []
    eps = 1e-10
    for (x, y, a, s) in out:
        s2 = max(s - eps, 0.0)
        res.append((min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0), 0.0, s2))
    res = res[:n]
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
