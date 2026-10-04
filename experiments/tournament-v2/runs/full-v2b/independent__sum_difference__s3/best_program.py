import math
import random
import time

def _score(a):
    a = list(set(a))
    n = len(a)
    if n < 2:
        return 0.0
    # compute difference and sum counts without storing huge sets when possible
    diffs = set()
    sums = set()
    for i, x in enumerate(a):
        for y in a:
            diffs.add(x - y)
            sums.add(x + y)
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / n) / 100

def solve():
    deadline = time.time() + 110

    best = [4, 8, 12, 16, 20, 24, -4, -8, -12]
    best_score = _score(best)

    # multiple restarts with different seeds / structures
    while time.time() < deadline:
        n = random.randint(12, 200)
        step = random.randint(1, 6)
        start = random.randint(-50, 50)
        base = [start + i * step for i in range(n)]
        cand = base[:]

        # random perturbations / extra shifts
        for _ in range(random.randint(0, n // 3)):
            idx = random.randrange(len(cand))
            cand[idx] += random.randint(-step * 3, step * 3)

        if random.random() < 0.3:
            extra = random.randint(1, 40)
            for _ in range(extra):
                cand.append(random.randint(-200, 200))

        cand = sorted(set(cand))
        s = _score(cand)
        if s > best_score:
            best_score = s
            best = cand[:]
        if time.time() > deadline:
            break

        # local search on this candidate
        cur = cand[:]
        cur_score = s
        local_end = min(deadline, time.time() + 2.0)
        while time.time() < local_end:
            temp = cur[:]
            if temp:
                i = random.randrange(len(temp))
                temp[i] += random.randint(-step * 5 - 1, step * 5 + 1)
            if random.random() < 0.08:
                temp.append(random.randint(-300, 300))
            if random.random() < 0.05 and len(temp) > 5:
                temp.pop(random.randrange(len(temp)))
            temp = sorted(set(temp))
            if len(temp) < 2:
                continue
            ts = _score(temp)
            if ts >= cur_score:
                cur, cur_score = temp, ts
                if ts > best_score:
                    best, best_score = temp[:], ts

    return sorted(set(best))
