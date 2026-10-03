# EVOLVE-BLOCK-START
import math
import time
import random
import numpy as np

try:
    from scipy.optimize import linprog
except Exception:  # pragma: no cover
    linprog = None


def _grid_dp(N, M):
    NEG = -1e18
    K = np.empty((N + 1, N + 1), dtype=np.int64)
    for c in range(N + 1):
        for c1 in range(N + 1):
            K[c, c1] = c - c1 if c >= c1 else N + 1
    g = {}
    typ = {}
    pos = {}
    arg = {}
    for w in range(1, M + 1):
        for h in range(1, M + 1):
            best = np.zeros(N + 1)
            t = np.zeros(N + 1, dtype=np.int64)
            p = np.zeros(N + 1, dtype=np.int64)
            a1 = np.zeros(N + 1, dtype=np.int64)
            if w == h and N >= 1:
                best[1:] = w
                t[1:] = 1
            for k in range(1, w // 2 + 1):
                a = g[(k, h)]
                b = np.append(g[(w - k, h)], NEG)
                S = a[None, :] + b[K]
                val = S.max(1)
                am = S.argmax(1)
                m = val > best + 1e-9
                if m.any():
                    best[m] = val[m]; t[m] = 2; p[m] = k; a1[m] = am[m]
            for k in range(1, h // 2 + 1):
                a = g[(w, k)]
                b = np.append(g[(w, h - k)], NEG)
                S = a[None, :] + b[K]
                val = S.max(1)
                am = S.argmax(1)
                m = val > best + 1e-9
                if m.any():
                    best[m] = val[m]; t[m] = 3; p[m] = k; a1[m] = am[m]
            g[(w, h)] = best
            typ[(w, h)] = t
            pos[(w, h)] = p
            arg[(w, h)] = a1
    return g, typ, pos, arg


def _reconstruct(typ, pos, arg, x, y, w, h, c, out):
    if c <= 0:
        return
    t = typ[(w, h)][c]
    if t == 1:
        out.append((x, y, w))
    elif t == 2:
        k = int(pos[(w, h)][c]); c1 = int(arg[(w, h)][c])
        _reconstruct(typ, pos, arg, x, y, k, h, c1, out)
        _reconstruct(typ, pos, arg, x + k, y, w - k, h, c - c1, out)
    elif t == 3:
        k = int(pos[(w, h)][c]); c1 = int(arg[(w, h)][c])
        _reconstruct(typ, pos, arg, x, y, w, k, c1, out)
        _reconstruct(typ, pos, arg, x, y + k, w, h - k, c - c1, out)


def _valid(X, Y, S, tol=0.0):
    n = len(S)
    if np.any(S < 0) or np.any(X < -tol) or np.any(Y < -tol):
        return False
    if np.any(X + S > 1 + tol) or np.any(Y + S > 1 + tol):
        return False
    for i in range(n):
        if S[i] <= 0:
            continue
        for j in range(i + 1, n):
            if S[j] <= 0:
                continue
            ox = min(X[i] + S[i], X[j] + S[j]) - max(X[i], X[j])
            oy = min(Y[i] + S[i], Y[j] + S[j]) - max(Y[i], Y[j])
            if ox > tol and oy > tol:
                return False
    return True


def _gap_fill(X, Y, S):
    X = X.copy(); Y = Y.copy(); S = S.copy()
    zeros = [i for i in range(len(S)) if S[i] <= 1e-12]
    for z in zeros:
        act = S > 1e-12
        ax, ay, as_ = X[act], Y[act], S[act]
        xs = np.unique(np.concatenate(([0.0], ax + as_)))
        ys = np.unique(np.concatenate(([0.0], ay + as_)))
        cx, cy = np.meshgrid(xs, ys)
        cx = cx.ravel(); cy = cy.ravel()
        lim = np.minimum(1 - cx, 1 - cy)
        if len(ax):
            # blocking squares
            right = (ax + as_)[None, :] > cx[:, None] + 1e-12
            top = (ay + as_)[None, :] > cy[:, None] + 1e-12
            blk = right & top
            v = np.maximum(ax[None, :] - cx[:, None], ay[None, :] - cy[:, None])
            v = np.where(blk, v, 2.0)
            lim = np.minimum(lim, v.min(1))
        lim = np.maximum(lim, 0)
        b = int(np.argmax(lim))
        if lim[b] > 1e-9:
            X[z] = cx[b]; Y[z] = cy[b]; S[z] = lim[b]
        else:
            X[z] = 0.0; Y[z] = 0.0; S[z] = 0.0
    return X, Y, S


def _lp(X, Y, S):
    n = len(S)
    if linprog is None or n == 0:
        return None
    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            gaps = [X[j] - (X[i] + S[i]), X[i] - (X[j] + S[j]),
                    Y[j] - (Y[i] + S[i]), Y[i] - (Y[j] + S[j])]
            d = int(np.argmax(gaps))
            r = np.zeros(3 * n)
            if d == 0:
                r[i] = 1; r[2 * n + i] = 1; r[j] = -1
            elif d == 1:
                r[j] = 1; r[2 * n + j] = 1; r[i] = -1
            elif d == 2:
                r[n + i] = 1; r[2 * n + i] = 1; r[n + j] = -1
            else:
                r[n + j] = 1; r[2 * n + j] = 1; r[n + i] = -1
            rows.append(r)
    for i in range(n):
        r = np.zeros(3 * n); r[i] = 1; r[2 * n + i] = 1; rows.append(r)
        r = np.zeros(3 * n); r[n + i] = 1; r[2 * n + i] = 1; rows.append(r)
    A = np.array(rows)
    b = np.zeros(len(rows))
    b[-2 * n:] = 1.0
    c = np.zeros(3 * n); c[2 * n:] = -1
    try:
        res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, 1)] * (3 * n), method="highs")
    except Exception:
        return None
    if res.status != 0:
        return None
    v = res.x
    Xn, Yn, Sn = v[:n].copy(), v[n:2 * n].copy(), np.maximum(v[2 * n:], 0).copy()
    Sn = np.where(Sn < 1e-11, 0.0, Sn)
    # small shrink for safety
    shr = np.where(Sn > 0, 2e-11, 0.0)
    Xn = Xn + shr / 2; Yn = Yn + shr / 2; Sn = Sn - shr
    Sn = np.maximum(Sn, 0)
    return Xn, Yn, Sn


