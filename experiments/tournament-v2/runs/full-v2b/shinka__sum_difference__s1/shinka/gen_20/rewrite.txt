# EVOLVE-BLOCK-START
"""Hybrid dense-core + Golomb construction with aggressive reflection hill-climbing and SA."""
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
    diffs = {0}
    for _ in range(n - 1):
        best_x = None
        best_new = -1
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
    """Dense (or strided) core plus a Golomb-like tail offset by core_end+gap."""
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


def _fast_stats(a):
    """Return (num_diffs, num_sums) using counting dicts."""
    n = len(a)
    if n < 2:
        return 0, 0
    diff_cnt = {}
    sum_cnt = {}
    for i in range(n):
        ai = a[i]
        for j in range(n):
            d = ai - a[j]
            diff_cnt[d] = diff_cnt.get(d, 0) + 1
            s = ai + a[j]
            sum_cnt[s] = sum_cnt.get(s, 0) + 1
    return len(diff_cnt), len(sum_cnt)


def _score_fast(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _fast_stats(a)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / n) / 100


def _score_pure(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _fast_stats(a)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns)


def _reflect(a, c, frac, side="top"):
    """Reflect a fraction of a about center c.

    side='top' reflects the largest frac*len(a) elements,
    side='bottom' the smallest, side='mid' a middle band.
    Returns the new set as a sorted list.
    """
    s = sorted(set(a))
    n = len(s)
    k = max(1, int(round(frac * n)))
    if k >= n:
        k = n - 1
    if k <= 0:
        return s
    if side == "top":
        idx = range(n - k, n)
    elif side == "bottom":
        idx = range(0, k)
    else:
        lo = max(0, (n - k) // 2)
        idx = range(lo, lo + k)
    keep = [s[i] for i in range(n) if i not in idx]
    moved = [2 * c - s[i] for i in idx]
    out = sorted(set(keep + moved))
    return out


def _reflection_hillclimb(a, deadline, rng):
    """Iteratively apply the best reflection move (many centers & fractions)."""
    cur = sorted(set(a))
    cur_score = _score_fast(cur)
    best = cur[:]
    best_score = cur_score
    while time.time() < deadline:
        s = sorted(cur)
        n = len(s)
        if n < 4:
            break
        # candidate centers: midpoints of pairs from the sorted set, plus
        # quantiles of prefixes/suffixes (so reflections about cluster centers).
        centers = set()
        # quantile-ish centers
        for q in (0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9):
            i = int(q * (n - 1))
            centers.add(s[i])
        # pair midpoints involving extremes and near-extremes
        for i in range(min(6, n)):
            for j in range(max(0, n - 6), n):
                centers.add((s[i] + s[j]) // 2)
                centers.add((s[i] + s[j] + 1) // 2)
        # a few random pair midpoints
        for _ in range(8):
            i = rng.randrange(n)
            j = rng.randrange(n)
            centers.add((s[i] + s[j]) // 2)
        fracs = (0.2, 0.3, 0.4, 0.5)
        sides = ("top", "bottom", "mid")
        improved = False
        best_local = None
        best_local_score = cur_score
        for c in centers:
            for f in fracs:
                for side in sides:
                    cand = _reflect(cur, c, f, side)
                    if len(cand) < 2:
                        continue
                    sc = _score_fast(cand)
                    if sc > best_local_score:
                        best_local_score = sc
                        best_local = cand
        if best_local is not None:
            cur = best_local
            cur_score = best_local_score
            improved = True
            if cur_score > best_score:
                best = cur[:]
                best_score = cur_score
        if not improved:
            break
    return best, best_score


def _local_search(seed, deadline, rng, pure=False):
    cur = sorted(set(seed))
    cur_score = _score_fast(cur)
    if pure:
        n0 = len(cur)
        if n0 >= 2:
            cur_score -= (1 - 1 / n0) / 100
    best = cur[:]
    best_score = cur_score
    T = 0.05
    step = 0
    while time.time() < deadline:
        step += 1
        if step % 1200 == 0:
            T = max(0.0003, T * 0.996)
        cand = cur[:]
        r = rng.random()
        if r < 0.35 and cand:
            i = rng.randrange(len(cand))
            if rng.random() < 0.5:
                base = rng.choice(cand)
                d = rng.randint(1, 80)
                cand[i] = base + d if rng.random() < 0.5 else base - d
            else:
                cand[i] += rng.randint(-12, 12)
            cand = list(set(cand))
        elif r < 0.60:
            if len(cand) < 4000:
                base = rng.choice(cand)
                cand.append(base + rng.randint(1, 30))
                cand = list(set(cand))
        elif r < 0.72:
            if len(cand) < 4000:
                lo = min(cand)
                hi = max(cand)
                span = max(hi - lo, 1)
                cand.append(rng.randint(lo - 2 * span, hi + 2 * span))
                cand = list(set(cand))
        elif r < 0.90 and len(cand) > 3:
            i = rng.randrange(len(cand))
            cand.pop(i)
        else:
            m = rng.randint(0, 18)
            gs = rng.randint(2, 20)
            gap = rng.randint(1, 20)
            stride = rng.choice([1, 1, 1, 2, 3])
            scale = rng.choice([1, 1, 1, 2, 3])
            cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
        if len(cand) < 2:
            continue
        s_full = _score_fast(cand)
        if pure:
            n = len(cand)
            s = s_full - (1 - 1 / n) / 100 if n >= 2 else 0.0
        else:
            s = s_full
        if s > cur_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-9)):
            cur = cand
            cur_score = s
            if s > best_score:
                best = cand[:]
                best_score = s
        if rng.random() < 0.005:
            cur = best[:]
            cur_score = best_score
    return best, best_score


def _build_of_size(n, rng):
    if n <= 1:
        return [0]
    if n <= 4:
        return list(range(n))
    m = max(1, int(round(math.sqrt(n))) - 1)
    gs = n - (m + 1)
    if gs <= 0:
        return list(range(n))
    gap = rng.randint(1, 20)
    stride = rng.choice([1, 1, 1, 2, 3])
    scale = rng.choice([1, 1, 1, 2, 3])
    cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
    cand = sorted(set(cand))
    if len(cand) < n:
        hi = max(cand)
        x = hi + 1
        while len(cand) < n:
            if x not in cand:
                cand.append(x)
            x += 1
        cand = sorted(set(cand))
    elif len(cand) > n:
        cand = sorted(cand)[:n]
    return cand


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
    rng = random.Random(987654321)
    deadline = time.time() + 110

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score_fast(best)

    # Phase 0: cardinality-aware search over target sizes using the pure ratio.
    target_sizes = [30, 45, 65, 90, 130, 180, 250, 350, 500]
    pure_best = None
    pure_best_score = -1.0
    phase0_end = time.time() + 40
    per_n = max(2.0, (phase0_end - time.time()) / max(1, len(target_sizes)))
    for n_target in target_sizes:
        if time.time() >= phase0_end:
            break
        local_best = None
        local_score = -1.0
        for _ in range(2):
            if time.time() >= phase0_end:
                break
            seed = _build_of_size(n_target, rng)
            sub_end = min(phase0_end, time.time() + per_n / 2.0)
            cand, s = _local_search(seed, sub_end, rng, pure=True)
            if s > local_score:
                local_score = s
                local_best = cand
        if local_best is not None and local_score > pure_best_score:
            pure_best_score = local_score
            pure_best = local_best[:]
    if pure_best is not None:
        s_full = _score_fast(pure_best)
        if s_full > best_score:
            best = pure_best
            best_score = s_full

    # Phase 1: systematic scan over (m, gs, gap, stride, scale) for the family
    phase1_end = time.time() + 20
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

    # Phase 2: reflection hill-climb on the best structured seed
    if time.time() < deadline - 5:
        sub = time.time() + min(15, deadline - time.time() - 3)
        cand, s = _reflection_hillclimb(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 2b: local search from the current best
    if time.time() < deadline - 5:
        sub = time.time() + min(25, deadline - time.time() - 3)
        cand, s = _local_search(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 2c: reflection again after SA polish
    if time.time() < deadline - 5:
        sub = time.time() + min(10, deadline - time.time() - 3)
        cand, s = _reflection_hillclimb(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 3: restarts, each followed by both SA and reflection
    while time.time() < deadline - 6:
        m = rng.randint(0, 18)
        gs = rng.randint(2, 20)
        gap = rng.randint(1, 20)
        stride = rng.choice([1, 1, 1, 2, 3])
        scale = rng.choice([1, 1, 1, 2, 3])
        seed = _build_dense_golomb(m, gs, gap, rng, stride, scale)
        sub = time.time() + min(8, deadline - time.time() - 4)
        cand, s = _local_search(seed, sub, rng)
        if s > best_score:
            best, best_score = cand, s
        # reflection polish on this candidate
        sub2 = min(deadline - 1, time.time() + 3)
        cand2, s2 = _reflection_hillclimb(cand, sub2, rng)
        if s2 > best_score:
            best, best_score = cand2, s2

    # Final reflection polish
    if time.time() < deadline - 1:
        cand, s = _reflection_hillclimb(best, deadline - 0.5, rng)
        if s > best_score:
            best, best_score = cand, s

    return sorted(set(best))
# EVOLVE-BLOCK-END