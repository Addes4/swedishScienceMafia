# EVOLVE-BLOCK-START
"""Grid with merged j x j blocks; zero-size padding squares sit on the outer boundary."""
import math


def solve(n):
    best = None  # (sum, m, j, b)
    mmax = min(n + 1, 60)
    for m in range(1, mmax + 1):
        for j in range(1, m + 1):
            maxb = (m // j) ** 2
            for b in range(0, maxb + 1):
                if j == 1 and b > 0:
                    continue
                cnt = m * m - b * (j * j - 1)
                if cnt > n or cnt < 1:
                    continue
                s = (m * m - b * j * j) / m + b * j / m
                if best is None or s > best[0] + 1e-12:
                    best = (s, m, j, b)
    _, m, j, b = best
    side = 1.0 / m
    used = [[False] * m for _ in range(m)]
    squares = []
    per = m // j
    placed = 0
    for a in range(per):
        for c in range(per):
            if placed >= b:
                break
            placed += 1
            for dx in range(j):
                for dy in range(j):
                    used[a * j + dx][c * j + dy] = True
            squares.append(((a * j + j / 2.0) * side, (c * j + j / 2.0) * side, 0.0, j * side))
    for x in range(m):
        for y in range(m):
            if not used[x][y]:
                squares.append(((x + 0.5) * side, (y + 0.5) * side, 0.0, side))
    extra = n - len(squares)
    for i in range(extra):
        t = (i + 1) / (extra + 1)
        squares.append((t, 0.0, 0.0, 0.0))
    return squares[:n]
# EVOLVE-BLOCK-END
