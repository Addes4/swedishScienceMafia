# EVOLVE-BLOCK-START
"""Guillotine DP over a lattice of rectangles (squares + axis-aligned cuts),
plus grid fallback with 2x2 merges / cell splits."""
import math
import numpy as np


def _dp(L, M):
    Fv = np.zeros((L + 1, L + 1, M + 1))
    chk = np.zeros((L + 1, L + 1, M + 1), dtype=np.int32)
    chc = np.zeros((L + 1, L + 1, M + 1), dtype=np.int32)
    chm = np.zeros((L + 1, L + 1, M + 1), dtype=np.int32)
    idxs = [np.arange(m + 1) for m in range(M + 1)]
    for a in range(1, L + 1):
        for b in range(1, L + 1):
            s = min(a, b)
            best = np.full(M + 1, float(s))
            best[0] = 0.0
            kinds = []
            cs = []
            a1x = []; a1y = []; a2x = []; a2y = []
            for c in range(1, a // 2 + 1):
                kinds.append(1); cs.append(c)
                a1x.append(c); a1y.append(b); a2x.append(a - c); a2y.append(b)
            for c in range(1, b // 2 + 1):
                kinds.append(2); cs.append(c)
                a1x.append(a); a1y.append(c); a2x.append(a); a2y.append(b - c)
            if kinds:
                P = Fv[a1x, a1y]
                Q = Fv[a2x, a2y]
                for m in range(1, M + 1):
                    I = idxs[m]
                    vals = P[:, I] + Q[:, m - I]
                    f = int(np.argmax(vals))
                    ci, ii = divmod(f, m + 1)
                    v = vals[ci, ii]
                    if v > best[m] + 1e-12:
                        best[m] = v
                        chk[a, b, m] = kinds[ci]
                        chc[a, b, m] = cs[ci]
                        chm[a, b, m] = ii
            Fv[a, b] = best
    return Fv, chk, chc, chm


def _dp_solve(n, L):
    Fv, chk, chc, chm = _dp(L, n)
    val = Fv[L, L, n] / L
    out = []
    stack = [(L, L, n, 0, 0)]
    while stack:
        a, b, m, x0, y0 = stack.pop()
        if m <= 0:
            continue
        k = chk[a, b, m]
        if k == 0:
            s = min(a, b)
            out.append(((x0 + s / 2.0) / L, (y0 + s / 2.0) / L, 0.0, s / L))
        else:
            c = int(chc[a, b, m]); m1 = int(chm[a, b, m])
            if k == 1:
                stack.append((c, b, m1, x0, y0))
                stack.append((a - c, b, m - m1, x0 + c, y0))
            else:
                stack.append((a, c, m1, x0, y0))
                stack.append((a, b - c, m - m1, x0, y0 + c))
    return val, out


def _fallback(n):
    k = max(1, math.isqrt(n))
    best = None
    # option A: k x k grid, split cells into 4 to gain count for free
    sqs = []
    r = n - k * k
    s = min(r // 3, k * k)
    cnt = 0
    for i in range(k):
        for j in range(k):
            if cnt < s:
                h = 0.5 / k
                for di in (0.25, 0.75):
                    for dj in (0.25, 0.75):
                        sqs.append(((i + di) / k, (j + dj) / k, 0.0, h))
                cnt += 1
            else:
                sqs.append(((i + 0.5) / k, (j + 0.5) / k, 0.0, 1.0 / k))
    best = (float(sum(q[3] for q in sqs[:n])), sqs[:n])
    # option B: (k+1) grid with merges and drops
    K = k + 1
    d = K * K - n
    if d >= 0:
        t = min(d // 3, (K // 2) ** 2)
        rest = d - 3 * t
        sq2 = []
        used = set()
        cntb = 0
        for i in range(K // 2):
            for j in range(K // 2):
                if cntb < t:
                    sq2.append(((2 * i + 1.0) / K, (2 * j + 1.0) / K, 0.0, 2.0 / K))
                    used.add((2 * i, 2 * j)); used.add((2 * i + 1, 2 * j))
                    used.add((2 * i, 2 * j + 1)); used.add((2 * i + 1, 2 * j + 1))
                    cntb += 1
        cells = [(i, j) for i in range(K) for j in range(K) if (i, j) not in used]
        if rest <= len(cells):
            cells = cells[:len(cells) - rest]
            for (i, j) in cells:
                sq2.append(((i + 0.5) / K, (j + 0.5) / K, 0.0, 1.0 / K))
            if len(sq2) <= n:
                v = float(sum(q[3] for q in sq2))
                if v > best[0]:
                    best = (v, sq2)
    return best


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    cands = [_fallback(n)]
    L = None
    if n <= 24:
        L = 60
    elif n <= 40:
        L = 24
    elif n <= 70:
        L = 12
    if L is not None:
        try:
            cands.append(_dp_solve(n, L))
        except Exception:
            pass
    val, sqs = max(cands, key=lambda c: c[0])
    sqs = list(sqs)[:n]
    sqs += [(0.5, 0.5, 0.0, 0.0)] * (n - len(sqs))
    res = []
    for (x, y, an, s) in sqs:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), an, min(1.0, max(0.0, s))))
    return res
# EVOLVE-BLOCK-END
