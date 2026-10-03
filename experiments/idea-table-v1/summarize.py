"""Write summary.json (headline numbers) and figure.png from analysis.json, table.jsonl and the usage logs.

    python experiments/idea-table-v1/summarize.py

Run `python -m autoresearch.policy_eval experiments/idea-table-v1` first; this script only reads
saved files and does no API calls.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_RANKERS = ("claude-haiku-4-5", "claude-opus-5-5", "jev", "codex")
FIG_POLICIES = ["uniform:haiku", "uniform:sonnet", "uniform:opus", "tiers:random", "tiers:claude-haiku-4-5",
                "tiers:claude-opus-5-5", "tiers:jev", "tiers:codex", "top2-opus:random", "top2-opus:claude-opus-5-5",
                "top2-opus:jev", "top2-opus:codex"]


def _jsonl(path):
    path = Path(path)
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def _ci(s, digits=4):
    return {k: (round(s[k], digits) if isinstance(s.get(k), float) else s.get(k)) for k in ("mean", "lo", "hi")}


def summarize(folder: Path) -> dict:
    a = json.loads((folder / "analysis.json").read_text())
    usage = _jsonl(folder / "usage.jsonl")
    modal = _jsonl(folder / "modal_usage.jsonl")
    rows = _jsonl(folder / "table.jsonl")
    rankings = json.loads((folder / "rankings.json").read_text())
    by_tag = Counter(u["tag"].split("/")[0] for u in usage)
    spend = {}
    for u in usage:
        k = u["tag"].split("/")[0]
        spend[k] = spend.get(k, 0.0) + (u.get("cost") or 0.0)
    out = {
        "experiment": "idea-table-v1",
        "question": "Does ranking ideas before implementation predict which ideas improve the program, and which "
                    "triage policy gives the best result per dollar?",
        "problem": "erdos_squares", "parent_score": a["parent_score"], "parent_hidden": a["parent_hidden"],
        "n_ideas": a["n_ideas"], "n_cells": len(rows), "excluded_ideas": a["excluded_ideas"],
        "cells_by_model": {m: {k: v for k, v in s.items() if k != "outcomes"} | {"outcomes": s["outcomes"]}
                           for m, s in a["cells"].items() if isinstance(s, dict)},
        "ideas_improved_by_any_model": a["cells"]["ideas_improved_by_any_model"],
        "rankers": {}, "policies": {}, "contrasts_primary": {},
        "noise": {k: v for k, v in a["noise"].items() if k != "detail"},
        "cross_model_agreement": {k: _ci(v, 3) for k, v in a["cross_model_agreement"].items()},
        "position_check": a.get("position_check", {}),
        "cost": {
            "anthropic_usd_total": round(sum(u.get("cost") or 0.0 for u in usage), 4),
            "anthropic_usd_by_step": {k: round(v, 4) for k, v in spend.items()},
            "anthropic_calls_by_step": dict(by_tag),
            "anthropic_failed_calls": sum(not u.get("ok", True) for u in usage),
            "input_tokens": sum(u.get("input_tokens") or 0 for u in usage),
            "output_tokens": sum(u.get("output_tokens") or 0 for u in usage),
            "jev_usd": rankings["rankers"].get("jev", {}).get("meta", {}).get("cost"),
            "codex_usd_marginal": 0.0,
            "modal_usd_estimate": round(sum(m.get("cost_estimate", 0.0) for m in modal), 4),
            "modal_containers": len(modal),
            "gate_evaluations": sum(1 for r in rows if r.get("eval_host")) + sum(1 for r in rows if r.get("eval_repeat")),
        },
        "bootstrap": {"n_boot": a["n_boot"], "n_point": a["n_point"], "seed": a["seed"]},
    }
    for r, s in a["rankers"].items():
        out["rankers"][r] = {k: _ci(s[k], 3) for k in ("auc_pooled", "auc_haiku", "auc_sonnet", "auc_opus", "auc_any",
                                                       "spearman_gain", "brier_pooled")}
        out["rankers"][r]["usd_per_idea"] = a["ranker_cost_per_idea"].get(r)
        if r != "random":
            out["rankers"][r]["auc_pooled_minus_random"] = _ci(a["contrasts"][f"auc_pooled: {r} - random"], 3)
    for p, s in a["policies"].items():
        out["policies"][p] = {k: _ci(s[k], 4) for k in ("cost", "improvements", "improvements_per_dollar",
                                                        "best_public", "best_hidden", "recall_any")}
        out["policies"][p]["dollars_per_improvement"] = s["dollars_per_improvement"]
    for r in a["rankers"]:
        if r == "random":
            continue
        out["contrasts_primary"][f"tiers:{r} - tiers:random | improvements"] = _ci(
            a["contrasts"][f"tiers:{r} - tiers:random | improvements"], 3)
    return out


def figure(folder: Path, a: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, muted, grid = "#0b0b0b", "#52514e", "#e4e3df"
    blue, orange, aqua = "#2a78d6", "#eb6834", "#1baf7a"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": muted, "axes.labelcolor": ink, "xtick.color": muted,
                         "ytick.color": muted, "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.5]})

    names = [r for r in ("random",) + MAIN_RANKERS if r in a["rankers"]]
    for y, r in enumerate(names):
        s = a["rankers"][r]["auc_pooled"]
        ax1.plot([s["lo"], s["hi"]], [y, y], color=blue, lw=2, solid_capstyle="round")
        ax1.plot(s["mean"], y, "o", color=blue, ms=8, mec="white", mew=2)
        ax1.text(s["hi"] + 0.01, y, f"{s['mean']:.2f}", va="center", color=ink, fontsize=8)
    ax1.axvline(0.5, color=muted, ls="--", lw=1)
    ax1.set_yticks(range(len(names)), names)
    ax1.set_xlabel("AUC of ranker key vs 'improved' (pooled over 3 models; 0.5 = chance)")
    ax1.set_title("A. Do rankers predict which ideas improve?", loc="left", color=ink, fontsize=10)
    ax1.grid(axis="x", color=grid, lw=0.8)
    ax1.set_axisbelow(True)

    fam = {"uniform": (blue, "uniform model"), "tiers": (orange, "ranked tiers (opus/sonnet/haiku thirds)"),
           "top2-opus": (aqua, "top 2 of 6 to Opus, rest skipped")}
    seen = set()
    for p in FIG_POLICIES:
        if p not in a["policies"]:
            continue
        s = a["policies"][p]
        f = p.split(":")[0]
        color, label = fam[f]
        x, y = s["cost"]["mean"], s["improvements"]["mean"]
        ax2.plot([x, x], [s["improvements"]["lo"], s["improvements"]["hi"]], color=color, lw=2, alpha=0.6)
        ax2.plot(x, y, "o", color=color, ms=8, mec="white", mew=2, label=None if f in seen else label)
        seen.add(f)
        ax2.annotate(p.split(":", 1)[1].replace("claude-", "").replace("-4-5", "").replace("-5-5", ""),
                     (x, y), xytext=(5, 3), textcoords="offset points", fontsize=7, color=muted)
    ax2.set_xlabel(f"Implementation spend over the {a['n_ideas']}-idea pool (US$, incl. ranker)")
    ax2.set_ylabel("Improving programs found (count)")
    ax2.set_title("B. Result per dollar by policy (95% bootstrap intervals)", loc="left", color=ink, fontsize=10)
    ax2.grid(color=grid, lw=0.8)
    ax2.set_axisbelow(True)
    ax2.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(folder / "figure.png", dpi=160)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=str(HERE))
    ap.add_argument("--no-figure", action="store_true")
    args = ap.parse_args()
    folder = Path(args.folder)
    out = summarize(folder)
    (folder / "summary.json").write_text(json.dumps(out, indent=2))
    if not args.no_figure:
        figure(folder, json.loads((folder / "analysis.json").read_text()))
    print(json.dumps({k: out[k] for k in ("n_ideas", "n_cells", "cost")}, indent=2))


if __name__ == "__main__":
    main()
