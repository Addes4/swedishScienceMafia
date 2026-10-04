# EVOLVE-BLOCK-START
"""Ratio-aware top-K seed selector with round-robin refinement.

Architecture:
  Phase 0: scorer utilities (single fast symmetric scorer).
  Phase 1: enumerate diverse structured seeds, rank by PURE ratio,
           keep top-K.
  Phase 2: round-robin short SA refinement bursts across top-K seeds.
  Phase 3: greedy growth polish on the global best.
  Phase 4: return best.
"""
import math
import random
import time


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_fast(a):
    """Pure ratio + tiny size bonus. a is a list of distinct ints."""
    n = len(a)
    if n < 2:
        return 0.0, 0.0  # (full, pure)
    diffs = set()
    sums = set()
    add_d = diffs.add
    add_s = sums.add
    for i in range(n):
        ai = a[i]
        for j in range(i, n):
            aj = a[j]
            add_d(ai - aj)
            add_d(aj - ai)
            add_s(ai + aj)
    nd = len(diffs)
    ns = len(sums)
    if ns <= 1:
        return 0.0, 0.0
    pure = math.log(nd) / math.log(ns)
    full = pure + (1 - 1 / n) / 100
    return full, pure


def _score(a):
    return _score_fast(list(set(a)))[0]


# ---------------------------------------------------------------------------
# Structured seed builders
# ---------------------------------------------------------------------------

def _greedy_golomb(n, hi, rng):
    """Greedy Golomb-like ruler: each new mark maximises new distinct differences."""
    if n <= 0:
        return []
    marks = [0]
    used = {0}
    diffs = {0}
    for _ in range(n - 1):
        best_x = None
        best_new = -1
        cands = set()
        for _ in range(60):
            cands.add(rng.randint(1, max(1, hi)))
        for m in marks:
            for d in (1, 2, 3, 5, 8, 13, 21, 34):
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
    """Dense or strided core plus a (optionally scaled) Golomb tail."""
    if stride <= 1:
        core = list(range(m + 1))
        core_end = m
    else:
        core = [i * stride for i in range(m + 1)]
        core_end = m * stride
    if gs <= 0:
        return core
    g = _greedy_golomb(gs, max(40, gs * gs + 30), rng)
    offset = core_end + gap
    extra = [offset + scale * x for x in g]
    return core + extra


def _build_two_block(m1, m2, gap, rng, stride1=1, stride2=1):
    """Two dense blocks placed far apart. Sums live in two clusters; diffs
    are enlarged by the large cross-block separation."""
    b1 = [i * stride1 for i in range(m1 + 1)]
    end1 = m1 * stride1
    start2 = end1 + gap
    b2 = [start2 + i * stride2 for i in range(m2 + 1)]
    return b1 + b2


def _build_mixed(m, gs, gap, stride, scale, rng):
    """Dense core + scaled Golomb + small strided tail far away."""
    base = _build_dense_golomb(m, gs, gap, rng, stride, scale)
    far = max(base) + gap + 1
    tail = [far + 3 * i for i in range(0, 4)]
    return base + tail


# ---------------------------------------------------------------------------
# Local search (short bursts)
# ---------------------------------------------------------------------------

def _refine_burst(seed, deadline, rng, T0=0.05):
    cur = sorted(set(seed))
    if len(cur) < 2:
        return cur, 0.0
    cur_score, cur_pure = _score_fast(cur)
    best = cur[:]
    best_score = cur_score
    T = T0
    step = 0
    while time.time() < deadline:
        step += 1
        if step % 400 == 0:
            T = max(0.0003, T * 0.996)
        cand = cur[:]
        r = rng.random()
        if r < 0.35 and cand:
            i = rng.randrange(len(cand))
            base = rng.choice(cand)
            d = rng.randint(1, 120)
            cand[i] = base + d if rng.random() < 0.5 else base - d
            cand = list(set(cand))
        elif r < 0.58:
            if len(cand) < 4000:
                base = rng.choice(cand)
                cand.append(base + rng.randint(1, 40))
                cand = list(set(cand))
        elif r < 0.72:
            if len(cand) < 4000:
                lo = min(cand)
                hi = max(cand)
                span = max(hi - lo, 1)
                cand.append(rng.randint(lo - 2 * span, hi + 2 * span))
                cand = list(set(cand))
        elif r < 0.90 and len(cand) > 3:
            cand.pop(rng.randrange(len(cand)))
        else:
            # rebuild a random structured seed occasionally
            kind = rng.random()
            if kind < 0.5:
                cand = _build_dense_golomb(
                    rng.randint(0, 18), rng.randint(2, 18),
                    rng.randint(1, 22), rng,
                    rng.choice([1, 1, 2, 3]), rng.choice([1, 1, 2, 3]))
            else:
                cand = _build_two_block(
                    rng.randint(2, 16), rng.randint(2, 16),
                    rng.randint(5, 60), rng,
                    rng.choice([1, 1, 2]), rng.choice([1, 1, 2]))
        if len(cand) < 2:
            continue
        s, _ = _score_fast(cand)
        if s > cur_score or rng.random() < math.exp((s - cur_score) / max(T, 1e-9)):
            cur = cand
            cur_score = s
            if s > best_score:
                best = cand[:]
                best_score = s
        if rng.random() < 0.006:
            cur = best[:]
            cur_score = best_score
    return best, best_score


# ---------------------------------------------------------------------------
# Greedy growth polish
# ---------------------------------------------------------------------------

