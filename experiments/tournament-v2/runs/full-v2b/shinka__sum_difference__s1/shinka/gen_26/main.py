# EVOLVE-BLOCK-START
"""Annealed SA with periodic restarts from dense-core + bounded-Sidon seeds."""
import math
import random
import time


def _stats(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0, 0
    diffs = set()
    sums = set()
    for i in range(n):
        ai = a[i]
        for j in range(i, n):
            aj = a[j]
            diffs.add(ai - aj)
            diffs.add(aj - ai)
            sums.add(ai + aj)
    return len(diffs), len(sums)


def _score(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _stats(a)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns) + (1 - 1 / n) / 100


def _score_pure(a):
    """Pure log-ratio without the size bonus; used for ratio-aware seed ranking."""
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _stats(a)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns)


def _greedy_golomb(n, max_val, rng):
    """Greedy near-Golomb ruler with n marks in [0, max_val]."""
    marks = [0]
    used = set()
    candidates = list(range(1, max_val + 1))
    rng.shuffle(candidates)
    for _ in range(n - 1):
        best_c, best_gain = None, -1
        for c in candidates[:min(300, len(candidates))]:
            if c in marks:
                continue
            new_d = set()
            ok = True
            for m in marks:
                d = abs(c - m)
                if d in new_d:
                    ok = False
                    break
                new_d.add(d)
            if not ok:
                continue
            gain = len(new_d - used)
            if gain > best_gain:
                best_gain = gain
                best_c = c
                if gain == len(marks):
                    break
        if best_c is None:
            for c in candidates:
                if c not in marks:
                    best_c = c
                    break
        if best_c is None:
            break
        marks.append(best_c)
        for m in marks[:-1]:
            used.add(abs(best_c - m))
    return marks


def _bounded_sidon(m, rng):
    """Classic bounded Sidon family {i*m + (i^2 mod m) : 0<=i<m}."""
    if m < 2:
        return [0]
    s = []
    for i in range(m):
        s.append(i * m + (i * i) % m)
    return s


def _dense_core_sidon(m, sidon_m, gap, rng):
    """Dense core {0..m} plus a bounded-Sidon block offset by gap."""
    core = list(range(m + 1))
    s = _bounded_sidon(sidon_m, rng)
    offset = m + gap
    return core + [offset + x for x in s]


def _dense_core_golomb(m, gs, gap, rng):
    core = list(range(m + 1))
    g = _greedy_golomb(gs, max(60, gs * gs), rng)
    offset = m + gap
    return core + [offset + x for x in g]


def _local_search(a, deadline, rng, T0=0.12, accept_floor=0.001):
    """SA with higher early acceptance and annealed temperature."""
    a = sorted(set(a))
    best = a[:]
    best_score = _score(a)
    cur = a[:]
    cur_score = best_score
    T = T0
    steps = 0
    last_improve = time.time()
    while time.time() < deadline:
        steps += 1
        if steps % 1500 == 0:
            T = max(accept_floor, T * 0.97)
        # stagnation restart: bump temperature and reset to best
        if time.time() - last_improve > 20:
            cur = best[:]
            cur_score = best_score
            T = min(T0, T * 3.0)
            last_improve = time.time()
        cand = cur[:]
        op = rng.random()
        if op < 0.35 and cand:
            i = rng.randrange(len(cand))
            j = rng.randrange(len(cand))
            d = cand[i] - cand[j]
            if d == 0:
                d = rng.randint(1, 20)
            cand[i] = cand[j] + d + rng.randint(-3, 3)
        elif op < 0.55 and len(cand) < 4000:
            x = rng.choice(cand)
            y = rng.choice(cand)
            cand.append(x + (x - y) + rng.randint(-2, 2))
        elif op < 0.7 and len(cand) < 4000:
            # add a bounded-Sidon style element
            base = rng.choice(cand)
            cand.append(base + rng.randint(1, 200))
        elif op < 0.85 and len(cand) > 3:
            cand.pop(rng.randrange(len(cand)))
        else:
            if len(cand) >= 2:
                i, j = rng.randrange(len(cand)), rng.randrange(len(cand))
                cand[i], cand[j] = cand[j], cand[i]
        cand = sorted(set(cand))
        if len(cand) < 2:
            continue
        s = _score(cand)
        if s > cur_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-9)):
            cur, cur_score = cand, s
            if s > best_score:
                best = cand[:]
                best_score = s
                last_improve = time.time()
    return best, best_score


