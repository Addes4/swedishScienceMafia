# EVOLVE-BLOCK-START
"""Multiplicative Sidon construction with dense-core embedding for log|A-A|/log|A+A|."""
import math
import random
import time


def _score(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    diffs = set()
    sums = set()
    for x in a:
        for y in a:
            diffs.add(x - y)
            sums.add(x + y)
    if len(sums) <= 1:
        return 0.0
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / n) / 100


def _parts(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0, 0, 0
    diffs = set()
    sums = set()
    for x in a:
        for y in a:
            diffs.add(x - y)
            sums.add(x + y)
    if len(sums) <= 1:
        return 0.0, len(diffs), len(sums)
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / n) / 100, len(diffs), len(sums)


def _is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def _bose_chowla(q):
    """Bose-Chowla Sidon set of size q in Z_{q^2-1}.
    Uses primitive element of GF(q^2). For prime q, we construct via
    the standard formula: theta is a primitive element of GF(q^2),
    and {i : theta^i - theta in GF(q)} gives q indices in Z_{q^2-1}.
    Here we use a simpler explicit construction: for prime q,
    the set {2*q*i + (i^2 mod q) : i=0..q-1} is Sidon in Z_{2q^2}."""
    # Use the classic Sidon set in Z_{q^2-1} via Bose-Chowla:
    # For prime q, indices i in [0, q^2-2] such that i is a "Singer difference set"
    # Simpler: use the Welch construction: for prime q, set
    # {2*q*i + (i^2 mod q) : i in [0,q-1]} is Sidon in Z_{2q^2}
    # But better: use the Bose construction {i^2 + i*alpha : ...}
    # We'll use the well-known Singer difference set in Z_{q^2+q+1}
    # For practical small q, use the quadratic construction:
    # S = {2*q*i + (i^2 mod q)} has |S-S| roughly q^2 and |S+S| roughly q^2/2
    return [2 * q * i + (i * i) % q for i in range(q)]


def _golomb_ruler(n, rng, max_tries=300):
    """Greedy construction of a near-optimal Golomb ruler with n marks."""
    if n <= 1:
        return [0]
    marks = [0]
    used = set()
    # candidate pool grows; use difference-targeting
    for _ in range(n - 1):
        best_c = None
        best_score = -1
        # sample candidate additions
        span = max(20, 4 * n * n)
        for _ in range(max_tries):
            c = rng.randint(1, span)
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
            if gain > best_score:
                best_score = gain
                best_c = c
        if best_c is None:
            # fallback: pick any unused value
            c = 1
            while c in marks:
                c += 1
            best_c = c
        marks.append(best_c)
        for m in marks[:-1]:
            used.add(abs(best_c - m))
    return sorted(marks)


