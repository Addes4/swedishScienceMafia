# EVOLVE-BLOCK-START
import math
import time

SHRINK = 1.0 - 1e-12


def _grid_search(n, deadline):
    best_val, best_p = -1.0, None
    r = math.isqrt(n)
    K = r + 6
    B = r + 2
    two_blocks = (K ** 3) * (B ** 2) < 4e6
    for k in range(1, K + 1):
        if k * k > n + 4 * k * k:  # never true; placeholder for clarity
            break
        for a1 in range(0, k + 1):
            b1_range = range(0, B + 1) if a1 > 0 else [0]
            for b1 in b1_range:
                c1 = k * k - a1 * a1 + b1 * b1
                v1 = k * k - a1 * a1 + a1 * b1
                if two_blocks:
                    a2_range = range(0, k - a1 + 1)
                else:
                    a2_range = [0]
                for a2 in a2_range:
                    b2_range = range(0, B + 1) if a2 > 0 else [0]
                    for b2 in b2_range:
                        cnt = c1 - a2 * a2 + b2 * b2
                        if cnt > n or cnt < 0:
                            continue
                        val = (v1 - a2 * a2 + a2 * b2) / k
                        if val > best_val + 1e-12:
                            best_val, best_p = val, (k, a1, b1, a2, b2)
        if time.time() > deadline:
            break
    return best_val, best_p


def _build_grid(p):
    k, a1, b1, a2, b2 = p
    cell = 1.0 / k
    blocks = [(0, 0, a1, b1), (a1, a1, a2, b2)]
    sq = []
    for i in range(k):
        for j in range(k):
            inside = False
            for (x0, y0, a, b) in blocks:
                if a > 0 and x0 <= i < x0 + a and y0 <= j < y0 + a:
                    inside = True
            if not inside:
                sq.append(((i + 0.5) * cell, (j + 0.5) * cell, 0.0, cell * SHRINK))
    for (x0, y0, a, b) in blocks:
        if a > 0 and b > 0:
            s = a * cell / b
            for i in range(b):
                for j in range(b):
                    sq.append((x0 * cell + (i + 0.5) * s, y0 * cell + (j + 0.5) * s, 0.0, s * SHRINK))
    return sq


def _tilted(n, deadline):
    best_val, best_sq = -1.0, None
    angles = [math.atan2(1, 2), math.atan2(3, 4), math.atan2(1, 3)]
    r = math.isqrt(n)
    for th in angles:
        c, s_ = math.cos(th), math.sin(th)
        for k in range(1, r + 1):
            if time.time() > deadline:
                return best_val, best_sq
            side = (1.0 / (k * (c + s_))) * (1 - 1e-9)
            H = k * side / 2.0
            rem = n - k * k
            core_val = k * side
            best_m, best_cells = None, []
            best_add = 0.0
            if rem > 0:
                for m in range(2, 41):
                    g = 1.0 / m
                    cells = []
                    for i in range(m):
                        for j in range(m):
                            cx, cy = (i + 0.5) * g, (j + 0.5) * g
                            dx, dy = cx - 0.5, cy - 0.5
                            ext = H * (c + s_)
                            sep = False
                            if abs(dx) - g / 2 - ext >= 1e-9 or abs(dy) - g / 2 - ext >= 1e-9:
                                sep = True
                            else:
                                pe = (g / 2) * (c + s_)
                                pu = dx * c + dy * s_
                                pv = -dx * s_ + dy * c
                                if abs(pu) - pe - H >= 1e-9 or abs(pv) - pe - H >= 1e-9:
                                    sep = True
                            if sep:
                                cells.append((cx, cy))
                    add = min(rem, len(cells)) * g
                    if add > best_add:
                        best_add, best_m, best_cells = add, m, cells[:rem]
            val = core_val + best_add
            if val > best_val:
                sq = []
                for i in range(k):
                    for j in range(k):
                        oi, oj = (i - (k - 1) / 2) * side, (j - (k - 1) / 2) * side
                        x = 0.5 + oi * c - oj * s_
                        y = 0.5 + oi * s_ + oj * c
                        sq.append((x, y, th / (2 * math.pi), side * SHRINK))
                if best_m:
                    g = 1.0 / best_m
                    for (cx, cy) in best_cells:
                        sq.append((cx, cy, 0.0, g * SHRINK))
                best_val, best_sq = val, sq
    return best_val, best_sq


def solve(n):
    t0 = time.time()
    gv, gp = _grid_search(n, t0 + 25)
    best_sq = _build_grid(gp) if gp is not None else []
    best_val = gv
    try:
        tv, tsq = _tilted(n, t0 + 45)
        if tsq is not None and tv > best_val + 1e-9 and len(tsq) <= n:
            best_val, best_sq = tv, tsq
    except Exception:
        pass
    best_sq = best_sq[:n]
    best_sq += [(0.0, 0.0, 0.0, 0.0)] * (n - len(best_sq))
    out = []
    for (x, y, a, s) in best_sq:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)),
                    min(1.0, max(0.0, a)), min(1.0, max(0.0, s))))
    return out
# EVOLVE-BLOCK-END