def solve():
    rng = random.Random(20240517)
    deadline = time.time() + 110

    best = [0, 1, 3]
    best_score = _score(best)

    # Ratio-aware top-K seed collector: keep top K seeds by PURE log-ratio.
    K = 8
    top_seeds = []  # list of (pure_score, tuple(cand)) kept sorted descending

    def _offer(cand):
        cand = sorted(set(cand))
        if len(cand) < 2:
            return
        ps = _score_pure(cand)
        key = tuple(cand)
        for i, (_, c) in enumerate(top_seeds):
            if c == key:
                return
        top_seeds.append((ps, key))
        top_seeds.sort(key=lambda t: -t[0])
        if len(top_seeds) > K:
            top_seeds.pop()

    # Phase 1: sweep structured seeds (dense-core + Sidon, dense-core + Golomb, pure Sidon)
    phase1_deadline = time.time() + 22
    seeds = []
    for m in range(0, 14):
        for sm in range(2, 16):
            for gap in [1, 2, 3, 5, 8, 13, 21]:
                seeds.append(("sidon", m, sm, gap))
    for m in range(0, 12):
        for gs in range(3, 14):
            for gap in [1, 2, 3, 5, 8, 13]:
                seeds.append(("golomb", m, gs, gap))
    rng.shuffle(seeds)
    for kind, m, k, gap in seeds:
        if time.time() > phase1_deadline:
            break
        if kind == "sidon":
            cand = _dense_core_sidon(m, k, gap, rng)
        else:
            cand = _dense_core_golomb(m, k, gap, rng)
        cand = sorted(set(cand))
        if len(cand) < 2:
            continue
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]
        _offer(cand)

    # Pure Sidon families
    for m in range(2, 40):
        if time.time() > phase1_deadline + 3:
            break
        cand = _bounded_sidon(m, rng)
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]
        _offer(cand)

    # Pure dense intervals
    for n in range(2, 80):
        if time.time() > phase1_deadline + 5:
            break
        cand = list(range(n))
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]
        _offer(cand)

    # Phase 2: refine EACH of the top-K seeds in order of pure ratio.
    n_top = len(top_seeds)
    for rank, (_, seed_t) in enumerate(top_seeds):
        if time.time() >= deadline - 4:
            break
        seed = list(seed_t)
        # Allocate the remaining budget across the remaining top seeds.
        remaining = deadline - time.time()
        slots_left = n_top - rank
        slice_budget = max(4.0, min(remaining - 3.0, remaining / max(1, slots_left)))
        sub_deadline = time.time() + slice_budget
        cand, s = _local_search(seed, sub_deadline, rng, T0=0.12)
        if s > best_score:
            best, best_score = cand, s

    # Phase 3: restarts from dense-core Sidon/Golomb seeds until deadline
    while time.time() < deadline:
        remaining = deadline - time.time()
        if remaining < 4:
            break
        m = rng.randint(0, 12)
        gap = rng.choice([1, 2, 3, 5, 8, 13, 21])
        if rng.random() < 0.6:
            sm = rng.randint(2, 15)
            seed = _dense_core_sidon(m, sm, gap, rng)
        else:
            gs = rng.randint(3, 13)
            seed = _dense_core_golomb(m, gs, gap, rng)
        sub_deadline = time.time() + min(remaining, 15)
        cand, s = _local_search(seed, sub_deadline, rng, T0=0.12)
        if s > best_score:
            best, best_score = cand, s

    return sorted(set(best))
# EVOLVE-BLOCK-END