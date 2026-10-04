# EVOLVE-BLOCK-START
"""Improved: structured Sidon-like constructions + local search."""
import math
import random
import time


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    if len(sums) == 0:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def _quadratic_set(p):
    """Bose-Chowla-like Sidon set: A = {i + p*(i^2 mod p) : i in 0..p-1}."""
    return [i + p * ((i * i) % p) for i in range(p)]


def _greedy_sidon(n, seed=0):
    """Greedily build a Sidon set of size ~n within a bounded range."""
    rng = random.Random(seed)
    A = []
    used_sums = set()
    used_diffs = set()
    cand = list(range(1, 4 * n * n + 10))
    rng.shuffle(cand)
    for x in cand:
        ok = True
        new_sums = set()
        new_diffs = set()
        for a in A:
            s = x + a
            if s in used_sums or s in new_sums:
                ok = False
                break
            new_sums.add(s)
            d1 = x - a
            d2 = a - x
            if d1 in used_diffs or d2 in used_diffs or d1 in new_diffs or d2 in new_diffs:
                ok = False
                break
            new_diffs.add(d1)
            new_diffs.add(d2)
        if ok:
            A.append(x)
            used_sums |= new_sums | {2 * x}
            used_diffs |= new_diffs
        if len(A) >= n:
            break
    return A


def _bounded_sidon(n, span, seed=0):
    """Build a Sidon-like set of size n inside [0, span] using randomized greedy,
    biased toward keeping elements near the middle (compacting the sum set)."""
    rng = random.Random(seed)
    A = []
    used_sums = set()
    used_diffs = set()
    center = span // 2
    cand = sorted(range(0, span + 1), key=lambda x: (abs(x - center), rng.random()))
    for x in cand:
        ok = True
        new_sums = set()
        new_diffs = set()
        for a in A:
            s = x + a
            if s in used_sums or s in new_sums:
                ok = False
                break
            new_sums.add(s)
            d1 = x - a
            d2 = a - x
            if d1 in used_diffs or d2 in used_diffs or d1 in new_diffs or d2 in new_diffs:
                ok = False
                break
            new_diffs.add(d1)
            new_diffs.add(d2)
        if ok:
            A.append(x)
            used_sums |= new_sums | {2 * x}
            used_diffs |= new_diffs
        if len(A) >= n:
            break
    return A


def _growth_search(seed, w, deadline, eps=0.001, max_stall=3):
    """Iteratively grow/refine `seed` using tradeoff gain = d_gain - w * s_cost.
    Allows up to `max_stall` consecutive non-improving (within eps) additions."""
    cur = list(set(seed))
    if len(cur) < 2:
        return cur
    cur_d = {x - y for x in cur for y in cur}
    cur_s = {x + y for x in cur for y in cur}
    best = cur[:]
    best_score = _score(cur)
    span = (max(cur) - min(cur)) if len(cur) > 1 else 1
    stall = 0
    while time.time() < deadline and stall < max_stall:
        # Try adding a new element chosen to keep sums small.
        lo = min(cur)
        hi = max(cur)
        c = (lo + hi) // 2
        # candidate positions: near center of current span, plus a few random
        candidates = []
        for _ in range(8):
            candidates.append(c + random.randint(-span, span))
        for _ in range(4):
            candidates.append(random.randint(lo - span, hi + span))
        improved = False
        for x in candidates:
            if x in cur:
                continue
            new = cur + [x]
            new_d = {p - q for p in new for q in new}
            new_s = {p + q for p in new for q in new}
            d_gain = len(new_d) - len(cur_d)
            s_cost = len(new_s) - len(cur_s)
            gain = d_gain - w * s_cost
            # Accept if gain is positive OR score not worse than best - eps.
            new_score = math.log(len(new_d)) / math.log(len(new_s)) + (1 - 1 / len(new)) / 100
            if gain > 0 or new_score >= best_score - eps:
                cur = new
                cur_d = new_d
                cur_s = new_s
                span = (max(cur) - min(cur)) if len(cur) > 1 else 1
                if new_score > best_score:
                    best = cur[:]
                    best_score = new_score
                    stall = 0
                else:
                    stall += 1
                improved = True
                break
        if not improved:
            # Try removing an element to reduce sums.
            if len(cur) > 2:
                j = random.randrange(len(cur))
                new = cur[:j] + cur[j + 1:]
                new_d = {p - q for p in new for q in new}
                new_s = {p + q for p in new for q in new}
                new_score = math.log(len(new_d)) / math.log(len(new_s)) + (1 - 1 / len(new)) / 100
                if new_score >= best_score - eps:
                    cur = new
                    cur_d = new_d
                    cur_s = new_s
                    if new_score > best_score:
                        best = cur[:]
                        best_score = new_score
                        stall = 0
                    else:
                        stall += 1
                    continue
            stall += 1
    return best


