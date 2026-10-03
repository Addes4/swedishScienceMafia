# EVOLVE-BLOCK-START
"""Guillotine DP over rational grids, guided/early-exited by known upper bounds."""
import math
import time


def _upper_bound(n):
    k = math.isqrt(n)
    if k * k == n:
        return float(k)
    if n == k * k + 1 and k <= 13:
        return float(k)
    return math.sqrt(n)


def _dp(D, N):
    """F[(a,b)][c] (a<=b): max sum (units 1/D) of c squares in a (width) x b (height)
    rectangle via guillotine cuts."""
    F = {}
    CH = {}
    for s in range(2, 2 * D + 1):
        for a in range(1, D + 1):
            b = s - a
            if b < a or b > D:
                continue
            best = [0] + [a] * N
            ch = [None] + [('sq',)] * N
            # horizontal cuts (split height b)
            for b1 in range(1, b // 2 + 1):
                b2 = b - b1
                A = F[(a, b1) if a <= b1 else (b1, a)]
                B = F[(a, b2) if a <= b2 else (b2, a)]
                for c in range(2, N + 1):
                    bc = best[c]
                    bi = -1
                    for i in range(1, c):
                        v = A[i] + B[c - i]
                        if v > bc:
                            bc = v
                            bi = i
                    if bi >= 0:
                        best[c] = bc
                        ch[c] = ('h', b1, bi)
            # vertical cuts (split width a)
            for a1 in range(1, a // 2 + 1):
                a2 = a - a1
                A = F[(a1, b)]
                B = F[(a2, b)]
                for c in range(2, N + 1):
                    bc = best[c]
                    bi = -1
                    for i in range(1, c):
                        v = A[i] + B[c - i]
                        if v > bc:
                            bc = v
                            bi = i
                    if bi >= 0:
                        best[c] = bc
                        ch[c] = ('v', a1, bi)
            for c in range(2, N + 1):
                if best[c - 1] > best[c]:
                    best[c] = best[c - 1]
                    ch[c] = ('carry',)
            F[(a, b)] = best
            CH[(a, b)] = ch
    return F, CH


def _reconstruct(CH, w, h, c, x0, y0, out):
    if c <= 0:
        return
    if w <= h:
        _rec(CH, w, h, c, x0, y0, False, out)
    else:
        _rec(CH, h, w, c, x0, y0, True, out)


def _rec(CH, a, b, c, x0, y0, tr, out):
    # rectangle key (a,b): width a, height b in key orientation; if tr, swapped.
    while True:
        ch = CH[(a, b)][c]
        if ch[0] == 'carry':
            c -= 1
            continue
        break
    if ch[0] == 'sq':
        out.append((x0, y0, a))
        return
    if ch[0] == 'h':
        b1, i = ch[1], ch[2]
        # lower: a x b1, upper: a x (b-b1) offset in key-y by b1
        if not tr:
            _reconstruct(CH, a, b1, i, x0, y0, out)
            _reconstruct(CH, a, b - b1, c - i, x0, y0 + b1, out)
        else:
            _reconstruct(CH, b1, a, i, x0, y0, out)
            _reconstruct(CH, b - b1, a, c - i, x0 + b1, y0, out)
    else:
        a1, i = ch[1], ch[2]
        if not tr:
            _reconstruct(CH, a1, b, i, x0, y0, out)
            _reconstruct(CH, a - a1, b, c - i, x0 + a1, y0, out)
        else:
            _reconstruct(CH, b, a1, i, x0, y0, out)
            _reconstruct(CH, b, a - a1, c - i, x0, y0 + a1, out)


def _grid(n):
    k = math.isqrt(n)
    side = 1.0 / k
    sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side * (1 - 1e-12))
          for i in range(k) for j in range(k)]
    return sq, float(k)


def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    bound = _upper_bound(n)
    best_sq, best_val = _grid(n)
    if best_val >= bound - 1e-9:
        best_sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_sq))
        return best_sq[:n]

    budget = 40.0
    Ds = [12, 24, 36, 48, 60, 72, 84, 96, 120]
    last_t, last_D = None, None
    for D in Ds:
        elapsed = time.time() - t0
        if last_t is not None:
            est = last_t * (D / last_D) ** 3 * 1.2
            if elapsed + est > budget:
                break
        ts = time.time()
        F, CH = _dp(D, n)
        val = F[(D, D)][n] / D
        if val > best_val + 1e-12:
            out = []
            _rec(CH, D, D, n, 0, 0, False, out)
            sq = []
            for (x, y, s) in out:
                sq.append(((x + s / 2.0) / D, (y + s / 2.0) / D, 0.0,
                           (s / D) * (1 - 1e-12)))
            best_sq, best_val = sq, val
        last_t, last_D = time.time() - ts, D
        if best_val >= bound - 1e-9:
            break

    best_sq = list(best_sq)
    best_sq += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_sq))
    return best_sq[:n]
# EVOLVE-BLOCK-END
