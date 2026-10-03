import math


def _shelf_pack(ms, k):
    """Place m x m blocks (sorted decreasing) in a k x k integer grid by shelves.
    Returns list of (x, y, m) or None."""
    pos = []
    y = 0
    x = 0
    shelf_h = 0
    for m in ms:
        if m > k:
            return None
        if shelf_h == 0:
            shelf_h = m
        if x + m > k:
            y += shelf_h
            x = 0
            shelf_h = m
        if y + m > k:
            return None
        pos.append((x, y, m))
        x += m
    return pos


def _best_for_k(k, extra):
    """Choose multiset of block sizes maximizing sum m, with sum(2m+1) <= extra."""
    best = [0, []]
    counter = [0]

    def rec(ms, maxm, used, gain):
        counter[0] += 1
        if counter[0] > 20000:
            return
        if gain > best[0]:
            best[0] = gain
            best[1] = list(ms)
        for m in range(maxm, 0, -1):
            c = 2 * m + 1
            if used + c > extra:
                continue
            ms.append(m)
            if _shelf_pack(ms, k) is not None:
                rec(ms, m, used + c, gain + m)
            ms.pop()

    rec([], k, 0, 0)
    return best[0], best[1]


def solve(n):
    best_val = -1.0
    best_cfg = None
    k = 1
    while k * k <= n:
        extra = n - k * k
        g, ms = _best_for_k(k, extra)
        val = k + g / k
        if val > best_val + 1e-12:
            best_val = val
            best_cfg = (k, ms)
        k += 1

    k, ms = best_cfg
    ms = sorted(ms, reverse=True)
    pos = _shelf_pack(ms, k) if ms else []
    covered = [[False] * k for _ in range(k)]
    squares = []
    for (bx, by, m) in pos:
        for i in range(m):
            for j in range(m):
                covered[bx + i][by + j] = True
        s = m / ((m + 1) * k)
        for i in range(m + 1):
            for j in range(m + 1):
                cx = (bx / k) + (i + 0.5) * s
                cy = (by / k) + (j + 0.5) * s
                squares.append((cx, cy, 0.0, s))
    side = 1.0 / k
    for i in range(k):
        for j in range(k):
            if not covered[i][j]:
                squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    # clamp to [0,1]
    out = []
    for (cx, cy, a, s) in squares:
        out.append((min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)), a, min(1.0, max(0.0, s))))
    return out
