"""Fresh audit for llm-informed-v1 (see PROTOCOL.md): every program on the same 100 new instances.

Programs: the 4 informed runs (this study), the 4 uninformed runs of llm-long-search-v1, best fit,
FunSearch's Weibull heuristic, Sum-of-Squares and FWSS. Each runs in the integrity gate's sandbox
(autoresearch.sandbox.run_online): a fresh process per instance, one item at a time. Writes audit.json.

    python experiments/llm-informed-v1/audit.py [--instances 100] [--workers 4]
"""
import argparse
import itertools
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))

import verify  # noqa: E402  (identical in bin_packing_online and bin_packing_online_informed)
from autoresearch.sandbox import run_online  # noqa: E402

HERE = Path(__file__).resolve().parent
LONG = ROOT / "experiments" / "llm-long-search-v1"
SEED0, N_ITEMS = 30000, 5000          # the same instances as llm-long-search-v1's audit
AGREE_INSTANCES = 10
BOOT_SEED, BOOT_DRAWS = 739, 10000


def programs():
    base = ROOT / "problems" / "bin_packing_online"
    progs = {"best_fit": base / "initial.py",
             "funsearch_weibull": base / "baselines" / "funsearch_weibull.py",
             "sum_of_squares": LONG / "references" / "sum_of_squares.py",
             "fwss": ROOT / "experiments" / "online-beyond-ss-v1" / "priority_fss.py"}
    for run in sorted((HERE / "runs").glob("s*/best_program.py")):
        progs[f"informed_{run.parent.name}"] = run
    for run in sorted((LONG / "runs").glob("s*/best_program.py")):
        progs[f"uninformed_{run.parent.name}"] = run
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
    keep = res.construction if seed < SEED0 + AGREE_INSTANCES else None
    return {"seed": seed, "valid": True, "bins": bins, "l2": l2,
            "excess_pct": 100.0 * (bins - l2) / l2, "seconds": res.seconds, "decisions": keep}


def boot_ci(diffs):
    rng = random.Random(BOOT_SEED)
    n = len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOT_DRAWS))
    return [means[int(0.025 * BOOT_DRAWS)], means[int(0.975 * BOOT_DRAWS) - 1]]


def agreement(rs, ref):
    pairs = [(x == y) for r in rs if r.get("decisions") is not None
             for x, y in zip(r["decisions"], ref[r["seed"]]["decisions"])]
    return sum(pairs) / len(pairs) if pairs else None


def permutation_p(a, b):
    """Exact two-sided permutation p-value for the difference in means between two small groups."""
    pooled, k = a + b, len(a)
    obs = abs(sum(a) / len(a) - sum(b) / len(b))
    hits = total = 0
    for idx in itertools.combinations(range(len(pooled)), k):
        g1 = [pooled[i] for i in idx]
        g2 = [pooled[i] for i in range(len(pooled)) if i not in idx]
        total += 1
        hits += abs(sum(g1) / len(g1) - sum(g2) / len(g2)) >= obs - 1e-12
    return hits / total


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instances", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    seeds = list(range(SEED0, SEED0 + a.instances))
    progs = programs()
    rows = {}
    with ThreadPoolExecutor(a.workers) as pool:
        for name, path in progs.items():
            rows[name] = list(pool.map(lambda s, p=path: run_one(p, s), seeds))
            print(f"{name:22s} {sum(r['valid'] for r in rows[name])}/{len(seeds)} valid", flush=True)

    refs = {k: {r["seed"]: r for r in rows[k]} for k in ("best_fit", "funsearch_weibull", "sum_of_squares", "fwss")}
    summary = {}
    for name, rs in rows.items():
        valid = [r for r in rs if r["valid"]]
        e = {"path": str(progs[name].relative_to(ROOT)), "valid": len(valid), "instances": len(rs)}
        if valid:
            e["mean_excess_pct"] = sum(r["excess_pct"] for r in valid) / len(valid)
        if len(valid) == len(rs):
            for ref_name, ref in refs.items():
                d = [r["excess_pct"] - ref[r["seed"]]["excess_pct"] for r in rs]
                db = [r["bins"] - ref[r["seed"]]["bins"] for r in rs]
                e[f"delta_pp_vs_{ref_name}"] = sum(d) / len(d)
                e[f"ci95_vs_{ref_name}"] = boot_ci(d)
                e[f"mean_bins_vs_{ref_name}"] = sum(db) / len(db)
                e[f"wtl_vs_{ref_name}"] = [sum(x < 0 for x in db), sum(x == 0 for x in db), sum(x > 0 for x in db)]
            for ref_name in ("funsearch_weibull", "sum_of_squares", "fwss"):
                e[f"decision_agreement_with_{ref_name}"] = agreement(rs, refs[ref_name])
            e["Q1_beats_funsearch"] = e["ci95_vs_funsearch_weibull"][1] < 0
            e["Q2_reaches_ss"] = e["ci95_vs_sum_of_squares"][1] <= 0      # interval at or below 0
            e["Q3_reaches_fwss"] = e["ci95_vs_fwss"][0] <= 0
        summary[name] = e
        print(f"{name:22s} excess {e.get('mean_excess_pct', float('nan')):.3f}%  "
              f"vs FS {e.get('delta_pp_vs_funsearch_weibull', float('nan')):+.3f}  "
              f"vs SS {e.get('delta_pp_vs_sum_of_squares', float('nan')):+.3f}  "
              f"vs FWSS {e.get('delta_pp_vs_fwss', float('nan')):+.3f}", flush=True)

    inf = [summary[k]["mean_excess_pct"] for k in summary if k.startswith("informed_") and "mean_excess_pct" in summary[k]]
    uninf = [summary[k]["mean_excess_pct"] for k in summary if k.startswith("uninformed_") and "mean_excess_pct" in summary[k]]
    q4 = None
    if inf and uninf:
        q4 = {"informed_mean": sum(inf) / len(inf), "uninformed_mean": sum(uninf) / len(uninf),
              "informed_best": min(inf), "uninformed_best": min(uninf),
              "permutation_p_two_sided": permutation_p(inf, uninf) if len(inf) + len(uninf) <= 12 else None}
        print("Q4", q4)

    # Positive control: shared programs must reproduce llm-long-search-v1's audit exactly.
    control = {}
    old_path = LONG / "audit.json"
    if old_path.exists():
        old = json.loads(old_path.read_text())["per_instance"]
        for mine, theirs in [("best_fit", "best_fit"), ("funsearch_weibull", "funsearch_weibull")] + \
                            [(f"uninformed_s{i}", f"run_s{i}") for i in range(4)]:
            if mine in rows and theirs in old:
                a_ = {r["seed"]: r.get("bins") for r in rows[mine]}
                b_ = {r["seed"]: r.get("bins") for r in old[theirs]}
                control[mine] = all(a_[s] == b_.get(s) for s in a_)
        print("positive control (identical bins to llm-long-search-v1/audit.json):", control)

    for rs in rows.values():
        for r in rs:
            r.pop("decisions", None)
    out = {"protocol": "PROTOCOL.md", "seeds": [seeds[0], seeds[-1]], "n_items": N_ITEMS,
           "bootstrap": {"seed": BOOT_SEED, "draws": BOOT_DRAWS}, "summary": summary, "Q4": q4,
           "positive_control": control, "per_instance": rows}
    (HERE / "audit.json").write_text(json.dumps(out, indent=1))
    print("wrote", HERE / "audit.json")


if __name__ == "__main__":
    main()
