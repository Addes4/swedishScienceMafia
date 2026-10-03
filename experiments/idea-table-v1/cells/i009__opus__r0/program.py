# EVOLVE-BLOCK-START
import math
import time
import random
import numpy as np


def _dp(n, t0, budget):
    M = n + 1
    Kcap = int(4 * math.sqrt(n)) + 12
    F = np.zeros((Kcap + 1, Kcap + 1, M))
    CHC = np.full((Kcap + 1, Kcap + 1, M), -1, dtype=np.int64)
    CHI = np.zeros((Kcap + 1, Kcap + 1, M), dtype=np.int64)
    ar = np.arange(M)
    idx = ar[None, :] - ar[:, None]  # [i, m] = m - i
    valid = idx >= 0
    idxc = np.where(valid, idx, 0)

    def get(a, b):
        return F[a, b] if a <= b else F[b, a]

    Kdone = 0
    for s in range(1, Kcap + 1):
        if s > 2 and time.time() - t0 > budget:
            break
        for w in range(1, s + 1):
            h = s
            base = np.full(M, float(w))
            base[0] = 0.0
            Ls, Rs = [], []
            for a in range(1, w // 2 + 1):
                Ls.append(get(a, h))
                Rs.append(get(w - a, h))
            for b in range(1, h // 2 + 1):
                Ls.append(get(w, b))
                Rs.append(get(w, h - b))
            if Ls:
                L = np.array(Ls)
                R = np.array(Rs)
                T = L[:, :, None] + R[:, idxc]
                T = np.where(valid[None], T, -1e18)
                T2 = T.reshape(-1, M)
                am = T2.argmax(0)
                val = T2[am, ar]
                better = val > base + 1e-9
                res = np.where(better, val, base)
                CHC[w, h] = np.where(better, am // M, -1)
                CHI[w, h] = np.where(better, am % M, 0)
            else:
                res = base
            F[w, h] = res
        Kdone = s
    return F, CHC, CHI, Kdone


def _reconstruct(F, CHC, CHI, w, h, m):
    if m <= 0 or w <= 0 or h <= 0:
        return []
    if w > h:
        return [(y, x, s) for (x, y, s) in _reconstruct(F, CHC, CHI, h, w, m)]
    c = int(CHC[w, h, m])
    if c == -1:
        return [(0, 0, w)]
    i = int(CHI[w, h, m])
    nv = w // 2
    if c < nv:
        a = c + 1
        left = _reconstruct(F, CHC, CHI, a, h, i)
        right = _reconstruct(F, CHC, CHI, w - a, h, m - i)
        return left + [(x + a, y, s) for (x, y, s) in right]
    b = c - nv + 1
    bot = _reconstruct(F, CHC, CHI, w, b, i)
    top = _reconstruct(F, CHC, CHI, w, h - b, m - i)
    return bot + [(x, y + b, s) for (x, y, s) in top]


def _anneal(K, init, n, tlimit, rng):
    grid = [[-1] * K for _ in range(K)]
    sq = {}
    nid = 0
    for (x, y, s) in init:
        sq[nid] = [x, y, s]
        for i in range(x, x + s):
            for j in range(y, y + s):
                grid[i][j] = nid
        nid += 1
    cur = sum(v[2] for v in sq.values())
    best = cur
    best_sq = [tuple(v) for v in sq.values()]

    def free(x, y, s, own):
        if x < 0 or y < 0 or x + s > K or y + s > K:
            return False
        for i in range(x, x + s):
            row = grid[i]
            for j in range(y, y + s):
                g = row[j]
                if g != -1 and g != own:
                    return False
        return True

    def paint(x, y, s, v):
        for i in range(x, x + s):
            row = grid[i]
            for j in range(y, y + s):
                row[j] = v

    T0, T1 = 1.0, 0.03
    start = time.time()
    it = 0
    T = T0
    while True:
        it += 1
        if (it & 255) == 0:
            el = time.time() - start
            if el > tlimit:
                break
            T = T0 * (T1 / T0) ** (el / tlimit)
        r = rng.random()
        cnt = len(sq)
        if cnt == 0 or (r < 0.12 and cnt < n):
            # add 1x1 square
            x = rng.randrange(K); y = rng.randrange(K)
            if grid[x][y] == -1 and cnt < n:
                sq[nid] = [x, y, 1]
                grid[x][y] = nid
                nid += 1
                cur += 1
            continue
        k = rng.choice(list(sq.keys()))
        x, y, s = sq[k]
        if r < 0.40:
            nx = x - rng.randrange(2); ny = y - rng.randrange(2); ns = s + 1
        elif r < 0.65:
            d = rng.randrange(4)
            nx = x + (1, -1, 0, 0)[d]; ny = y + (0, 0, 1, -1)[d]; ns = s
        elif r < 0.85:
            ns = s - 1
            nx = x + rng.randrange(2); ny = y + rng.randrange(2)
        elif r < 0.93:
            ns = 0; nx = x; ny = y
        else:
            # split
            if s % 2 == 0 and s >= 2 and cnt + 3 <= n:
                t = s // 2
                paint(x, y, s, -1)
                del sq[k]
                for (dx, dy) in ((0, 0), (t, 0), (0, t), (t, t)):
                    sq[nid] = [x + dx, y + dy, t]
                    paint(x + dx, y + dy, t, nid)
                    nid += 1
                cur += s
                if cur > best:
                    best = cur
                    best_sq = [tuple(v) for v in sq.values()]
            continue
        delta = ns - s
        if delta < 0 and rng.random() >= math.exp(delta / T):
            continue
        if ns <= 0:
            paint(x, y, s, -1)
            del sq[k]
            cur -= s
            continue
        if not free(nx, ny, ns, k):
            continue
        paint(x, y, s, -1)
        paint(nx, ny, ns, k)
        sq[k] = [nx, ny, ns]
        cur += delta
        if cur > best:
            best = cur
            best_sq = [tuple(v) for v in sq.values()]
    return best, best_sq


def solve(n):
    if n <= 0:
        return []
    t0 = time.time()
    F, CHC, CHI, Kdone = _dp(n, t0, 20.0)
    cands = []
    for K in range(1, Kdone + 1):
        cands.append((F[K, K, n] / K, K))
    cands.sort(reverse=True)
    bestv, bestK = cands[0]
    best_sq = _reconstruct(F, CHC, CHI, bestK, bestK, n)

    rng = random.Random(12345)
    tops = [K for _, K in cands[:3]]
    for K in tops:
        init = _reconstruct(F, CHC, CHI, K, K, n)
        if len(init) > n:
            continue
        val, sqs = _anneal(K, init, n, 2.0, rng)
        if val / K > bestv + 1e-12 and len(sqs) <= n:
            bestv, bestK, best_sq = val / K, K, sqs

    K = bestK
    out = []
    for (x, y, s) in best_sq[:n]:
        out.append(((x + s / 2.0) / K, (y + s / 2.0) / K, 0.0, s / K))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
