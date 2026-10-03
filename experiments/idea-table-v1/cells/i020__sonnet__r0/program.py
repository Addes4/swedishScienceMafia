import math


def _grid(k):
    s = 1.0 / k
    return [(i * s, j * s, s) for i in range(k) for j in range(k)]


def _merge(k, j):
    s = 1.0 / k
    res = [(0.0, 0.0, j * s)]
    for a in range(k):
        for b in range(k):
            if a < j and b < j:
                continue
            res.append((a * s, b * s, s))
    return res


def _subst(layout, idx, sub):
    x, y, s = layout[idx]
    res = layout[:idx] + layout[idx + 1:]
    for (a, b, t) in sub:
        res.append((x + a * s, y + b * s, t * s))
    return res


def _pick(layout):
    # indices of largest and smallest positive-side squares
    mx = -1
    mn = -1
    for i, (_, _, s) in enumerate(layout):
        if s <= 1e-12:
            continue
        if mx < 0 or s > layout[mx][2]:
            mx = i
        if mn < 0 or s < layout[mn][2]:
            mn = i
    return mx, mn


def solve(n):
    total = [0.0] * (n + 1)
    lay = [None] * (n + 1)
    picks = [None] * (n + 1)

    def store(N, L):
        lay[N] = L
        total[N] = sum(t for (_, _, t) in L)
        picks[N] = _pick(L)

    for N in range(1, n + 1):
        cands = []  # (value, kind, data)
        k = math.isqrt(N)
        if k * k == N:
            cands.append((float(k), 'grid', k))
        for kk in range(2, N + 2):
            if kk * kk - (kk - 1) ** 2 + 1 > N:
                break
            for j in range(2, kk):
                if kk * kk - j * j + 1 == N:
                    cands.append(((kk * kk - j * j + j) / kk, 'merge', (kk, j)))
        if N > 1:
            cands.append((total[N - 1], 'pad', None))
        for m in range(2, N):
            base = N - m + 1
            if base < 1 or lay[base] is None:
                continue
            seen = set()
            for idx in picks[base]:
                if idx < 0 or idx in seen:
                    continue
                seen.add(idx)
                s = lay[base][idx][2]
                v = total[base] - s + s * total[m]
                cands.append((v, 'sub', (base, idx, m)))
        best = max(cands, key=lambda c: c[0])
        kind, data = best[1], best[2]
        if kind == 'grid':
            L = _grid(data)
        elif kind == 'merge':
            L = _merge(*data)
        elif kind == 'pad':
            L = lay[N - 1] + [(0.0, 0.0, 0.0)]
        else:
            base, idx, m = data
            L = _subst(lay[base], idx, lay[m])
        store(N, L)

    out = []
    eps = 1e-9
    for (x, y, s) in lay[n]:
        s2 = s * (1 - eps)
        cx = x + s / 2
        cy = y + s / 2
        cx = min(1.0, max(0.0, cx))
        cy = min(1.0, max(0.0, cy))
        out.append((cx, cy, 0.0, min(1.0, max(0.0, s2))))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out[:n]
