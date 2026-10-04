# EVOLVE-BLOCK-START
"""Hybrid solver combining dilated Golomb/Sidon constructions with aggressive
sum-collapse local search (target-sum moves) to maximize log|A-A|/log|A+A|."""
import math
import random
import time


# ---------------------------------------------------------------- scoring
def _diffs_sums(a):
    diffs = set()
    sums = set()
    for x in a:
        for y in a:
            diffs.add(x - y)
            sums.add(x + y)
    return diffs, sums


def _score_from(diffs, sums, n):
    if len(sums) < 2 or n < 2:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / n) / 100


def _score(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    diffs, sums = _diffs_sums(a)
    return _score_from(diffs, sums, n)


# ---------------------------------------------------------------- constructions
def greedy_golomb(n, max_val=None, seed=0):
    """Greedy Golomb ruler: add smallest integer keeping all differences distinct."""
    marks = [0]
    used_diffs = {0}
    candidate = 1
    while len(marks) < n:
        ok = True
        new_diffs = []
        for m in marks:
            d = candidate - m
            if d in used_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            for d in new_diffs:
                used_diffs.add(d)
                used_diffs.add(-d)
            marks.append(candidate)
            candidate += 1
        else:
            candidate += 1
            if max_val is not None and candidate > max_val:
                break
    return marks


def greedy_sidon_weighted(n, weight=0.5, window=200, seed=0):
    """Greedy Sidon-like: prefer candidates adding many diffs, few sums."""
    marks = [0, 1]
    while len(marks) < n:
        existing_diffs = set()
        existing_sums = set()
        for x in marks:
            for y in marks:
                existing_diffs.add(x - y)
                existing_sums.add(x + y)
        best_c = None
        best_cost = None
        start = marks[-1] + 1
        for c in range(start, start + window):
            diffs = set()
            sums = set()
            for m in marks:
                diffs.add(c - m)
                diffs.add(m - c)
                sums.add(c + m)
            nd = len(diffs - existing_diffs)
            ns = len(sums - existing_sums)
            cost = ns - weight * nd
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_c = c
        if best_c is None:
            best_c = marks[-1] + 1
        marks.append(best_c)
    return marks


def ratio_greedy(n, seed=0, window=80):
    """Greedily add the candidate maximizing the marginal ratio."""
    A = [0, 1]
    target = n
    while len(A) < target:
        base_score = _score(A)
        best_c = None
        best_s = base_score
        start = A[-1] + 1
        for c in range(start, start + window):
            cand = A + [c]
            s = _score(cand)
            if s > best_s:
                best_s = s
                best_c = c
        if best_c is None:
            best_c = A[-1] + 1
        A.append(best_c)
    return A


def dilate(base, T, K):
    """A = base + T*{0..K-1}: differences multiply, sums concentrate."""
    out = set()
    for k in range(K):
        off = T * k
        for b in base:
            out.add(b + off)
    return sorted(out)


def multi_band(base, gaps):
    """A = union of base + g for g in gaps."""
    out = set()
    for g in gaps:
        for b in base:
            out.add(b + g)
    return sorted(out)


def _beatty(alpha, n, start=1):
    """Return {floor(k*alpha) : k = start .. start+n-1}."""
    return sorted({int(math.floor(k * alpha)) for k in range(start, start + n)})


def _beatty_pair(alpha, beta, n, start=1):
    """Return {floor(k*alpha) + floor(k*beta) : k = start .. start+n-1}."""
    return sorted({int(math.floor(k * alpha) + math.floor(k * beta))
                   for k in range(start, start + n)})


def _beatty_two_irr(alpha, beta, n, start=1):
    """Return {floor(k*alpha) + floor(j*beta) : 1<=k,j<=n} (cross-sum)."""
    A = [int(math.floor(k * alpha)) for k in range(start, start + n)]
    B = [int(math.floor(k * beta)) for k in range(start, start + n)]
    out = set()
    for x in A:
        for y in B:
            out.add(x + y)
    return sorted(out)


# ---------------------------------------------------------------- moves
def _target_sum_move(a, rng, multi=1):
    """Force one (or more) sum collisions.

    target = a[j1] + a[j2]; new_val = target - a[j3].
    Then a[k] + a[j3] == a[j1] + a[j2], collapsing one sum.
    """
    n = len(a)
    if n < 4:
        return a
    cand = a[:]
    for _ in range(multi):
        j1 = rng.randrange(n)
        j2 = rng.randrange(n)
        if j1 == j2:
            continue
        target = a[j1] + a[j2]
        j3 = rng.randrange(n)
        new_val = target - a[j3]
        k = rng.randrange(n)
        if new_val == cand[k]:
            continue
        if new_val in cand and new_val != cand[k]:
            new_val += rng.choice([-1, 1])
            if new_val in cand:
                continue
        cand[k] = new_val
    return cand


def _difference_move(a, rng):
    """Push an element far out to expand the difference set."""
    n = len(a)
    if n < 2:
        return a
    cand = a[:]
    lo = min(cand)
    hi = max(cand)
    span = max(1, hi - lo)
    i = rng.randrange(n)
    cand[i] = hi + rng.randint(1, max(2, span))
    return cand


def _perturb_move(a, rng):
    """Small local perturbation."""
    n = len(a)
    if n < 2:
        return a
    cand = a[:]
    i = rng.randrange(n)
    lo = min(cand)
    hi = max(cand)
    span = max(1, hi - lo)
    cand[i] += rng.randint(-max(1, span // 10), max(1, span // 10))
    return cand


def _shift_move(a, rng):
    shift = rng.randint(-3, 3)
    return [x + shift for x in a]


def _dedup(a):
    return sorted(set(a))


# ---------------------------------------------------------------- local search
def local_search(a, deadline, best_global_score, temperature=3.0):
    """Hill-climb with adaptive temperature."""
    a = list(set(a))
    if len(a) < 2:
        return a, _score(a)
    cur_score = _score(a)
    best = a[:]
    best_score = cur_score
    lo = min(a)
    hi = max(a)
    span = max(1, hi - lo)
    step_base = max(1, span // 20)
    rng = random.Random()
    while time.time() < deadline:
        move = rng.random()
        cand = a[:]
        if move < 0.45 and cand:
            i = rng.randrange(len(cand))
            step = max(1, int(step_base * (0.1 + temperature * rng.random())))
            cand[i] += rng.randint(-step, step)
        elif move < 0.7:
            new_val = rng.randint(lo - span, hi + span)
            cand.append(new_val)
        elif move < 0.9 and len(cand) > 3:
            i = rng.randrange(len(cand))
            cand.pop(i)
        else:
            shift = rng.randint(-step_base, step_base)
            cand = [x + shift for x in cand]
        cand = list(set(cand))
        if len(cand) < 2 or len(cand) > 4000:
            continue
        s = _score(cand)
        if s > cur_score:
            a = cand
            cur_score = s
            if s > best_score:
                best = cand[:]
                best_score = s
        elif rng.random() < 0.03:
            a = cand
            cur_score = s
        temperature *= 0.9999
    return best, best_score


# ---------------------------------------------------------------- main
def solve():
    rng = random.Random(12345)
    deadline = time.time() + 112
    total = 112

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score(best)

    # ---------- Phase 1: construction warm starts (~10%) ----------
    phase1_end = time.time() + 0.10 * total

    # dilated Golomb
    for gn in [4, 5, 6, 7, 8, 10, 12]:
        if time.time() > phase1_end:
            break
        G = greedy_golomb(gn)
        for K in [2, 3, 4, 5, 6, 8, 10, 12, 16, 20]:
            for T in [3, 5, 7, 9, 11, 13, 17, 19, 23, 29, 31, 37, 41, 47, 53, 61]:
                A = dilate(G, T, K)
                if len(A) < 2 or len(A) > 4000:
                    continue
                s = _score(A)
                if s > best_score:
                    best, best_score = A[:], s

    # dilated Sidon
    for gn in [5, 6, 7, 8, 10]:
        if time.time() > phase1_end:
            break
        for w in [0.3, 0.5, 0.7, 1.0]:
            S = greedy_sidon_weighted(gn, weight=w, window=150)
            for K in [2, 3, 4, 6, 8, 10, 12]:
                for T in [5, 7, 9, 11, 13, 17, 19, 23, 29, 31, 41, 47]:
                    A = dilate(S, T, K)
                    if len(A) < 2 or len(A) > 4000:
                        continue
                    s = _score(A)
                    if s > best_score:
                        best, best_score = A[:], s

    # multi-band
    for gn in [4, 5, 6, 7, 8]:
        if time.time() > phase1_end:
            break
        G = greedy_golomb(gn)
        for gaps in (
            [0, 1, 3, 7, 15, 31, 63],
            [0, 2, 6, 14, 30, 62],
            [0, 1, 4, 10, 22, 46, 94],
            [0, 3, 9, 27, 81],
            [0, 5, 15, 45, 135],
        ):
            A = multi_band(G, gaps)
            if len(A) < 2 or len(A) > 4000:
                continue
            s = _score(A)
            if s > best_score:
                best, best_score = A[:], s

    # ratio-aware greedy
    for n in [8, 12, 16, 20, 25, 30]:
        if time.time() > phase1_end:
            break
        A = ratio_greedy(n, window=60)
        s = _score(A)
        if s > best_score:
            best, best_score = A[:], s

    # ---------- Phase 1b: Beatty / Sturmian seeds (compact) ----------
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    phi2 = phi * phi
    sq2 = 2.0 ** 0.5
    sq3 = 3.0 ** 0.5
    e = math.e
    pi = math.pi

    for alpha in [phi, phi2, sq2, sq3, e, pi]:
        for n in [100, 200, 400]:
            if time.time() > phase1_end:
                break
            A = _beatty(alpha, n)
            if len(A) < 2 or len(A) > 4000:
                continue
            s = _score(A)
            if s > best_score:
                best, best_score = A[:], s

    for n in [100, 200, 400]:
        if time.time() > phase1_end:
            break
        A = _beatty_pair(phi, phi2, n)
        if len(A) < 2 or len(A) > 4000:
            continue
        s = _score(A)
        if s > best_score:
            best, best_score = A[:], s

    for (alpha, beta) in [(phi, sq2), (phi, sq3), (sq2, sq3), (phi, e)]:
        for n in [100, 200, 400]:
            if time.time() > phase1_end:
                break
            A = _beatty_pair(alpha, beta, n)
            if len(A) < 2 or len(A) > 4000:
                continue
            s = _score(A)
            if s > best_score:
                best, best_score = A[:], s

    for (alpha, beta) in [(phi, sq2), (phi, sq3)]:
        for n in [30, 50]:
            if time.time() > phase1_end:
                break
            A = _beatty_two_irr(alpha, beta, n)
            if len(A) < 2 or len(A) > 4000:
                continue
            s = _score(A)
            if s > best_score:
                best, best_score = A[:], s

    # pure Golomb
    for n in [8, 12, 16, 20, 25, 30, 40, 50]:
        if time.time() > phase1_end:
            break
        G = greedy_golomb(n)
        s = _score(G)
        if s > best_score:
            best, best_score = G[:], s

    # ---------- Phase 2: sum-collapse hill-climb (~55%) ----------
    phase2_start = time.time()
    phase2_end = phase2_start + 0.55 * total
    phase2_duration = max(1e-6, phase2_end - phase2_start)
    cur = best[:]
    cd, cs = _diffs_sums(cur)
    cur_score = _score_from(cd, cs, len(cur))
    temperature = 0.05

    while time.time() < phase2_end:
        frac = (time.time() - phase2_start) / phase2_duration
        if frac < 0.30:
            temperature = 0.05
        elif frac < 0.80:
            # linear decay from 0.05 to 0.005 over frac in [0.30, 0.80]
            t = (frac - 0.30) / 0.50
            temperature = 0.05 + t * (0.005 - 0.05)
        else:
            temperature = 0.002
        r = rng.random()
        if r < 0.70:
            multi = 1 if rng.random() < 0.7 else 2
            cand = _target_sum_move(cur, rng, multi=multi)
        elif r < 0.85:
            cand = _difference_move(cur, rng)
        elif r < 0.95:
            cand = _perturb_move(cur, rng)
        else:
            cand = _shift_move(cur, rng)

        cand = _dedup(cand)
        if len(cand) < 2 or len(cand) > 4000:
            continue

        cd2, cs2 = _diffs_sums(cand)
        s = _score_from(cd2, cs2, len(cand))

        if s > cur_score:
            cur, cd, cs, cur_score = cand, cd2, cs2, s
            if s > best_score:
                best, best_score = cand[:], s
        elif rng.random() < temperature:
            cur, cd, cs, cur_score = cand, cd2, cs2, s

        if rng.random() < 0.01:
            cur = best[:]
            cd, cs = _diffs_sums(cur)
            cur_score = _score_from(cd, cs, len(cur))

    # ---------- Phase 3: targeted sum-collapse polish (~25%) ----------
    phase3_end = time.time() + 0.25 * total
    candidates = [best]
    for extra_T in [11, 17, 23, 29, 41]:
        for extra_K in [8, 12, 16]:
            G = greedy_golomb(5)
            A = dilate(G, extra_T, extra_K)
            if 2 <= len(A) <= 4000:
                candidates.append(A)

    for start in candidates:
        if time.time() > phase3_end:
            break
        cur = start[:]
        cd, cs = _diffs_sums(cur)
        cur_score = _score_from(cd, cs, len(cur))
        local_end = min(phase3_end, time.time() + 8)
        while time.time() < local_end:
            cand = _target_sum_move(cur, rng, multi=1)
            cand = _dedup(cand)
            if len(cand) < 2 or len(cand) > 4000:
                continue
            cd2, cs2 = _diffs_sums(cand)
            s = _score_from(cd2, cs2, len(cand))
            if s >= cur_score:
                cur, cd, cs, cur_score = cand, cd2, cs2, s
                if s > best_score:
                    best, best_score = cand[:], s

    # ---------- Phase 4: final polish (~5%) ----------
    cur = best[:]
    cd, cs = _diffs_sums(cur)
    cur_score = _score_from(cd, cs, len(cur))
    while time.time() < deadline:
        cand = _target_sum_move(cur, rng, multi=1)
        if rng.random() < 0.3:
            cand = _perturb_move(cand, rng)
        cand = _dedup(cand)
        if len(cand) < 2 or len(cand) > 4000:
            continue
        cd2, cs2 = _diffs_sums(cand)
        s = _score_from(cd2, cs2, len(cand))
        if s >= cur_score:
            cur, cur_score = cand, s
            if s > best_score:
                best, best_score = cand[:], s

    return sorted(set(best))
# EVOLVE-BLOCK-END