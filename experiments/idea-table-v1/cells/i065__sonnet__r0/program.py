import math
import time
import numpy as np


def _first_fit(grid, a, k):
    n = k - a + 1
    if n <= 0:
        return None
    for i in range(n):
        for j in range(n):
            if not grid[i:i + a, j:j + a].any():
                return i, j
    return None


def _search(k, n, deadline):
    D = max(0, k * k - n)
    best = {"loss": float("inf"), "blocks": None}
    if D == 0:
        return 0.0, []
    nodes = [0]
    lb = 2.0 / (3.0 * k)

    def dfs(maxa, R, grid, loss, blocks):
        if R <= 0:
            if loss < best["loss"]:
                best["loss"] = loss
                best["blocks"] = list(blocks)
            return
        if loss + R * lb >= best["loss"] - 1e-12:
            return
        nodes[0] += 1
        if nodes[0] > 20000 or time.time() > deadline:
            return
        for a in range(maxa, 1, -1):
            pos = _first_fit(grid, a, k)
            if pos is None:
                continue
            i, j = pos
            g2 = grid.copy()
            g2[i:i + a, j:j + a] = True
            blocks.append((i, j, a))
            dfs(a, R - (a * a - 1), g2, loss + (a * a - a) / k, blocks)
            blocks.pop()

    dfs(k, D, np.zeros((k, k), dtype=bool), 0.0, [])
    if best["blocks"] is None:
        return None
    return best["loss"], best["blocks"]


def solve(n):
    t0 = time.time()
    k0 = max(1, math.isqrt(n))
    if k0 * k0 < n:
        k0 += 1
    best_val = -1.0
    best_cfg = None
    # baseline: floor grid
    kb = max(1, math.isqrt(n))
    best_val = float(kb)
    best_cfg = (kb, [])
    kmax = min(k0 + 6, 40)
    for k in range(k0, kmax + 1):
        if time.time() - t0 > 45:
            break
        res = _search(k, n, t0 + 6.0 * (k - k0 + 1))
        if res is None:
            continue
        loss, blocks = res
        val = (k * k) / k - loss
        if val > best_val + 1e-12:
            best_val = val
            best_cfg = (k, blocks)
    k, blocks = best_cfg
    side = 1.0 / k
    grid = np.zeros((k, k), dtype=bool)
    squares = []
    for (i, j, a) in blocks:
        grid[i:i + a, j:j + a] = True
        squares.append(((j + a / 2.0) * side, (i + a / 2.0) * side, 0.0, a * side))
    for i in range(k):
        for j in range(k):
            if not grid[i, j]:
                squares.append(((j + 0.5) * side, (i + 0.5) * side, 0.0, side))
    # if too many (shouldn't happen), drop smallest
    if len(squares) > n:
        squares.sort(key=lambda s: -s[3])
        squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
