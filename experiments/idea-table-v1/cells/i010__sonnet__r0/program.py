import math


def solve(n):
    """Grid-based constructions: on a k x k grid, place c aligned m x m blocks and
    fill remaining cells with unit squares (side 1/k); pad with size-zero squares.
    Choose the best (k, m, c) by total side length."""
    best = None
    kmax = int(2 * math.sqrt(n)) + 4
    for k in range(1, kmax + 1):
        # plain grid, c = 0
        val = min(n, k * k) / k
        if best is None or val > best[0] + 1e-12:
            best = (val, k, 1, 0)
        for m in range(2, k + 1):
            maxc = min((k // m) ** 2, n)
            for c in range(1, maxc + 1):
                val = (c * m + min(n - c, k * k - c * m * m)) / k
                if val > best[0] + 1e-12:
                    best = (val, k, m, c)
    _, k, m, c = best
    side = 1.0 / k
    squares = []
    occ = [[False] * k for _ in range(k)]
    if c > 0 and m >= 2:
        per = k // m
        placed = 0
        for bi in range(per):
            for bj in range(per):
                if placed >= c:
                    break
                for i in range(bi * m, (bi + 1) * m):
                    for j in range(bj * m, (bj + 1) * m):
                        occ[i][j] = True
                squares.append(((bi * m + m / 2) * side, (bj * m + m / 2) * side, 0.0, m * side))
                placed += 1
    for i in range(k):
        for j in range(k):
            if len(squares) >= n:
                break
            if not occ[i][j]:
                squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
