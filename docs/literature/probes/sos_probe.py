"""Exploratory probe (not pre-registered): Sum-of-Squares against best fit and FunSearch.

Sum-of-Squares (SS; Csirik, Johnson, Kenyon, Orlin, Shor and Weber, JACM 53(1), 2006,
arXiv cs/0210013) places each item where it minimises sum_g N(g)^2, where N(g) counts open
bins with remaining capacity g (0 < g < C). It has no parameters and uses only past items.

Usage, from the repository root (CPU only, about 3 minutes):
    python docs/literature/probes/sos_probe.py            # released Weibull 5k data plus fresh instances
    python docs/literature/probes/sos_probe.py --quick    # released data only
    python docs/literature/probes/sos_probe.py --or3 PATH # also FunSearch's OR3 data (datasets.json from the
                                                  # unmerged campaign branch, key "OR3")

Excess is over L1 = ceil(sum/C) for FunSearch's released data (FunSearch's own metric) and over
the Martello-Toth L2 bound for fresh instances (bp-ceiling-v1's metric). Fresh instances use
problems/bin_packing_online/verify.items_for with seeds 52000+, 53000+, 60000+, 61000+, 62000+,
which no repository study uses.
"""
import argparse
import gzip
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))
import verify  # noqa: E402


def _load(name):
    path = ROOT / "problems" / "bin_packing_online" / "baselines" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.priority


FUNSEARCH = {"FunSearch Weibull": _load("funsearch_weibull"), "FunSearch OR": _load("funsearch_or")}


def pack_priority(items, cap, priority):
    """FunSearch's evaluator: priority sees every bin the item fits in, unused bins included."""
    bins = np.full(len(items), cap, dtype=np.int64)
    for it in items:
        valid = np.nonzero(bins - it >= 0)[0]
        bins[valid[np.argmax(np.asarray(priority(it, bins[valid]), dtype=np.float64))]] -= it
    return int((bins != cap).sum())


def pack_gaps(items, cap, rule):
    """Pack with a rule over the gap histogram N; returns the number of bins opened."""
    N = [0] * (cap + 1)
    opened = 0
    for s in items:
        g = rule(N, s, cap)
        if g == cap:
            opened += 1
        else:
            N[g] -= 1
        if g - s > 0:
            N[g - s] += 1
    return opened


def best_fit(N, s, cap):
    return next((g for g in range(s, cap) if N[g]), cap)


def sum_of_squares(N, s, cap):
    best, best_g = None, cap
    for g in range(s, cap + 1):
        if g < cap and not N[g]:
            continue
        r = g - s
        key = ((-2 * N[g] + 1 if g < cap else 0) + (2 * N[r] + 1 if r > 0 else 0), r)  # ties: tighter fit
        if best is None or key < best:
            best, best_g = key, g
    return best_g


def sos_visible_only(item, bins, cap=100):
    """SS restricted to FunSearch's stateless view: only gaps of bins the item fits in are known."""
    N = np.bincount(bins[bins < cap], minlength=cap + 1)
    r = bins - item
    d = np.where(bins < cap, -2 * N[bins] + 1, 0) + np.where(r > 0, 2 * N[np.clip(r, 0, cap)] + 1, 0)
    return -(d + 1e-6 * r)


def released(insts, label, with_visible):
    tot, lb, per = {}, 0, []
    for v in insts.values():
        cap, items = v["capacity"], [int(x) for x in v["items"]]
        lb += math.ceil(sum(items) / cap)
        row = {"best fit": pack_gaps(items, cap, best_fit), "Sum-of-Squares": pack_gaps(items, cap, sum_of_squares)}
        for name, pr in FUNSEARCH.items():
            row[name] = pack_priority(items, cap, pr)
        if with_visible:
            row["SS, FunSearch's stateless view"] = pack_priority(items, cap, sos_visible_only)
        for k, x in row.items():
            tot[k] = tot.get(k, 0) + x
        per.append(row)
    print(f"\n{label}: {len(insts)} instances, capacity {cap}; excess over L1")
    for k, x in tot.items():
        print(f"  {k:32s} {100 * (x - lb) / lb:6.3f}%")
    d = np.array([r["Sum-of-Squares"] - min(r["FunSearch Weibull"], r["FunSearch OR"]) for r in per])
    print(f"  SS minus the better FunSearch heuristic: {d.mean():+.2f} bins/instance, "
          f"wins/ties/losses {(d < 0).sum()}/{(d == 0).sum()}/{(d > 0).sum()}")


def fresh(n, seeds, with_funsearch):
    rows = []
    for sd in seeds:
        items = verify.items_for(sd, n)
        rows.append((verify.l2_bound(items), math.ceil(sum(items) / 100), pack_gaps(items, 100, best_fit), pack_gaps(items, 100, sum_of_squares),
                     pack_priority(items, 100, FUNSEARCH["FunSearch Weibull"]) if with_funsearch else np.nan))
    l2, l1, bf, ss, fs = np.array(rows, dtype=float).T
    ex = lambda x: 100 * (x.sum() - l2.sum()) / l2.sum()
    line = (f"  n={n:6d}, {len(seeds):3d} fresh instances: excess over L2  best fit {ex(bf):.3f}%  SS {ex(ss):.3f}% "
            f"(over L1 {100 * (ss.sum() - l1.sum()) / l1.sum():.3f}%, {np.mean(ss - l1):.1f} bins above L1)")
    if with_funsearch:
        d = ss - fs
        line += (f"  FunSearch {ex(fs):.3f}%  | SS - FunSearch {d.mean():+.2f} bins/instance "
                 f"({(d < 0).sum()}/{(d == 0).sum()}/{(d > 0).sum()})")
    print(line, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true", help="released data only")
    ap.add_argument("--or3", type=Path, help="datasets.json with an 'OR3' key (FunSearch's OR3 data)")
    a = ap.parse_args()
    weibull = ROOT / "experiments" / "bp-ceiling-v1" / "funsearch_weibull5k_test.json.gz"
    released(json.load(gzip.open(weibull))["instances"], "FunSearch's released Weibull 5k test data", True)
    if a.or3:
        released(json.load(open(a.or3))["OR3"], "FunSearch's released OR3 data", False)
    if not a.quick:
        print("\nFresh instances from the repository's Weibull generator")
        fresh(80, range(50000, 50400), True)
        fresh(500, range(51000, 51100), True)
        fresh(5000, range(52000, 52020), True)
        fresh(20000, range(53000, 53004), True)
        fresh(10000, range(61000, 61005), False)
        fresh(100000, range(62000, 62002), False)
