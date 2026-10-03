# EVOLVE-BLOCK-START
"""Guillotine DP over D x D grids (generalises frame peeling: corner square + strips of
equal squares + recursion into leftover rectangles), keeping exact count Pareto tables."""
import math
import time
import numpy as np


def _norm(w, h):
    return (w, h) if w >= h else (h, w)


def _run(D, N, IDX):
    NN = N + 1
    NEG = -1e18
    tables = {}
    for a in range(1, D + 1):
        for b in range(1, a + 1):
            best = np.full(NN, NEG)
            best[0] = 0.0
            typ = np.zeros(NN, dtype=np.int64)
            par = np.zeros(NN, dtype=np.int64)
            spl = np.zeros(NN, dtype=np.int64)
            if N >= 1:
                best[1] = float(b)
                typ[1] = 1
            cuts = []
            for x in range(1, a // 2 + 1):
                cuts.append((2, x, _norm(x, b), _norm(a - x, b)))
            for y in range(1, b // 2 + 1):
                cuts.append((3, y, _norm(a, y), _norm(a, b - y)))
            if cuts and N >= 1:
                A = np.stack([tables[c[2]][0] for c in cuts])
                B = np.stack([tables[c[3]][0] for c in cuts])
                K = len(cuts)
                M = (A[:, :, None] + B[:, None, :]).reshape(K, NN * NN)
                M = np.concatenate([M, np.full((K, 1), NEG)], axis=1)
                G = M[:, IDX]  # (K, NN, NN)
                vals = G.max(axis=2)
                args = G.argmax(axis=2)
                kbest = vals.argmax(axis=0)
                rng = np.arange(NN)
                v = vals[kbest, rng]
                imp = v > best + 1e-9
                for c in np.nonzero(imp)[0]:
                    k = kbest[c]
                    best[c] = v[c]
                    typ[c] = cuts[k][0]
                    par[c] = cuts[k][1]
                    spl[c] = args[k, c]
            for c in range(1, NN):
                if best[c - 1] > best[c] + 1e-9:
                    best[c] = best[c - 1]
                    typ[c] = 4
            tables[(a, b)] = (best, typ, par, spl)
    return tables


def _rebuild(tables, D, n):
    out = []

    def rec(w, h, x0, y0, c):
        if c <= 0:
            return
        key = _norm(w, h)
        best, typ, par, spl = tables[key]
        t = typ[c]
        if t == 4:
            out.append((0.0, 0.0, 0.0, 0.0))
            rec(w, h, x0, y0, c - 1)
        elif t == 1:
            s = min(w, h)
            out.append(((x0 + s / 2) / D, (y0 + s / 2) / D, 0.0, s / D))
        elif t == 2 or t == 3:
            p = int(par[c])
            i = int(spl[c])
            long_is_w = w >= h
            # type 2: cut along long side; type 3: cut along short side
            cut_w = (t == 2) == long_is_w
            if cut_w:
                rec(p, h, x0, y0, i)
                rec(w - p, h, x0 + p, y0, c - i)
            else:
                rec(w, p, x0, y0, i)
                rec(w, h - p, x0, y0 + p, c - i)
        else:
            for _ in range(c):
                out.append((0.0, 0.0, 0.0, 0.0))

    rec(D, D, 0, 0, n)
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]


def solve(n):
    if n <= 0:
        return []
    t0 = time.time()
    N = n
    NN = N + 1
    IDX = np.full((NN, NN), NN * NN, dtype=np.int64)
    for c in range(NN):
        for i in range(c + 1):
            IDX[c, i] = i * NN + (c - i)
    best_val = -1.0
    best_D = 1
    best_tables = None
    last = 0.0
    for D in range(1, 80):
        el = time.time() - t0
        # estimate next run cost (roughly ~D^3 growth)
        if el + last * 1.6 > 40.0:
            break
        ts = time.time()
        tables = _run(D, N, IDX)
        last = time.time() - ts
        v = tables[(D, D)][0][n] / D
        if v > best_val + 1e-12:
            best_val = v
            best_D = D
            best_tables = tables
    if best_tables is None:
        k = math.isqrt(n)
        side = 1.0 / k
        sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        sq += [(0.0, 0.0, 0.0, 0.0)] * (n - len(sq))
        return sq[:n]
    res = _rebuild(best_tables, best_D, n)
    clean = []
    for (x, y, a, s) in res:
        clean.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return clean
# EVOLVE-BLOCK-END
