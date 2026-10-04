"""Amendment 1: the MoH/HMACE leaderboard settings (capacity 100-500 x 1k/5k/10k items, 100 instances each).

Usage (from the repository root):
    python experiments/online-beyond-ss-v1/run_moh.py --workers 2

Instances come from EoH's generator: round(clip(45 * Weibull(3), 1, 100)) with
numpy.random.default_rng(600000 + 1000 * i + k), for setting i = 0..14 and instance k = 0..99.
Writes results_moh.json (per-instance bin counts and L1). No optimum is computed here.
"""
import argparse
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from fast import pack_fss, pack_wss  # noqa: E402
from frontier_snapshot import FS_OR, FS_W, pack_funsearch  # noqa: E402

CONFIG = json.loads((HERE / "config.json").read_text())
SETTINGS = [(C, n) for C in (100, 200, 300, 400, 500) for n in (1000, 5000, 10000)]


def items_for(i, k, n):
    rng = np.random.default_rng(600000 + 1000 * i + k)
    return np.round(np.clip(rng.weibull(3, n) * 45, 1, 100)).astype(int).tolist()


def run_one(task):
    i, k = task
    C, n = SETTINGS[i]
    items = items_for(i, k, n)
    beta, alpha, c = CONFIG["beta"], CONFIG["alpha"], CONFIG["c"]
    ones = [1.0] * (C + 1)
    return {"setting": f"c{C}_n{n}", "C": C, "n": n, "k": k, "L1": math.ceil(sum(items) / C), "bins": {
        "FWSS": pack_fss(items, C, beta, c, alpha),
        "FWSS-no-finish": pack_fss(items, C, beta, 0.0, alpha),
        "SS+finish": pack_fss(items, C, 0.0, c, 0.0),
        "SS": pack_wss(items, C, ones, 0),
        "BF": pack_wss(items, C, ones, n),
        "FS-W": pack_funsearch(items, C, FS_W),
        "FS-OR": pack_funsearch(items, C, FS_OR),
    }}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--instances", type=int, default=100)
    a = ap.parse_args()
    tasks = [(i, k) for i in range(len(SETTINGS)) for k in range(a.instances)]
    tasks.sort(key=lambda t: -SETTINGS[t[0]][1])
    out, t0 = [], time.time()
    with Pool(a.workers) as pool:
        for j, r in enumerate(pool.imap_unordered(run_one, tasks), 1):
            out.append(r)
            if j % 100 == 0:
                print(f"[{time.time() - t0:6.0f}s] {j}/{len(tasks)}", flush=True)
    out.sort(key=lambda r: (r["C"], r["n"], r["k"]))
    (HERE / "results_moh.json").write_text(json.dumps({"config": CONFIG, "instances": out}))
    print(f"wrote results_moh.json ({len(out)} instances, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
