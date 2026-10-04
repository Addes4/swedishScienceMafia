"""Pre-run checks required by PROTOCOL.md: compact evaluator == full evaluator; vectorised ab-WF ==
transcription; arc-flow OPT == OR-Library's listed optimum. Writes checks.json."""
import json, time
import numpy as np
import frontier as F

out = {"compact_equals_full": [], "abwf_vectorised_equals_transcription": [], "or_opt_matches_listed": []}
sets = {f"W5k-released/{k}": (c, it) for k, (c, it) in F.load_released_weibull().items()}
sets.update({f"OR3/{k}": (c, it) for k, (c, it, b) in F.load_orlib(3).items()})
for name, (C, items) in sets.items():
    for label, pr in [("FS-W", F.FS_W), ("FS-OR", F.FS_OR), ("ab-WF", F.ab_worst_fit(C=C))]:
        a, b = F.pack_funsearch(items, C, pr, compact=True), F.pack_funsearch(items, C, pr, compact=False)
        out["compact_equals_full"].append({"instance": name, "policy": label, "compact": a, "full": b, "equal": a == b})
    if name.startswith("W5k") or name.endswith("_00") or name.endswith("_01"):
        a = F.pack_funsearch(items, C, F.ab_worst_fit(C=C)); b = F.pack_funsearch(items, C, F.ab_priority("ab_worst_fit", 1, 21, C))
        out["abwf_vectorised_equals_transcription"].append({"instance": name, "vectorised": a, "transcription": b, "equal": a == b})
    print(name, "done", flush=True)
for i in (1, 2, 3, 4):
    for k, (C, items, best) in F.load_orlib(i).items():
        t = time.time(); r = F.optimum(items, C)
        out["or_opt_matches_listed"].append({"set": f"OR{i}", "instance": k, "listed": best, "opt": r.get("opt"),
                                            "proved": r["proved"], "seconds": round(time.time() - t, 2), "equal": r.get("opt") == best})
    print(f"OR{i} optima done", flush=True)
summ = {k: f"{sum(x['equal'] for x in v)}/{len(v)}" for k, v in out.items()}
out["summary"] = summ
json.dump(out, open("checks.json", "w"), indent=1)
print(summ)
print("max OPT seconds", max(x["seconds"] for x in out["or_opt_matches_listed"]))