def solve(n):
    if n <= 0:
        return []
    t0 = time.time()
    M = min(max(8, int(3 * math.sqrt(n)) + 6), 30)
    g, typ, pos, arg = _grid_dp(n, M)
    bestm, bestv = 1, -1
    for m in range(1, M + 1):
        v = g[(m, m)][n] / m
        if v > bestv + 1e-12:
            bestv, bestm = v, m
    out = []
    _reconstruct(typ, pos, arg, 0, 0, bestm, bestm, n, out)
    m = bestm
    X = np.zeros(n); Y = np.zeros(n); S = np.zeros(n)
    for idx, (x, y, w) in enumerate(out[:n]):
        X[idx] = x / m; Y[idx] = y / m; S[idx] = w / m
    best = (X.copy(), Y.copy(), S.copy())
    bsum = S.sum()

    # Gap-filling + LP polishing with random perturbations
    rng = random.Random(12345)
    cur = best
    budget = 8.0
    it = 0
    while time.time() - t0 < budget and linprog is not None:
        it += 1
        Xc, Yc, Sc = cur[0].copy(), cur[1].copy(), cur[2].copy()
        if it > 1:
            pos_idx = [i for i in range(n) if Sc[i] > 0]
            if pos_idx:
                for _ in range(rng.randint(1, 2)):
                    i = rng.choice(pos_idx)
                    Sc[i] = 0.0
        Xc, Yc, Sc = _gap_fill(Xc, Yc, Sc)
        r = _lp(Xc, Yc, Sc)
        if r is None:
            continue
        Xn, Yn, Sn = r
        Xn, Yn, Sn = _gap_fill(Xn, Yn, Sn)
        if not _valid(Xn, Yn, Sn, tol=0.0):
            continue
        tot = Sn.sum()
        if tot > bsum + 1e-7:
            best = (Xn, Yn, Sn); bsum = tot
            cur = best
        elif tot > cur[2].sum() - 1e-9 or rng.random() < 0.2:
            cur = (Xn, Yn, Sn)
        else:
            cur = best

    X, Y, S = best
    res = []
    for i in range(n):
        s = float(S[i])
        if s <= 0:
            res.append((0.0, 0.0, 0.0, 0.0))
        else:
            cx = min(max(float(X[i] + s / 2), 0.0), 1.0)
            cy = min(max(float(Y[i] + s / 2), 0.0), 1.0)
            res.append((cx, cy, 0.0, min(s, 1.0)))
    return res
# EVOLVE-BLOCK-END
