# EVOLVE-BLOCK-START
"""Fast time-bounded search for sets with large |A-A| and small |A+A|."""
import math
import random
import time

import numpy as np


def _eval(a):
    """Score of integer array a. Returns (score, ndiff, nsum)."""
    a = np.asarray(a, dtype=np.int64)
    n = a.size
    if n < 2:
        return 0.0, 0, 0
    d = np.unique(a[:, None] - a[None, :]).size
    s = np.unique(a[:, None] + a[None, :]).size
    if s < 2:
        return 0.0, d, s
    return math.log(d) / math.log(s) + (1 - 1 / n) / 100, d, s


def _grow(n, rng):
    """Greedy: build a by minimizing new sums while maximizing new diffs."""
    a = [0]
    for _ in range(n - 1):
        cur = np.array(a, dtype=np.int64)
        curd = set(np.unique(cur[:, None] - cur[None, :]).tolist())
        curs = set(np.unique(cur[:, None] + cur[None, :]).tolist())
        # candidate positions near existing elements
        cands = set()
        for base in a:
            for d in range(1, 24):
                cands.add(base + d)
                cands.add(base - d)
        cands = [c for c in cands if c not in set(a)]
        rng.shuffle(cands)
        cands = cands[:500]
        best_x = None
        best_val = None
        for x in cands:
            newd = 0
            news = 0
            for y in a:
                if (x - y) not in curd or (y - x) not in curd:
                    newd += 1
                if (x + y) not in curs:
                    news += 1
            val = newd - 2.0 * news
            if best_val is None or val > best_val:
                best_val = val
                best_x = x
        if best_x is None:
            break
        a.append(best_x)
    return a


def _hill(a, deadline, rng):
    """Fast hill-climb moving single elements, maximizing true score."""
    cur = np.array(sorted(set(int(x) for x in a)), dtype=np.int64)
    if cur.size < 2:
        return cur, -1.0
    cs, _, _ = _eval(cur)
    span = max(1, int(cur.max() - cur.min()))
    while time.time() < deadline:
        i = rng.randrange(cur.size)
        step = max(1, span // rng.choice([2, 3, 4, 6, 8]))
        delta = rng.randint(-step, step)
        if delta == 0:
            delta = 1
        cand = cur.copy()
        cand[i] += delta
        if np.unique(cand).size != cand.size:
            continue
        cand = np.sort(cand)
        ns, _, _ = _eval(cand)
        if ns >= cs:
            cur = cand
            cs = ns
    return cur, cs


def solve():
    deadline = time.time() + 112
    rng = random.Random(987654321)
    best = None
    best_score = -1.0

    sizes = list(range(8, 30)) + [35, 40, 50, 60]
    random.shuffle(sizes)
    idx = 0

    while time.time() < deadline - 12:
        n = sizes[idx % len(sizes)]
        idx += 1
        a = _grow(n, rng)
        if len(a) < 2:
            continue
        arr = np.array(sorted(set(a)), dtype=np.int64)
        s, _, _ = _eval(arr)
        if s > best_score:
            best_score = s
            best = arr.tolist()
        t_end = min(deadline - 12, time.time() + 0.6)
        pol, ps = _hill(a, t_end, rng)
        if ps > best_score:
            best_score = ps
            best = pol.tolist()
        if idx % (2 * len(sizes)) == 0:
            random.shuffle(sizes)

    if best is None:
        best = [0, 1, 3, 7, 12]

    cur = sorted(set(int(x) for x in best))
    cur_score = best_score
    while time.time() < deadline:
        t_end = min(deadline, time.time() + 3.0)
        cand, cs = _hill(cur, t_end, rng)
        if cs > cur_score:
            cur = cand.tolist()
            cur_score = cs
        else:
            arr = np.array(cur, dtype=np.int64)
            if arr.size:
                k = max(1, arr.size // 8)
                for _ in range(rng.randint(1, k)):
                    j = rng.randrange(arr.size)
                    arr[j] += rng.randint(-30, 30)
                arr = np.unique(np.sort(arr))
                cur = arr.tolist()
                cur_score, _, _ = _eval(arr)

    return sorted(set(int(x) for x in best))
# EVOLVE-BLOCK-END
