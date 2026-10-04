"""online-frontier-v1 confirmatory run: every policy and the exact optimum on every instance in PROTOCOL.md.

    python run.py [--workers 2]     # appends to results.jsonl; finished instances are skipped on restart
"""
import argparse
import json
import multiprocessing as mp
import time
from pathlib import Path

import frontier as F

HERE = Path(__file__).resolve().parent
OUT = HERE / "results.jsonl"


def tasks():
    t = [("W5k-released", k, None) for k in F.load_released_weibull()]
    for i in (1, 2, 3, 4):
        t += [(f"OR{i}", k, None) for k in F.load_orlib(i)]
    t += [("W5k-fresh", f"seed{s}", (s, 5000)) for s in range(81000, 81100)]
    t += [("W10k-fresh", f"seed{s}", (s, 10000)) for s in range(82000, 82020)]
    t += [("W100k-fresh", f"seed{s}", (s, 100000)) for s in range(83000, 83005)]
    return t


def instance(set_name, name, fresh):
    if fresh:
        C, items = F.fresh(*fresh)
        return C, items, None
    if set_name == "W5k-released":
        C, items = F.load_released_weibull()[name]
        return C, items, None
    return F.load_orlib(int(set_name[2]))[name]


def solve(task):
    set_name, name, fresh = task
    C, items, listed = instance(set_name, name, fresh)
    row = {"set": set_name, "instance": name, "n": len(items), "capacity": C,
           "L1": F.l1_bound(items, C), "L2": F.verify.l2_bound(items, C), "listed_opt": listed, "bins": {}, "seconds": {}}
    t = time.time()
    row["opt"] = F.optimum(items, C)
    row["seconds"]["OPT"] = round(time.time() - t, 2)
    policies = [(k, lambda r=r: F.pack_hist(items, C, r)) for k, r in F.HIST_POLICIES.items()]
    policies += [("FS-W", lambda: F.pack_funsearch(items, C, F.FS_W)),
                 ("FS-OR", lambda: F.pack_funsearch(items, C, F.FS_OR)),
                 ("ab-WF", lambda: F.pack_funsearch(items, C, F.ab_worst_fit(C=C))),
                 ("SS-view", lambda: F.pack_funsearch(items, C, lambda it, b: F.ss_view(it, b, C)))]
    for k, f in policies:
        t = time.time()
        row["bins"][k] = f()
        row["seconds"][k] = round(time.time() - t, 2)
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    done = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            r = json.loads(line)
            done.add((r["set"], r["instance"]))
    todo = [t for t in tasks() if (t[0], t[1]) not in done]
    print(f"{len(todo)} instances to run, {len(done)} already done", flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool, OUT.open("a") as f:
        for row in pool.imap_unordered(solve, todo):
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(time.strftime("%H:%M:%S"), row["set"], row["instance"], "OPT", row["opt"].get("opt"),
                  {k: v - row["opt"].get("opt", 0) for k, v in row["bins"].items()}, flush=True)


if __name__ == "__main__":
    main()
