"""Exploratory simulator for online bin packing over the gap histogram (not pre-registered).

A policy is rule(N, s, C, t, T, hist) -> g, the gap of the bin that receives item s; g == C opens
a new bin. N[g] counts open bins with remaining capacity g (0 < g < C). `hist[x]` counts items
of size x seen before the current one (the current item is not included), so a policy can learn
the item distribution online without knowing it in advance.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))
import verify  # noqa: E402


def pack(items, C, rule, return_state=False):
    N = [0] * (C + 1)
    hist = [0] * (C + 1)
    opened = 0
    T = len(items)
    for t, s in enumerate(items, start=1):
        g = rule(N, s, C, t, T, hist)
        if g == C:
            opened += 1
        else:
            assert N[g] > 0 and g >= s, (g, s)
            N[g] -= 1
        if g - s > 0:
            N[g - s] += 1
        hist[s] += 1
    if return_state:
        return opened, N
    return opened


def l1(items, C):
    return math.ceil(sum(items) / C)


def best_fit(N, s, C, t, T, hist):
    return next((g for g in range(s, C) if N[g]), C)


def sum_of_squares(N, s, C, t, T, hist):
    best, best_g = None, C
    for g in range(s, C + 1):
        if g < C and not N[g]:
            continue
        r = g - s
        key = ((-2 * N[g] + 1 if g < C else 0) + (2 * N[r] + 1 if r > 0 else 0), r)
        if best is None or key < best:
            best, best_g = key, g
    return best_g


def weibull_items(seed, n):
    return list(verify.items_for(seed, n))


def pack_fss_py(items, C, beta, c, alpha=0.0):
    """Reference implementation of fast.pack_fss (slow; used to check the C code).

    Weighted Sum-of-Squares with weight F(g)^-beta * g^-alpha on N(g)^2, where F is the empirical
    CDF of the sizes seen so far (current item included, add-one smoothed). Once the expected
    volume of the remaining items, (n - t + 1) * mean size so far, is at most c times the total
    open gap, it switches to best fit for the rest of the sequence.
    """
    N = [0] * (C + 1)
    cnt = [0] * (C + 1)
    n = len(items)
    opened, gap, seen, switched = 0, 0, 0, False
    for t, s in enumerate(items, start=1):
        seen += s
        cnt[s] += 1
        if not switched and c > 0 and (n - t + 1) * (seen / t) <= c * gap:
            switched = True
        if switched:
            g_sel = next((g for g in range(s, C) if N[g]), C)
        else:
            w, cum = [0.0] * (C + 1), 0
            for g in range(1, C + 1):
                cum += cnt[g]
                w[g] = ((1.0 + cum) / (1.0 + t)) ** -beta * float(g) ** -alpha
            best, g_sel = None, C
            for g in range(s, C + 1):
                if g < C and not N[g]:
                    continue
                r = g - s
                d = (w[g] * (-2 * N[g] + 1) if g < C else 0.0) + (w[r] * (2 * N[r] + 1) if r > 0 else 0.0)
                if best is None or (d, r) < best:
                    best, g_sel = (d, r), g
        if g_sel == C:
            opened += 1
            gap += C - s
        else:
            N[g_sel] -= 1
            gap -= s
        if g_sel - s > 0:
            N[g_sel - s] += 1
    return opened, N
