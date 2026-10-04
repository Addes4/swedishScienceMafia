"""Analysis for short-horizon-v1: primary contrasts from audit.json, secondary measures from each run's
evals.jsonl / events.jsonl / usage.jsonl. Writes summary.json and tables.md (see PROTOCOL.md).

    python experiments/short-horizon-v1/analyze.py
"""
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau

HERE = Path(__file__).resolve().parent
ARMS = {"A": "bp_sh_a5000", "B": "bp_sh_b200", "C": "bp_sh_c80", "D": "bp_sh_d_cex", "E": "bp_sh_e_rand"}
PRIMARY = [("B", "A"), ("C", "A")]
SECONDARY = [("D", "E"), ("D", "A"), ("E", "A")]
BOOT_SEED, BOOT_DRAWS = 20261004, 10000


def boot_diff(x, y):
    rng = np.random.default_rng(BOOT_SEED)
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = rng.choice(x, (BOOT_DRAWS, len(x))).mean(1) - rng.choice(y, (BOOT_DRAWS, len(y))).mean(1)
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def perm_p(x, y):
    """Exact two-sided permutation p-value for the difference in means."""
    pool = list(x) + list(y)
    obs = abs(np.mean(x) - np.mean(y))
    n, k = len(pool), len(x)
    hits = total = 0
    for idx in itertools.combinations(range(n), k):
        a = [pool[i] for i in idx]
        b = [pool[i] for i in range(n) if i not in idx]
        total += 1
        hits += abs(np.mean(a) - np.mean(b)) >= obs - 1e-12
    return hits / total


def run_secondaries(run_dir):
    ev = {}
    for line in (run_dir / "evals.jsonl").read_text().splitlines():
        r = json.loads(line)
        ev[r["tag"]] = r
    steps = [json.loads(l) for l in (run_dir / "events.jsonl").read_text().splitlines()]
    steps = [s for s in steps if s.get("event") == "step"]
    valid = [r for r in ev.values() if r.get("correct") and r.get("hidden_mean") is not None]
    pub = [r["combined"] for r in valid]
    pub5 = [float(np.mean(r["public_normalized"][:2])) for r in valid]
    hid = [r["hidden_mean"] for r in valid]
    tau = kendalltau(pub, hid).statistic if len(valid) > 2 else None
    h_inc = ev["initial"]["hidden_mean"]
    false_rej = false_rej_material = false_acc = promotions = 0
    for s in steps:
        c = ev.get(f"it{s['iter']:04d}")
        if c is None or not c.get("correct") or c.get("hidden_mean") is None:
            continue
        h = c["hidden_mean"]
        if s["outcome"] in ("not_better", "gate_rejected"):
            false_rej += h > h_inc + 1e-9
            false_rej_material += h > h_inc + 5e-4
        elif s["outcome"] == "improved":
            promotions += 1
            false_acc += h < h_inc - 1e-9
            h_inc = h
    usage = [json.loads(l) for l in (run_dir / "usage.jsonl").read_text().splitlines()]
    spend = sum(u.get("cost_usd") or 0 for u in usage if u.get("event") == "call")
    outcomes = {}
    for s in steps:
        outcomes[s["outcome"]] = outcomes.get(s["outcome"], 0) + 1
    return {"valid_candidates": len(valid), "tau_public_hidden": tau,
            "tau_public5k_or_short_hidden": kendalltau(pub5, hid).statistic if len(valid) > 2 else None,
            "promotions": promotions, "false_rejections": int(false_rej),
            "false_rejections_material": int(false_rej_material), "false_acceptances": int(false_acc),
            "steps": len(steps), "spend_usd": spend, "outcomes": outcomes}


