# EVOLVE-BLOCK-START
"""Lagrangian count pricing over guillotine layouts on an integer grid,
followed by count repair (delete smallest / split squares)."""
import math
import time


def _dp_layout(N, lam):
    # F[a][b]: best (sum sides/N - lam*count) for a x b rectangle (grid units)
    F = [[0.0] * (N + 1) for _ in range(N + 1)]
    C = [[None] * (N + 1) for _ in range(N + 1)]
    for a in range(1, N + 1):
        for b in range(1, N + 1):
            best = 0.0
            ch = None
            if a == b:
                v = a / N - lam
                if v > best + 1e-12:
                    best = v
                    ch = ('s',)
            for x in range(1, a // 2 + 1):
                v = F[x][b] + F[a - x][b]
                if v > best + 1e-12:
                    best = v
                    ch = ('v', x)
            for y in range(1, b // 2 + 1):
                v = F[a][y] + F[a][b - y]
                if v > best + 1e-12:
                    best = v
                    ch = ('h', y)
            F[a][b] = best
            C[a][b] = ch
    out = []
    stack = [(0, 0, N, N)]
    while stack:
        x0, y0, a, b = stack.pop()
        ch = C[a][b]
        if ch is None:
            continue
        if ch[0] == 's':
            out.append((x0 / N, y0 / N, a / N))
        elif ch[0] == 'v':
            x = ch[1]
            stack.append((x0, y0, x, b))
            stack.append((x0 + x, y0, a - x, b))
        else:
            y = ch[1]
            stack.append((x0, y0, a, y))
            stack.append((x0, y0 + y, a, b - y))
    return out


def _total(sq):
    return sum(s[2] for s in sq)


def _repair(sq, n):
    sq = sorted(sq, key=lambda t: -t[2])
    if len(sq) > n:
        sq = sq[:n]
    # fill remaining slots by splitting squares
    guard = 0
    while len(sq) < n and guard < 200:
        guard += 1
        r = n - len(sq)
        best = None
        for idx, (x, y, s) in enumerate(sq):
            for k in range(2, 8):
                jmax = min(k * k, r + 1)
                if jmax < 2:
                    continue
                j = jmax
                gain = j * s / k - s
                if gain > 1e-12 and (best is None or gain > best[0] + 1e-12):
                    best = (gain, idx, k, j)
        if best is None:
            break
        _, idx, k, j = best
        x, y, s = sq[idx]
        h = s / k
        new = []
        for i in range(k):
            for jj in range(k):
                if len(new) < j:
                    new.append((x + i * h, y + jj * h, h))
        sq = sq[:idx] + sq[idx + 1:] + new
    return sq[:n]


def solve(n):
    t0 = time.time()
    k = math.isqrt(n)
    side = 1.0 / k
    best_sq = [(i * side, j * side, side) for i in range(k) for j in range(k)][:n]
    best_val = _total(best_sq)

    lams = [0.5 * (1e-4 / 0.5) ** (i / 44.0) for i in range(45)]
    lams.append(0.0)
    Ns = [4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 30, 36, 40, 48]
    seen = set()
    for N in Ns:
        for lam in lams:
            if time.time() - t0 > 30:
                break
            lay = _dp_layout(N, lam)
            key = (N, tuple(sorted(round(s[2] * N) for s in lay)))
            if key in seen:
                continue
            seen.add(key)
            rep = _repair(lay, n)
            v = _total(rep)
            if v > best_val + 1e-12:
                best_val = v
                best_sq = rep
        if time.time() - t0 > 30:
            break

    eps = 1e-12
    res = []
    for (x, y, s) in best_sq:
        s2 = max(0.0, s - eps)
        cx = min(1.0, max(0.0, x + s / 2))
        cy = min(1.0, max(0.0, y + s / 2))
        res.append((cx, cy, 0.0, s2))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
