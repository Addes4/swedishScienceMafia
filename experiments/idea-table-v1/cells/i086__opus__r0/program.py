# EVOLVE-BLOCK-START
"""GRASP + path relinking on integer m x m boards; best board scaled to unit square."""
import math
import random
import time


def _score(sqs, n):
    sides = sorted((s for _, _, s in sqs), reverse=True)
    return sum(sides[:n])


def _occ_from(sqs, m):
    occ = [[0] * m for _ in range(m)]
    for x, y, s in sqs:
        for yy in range(y, y + s):
            r = occ[yy]
            for xx in range(x, x + s):
                r[xx] = 1
    return occ


def _fill(occ, sqs, m, rng, cap, pg):
    for y in range(m):
        row = occ[y]
        for x in range(m):
            if row[x]:
                continue
            smax = 1
            lim = min(m - x, m - y, cap)
            while smax < lim:
                s = smax
                ok = True
                for yy in range(y, y + s + 1):
                    if occ[yy][x + s]:
                        ok = False
                        break
                if ok:
                    r = occ[y + s]
                    for xx in range(x, x + s):
                        if r[xx]:
                            ok = False
                            break
                if not ok:
                    break
                smax += 1
            s = smax if rng.random() < pg else rng.randint(1, smax)
            for yy in range(y, y + s):
                r = occ[yy]
                for xx in range(x, x + s):
                    r[xx] = 1
            sqs.append((x, y, s))
    return sqs


def _transform(sqs, m, t):
    out = []
    for x, y, s in sqs:
        if t & 1:
            x = m - x - s
        if t & 2:
            y = m - y - s
        if t & 4:
            x, y = y, x
        out.append((x, y, s))
    return out


def _repair_up(sqs, n):
    sqs = list(sqs)
    cnt = len(sqs)
    while cnt < n:
        room = n - cnt
        best = None
        for i, (x, y, s) in enumerate(sqs):
            if s < 2:
                continue
            if s % 2 == 0 and 3 <= room:
                cand = (s, -3, i, 0)
                if best is None or cand > best:
                    best = cand
            add = 2 * s - 1
            if add <= room:
                cand = (2 * s - 2, -add, i, 1)
                if best is None or cand > best:
                    best = cand
        if best is None:
            break
        _, negadd, i, typ = best
        x, y, s = sqs[i]
        sqs.pop(i)
        if typ == 0:
            h = s // 2
            sqs += [(x, y, h), (x + h, y, h), (x, y + h, h), (x + h, y + h, h)]
        else:
            sqs.append((x, y, s - 1))
            for t in range(s):
                sqs.append((x + s - 1, y + t, 1))
            for t in range(s - 1):
                sqs.append((x + t, y + s - 1, 1))
        cnt -= negadd
    return sqs


def _rand_rect(m, rng):
    w = rng.randint(1, m)
    h = rng.randint(1, m)
    x0 = rng.randint(0, m - w)
    y0 = rng.randint(0, m - h)
    return x0, y0, x0 + w, y0 + h


def _lns_move(sqs, m, rng):
    x0, y0, x1, y1 = _rand_rect(m, rng)
    kept = [q for q in sqs if not (q[0] < x1 and q[0] + q[2] > x0 and q[1] < y1 and q[1] + q[2] > y0)]
    occ = _occ_from(kept, m)
    cap = rng.randint(1, m)
    pg = rng.choice((1.0, 1.0, 0.8, 0.5))
    return _fill(occ, kept, m, rng, cap, pg)


def _ls(sqs, m, n, rng, tend, limit=30):
    cur = sqs
    cs = _score(cur, n)
    it = 0
    while it < limit and time.time() < tend:
        base = cur
        if rng.random() < 0.3:
            base = _transform(cur, m, rng.randint(1, 7))
        cand = _repair_up(_lns_move(base, m, rng), n)
        sc = _score(cand, n)
        if sc > cs:
            cur, cs, it = cand, sc, 0
        else:
            if sc == cs:
                cur = cand
            it += 1
    return cur


def _overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[2] and b[1] < a[1] + a[2]


def _relink(A, B, m, n, rng):
    cur = list(A)
    best, bs = cur, _score(cur, n)
    setA = set(A)
    diff = [b for b in B if b not in setA]
    if not diff:
        return best
    a, c = rng.uniform(-1, 1), rng.uniform(-1, 1)
    diff.sort(key=lambda q: a * q[0] + c * q[1])
    steps = 0
    while diff and steps < 60:
        steps += 1
        if rng.random() < 0.5:
            x0, y0, x1, y1 = _rand_rect(m, rng)
            chunk = [q for q in diff if q[0] >= x0 and q[1] >= y0 and q[0] + q[2] <= x1 and q[1] + q[2] <= y1]
            if not chunk:
                chunk = diff[:1]
        else:
            k = rng.randint(1, 3)
            chunk = diff[:k]
        cs = set(chunk)
        diff = [q for q in diff if q not in cs]
        kept = [q for q in cur if not any(_overlap(q, d) for d in chunk)]
        kept += chunk
        occ = _occ_from(kept, m)
        cur = _fill(occ, kept, m, rng, rng.randint(1, m), rng.choice((1.0, 0.7)))
        rep = _repair_up(cur, n)
        sc = _score(rep, n)
        if sc > bs:
            best, bs = rep, sc
    return best


def _search(m, n, rng, tend):
    elite = []
    keys = set()
    maxE = 12

    def add(sqs):
        key = tuple(sorted(sqs))
        if key in keys:
            return
        keys.add(key)
        elite.append((_score(sqs, n), key, sqs))
        elite.sort(key=lambda e: -e[0])
        while len(elite) > maxE:
            e = elite.pop()
            keys.discard(e[1])

    for cap in range(1, m + 1):
        if time.time() > tend and elite:
            break
        s = _fill([[0] * m for _ in range(m)], [], m, rng, cap, 1.0)
        s = _repair_up(s, n)
        add(s)
        add(_ls(s, m, n, rng, tend, 10))
    while time.time() < tend:
        if len(elite) < 2 or rng.random() < 0.3:
            s = _fill([[0] * m for _ in range(m)], [], m, rng, rng.randint(1, m),
                      rng.choice((1.0, 0.8, 0.5)))
            s = _repair_up(s, n)
            add(_ls(s, m, n, rng, tend))
        else:
            ea, eb = rng.sample(elite, 2)
            A = ea[2]
            B = eb[2]
            if rng.random() < 0.5:
                A, B = B, A
            r = _relink(A, B, m, n, rng)
            add(_ls(r, m, n, rng, tend))
    return elite[0][2]


def solve(n):
    if n <= 0:
        return []
    rng = random.Random(12345)
    k = max(1, math.isqrt(n))
    ms = list(range(k, min(2 * k + 4, max(k, 26)) + 1))
    total = 38.0
    wsum = sum(ms)
    t0 = time.time()
    best_val, best_m, best_sqs = -1.0, 1, [(0, 0, 1)]
    acc = 0.0
    for m in ms:
        acc += total * m / wsum
        tend = t0 + acc
        sqs = _search(m, n, rng, tend)
        val = _score(sqs, n) / m
        if val > best_val + 1e-12:
            best_val, best_m, best_sqs = val, m, sqs
    m = best_m
    chosen = sorted(best_sqs, key=lambda q: -q[2])[:n]
    out = []
    for x, y, s in chosen:
        side = s / m
        cx = (x + s / 2.0) / m
        cy = (y + s / 2.0) / m
        out.append((min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0), 0.0, side * (1 - 1e-12)))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]
# EVOLVE-BLOCK-END
