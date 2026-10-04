# EVOLVE-BLOCK-START
"""Baseline: the largest k x k grid that fits, plus size-zero squares for the rest."""
import math


def _plan(n):
    NEG = -1e18
    M = math.isqrt(n) + 3
    CM = M * M
    F = [0.0] * (n + 1)
    desc = [None] * (n + 1)
    H = [[NEG] * (n + 1) for _ in range(CM + 1)]
    chF = [[0] * (n + 1) for _ in range(CM + 1)]
    chR = [[0] * (n + 1) for _ in range(CM + 1)]
    for c in range(CM + 1):
        H[c][0] = 0.0
    for r in range(1, n + 1):
        F[r] = NEG
        # restricted pass: no cell holds all r squares
        for c in range(1, CM + 1):
            best = NEG
            bj = 0
            for j in range(0, r):
                v = F[j] + H[c - 1][r - j]
                if v > best:
                    best = v
                    bj = j
            H[c][r] = best
            chR[c][r] = bj
        Hr = [H[c][r] for c in range(CM + 1)]
        if r == 1:
            F[1] = 1.0
            desc[1] = ('one',)
        else:
            best = F[r - 1]
            d = ('same',)
            for m in range(2, M + 1):
                for a in range(0, m):
                    c = m * m - a * a
                    if a == 0:
                        v = Hr[c] / m
                        if v > best + 1e-12:
                            best = v
                            d = ('grid', m, 0, 0)
                    else:
                        for j1 in range(1, r):
                            v = a / m * F[j1] + H[c][r - j1] / m
                            if v > best + 1e-12:
                                best = v
                                d = ('grid', m, a, j1)
            F[r] = best
            desc[r] = d
        # full pass with F[r] known
        for c in range(1, CM + 1):
            best = NEG
            bj = 0
            for j in range(0, r + 1):
                v = F[j] + H[c - 1][r - j]
                if v > best:
                    best = v
                    bj = j
            H[c][r] = best
            chF[c][r] = bj
    return F, desc, chF, chR


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    F, desc, chF, chR = _plan(n)
    out = []

    def build(r, x0, y0, size):
        if r == 0:
            return
        d = desc[r]
        if d[0] == 'one':
            out.append((x0 + size / 2, y0 + size / 2, 0.0, size))
        elif d[0] == 'same':
            build(r - 1, x0, y0, size)
        else:
            _, m, a, j1 = d
            s = size / m
            cells = [(i, j) for i in range(m) for j in range(m) if not (i < a and j < a)]
            if a > 0:
                build(j1, x0, y0, a * s)
            rr = r - j1
            c = len(cells)
            for (i, j) in cells:
                ch = chR if rr == r else chF
                jj = ch[c][rr]
                build(jj, x0 + i * s, y0 + j * s, s)
                rr -= jj
                c -= 1

    build(n, 0.0, 0.0, 1.0)
    out = [(min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), 0.0, min(1.0, max(0.0, sd)))
           for (x, y, _, sd) in out]
    out = out[:n]
    out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(out))
    return out
# EVOLVE-BLOCK-END