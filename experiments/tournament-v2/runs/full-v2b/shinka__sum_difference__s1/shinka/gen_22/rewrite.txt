# EVOLVE-BLOCK-START
"""Budget-adaptive SA with watchdog restarts over dense-core + Golomb constructions."""
import math
import random
import time


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


def _score_pure(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    nd, ns = _fast_stats(a)
    if ns <= 1:
        return 0.0
    return math.log(nd) / math.log(ns)


def _score(a):
    return _score_fast(a)


def _greedy_golomb(n, hi, rng):
    """Greedy Golomb-like ruler: each new mark maximises new distinct differences."""
    marks = [0]
    used = {0}
    diffs = {0}
    for _ in range(n - 1):
        best_x = None
        best_new = -1
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


def _build_dense_golomb(m, gs, gap, rng, stride=1, scale=1):
    """Dense (or strided) core plus a Golomb-like tail offset by core_end+gap."""
    if stride <= 1:
        core = list(range(m + 1))
        core_end = m
    else:
        core = [i * stride for i in range(m + 1)]
        core_end = m * stride
    if gs <= 0:
        return core
    g = _greedy_golomb(gs, max(30, gs * gs + 20), rng)
    offset = core_end + gap
    extra = [offset + scale * x for x in g]
    return core + extra


def _reflect(a, c, frac, side="top"):
    s = sorted(set(a))
    n = len(s)
    k = max(1, int(round(frac * n)))
    if k >= n:
        k = n - 1
    if k <= 0:
        return s
    if side == "top":
        idx = set(range(n - k, n))
    elif side == "bottom":
        idx = set(range(0, k))
    else:
        lo = max(0, (n - k) // 2)
        idx = set(range(lo, lo + k))
    keep = [s[i] for i in range(n) if i not in idx]
    moved = [2 * c - s[i] for i in idx]
    return sorted(set(keep + moved))


def _reflection_hillclimb(a, deadline, rng):
    cur = sorted(set(a))
    cur_score = _score_fast(cur)
    best = cur[:]
    best_score = cur_score
    while time.time() < deadline:
        s = sorted(cur)
        n = len(s)
        if n < 4:
            break
        centers = set()
        for q in (0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9):
            i = int(q * (n - 1))
            centers.add(s[i])
        for i in range(min(6, n)):
            for j in range(max(0, n - 6), n):
                centers.add((s[i] + s[j]) // 2)
                centers.add((s[i] + s[j] + 1) // 2)
        for _ in range(8):
            i = rng.randrange(n)
            j = rng.randrange(n)
            centers.add((s[i] + s[j]) // 2)
        fracs = (0.2, 0.3, 0.4, 0.5)
        sides = ("top", "bottom", "mid")
        best_local = None
        best_local_score = cur_score
        for c in centers:
            for f in fracs:
                for side in sides:
                    cand = _reflect(cur, c, f, side)
                    if len(cand) < 2:
                        continue
                    sc = _score_fast(cand)
                    if sc > best_local_score:
                        best_local_score = sc
                        best_local = cand
        if best_local is not None:
            cur = best_local
            cur_score = best_local_score
            if cur_score > best_score:
                best = cur[:]
                best_score = cur_score
        else:
            break
    return best, best_score


def _mutate(cur, rng):
    cand = cur[:]
    r = rng.random()
    if r < 0.35 and cand:
        i = rng.randrange(len(cand))
        if rng.random() < 0.5:
            base = rng.choice(cand)
            d = rng.randint(1, 80)
            cand[i] = base + d if rng.random() < 0.5 else base - d
        else:
            cand[i] += rng.randint(-12, 12)
        cand = list(set(cand))
    elif r < 0.60:
        if len(cand) < 4000:
            base = rng.choice(cand)
            cand.append(base + rng.randint(1, 30))
            cand = list(set(cand))
    elif r < 0.72:
        if len(cand) < 4000:
            lo = min(cand)
            hi = max(cand)
            span = max(hi - lo, 1)
            cand.append(rng.randint(lo - 2 * span, hi + 2 * span))
            cand = list(set(cand))
    elif r < 0.90 and len(cand) > 3:
        i = rng.randrange(len(cand))
        cand.pop(i)
    else:
        m = rng.randint(0, 18)
        gs = rng.randint(2, 20)
        gap = rng.randint(1, 20)
        stride = rng.choice([1, 1, 1, 2, 3])
        scale = rng.choice([1, 1, 1, 2, 3])
        cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
    return cand


def _budget_adaptive_sa(seed, deadline, rng, restart_fn=None,
                        watchdog=20.0, total_budget=110.0):
    """SA with T derived from remaining budget and a no-improvement watchdog."""
    cur = sorted(set(seed))
    cur_score = _score_fast(cur)
    best = cur[:]
    best_score = cur_score
    last_improve = time.time()
    start = time.time()
    while True:
        now = time.time()
        if now >= deadline:
            break
        remaining = max(0.0, deadline - now)
        # Budget-adaptive temperature: broad early, tight late.
        T = 0.15 * (remaining / total_budget) + 0.005
        cand = _mutate(cur, rng)
        if len(cand) < 2:
            continue
        s = _score_fast(cand)
        if s > cur_score:
            cur, cur_score = cand, s
            if s > best_score:
                best, best_score = cand[:], s
                last_improve = now
        else:
            # Non-improving acceptance with a floor that decays with budget.
            floor = 0.10 if (now - start) < 30.0 else 0.02
            p = max(floor, math.exp((s - cur_score) / max(T, 1e-9)))
            if rng.random() < p:
                cur, cur_score = cand, s
        if rng.random() < 0.005:
            cur = best[:]
            cur_score = best_score
        # Watchdog: restart from a fresh structured seed if stuck too long.
        if restart_fn is not None and (now - last_improve) > watchdog:
            seed2 = restart_fn(rng)
            cur = sorted(set(seed2))
            cur_score = _score_fast(cur)
            last_improve = now
    return best, best_score


def _build_of_size(n, rng):
    if n <= 1:
        return [0]
    if n <= 4:
        return list(range(n))
    m = max(1, int(round(math.sqrt(n))) - 1)
    gs = n - (m + 1)
    if gs <= 0:
        return list(range(n))
    gap = rng.randint(1, 20)
    stride = rng.choice([1, 1, 1, 2, 3])
    scale = rng.choice([1, 1, 1, 2, 3])
    cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
    cand = sorted(set(cand))
    if len(cand) < n:
        hi = max(cand)
        x = hi + 1
        while len(cand) < n:
            if x not in cand:
                cand.append(x)
            x += 1
        cand = sorted(set(cand))
    elif len(cand) > n:
        cand = sorted(cand)[:n]
    return cand


def solve():
    """Return a list of distinct integers A making |A - A| large and |A + A| small:
    maximise log|A - A| / log|A + A|."""
    rng = random.Random(987654321)
    total_budget = 110.0
    deadline = time.time() + total_budget

    best = [7, 15, 18, 22, -3, -2]
    best_score = _score_fast(best)

    # Phase 0: cardinality-aware search over target sizes using the pure ratio.
    target_sizes = [30, 45, 65, 90, 130, 180, 250, 350, 500]
    pure_best = None
    pure_best_score = -1.0
    phase0_end = time.time() + 35
    per_n = max(2.0, (phase0_end - time.time()) / max(1, len(target_sizes)))
    for n_target in target_sizes:
        if time.time() >= phase0_end:
            break
        local_best = None
        local_score = -1.0
        for _ in range(2):
            if time.time() >= phase0_end:
                break
            seed = _build_of_size(n_target, rng)
            sub_end = min(phase0_end, time.time() + per_n / 2.0)
            cand, s = _budget_adaptive_sa(
                seed, sub_end, rng,
                restart_fn=lambda r: _build_of_size(n_target, r),
                watchdog=15.0, total_budget=total_budget)
            # pure ratio for phase-0 comparison
            sp = _score_pure(cand)
            if sp > local_score:
                local_score = sp
                local_best = cand
        if local_best is not None and local_score > pure_best_score:
            pure_best_score = local_score
            pure_best = local_best[:]
    if pure_best is not None:
        s_full = _score_fast(pure_best)
        if s_full > best_score:
            best = pure_best
            best_score = s_full

    # Phase 1: systematic scan over (m, gs, gap, stride, scale).
    phase1_end = time.time() + 20
    tried = []
    for m in range(0, 20):
        for gs in range(0, 22):
            for gap in [1, 2, 3, 4, 5, 7, 9, 12, 16, 22]:
                for stride in (1, 2, 3):
                    for scale in (1, 2, 3):
                        tried.append((m, gs, gap, stride, scale))
    rng.shuffle(tried)
    for (m, gs, gap, stride, scale) in tried:
        if time.time() > phase1_end:
            break
        cand = _build_dense_golomb(m, gs, gap, rng, stride, scale)
        s = _score_fast(cand)
        if s > best_score:
            best_score = s
            best = cand[:]

    # Phase 2: reflection hill-climb on the best structured seed.
    if time.time() < deadline - 5:
        sub = time.time() + min(15, deadline - time.time() - 3)
        cand, s = _reflection_hillclimb(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 2b: budget-adaptive SA with watchdog restarts on the current best.
    if time.time() < deadline - 5:
        sub = time.time() + min(35, deadline - time.time() - 3)

        def _restart(r):
            m = r.randint(0, 18)
            gs = r.randint(2, 20)
            gap = r.randint(1, 20)
            stride = r.choice([1, 1, 1, 2, 3])
            scale = r.choice([1, 1, 1, 2, 3])
            return _build_dense_golomb(m, gs, gap, r, stride, scale)

        cand, s = _budget_adaptive_sa(
            best, sub, rng, restart_fn=_restart,
            watchdog=20.0, total_budget=total_budget)
        if s > best_score:
            best, best_score = cand, s

    # Phase 2c: reflection again after SA polish.
    if time.time() < deadline - 5:
        sub = time.time() + min(10, deadline - time.time() - 3)
        cand, s = _reflection_hillclimb(best, sub, rng)
        if s > best_score:
            best, best_score = cand, s

    # Phase 3: watchdog-driven SA restarts consuming the remaining budget.
    def _restart_any(r):
        m = r.randint(0, 18)
        gs = r.randint(2, 20)
        gap = r.randint(1, 20)
        stride = r.choice([1, 1, 1, 2, 3])
        scale = r.choice([1, 1, 1, 2, 3])
        return _build_dense_golomb(m, gs, gap, r, stride, scale)

    while time.time() < deadline - 6:
        seed = _restart_any(rng)
        sub = time.time() + min(10, deadline - time.time() - 4)
        cand, s = _budget_adaptive_sa(
            seed, sub, rng, restart_fn=_restart_any,
            watchdog=20.0, total_budget=total_budget)
        if s > best_score:
            best, best_score = cand, s
        sub2 = min(deadline - 1, time.time() + 3)
        cand2, s2 = _reflection_hillclimb(cand, sub2, rng)
        if s2 > best_score:
            best, best_score = cand2, s2

    # Final reflection polish.
    if time.time() < deadline - 1:
        cand, s = _reflection_hillclimb(best, deadline - 0.5, rng)
        if s > best_score:
            best, best_score = cand, s

    return sorted(set(best))
# EVOLVE-BLOCK-END