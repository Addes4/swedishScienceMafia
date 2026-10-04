# EVOLVE-BLOCK-START
"""Greedy + simulated annealing search for sets with large difference set and small sum set."""
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


def _greedy_build(n, hi, rng):
    """Build a set of size n greedily, choosing each new element to maximise score."""
    a = [0, 1]
    while len(a) < n:
        best_x = None
        best_s = -1.0
        # sample candidates
        cands = set()
        for _ in range(60):
            cands.add(rng.randint(-hi, hi))
        # also try perturbations of existing elements (differences)
        base = list(a)
        for _ in range(40):
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


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
    rng = random.Random(12345)
    deadline = time.time() + 110

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score(best)

    # Try greedy constructions of various sizes
    for n in [6, 8, 10, 12, 15, 18, 22, 28, 35, 45, 60]:
        if time.time() > deadline:
            break
        for hi in [20, 60, 200, 1000]:
            if time.time() > deadline:
                break
            a = _greedy_build(n, hi, rng)
            s = _score(a)
            if s > best_score:
                best, best_score = a[:], s

    # Simulated annealing refinement
    cur = best[:]
    cur_score = best_score
    T = 0.05
    step = 0
    while time.time() < deadline:
        step += 1
        if step % 2000 == 0:
            T = max(0.001, T * 0.999)
        cand = cur[:]
        op = rng.random()
        if op < 0.5 and cand:
            i = rng.randrange(len(cand))
            cand[i] += rng.randint(-5, 5)
        elif op < 0.8:
            cand.append(rng.randint(-50, 50))
        elif op < 0.9 and len(cand) > 3:
            cand.pop(rng.randrange(len(cand)))
        else:
            if len(cand) >= 2:
                i, j = rng.randrange(len(cand)), rng.randrange(len(cand))
                cand[i], cand[j] = cand[j], cand[i]
        cand = list(set(cand))
        if len(cand) < 2:
            continue
        s = _score(cand)
        if s > cur_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-9)):
            cur, cur_score = cand, s
            if s > best_score:
                best, best_score = cand[:], s
    return sorted(set(best))
# EVOLVE-BLOCK-END