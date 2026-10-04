"""`pack_hist`, `best_fit` and `sum_of_squares`, copied verbatim from experiments/online-frontier-v1/frontier.py
(SHA-256 3b74ed18...; full copy in frontier.py here)."""

def pack_hist(items, C, rule):
    """Number of bins a gap-histogram rule uses on `items`."""
    N = [0] * (C + 1)
    opened = 0
    T = len(items)
    for t, s in enumerate(items, start=1):
        g = rule(N, s, C, t, T)
        if g == C:
            opened += 1
        else:
            assert N[g] > 0 and g >= s
            N[g] -= 1
        if g - s > 0:
            N[g - s] += 1
    return opened

def best_fit(N, s, C, t, T):
    return next((g for g in range(s, C) if N[g]), C)

def sum_of_squares(N, s, C, t, T):
    """Csirik et al.: minimise sum_{0<g<C} N(g)^2; ties to the smaller resulting gap."""
    best, best_g = None, C
    for g in range(s, C + 1):
        if g < C and not N[g]:
            continue
        r = g - s
        d = (1 - 2 * N[g] if g < C else 0) + (2 * N[r] + 1 if r > 0 else 0)
        if best is None or (d, r) < best:
            best, best_g = (d, r), g
    return best_g