def main():
    audit = json.loads((HERE / "audit.json").read_text())["programs"]
    bf = {r["seed"]: r for r in audit["ref:best_fit"]["per_instance"]}

    def delta(name):
        rs = audit[name]["per_instance"]
        if not all(r["valid"] for r in rs):
            return None, None
        d = [r["excess_pct"] - bf[r["seed"]]["excess_pct"] for r in rs]
        my = [r["myopia"] for r in rs if "myopia" in r]
        return float(np.mean(d)), float(np.mean(my)) if my else None

    refs = {k[4:]: dict(zip(("delta_pp_vs_best_fit", "myopia"), delta(k))) for k in audit if k.startswith("ref:")}
    runs, per_arm = {}, {a: [] for a in ARMS}
    for arm, folder in ARMS.items():
        for seed in range(4):
            name = f"{folder}-s{seed}"
            key = f"run:{name}"
            if key not in audit:
                continue
            dpp, my = delta(key)
            sec = run_secondaries(HERE / "runs" / name)
            runs[name] = {"arm": arm, "seed": seed, "delta_pp_vs_best_fit": dpp, "myopia": my, **sec}
            if dpp is not None:
                per_arm[arm].append(dpp)
    arm_summary = {}
    for arm in ARMS:
        rs = [r for r in runs.values() if r["arm"] == arm]
        arm_summary[arm] = {
            "runs": len(rs), "delta_pp_mean": float(np.mean(per_arm[arm])) if per_arm[arm] else None,
            "delta_pp_runs": per_arm[arm],
            "myopia_mean": float(np.mean([r["myopia"] for r in rs if r["myopia"] is not None])) if rs else None,
            "tau_mean": float(np.mean([r["tau_public_hidden"] for r in rs if r["tau_public_hidden"] is not None])) if rs else None,
            "false_rejections_mean": float(np.mean([r["false_rejections"] for r in rs])) if rs else None,
            "false_rejections_material_mean": float(np.mean([r["false_rejections_material"] for r in rs])) if rs else None,
            "false_acceptances_mean": float(np.mean([r["false_acceptances"] for r in rs])) if rs else None,
            "promotions_mean": float(np.mean([r["promotions"] for r in rs])) if rs else None,
            "spend_usd": float(sum(r["spend_usd"] for r in rs)),
        }
    contrasts = {}
    for kind, pairs in (("primary", PRIMARY), ("secondary", SECONDARY)):
        for a, b in pairs:
            x, y = per_arm[a], per_arm[b]
            if len(x) >= 2 and len(y) >= 2:
                contrasts[f"{a}-{b}"] = {"kind": kind, "mean": float(np.mean(x) - np.mean(y)), "ci95": boot_diff(x, y),
                                         "perm_p": perm_p(x, y)}
    prim = sorted((v["perm_p"], k) for k, v in contrasts.items() if v["kind"] == "primary")
    running = 0.0
    for i, (p, k) in enumerate(prim):
        running = max(running, min(1.0, (len(prim) - i) * p))
        contrasts[k]["holm_p"] = running
    summary = {"references": refs, "arms": arm_summary, "contrasts": contrasts, "runs": runs,
               "total_spend_usd": float(sum(r["spend_usd"] for r in runs.values()))}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1))

    L = ["# short-horizon-v1 tables", "", "Generated by `analyze.py` from `audit.json` and the run folders.", "",
         "## Fresh audit: 100 new 5,000-item instances (Δ vs best fit, pp; lower is better)", "",
         "| Arm | Selection instances | Runs | Δ vs best fit, per run | Arm mean | Myopia (mean) | τ(public, hidden) | Promotions | Long-horizon false rejections (material) | False acceptances | Spend |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    desc = {"A": "2 × 5,000", "B": "2 × 25 × 200", "C": "2 × 63/62 × 80", "D": "2 × 5,000 + counterexample suite",
            "E": "2 × 5,000 + random suite (same lengths)"}
    for arm, s in arm_summary.items():
        f = lambda v, p=3: "—" if v is None else f"{v:.{p}f}"
        L.append(f"| {arm} | {desc[arm]} | {s['runs']} | {', '.join(f'{v:+.3f}' for v in s['delta_pp_runs'])} | "
                 f"{f(s['delta_pp_mean'])} | {f(s['myopia_mean'], 4)} | {f(s['tau_mean'], 2)} | {f(s['promotions_mean'], 1)} | "
                 f"{f(s['false_rejections_mean'], 1)} ({f(s['false_rejections_material_mean'], 1)}) | {f(s['false_acceptances_mean'], 1)} | ${s['spend_usd']:.3f} |")
    L += ["", "References on the same instances: " + ", ".join(
        f"{k} {v['delta_pp_vs_best_fit']:+.3f} pp (myopia {v['myopia']:.4f})" for k, v in refs.items() if v["delta_pp_vs_best_fit"] is not None) + ".",
        "", "## Contrasts (difference of arm means of Δ vs best fit, pp)", "",
        "| Contrast | Kind | Mean | 95% CI (bootstrap over runs) | Exact permutation p | Holm p |", "|---|---|---|---|---|---|"]
    for k, v in contrasts.items():
        L.append(f"| {k} | {v['kind']} | {v['mean']:+.3f} | [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] | {v['perm_p']:.3f} | "
                 f"{v.get('holm_p', float('nan')):.3f} |" if "holm_p" in v else
                 f"| {k} | {v['kind']} | {v['mean']:+.3f} | [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] | {v['perm_p']:.3f} | — |")
    L += ["", "## Runs", "", "| Run | Δ vs best fit | Myopia | Valid candidates | τ | Promotions | False rej. (material) | False acc. | Steps | Spend | Outcomes |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in runs.items():
        f = lambda v, p=3: "—" if v is None else f"{v:.{p}f}"
        L.append(f"| {name} | {f(r['delta_pp_vs_best_fit'])} | {f(r['myopia'], 4)} | {r['valid_candidates']} | {f(r['tau_public_hidden'], 2)} | "
                 f"{r['promotions']} | {r['false_rejections']} ({r['false_rejections_material']}) | {r['false_acceptances']} | {r['steps']} | "
                 f"${r['spend_usd']:.4f} | {', '.join(f'{k} {v}' for k, v in sorted(r['outcomes'].items()))} |")
    L += ["", f"Total spend: ${summary['total_spend_usd']:.4f}."]
    (HERE / "tables.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
