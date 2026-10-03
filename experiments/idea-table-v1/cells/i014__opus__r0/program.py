# EVOLVE-BLOCK-START
"""Best-first search over grid-based layouts using split / merge moves."""
import math
import heapq
import time

# common denominator for exact integer coordinates
D = (2 ** 10) * (3 ** 6) * (5 ** 3) * (7 ** 2) * 11 * 13


def _value(state, n):
    sides = sorted((s for (_, _, s) in state), reverse=True)
    return sum(sides[:n])


def _expand(state, maxcnt):
    cnt = len(state)
    sset = set(state)
    out = []
    for sq in state:
        x, y, s = sq
        # splits
        j = 2
        while cnt + j * j - 1 <= maxcnt:
            if s % j == 0:
                t = s // j
                rest = [q for q in state if q != sq]
                for a in range(j):
                    for b in range(j):
                        rest.append((x + a * t, y + b * t, t))
                out.append(tuple(sorted(rest)))
            j += 1
        # merges (sq is bottom-left corner)
        j = 2
        while x + j * s <= D and y + j * s <= D:
            ok = True
            for a in range(j):
                for b in range(j):
                    if (x + a * s, y + b * s, s) not in sset:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
            blk = set((x + a * s, y + b * s, s) for a in range(j) for b in range(j))
            rest = [q for q in state if q not in blk]
            rest.append((x, y, j * s))
            out.append(tuple(sorted(rest)))
            j += 1
    return out


def _search(n, time_limit=40.0, max_states=400000):
    t0 = time.time()
    slack = 2 * math.isqrt(n) + 4
    maxcnt = n + slack
    heap = []
    visited = set()
    best_val = -1.0
    best_state = None
    counter = 0
    k = 1
    while k * k <= maxcnt:
        if D % k == 0:
            t = D // k
            st = tuple(sorted((i * t, j * t, t) for i in range(k) for j in range(k)))
            if st not in visited:
                visited.add(st)
                v = _value(st, n)
                heapq.heappush(heap, (-v, counter, st))
                counter += 1
                if v > best_val:
                    best_val, best_state = v, st
        k += 1
    while heap:
        if time.time() - t0 > time_limit or len(visited) > max_states:
            break
        _, _, st = heapq.heappop(heap)
        for ch in _expand(st, maxcnt):
            if ch in visited:
                continue
            visited.add(ch)
            v = _value(ch, n)
            if v > best_val:
                best_val, best_state = v, ch
            heapq.heappush(heap, (-v, counter, ch))
            counter += 1
    return best_state


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    if n <= 0:
        return []
    st = _search(n)
    sq = sorted(st, key=lambda q: -q[2])[:n]
    res = []
    for (x, y, s) in sq:
        cx = (x + s / 2.0) / D
        cy = (y + s / 2.0) / D
        side = s / D
        cx = min(max(cx, 0.0), 1.0)
        cy = min(max(cy, 0.0), 1.0)
        side = min(max(side, 0.0), 1.0)
        res.append((cx, cy, 0.0, side))
    while len(res) < n:
        res.append((0.0, 0.0, 0.0, 0.0))
    return res[:n]
# EVOLVE-BLOCK-END
