# EVOLVE-BLOCK-START
"""Grid + merge + subdivide construction, optimised over grid size by exact greedy."""
import math


def _levels(R, B):
    """Max sum of t over R cells with sum t^2 <= B. Returns (value, number of cells at each level)."""
    value = 0
    full = R  # number of cells that reached current level-1
    counts = []
    L = 1
    while True:
        cost = 2 * L - 1
        k = min(full, B // cost)
        if k <= 0:
            break
        counts.append(k)
        value += k
        B -= k * cost
        if k < full:
            break
        L += 1
    return value, counts


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    best = None  # (value, m, a, nb, counts)
    k0 = math.isqrt(n)
    for m in range(max(1, k0 - 1), k0 + 6):
        options = [(0, 0)]
        for a in range(2, m + 1):
            for nb in range(1, (m // a) ** 2 + 1):
                options.append((a, nb))
        for a, nb in options:
            R = m * m - nb * a * a
            B = n - nb
            if B < 0 or R < 0:
                continue
            v, counts = _levels(R, B)
            val = (nb * a + v) / m
            if best is None or val > best[0] + 1e-12:
                best = (val, m, a, nb, counts)
    _, m, a, nb, counts = best
    squares = []
    used = set()
    if nb > 0:
        per_row = m // a
        for idx in range(nb):
            bi, bj = divmod(idx, per_row)
            x0, y0 = bi * a, bj * a
            for di in range(a):
                for dj in range(a):
                    used.add((x0 + di, y0 + dj))
            squares.append(((x0 + a / 2.0) / m, (y0 + a / 2.0) / m, 0.0, a / m))
    # t per remaining cell
    cells = [(i, j) for i in range(m) for j in range(m) if (i, j) not in used]
    tvals = [0] * len(cells)
    for lvl, k in enumerate(counts):
        for c in range(k):
            tvals[c] = lvl + 1
    for (i, j), t in zip(cells, tvals):
        if t == 0:
            continue
        s = 1.0 / (m * t)
        for p in range(t):
            for q in range(t):
                squares.append(((i * t + p + 0.5) * s, (j * t + q + 0.5) * s, 0.0, s))
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
