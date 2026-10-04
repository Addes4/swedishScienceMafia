# EVOLVE-BLOCK-START
"""Nested-interval Sidon construction: distinct differences, colliding sums."""
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


def _greedy_sidon_base(n, seed=0):
    """Small Sidon-ish base set with many distinct differences."""
    rng = random.Random(seed)
    A = [0]
    used = {0}
    cand = 1
    limit = 4 * n * n + 50
    while len(A) < n and cand < limit:
        ok = True
        for a in A:
            d = cand - a
            if d in used:
                ok = False
                break
        if ok:
            for a in A:
                used.add(cand - a)
            A.append(cand)
        cand += 1
    return A


def _build_nested(base, offsets):
    """Union of (base + off) for each offset in offsets."""
    A = []
    for off in offsets:
        for b in base:
            A.append(b + off)
    return A


def _refine_offsets(base, offsets, deadline, rng):
    """Local search over offsets only, keeping the base structure fixed."""
    cur = sorted(offsets)
    cur_set = _build_nested(base, cur)
    cur_score = _score(cur_set)
    best = cur[:]
    best_score = cur_score
    span = max(cur) - min(cur) if len(cur) > 1 else 1
    while time.time() < deadline:
        cand = cur[:]
        i = rng.randrange(len(cand))
        # perturb one offset; use a scale related to base extent
        step = rng.randint(-max(1, span // 20), max(1, span // 20))
        if step == 0:
            step = rng.choice([-1, 1])
        cand[i] += step
        cand = sorted(set(cand))
        if len(cand) < 2:
            continue
        A = _build_nested(base, cand)
        if len(set(A)) < 2:
            continue
        s = _score(A)
        if s >= cur_score:
            cur, cur_score = cand, s
            if s > best_score:
                best, best_score = cand[:], s
        elif rng.random() < 0.05:
            cur, cur_score = cand, s
    return best, best_score


def solve():
    """Return A with large A-A and small A+A via nested-interval construction."""
    rng = random.Random(987654321)
    deadline = time.time() + 110

    best = None
    best_score = -1.0

    # Base sizes: small Sidon-like blocks whose internal differences are all distinct.
    base_sizes = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64]
    # Number of blocks (copies).
    block_counts = [2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80]

    for bn in base_sizes:
        if time.time() > deadline - 10:
            break
        for seed in range(3):
            base = _greedy_sidon_base(bn, seed=seed * 1000 + bn)
            if len(base) < 3:
                continue
            base_span = base[-1] if base else 1
            # Choose spacing M so that distinct blocks don't overlap and
            # differences between blocks are well-separated.
            M = base_span + 1
            for K in block_counts:
                if time.time() > deadline - 5:
                    break
                if bn * K > 3800:
                    continue
                # Offsets: tightly packed in a short arithmetic progression.
                # Tight packing causes many sum collisions.
                offsets = [k * M for k in range(K)]
                A = _build_nested(base, offsets)
                if len(set(A)) < 2:
                    continue
                s = _score(A)
                if s > best_score:
                    best_score = s
                    best = sorted(set(A))

                # Try a few random perturbations of the spacing to encourage collisions.
                for trial in range(2):
                    if time.time() > deadline - 5:
                        break
                    off2 = offsets[:]
                    j = rng.randrange(len(off2))
                    off2[j] += rng.randint(-M // 2, M // 2)
                    if len(set(off2)) < len(off2):
                        continue
                    A2 = _build_nested(base, sorted(off2))
                    if len(set(A2)) < 2:
                        continue
                    s2 = _score(A2)
                    if s2 > best_score:
                        best_score = s2
                        best = sorted(set(A2))

    if best is None:
        best = [7, 15, 18, 22, -3, -2]
        best_score = _score(best)

    # Final polish: local search over offsets of the best construction.
    # Reconstruct base/offsets from best if it is a nested build.
    # We approximate by trying a generic offset refinement on a fresh base.
    t_left = deadline - time.time()
    if t_left > 2:
        # Use the best construction as a starting point for element-level polish,
        # but only allow moves that preserve/improve the score.
        cur = best[:]
        cur_score = best_score
        n = len(cur)
        step = max(1, (max(cur) - min(cur)) // max(1, n))
        while time.time() < deadline:
            cand = cur[:]
            i = rng.randrange(n)
            cand[i] += rng.randint(-step, step)
            if len(set(cand)) < 2:
                continue
            s = _score(cand)
            if s > cur_score:
                cur, cur_score = cand, s
                if s > best_score:
                    best, best_score = cand[:], s
            elif rng.random() < 0.01:
                cur = best[:]
                cur_score = best_score

    return sorted(set(best))
# EVOLVE-BLOCK-END
