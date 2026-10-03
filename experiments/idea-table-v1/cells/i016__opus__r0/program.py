# EVOLVE-BLOCK-START
"""Two-scale mixed lattice: p x p grid with a corner m x m block re-gridded as
q x q, plus a band variant; best found configuration padded with points."""
import math


def _corner_build(p, m, q):
    sq = []
    s = 1.0 / p
    for i in range(p):
        for j in range(p):
            if i < m and j < m:
                continue
            sq.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
    if q > 0 and m > 0:
        t = m / (p * q)
        for i in range(q):
            for j in range(q):
                sq.append(((i + 0.5) * t, (j + 0.5) * t, 0.0, t))
    return sq


def _band_build(p, r, t):
    sq = []
    s = 1.0 / p
    # band occupies bottom r rows: height r/p
    h = r / p
    small = h / t
    cols = int(math.floor(t * p / r + 1e-9))
    for i in range(cols):
        for j in range(t):
            sq.append(((i + 0.5) * small, (j + 0.5) * small, 0.0, small))
    for i in range(p):
        for j in range(r, p):
            sq.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
    return sq


def solve(n):
    best_val = -1.0
    best = None
    if n <= 0:
        return []
    # corner-block constructions
    pmax = n + 1
    for p in range(1, pmax + 1):
        mlow = 0
        if p * p > n:
            mlow = math.isqrt(p * p - n)
            while p * p - mlow * mlow > n:
                mlow += 1
        for m in range(mlow, p + 1):
            base = p * p - m * m
            if base > n:
                continue
            rem = n - base
            q = math.isqrt(rem) if m > 0 else 0
            val = (base + q * m) / p
            if val > best_val + 1e-12:
                best_val = val
                best = ("c", p, m, q)
    # band constructions
    plim = math.isqrt(n) + 3
    for p in range(1, plim + 1):
        for r in range(1, p + 1):
            base = (p - r) * p
            if base > n:
                continue
            t = 1
            bestt = 0
            while True:
                cols = int(math.floor(t * p / r + 1e-9))
                cnt = base + t * cols
                if cnt > n:
                    break
                bestt = t
                t += 1
            if bestt == 0:
                continue
            cols = int(math.floor(bestt * p / r + 1e-9))
            val = (p - r) + cols * r / p
            if val > best_val + 1e-12:
                best_val = val
                best = ("b", p, r, bestt)
    if best[0] == "c":
        squares = _corner_build(best[1], best[2], best[3])
    else:
        squares = _band_build(best[1], best[2], best[3])
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    # clamp to [0,1]
    out = []
    for (x, y, a, s) in squares:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return out
# EVOLVE-BLOCK-END
