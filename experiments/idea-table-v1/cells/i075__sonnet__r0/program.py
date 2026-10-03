# EVOLVE-BLOCK-START
"""Recursive block-grid construction: k x k grid whose cells are merged into
aligned m x m blocks (L-frames are a special case); each block/cell is filled
recursively. Counts are distributed by a max-plus knapsack."""
import math
import time
import numpy as np

_TIL = {}


def _tilings(k):
    if k in _TIL:
        return _TIL[k]
    seen = {}
    if k <= 5:
        grid = [[0] * k for _ in range(k)]
        blocks = []
        cnt = [0]

        def rec():
            cnt[0] += 1
            if cnt[0] > 300000:
                return
            pos = None
            for r in range(k):
                for c in range(k):
                    if grid[r][c] == 0:
                        pos = (r, c)
                        break
                if pos:
                    break
            if pos is None:
                key = tuple(sorted(b[2] for b in blocks))
                if key not in seen:
                    seen[key] = list(blocks)
                return
            r, c = pos
            m = 1
            while m < k and r + m <= k and c + m <= k:
                if any(grid[r + i][c + m - 1] for i in range(m)) or any(grid[r + m - 1][c + j] for j in range(m)):
                    break
                for i in range(m):
                    for j in range(m):
                        grid[r + i][c + j] = 1
                blocks.append((r, c, m))
                rec()
                blocks.pop()
                for i in range(m):
                    for j in range(m):
                        grid[r + i][c + j] = 0
                m += 1
                if r + m > k or c + m > k:
                    break
        rec()
    else:
        for m in range(2, k):
            for m2 in [0] + list(range(2, k - m + 1)):
                bl = [(0, 0, m)]
                if m2:
                    bl.append((k - m2, k - m2, m2))
                occ = [[0] * k for _ in range(k)]
                for (r, c, mm) in bl:
                    for i in range(mm):
                        for j in range(mm):
                            occ[r + i][c + j] = 1
                for r in range(k):
                    for c in range(k):
                        if not occ[r][c]:
                            bl.append((r, c, 1))
                key = tuple(sorted(b[2] for b in bl))
                if key not in seen:
                    seen[key] = bl
    res = list(seen.values())
    _TIL[k] = res
    return res


def _knap(sizes, k, f, N, track):
    dp = np.zeros(N + 1)
    args = []
    for m in sizes:
        h = f[:N + 1] * (m / k)
        new = dp.copy()
        arg = np.zeros(N + 1, dtype=int) if track else None
        for a in range(1, N + 1):
            cand = dp[:N + 1 - a] + h[a]
            seg = new[a:]
            if track:
                mask = cand > seg + 1e-15
                view = arg[a:]
                view[mask] = a
            np.maximum(seg, cand, out=seg)
        dp = new
        args.append(arg)
    return dp, args


def _grid_choice(n):
    hi = math.isqrt(n)
    if hi * hi < n:
        hi += 1
    lo = max(1, math.isqrt(n))
    vh = n / hi
    vl = float(lo)
    if vh >= vl:
        return vh, ('grid', hi)
    return vl, ('grid', lo)


def solve(n):
    if n <= 0:
        return []
    t0 = time.time()
    N = n
    f0 = np.zeros(N + 1)
    ch0 = {}
    for j in range(1, N + 1):
        v, c = _grid_choice(j)
        f0[j] = v
        ch0[j] = c
    for j in range(2, N + 1):
        if f0[j] < f0[j - 1]:
            f0[j] = f0[j - 1]
            ch0[j] = ('less',)
    F = [f0]
    CH = [ch0]
    kmax = 8
    for p in range(1, 5):
        fprev = F[-1]
        fnew = fprev.copy()
        chn = dict(CH[-1])
        changed = False
        stop = False
        for k in range(2, kmax + 1):
            if stop:
                break
            for idx, lay in enumerate(_tilings(k)):
                if time.time() - t0 > 35:
                    stop = True
                    break
                sizes = [b[2] for b in lay]
                dp, _ = _knap(sizes, k, fprev, N, False)
                for j in range(1, N + 1):
                    if dp[j] > fnew[j] + 1e-12:
                        fnew[j] = dp[j]
                        chn[j] = ('til', p, k, idx)
                        changed = True
        for j in range(2, N + 1):
            if fnew[j] < fnew[j - 1] - 1e-12:
                fnew[j] = fnew[j - 1]
                chn[j] = ('less',)
        F.append(fnew)
        CH.append(chn)
        if not changed or stop:
            break

    def pad(lst, m):
        return lst + [(0.5, 0.5, 0.0, 0.0)] * (m - len(lst))

    def build(m, p):
        if m <= 0:
            return []
        ch = CH[p][m]
        if ch[0] == 'grid':
            k = ch[1]
            out = []
            s = 1.0 / k
            for r in range(k):
                for c in range(k):
                    if len(out) < m:
                        out.append(((c + 0.5) * s, (r + 0.5) * s, 0.0, s))
            return pad(out, m)
        if ch[0] == 'less':
            return pad(build(m - 1, p), m)
        _, q, k, idx = ch
        lay = _tilings(k)[idx]
        sizes = [b[2] for b in lay]
        dp, args = _knap(sizes, k, F[q - 1], m, True)
        j = m
        alloc = [0] * len(sizes)
        for bi in range(len(sizes) - 1, -1, -1):
            a = int(args[bi][j])
            alloc[bi] = a
            j -= a
        out = []
        for bi, (r, c, mm) in enumerate(lay):
            if alloc[bi] <= 0:
                continue
            sub = build(alloc[bi], q - 1)
            x0 = c / k
            y0 = r / k
            sz = mm / k
            for (cx, cy, ang, sd) in sub:
                out.append((x0 + sz * cx, y0 + sz * cy, ang, sz * sd))
        return pad(out, m)

    res = build(n, len(CH) - 1)
    final = []
    for (cx, cy, ang, sd) in res[:n]:
        sd2 = sd * (1 - 1e-9)
        cx = min(1.0, max(0.0, cx))
        cy = min(1.0, max(0.0, cy))
        final.append((cx, cy, ang, max(0.0, sd2)))
    return final
# EVOLVE-BLOCK-END
