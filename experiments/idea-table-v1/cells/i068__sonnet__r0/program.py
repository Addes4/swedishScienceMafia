# EVOLVE-BLOCK-START
"""Recursive axis-aligned substitution: k x k grids, optionally with a b x b block
merged in a corner; every cell/block recursively holds a scaled best packing."""
import math

_NEG = float("-inf")


def _build_tables(n):
    K = 7 if n <= 300 else 5
    cmax = K * K
    f = [0.0] * (n + 1)
    ftype = [None] * (n + 1)
    h = [[_NEG] * (n + 1) for _ in range(cmax + 1)]
    ch = [[0] * (n + 1) for _ in range(cmax + 1)]
    for c in range(cmax + 1):
        h[c][0] = 0.0
    for m in range(1, n + 1):
        best = 1.0
        bt = ("one",)
        if m >= 2:
            for k in range(2, K + 1):
                # pure grid
                c = k * k
                hv = _NEG
                row = h[c - 1]
                for t in range(1, m):
                    v = f[t] + row[m - t]
                    if v > hv:
                        hv = v
                if hv > _NEG:
                    v = hv / k
                    if v > best + 1e-12:
                        best = v
                        bt = ("grid", k)
                # block variants
                for b in range(2, k):
                    u = k * k - b * b
                    hu = h[u]
                    for m0 in range(1, m):
                        r = hu[m - m0]
                        if r == _NEG:
                            continue
                        v = (b * f[m0] + r) / k
                        if v > best + 1e-12:
                            best = v
                            bt = ("block", k, b, m0)
        f[m] = best
        ftype[m] = bt
        for c in range(1, cmax + 1):
            hv = _NEG
            ht = 0
            row = h[c - 1]
            for t in range(1, m + 1):
                r = row[m - t]
                if r == _NEG:
                    continue
                v = f[t] + r
                if v > hv:
                    hv = v
                    ht = t
            h[c][m] = hv
            ch[c][m] = ht
    return f, ftype, h, ch


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    f, ftype, h, ch = _build_tables(n)
    out = []

    def distribute(c, m, cells, x0, y0, cs):
        # cells: list of (i, j); c == len(cells)
        rem = m
        idx = 0
        while c >= 1 and rem > 0:
            t = ch[c][rem]
            if t <= 0:
                break
            i, j = cells[idx]
            build(t, x0 + i * cs, y0 + j * cs, cs)
            rem -= t
            idx += 1
            c -= 1

    def build(m, x0, y0, size):
        if m <= 0:
            return
        tp = ftype[m]
        if tp[0] == "one":
            out.append((x0, y0, size))
        elif tp[0] == "grid":
            k = tp[1]
            cs = size / k
            cells = [(i, j) for i in range(k) for j in range(k)]
            distribute(k * k, m, cells, x0, y0, cs)
        else:
            _, k, b, m0 = tp
            cs = size / k
            build(m0, x0, y0, b * cs)
            cells = [(i, j) for i in range(k) for j in range(k) if not (i < b and j < b)]
            distribute(len(cells), m - m0, cells, x0, y0, cs)

    build(n, 0.0, 0.0, 1.0)
    res = []
    shrink = 1.0 - 1e-9
    for (x0, y0, s) in out[:n]:
        s2 = s * shrink
        cx = x0 + s / 2.0
        cy = y0 + s / 2.0
        res.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, min(1.0, max(0.0, s2))))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
