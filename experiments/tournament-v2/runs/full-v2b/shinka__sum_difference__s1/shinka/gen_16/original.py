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
    # Prefer candidates near the center of the span to keep |A+A| small.
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


def _reflect_fraction(A, frac, center_mode="mid"):
    """Reflect the top `frac` portion of A around a chosen center c.

    Reflection preserves the difference multiset (up to sign) but can shrink
    the sum set, so this is a cheap structural move for improving the ratio.
    """
    if len(A) < 4:
        return A
    B = sorted(A)
    n = len(B)
    k = int(round(frac * n))
    if k <= 0 or k >= n:
        return A
    if center_mode == "mid":
        c = (B[0] + B[-1]) // 2
    elif center_mode == "mean":
        c = int(round(sum(B) / n))
    elif center_mode == "median":
        c = B[n // 2]
    elif center_mode == "topmid":
        c = (B[n - k] + B[-1]) // 2
    else:
        c = (B[0] + B[-1]) // 2
    out = B[: n - k] + [2 * c - x for x in B[n - k:]]
    if len(set(out)) != n:
        return A
    return out


def _multi_reflect(A, max_rounds=3):
    """Try many reflection fractions/centers (and iterate) to shrink |A+A|."""
    best = list(A)
    best_s = _score(best)
    improved = True
    rounds = 0
    while improved and rounds < max_rounds:
        improved = False
        rounds += 1
        for frac in (0.5, 0.4, 0.3, 0.6):
            for mode in ("mid", "mean", "median", "topmid"):
                cand = _reflect_fraction(best, frac, mode)
                if len(set(cand)) != len(best):
                    continue
                s = _score(cand)
                if s > best_s:
                    best_s = s
                    best = cand
                    improved = True
    return best


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
        # Try reflect variants (multi-fraction, multi-center, iterated)
        r = _multi_reflect(cand)
        if len(set(r)) == len(cand):
            s = _score(r)
            if s > best_score:
                best_score = s
                best = r[:]

    # Bounded Sidon constructions inside a tight span: this directly aims to
    # keep |A+A| small while |A-A| remains large.
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

    # Local search: perturb elements, accept improvements. Allow multi-scale steps.
    cur = best[:]
    cur_score = best_score
    deadline = time.time() + 100
    span_cur = (max(cur) - min(cur)) if len(cur) > 1 else 1
    while time.time() < deadline:
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
    r = _multi_reflect(best, max_rounds=6)
    if len(set(r)) == len(best):
        s = _score(r)
        if s > best_score:
            best_score = s
            best = r[:]

    return sorted(set(best))
# EVOLVE-BLOCK-END