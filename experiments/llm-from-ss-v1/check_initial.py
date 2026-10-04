"""Pre-run check: initial.py (Sum-of-Squares in the priority interface) run in the gate's sandbox, one
instance per process, gives the same bin counts as the gap-histogram Sum-of-Squares from
online-frontier-v1. Seeds 84900-84904 (reserved range, outside the audit set). Writes check_initial.json."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "problems" / "bin_packing_online_ss"), str(HERE / "references")]
import verify, ss_hist
from autoresearch.sandbox import run_online
rows = []
for seed in range(84900, 84905):
    inst = {"name": f"check {seed}", "seed": seed, "n": 5000}
    header, inputs = verify.online(inst)
    res = run_online(str(ROOT / "problems/bin_packing_online_ss/initial.py"), verify.FUNCTION, verify.DRIVER, header, inputs, timeout_s=120)
    items = verify.items_for(seed, 5000)
    sandbox = verify.bins_used(res.construction, items) if res.ok else None
    ref = ss_hist.pack_hist(list(items), 100, ss_hist.sum_of_squares)
    rows.append({"seed": seed, "sandbox_bins": sandbox, "frontier_ss_bins": ref, "equal": sandbox == ref, "seconds": res.seconds})
    print(rows[-1], flush=True)
json.dump({"rows": rows, "all_equal": all(r["equal"] for r in rows)}, open(HERE / "check_initial.json", "w"), indent=1)
