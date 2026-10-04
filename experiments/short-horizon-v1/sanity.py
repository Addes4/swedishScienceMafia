"""Pre-run checks for short-horizon-v1: every arm's evaluator runs best fit, FunSearch's heuristics and
Sum-of-Squares through the integrity gate; multi-stream state resets are verified against an independent
per-stream simulation; the generator matches problems/bin_packing_online. Writes sanity.json."""
import importlib.util, json, os, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from autoresearch.gate import evaluate

def load(path, name="m"):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

orig = load(ROOT / "problems/bin_packing_online/verify.py", "orig")
out = {"generator_matches": None, "arms": {}, "ss_reset_check": {}}
v = load(ROOT / "problems/bp_sh_b200/verify.py", "vb")
out["generator_matches"] = all(v.items_for(s, 200) == orig.items_for(s, 200) for s in (85600, 85601, 85649))

def ss_bins(items, C=100):   # independent SS (fresh state per stream), ties to tighter fit
    N = [0]*(C+1); opened = 0
    for s in items:
        best = None
        for g in range(s, C+1):
            if g < C and not N[g]: continue
            r = g - s; d = (1 - 2*N[g] if g < C else 0) + (2*N[r] + 1 if r > 0 else 0)
            if best is None or (d, r) < best: best, bg = (d, r), g
        if bg == C: opened += 1
        else: N[bg] -= 1
        if bg - s > 0: N[bg - s] += 1
    return opened

progs = {"best_fit": "initial.py", "funsearch_weibull": "baselines/funsearch_weibull.py", "sum_of_squares": "baselines/sum_of_squares.py"}
for arm in ["bp_sh_a5000", "bp_sh_b200", "bp_sh_c80", "bp_sh_d_cex", "bp_sh_e_rand"]:
    d = ROOT / "problems" / arm; out["arms"][arm] = {}
    for name, rel in progs.items():
        with tempfile.TemporaryDirectory() as tmp:
            t = time.time(); m = evaluate(d, str(d / rel), tmp)
            integ = json.load(open(os.path.join(tmp, "integrity.json")))
        out["arms"][arm][name] = {"combined": m["combined_score"], "public": m["public"], "hidden_mean": m["private"]["hidden_mean"],
                                  "reasons": [r.get("reason") for r in integ["public"]], "seconds": round(time.time() - t, 1)}
        print(arm, name, round(m["combined_score"], 6), m["private"]["hidden_mean"], [r.get("reason") for r in integ["public"]], flush=True)
# SS reset check on arm B: gate bins per instance must equal independent per-stream SS bins
vb = load(ROOT / "problems/bp_sh_b200/verify.py", "vb2")
for inst in vb.PUBLIC:
    ss = vb.streams(inst); exp_bins = sum(ss_bins(s) for s in ss); l2 = sum(vb.l2_bound(s) for s in ss)
    got = out["arms"]["bp_sh_b200"]["sum_of_squares"]["public"][vb.label(inst)]
    out["ss_reset_check"][inst["name"]] = {"expected_score": l2 / exp_bins, "gate_score": got, "equal": abs(l2/exp_bins - got) < 1e-12}
print(out["ss_reset_check"], "generator", out["generator_matches"])
json.dump(out, open(Path(__file__).parent / "sanity.json", "w"), indent=1)
