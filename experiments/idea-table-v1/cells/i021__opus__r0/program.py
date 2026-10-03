# EVOLVE-BLOCK-START
"""Erdos-Soifer style constructions (k x k grid with corner blocks re-gridded),
over-built and then trimmed by deleting the smallest squares."""
import math


def _build(k, a1, b1, a2, b2):
    u = 1.0 / k
    sq = []
    for i in range(k):
        for j in range(k):
            if i < a1 and j < a1:
                continue
            if i >= k - a2 and j >= k - a2:
                continue
            sq.append(((i + 0.5) * u, (j + 0.5) * u, 0.0, u))
    if a1 > 0 and b1 > 0:
        s = a1 * u / b1
        for i in range(b1):
            for j in range(b1):
                sq.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
    if a2 > 0 and b2 > 0:
        s = a2 * u / b2
        off = 1.0 - a2 * u
        for i in range(b2):
            for j in range(b2):
                sq.append((off + (i + 0.5) * s, off + (j + 0.5) * s, 0.0, s))
    return sq


def _valid(sq):
    eps = 1e-12
    for (x, y, _, s) in sq:
        if s < 0 or x - s / 2 < -eps or x + s / 2 > 1 + eps or y - s / 2 < -eps or y + s / 2 > 1 + eps:
            return False
    m = len(sq)
    for p in range(m):
        x1, y1, _, s1 = sq[p]
        if s1 <= 0:
            continue
        for q in range(p + 1, m):
            x2, y2, _, s2 = sq[q]
            if s2 <= 0:
                continue
            if abs(x1 - x2) < (s1 + s2) / 2 - 1e-9 and abs(y1 - y2) < (s1 + s2) / 2 - 1e-9:
                return False
    return True


def _top_sum(groups, n):
    groups = sorted(groups, key=lambda g: -g[0])
    tot = 0.0
    left = n
    for s, c in groups:
        if left <= 0:
            break
        t = c if c < left else left
        tot += s * t
        left -= t
    return tot


def solve(n):
    if n <= 0:
        return []
    r = math.isqrt(n)
    maxN = n + 2 * r + 2 + max(0, 6 - r)
    cands = []
    for k in range(max(1, r - 3), r + 4):
        for a1 in range(0, k + 1):
            b1s = sorted(set([0] + [b for b in range(max(0, a1 - 3), a1 + 4)])) if a1 > 0 else [0]
            for a2 in range(0, k - a1 + 1):
                if a2 > a1:
                    continue
                b2s = sorted(set([0] + [b for b in range(max(0, a2 - 3), a2 + 4)])) if a2 > 0 else [0]
                base = k * k - a1 * a1 - a2 * a2
                for b1 in b1s:
                    for b2 in b2s:
                        cnt = base + b1 * b1 + b2 * b2
                        if cnt > maxN:
                            continue
                        groups = [(1.0 / k, base)]
                        if a1 > 0 and b1 > 0:
                            groups.append((a1 / (k * b1), b1 * b1))
                        if a2 > 0 and b2 > 0:
                            groups.append((a2 / (k * b2), b2 * b2))
                        val = _top_sum(groups, n)
                        cands.append((val, k, a1, b1, a2, b2))
    cands.sort(key=lambda c: -c[0])
    best = None
    for c in cands[:50]:
        _, k, a1, b1, a2, b2 = c
        sq = _build(k, a1, b1, a2, b2)
        sq.sort(key=lambda t: -t[3])
        sq = sq[:n]
        if _valid(sq):
            best = sq
            break
    if best is None:
        k = max(1, r)
        best = _build(k, 0, 0, 0, 0)[:n]
    best = list(best)
    while len(best) < n:
        best.append((0.0, 0.0, 0.0, 0.0))
    # clamp to [0,1]
    out = []
    for (x, y, a, s) in best:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), a, min(1.0, max(0.0, s))))
    return out
# EVOLVE-BLOCK-END
