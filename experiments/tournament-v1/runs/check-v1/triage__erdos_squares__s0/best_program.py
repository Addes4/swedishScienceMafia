# EVOLVE-BLOCK-START
"""Recursive quadtree / grid-split construction optimised by dynamic programming.

g[m] = best sum of sides using m squares inside a unit square, where a square is
either a leaf (m=1), or split into a k x k grid (children scaled 1/k, possibly
empty), or split into an 'L' template (one child of side (k-1)/k plus 2k-1
children of side 1/k).  Children recursively use g.  Zero-size squares pad.
"""
import math
import numpy as np


def solve(n):
    if n <= 0:
        return []
    K = math.isqrt(n) + 1
    J = max(K * K, 2 * K - 1)
    NEG = -1e18

    g = np.full(n + 1, NEG)
    g[0] = 0.0
    P = np.full((J + 1, n + 1), NEG)
    Q = np.full((J + 1, n + 1), NEG)
    P[:, 0] = 0.0
    Q[:, 0] = 0.0
    Qarg = np.zeros((J + 1, n + 1), dtype=np.int64)
    Parg = np.zeros((J + 1, n + 1), dtype=np.int8)
    choice = [None] * (n + 1)

    for m in range(1, n + 1):
        # Q_j(m): partitions of m into j parts, each part < m
        for j in range(1, J + 1):
            best = Q[j - 1][m]
            arg = 0
            if m > 1:
                vals = g[1:m] + P[j - 1][m - 1:0:-1]
                i = int(np.argmax(vals))
                if vals[i] > best + 1e-12:
                    best = vals[i]
                    arg = i + 1
            Q[j][m] = best
            Qarg[j][m] = arg
        # g(m)
        best = NEG
        ch = None
        if m == 1:
            best = 1.0
            ch = ("leaf",)
        for k in range(2, K + 1):
            v = Q[k * k][m] / k
            if v > best + 1e-12:
                best = v
                ch = ("grid", k)
        for k in range(2, K + 1):
            c = 2 * k - 1
            for t in range(0, m):
                rest = Q[c][m] if t == 0 else P[c][m - t]
                if rest <= NEG / 2 or g[t] <= NEG / 2:
                    continue
                v = (k - 1) / k * g[t] + rest / k
                if v > best + 1e-12:
                    best = v
                    ch = ("L", k, t)
        g[m] = best
        choice[m] = ch
        for j in range(1, J + 1):
            if g[m] > Q[j][m] + 1e-12:
                P[j][m] = g[m]
                Parg[j][m] = 1
            else:
                P[j][m] = Q[j][m]
                Parg[j][m] = 0

    def partition(j, m, mode_q):
        parts = []
        while j > 0:
            if m == 0:
                parts += [0] * j
                break
            if not mode_q:
                if Parg[j][m]:
                    parts.append(m)
                    parts += [0] * (j - 1)
                    break
                mode_q = True
                continue
            t = int(Qarg[j][m])
            if t == 0:
                parts.append(0)
                j -= 1
            else:
                parts.append(t)
                j -= 1
                m -= t
                mode_q = False
        return parts

    out = []

    def clamp(x):
        return min(1.0, max(0.0, x))

    stack = [(0.5, 0.5, 1.0, n)]
    while stack:
        cx, cy, s, m = stack.pop()
        if m <= 0:
            continue
        ch = choice[m]
        if ch[0] == "leaf":
            out.append((clamp(cx), clamp(cy), 0.0, clamp(s)))
        elif ch[0] == "grid":
            k = ch[1]
            parts = partition(k * k, m, True)
            x0 = cx - s / 2
            y0 = cy - s / 2
            cs = s / k
            idx = 0
            for a in range(k):
                for b in range(k):
                    if parts[idx] > 0:
                        stack.append((x0 + (a + 0.5) * cs, y0 + (b + 0.5) * cs, cs, parts[idx]))
                    idx += 1
        else:
            k, t = ch[1], ch[2]
            c = 2 * k - 1
            parts = partition(c, m - t, t == 0)
            x0 = cx - s / 2
            y0 = cy - s / 2
            cs = s / k
            if t > 0:
                bs = s * (k - 1) / k
                stack.append((x0 + bs / 2, y0 + bs / 2, bs, t))
            cells = [(a, k - 1) for a in range(k)] + [(k - 1, b) for b in range(k - 1)]
            for (a, b), p in zip(cells, parts):
                if p > 0:
                    stack.append((x0 + (a + 0.5) * cs, y0 + (b + 0.5) * cs, cs, p))

    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END