def _grow_by_difference(seed, deadline, rng):
    cur = sorted(set(seed))
    if len(cur) < 2:
        return cur, 0.0
    cur_score, cur_pure = _score_fast(cur)
    best = cur[:]
    best_score = cur_score
    while time.time() < deadline and len(cur) < 4000:
        base_diffs = set()
        base_sums = set()
        n = len(cur)
        for i in range(n):
            ai = cur[i]
            for j in range(i, n):
                aj = cur[j]
                base_diffs.add(ai - aj)
                base_diffs.add(aj - ai)
                base_sums.add(ai + aj)
        best_c = None
        best_gain = -1e18
        for _ in range(60):
            x = rng.choice(cur)
            y = rng.choice(cur)
            c = x + (x - y) + rng.randint(-4, 4)
            if c in cur:
                continue
            new_d = 0
            for z in cur:
                if (c - z) not in base_diffs:
                    new_d += 1
                if (z - c) not in base_diffs:
                    new_d += 1
            new_s = 0
            for z in cur:
                if (c + z) not in base_sums:
                    new_s += 1
            gain = new_d - 0.35 * new_s
            if gain > best_gain:
                best_gain = gain
                best_c = c
        if best_c is None:
            break
        cur.append(best_c)
        cur = sorted(set(cur))
        s, _ = _score_fast(cur)
        if s > cur_score:
            cur_score = s
            if s > best_score:
                best = cur[:]
                best_score = s
        else:
            cur = best[:]
            cur_score = best_score
            break
    return best, best_score


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve():
    rng = random.Random(20240607)
    deadline = time.time() + 108

    # ---- Phase 1: enumerate diverse seeds, rank by PURE ratio -------------
    phase1_end = time.time() + 32
    seeds = []  # list of (pure, full, list)

    def consider(cand):
        cand = sorted(set(cand))
        if len(cand) < 2:
            return
        full, pure = _score_fast(cand)
        if pure > 0:
            seeds.append((pure, full, cand))

    # small pure intervals
    for n in range(2, 90):
        consider(list(range(n)))

    # dense + Golomb family
    for m in range(0, 20):
        for gs in range(2, 20):
            for gap in (1, 2, 3, 5, 8, 13, 21, 34, 55):
                for stride in (1, 2, 3):
                    for scale in (1, 2, 3):
                        if time.time() > phase1_end:
                            break
                        consider(_build_dense_golomb(m, gs, gap, rng, stride, scale))
                    if time.time() > phase1_end:
                        break
                if time.time() > phase1_end:
                    break
            if time.time() > phase1_end:
                break
        if time.time() > phase1_end:
            break

    # two-block family
    for m1 in range(2, 18):
        for m2 in range(2, 18):
            for gap in (5, 10, 20, 40, 80):
                for s1 in (1, 2):
                    for s2 in (1, 2):
                        if time.time() > phase1_end:
                            break
                        consider(_build_two_block(m1, m2, gap, rng, s1, s2))
                    if time.time() > phase1_end:
                        break
                if time.time() > phase1_end:
                    break
            if time.time() > phase1_end:
                break
        if time.time() > phase1_end:
            break

    # mixed family (few random draws)
    for _ in range(400):
        if time.time() > phase1_end:
            break
        consider(_build_mixed(
            rng.randint(0, 16), rng.randint(2, 16),
            rng.randint(1, 30), rng.choice([1, 1, 2, 3]),
            rng.choice([1, 1, 2, 3]), rng))

    # rank by pure ratio; tiebreak by full score
    seeds.sort(key=lambda t: (t[0], t[1]), reverse=True)
    # deduplicate by tuple to avoid refining identical seeds
    seen = set()
    topK = []
    for pure, full, cand in seeds:
        key = tuple(cand)
        if key in seen:
            continue
        seen.add(key)
        topK.append((pure, full, cand))
        if len(topK) >= 24:
            break

    if not topK:
        topK = [(0.0, 0.0, [0, 1, 3])]

    best_pure, best_full, best = topK[0]
    best_score = best_full

    # ---- Phase 2: round-robin short refinement bursts ---------------------
    burst_len = 4.0
    idx = 0
    while time.time() < deadline - 6:
        pure, full, seed = topK[idx % len(topK)]
        idx += 1
        remaining = deadline - time.time()
        if remaining < 1.5:
            break
        sub = time.time() + min(burst_len, remaining - 1.0)
        cand, s = _refine_burst(seed, sub, rng, T0=0.05)
        if s > best_score:
            best = cand[:]
            best_score = s
            _, best_pure = _score_fast(best)
        # Occasionally replace a weak top-K slot with a fresh random seed
        if rng.random() < 0.15 and len(topK) > 1:
            j = rng.randrange(len(topK))
            if j != 0:
                kind = rng.random()
                if kind < 0.5:
                    fresh = _build_dense_golomb(
                        rng.randint(0, 16), rng.randint(2, 16),
                        rng.randint(1, 25), rng,
                        rng.choice([1, 1, 2, 3]), rng.choice([1, 1, 2, 3]))
                else:
                    fresh = _build_two_block(
                        rng.randint(2, 14), rng.randint(2, 14),
                        rng.randint(5, 40), rng,
                        rng.choice([1, 1, 2]), rng.choice([1, 1, 2]))
                fresh = sorted(set(fresh))
                if len(fresh) >= 2:
                    fp, ff = _score_fast(fresh)
                    topK[j] = (fp, ff, fresh)

    # ---- Phase 3: greedy growth polish ------------------------------------
    if time.time() < deadline:
        cand, s = _grow_by_difference(best, deadline, rng)
        if s > best_score:
            best = cand[:]
            best_score = s

    return sorted(set(best))


if __name__ == "__main__":
    print(solve())
# EVOLVE-BLOCK-END
