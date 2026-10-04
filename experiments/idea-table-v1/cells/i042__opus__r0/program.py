# EVOLVE-BLOCK-START
"""GA over ordered side-multisets with a skyline (bottom-left) decoder,
seeded from grid / block-subdivision (Erdos-Soifer type) constructions."""
import math
import random
import time
from fractions import Fraction


def _lcm(a, b):
    return a // math.gcd(a, b) * b


def _seed_constructions(n):
    """Grid k x k with b disjoint s x s blocks each replaced by t x t squares."""
    res = []
    K = math.isqrt(n) + 3
    for k in range(1, K + 1):
        for s in range(1, k + 1):
            for t in range(0, K + 2):
                if t == s and s > 1:
                    continue
                maxb = (k // s) ** 2
                for b in range(0, maxb + 1):
                    if b > 0 and t == s:
                        continue
                    cnt = k * k + b * (t * t - s * s)
                    if cnt <= 0 or cnt > n + 3 * n + 20:
                        continue
                    sides = [Fraction(1, k)] * (k * k - b * s * s)
                    if t > 0:
                        sides += [Fraction(s, t * k)] * (b * t * t)
                    sides.sort(reverse=True)
                    sides = sides[:n]
                    val = sum(sides)
                    res.append((val, k, s, t, b))
                    if b == 0:
                        break
    res.sort(key=lambda r: -r[0])
    return res


def _build_direct(n, k, s, t, b):
    sq = []
    nb = k // s
    blocks = set()
    cnt = 0
    for bi in range(nb):
        for bj in range(nb):
            if cnt < b:
                blocks.add((bi, bj))
                cnt += 1
    inblock = set()
    for (bi, bj) in blocks:
        for i in range(bi * s, bi * s + s):
            for j in range(bj * s, bj * s + s):
                inblock.add((i, j))
        if t > 0:
            side = Fraction(s, t * k)
            for a in range(t):
                for c in range(t):
                    sq.append((Fraction(bi * s, k) + a * side,
                               Fraction(bj * s, k) + c * side, side))
    for i in range(k):
        for j in range(k):
            if (i, j) not in inblock:
                sq.append((Fraction(i, k), Fraction(j, k), Fraction(1, k)))
    sq.sort(key=lambda q: -q[2])
    return sq[:n]


def _decode(chrom, L):
    sky = [(0, L, 0)]
    placed = []
    total = 0
    for a in chrom:
        if a <= 0:
            placed.append(None)
            continue
        best = None
        m = len(sky)
        for i in range(m):
            x = sky[i][0]
            end = x + a
            if end > L:
                break
            y = 0
            j = i
            while j < m and sky[j][0] < end:
                if sky[j][2] > y:
                    y = sky[j][2]
                j += 1
            if y + a <= L and (best is None or y < best[0] or (y == best[0] and x < best[1])):
                best = (y, x)
        if best is None:
            placed.append(None)
            continue
        y, x = best
        top = y + a
        end = x + a
        left = []
        right = []
        for (sx, sw, sy) in sky:
            se = sx + sw
            if sx < x:
                e = se if se < x else x
                left.append((sx, e - sx, sy))
            if se > end:
                st = sx if sx > end else end
                right.append((st, se - st, sy))
        new = left + [(x, a, top)] + right
        merged = []
        for seg in new:
            if merged and merged[-1][2] == seg[2]:
                px, pw, py = merged[-1]
                merged[-1] = (px, pw + seg[1], py)
            else:
                merged.append(seg)
        sky = merged
        placed.append((x, y, a))
        total += a
    return total, placed


def _valid(sq):
    for q in sq:
        cx, cy, ang, s = q
        for v in q:
            if not (0.0 <= v <= 1.0):
                return False
    m = [(cx - s / 2, cy - s / 2, s) for cx, cy, _, s in sq if s > 0]
    for i in range(len(m)):
        x1, y1, s1 = m[i]
        if x1 < -1e-12 or y1 < -1e-12 or x1 + s1 > 1 + 1e-12 or y1 + s1 > 1 + 1e-12:
            return False
        for j in range(i + 1, len(m)):
            x2, y2, s2 = m[j]
            ox = min(x1 + s1, x2 + s2) - max(x1, x2)
            oy = min(y1 + s1, y2 + s2) - max(y1, y2)
            if ox > 1e-13 and oy > 1e-13:
                return False
    return True


def _to_output(sqs, n):
    out = []
    for (x, y, s) in sqs:
        xf, yf, sf = float(x), float(y), float(s)
        cx = min(1.0, max(0.0, xf + sf / 2))
        cy = min(1.0, max(0.0, yf + sf / 2))
        out.append((cx, cy, 0.0, max(0.0, sf * (1 - 1e-12) - 1e-15)))
    while len(out) < n:
        out.append((0.0, 0.0, 0.0, 0.0))
    return out[:n]


def solve(n):
    t0 = time.time()
    budget = 30.0
    rng = random.Random(12345 + n)

    k0 = max(1, math.isqrt(n))
    grid = [((i + 0.5) / k0, (j + 0.5) / k0, 0.0, 1.0 / k0) for i in range(k0) for j in range(k0)]
    grid += [(0.0, 0.0, 0.0, 0.0)] * (n - len(grid))
    fallback = grid[:n]

    seeds = _seed_constructions(n)
    best_val = Fraction(k0)
    best_out = fallback
    if seeds:
        v, k, s, t, b = seeds[0]
        sq = _build_direct(n, k, s, t, b)
        out = _to_output(sq, n)
        if _valid(out) and sum(q[2] for q in sq) > best_val:
            best_val = sum(q[2] for q in sq)
            best_out = out

    # alphabet
    alpha = set()
    D = 2 * math.isqrt(n) + 4
    for d in range(1, D + 1):
        alpha.add(Fraction(1, d))
    seedsets = []
    for (v, k, s, t, b) in seeds[:25]:
        sides = [Fraction(1, k)] * (k * k - b * s * s)
        if t > 0:
            sides += [Fraction(s, t * k)] * (b * t * t)
            alpha.add(Fraction(s, t * k))
        alpha.add(Fraction(1, k))
        sides.sort(reverse=True)
        seedsets.append(sides[:n])
    alpha = sorted(alpha, reverse=True)
    L = 1
    for f in alpha:
        L = _lcm(L, f.denominator)
    A = [int(f * L) for f in alpha]

    def enc(sides):
        c = [int(f * L) for f in sides]
        c += [0] * (n - len(c))
        return c[:n]

    def rand_chrom():
        base = rng.randint(max(1, math.isqrt(n) - 1), math.isqrt(n) + 2)
        c = []
        for _ in range(n):
            r = rng.random()
            if r < 0.6:
                d = base
            elif r < 0.9:
                d = max(1, base + rng.choice([-1, 1, 2]))
            else:
                c.append(rng.choice(A))
                continue
            d = min(d, D)
            c.append(L // d)
        c.sort(reverse=True)
        return c

    pop = []
    for ss in seedsets:
        c = enc(ss)
        pop.append(c)
        c2 = c[:]
        rng.shuffle(c2)
        pop.append(c2)
        c3 = sorted(c)  # ascending order variant
        pop.append(c3)
    POP = 60
    while len(pop) < POP:
        pop.append(rand_chrom())

    def fit(c):
        return _decode(c, L)[0]

    scored = [(fit(c), c) for c in pop]
    scored.sort(key=lambda z: -z[0])
    gbest_f, gbest_c = scored[0]

    def mutate(c):
        c = c[:]
        nm = 1 + (rng.random() < 0.5) + (rng.random() < 0.2)
        for _ in range(nm):
            op = rng.random()
            i = rng.randrange(n)
            if op < 0.25:
                j = rng.randrange(n)
                c[i], c[j] = c[j], c[i]
            elif op < 0.45:
                g = c.pop(i)
                c.insert(rng.randrange(n), g)
            elif op < 0.65:
                nz = [v for v in c if v > 0]
                if nz and rng.random() < 0.6:
                    c[i] = rng.choice(nz)
                else:
                    c[i] = rng.choice(A)
            elif op < 0.8:
                # shift to neighbour size in alphabet
                v = c[i]
                if v in A:
                    p = A.index(v) + rng.choice([-1, 1])
                    if 0 <= p < len(A):
                        c[i] = A[p]
                else:
                    c[i] = rng.choice(A)
            elif op < 0.9:
                c[i] = 0 if c[i] > 0 else rng.choice(A)
            else:
                j = rng.randrange(n)
                a, b = min(i, j), max(i, j)
                c[a:b + 1] = sorted(c[a:b + 1], reverse=rng.random() < 0.8)
        return c

    def crossover(p1, p2):
        if rng.random() < 0.5:
            cut = rng.randrange(1, n) if n > 1 else 0
            return p1[:cut] + p2[cut:]
        child = [p1[i] if rng.random() < 0.5 else p2[i] for i in range(n)]
        if rng.random() < 0.5:
            child.sort(reverse=True)
        return child

    def tourn():
        best = None
        for _ in range(3):
            z = scored[rng.randrange(len(scored))]
            if best is None or z[0] > best[0]:
                best = z
        return best[1]

    stall = 0
    while time.time() - t0 < budget:
        elite = scored[:6]
        newpop = list(elite)
        seen = set(tuple(c) for _, c in elite)
        while len(newpop) < POP:
            if rng.random() < 0.6:
                child = crossover(tourn(), tourn())
                if rng.random() < 0.5:
                    child = mutate(child)
            else:
                child = mutate(tourn())
            tc = tuple(child)
            if tc in seen:
                continue
            seen.add(tc)
            newpop.append((fit(child), child))
            if time.time() - t0 > budget:
                break
        newpop.sort(key=lambda z: -z[0])
        scored = newpop[:POP]
        if scored[0][0] > gbest_f:
            gbest_f, gbest_c = scored[0]
            stall = 0
        else:
            stall += 1
        if stall > 60:
            # immigrants
            keep = scored[:10]
            imm = [(fit(c), c) for c in (rand_chrom() for _ in range(POP - 10))]
            scored = sorted(keep + imm, key=lambda z: -z[0])
            stall = 0

    gval = Fraction(gbest_f, L)
    if gval > best_val:
        _, placed = _decode(gbest_c, L)
        sq = [(Fraction(x, L), Fraction(y, L), Fraction(a, L)) for p in placed if p is not None
              for (x, y, a) in [p]]
        out = _to_output(sq, n)
        if _valid(out):
            best_out = out
    if not _valid(best_out):
        best_out = fallback
    return best_out
# EVOLVE-BLOCK-END
