# EVOLVE-BLOCK-START
"""Baseline: greedy construction with random restarts."""
import random
import time


def solve():
    """Return a list of +1/-1 values x_1, x_2, ... that is as long as possible while every
    sum x_d + x_2d + ... + x_kd stays between -2 and 2."""
    best = []
    deadline = time.time() + 20
    while time.time() < deadline:
        seq, sums = [], {}
        while True:
            m = len(seq) + 1
            options = [v for v in (1, -1)
                       if all(abs(sums.get(d, 0) + v) <= 2 for d in range(1, m + 1) if m % d == 0)]
            if not options:
                break
            v = random.choice(options)
            seq.append(v)
            for d in range(1, m + 1):
                if m % d == 0:
                    sums[d] = sums.get(d, 0) + v
        if len(seq) > len(best):
            best = seq
    return best
# EVOLVE-BLOCK-END