def _build_sidon_embed(q, base_mult, gap, rng):
    """Build a set = dense core + scaled Sidon tail."""
    core_size = max(1, q // 2)
    core = list(range(core_size))
    sidon = _bose_chowla(q)
    # lift to integer with multiplicative scaling
    tail = [base_mult * s + gap for s in sidon]
    return sorted(set(core + tail))


def _build_dense_golomb(m, gs, gap, rng):
    core = list(range(m + 1))
    if gs <= 0:
        return core
    g = _golomb_ruler(gs, rng)
    offset = m + gap
    return sorted(set(core + [offset + x for x in g]))


def _reflect(a, center, k):
    """Reflect the top k elements through center."""
    a = sorted(set(a))
    if k <= 0 or k >= len(a):
        return a
    head = a[:len(a) - k]
    tail = a[len(a) - k:]
    reflected = [2 * center - x for x in tail]
    return sorted(set(head + reflected))


def _reflection_polish(a, deadline, rng):
    """Try reflections through various centers to collapse sums."""
    best = sorted(set(a))
    best_s = _score(best)
    while time.time() < deadline:
        improved = False
        n = len(best)
        if n < 4:
            break
        for q_idx in [0.3, 0.4, 0.5, 0.6, 0.7]:
            idx = int(q_idx * (n - 1))
            center = best[idx]
            for frac in [0.15, 0.25, 0.35, 0.45]:
                k = max(1, int(frac * n))
                cand = _reflect(best, center, k)
                if len(cand) < 2:
                    continue
                s = _score(cand)
                if s > best_s:
                    best = cand
                    best_s = s
                    improved = True
        if not improved:
            break
    return best, best_s


def _targeted_grow(a, deadline, rng, max_size=4000):
    """Greedily add elements maximizing new differences while minimizing new sums."""
    a = sorted(set(a))
    cur_d = set()
    cur_s = set()
    for x in a:
        for y in a:
            cur_d.add(x - y)
            cur_s.add(x + y)
    cur_score = _score(a)
    while time.time() < deadline and len(a) < max_size:
        n = len(a)
        candidates = set()
        # candidate pool based on existing structure
        for _ in range(200):
            i = rng.randrange(n)
            j = rng.randrange(n)
            base = 2 * a[i] - a[j]
            candidates.add(base)
            candidates.add(base + rng.randint(-3, 3))
        for _ in range(50):
            i = rng.randrange(n)
            candidates.add(a[i] + rng.randint(1, 50))
            candidates.add(a[i] - rng.randint(1, 50))
        for v in range(0, 30):
            candidates.add(v)
        best_c = None
        best_gain = -1e18
        for c in candidates:
            if c in a:
                continue
            new_d = set()
            new_s = set()
            for z in a:
                new_d.add(c - z)
                new_d.add(z - c)
                new_s.add(c + z)
            d_gain = len(new_d - cur_d)
            s_cost = len(new_s - cur_s)
            gain = d_gain - 0.35 * s_cost
            if gain > best_gain:
                best_gain = gain
                best_c = c
        if best_c is None:
            break
        trial = sorted(set(a + [best_c]))
        s = _score(trial)
        if s > cur_score:
            a = trial
            cur_score = s
            for z in a:
                cur_d.add(best_c - z)
                cur_d.add(z - best_c)
                cur_s.add(best_c + z)
        else:
            # try a batch
            improved = False
            batch = []
            for c in candidates:
                if c in a:
                    continue
                new_d = set()
                new_s = set()
                for z in a:
                    new_d.add(c - z)
                    new_d.add(z - c)
                    new_s.add(c + z)
                gain = len(new_d - cur_d) - 0.35 * len(new_s - cur_s)
                batch.append((gain, c))
            batch.sort(reverse=True)
            for _, c in batch[:40]:
                trial = sorted(set(a + [c]))
                if _score(trial) > cur_score:
                    a = trial
                    cur_score = _score(a)
                    cur_d = set()
                    cur_s = set()
                    for x in a:
                        for y in a:
                            cur_d.add(x - y)
                            cur_s.add(x + y)
                    improved = True
                    break
            if not improved:
                break
    return a, cur_score


def _prune(a, deadline, rng):
    a = sorted(set(a))
    cur = _score(a)
    improved = True
    while improved and time.time() < deadline:
        improved = False
        order = list(range(len(a)))
        rng.shuffle(order)
        for i in order:
            if len(a) <= 3:
                break
            trial = a[:i] + a[i+1:]
            s = _score(trial)
            if s > cur:
                a = trial
                cur = s
                improved = True
                break
    return a, cur


def _local_search(a, deadline, rng):
    """Targeted local search with ratio-aware moves."""
    cur = sorted(set(a))
    cur_s = _score(cur)
    best = cur[:]
    best_s = cur_s
    T = 0.05
    step = 0
    while time.time() < deadline:
        step += 1
        if step % 800 == 0:
            T = max(0.0003, T * 0.996)
        cand = cur[:]
        op = rng.random()
        if op < 0.35 and cand:
            # shift an element
            i = rng.randrange(len(cand))
            if len(cand) > 1:
                j = rng.randrange(len(cand))
                d = cand[i] - cand[j]
                if d == 0:
                    d = rng.randint(1, 20)
                cand[i] = cand[j] + d + rng.randint(-2, 2)
        elif op < 0.6 and len(cand) < 4000:
            # add a targeted element
            if len(cand) >= 2:
                x = rng.choice(cand)
                y = rng.choice(cand)
                cand.append(x + (x - y) + rng.randint(-1, 1))
        elif op < 0.78 and len(cand) > 3:
            cand.pop(rng.randrange(len(cand)))
        else:
            if len(cand) >= 2:
                i, j = rng.randrange(len(cand)), rng.randrange(len(cand))
                cand[i], cand[j] = cand[j], cand[i]
        cand = sorted(set(cand))
        if len(cand) < 2:
            continue
        s = _score(cand)
        if s > cur_s or rng.random() < math.exp((s - cur_s) / max(T, 1e-9)):
            cur = cand
            cur_s = s
            if s > best_s:
                best = cand[:]
                best_s = s
        if rng.random() < 0.01:
            cur = best[:]
            cur_s = best_s
    return best, best_s


def solve():
    rng = random.Random(20240817)
    deadline = time.time() + 110

    best = [0, 1, 3]
    best_score = _score(best)

    # Phase 1: algebraic Sidon embeddings (Bose-Chowla style)
    phase1 = time.time() + 30
    for q in range(3, 60):
        if time.time() > phase1:
            break
        if not _is_prime(q):
            continue
        for base_mult in [1, 2, 3, 4, 5, 7, 10, 15, 20, 30]:
            for gap in [0, 1, 2, 3, 5, 8, 13, 21, 34, 55]:
                cand = _build_sidon_embed(q, base_mult, gap, rng)
                if len(cand) < 2:
                    continue
                s = _score(cand)
                if s > best_score:
                    best_score = s
                    best = cand[:]

    # Phase 2: dense + Golomb sweeps
    phase2 = time.time() + 20
    configs = []
    for m in range(0, 20):
        for gs in range(2, 20):
            for gap in [1, 2, 3, 5, 8, 13, 21]:
                configs.append((m, gs, gap))
    rng.shuffle(configs)
    for (m, gs, gap) in configs:
        if time.time() > phase2:
            break
        cand = _build_dense_golomb(m, gs, gap, rng)
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    # Pure dense intervals
    for n in range(2, 200):
        cand = list(range(n))
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    # Phase 3: reflection polish
    if time.time() < deadline:
        sub = time.time() + 10
        cand, s = _reflection_polish(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 4: targeted growth
    if time.time() < deadline:
        sub = time.time() + 20
        cand, s = _targeted_grow(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 5: local search
    if time.time() < deadline:
        sub = time.time() + 15
        cand, s = _local_search(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 6: prune
    if time.time() < deadline:
        sub = time.time() + 5
        cand, s = _prune(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 7: restarts with diverse seeds
    while time.time() < deadline:
        remaining = deadline - time.time()
        if remaining < 4:
            break
        choice = rng.random()
        if choice < 0.4:
            q = rng.choice([3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47])
            bm = rng.choice([1, 2, 3, 5, 7, 10, 15])
            gap = rng.randint(0, 50)
            seed = _build_sidon_embed(q, bm, gap, rng)
        elif choice < 0.75:
            m = rng.randint(0, 18)
            gs = rng.randint(2, 18)
            gap = rng.choice([1, 2, 3, 5, 8, 13, 21])
            seed = _build_dense_golomb(m, gs, gap, rng)
        else:
            n = rng.randint(3, 60)
            seed = list(range(n))
        sub = time.time() + min(remaining, 8)
        cand, s = _targeted_grow(seed, sub, rng)
        if time.time() < deadline:
            sub2 = time.time() + min(deadline - time.time(), 3)
            cand, s = _local_search(cand, sub2, rng)
        if s > best_score:
            best, best_score = cand, s

    # Final polish
    if time.time() < deadline + 5:
        try:
            cand, s = _reflection_polish(best, time.time() + 3, rng)
            if s > best_score:
                best, best_score = cand, s
        except Exception:
            pass

    # Deduplicate and sanitize
    out = sorted(set(int(x) for x in best))
    if len(out) > 4000:
        out = out[:4000]
    return out
# EVOLVE-BLOCK-END