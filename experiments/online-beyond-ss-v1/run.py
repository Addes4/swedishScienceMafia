"""online-beyond-ss-v1 confirmatory run: every policy on every test set; writes results.json.

Usage (from the repository root):
    python experiments/online-beyond-ss-v1/run.py --workers 2            # everything
    python experiments/online-beyond-ss-v1/run.py --sets fs_released     # one set
    python experiments/online-beyond-ss-v1/run.py --no-opt               # skip the exact optimum

The frozen policy parameters are read from config.json. Test sets are listed in PROTOCOL.md; none was
used to choose a parameter. Results hold per-instance bin counts, L1, and the exact optimum (arc-flow
MILP, HiGHS, 300 s limit) where it was proved.
"""
import argparse
import gzip
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))

import verify  # noqa: E402
from fast import pack_fss, pack_wss  # noqa: E402
from frontier_snapshot import FS_OR, FS_W, optimum, pack_funsearch  # noqa: E402
from falsify.funsearch_heuristics import ab_priority  # noqa: E402

CONFIG = json.loads((HERE / "config.json").read_text())


def _load_py(path, fn):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn)


EOH = _load_py(HERE / "eoh_data" / "heuristic_EoH_by_this_code.py", "score")
EOH_PAPER = _load_py(HERE / "eoh_data" / "heuristic_original_EoH_paper.py", "score")


def full_evaluator(items, C, priority):
    """FunSearch's / EoH's evaluator as published: num_items bins, every fitting bin passed."""
    bins = np.array([C for _ in range(len(items))])
    for item in items:
        valid = np.nonzero((bins - item) >= 0)[0]
        j = valid[np.argmax(priority(item, bins[valid]))]
        bins[j] -= item
    return int((bins != C).sum())


# ---------------------------------------------------------------- test sets

def test_sets():
    """name -> (capacity, [(instance id, items, known optimum or None)])."""
    sets = {}
    rel = json.load(gzip.open(ROOT / "experiments" / "bp-ceiling-v1" / "funsearch_weibull5k_test.json.gz"))["instances"]
    sets["fs_released_w5k"] = (100, [(k, [int(x) for x in v["items"]], None) for k, v in rel.items()])
    for name, n, seeds in [("fresh_w1k", 1000, range(98000, 98200)), ("fresh_w5k", 5000, range(98200, 98400)),
                           ("fresh_w10k", 10000, range(98400, 98450)), ("fresh_w100k", 100000, range(98450, 98460))]:
        sets[name] = (100, [(f"seed{s}", list(verify.items_for(s, n)), None) for s in seeds])
    sys.path.insert(0, str(HERE / "eoh_data"))
    from load import load
    for tag, fn in [("1k", "test_dataset_1k.pkl"), ("2k", "test_dataset_2k.pkl"), ("5k", "test_dataset_5k.pkl"),
                    ("10k", "test_dataset_10k.pkl"), ("100k", "test_dataset_100k.pkl")]:
        raw = [list(map(int, x)) for v in load(fn).values() for x in v]
        for C in (100, 500):
            sets[f"eoh_{tag}_c{C}"] = (C, [(f"test_{i}", x, None) for i, x in enumerate(raw, 1)])
    for i in (1, 2, 3, 4):
        t = (HERE / "orlib_data" / f"binpack{i}.txt").read_text().split()
        n, k, insts = int(t[0]), 1, []
        for _ in range(n):
            name, cap, m, best = t[k], int(float(t[k + 1])), int(t[k + 2]), int(t[k + 3])
            k += 4
            insts.append((name, [int(float(x)) for x in t[k:k + m]], best))
            k += m
        sets[f"or{i}"] = (150, insts)
    return sets


# ---------------------------------------------------------------- one instance

def run_instance(task):
    set_name, C, inst_id, items, known_opt, do_opt = task
    n = len(items)
    t0 = time.time()
    beta, alpha, c = CONFIG["beta"], CONFIG["alpha"], CONFIG["c"]
    ones = [1.0] * (C + 1)
    r = {"set": set_name, "id": inst_id, "n": n, "C": C, "L1": math.ceil(sum(items) / C),
         "bins": {
             "FWSS": pack_fss(items, C, beta, c, alpha),          # the frozen policy
             "FWSS-no-finish": pack_fss(items, C, beta, 0.0, alpha),   # ablation: weights only
             "SS+finish": pack_fss(items, C, 0.0, c, 0.0),         # ablation: finish only
             "SS": pack_wss(items, C, ones, 0),
             "BF": pack_wss(items, C, ones, n),
             "FS-W": pack_funsearch(items, C, FS_W),
             "FS-OR": pack_funsearch(items, C, FS_OR),
             "abWF": pack_funsearch(items, C, ab_priority("ab_worst_fit", 1, 21, C)),
         }}
    if n <= 10000:   # the published full evaluator is O(n^2); EoH's heuristic needs it (it reads all bins)
        r["bins"]["EoH"] = full_evaluator(items, C, EOH)
        r["bins"]["EoH-paper"] = full_evaluator(items, C, EOH_PAPER)
    if known_opt is not None:
        r["opt"], r["opt_source"], r["listed_opt"] = known_opt, "OR-Library listed optimum", known_opt
    if do_opt:
        o = optimum(items, C, time_limit=300.0)
        r["arcflow"] = {k: o.get(k) for k in ("opt", "proved", "dual_bound", "arcs")}
        if o["proved"]:
            if known_opt is not None and o["opt"] != known_opt:
                r["opt_mismatch"] = True
            r["opt"], r["opt_source"] = o["opt"], "arc-flow MILP (proved)"
    r["seconds"] = round(time.time() - t0, 1)
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sets", nargs="*", help="subset of set names (default: all)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-opt", action="store_true")
    ap.add_argument("--out", default=str(HERE / "results.json"))
    a = ap.parse_args()
    sets = test_sets()
    names = a.sets or list(sets)
    tasks = [(nm, sets[nm][0], iid, items, kopt, not a.no_opt) for nm in names for iid, items, kopt in sets[nm][1]]
    tasks.sort(key=lambda t: -len(t[3]))       # longest first
    print(f"{len(tasks)} instances in {len(names)} sets; config {CONFIG}", flush=True)
    out, t0 = [], time.time()
    with Pool(a.workers) as pool:
        for k, r in enumerate(pool.imap_unordered(run_instance, tasks), 1):
            out.append(r)
            if k % 25 == 0 or len(r["bins"]) and r["n"] >= 10000:
                print(f"[{time.time() - t0:7.0f}s] {k}/{len(tasks)} {r['set']} {r['id']} {r['bins']} opt={r.get('opt')}", flush=True)
    out.sort(key=lambda r: (r["set"], r["id"]))
    Path(a.out).write_text(json.dumps({"config": CONFIG, "instances": out}, indent=1))
    print(f"wrote {a.out} ({len(out)} instances, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
