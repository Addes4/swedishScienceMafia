# EVOLVE-BLOCK-START
"""Grid of k x k cells; up to three disjoint rectangular a x b blocks re-tiled by
p x q equal squares (side min(a/p, b/q)/k), optionally dropping a few squares."""
import math
import time
import heapq


def _can_pack(blocks, k):
    grid = [[False] * k for _ in range(k)]
    order = sorted(range(len(blocks)), key=lambda i: -blocks[i][0] * blocks[i][1])
    place = [None] * len(blocks)

    def rec(t):
        if t == len(order):
            return True
        i = order[t]
        a, b = blocks[i]
        orients = [(a, b, False)] if a == b else [(a, b, False), (b, a, True)]
        for w, h, tr in orients:
            if w > k or h > k:
                continue
            for x in range(k - w + 1):
                for y in range(k - h + 1):
                    ok = True
                    for xx in range(x, x + w):
                        row = grid[xx]
                        for yy in range(y, y + h):
                            if row[yy]:
                                ok = False
                                break
                        if not ok:
                            break
                    if not ok:
                        continue
                    for xx in range(x, x + w):
                        for yy in range(y, y + h):
                            grid[xx][yy] = True
                    place[i] = (x, y, w, h, tr)
                    if rec(t + 1):
                        return True
                    for xx in range(x, x + w):
                        for yy in range(y, y + h):
                            grid[xx][yy] = False
        return False

    if rec(0):
        return place
    return None


def _build(k, ops, place):
    covered = [[False] * k for _ in range(k)]
    sq = []
    zeros = 0
    for op, pl in zip(ops, place):
        a, b, p, q, r = op
        x, y, w, h, tr = pl
        if tr:
            p, q = q, p
        for xx in range(x, x + w):
            for yy in range(y, y + h):
                covered[xx][yy] = True
        s = min(w / p, h / q) / k
        items = []
        for i in range(p):
            for j in range(q):
                items.append((x / k + (i + 0.5) * s, y / k + (j + 0.5) * s, 0.0, s))
        keep = len(items) - r
        sq.extend(items[:keep])
        zeros += r
    for xx in range(k):
        for yy in range(k):
            if not covered[xx][yy]:
                sq.append(((xx + 0.5) / k, (yy + 0.5) / k, 0.0, 1.0 / k))
    sq.extend([(0.0, 0.0, 0.0, 0.0)] * zeros)
    return sq


def solve(n):
    t0 = time.time()
    k0 = max(1, math.isqrt(n))
    best_val = float(k0)
    best_sq = [((i + 0.5) / k0, (j + 0.5) / k0, 0.0, 1.0 / k0) for i in range(k0) for j in range(k0)]

    Kmax = math.isqrt(n) + 4
    for k in range(1, Kmax + 1):
        if time.time() - t0 > 40:
            break
        target = n - k * k
        lo = -k * k
        hi = target + 2 * k * k
        ops = {}
        for a in range(1, k + 1):
            for b in range(a, k + 1):
                area = a * b
                lim = n + area
                bestc = {}
                for p in range(1, lim + 1):
                    for q in range(1, lim // p + 1):
                        c = p * q
                        s = min(a / p, b / q) / k
                        cur = bestc.get(c)
                        if cur is None or s > cur[0] + 1e-15:
                            bestc[c] = (s, p, q)
                for c, (s, p, q) in bestc.items():
                    for r in {0, 1, 2, 3, c}:
                        if r > c:
                            continue
                        cnt = c - r
                        dc = cnt - area
                        if dc < lo or dc > hi:
                            continue
                        if cnt == 0 and not (a == 1 and b == 1):
                            continue
                        ds = cnt * s - area / k
                        ops.setdefault(dc, []).append((ds, area, (a, b, p, q, r)))
        # Pareto prune per dc
        pruned = {}
        for dc, lst in ops.items():
            lst.sort(key=lambda e: (e[1], -e[0]))
            front = []
            bestds = -1e18
            for e in lst:
                if e[0] > bestds + 1e-12:
                    front.append(e)
                    bestds = e[0]
            if len(front) > 3:
                front = [front[0], front[len(front) // 2], front[-1]]
            pruned[dc] = front
        pruned.setdefault(0, [])
        pruned[0] = [(0.0, 0, None)] + pruned[0]
        dcs = sorted(pruned.keys())
        cands = []
        kk = k * k
        for i1, d1 in enumerate(dcs):
            L1 = pruned[d1]
            for d2 in dcs[i1:]:
                d3 = target - d1 - d2
                if d3 < d2:
                    break
                L3 = pruned.get(d3)
                if L3 is None:
                    continue
                L2 = pruned[d2]
                for e1 in L1:
                    for e2 in L2:
                        a12 = e1[1] + e2[1]
                        if a12 > kk:
                            continue
                        s12 = e1[0] + e2[0]
                        for e3 in L3:
                            if a12 + e3[1] > kk:
                                continue
                            tot = k + s12 + e3[0]
                            if tot <= best_val + 1e-12:
                                continue
                            item = (tot, id((e1, e2, e3)), (e1, e2, e3))
                            if len(cands) < 40:
                                heapq.heappush(cands, item)
                            elif tot > cands[0][0]:
                                heapq.heapreplace(cands, item)
        cands.sort(key=lambda c: -c[0])
        for tot, _, es in cands:
            if tot <= best_val + 1e-12:
                break
            opl = [e[2] for e in es if e[2] is not None]
            blocks = [(o[0], o[1]) for o in opl]
            pl = _can_pack(blocks, k)
            if pl is None:
                continue
            sq = _build(k, opl, pl)
            val = sum(s[3] for s in sorted(sq, key=lambda s: -s[3])[:n])
            if val > best_val + 1e-12:
                best_val = val
                best_sq = sq
            break

    sq = sorted(best_sq, key=lambda s: -s[3])[:n]
    sq += [(0.0, 0.0, 0.0, 0.0)] * (n - len(sq))
    out = []
    for (x, y, ang, s) in sq:
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), ang, min(1.0, max(0.0, s))))
    return out
# EVOLVE-BLOCK-END
