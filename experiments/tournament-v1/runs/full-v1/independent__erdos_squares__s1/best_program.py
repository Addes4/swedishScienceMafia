import math


def solve(n):
    if n <= 0:
        return []
    f = [0.0] * (n + 1)
    choice = [None] * (n + 1)
    f[1] = 1.0
    choice[1] = ('one',)
    for N in range(2, n + 1):
        best = f[N - 1]
        ch = ('pad',)
        K = math.isqrt(N) + 3
        for k in range(2, K + 1):
            kk = k * k
            for m in range(1, k):
                r = kk - m * m
                for j in range(1, N):
                    t = N - j
                    a, q1 = divmod(t, r)
                    cellv = (q1 * f[a + 1] if q1 else 0.0) + (r - q1) * f[a] if a + 1 <= N else 0.0
                    if a + 1 > N:
                        continue
                    v = (m / k) * f[j] + cellv / k
                    if v > best + 1e-12:
                        best = v
                        ch = ('grid', k, m, j)
        f[N] = best
        choice[N] = ch

    out = []
    shrink = 1.0 - 1e-9

    def build(cnt, ox, oy, s):
        if cnt <= 0:
            return
        c = choice[cnt]
        if c[0] == 'one':
            out.append((ox + s / 2, oy + s / 2, 0.0, s * shrink))
            return
        if c[0] == 'pad':
            build(cnt - 1, ox, oy, s)
            out.append((ox + s / 2, oy + s / 2, 0.0, 0.0))
            return
        _, k, m, j = c
        cs = s / k
        build(j, ox, oy, cs * m)
        cells = [(i, jj) for i in range(k) for jj in range(k) if not (i < m and jj < m)]
        r = len(cells)
        t = cnt - j
        a, q1 = divmod(t, r)
        for idx, (i, jj) in enumerate(cells):
            cc = a + 1 if idx < q1 else a
            build(cc, ox + i * cs, oy + jj * cs, cs)

    build(n, 0.0, 0.0, 1.0)
    res = []
    for (x, y, ang, sd) in out:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), ang, min(1.0, max(0.0, sd))))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
