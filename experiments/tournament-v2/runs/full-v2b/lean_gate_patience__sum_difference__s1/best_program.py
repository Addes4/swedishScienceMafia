# EVOLVE-BLOCK-START
"""Constructive search: union of translated AP clusters at Golomb-like offsets,
balancing a small sum set against a large difference set."""
import math
import random
import time


def _score(a):
    a = set(a)
    if len(a) < 2:
        return 0.0
    diffs = {x - y for x in a for y in a}
    sums = {x + y for x in a for y in a}
    return math.log(len(diffs)) / math.log(len(sums)) + (1 - 1 / len(a)) / 100


def _golomb(n):
    """Approximate Golomb ruler with n marks using a greedy largest-gap-free search."""
    marks = [0]
    used = {0}
    while len(marks) < n:
        cand = marks[-1] + 1
        while True:
            ok = True
            for m in marks:
                d = cand - m
                if d in used or d == 0:
                    ok = False
                    break
            if ok:
                break
            cand += 1
        for m in marks:
            used.add(cand - m)
        marks.append(cand)
    return marks


def _build(clusters, width, offset_scale):
    """Union of `clusters` translated copies of an AP of length `width`,
    placed at Golomb offsets scaled by `offset_scale`."""
    offs = _golomb(clusters)
    offs = [o * offset_scale for o in offs]
    A = []
    for o in offs:
        for k in range(width):
            A.append(o + k)
    return A


def solve():
    """Return A making |A-A| large and |A+A| small."""
    best = None
    best_score = -1.0
    deadline = time.time() + 100

    # structured candidates
    for clusters in range(2, 40):
        for width in range(2, 40):
            n = clusters * width
            if n < 2 or n > 4000:
                continue
            scale = width * (width + len(_golomb(clusters)))
            A = _build(clusters, width, scale)
            s = _score(A)
            if s > best_score:
                best_score, best = s, A[:]
            if time.time() > deadline:
                break
        if time.time() > deadline:
            break

    if best is None:
        best = [0, 1, 2, 4, 8]
        best_score = _score(best)

    # local refinement: add single integers that help
    cur = best[:]
    improve_deadline = time.time() + 15
    while time.time() < improve_deadline:
        cand = cur[:]
        # try adding an element near existing ones
        base = random.choice(cand)
        cand.append(base + random.randint(-200, 200))
        cand = list(set(cand))
        if len(cand) > 4000:
            continue
        s = _score(cand)
        if s >= best_score:
            best_score, best, cur = s, cand[:], cand
        elif random.random() < 0.2:
            # try removing an element to reduce sum set
            if len(cand) > 3:
                cand2 = cand[:]
                cand2.pop(random.randrange(len(cand2)))
                s2 = _score(cand2)
                if s2 >= best_score:
                    best_score, best, cur = s2, cand2[:], cand2

    return sorted(set(best))
# EVOLVE-BLOCK-END
