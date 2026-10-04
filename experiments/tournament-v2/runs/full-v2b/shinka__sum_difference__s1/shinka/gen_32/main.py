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


def _build_dense_golomb(m, gs, gap, rng):
    """Dense core {0..m} plus a Golomb-like tail offset by m+gap."""
    core = list(range(m + 1))
    if gs <= 0:
        return core
    g = _greedy_golomb(gs, max(30, gs * gs + 20), rng)
    offset = m + gap
    extra = [offset + x for x in g]
    return core + extra


def _reflect_marks(a, center, frac):
    """Reflect the top `frac` fraction of marks above `center` around `center`.

    This preserves cardinality and (approximately) the difference-set size
    while producing a structurally distinct seed.
    """
    a = sorted(set(a))
    n = len(a)
    if n < 2:
        return a[:]
    k = max(1, int(round(frac * n)))
    top = a[-k:]
    rest = a[:-k]
    reflected = [2 * center - x for x in top]
    out = sorted(set(rest + reflected))
    return out


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


def _local_search(seed, deadline, rng):
    cur = sorted(set(seed))
    cur_score = _score_fast(cur)
    best = cur[:]
    best_score = cur_score
    T = 0.04
    step = 0
    while time.time() < deadline:
        step += 1
        if step % 1500 == 0:
            T = max(0.0005, T * 0.995)
        cand = cur[:]
        r = rng.random()
        if r < 0.45 and cand:
            i = rng.randrange(len(cand))
            cand[i] += rng.randint(-8, 8)
            cand = list(set(cand))
        elif r < 0.70:
            if len(cand) < 4000:
                base = rng.choice(cand)
                cand.append(base + rng.randint(1, 60))
                cand = list(set(cand))
        elif r < 0.90 and len(cand) > 3:
            i = rng.randrange(len(cand))
            cand.pop(i)
        else:
            # rebuild a fresh structured seed occasionally
            m = rng.randint(0, 14)
            gs = rng.randint(2, 16)
            gap = rng.randint(1, 12)
            cand = _build_dense_golomb(m, gs, gap, rng)
        if len(cand) < 2:
            continue
        s = _score_fast(cand)
        if s > cur_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-9)):
            cur = cand
            cur_score = s
            if s > best_score:
                best = cand[:]
                best_score = s
        if rng.random() < 0.01:
            cur = best[:]
            cur_score = best_score
    return best, best_score


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
    rng = random.Random(987654321)
    deadline = time.time() + 110

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score_fast(best)

    # Phase 1: systematic scan over (m, gs, gap) for the dense+Golomb family.
    # Collect a top-K list of seeds so we can later generate diverse reflected variants.
    phase1_end = time.time() + 40
    tried = []
    for m in range(0, 16):
        for gs in range(0, 18):
            for gap in [1, 2, 3, 4, 5, 7, 9, 12]:
                if time.time() > phase1_end:
                    break
                tried.append((m, gs, gap))
    # shuffle but keep deterministic
    rng.shuffle(tried)
    top_seeds = []  # list of (score, tuple(cand))
    for (m, gs, gap) in tried:
        if time.time() > phase1_end:
            break
        cand = _build_dense_golomb(m, gs, gap, rng)
        s = _score_fast(cand)
        if s > best_score:
            best_score = s
            best = cand[:]
        tup = tuple(sorted(set(cand)))
        top_seeds.append((s, tup))
    top_seeds.sort(key=lambda t: -t[0])
    # dedupe by cardinality, keep top 8
    seen_card = set()
    pruned = []
    for s, tup in top_seeds:
        c = len(tup)
        if c in seen_card:
            continue
        seen_card.add(c)
        pruned.append((s, tup))
        if len(pruned) >= 8:
            break
    top_seeds = pruned

    # Phase 2: local search from the best structured seed
    if time.time() < deadline:
        sub = time.time() + min(20, deadline - time.time())
        cand, s = _local_search(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 2b: diversity-preserving seed augmentation.
    # Reflect top seeds at multiple centers/fractions to obtain structurally
    # distinct seeds with nearly the same |A-A|, then refine each.
    reflected_seeds = []
    seen_card_ref = set()
    for s, tup in top_seeds:
        a = list(tup)
        if len(a) < 4:
            continue
        lo, hi = min(a), max(a)
        span = hi - lo
        if span <= 0:
            continue
        for cf in (0.3, 0.4, 0.5, 0.6, 0.7):
            center = lo + cf * span
            for frac in (0.3, 0.4, 0.5):
                r = _reflect_marks(a, center, frac)
                key = len(r)
                if key in seen_card_ref:
                    continue
                seen_card_ref.add(key)
                reflected_seeds.append(r)
    # Also always include a reflection of the current best
    if len(best) >= 4:
        lo, hi = min(best), max(best)
        span = hi - lo
        if span > 0:
            for cf in (0.4, 0.5, 0.6):
                center = lo + cf * span
                r = _reflect_marks(best, center, 0.4)
                if len(r) not in seen_card_ref:
                    seen_card_ref.add(len(r))
                    reflected_seeds.append(r)

    for seed in reflected_seeds:
        if time.time() > deadline - 5:
            break
        sub = time.time() + min(8, deadline - time.time())
        cand, s = _local_search(seed, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 3: repeated restarts until deadline (mix fresh structured seeds
    # with reflected variants of the current best for basin diversity).
    while time.time() < deadline - 3:
        if best and rng.random() < 0.35 and len(best) >= 4:
            lo, hi = min(best), max(best)
            span = hi - lo
            if span <= 0:
                continue
            cf = rng.uniform(0.25, 0.75)
            center = lo + cf * span
            frac = rng.uniform(0.25, 0.55)
            seed = _reflect_marks(best, center, frac)
        else:
            m = rng.randint(0, 14)
            gs = rng.randint(2, 16)
            gap = rng.randint(1, 12)
            seed = _build_dense_golomb(m, gs, gap, rng)
        sub = time.time() + min(12, deadline - time.time())
        cand, s = _local_search(seed, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    return sorted(set(best))
# EVOLVE-BLOCK-END