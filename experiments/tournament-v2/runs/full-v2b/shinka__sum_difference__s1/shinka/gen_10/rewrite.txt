# EVOLVE-BLOCK-START
"""Hybrid Golomb + dense-core + greedy-seed search for maximizing log|A-A|/log|A+A|."""
import math
import random
import time


def _score(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    diffs = set()
    sums = set()
    for x in a:
        for y in a:
            diffs.add(x - y)
            sums.add(x + y)
    if len(sums) <= 1:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / n) / 100


def _greedy_golomb(n, max_val, rng):
    """Greedily build a Golomb ruler with n marks."""
    marks = [0]
    candidates = list(range(1, max_val + 1))
    rng.shuffle(candidates)
    for _ in range(n - 1):
        best_c = None
        best_new = -1
        sample = candidates[:min(200, len(candidates))]
        for c in sample:
            if c in marks:
                continue
            new_diffs = set()
            ok = True
            for m in marks:
                d = abs(c - m)
                if d in new_diffs:
                    ok = False
                    break
                new_diffs.add(d)
            if not ok:
                continue
            all_d = set()
            new_set = marks + [c]
            for i in range(len(new_set)):
                for j in range(i + 1, len(new_set)):
                    all_d.add(abs(new_set[i] - new_set[j]))
            if len(all_d) > best_new:
                best_new = len(all_d)
                best_c = c
        if best_c is None:
            for c in candidates:
                if c not in marks:
                    best_c = c
                    break
        if best_c is not None:
            marks.append(best_c)
    return marks


def _build_dense_golomb(m, golomb_size, gap, rng):
    """Dense core {0..m} plus Golomb-like values offset by gap."""
    core = list(range(m + 1))
    g = _greedy_golomb(golomb_size, max(50, golomb_size * 8), rng)
    offset = m + gap
    extra = [offset + x for x in g]
    return core + extra


def _greedy_build(n, hi, rng):
    """Objective-driven greedy build of size n, sampling candidates in [-hi, hi]."""
    a = [0, 1]
    while len(a) < n:
        best_x = None
        best_s = -1.0
        cands = set()
        for _ in range(40):
            cands.add(rng.randint(-hi, hi))
        base = list(a)
        for _ in range(30):
            x, y = rng.choice(base), rng.choice(base)
            cands.add(x + (x - y) if x != y else x + rng.randint(1, 5))
        for x in cands:
            if x in a:
                continue
            cand = a + [x]
            s = _score(cand)
            if s > best_s:
                best_s = s
                best_x = x
        if best_x is None:
            break
        a.append(best_x)
    return a


def _local_search(a, deadline, rng):
    """Simulated annealing with structured jumps on the actual objective."""
    a = sorted(set(a))
    best = a[:]
    best_score = _score(a)
    cur = a[:]
    cur_score = best_score
    T = 0.05
    steps = 0
    while time.time() < deadline:
        steps += 1
        if steps % 200 == 0:
            T *= 0.999
        cand = cur[:]
        op = rng.random()
        if op < 0.5 and len(cand) > 2:
            i = rng.randrange(len(cand))
            cand[i] += rng.randint(-5, 5)
        elif op < 0.75:
            if len(cand) < 4000:
                base = rng.choice(cand)
                cand.append(base + rng.randint(1, 30))
        elif op < 0.9 and len(cand) > 3:
            i = rng.randrange(len(cand))
            cand.pop(i)
        else:
            m = rng.randint(2, 8)
            gs = rng.randint(3, 10)
            gap = rng.randint(1, 5)
            cand = _build_dense_golomb(m, gs, gap, rng)
        cand = sorted(set(cand))
        if len(cand) < 2:
            continue
        s = _score(cand)
        if s > best_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-6)):
            cur = cand
            cur_score = s
            if s > best_score:
                best = cand[:]
                best_score = s
        if rng.random() < 0.02:
            cur = best[:]
            cur_score = best_score
    return best, best_score


def solve():
    rng = random.Random(12345)
    deadline = time.time() + 110
    best = None
    best_score = -1.0

    # Phase 1a: structured dense-core + Golomb constructions
    constructions = []
    for m in range(0, 12):
        for gs in range(3, 15):
            for gap in [1, 2, 3, 5, 8, 13]:
                constructions.append((m, gs, gap))
    rng.shuffle(constructions)

    phase1_deadline = time.time() + 30
    for (m, gs, gap) in constructions:
        if time.time() > phase1_deadline:
            break
        cand = sorted(set(_build_dense_golomb(m, gs, gap, rng)))
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    # Phase 1b: pure dense intervals and pure greedy Golomb rulers
    for n in range(3, 60):
        if time.time() > phase1_deadline + 5:
            break
        cand = list(range(n))
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]
    for n in range(3, 40):
        if time.time() > phase1_deadline + 10:
            break
        cand = _greedy_golomb(n, n * n, rng)
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    # Phase 1c: objective-driven greedy seeds
    phase1c_deadline = time.time() + 15
    for n in [6, 8, 10, 12, 15, 18, 22, 28, 35, 45, 60]:
        if time.time() > phase1c_deadline:
            break
        for hi in [20, 60, 200, 1000]:
            if time.time() > phase1c_deadline:
                break
            cand = _greedy_build(n, hi, rng)
            s = _score(cand)
            if s > best_score:
                best_score = s
                best = cand[:]

    if best is None:
        best = [0, 1, 3]
        best_score = _score(best)

    # Phase 2: local search from best
    improved, imp_score = _local_search(best, deadline, rng)
    if imp_score > best_score:
        best = improved
        best_score = imp_score

    # Phase 3: restart local search from fresh structured seeds
    while time.time() < deadline:
        m = rng.randint(1, 10)
        gs = rng.randint(3, 12)
        gap = rng.randint(1, 10)
        seed = _build_dense_golomb(m, gs, gap, rng)
        remaining = deadline - time.time()
        if remaining < 5:
            break
        sub_deadline = time.time() + min(remaining, 15)
        cand, s = _local_search(seed, sub_deadline, rng)
        if s > best_score:
            best = cand
            best_score = s

    return sorted(set(best))
# EVOLVE-BLOCK-END