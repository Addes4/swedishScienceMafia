"""The fill-weighted Sum-of-Squares policy as a drop-in FunSearch `priority(item, bins)` function.

FunSearch's evaluator (Romera-Paredes et al., Nature 2024; also EoH's and this repository's
bin_packing_online) calls priority(item, bins) once per item. `bins` holds the remaining capacity
of every bin the item fits in, unused bins included, in bin order, and the item goes to the first
highest score. This function keeps state between calls; that is the one thing FunSearch's evolved
heuristics did not do. The state is rebuilt only from what the function itself has seen:
  - the gap histogram N(g) of open bins, updated with its own choice after every call;
  - the sizes seen so far (for the empirical CDF F and the mean size);
  - the horizon T, read as len(bins) on the first call of an instance, when every bin is unused.
It never looks at future items. A new instance starts once T items have been placed.

The decision rule is the same as fast.pack_fss and sim.pack_fss_py (check_priority.py checks
that the bin counts are identical).
"""
import numpy as np

BETA = 1.0     # weight F(g)^-BETA on N(g)^2; set by the frozen protocol
ALPHA = 0.0    # extra weight g^-ALPHA
SWITCH_C = 1.1  # switch to best fit once (items left) * (mean size) <= SWITCH_C * (total open gap)

_state = None


def _reset(T, C):
    return {"T": T, "C": C, "t": 0, "N": [0] * (C + 1), "cnt": [0] * (C + 1),
            "seen": 0, "gap": 0, "switched": False}


def priority(item, bins):
    global _state
    bins = np.asarray(bins)
    item = int(item)
    if _state is None or _state["t"] >= _state["T"]:
        # First call of an instance: every bin is unused, so they all have the capacity.
        _state = _reset(len(bins), int(bins.max()))
    S = _state
    C, N, cnt = S["C"], S["N"], S["cnt"]
    S["t"] += 1
    t, n = S["t"], S["T"]
    S["seen"] += item
    cnt[item] += 1
    if not S["switched"] and SWITCH_C > 0 and (n - t + 1) * (S["seen"] / t) <= SWITCH_C * S["gap"]:
        S["switched"] = True
    if S["switched"]:
        g_sel = next((g for g in range(item, C) if N[g]), C)
    else:
        w, cum = [0.0] * (C + 1), 0
        for g in range(1, C + 1):
            cum += cnt[g]
            w[g] = ((1.0 + cum) / (1.0 + t)) ** -BETA * float(g) ** -ALPHA
        best, g_sel = None, C
        for g in range(item, C + 1):
            if g < C and not N[g]:
                continue
            r = g - item
            d = (w[g] * (-2 * N[g] + 1) if g < C else 0.0) + (w[r] * (2 * N[r] + 1) if r > 0 else 0.0)
            if best is None or (d, r) < best:
                best, g_sel = (d, r), g
    if g_sel == C:
        S["gap"] += C - item
    else:
        N[g_sel] -= 1
        S["gap"] -= item
    if g_sel - item > 0:
        N[g_sel - item] += 1
    # Any bin with the chosen gap is equivalent; the evaluator takes the first one.
    return (bins == g_sel).astype(float)
