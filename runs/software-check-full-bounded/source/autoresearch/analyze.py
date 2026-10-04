"""Summarise and compare triage runs.

    python -m autoresearch.analyze results/triage_*/log.jsonl          # comparison table
    python -m autoresearch.analyze results/run_a/log.jsonl --curve c.csv  # best score vs dollars, for plotting
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def _events(log_path):
    with open(log_path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _auc(pos, neg):
    """P(a random improving idea was ranked above a random non-improving one); 0.5 = chance."""
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def _rate(rows):
    return round(sum(r["outcome"] == "improved" for r in rows) / len(rows), 3) if rows else None


def summarize(log_path) -> dict:
    ev = _events(log_path)
    start = next(e for e in ev if e["event"] == "start")
    results = [e for e in ev if e["event"] == "result"]
    promos = [e for e in ev if e["event"] == "promotion"]
    ends = [e for e in ev if e["event"] == "round_end"]
    cost = defaultdict(float)
    for e in ev:
        if e["event"] == "propose":
            cost["propose"] += e["cost"]
        elif e["event"] == "rank":
            cost["rank"] += e["cost"]
        elif e["event"] in ("result", "promotion"):
            cost[f"implement:{e['model']}"] += e.get("cost", 0.0)

    by_tier = {}
    for tier in ("favourite", "middle", "long_shot"):
        rows = [r for r in results if r["tier"] == tier]
        by_tier[tier] = {"ideas": len(rows), "improved": sum(r["outcome"] == "improved" for r in rows),
                         "success_rate": _rate(rows), "cost": round(sum(r.get("cost", 0) for r in rows), 4),
                         "models": sorted({r["model"] for r in rows})}

    judged = [r for r in results if r["outcome"] not in ("api_error", "refused")]
    pos = [r["ranker_key"] for r in judged if r["outcome"] == "improved"]
    neg = [r["ranker_key"] for r in judged if r["outcome"] != "improved"]
    brier = (sum((r["p_improve"] - (r["outcome"] == "improved")) ** 2 for r in judged) / len(judged)) if judged else None
    planned = {t: _rate([r for r in judged if r["planned_tier"] == t]) for t in ("favourite", "middle", "long_shot")}
    swaps = defaultdict(list)
    for r in judged:
        if r["swapped"]:
            swaps[f"{r['planned_tier']} -> {r['tier']}"].append(r)

    return {
        "problem": start["problem"], "ranker": start["ranker"], "uniform": start.get("uniform"),
        "initial_score": start["initial_score"],
        "best_score": ends[-1]["best_score"] if ends else start["initial_score"],
        "rounds": len(ends), "ideas": len(results),
        "spent_usd": round(ev[-1]["spent_total"], 4), "cost_breakdown": {k: round(v, 4) for k, v in cost.items()},
        "outcomes": dict(sorted(Counter(r["outcome"] for r in results).items())),
        "by_tier": by_tier,
        "ranker_quality": {
            "auc": None if _auc(pos, neg) is None else round(_auc(pos, neg), 3),
            "brier_p_improve": None if brier is None else round(brier, 4),
            "success_rate_by_planned_tier": planned,
        },
        "swaps": {k: {"n": len(v), "success_rate": _rate(v)} for k, v in swaps.items()},
        "promotions": {"n": len(promos), "improved_further": sum(p.get("outcome") == "improved" for p in promos)},
        "curve": [(round(e["spent_total"], 4), e["best_score"]) for e in ends],
    }


def write_notebook(log_path, out_path):
    ev = _events(log_path)
    start = next(e for e in ev if e["event"] == "start")
    lines = [f"# Research notebook: {start['problem']}", "",
             f"Ranker `{start['ranker']}`, tiers {start['tiers']}, swap rate {start['swap_rate']}, "
             f"initial score {start['initial_score']:.6f}.", ""]
    for e in ev:
        if e["event"] == "propose":
            lines += [f"## Round {e['round']}", "", "| # | idea | rank key | planned | ran on | outcome | score |",
                      "|---|---|---|---|---|---|---|"]
        elif e["event"] == "result":
            swap = " (swapped)" if e["swapped"] else ""
            score = f"{e['score']:.6f}" if e.get("score") is not None else ""
            idea = e["idea"].replace("|", "/")[:160]
            lines.append(f"| {e['idea_index']} | {idea} | {e['ranker_key']:.2f} | {e['planned_tier']} | "
                         f"{e['model'].replace('claude-', '')}{swap} | {e['outcome']} | {score} |")
        elif e["event"] == "promotion":
            lines += ["", f"Promotion: {e['promoted_from']} found an improvement; {e['model']} refined it -> "
                          f"{e.get('outcome')} ({e.get('score', 0):.6f})."]
        elif e["event"] == "round_end":
            lines += ["", f"Best after round {e['round']}: **{e['best_score']:.6f}** (spent ${e['spent_total']:.2f})", ""]
    Path(out_path).write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--curve", help="write spent-vs-best-score CSV for all runs")
    args = ap.parse_args()
    sums = [(p, summarize(p)) for p in args.logs]
    print(f"{'run':<44} {'ranker':<7} {'uniform':<18} {'best':>9} {'$':>8} {'ideas':>5} {'AUC':>5} {'fav/mid/long success':>22}")
    for p, s in sums:
        q = s["ranker_quality"]["success_rate_by_planned_tier"]
        tiers = "/".join("-" if q[t] is None else f"{q[t]:.2f}" for t in ("favourite", "middle", "long_shot"))
        auc = s["ranker_quality"]["auc"]
        print(f"{Path(p).parent.name[:44]:<44} {s['ranker']:<7} {str(s['uniform'] or '-'):<18} {s['best_score']:>9.5f} "
              f"{s['spent_usd']:>8.2f} {s['ideas']:>5} {('-' if auc is None else f'{auc:.2f}'):>5} {tiers:>22}")
    if args.curve:
        with open(args.curve, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["run", "ranker", "uniform", "spent_usd", "best_score"])
            for p, s in sums:
                for spent, score in s["curve"]:
                    w.writerow([Path(p).parent.name, s["ranker"], s["uniform"] or "", spent, score])
        print(f"curve written to {args.curve}")


if __name__ == "__main__":
    main()
