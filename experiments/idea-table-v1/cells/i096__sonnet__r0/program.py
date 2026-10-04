# EVOLVE-BLOCK-START
import math
import time
import itertools
import numpy as np

try:
    from scipy.optimize import linprog
except Exception:  # pragma: no cover
    linprog = None


def _grid_candidate(n, k, counts):
    """counts: dict m->a_m. Returns list of (x,y,s) lower-left squares or None."""
    occ = [[False] * k for _ in range(k)]
    sq = []
    blocks = []
    for m in sorted(counts, reverse=True):
        blocks += [m] * counts[m]
    for m in blocks:
        placed = False
        for i in range(k - m + 1):
            for j in range(k - m + 1):
                if all(not occ[i + a][j + b] for a in range(m) for b in range(m)):
                    for a in range(m):
                        for b in range(m):
                            occ[i + a][j + b] = True
                    sq.append((i / k, j / k, m / k))
                    placed = True
                    break
            if placed:
                break
        if not placed:
            return None
    free = [(i, j) for i in range(k) for j in range(k) if not occ[i][j]]
    need = n - len(sq)
    if need < 0 or need > len(free):
        return None
    for (i, j) in free[:need]:
        sq.append((i / k, j / k, 1.0 / k))
    for (i, j) in free[need:]:
        sq.append(((i + 0.5) / k, (j + 0.5) / k, 0.0))
    # free cells beyond need are zero squares; count must be exactly n
    if len(sq) != n:
        # pad/trim zero squares
        while len(sq) < n:
            sq.append((0.0, 0.0, 0.0))
        sq = sq[:n]
    return sq


def _best_construction(n):
    best = None
    bestv = -1
    k0 = math.isqrt(n)
    if k0 * k0 < n:
        k0 += 1
    for k in range(k0, k0 + 3):
        r = k * k - n
        maxm = min(4, k - 1)
        ms = list(range(2, maxm + 1))
        # enumerate counts
        def rec(idx, rem, cur):
            if idx == len(ms):
                yield dict(cur)
                return
            m = ms[idx]
            red = m * m - 1
            a = 0
            while a * red <= rem:
                if a:
                    cur[m] = a
                yield from rec(idx + 1, rem - a * red, cur)
                a += 1
            cur.pop(m, None)
        cnt = 0
        for counts in rec(0, r, {}):
            cnt += 1
            if cnt > 3000:
                break
            sq = _grid_candidate(n, k, counts)
            if sq is None:
                continue
            v = sum(s for _, _, s in sq)
            if v > bestv + 1e-12:
                bestv = v
                best = sq
    return best, bestv


def _gaps(sq, i, j):
    xi, yi, si = sq[i]
    xj, yj, sj = sq[j]
    return [xj - (xi + si), xi - (xj + sj), yj - (yi + si), yi - (yj + sj)]


def _solve_lp(n, rel):
    nv = 3 * n
    rows = []
    for (i, j), t in rel.items():
        row = np.zeros(nv)
        if t == 0:
            a, b, off = i, j, 0
            row[a] += 1; row[2 * n + a] += 1; row[b] -= 1
        elif t == 1:
            a, b = j, i
            row[a] += 1; row[2 * n + a] += 1; row[b] -= 1
        elif t == 2:
            a, b = i, j
            row[n + a] += 1; row[2 * n + a] += 1; row[n + b] -= 1
        else:
            a, b = j, i
            row[n + a] += 1; row[2 * n + a] += 1; row[n + b] -= 1
        rows.append(row)
    for i in range(n):
        r1 = np.zeros(nv); r1[i] = 1; r1[2 * n + i] = 1; rows.append(r1)
        r2 = np.zeros(nv); r2[n + i] = 1; r2[2 * n + i] = 1; rows.append(r2)
    A = np.array(rows)
    b = np.zeros(len(rows))
    b[-2 * n:] = 1.0
    c = np.zeros(nv)
    c[2 * n:] = -1.0
    try:
        res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, 1)] * nv, method="highs")
    except Exception:
        return None, -1
    if res.status != 0:
        return None, -1
    v = res.x
    sq = [(v[i], v[n + i], max(v[2 * n + i], 0.0)) for i in range(n)]
    return sq, float(v[2 * n:].sum())


def _polish(n, sq, t_end):
    rel = {}
    alts = {}
    for i in range(n):
        for j in range(i + 1, n):
            g = _gaps(sq, i, j)
            t = int(np.argmax(g))
            rel[(i, j)] = t
    cur, val = _solve_lp(n, rel)
    if cur is None:
        return sq
    improved = True
    while improved and time.time() < t_end:
        improved = False
        cands = []
        for (i, j), t in rel.items():
            g = _gaps(cur, i, j)
            if g[t] > 1e-7:
                continue
            for t2 in range(4):
                if t2 != t and g[t2] > -1e-7 - 0.0 and g[t2] > -0.5 * max(cur[i][2], cur[j][2]) - 1e-7:
                    cands.append((i, j, t2))
        for (i, j, t2) in cands:
            if time.time() > t_end:
                break
            old = rel[(i, j)]
            rel[(i, j)] = t2
            s2, v2 = _solve_lp(n, rel)
            if s2 is not None and v2 > val + 1e-9:
                val, cur = v2, s2
                improved = True
            else:
                rel[(i, j)] = old
    return cur


def solve(n):
    t0 = time.time()
    sq, v = _best_construction(n)
    if sq is None:
        k = max(1, math.isqrt(n))
        sq = [((i % k) / k, (i // k) / k, 1.0 / k) if i < k * k else (0.0, 0.0, 0.0)
              for i in range(n)]
    final = sq
    shrink = 0.0
    if linprog is not None and n <= 60:
        try:
            p = _polish(n, sq, t0 + 20.0)
            if sum(s for _, _, s in p) >= sum(s for _, _, s in sq) - 1e-12:
                final = p
                shrink = 1e-10
        except Exception:
            final = sq
    out = []
    for (x, y, s) in final:
        s2 = max(s - shrink, 0.0)
        cx = min(max(x + s2 / 2 + (shrink / 2 if s > shrink else 0.0), 0.0), 1.0)
        cy = min(max(y + s2 / 2 + (shrink / 2 if s > shrink else 0.0), 0.0), 1.0)
        out.append((cx, cy, 0.0, min(s2, 1.0)))
    return out[:n]
# EVOLVE-BLOCK-END
