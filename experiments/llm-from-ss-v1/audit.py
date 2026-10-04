"""Fresh audit for llm-from-ss-v1 (see PROTOCOL.md): every run's final program and the references on 100 new
5,000-item instances in the gate's sandbox, the exact optimum, decision agreement and the horizon check.

    python experiments/llm-from-ss-v1/audit.py [--instances 100] [--workers 3]
"""
import argparse
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROB = ROOT / "problems" / "bin_packing_online_ss"
sys.path[:0] = [str(ROOT), str(PROB), str(HERE / "references")]
import verify  # noqa: E402
import arcflow  # noqa: E402
from autoresearch.sandbox import run_online  # noqa: E402

SEED0, N_ITEMS, AGREE_N, HORIZON_SEEDS, HORIZON_PREFIX = 84000, 5000, 10, 5, 4000
BOOT_SEED, BOOT_DRAWS = 84, 10000


def programs():
    p = {"sum_of_squares": PROB / "initial.py", "best_fit": PROB / "baselines" / "best_fit.py",
         "funsearch_weibull": PROB / "baselines" / "funsearch_weibull.py", "fwss": HERE / "references" / "priority_fss.py"}
    for run in sorted((HERE / "runs").glob("s*/best_program.py")):
        p[f"run_{run.parent.name}"] = run
    return p


def run(path, seed, n=N_ITEMS):
    inst = {"name": f"audit {seed}", "seed": seed, "n": n}
    header, inputs = verify.online(inst)
    res = run_online(str(path), verify.FUNCTION, verify.DRIVER, header, inputs, timeout_s=120)
    if not res.ok:
        return {"seed": seed, "valid": False, "error": res.error}
    chk = verify.check(res.construction, inst)
    if not chk["valid"]:
        return {"seed": seed, "valid": False, "error": chk["reason"]}
    items = verify.items_for(seed, n)
    return {"seed": seed, "valid": True, "bins": verify.bins_used(res.construction, items),
            "seconds": res.seconds, "decisions": res.construction}


def boot_ci(d):
    rng = random.Random(BOOT_SEED)
    n = len(d)
    m = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOT_DRAWS))
    return [m[int(0.025 * BOOT_DRAWS)], m[int(0.975 * BOOT_DRAWS) - 1]]


def contrast(a, b):
    d = [x["bins"] - y["bins"] for x, y in zip(a, b)]
    return {"mean": sum(d) / len(d), "ci95": boot_ci(d), "wins": sum(x < 0 for x in d),
            "ties": sum(x == 0 for x in d), "losses": sum(x > 0 for x in d)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instances", type=int, default=100)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    seeds = list(range(SEED0, SEED0 + a.instances))
    progs = programs()
    with ThreadPoolExecutor(a.workers) as pool:
        opt = dict(zip(seeds, pool.map(lambda s: arcflow.optimum(list(verify.items_for(s, N_ITEMS)), 100), seeds)))
        print("optimum done; proved", sum(o["proved"] for o in opt.values()), flush=True)
        rows = {}
        for name, path in progs.items():
            rows[name] = list(pool.map(lambda s, p=path: run(p, s), seeds))
            print(f"{name:20s} {sum(r['valid'] for r in rows[name])}/{len(seeds)} valid", flush=True)
        horizon = {}
        for name, path in progs.items():
            hs = seeds[:HORIZON_SEEDS]
            short = list(pool.map(lambda s, p=path: run(p, s, HORIZON_PREFIX), hs))
            diffs = []
            for s, r4 in zip(hs, short):
                r5 = next(r for r in rows[name] if r["seed"] == s)
                if r4["valid"] and r5["valid"]:
                    diffs.append(sum(x != y for x, y in zip(r4["decisions"], r5["decisions"][:HORIZON_PREFIX])))
                else:
                    diffs.append(None)
            horizon[name] = {"differing_decisions_in_prefix": diffs,
                             "uses_horizon": any(d for d in diffs if d is not None)}
    l1 = {s: -(-sum(verify.items_for(s, N_ITEMS)) // 100) for s in seeds}
    summary = {}
    for name, rs in rows.items():
        e = {"path": str(progs[name].relative_to(ROOT)), "valid": sum(r["valid"] for r in rs), "instances": len(rs)}
        if e["valid"] == len(rs):
            e["bins_above_opt"] = sum(r["bins"] - opt[r["seed"]]["opt"] for r in rs) / len(rs)
            e["excess_over_L1_pct"] = 100 * sum(r["bins"] - l1[r["seed"]] for r in rs) / sum(l1.values())
            for ref in ("sum_of_squares", "funsearch_weibull", "fwss"):
                if all(x["valid"] for x in rows[ref]):
                    e[f"vs_{ref}"] = contrast(rs, rows[ref])
            for ref in ("sum_of_squares", "funsearch_weibull"):
                agree = [x == y for r, q in zip(rs[:AGREE_N], rows[ref][:AGREE_N]) for x, y in zip(r["decisions"], q["decisions"])]
                e[f"decision_agreement_{ref}"] = sum(agree) / len(agree)
            e["beats_sum_of_squares"] = e["vs_sum_of_squares"]["ci95"][1] < 0
        e["horizon"] = horizon[name]
        e["mean_seconds"] = sum(r.get("seconds", 0) for r in rs) / len(rs)
        summary[name] = e
        print(name, {k: v for k, v in e.items() if k not in ("path", "horizon")}, flush=True)
    for rs in rows.values():
        for r in rs:
            r.pop("decisions", None)
    out = {"protocol": "PROTOCOL.md", "seeds": [seeds[0], seeds[-1]], "n_items": N_ITEMS,
           "bootstrap": {"seed": BOOT_SEED, "draws": BOOT_DRAWS},
           "optimum": {str(s): o for s, o in opt.items()}, "summary": summary, "per_instance": rows}
    (HERE / "audit.json").write_text(json.dumps(out, indent=1))
    print("wrote", HERE / "audit.json")


if __name__ == "__main__":
    main()
