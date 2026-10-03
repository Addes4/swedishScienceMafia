# EVOLVE-BLOCK-START
"""Genetic algorithm over side multisets/orderings with a skyline bottom-left-fill decoder."""
import math
import random
import time

EPS = 1e-9


def _decode(genes):
    """Skyline placement. Returns (total, placements) placements aligned with genes
    (None where square did not fit)."""
    segs = [(0.0, 1.0, 0.0)]  # (x, w, y)
    total = 0.0
    out = []
    for s in genes:
        if s <= 0:
            out.append(None)
            continue
        best = None
        m = len(segs)
        for i in range(m):
            sx, sw, sy = segs[i]
            for x in (sx, sx + sw - s):
                if x < -EPS or x + s > 1 + EPS:
                    continue
                if x < 0:
                    x = 0.0
                # find max height over [x, x+s]
                y = 0.0
                for j in range(m):
                    jx, jw, jy = segs[j]
                    if jx + jw <= x + EPS:
                        continue
                    if jx >= x + s - EPS:
                        break
                    if jy > y:
                        y = jy
                if y + s <= 1 + EPS:
                    if best is None or y < best[0] - EPS or (abs(y - best[0]) <= EPS and x < best[1]):
                        best = (y, x)
        if best is None:
            out.append(None)
            continue
        y, x = best
        out.append((x, y))
        total += s
        # update skyline
        new = []
        x2 = x + s
        for (sx, sw, sy) in segs:
            e = sx + sw
            if e <= x + EPS or sx >= x2 - EPS:
                new.append((sx, sw, sy))
                continue
            if sx < x - EPS:
                new.append((sx, x - sx, sy))
            if e > x2 + EPS:
                new.append((x2, e - x2, sy))
        new.append((x, s, y + s))
        new.sort()
        merged = []
        for seg in new:
            if merged and abs(merged[-1][2] - seg[2]) < EPS and abs(merged[-1][0] + merged[-1][1] - seg[0]) < EPS:
                px, pw, py = merged[-1]
                merged[-1] = (px, pw + seg[1], py)
            else:
                merged.append(seg)
        segs = merged
    return total, out


def solve(n):
    t0 = time.time()
    budget = 35.0
    rng = random.Random(12345 + n)
    Q = min(30, max(10, 2 * math.isqrt(n) + 2))

    def rand_gene():
        q = rng.randint(1, Q)
        if rng.random() < 0.75:
            return 1.0 / q
        p = rng.randint(1, q)
        return p / q

    cache = {}

    def fit(ch):
        key = tuple(ch)
        v = cache.get(key)
        if v is None:
            v = _decode(ch)[0]
            if len(cache) > 300000:
                cache.clear()
            cache[key] = v
        return v

    pop = []
    kmax = math.isqrt(n)
    # grid seeds
    for k in range(1, kmax + 1):
        base = [1.0 / k] * (k * k)
        base = base[:n]
        rest = n - len(base)
        pop.append(base + [0.0] * rest)
        for d in range(k + 1, min(Q, 3 * k) + 1):
            pop.append(base + [1.0 / d] * rest)
    # one big square + ring of 1/(d) squares
    for d in range(2, Q + 1):
        big = (d - 1) / d
        ring = 2 * (d - 1) + 1
        ch = [big] + [1.0 / d] * ring
        if len(ch) <= n:
            ch += [1.0 / (d + 1)] * (n - len(ch))
        pop.append(ch[:n])
    # random multisets from 1/d, sorted descending
    while len(pop) < 60:
        d = rng.randint(1, Q)
        ch = []
        for _ in range(n):
            if rng.random() < 0.6:
                ch.append(1.0 / d)
            else:
                ch.append(rand_gene())
        ch.sort(reverse=True)
        pop.append(ch)

    scored = {}
    for ch in pop:
        scored[tuple(ch)] = fit(ch)
    P = sorted(scored.items(), key=lambda t: -t[1])[:60]
    pop = [list(c) for c, _ in P]
    fits = [f for _, f in P]
    seen = set(tuple(c) for c in pop)

    def tour():
        a = rng.randrange(len(pop))
        for _ in range(2):
            b = rng.randrange(len(pop))
            if fits[b] > fits[a]:
                a = b
        return pop[a]

    it = 0
    while True:
        it += 1
        if (it & 15) == 0 and time.time() - t0 > budget:
            break
        r = rng.random()
        a = tour()
        if r < 0.3:
            b = tour()
            c = rng.randint(1, n - 1) if n > 1 else 0
            child = a[:c] + b[c:]
        else:
            child = list(a)
        nm = rng.choice((1, 1, 2, 3))
        for _ in range(nm):
            m = rng.random()
            i = rng.randrange(n)
            if m < 0.35:
                child[i] = rand_gene()
            elif m < 0.6:
                j = rng.randrange(n)
                child[i], child[j] = child[j], child[i]
            elif m < 0.7:
                child.sort(reverse=True)
            elif m < 0.8:
                g = child.pop(i)
                child.insert(rng.randrange(n), g)
            elif m < 0.9:
                # replace a gene by a neighbour denominator
                g = child[i]
                if g > 0:
                    q = round(1 / g) if g > 0 else 1
                    q = max(1, min(Q, q + rng.choice((-1, 1))))
                    child[i] = 1.0 / q
            else:
                # shift a block of equal genes
                child[i] = child[rng.randrange(n)]
        key = tuple(child)
        if key in seen:
            continue
        f = fit(child)
        w = min(range(len(pop)), key=lambda t: fits[t])
        if f > fits[w]:
            seen.discard(tuple(pop[w]))
            pop[w] = child
            fits[w] = f
            seen.add(key)

    bi = max(range(len(pop)), key=lambda t: fits[t])
    best = pop[bi]
    total, pl = _decode(best)
    res = []
    for s, p in zip(best, pl):
        if p is None:
            res.append((0.5, 0.5, 0.0, 0.0))
        else:
            ss = max(0.0, s - 1e-10)
            cx = min(1.0, max(0.0, p[0] + s / 2))
            cy = min(1.0, max(0.0, p[1] + s / 2))
            res.append((cx, cy, 0.0, ss))
    while len(res) < n:
        res.append((0.5, 0.5, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
