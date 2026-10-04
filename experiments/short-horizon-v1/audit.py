"""Fresh audit for short-horizon-v1: every run's final program and four references on 100 new 5,000-item
instances (seeds 85000-85099), in the integrity gate's sandbox, one item at a time (see PROTOCOL.md).

    python experiments/short-horizon-v1/audit.py [--workers 4]

Resumable: per-(program, seed) results are appended to audit_cache.jsonl. Writes audit.json.
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "problems" / "bin_packing_online"))
import verify  # noqa: E402  (single-stream driver, generator and checker of the original problem)
from autoresearch.sandbox import run_online  # noqa: E402

HERE = Path(__file__).resolve().parent
SEEDS = list(range(85000, 85100))
N_ITEMS = 5000
MYOPIA_INSTANCES = 10
CAP = 100


def programs():
    base = ROOT / "problems" / "bp_sh_a5000"
    progs = {"ref:best_fit": base / "initial.py",
             "ref:funsearch_weibull": base / "baselines" / "funsearch_weibull.py",
             "ref:funsearch_or": base / "baselines" / "funsearch_or.py",
             "ref:sum_of_squares": base / "baselines" / "sum_of_squares.py"}
    for p in sorted((HERE / "runs").glob("*/best_program.py")):
        progs[f"run:{p.parent.name}"] = p
    return progs


def myopia(decisions, items):
    """Share of placements that open a new bin while an already-open bin has room for the item."""
    load, count = {}, 0
    for b, x in zip(decisions, items):
        if b not in load and any(CAP - l >= x for l in load.values()):
            count += 1
        load[b] = load.get(b, 0) + x
    return count / len(items)


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
    out = {"seed": seed, "valid": True, "bins": bins, "l2": l2, "excess_pct": 100.0 * (bins - l2) / l2,
           "seconds": round(res.seconds, 2)}
    if seed < SEEDS[0] + MYOPIA_INSTANCES:
        out["myopia"] = myopia(res.construction, items)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    cache_path = HERE / "audit_cache.jsonl"
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text().splitlines():
            r = json.loads(line)
            cache[(r["sha"], r["seed"])] = r
    progs = programs()
    rows = {}
    with ThreadPoolExecutor(a.workers) as pool, cache_path.open("a") as f:
        for name, path in progs.items():
            sha = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
            todo = [s for s in SEEDS if (sha, s) not in cache]
            for r in pool.map(lambda s, p=path: run_one(p, s), todo):
                r["sha"] = sha
                cache[(sha, r["seed"])] = r
                f.write(json.dumps(r) + "\n")
                f.flush()
            rows[name] = {"path": str(path.relative_to(ROOT)), "sha": sha, "per_instance": [cache[(sha, s)] for s in SEEDS]}
            ok = sum(r["valid"] for r in rows[name]["per_instance"])
            print(f"{name:32s} {ok}/{len(SEEDS)} valid", flush=True)
    (HERE / "audit.json").write_text(json.dumps({"protocol": "PROTOCOL.md", "seeds": [SEEDS[0], SEEDS[-1]],
                                                 "n_items": N_ITEMS, "programs": rows}, indent=1))
    print("wrote", HERE / "audit.json")


if __name__ == "__main__":
    main()
