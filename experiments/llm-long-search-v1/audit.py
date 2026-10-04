"""Fresh audit for llm-long-search-v1: score each run's final program on 100 new instances.

Every program runs in the integrity gate's sandbox (autoresearch.sandbox.run_online), one item at a
time, so model-written code never runs in this process. Writes audit.json next to this file.

    python experiments/llm-long-search-v1/audit.py [--instances 100] [--workers 8]
"""
import argparse
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))

import verify  # noqa: E402  (the problem's own instance generator and checker)
from autoresearch.sandbox import run_online  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED0 = 30000          # never used by any earlier study or run (see PROTOCOL.md)
N_ITEMS = 5000
SIMILARITY_INSTANCES = 10
BOOT_SEED, BOOT_DRAWS = 739, 10000


def programs():
    base = ROOT / "problems" / "bin_packing_online"
    progs = {"best_fit": base / "initial.py",
             "funsearch_weibull": base / "baselines" / "funsearch_weibull.py",
             "funsearch_or": base / "baselines" / "funsearch_or.py"}
    for run in sorted((HERE / "runs").glob("s*/best_program.py")):
        progs[f"run_{run.parent.name}"] = run
    return progs


def run_one(path, seed):
    inst = {"name": f"audit {seed}", "seed": seed, "n": N_ITEMS}
    header, inputs = verify.online(inst)
    res = run_online(str(path), verify.FUNCTION, verify.DRIVER, header, inputs, timeout_s=120)
    if not res.ok:
        return {"seed": seed, "valid": False, "error": res.error}
    chk = verify.check(res.construction, inst)
    if not chk["valid"]:
        return {"seed": seed, "valid": False, "error": chk["reason"]}
    items = verify.items_for(seed, N_ITEMS)
    l2 = verify.l2_bound(items)
    bins = verify.bins_used(res.construction, items)
    keep = res.construction if seed < SEED0 + SIMILARITY_INSTANCES else None
    return {"seed": seed, "valid": True, "bins": bins, "l2": l2,
            "excess_pct": 100.0 * (bins - l2) / l2, "seconds": res.seconds, "decisions": keep}


def boot_ci(diffs):
    rng = random.Random(BOOT_SEED)
    n = len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOT_DRAWS))
    return [means[int(0.025 * BOOT_DRAWS)], means[int(0.975 * BOOT_DRAWS) - 1]]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instances", type=int, default=100)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(argv)
    seeds = list(range(SEED0, SEED0 + a.instances))
    progs = programs()
    rows = {}
    with ThreadPoolExecutor(a.workers) as pool:
        for name, path in progs.items():
            rows[name] = list(pool.map(lambda s, p=path: run_one(p, s), seeds))
            ok = sum(r["valid"] for r in rows[name])
            print(f"{name:20s} {ok}/{len(seeds)} valid", flush=True)

    ref = {r["seed"]: r for r in rows["best_fit"]}
    fs = {r["seed"]: r for r in rows["funsearch_weibull"]}
    summary = {}
    for name, rs in rows.items():
        valid = [r for r in rs if r["valid"]]
        entry = {"path": str(progs[name].relative_to(ROOT)), "valid": len(valid), "instances": len(rs)}
        if valid:
            entry["mean_excess_pct"] = sum(r["excess_pct"] for r in valid) / len(valid)
        if len(valid) == len(rs):
            d_bf = [r["excess_pct"] - ref[r["seed"]]["excess_pct"] for r in rs]
            d_fs = [r["excess_pct"] - fs[r["seed"]]["excess_pct"] for r in rs]
            entry["delta_pp_vs_best_fit"] = sum(d_bf) / len(d_bf)
            entry["ci95_vs_best_fit"] = boot_ci(d_bf)
            entry["delta_pp_vs_funsearch_weibull"] = sum(d_fs) / len(d_fs)
            entry["ci95_vs_funsearch_weibull"] = boot_ci(d_fs)
            agree = [(x == y) for r in rs if r["decisions"] is not None
                     for x, y in zip(r["decisions"], fs[r["seed"]]["decisions"])]
            entry["decision_agreement_with_funsearch"] = sum(agree) / len(agree) if agree else None
        summary[name] = entry
        print(f"{name:20s} " + ", ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}"
                                         for k, v in entry.items() if k != "path"), flush=True)

    for rs in rows.values():
        for r in rs:
            r.pop("decisions", None)
    out = {"protocol": "PROTOCOL.md", "seeds": [seeds[0], seeds[-1]], "n_items": N_ITEMS,
           "bootstrap": {"seed": BOOT_SEED, "draws": BOOT_DRAWS}, "summary": summary, "per_instance": rows}
    (HERE / "audit.json").write_text(json.dumps(out, indent=1))
    print("wrote", HERE / "audit.json")


if __name__ == "__main__":
    main()
