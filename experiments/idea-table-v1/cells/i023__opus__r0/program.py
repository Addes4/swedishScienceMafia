# EVOLVE-BLOCK-START
import math
import numpy as np


def _dp(n):
    NEG = -1e18
    f = [NEG] * (n + 1)
    choice = [None] * (n + 1)
    f[0] = 0.0
    choice[0] = ('empty',)
    if n >= 1:
        f[1] = 1.0
        choice[1] = ('single',)
    K = math.isqrt(n) + 2
    for _ in range(10):
        changed = False
        for c in range(1, n + 1):
            if f[c - 1] > f[c] + 1e-12:
                f[c] = f[c - 1]
                choice[c] = ('pad',)
                changed = True
        for k in range(2, K + 1):
            farr = np.array(f, dtype=float)
            umax = k * k
            H = [np.full(n + 1, NEG)]
            H[0][0] = 0.0
            P = []
            for i in range(umax):
                hp = H[-1]
                hn = np.full(n + 1, NEG)
                par = np.zeros(n + 1, dtype=int)
                for c1 in range(n + 1):
                    cand = farr[c1] + hp[:n + 1 - c1]
                    seg = hn[c1:]
                    mask = cand > seg + 1e-12
                    if mask.any():
                        seg[mask] = cand[mask]
                        par[c1:][mask] = c1
                H.append(hn)
                P.append(par)

            def backtrack(u, rem):
                counts = []
                for i in range(u, 0, -1):
                    c1 = int(P[i - 1][rem])
                    counts.append(c1)
                    rem -= c1
                return counts

            for c in range(1, n + 1):
                val = H[umax][c] / k
                if val > f[c] + 1e-12:
                    f[c] = val
                    choice[c] = ('grid', k, 0, 0, backtrack(umax, c))
                    changed = True
                for m in range(2, k):
                    u = umax - m * m
                    best, bcb = NEG, -1
                    for cb in range(0, c + 1):
                        v = (m / k) * f[cb] + H[u][c - cb] / k
                        if v > best:
                            best, bcb = v, cb
                    if best > f[c] + 1e-12:
                        f[c] = best
                        choice[c] = ('grid', k, m, bcb, backtrack(u, c - bcb))
                        changed = True
        if not changed:
            break
    return f, choice


def _build(c, x0, y0, s, choice, out):
    ch = choice[c]
    t = ch[0]
    if t == 'empty':
        return
    if t == 'single':
        out.append((x0 + s / 2, y0 + s / 2, 0.0, s))
        return
    if t == 'pad':
        _build(c - 1, x0, y0, s, choice, out)
        out.append((x0, y0, 0.0, 0.0))
        return
    _, k, m, cb, counts = ch
    cell = s / k
    if m >= 2:
        _build(cb, x0, y0, m * cell, choice, out)
    idx = 0
    for i in range(k):
        for j in range(k):
            if m >= 2 and i < m and j < m:
                continue
            _build(counts[idx], x0 + i * cell, y0 + j * cell, cell, choice, out)
            idx += 1


def _valid(sq, n, tol=1e-9):
    if len(sq) != n:
        return False
    boxes = []
    for (cx, cy, a, s) in sq:
        for v in (cx, cy, a, s):
            if not (0 <= v <= 1):
                return False
        if cx - s / 2 < -tol or cx + s / 2 > 1 + tol or cy - s / 2 < -tol or cy + s / 2 > 1 + tol:
            return False
        boxes.append((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2, s))
    for i in range(n):
        for j in range(i + 1, n):
            a, b = boxes[i], boxes[j]
            if a[4] <= 0 or b[4] <= 0:
                continue
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > tol and oy > tol:
                return False
    return True


def _milp(n, cutoff, tlim):
    try:
        from scipy.optimize import milp, LinearConstraint, Bounds
        from scipy.sparse import lil_matrix
    except Exception:
        return None
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    P = len(pairs)
    nv = 3 * n + 4 * P
    X = lambda i: i
    Y = lambda i: n + i
    S = lambda i: 2 * n + i
    B = lambda p, t: 3 * n + 4 * p + t
    rows = 2 * n + 5 * P + (n - 1) + 2 + 1
    A = lil_matrix((rows, nv))
    lo = np.full(rows, -np.inf)
    hi = np.full(rows, np.inf)
    r = 0
    for i in range(n):
        A[r, X(i)] = 1; A[r, S(i)] = 1; hi[r] = 1; r += 1
        A[r, Y(i)] = 1; A[r, S(i)] = 1; hi[r] = 1; r += 1
    for p, (i, j) in enumerate(pairs):
        # i left of j
        A[r, X(i)] = 1; A[r, S(i)] = 1; A[r, X(j)] = -1; A[r, B(p, 0)] = 1; hi[r] = 1; r += 1
        A[r, X(j)] = 1; A[r, S(j)] = 1; A[r, X(i)] = -1; A[r, B(p, 1)] = 1; hi[r] = 1; r += 1
        A[r, Y(i)] = 1; A[r, S(i)] = 1; A[r, Y(j)] = -1; A[r, B(p, 2)] = 1; hi[r] = 1; r += 1
        A[r, Y(j)] = 1; A[r, S(j)] = 1; A[r, Y(i)] = -1; A[r, B(p, 3)] = 1; hi[r] = 1; r += 1
        for t in range(4):
            A[r, B(p, t)] = 1
        lo[r] = 1; r += 1
    for i in range(n - 1):
        A[r, S(i)] = 1; A[r, S(i + 1)] = -1; lo[r] = 0; r += 1
    A[r, X(0)] = 1; A[r, S(0)] = 0.5; hi[r] = 0.5; r += 1
    A[r, Y(0)] = 1; A[r, S(0)] = 0.5; hi[r] = 0.5; r += 1
    for i in range(n):
        A[r, S(i)] = 1
    lo[r] = cutoff; r += 1
    c = np.zeros(nv)
    c[2 * n:3 * n] = -1
    integ = np.zeros(nv)
    integ[3 * n:] = 1
    bounds = Bounds(np.zeros(nv), np.ones(nv))
    try:
        res = milp(c, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=integ,
                   bounds=bounds, options={'time_limit': tlim, 'disp': False})
    except Exception:
        return None
    if res is None or res.x is None:
        return None
    x = res.x
    out = []
    for i in range(n):
        s = max(0.0, x[S(i)] - 1e-7)
        cx = min(max(x[X(i)] + x[S(i)] / 2, s / 2), 1 - s / 2)
        cy = min(max(x[Y(i)] + x[S(i)] / 2, s / 2), 1 - s / 2)
        out.append((cx, cy, 0.0, s))
    return out


def solve(n):
    if n <= 0:
        return []
    f, choice = _dp(n)
    out = []
    _build(n, 0.0, 0.0, 1.0, choice, out)
    out = [(min(max(a, 0.0), 1.0), min(max(b, 0.0), 1.0), 0.0, min(max(s, 0.0), 1.0))
           for (a, b, _, s) in out]
    best = out
    bestv = sum(s for *_, s in out) if _valid(out, n) else -1
    if bestv < 0:
        k = math.isqrt(n)
        side = 1.0 / k
        best = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        best += [(0.0, 0.0, 0.0, 0.0)] * (n - len(best))
        best = best[:n]
        bestv = sum(s for *_, s in best)
    if 2 <= n <= 12:
        res = _milp(n, bestv + 1e-4, 25.0)
        if res is not None and _valid(res, n, tol=1e-12):
            v = sum(s for *_, s in res)
            if v > bestv + 1e-6:
                best, bestv = res, v
    return best
# EVOLVE-BLOCK-END