def _reflect_half(A):
    """Reflect the upper half of A around its center to try to shrink |A+A|."""
    if len(A) < 4:
        return A
    B = sorted(A)
    c = (B[0] + B[-1]) // 2
    n = len(B)
    out = B[: n // 2] + [2 * c - x for x in B[n // 2:]]
    if len(set(out)) != len(B):
        return A
    return out


def _sum_compaction_step(A, rng, window=25, floor=0.97):
    """Pick a random index and try to replace a[i] with a nearby value that
    reduces |A+A| while keeping |A-A| >= floor * current |A-A|.
    Returns (new_A, new_score) or (A, _score(A)) if no improvement found."""
    if len(A) < 3:
        return A, _score(A)
    n = len(A)
    base_sums = {x + y for x in A for y in A}
    base_diffs = {x - y for x in A for y in A}
    base_size = len(base_diffs)
    best_A = A
    best_sums = len(base_sums)
    best_diffs = base_size
    i = rng.randrange(n)
    ai = A[i]
    others = A[:i] + A[i + 1:]
    # Precompute sums/diffs not involving a[i]
    others_set = set(others)
    sums_no_i = {x + y for x in others for y in others}
    diffs_no_i = {x - y for x in others for y in others}
    # Candidate values around a[i]
    candidates = [ai + d for d in range(-window, window + 1) if d != 0]
    rng.shuffle(candidates)
    # Always include the current value to allow early exit comparison
    for v in candidates:
        if v in others_set:
            continue
        new_sums = sums_no_i | {v + x for x in others} | {2 * v}
        new_diffs = diffs_no_i | {v - x for x in others} | {x - v for x in others}
        nd = len(new_diffs)
        if nd < floor * base_size:
            continue
        ns = len(new_sums)
        if ns < best_sums or (ns == best_sums and nd > best_diffs):
            best_sums = ns
            best_diffs = nd
            best_A = others + [v]
    if best_A is A:
        return A, _score(A)
    return best_A, _score(best_A)


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small."""
    best = None
    best_score = -1.0

    # Try structured quadratic constructions for a range of primes.
    primes = [p for p in range(11, 200) if all(p % d for d in range(2, int(p ** 0.5) + 1))]
    for p in primes:
        cand = _quadratic_set(p)
        for shift in (0, -p // 2):
            c2 = [x + shift for x in cand]
            s = _score(c2)
            if s > best_score:
                best_score = s
                best = c2[:]
        r = _reflect_half(cand)
        if len(set(r)) == len(cand):
            s = _score(r)
            if s > best_score:
                best_score = s
                best = r[:]

    # Bounded Sidon constructions inside a tight span: directly aims to keep
    # |A+A| small while |A-A| remains large.
    for n in [20, 40, 60, 90, 120, 160, 200]:
        for span_mult in (2, 3, 4, 6):
            span = n * n * span_mult
            if span > 10 ** 6:
                continue
            for seed in (n, n * 7 + 1, n * 13 + 5):
                cand = _bounded_sidon(n, span, seed=seed)
                if len(cand) >= 2:
                    s = _score(cand)
                    if s > best_score:
                        best_score = s
                        best = cand[:]

    # Also try greedy Sidon sets of various sizes.
    for n in [30, 50, 80, 120, 150]:
        cand = _greedy_sidon(n, seed=n)
        if len(cand) >= 2:
            s = _score(cand)
            if s > best_score:
                best_score = s
                best = cand[:]

    if best is None:
        best = [7, 15, 18, 22, -3, -2]
        best_score = _score(best)

    # Iterative growth search with tradeoff weight sweep from several seeds.
    deadline = time.time() + 100
    seeds = []
    if best is not None:
        seeds.append(best[:])
    for p in [31, 53, 79, 101, 127, 151, 179]:
        q = _quadratic_set(p)
        if len(q) >= 2:
            seeds.append(q)
    for n in [40, 80, 120]:
        g = _bounded_sidon(n, n * n * 3, seed=n)
        if len(g) >= 2:
            seeds.append(g)
    weights = [0.15, 0.25, 0.35, 0.5]
    seed_idx = 0
    while time.time() < deadline - 30 and seed_idx < len(seeds):
        for w in weights:
            if time.time() >= deadline - 30:
                break
            g = _growth_search(seeds[seed_idx], w, deadline - 30)
            if len(g) >= 2:
                s = _score(g)
                if s > best_score:
                    best_score = s
                    best = g[:]
        seed_idx += 1

    # Local search: perturb elements, accept improvements. Allow multi-scale steps.
    # Interleave random perturbation with a targeted sum-set compaction move that
    # directly attacks |A+A| while protecting |A-A|.
    cur = best[:]
    cur_score = best_score
    deadline = time.time() + 100
    span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1
    rng_local = random.Random(1234567)
    while time.time() < deadline:
        # With probability ~40%, do a sum-compaction move; otherwise random perturb.
        if rng_local.random() < 0.4:
            new_A, new_score = _sum_compaction_step(cur, rng_local, window=25, floor=0.97)
            if new_score >= cur_score:
                cur, cur_score = new_A, new_score
                span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1
                if new_score > best_score:
                    best, best_score = new_A[:], new_score
            continue
        cand = cur[:]
        i = random.randrange(len(cand))
        if random.random() < 0.7:
            step = max(1, span_cur // 50)
        else:
            step = max(1, span_cur // 8)
        delta = random.randint(-step, step)
        if delta == 0:
            delta = 1
        cand[i] += delta
        cand = list(set(cand))
        if len(cand) < 2:
            continue
        s = _score(cand)
        if s >= cur_score:
            cur, cur_score = cand, s
            span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1
            if s > best_score:
                best, best_score = cand[:], s
        elif random.random() < 0.03:
            cur = cand
            span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1

    # Final polishing: try reflecting and small shifts on the best found.
    for shift in range(-3, 4):
        c2 = [x + shift for x in best]
        s = _score(c2)
        if s > best_score:
            best_score = s
            best = c2[:]
    r = _reflect_half(best)
    if len(set(r)) == len(best):
        s = _score(r)
        if s > best_score:
            best_score = s
            best = r[:]

    return sorted(set(best))
# EVOLVE-BLOCK-END