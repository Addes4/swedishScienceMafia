"""Disclosed extra references for llm-long-search-v1, scored on the same 100 audit instances.

Added after PROTOCOL.md was written: Sum-of-Squares (references/sum_of_squares.py), because an
exploratory probe elsewhere in the project found it beats FunSearch's heuristic on these instances.
It does not change the primary endpoint. It reuses audit.py's sandboxed runner and the per-instance
best-fit and FunSearch results in audit.json, and writes audit_extra.json.

    python experiments/llm-long-search-v1/audit_extra.py [--workers 8]
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit  # noqa: E402  (same runner, seeds and bootstrap)

EXTRA = {"sum_of_squares": HERE / "references" / "sum_of_squares.py"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(argv)
    base = json.loads((HERE / "audit.json").read_text())
    seeds = list(range(base["seeds"][0], base["seeds"][1] + 1))
    ref = {r["seed"]: r for r in base["per_instance"]["best_fit"]}
    fs = {r["seed"]: r for r in base["per_instance"]["funsearch_weibull"]}
    out = {"note": "added after PROTOCOL.md; not part of the primary endpoint", "summary": {}, "per_instance": {}}
    with ThreadPoolExecutor(a.workers) as pool:
        for name, path in EXTRA.items():
            rows = list(pool.map(lambda s, p=path: audit.run_one(p, s), seeds))
            for r in rows:
                r.pop("decisions", None)
            valid = [r for r in rows if r["valid"]]
            entry = {"path": str(path.relative_to(audit.ROOT)), "valid": len(valid), "instances": len(rows)}
            if len(valid) == len(rows):
                d_bf = [r["excess_pct"] - ref[r["seed"]]["excess_pct"] for r in rows]
                d_fs = [r["excess_pct"] - fs[r["seed"]]["excess_pct"] for r in rows]
                entry.update(mean_excess_pct=sum(r["excess_pct"] for r in rows) / len(rows),
                             delta_pp_vs_best_fit=sum(d_bf) / len(d_bf), ci95_vs_best_fit=audit.boot_ci(d_bf),
                             delta_pp_vs_funsearch_weibull=sum(d_fs) / len(d_fs),
                             ci95_vs_funsearch_weibull=audit.boot_ci(d_fs))
            out["summary"][name], out["per_instance"][name] = entry, rows
            print(name, {k: v for k, v in entry.items() if k != "path"}, flush=True)
    (HERE / "audit_extra.json").write_text(json.dumps(out, indent=1))
    print("wrote", HERE / "audit_extra.json")


if __name__ == "__main__":
    main()
