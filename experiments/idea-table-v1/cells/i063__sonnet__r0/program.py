import math
import time
import numpy as np


def _dp(m, n):
    K = min(n, m * m)
    val = {}
    ch = {}
    for a in range(1, m + 1):
        for b in range(1, m + 1):
            v = np.full(K + 1, float(min(a, b)))
            v[0] = 0.0
            t = np.zeros(K + 1, dtype=np.int8)   # 0 square, 1 cut along a, 2 cut along b
            cc = np.zeros(K + 1, dtype=np.int32)
            kk = np.zeros(K + 1, dtype=np.int32)
            for axis in (1, 2):
                L = a if axis == 1 else b
                for c in range(1, L // 2 + 1):
                    if axis == 1:
                        V1 = val[(c, b)]
                        V2 = val[(a - c, b)]
                    else:
                        V1 = val[(a, c)]
                        V2 = val[(a, b - c)]
                    for k1 in range(1, K):
                        ks = np.arange(k1 + 1, K + 1)
                        cand = V1[k1] + V2[1:K - k1 + 1]
                        cur = v[k1 + 1:]
                        mask = cand > cur + 1e-12
                        if mask.any():
                            idx = ks[mask]
                            v[idx] = cand[mask]
                            t[idx] = axis
                            cc[idx] = c
                            kk[idx] = k1
            val[(a, b)] = v
            ch[(a, b)] = (t, cc, kk)
    return val, ch, K


def _build(m, ch, a, b, k, x, y, out):
    if k <= 0:
        return
    t, cc, kk = ch[(a, b)]
    ty = int(t[k])
    if ty == 0:
        s = min(a, b)
        out.append(((x + s / 2.0) / m, (y + s / 2.0) / m, 0.0, s / m))
        return
    c = int(cc[k])
    k1 = int(kk[k])
    if ty == 1:
        _build(m, ch, c, b, k1, x, y, out)
        _build(m, ch, a - c, b, k - k1, x + c, y, out)
    else:
        _build(m, ch, a, c, k1, x, y, out)
        _build(m, ch, a, b - c, k - k1, x, y + c, out)


def solve(n):
    t0 = time.time()
    best = None
    bestv = -1.0
    k0 = max(1, math.isqrt(n))
    for m in range(1, 17):
        if time.time() - t0 > 30 and m > k0:
            break
        val, ch, K = _dp(m, n)
        v = val[(m, m)][K] / m
        if v > bestv + 1e-12:
            bestv = v
            best = (m, ch, K)
    m, ch, K = best
    out = []
    _build(m, ch, m, m, K, 0, 0, out)
    out = out[:n]
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    res = []
    for (x, y, ang, s) in out:
        res.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), ang, min(1.0, max(0.0, s))))
    return res
