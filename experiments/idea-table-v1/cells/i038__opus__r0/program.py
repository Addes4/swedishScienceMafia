# EVOLVE-BLOCK-START
"""Recursive self-similar subdivision DP (grid / merged corner blocks + knapsack)."""
import math
import time
import numpy as np

NEG = -1e18


def solve(n):
    if n <= 0:
        return []
    t_start = time.time()
    F = np.zeros(n + 1)
    if n >= 1:
        F[1] = 1.0
    Hfin = np.full((n + 1, n + 1), NEG)
    Harg = np.zeros((n + 1, n + 1), dtype=int)
    Hfin[:, 0] = 0.0
    choice = [None] * (n + 1)
    choice[0] = ('none',)
    choice[1] = ('one',)
    HP = {}
    HPA = {}

    def finalize_col(N):
        ts = np.arange(N + 1)
        xs = N - ts
        for m in range(1, N + 1):
            prev = Hfin[np.minimum(m - 1, xs), xs]
            vals = F[ts] + prev
            i = int(np.argmax(vals))
            Hfin[m, N] = vals[i]
            Harg[m, N] = i

    if n >= 1:
        finalize_col(1)

    for N in range(2, n + 1):
        elapsed = time.time() - t_start
        hp = np.full(N + 1, NEG)
        hpa = np.zeros(N + 1, dtype=int)
        ts = np.arange(1, N)
        xs = N - ts
        for m in range(2, N + 1):
            vals = F[ts] + Hfin[np.minimum(m - 1, xs), xs]
            i = int(np.argmax(vals))
            if vals[i] >= hp[m - 1]:
                hp[m] = vals[i]
                hpa[m] = int(ts[i])
            else:
                hp[m] = hp[m - 1]
                hpa[m] = 0
        HP[N] = hp
        HPA[N] = hpa

        def HpG(m):
            return hp[min(m, N)]

        best = F[N - 1]
        ch = ('pad',)
        r = math.isqrt(N)
        K1 = 2 * r + 2 if elapsed < 30 else r + 2
        n0s = np.arange(1, N)
        xs0 = N - n0s
        for k in range(2, K1 + 1):
            v = HpG(k * k) / k
            if v > best + 1e-12:
                best = v
                ch = ('grid', k, 0, 0)
            if elapsed > 45:
                continue
            for j in range(2, k):
                m = k * k - j * j
                vals = j * F[n0s] + Hfin[np.minimum(m, xs0), xs0]
                i = int(np.argmax(vals))
                v = vals[i] / k
                if v > best + 1e-12:
                    best = v
                    ch = ('grid', k, j, int(n0s[i]))
                v = HpG(m) / k
                if v > best + 1e-12:
                    best = v
                    ch = ('grid', k, j, 0)
        if elapsed < 25:
            K2 = r + 3
            ar = np.arange(N)
            n0g = ar[:, None]
            n1g = ar[None, :]
            rem = N - n0g - n1g
            valid = rem >= 0
            remc = np.clip(rem, 0, N)
            for k in range(4, K2 + 1):
                for a in range(2, k - 1):
                    for b in range(2, min(a, k - a) + 1):
                        m = k * k - a * a - b * b
                        Hc = Hfin[np.minimum(m, remc), remc]
                        tot = a * F[n0g] + b * F[n1g] + Hc
                        tot = np.where(valid, tot, NEG)
                        tot[0, 0] = HpG(m)
                        idx = int(np.argmax(tot))
                        i0, i1 = divmod(idx, N)
                        v = tot[i0, i1] / k
                        if v > best + 1e-12:
                            best = v
                            ch = ('two', k, a, b, i0, i1)
        F[N] = best
        choice[N] = ch
        finalize_col(N)

    def dist_fin(m, x):
        res = []
        mm = min(m, x)
        while x > 0 and mm > 0:
            t = int(Harg[mm, x])
            res.append(t)
            x -= t
            mm = min(mm - 1, x)
        res += [0] * (m - len(res))
        return res

    def dist_prime(m, N):
        hpa = HPA[N]
        mm = min(m, N)
        while hpa[mm] == 0 and mm > 2:
            mm -= 1
        t = int(hpa[mm])
        res = [t] + dist_fin(min(mm - 1, N - t), N - t)
        res += [0] * (m - len(res))
        return res[:m] if len(res) > m else res

    out = []

    def build(N, x0, y0, s):
        if N <= 0:
            return
        c = choice[N]
        if c[0] == 'one':
            out.append((x0 + s / 2, y0 + s / 2, s))
            return
        if c[0] == 'pad':
            build(N - 1, x0, y0, s)
            return
        if c[0] == 'grid':
            _, k, j, n0 = c
            cs = s / k
            if j >= 2:
                build(n0, x0, y0, j * cs)
                cells = [(i, l) for i in range(k) for l in range(k) if not (i < j and l < j)]
            else:
                n0 = 0
                cells = [(i, l) for i in range(k) for l in range(k)]
            R = N - n0
            if R == N:
                counts = dist_prime(len(cells), N)
            else:
                counts = dist_fin(len(cells), R)
            for (i, l), cnt in zip(cells, counts):
                build(cnt, x0 + i * cs, y0 + l * cs, cs)
            return
        if c[0] == 'two':
            _, k, a, b, n0, n1 = c
            cs = s / k
            build(n0, x0, y0, a * cs)
            build(n1, x0 + (k - b) * cs, y0 + (k - b) * cs, b * cs)
            cells = [(i, l) for i in range(k) for l in range(k)
                     if not (i < a and l < a) and not (i >= k - b and l >= k - b)]
            R = N - n0 - n1
            if R == N:
                counts = dist_prime(len(cells), N)
            else:
                counts = dist_fin(len(cells), R)
            for (i, l), cnt in zip(cells, counts):
                build(cnt, x0 + i * cs, y0 + l * cs, cs)
            return

    build(n, 0.0, 0.0, 1.0)
    res = []
    for (cx, cy, s) in out[:n]:
        s2 = s * (1 - 1e-12)
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        res.append((cx, cy, 0.0, max(0.0, min(1.0, s2))))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res
# EVOLVE-BLOCK-END
