# EVOLVE-BLOCK-START
"""Search for A maximising log|A-A|/log|A+A| via structured seeding + exact hill-climb."""
import math
import random
import time


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    if len(sums) < 2:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def _stats(a):
    a = list(set(a))
    n = len(a)
    diffs = set()
    sums = set()
    for x in a:
        for y in a:
            diffs.add(x - y)
            sums.add(x + y)
    return len(diffs), len(sums), n


def _seed_interval_geometric(rng):
    """A = {0..n-1} union scaled geometric-ish block well separated."""
    n = rng.randint(8, 40)
    base = set(range(n))
    # geometric block: pick k distinct large values
    k = rng.randint(2, 6)
    scale = rng.choice([n * 2, n * 3, n * 4, n * 8])
    pts = set()
    v = scale
    for _ in range(k):
        pts.add(v)
        v = int(v * rng.uniform(1.5, 2.5)) + rng.randint(0, scale)
    return sorted(base | pts)


def _seed_twoblocks(rng):
    """Two intervals: {0..n-1} union {s..s+m-1} with tuned offset."""
    n = rng.randint(6, 30)
    m = rng.randint(3, 20)
    s = rng.randint(n + 1, 6 * (n + m))
    A = set(range(n))
    A |= {s + i for i in range(m)}
    return sorted(A)


def _hill_climb(start, deadline, rng):
    best = list(set(start))
    best_s = _score(best)
    cur = best[:]
    cur_s = best_s
    hi = max(abs(x) for x in cur) if cur else 1
    while time.time() < deadline:
        cand = cur[:]
        r = rng.random()
        if r < 0.5 and cand:
            # perturb an element
            i = rng.randrange(len(cand))
            span = max(1, hi // 2)
            cand[i] += rng.randint(-span, span)
        elif r < 0.8:
            # add a new element near existing structure
            anchor = rng.choice(cand) if cand else 0
            cand.append(anchor + rng.randint(-hi, hi))
        elif r < 0.95 and len(cand) > 3:
            # remove an element
            del cand[rng.randrange(len(cand))]
        else:
            # duplicate a scaling pattern
            if cand:
                cand = sorted(set(cand))
        cand = list(set(cand))
        if len(cand) < 2 or len(cand) > 4000:
            continue
        s = _score(cand)
        if s >= cur_s:
            cur, cur_s = cand, s
            if s > best_s:
                best, best_s = cand[:], s
        elif rng.random() < 0.08:
            cur, cur_s = best[:], best_s
    return best, best_s


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small."""
    rng = random.Random(12345)
    deadline = time.time() + 110

    best = [7, 15, 18, 22, -3, -2]
    best_s = _score(best)

    # deterministic candidate seeds
    seeds = []
    # pure interval as sanity (ratio ~1)
    for n in (10, 20, 40, 80):
        seeds.append(list(range(n)))
    # interval + geometric
    for _ in range(40):
        seeds.append(_seed_interval_geometric(rng))
    # two blocks
    for _ in range(40):
        seeds.append(_seed_twoblocks(rng))

    for seed in seeds:
        s = _score(seed)
        if s > best_s:
            best, best_s = seed[:], s

    # hill climb from multiple restarts
    attempts = 0
    while time.time() < deadline:
        attempts += 1
        if attempts % 3 == 0:
            start = _seed_interval_geometric(rng)
        elif attempts % 3 == 1:
            start = _seed_twoblocks(rng)
        else:
            start = best[:]
        cand, cs = _hill_climb(start, min(deadline, time.time() + 12), rng)
        if cs > best_s:
            best, best_s = cand[:], cs

    return sorted(set(best))
# EVOLVE-BLOCK-END

