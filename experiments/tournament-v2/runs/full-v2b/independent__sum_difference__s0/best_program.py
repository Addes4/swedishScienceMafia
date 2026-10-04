import math
import random
import time


def _score(a):
    if len(a) < 2:
        return 0.0
    aa = list(a)
    diffs = set()
    sums = set()
    n = len(aa)
    for i in range(n):
        ai = aa[i]
        for j in range(n):
            aj = aa[j]
            diffs.add(ai - aj)
            sums.add(ai + aj)
    return math.log(len(diffs)) / math.log(len(sums))


def _score_bonus(a):
    s = _score(a)
    if len(a) >= 1:
        s += (1.0 - 1.0 / len(a)) / 100.0
    return s


def _build_from_seed(seed, shift, layers):
    """A = seed + k*shift for k in 0..layers-1"""
    A = []
    for k in range(layers):
        off = k * shift
        for x in seed:
            A.append(x + off)
    return sorted(set(A))


def _seed_search(tlimit=8.0):
    """Find a good compact seed set with strong difference/sum ratio."""
    best = [0, 1]
    best_r = 0.0
    rng = random.Random(12345)
    deadline = time.time() + tlimit
    # start from small known-good sets
    seeds = [
        [0, 1, 3, 7],
        [0, 1, 3, 6],
        [0, 1, 4, 6],
        [0, 1, 3, 7, 12],
        [0, 1, 4, 9, 15],
        [0, 1, 3, 7, 15],
        [0, 1, 3, 7, 12, 20],
    ]
    for s in seeds:
        r = _score(s)
        if r > best_r:
            best_r = r
            best = s[:]
    # local search: small sets, coordinate moves
    cur = best[:]
    cur_r = best_r
    while time.time() < deadline:
        cand = cur[:]
        op = rng.random()
        if op < 0.5 and len(cand) > 2:
            i = rng.randrange(len(cand))
            cand[i] += rng.randint(-4, 4)
        elif op < 0.8:
            cand.append(rng.randint(0, 30))
        elif len(cand) > 3:
            i = rng.randrange(len(cand))
            del cand[i]
        cand = sorted(set(cand))
        if len(cand) < 2 or len(cand) > 10:
            continue
        if min(cand) < 0 or max(cand) > 60:
            continue
        r = _score(cand)
        if r > cur_r:
            cur, cur_r = cand, r
            if r > best_r:
                best, best_r = cand[:], r
        elif rng.random() < 0.15:
            cur, cur_r = best[:], best_r
    return best


def _eval_full(A):
    A = sorted(set(A))
    if len(A) < 2:
        return -1.0
    n = len(A)
    diffs = set()
    sums = set()
    for i in range(n):
        ai = A[i]
        for j in range(n):
            aj = A[j]
            diffs.add(ai - aj)
            sums.add(ai + aj)
    if len(sums) == 0:
        return -1.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1.0 - 1.0 / len(A)) / 100.0


def solve():
    rng = random.Random(999)
    deadline = time.time() + 115.0

    # Phase 1: get a good seed.
    seed = _seed_search(tlimit=min(10.0, deadline - time.time() - 5))
    if len(seed) < 2:
        seed = [0, 1, 3, 7]

    bestA = list(seed)
    bestS = _eval_full(bestA)

    # Phase 2: layered construction A = seed + k*shift, tune shift & layers.
    # Also consider copies with variable shifts (geometric spacing) to reduce sums.
    seed_rng = seed[:]
    base = seed[:]

    # Try layered copies with uniform shift and with geometric shifts
    shift_scales = [1, 2, 3, 4, 5, 7, 10, 13, 17, 23, 31, 41, 53, 67, 83, 101,
                    127, 157, 191, 233, 283, 341, 409, 491, 587, 701, 839, 1003,
                    1199, 1433, 1711, 2045, 2443, 2917, 3485, 4163, 4973, 5939,
                    7093, 8471, 10117, 12083, 14431, 17233, 20579, 24571, 29341,
                    35035, 41837, 49961, 59657, 71231]
    seedspan = max(base) - min(base)
    seedspan = max(seedspan, 1)

    candidates = []

    # candidate generators
    for sc in shift_scales:
        sft = sc * seedspan + rng.randint(0, 5)
        if sft <= 0:
            continue
        for layers in range(2, 14):
            A = _build_from_seed(base, sft, layers)
            if len(A) > 4000:
                break
            candidates.append(A)

    # geometric spacing layered: shifts grow by factor
    for grow in [2, 3, 4, 5, 6]:
        for start in [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]:
            for layers in range(2, 12):
                A = []
                off = 0
                step = start
                for k in range(layers):
                    for x in base:
                        A.append(x + off)
                    off += step
                    step *= grow
                    if len(A) > 4000:
                        break
                if len(A) > 4000:
                    continue
                candidates.append(A)

    # random sparse layered: combine several random shifts
    for _ in range(400):
        layers_count = rng.randint(2, 20)
        A = []
        off = 0
        for k in range(layers_count):
            for x in base:
                A.append(x + off)
            off += rng.randint(seedspan + 1, seedspan * 200 + 200)
            if len(A) > 4000:
                break
        if len(A) <= 4000:
            candidates.append(A)

    # Evaluate candidates quickly (dedupe / cap size). Score incrementally is hard,
    # so evaluate a bounded number fully.
    scored = []
    for A in candidates:
        A = sorted(set(A))
        if len(A) < 2 or len(A) > 4000:
            continue
        scored.append(A)

    # Evaluate top candidates by heuristic count first if many
    def rough(A):
        n = len(A)
        return n

    scored.sort(key=rough, reverse=True)

    # Evaluate fully, but limited by deadline
    eval_list = scored[:2000]
    for A in eval_list:
        if time.time() > deadline:
            break
        s = _eval_full(A)
        if s > bestS:
            bestS = s
            bestA = A

    # Phase 3: local search on best layered set (move whole layer offsets sometimes)
    A = bestA[:]
    cur = A[:]
    curS = bestS
    while time.time() < deadline:
        cand = cur[:]
        r = rng.random()
        if r < 0.5:
            # perturb a few elements
            for _ in range(rng.randint(1, 3)):
                i = rng.randrange(len(cand))
                cand[i] += rng.choice([-1, 1, -2, 2, -3, 3, -seedspan, seedspan,
                                       -2 * seedspan, 2 * seedspan])
        elif r < 0.8:
            # add element in a gap
            x = rng.randint(min(cand), max(cand))
            cand.append(x)
        else:
            # remove an element
            if len(cand) > max(3, len(base)):
                i = rng.randrange(len(cand))
                del cand[i]
        cand = sorted(set(cand))
        if len(cand) < 2 or len(cand) > 4000:
            continue
        s = _eval_full(cand)
        if s > curS:
            cur, curS = cand, s
            if s > bestS:
                bestS = s
                bestA = cand[:]
        elif rng.random() < 0.2:
            cur, curS = bestA[:], bestS

    # final polish with dedicated difference-sum optimization on smaller version
    A = sorted(set(bestA))
    return A
