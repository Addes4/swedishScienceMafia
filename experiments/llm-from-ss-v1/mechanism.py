"""Post-hoc mechanism check (not in the protocol): how much of s3's gain over SS comes from its gap weighting
(100/g)^0.8 alone? Gap-histogram versions, scored on the same 100 audit instances; compared with s3's and
SS's bins from audit.json. Writes mechanism.json."""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "problems" / "bin_packing_online_ss"), str(HERE / "references")]
import verify, ss_hist

def weighted_ss(p):
    W = [0.0] + [(100 / g) ** p for g in range(1, 101)]
    def rule(N, s, C, t, T):
        best, bg = None, C
        for g in range(s, C + 1):
            if g < C and not N[g]:
                continue
            r = g - s
            d = (W[g] * (1 - 2 * N[g]) if g < C else 0.0) + (W[r] * (2 * N[r] + 1) if r > 0 else 0.0)
            if best is None or (d, r) < best:
                best, bg = (d, r), g
        return bg
    return rule

audit = json.loads((HERE / "audit.json").read_text())
seeds = list(range(audit["seeds"][0], audit["seeds"][1] + 1))
ss = {r["seed"]: r["bins"] for r in audit["per_instance"]["sum_of_squares"]}
s3 = {r["seed"]: r["bins"] for r in audit["per_instance"]["run_s3"]}
out = {}
for p in (0.0, 0.8):
    b = {s: ss_hist.pack_hist(list(verify.items_for(s, 5000)), 100, weighted_ss(p)) for s in seeds}
    d_ss = [b[s] - ss[s] for s in seeds]; d_s3 = [b[s] - s3[s] for s in seeds]
    out[f"p={p}"] = {"mean_vs_SS": sum(d_ss) / len(d_ss), "mean_vs_s3": sum(d_s3) / len(d_s3),
                     "identical_bins_to_SS": sum(x == 0 for x in d_ss)}
    print(p, out[f"p={p}"], flush=True)
(HERE / "mechanism.json").write_text(json.dumps(out, indent=1))
