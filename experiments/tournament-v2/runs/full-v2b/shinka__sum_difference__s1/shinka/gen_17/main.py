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
    # Pure log-ratio: no size bonus, so cardinality is optimized jointly.
    return math.log(len(diffs)) / math.log(len(sums))


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


def _local_search(start, deadline, rng, allow_resize=True):
    """Run a perturbation-based local search from `start` until `deadline`.

    Moves include element perturbation (multi-scale), element insertion and
    element deletion (when `allow_resize`), so cardinality is optimized jointly
    with the log-ratio score.
    """
    cur = list(start)
    cur_score = _score(cur)
    best = cur[:]
    best_score = cur_score
    span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1
    while time.time() < deadline:
        cand = cur[:]
        r = rng.random()
        if allow_resize and r < 0.08 and len(cand) > 4:
            # Delete a random element (prefer extremes to tighten the sum set).
            if rng.random() < 0.6:
                idx = 0 if rng.random() < 0.5 else len(cand) - 1
            else:
                idx = rng.randrange(len(cand))
            cand.pop(idx)
        elif allow_resize and r < 0.16:
            # Insert a new element near the current center span.
            lo, hi = min(cand), max(cand)
            cand.append(rng.randint(lo, hi))
        else:
            i = rng.randrange(len(cand))
            if rng.random() < 0.7:
                step = max(1, span_cur // 50)
            else:
                step = max(1, span_cur // 8)
            delta = rng.randint(-step, step)
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
        elif rng.random() < 0.03:
            cur = cand
            span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1
    return best, best_score


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small.

    We run a joint cardinality + structure search: structured seeds of many
    sizes, then local search across a range of n to find the best pure ratio.
    """
    rng = random.Random(12345)
    best = None
    best_score = -1.0

    # Structured quadratic (Bose-Chowla-like) constructions for a range of primes.
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

    # Collect candidate seeds across a range of cardinalities.
    seeds = []
    for n in [60, 100, 150, 200, 300]:
        # Bounded Sidon constructions inside a tight span.
        for span_mult in (2, 3, 4, 6):
            span = n * n * span_mult
            if span > 10 ** 7:
                continue
            for seed in (n, n * 7 + 1, n * 13 + 5):
                cand = _bounded_sidon(n, span, seed=seed)
                if len(cand) >= 2:
                    seeds.append(cand)
        # Greedy Sidon sets of the same size.
        cand = _greedy_sidon(n, seed=n)
        if len(cand) >= 2:
            seeds.append(cand)

    # Also include a few smaller sizes for completeness.
    for n in [30, 50, 80, 120]:
        cand = _greedy_sidon(n, seed=n)
        if len(cand) >= 2:
            seeds.append(cand)

    # Evaluate all seeds; keep the best pure-ratio one as warm start.
    for cand in seeds:
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    if best is None:
        best = [7, 15, 18, 22, -3, -2]
        best_score = _score(best)

    # Joint cardinality + structure local search across several n values.
    # Each run gets a slice of the time budget; allow_resize lets n drift.
    overall_deadline = time.time() + 100
    n_targets = [60, 100, 150, 200, 300]
    per_run = 100.0 / (len(n_targets) + 1)
    for n in n_targets:
        # Build a starting point of roughly size n from the best-known set or
        # a structured seed, then let local search refine it.
        if len(best) >= n:
            start = sorted(best)[:n]
        else:
            start = _greedy_sidon(n, seed=n * 31 + 7)
            if len(start) < 2:
                start = best[:]
        run_deadline = min(overall_deadline, time.time() + per_run)
        cand, s = _local_search(start, run_deadline, rng, allow_resize=True)
        if s > best_score:
            best, best_score = cand[:], s

    # Final long run from the best found, letting n drift freely.
    if time.time() < overall_deadline:
        cand, s = _local_search(best, overall_deadline, rng, allow_resize=True)
        if s > best_score:
            best, best_score = cand[:], s

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