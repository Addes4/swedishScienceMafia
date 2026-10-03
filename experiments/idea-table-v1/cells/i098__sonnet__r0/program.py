# EVOLVE-BLOCK-START
"""Guillotine DP over integer-lattice rectangles (covers recursive frame peeling)."""
import math
import time
import numpy as np


def _run(L, n):
    NEG = -1e18
    I = np.arange(n + 1)[:, None]          # i
    M = np.arange(n + 1)[None, :]          # m
    # T index: for m (rows) and i (cols): j = m - i
    Jm = M.T - np.arange(n + 1)[None, :]   # shape (m, i) -> m - i
    valid = Jm >= 0
    Jc = np.where(valid, Jm, 0)
    Ic = np.broadcast_to(np.arange(n + 1)[None, :], Jc.shape)

    F = [[None] * (L + 1) for _ in range(L + 1)]
    ch = [[None] * (L + 1) for _ in range(L + 1)]
    for w in range(1, L + 1):
        for h in range(1, L + 1):
            best = np.zeros(n + 1)
            info = [None] * (n + 1)
            if w == h:
                best[1:] = w
                for m in range(1, n + 1):
                    info[m] = ('s',)
            cuts = []
            for c in range(1, w // 2 + 1):
                cuts.append(('v', c, F[c][h], F[w - c][h]))
            for c in range(1, h // 2 + 1):
                cuts.append(('h', c, F[w][c], F[w][h - c]))
            for kind, c, A, B in cuts:
                T = np.where(valid, A[Ic] + B[Jc], NEG)
                arg = T.argmax(axis=1)
                val = T[np.arange(n + 1), arg]
                better = val > best + 1e-12
                if better.any():
                    for m in np.nonzero(better)[0]:
                        best[m] = val[m]
                        info[m] = (kind, c, int(arg[m]))
            F[w][h] = best
            ch[w][h] = info
    return F, ch


def _build(L, n, F, ch):
    out = []

    def rec(w, h, m, x, y):
        if m <= 0:
            return
        inf = ch[w][h][m]
        if inf is None:
            return
        if inf[0] == 's':
            out.append(((x + w / 2) / L, (y + h / 2) / L, 0.0, w / L))
        elif inf[0] == 'v':
            _, c, i = inf
            rec(c, h, i, x, y)
            rec(w - c, h, m - i, x + c, y)
        else:
            _, c, i = inf
            rec(w, c, i, x, y)
            rec(w, h - c, m - i, x, y + c)

    rec(L, L, n, 0, 0)
    return out


def solve(n):
    t0 = time.time()
    best_val = -1.0
    best_sq = None
    last_t = 0.0
    last_L = 1
    for L in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 24]:
        el = time.time() - t0
        if last_t > 0:
            est = last_t * (L / last_L) ** 3.2
            if el + est > 40:
                break
        elif el > 40:
            break
        ts = time.time()
        F, ch = _run(L, n)
        last_t = time.time() - ts
        last_L = L
        val = F[L][L][n] / L
        if val > best_val + 1e-12:
            sq = _build(L, n, F, ch)
            best_val = val
            best_sq = sq
    squares = list(best_sq)[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
