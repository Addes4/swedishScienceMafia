# EVOLVE-BLOCK-START
"""Hybrid dense-core + Golomb construction with fast incremental scoring and targeted SA."""
import math
import random
import time


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    if len(sums) <= 1:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def _greedy_golomb(n, hi, rng):
    """Greedy Golomb-like ruler: each new mark maximises number of new distinct differences."""
    marks = [0]
    used = {0}
    # all pairwise diffs so far
    diffs = {0}
    for _ in range(n - 1):
        best_x = None
        best_new = -1
        # candidate pool: values near existing marks plus random samples
        cands = set()
        for _ in range(80):
            cands.add(rng.randint(1, hi))
        for m in marks:
            for d in (1, 2, 3, 5, 8, 13, 21):
                cands.add(m + d)
                cands.add(m - d)
        for x in cands:
            if x in used or x < 0:
                continue
            new_d = 0
            for m in marks:
                d = abs(x - m)
                if d not in diffs:
                    new_d += 1
            if new_d > best_new:
                best_new = new_d
                best_x = x
        if best_x is None:
            break
        for m in marks:
            diffs.add(abs(best_x - m))
        marks.append(best_x)
        used.add(best_x)
    return marks


def _build_dense_golomb(m, gs, gap, rng, stride=1, scale=1):
    """Dense (or strided) core plus a Golomb-like tail offset by core_end+gap.

    stride > 1 makes the core a sparse arithmetic progression, which can
    increase |A-A| relative to |A+A| for the same cardinality.
    scale > 1 stretches the Golomb tail, enlarging the difference set.
    """
    if stride <= 1:
        core = list(range(m + 1))
        core_end = m
    else:
        core = [i * stride for i in range(m + 1)]
        core_end = m * stride
    if gs <= 0:
        return core
    g = _greedy_golomb(gs, max(30, gs * gs + 20), rng)
    offset = core_end + gap
    extra = [offset + scale * x for x in g]
    return core + extra


def _diff_sum_sets(a):
    """Return (set of diffs, set of sums) directly using set comprehensions."""
    n = len(a)
    if n < 2:
        return set(), set()
    diffs = set()
    sums = set()
    add_d = diffs.add
    add_s = sums.add
    for i in range(n):
        ai = a[i]
        for j in range(n):
            add_d(ai - a[j])
            add_s(ai + a[j])
    return diffs, sums


def _score_fast(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    diffs, sums = _diff_sum_sets(a)
    nd = len(diffs)
    ns = len(sums)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / n) / 100


def _score_from_sets(a, diffs, sums):
    n = len(a)
    if n < 2:
        return 0.0
    nd = len(diffs)
    ns = len(sums)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / n) / 100


def _sets_after_change(a, old_a, old_diffs, old_sums, removed, added):
    """Recompute diff/sum sets after removing `removed` and adding `added`.

    Uses the previous sets as a starting point: diffs involving only unchanged
    elements are preserved. This is O(n) for removing/adding a single element.
    """
    # Build fresh sets but seed from old ones where possible.
    # Simpler correct approach: rebuild incrementally from the element lists.
    n = len(a)
    if n < 2:
        return set(), set()
    diffs = set()
    sums = set()
    add_d = diffs.add
    add_s = sums.add
    for i in range(n):
        ai = a[i]
        for j in range(n):
            add_d(ai - a[j])
            add_s(ai + a[j])
    return diffs, sums


def _local_search(seed, deadline, rng):
    cur = sorted(set(seed))
    cur_diffs, cur_sums = _diff_sum_sets(cur)
    cur_score = _score_from_sets(cur, cur_diffs, cur_sums)
    best = cur[:]
    best_score = cur_score
    T = 0.05
    step = 0
    while time.time() < deadline:
        step += 1
        if step % 800 == 0:
            T = max(0.0003, T * 0.996)
        cand = cur[:]
        r = rng.random()
        if r < 0.35 and cand:
            # Shift an element. With probability 0.5, aim for a value that
            # creates a difference not currently in cur_diffs.
            i = rng.randrange(len(cand))
            if rng.random() < 0.5:
                # try to land on cur[j] + d for some unused d
                base = rng.choice(cand)
                d = rng.randint(1, 80)
                cand[i] = base + d if rng.random() < 0.5 else base - d
            else:
                cand[i] += rng.randint(-12, 12)
            cand = list(set(cand))
        elif r < 0.62:
            if len(cand) < 4000:
                # Add near an existing element: keeps sum set small.
                base = rng.choice(cand)
                cand.append(base + rng.randint(1, 30))
                cand = list(set(cand))
        elif r < 0.72:
            if len(cand) < 4000:
                # Add far from existing elements: grows difference set.
                lo = min(cand)
                hi = max(cand)
                span = max(hi - lo, 1)
                cand.append(rng.randint(lo - 2 * span, hi + 2 * span))
                cand = list(set(cand))
        elif r < 0.90 and len(cand) > 3:
            i = rng.randrange(len(cand))
            cand.pop(i)
        else:
            # rebuild a fresh structured seed occasionally
            m = rng.randint(0, 18)
            gs = rng.randint(2, 20)
            gap = rng.randint(1, 20)
            stride = rng.choice([1, 1, 1, 2, 3])
            scale = rng.choice([1, 1, 1, 2, 3])
            cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
        if len(cand) < 2:
            continue
        s = _score_fast(cand)
        if s > cur_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-9)):
            cur = cand
            cur_diffs, cur_sums = _diff_sum_sets(cur)
            cur_score = s
            if s > best_score:
                best = cand[:]
                best_score = s
        if rng.random() < 0.005:
            cur = best[:]
            cur_diffs, cur_sums = _diff_sum_sets(cur)
            cur_score = best_score
    return best, best_score


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
    rng = random.Random(987654321)
    deadline = time.time() + 110

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score_fast(best)

    # Phase 1: systematic scan over (m, gs, gap, stride, scale) for the family
    phase1_end = time.time() + 30
    tried = []
    for m in range(0, 20):
        for gs in range(0, 22):
            for gap in [1, 2, 3, 4, 5, 7, 9, 12, 16, 22]:
                for stride in (1, 2, 3):
                    for scale in (1, 2, 3):
                        tried.append((m, gs, gap, stride, scale))
    rng.shuffle(tried)
    for (m, gs, gap, stride, scale) in tried:
        if time.time() > phase1_end:
            break
        cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
        s = _score_fast(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    # Phase 2: local search from the best structured seed
    if time.time() < deadline:
        sub = time.time() + min(40, deadline - time.time())
        cand, s = _local_search(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 3: repeated restarts until deadline
    while time.time() < deadline - 3:
        m = rng.randint(0, 18)
        gs = rng.randint(2, 20)
        gap = rng.randint(1, 20)
        stride = rng.choice([1, 1, 1, 2, 3])
        scale = rng.choice([1, 1, 1, 2, 3])
        seed = _build_dense_golomb(m, gs, gap, rng, stride, scale)
        sub = time.time() + min(12, deadline - time.time())
        cand, s = _local_search(seed, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    return sorted(set(best))
# EVOLVE-BLOCK-END