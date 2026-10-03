# EVOLVE-BLOCK-START
"""Guillotine DP on a D x D lattice: generalises Egyptian rows / L-shaped / merged-grid
constructions. Rectangles are split by integer cuts; squares fill leaf rectangles."""
import time
import numpy as np


def _build(D, N):
    G = [[None] * (D + 1) for _ in range(D + 1)]
    for p in range(1, D + 1):
        for q in range(1, D + 1):
            if q < p:
                G[p][q] = G[q][p]
                continue
            out = np.zeros(N + 1)
            out[1:] = min(p, q) / D
            for i in range(1, p // 2 + 1):
                A = G[i][q]
                B = G[p - i][q]
                for n1 in range(0, N + 1):
                    np.maximum(out[n1:], A[n1] + B[:N + 1 - n1], out=out[n1:])
            for j in range(1, q // 2 + 1):
                A = G[p][j]
                B = G[p][q - j]
                for n1 in range(0, N + 1):
                    np.maximum(out[n1:], A[n1] + B[:N + 1 - n1], out=out[n1:])
            out = np.maximum.accumulate(out)
            G[p][q] = out
    return G


def _reconstruct(G, D, n):
    res = []
    stack = [(D, D, n, 0, 0)]
    while stack:
        p, q, k, x0, y0 = stack.pop()
        if k <= 0:
            continue
        target = G[p][q][k]
        s = min(p, q)
        if s / D >= target - 1e-9:
            res.append(((x0 + s / 2) / D, (y0 + s / 2) / D, 0.0, s / D))
            continue
        found = False
        for i in range(1, p // 2 + 1):
            A = G[i][q]
            B = G[p - i][q]
            vals = A[:k + 1] + B[k::-1]
            n1 = int(np.argmax(vals))
            if vals[n1] >= target - 1e-9:
                stack.append((i, q, n1, x0, y0))
                stack.append((p - i, q, k - n1, x0 + i, y0))
                found = True
                break
        if found:
            continue
        for j in range(1, q // 2 + 1):
            A = G[p][j]
            B = G[p][q - j]
            vals = A[:k + 1] + B[k::-1]
            n1 = int(np.argmax(vals))
            if vals[n1] >= target - 1e-9:
                stack.append((p, j, n1, x0, y0))
                stack.append((p, q - j, k - n1, x0, y0 + j))
                found = True
                break
        if not found:
            res.append(((x0 + s / 2) / D, (y0 + s / 2) / D, 0.0, s / D))
    return res


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    t0 = time.time()
    budget = 30.0
    best = None
    D = 2
    last_t = None
    lastD = None
    while D <= 40:
        if last_t is not None:
            est = last_t * (D / lastD) ** 3.2
            if time.time() - t0 + est > budget:
                break
        ts = time.time()
        G = _build(D, n)
        last_t = max(time.time() - ts, 1e-4)
        lastD = D
        val = G[D][D][n]
        if best is None or val > best[0] + 1e-12:
            best = (val, D, G)
        D += 1 if D < 12 else 2
    val, D, G = best
    sq = _reconstruct(G, D, n)
    eps = 1e-9
    out = []
    for (cx, cy, a, s) in sq:
        s2 = max(0.0, s - eps)
        out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), 0.0, s2))
    out = out[:n]
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
