# EVOLVE-BLOCK-START
"""Grid + block substitution: in a k x k grid of cells (side 1/k), replace a q x q
block by an r x r grid of equal squares (r = q-1 or q+1).  Up to two disjoint
substitutions are combined; the best layout with <= n squares is padded with
zero-size squares."""
import math


def _evaluate(k, ops):
    cnt = k * k
    s = float(k)
    for q, r in ops:
        cnt += r * r - q * q
        s += (r * r) * q / (r * k) - q * q / k if r > 0 else -q * q / k
    return cnt, s


def _build(k, ops):
    blocked = set()
    squares = []
    pos = 0
    for q, r in ops:
        bx = by = pos
        for i in range(bx, bx + q):
            for j in range(by, by + q):
                blocked.add((i, j))
        if r > 0:
            side = q / (r * k)
            x0 = bx / k
            y0 = by / k
            for a in range(r):
                for b in range(r):
                    squares.append((x0 + (a + 0.5) * side, y0 + (b + 0.5) * side, side))
        pos += q
    cell = 1.0 / k
    for i in range(k):
        for j in range(k):
            if (i, j) not in blocked:
                squares.append(((i + 0.5) * cell, (j + 0.5) * cell, cell))
    return squares


def solve(n):
    best = None  # (sum, k, ops)
    kmax = math.isqrt(n) + 3
    for k in range(1, kmax + 1):
        # candidate single and double operations
        opts = [()]
        single = []
        for q in range(1, k + 1):
            single.append((q, q - 1))
            single.append((q, q + 1))
        for o in single:
            opts.append((o,))
        for i, o1 in enumerate(single):
            for o2 in single[i:]:
                if o1[0] + o2[0] <= k:
                    opts.append((o1, o2))
        for ops in opts:
            cnt, s = _evaluate(k, ops)
            if cnt <= n and cnt >= 0:
                if best is None or s > best[0] + 1e-12:
                    best = (s, k, ops)
    if best is None:
        return [(0.5, 0.5, 0.0, 0.0)] * n
    _, k, ops = best
    sq = _build(k, ops)
    shrink = 1.0 - 1e-12
    res = []
    for x, y, side in sq:
        sd = side * shrink
        x = min(max(x, 0.0), 1.0)
        y = min(max(y, 0.0), 1.0)
        res.append((x, y, 0.0, min(max(sd, 0.0), 1.0)))
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res[:n]
# EVOLVE-BLOCK-END
