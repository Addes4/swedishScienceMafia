"""Tournament report: tables, paired comparisons and best-score-versus-dollars curves.

    python -m tournament.report experiments/tournament-v1/runs/full-v1 --recompute
    python -m tournament.report runs/full-v1 runs/full-v1-rerun --out runs/merged      # a later folder's run
                                                                                       # replaces an earlier one
Writes report.md, report.html (inline SVG, no scripts), all_curves.csv and results.json to --out
(default: the first folder), plus --figure (standalone SVG) and --headline (JSON) if given.

Two analyses, kept apart:

1. Full budget. Only budget-matched runs (completion "budget": the run used its cap before any API
   error) enter the per-arm table and the paired comparisons, and a pair is used only if both of
   its runs are complete. Truncated runs are listed separately with how far they got.
2. Common spend checkpoint. Per problem, X = the smallest valid spend of any run of that problem,
   rounded down to a multiple of $0.05. Every run is valid up to X, so all arms and seeds compare
   at X: the incumbent's score at X and the area under its curve over [0, X], each as a fraction
   of the headroom above the starting score.
"""
import argparse
import csv
import html
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from .metrics import CURVE_FIELDS, auc_to, score_at, summarize, valid_curve

# Categorical slots of the validated reference palette (dataviz skill, light surface #fcfcfb).
# Two of them sit below 3:1 contrast, so every chart has a legend and a table view.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
MATCHES_RECORD = 1 - 1e-6    # normalized score treated as a tie with the best known value
CHECKPOINT_STEP = 0.05


def load_runs(folders, recompute=False):
    """Runs keyed by folder name; a run in a later folder replaces one of the same name."""
    runs = {}
    for folder in folders:
        for d in sorted(p for p in Path(folder).iterdir() if p.is_dir()):
            if recompute and (d / "job.json").exists():
                s = summarize(d)
            elif (d / "summary.json").exists():
                s = json.loads((d / "summary.json").read_text())
            else:
                continue
            if "completion" not in s and (d / "job.json").exists():
                s = summarize(d)    # summaries written before completion was recorded
            s["run_dir"] = d.name
            s["source"] = Path(folder).name
            runs[d.name] = s
    return list(runs.values())


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def _fmt(x, nd=4):
    if x is None:
        return "–"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def step_value(curve, x_usd, y0):
    y = y0
    for c in curve:
        if c["spent_usd"] <= x_usd + 1e-12:
            y = c["incumbent_public"]
        else:
            break
    return y


# -- statistics --------------------------------------------------------------------------------
def bootstrap_ci(diffs, reps=10_000, seed=0):
    if len(diffs) < 2:
        return None
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(diffs, k=len(diffs))) for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def bootstrap_p_greater(diffs, reps=10_000, seed=1):
    """P(A > B) over matched units (ties count one half), with a bootstrap 95% interval."""
    score = lambda ds: sum((d > 1e-9) + 0.5 * (abs(d) <= 1e-9) for d in ds) / len(ds)
    if len(diffs) < 2:
        return score(diffs), None
    rng = random.Random(seed)
    sims = sorted(score(rng.choices(diffs, k=len(diffs))) for _ in range(reps))
    return score(diffs), (sims[int(0.025 * reps)], sims[int(0.975 * reps) - 1])


def sign_flip_p(diffs, reps=100_000, seed=2):
    """Two-sided paired permutation p-value for mean difference = 0 (exact up to 16 units)."""
    n = len(diffs)
    if n == 0:
        return None
    obs = abs(sum(diffs)) - 1e-12
    if n <= 16:
        hits = sum(abs(sum(d if (mask >> i) & 1 else -d for i, d in enumerate(diffs))) >= obs for mask in range(2 ** n))
        return hits / 2 ** n
    rng = random.Random(seed)
    hits = sum(abs(sum(d if rng.random() < 0.5 else -d for d in diffs)) >= obs for _ in range(reps))
    return (hits + 1) / (reps + 1)


def holm(pvalues: dict) -> dict:
    """Holm-adjusted p-values for a family {name: p}."""
    items = sorted((p, k) for k, p in pvalues.items() if p is not None)
    out, running = {}, 0.0
    for i, (p, k) in enumerate(items):
        running = max(running, min(1.0, (len(items) - i) * p))
        out[k] = running
    return out


def paired(runs, reference, metric):
    """Arm minus reference on matched (problem, seed) units."""
    by = {(r["arm"], r["problem"], r["seed"]): r for r in runs}
    out = {}
    for arm in sorted({r["arm"] for r in runs} - {reference}):
        diffs = [(by[(arm, p, s)][metric], by[(reference, p, s)][metric]) for (a, p, s) in by
                 if a == arm and (reference, p, s) in by]
        diffs = [x - y for x, y in diffs if x is not None and y is not None]
        if diffs:
            ci = bootstrap_ci(diffs)
            p_greater, p_ci = bootstrap_p_greater(diffs)
            out[arm] = {"n": len(diffs), "mean_diff": statistics.fmean(diffs), "ci95": ci,
                        "p_greater": p_greater, "p_greater_ci95": p_ci, "p_value": sign_flip_p(diffs),
                        "wins": sum(d > 1e-9 for d in diffs), "ties": sum(abs(d) <= 1e-9 for d in diffs),
                        "losses": sum(d < -1e-9 for d in diffs)}
    adjusted = holm({arm: c["p_value"] for arm, c in out.items()})
    for arm, c in out.items():
        c["p_holm"] = adjusted.get(arm)
    return out


SECONDARY = (("lean_gate_patience", "lean"), ("lean", "independent"))


def secondary_contrasts(runs, arms, metrics=("auc_gain", "final_public")):
    """First arm minus second on matched units, for the protocol's secondary questions."""
    out = {}
    for first, second in SECONDARY:
        if first in arms and second in arms:
            sub = [r for r in runs if r["arm"] in (first, second)]
            res = {m: paired(sub, second, m).get(first) for m in metrics}
            out[f"{first} - {second}"] = {m: c for m, c in res.items() if c}
    return out


# -- tables ------------------------------------------------------------------------------------
def group_table(runs):
    groups = defaultdict(list)
    for r in runs:
        groups[(r["problem"], r["arm"])].append(r)
    rows = []
    for (problem, arm), rs in sorted(groups.items()):
        finals = [r["final_public"] for r in rs if r["final_public"] is not None]
        rows.append({
            "problem": problem, "arm": arm, "runs": len(rs), "seeds": sorted(r["seed"] for r in rs),
            "final_public": _mean(finals), "final_min": min(finals) if finals else None,
            "final_max": max(finals) if finals else None,
            "auc_gain": _mean(r["auc_gain"] for r in rs), "final_hidden": _mean(r["final_hidden"] for r in rs),
            "spent_usd": _mean(r["spent_usd"] for r in rs), "cap_usd": _mean(r["cap_usd"] for r in rs),
            "improvements": _mean(r["improvements"] for r in rs),
            "usd_per_improvement": _mean(r["usd_per_improvement"] for r in rs),
            "tokens_per_improvement": _mean(r["tokens_per_improvement"] for r in rs),
            "calls": _mean(r["calls"] for r in rs), "idea_calls": _mean(r.get("idea_calls") for r in rs),
            "evals": _mean(r["evals"] for r in rs),
            "valid_evals": _mean(r["valid_evals"] for r in rs), "wall_s": _mean(r["wall_s"] for r in rs),
            "evals_with_timeout": _mean(r.get("evals_with_timeout") for r in rs),
            "all_within_cap": all(r["within_cap"] for r in rs),
            "matches_record": sum((r["final_public"] or 0) >= MATCHES_RECORD for r in rs),
        })
    return rows


def checkpoints(runs, step=CHECKPOINT_STEP):
    """Per problem: the largest multiple of `step` at or below every run's valid spend."""
    out = {}
    for problem in sorted({r["problem"] for r in runs}):
        low = min(r["valid_spend_usd"] for r in runs if r["problem"] == problem)
        x = math.floor(low / step + 1e-9) * step
        out[problem] = round(x, 2) if x > 0 else None
    return out


def checkpoint_rows(runs, cps):
    """One record per run at its problem's checkpoint (score and area as fractions of headroom)."""
    rows = []
    for r in runs:
        x = cps.get(r["problem"])
        if not x:
            continue
        y0 = r["initial_public"]
        s, a = score_at(r, x), auc_to(r, x)
        head = 1 - y0 if y0 is not None and y0 < 1 else None
        rows.append({"run_dir": r["run_dir"], "arm": r["arm"], "problem": r["problem"], "seed": r["seed"],
                     "checkpoint_usd": x, "initial": y0, "score": s, "auc": a,
                     "gain": (s - y0) / head if head and s is not None else None,
                     "auc_gain": (a - y0) / head if head and a is not None else None})
    return rows


def checkpoint_groups(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["problem"], r["arm"])].append(r)
    out = []
    for (problem, arm), rs in sorted(groups.items()):
        scores = [r["score"] for r in rs if r["score"] is not None]
        out.append({"problem": problem, "arm": arm, "checkpoint_usd": rs[0]["checkpoint_usd"], "runs": len(rs),
                    "score": _mean(scores), "score_min": min(scores) if scores else None,
                    "score_max": max(scores) if scores else None, "gain": _mean(r["gain"] for r in rs),
                    "auc_gain": _mean(r["auc_gain"] for r in rs),
                    "at_record": sum(s >= MATCHES_RECORD for s in scores)})
    return out


# -- SVG ---------------------------------------------------------------------------------------
def svg_chart(problem, runs, arms, width=640, height=360, checkpoint=None):
    """Thin line per run up to its valid spend; bold mean over seeds up to the checkpoint (or the cap)."""
    pad_l, pad_r, pad_t, pad_b = 56, 28, 16, 44
    cap = max(r["cap_usd"] for r in runs) or 1.0
    ys = [c["incumbent_public"] for r in runs for c in valid_curve(r)] or [0, 1]
    lo, hi = min(ys), max(ys)
    if hi - lo < 1e-6:
        lo, hi = lo - 0.01, hi + 0.01
    span = hi - lo
    lo, hi = lo - 0.05 * span, hi + 0.05 * span
    pw, ph = width - pad_l - pad_r, height - pad_t - pad_b

    def X(usd):
        return pad_l + pw * min(max(usd / cap, 0), 1)

    def Y(v):
        return pad_t + ph * (1 - (v - lo) / (hi - lo))

    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
             f'aria-label="Best public score versus dollars spent, {html.escape(problem)}" '
             f'style="background:{SURFACE};font-family:system-ui,sans-serif;font-size:11px">']
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        parts.append(f'<line x1="{pad_l}" x2="{width - pad_r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" fill="{INK2}">{v:.3f}</text>')
    for i in range(5):
        usd = cap * i / 4
        parts.append(f'<text x="{X(usd):.1f}" y="{height - pad_b + 16}" text-anchor="middle" fill="{INK2}">${usd:.3g}</text>')
    parts.append(f'<text x="{pad_l + pw / 2:.1f}" y="{height - 8}" text-anchor="middle" fill="{INK2}">US dollars spent</text>')
    parts.append(f'<text x="12" y="{pad_t + ph / 2:.1f}" text-anchor="middle" fill="{INK2}" '
                 f'transform="rotate(-90 12 {pad_t + ph / 2:.1f})">best public score (1.0 = reference)</text>')
    if checkpoint:
        parts.append(f'<line x1="{X(checkpoint):.1f}" x2="{X(checkpoint):.1f}" y1="{pad_t}" y2="{pad_t + ph}" '
                     f'stroke="{INK2}" stroke-width="1"/><text x="{X(checkpoint) + 4:.1f}" y="{pad_t + 12}" '
                     f'fill="{INK2}">checkpoint ${checkpoint:.2f}</text>')
    mean_until = checkpoint or cap
    grid_x = [mean_until * i / 100 for i in range(101)]
    for k, arm in enumerate(arms):
        color = COLORS[k % len(COLORS)]
        mine = [r for r in runs if r["arm"] == arm and valid_curve(r)]
        for r in mine:   # thin per-run step lines, ending where the run stops being valid
            curve = valid_curve(r)
            pts, y_prev = [], curve[0]["incumbent_public"]
            for c in curve:
                pts += [(X(c["spent_usd"]), Y(y_prev)), (X(c["spent_usd"]), Y(c["incumbent_public"]))]
                y_prev = c["incumbent_public"]
            pts.append((X(max(r["valid_spend_usd"], curve[-1]["spent_usd"])), Y(y_prev)))
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            note = "complete" if r.get("completion") == "budget" else f"valid to ${r['valid_spend_usd']:.2f}"
            parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-opacity="0.35" stroke-width="1">'
                         f'<title>{html.escape(arm)} seed {r["seed"]} ({note}): {y_prev:.4f}</title></polyline>')
        if mine:
            means = [statistics.fmean(step_value(valid_curve(r), x, valid_curve(r)[0]["incumbent_public"]) for r in mine)
                     for x in grid_x]
            pts = []
            for i, (x, m) in enumerate(zip(grid_x, means)):
                if i and m != means[i - 1]:
                    pts.append((X(x), Y(means[i - 1])))
                pts.append((X(x), Y(m)))
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2" '
                         f'stroke-linejoin="round" stroke-linecap="round"><title>{html.escape(arm)} mean of '
                         f'{len(mine)} runs at ${mean_until:.2f}: {means[-1]:.4f}</title></polyline>')
    parts.append("</svg>")
    return "".join(parts)


def legend(arms):
    items = "".join(f'<span style="margin-right:16px;white-space:nowrap"><svg width="18" height="10">'
                    f'<line x1="0" x2="18" y1="5" y2="5" stroke="{COLORS[k % len(COLORS)]}" stroke-width="2"/></svg> '
                    f'{html.escape(a)}</span>' for k, a in enumerate(arms))
    return f'<div style="margin:8px 0;color:{INK}">{items}</div>'


def figure_svg(runs, arms, cps=None, width=640, height=300):
    """All problems as stacked panels in one standalone SVG, with a legend row on top."""
    problems = sorted({r["problem"] for r in runs})
    legend_h, title_h = 28, 22
    total_h = legend_h + len(problems) * (title_h + height)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_h}" width="{width}" height="{total_h}" '
             f'style="background:{SURFACE};font-family:system-ui,sans-serif;font-size:12px">'
             f'<rect width="{width}" height="{total_h}" fill="{SURFACE}"/>']
    x = 56
    for k, arm in enumerate(arms):
        parts.append(f'<line x1="{x}" x2="{x + 18}" y1="14" y2="14" stroke="{COLORS[k % len(COLORS)]}" stroke-width="2"/>'
                     f'<text x="{x + 24}" y="18" fill="{INK}">{html.escape(arm)}</text>')
        x += 30 + 7.5 * len(arm)
    y = legend_h
    for problem in problems:
        parts.append(f'<text x="56" y="{y + 16}" fill="{INK}" font-weight="600">{html.escape(problem)}: '
                     f'best public score (1.0 = reference) vs US dollars spent</text>')
        chart = svg_chart(problem, [r for r in runs if r["problem"] == problem], arms, width, height,
                          checkpoint=(cps or {}).get(problem))
        parts.append(chart.replace("<svg ", f'<svg x="0" y="{y + title_h}" ', 1))
        y += title_h + height
    parts.append("</svg>")
    return "".join(parts)


# -- outputs -----------------------------------------------------------------------------------
TABLE_COLS = [("problem", "problem"), ("arm", "arm"), ("runs", "runs"), ("final_public", "final public (mean)"),
              ("final_min", "min"), ("final_max", "max"), ("auc_gain", "AUC gain"), ("final_hidden", "final hidden"),
              ("spent_usd", "$ spent"), ("calls", "calls"), ("idea_calls", "idea calls (triage rounds)"),
              ("evals", "evals"), ("valid_evals", "valid evals"), ("improvements", "improvements"),
              ("usd_per_improvement", "$/improvement"), ("evals_with_timeout", "evals hitting a time limit"),
              ("wall_s", "wall s"), ("matches_record", "runs at record")]
COUNT_COLS = {"improvements", "calls", "idea_calls", "valid_evals", "evals", "wall_s", "evals_with_timeout"}


def _comparison_lines(comparisons, reference, title):
    lines = ["", title, "",
             "Sign-flip permutation p-values, Holm-adjusted within each metric across the arms compared.", "",
             "| metric | arm | n | mean difference | bootstrap 95% CI | P(arm > reference) | 95% CI | "
             "wins / ties / losses | p | p (Holm) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for metric, comp in comparisons.items():
        for arm, c in comp.items():
            ci = f"[{c['ci95'][0]:.4f}, {c['ci95'][1]:.4f}]" if c["ci95"] else "–"
            pci = f"[{c['p_greater_ci95'][0]:.2f}, {c['p_greater_ci95'][1]:.2f}]" if c["p_greater_ci95"] else "–"
            lines.append(f"| {metric} | {arm} | {c['n']} | {c['mean_diff']:.4f} | {ci} | {c['p_greater']:.2f} | {pci} | "
                         f"{c['wins']} / {c['ties']} / {c['losses']} | {_fmt(c['p_value'], 3)} | {_fmt(c['p_holm'], 3)} |")
    return lines


def _contrast_lines(contrasts, title):
    lines = ["", title, "", "| contrast | metric | n | mean difference | bootstrap 95% CI | P(first > second) | 95% CI | "
             "wins / ties / losses | p |", "|---|---|---|---|---|---|---|---|---|"]
    for name, by_metric in contrasts.items():
        for metric, c in by_metric.items():
            ci = f"[{c['ci95'][0]:.4f}, {c['ci95'][1]:.4f}]" if c["ci95"] else "–"
            pci = f"[{c['p_greater_ci95'][0]:.2f}, {c['p_greater_ci95'][1]:.2f}]" if c["p_greater_ci95"] else "–"
            lines.append(f"| {name} | {metric} | {c['n']} | {c['mean_diff']:.4f} | {ci} | {c['p_greater']:.2f} | {pci} | "
                         f"{c['wins']} / {c['ties']} / {c['losses']} | {_fmt(c['p_value'], 3)} |")
    return lines


def markdown(title, runs, analysis, reference):
    complete = [r for r in runs if r.get("completion") == "budget"]
    total = sum(r["spent_usd"] for r in runs if not r.get("mock"))
    lines = [f"# {title}", "",
             f"{len(runs)} runs, {len(complete)} budget-matched (used their cap before any API error). "
             f"Anthropic spend recorded (live runs): ${total:.2f}. Scores are normalized so 1.0 matches the reference "
             "value; higher is better. A final score of at least 1 - 1e-6 ties with the reference.", "",
             "## Full budget: budget-matched runs only", "",
             "AUC gain: area under the incumbent score over budget fraction [0, 1], minus the starting score, "
             "divided by the headroom (1 - starting score).", "",
             "| " + " | ".join(h for _, h in TABLE_COLS) + " |", "|" + "---|" * len(TABLE_COLS)]
    for row in analysis["groups"]:
        lines.append("| " + " | ".join(_fmt(row[k], 1 if k in COUNT_COLS else 4) for k, _ in TABLE_COLS) + " |")
    if analysis["comparisons"]:
        lines += _comparison_lines(analysis["comparisons"], reference,
                                   f"### Paired against `{reference}`, both runs complete")
    if analysis["contrasts"]:
        lines += _contrast_lines(analysis["contrasts"], "### Secondary contrasts, both runs complete")

    cps = analysis["checkpoints"]
    if cps:
        lines += ["", "## Common spend checkpoint (every run)", "",
                  "Per problem, the checkpoint is the smallest spend any run reached before an API error (or its "
                  "cap), rounded down to a multiple of $0.05: "
                  + ", ".join(f"{p} ${x:.2f}" for p, x in cps.items() if x) + ". Gain: (score at checkpoint - start) / "
                  "(1 - start). AUC gain: same for the mean incumbent score over spend [0, checkpoint].", "",
                  "| problem | arm | checkpoint $ | runs | score (mean) | min | max | gain | AUC gain | runs at record |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for g in analysis["checkpoint_groups"]:
            lines.append(f"| {g['problem']} | {g['arm']} | {g['checkpoint_usd']:.2f} | {g['runs']} | {_fmt(g['score'])} | "
                         f"{_fmt(g['score_min'])} | {_fmt(g['score_max'])} | {_fmt(g['gain'])} | {_fmt(g['auc_gain'])} | "
                         f"{g['at_record']} |")
        if analysis["checkpoint_comparisons"]:
            lines += _comparison_lines(analysis["checkpoint_comparisons"], reference,
                                       f"### Paired against `{reference}` at the checkpoint, all problems pooled")
        if analysis["checkpoint_contrasts"]:
            lines += _contrast_lines(analysis["checkpoint_contrasts"], "### Secondary contrasts at the checkpoint")

    flags = [dict(f, run=r["run_dir"]) for r in runs for f in r.get("record_flags") or []]
    if flags:
        lines += ["", "## Scores above the best known value", "",
                  "Re-checked by the strict checker in the gate. Only a margin above n x tolerance is worth a human "
                  "review; nothing here is a claim until reviewed.", "",
                  "| run | instance | score | reference | margin | n x tolerance | worth review |", "|---|---|---|---|---|---|---|"]
        for f in flags:
            lines.append(f"| {f['run']} | {f['label']} | {f['score']:.12g} | {f['reference']:.12g} | {f['margin']:.3g} | "
                         f"{f['n_x_tolerance']:.3g} | {f['worth_review']} |")
    by_arm = defaultdict(lambda: defaultdict(int))
    for r in runs:
        by_arm[r["arm"]][r.get("completion")] += 1
        by_arm[r["arm"]]["evals"] += r["evals"]
        by_arm[r["arm"]]["evals_with_timeout"] += r.get("evals_with_timeout") or 0
    kinds = sorted({r.get("completion") for r in runs})
    lines += ["", "## Completion and time limits by arm", "",
              "| arm | " + " | ".join(kinds) + " | evaluations | evaluations with an instance at its time limit |",
              "|---|" + "---|" * (len(kinds) + 2)]
    for arm in sorted(by_arm):
        c = by_arm[arm]
        lines.append(f"| {arm} | " + " | ".join(str(c[k]) for k in kinds) + f" | {c['evals']} | {c['evals_with_timeout']} |")
    lines += ["", "## Runs", "",
              "$ spent includes reservations charged for calls whose billing was unknown. Last public / hidden: the "
              "run's last incumbent, which for a truncated run is not a full-budget result. AUC gain over the full "
              "budget is shown for complete runs only.", "",
              "| run | completion | $ spent | valid to $ | cap | calls | failed calls | evals | start | last public | "
              "last hidden | AUC gain |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(runs, key=lambda r: (r["problem"], r["arm"], r["seed"])):
        auc = _fmt(r["auc_gain"]) if r.get("completion") == "budget" else "n/a"
        lines.append(f"| {r['run_dir']} | {r.get('completion')} | {r['spent_usd']:.4f} | {r['valid_spend_usd']:.4f} | "
                     f"{r['cap_usd']:.2f} | {r['calls']} | {r['failed_calls']} | {r['evals']} | {_fmt(r['initial_public'])} | "
                     f"{_fmt(r['final_public'])} | {_fmt(r['final_hidden'])} | {auc} |")
    return "\n".join(lines) + "\n"


def html_report(title, md_text, runs, arms, cps):
    charts = []
    for problem in sorted({r["problem"] for r in runs}):
        rs = [r for r in runs if r["problem"] == problem]
        charts.append(f"<h2>{html.escape(problem)}</h2>{legend(arms)}{svg_chart(problem, rs, arms, checkpoint=cps.get(problem))}")
    body = "".join(charts)
    table_html = _md_tables_to_html(md_text)
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>body{{font-family:system-ui,sans-serif;color:{INK};background:{SURFACE};max-width:1100px;"
            f"margin:24px auto;padding:0 16px}}table{{border-collapse:collapse;font-size:12px;margin:8px 0 24px}}"
            f"td,th{{border-bottom:1px solid {GRID};padding:3px 8px;text-align:right}}td:first-child,th:first-child,"
            f"td:nth-child(2),th:nth-child(2){{text-align:left}}p{{color:{INK2}}}</style></head><body>"
            f"<h1>{html.escape(title)}</h1><p>Thin lines: one run each, drawn only as far as the run is valid (to its "
            f"cap, or to its first API error). Bold line: mean over runs up to the common checkpoint. Hover a line for "
            f"its numbers; the tables below carry every value.</p>{body}{table_html}</body></html>")


def _md_tables_to_html(md_text):
    out, table = [], []
    for line in md_text.splitlines():
        if line.startswith("|"):
            table.append(line)
            continue
        if table:
            out.append(_table(table))
            table = []
        if line.startswith("### "):
            out.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            continue
        elif line.strip():
            out.append(f"<p>{html.escape(line)}</p>")
    if table:
        out.append(_table(table))
    return "".join(out)


def _table(lines):
    rows = [[c.strip() for c in l.strip("|").split("|")] for l in lines if not set(l) <= set("|-")]
    head, rest = rows[0], rows[1:]
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r) + "</tr>" for r in rest)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def analyse(runs, arms, reference):
    complete = [r for r in runs if r.get("completion") == "budget"]
    cps = checkpoints(runs)
    cp_rows = checkpoint_rows(runs, cps)
    analysis = {
        "groups": group_table(complete),
        "comparisons": ({m: paired(complete, reference, m) for m in ("auc_gain", "final_public", "final_hidden")}
                        if reference in arms else {}),
        "contrasts": secondary_contrasts(complete, arms),
        "checkpoints": cps,
        "checkpoint_runs": cp_rows,
        "checkpoint_groups": checkpoint_groups(cp_rows),
        "checkpoint_comparisons": ({m: paired(cp_rows, reference, m) for m in ("auc_gain", "gain")}
                                   if reference in arms else {}),
        "checkpoint_contrasts": secondary_contrasts(cp_rows, arms, metrics=("auc_gain", "gain")),
        "completion_counts": {c: sum(r.get("completion") == c for r in runs)
                              for c in sorted({r.get("completion") for r in runs})},
    }
    return analysis


def headline(analysis, runs, reference):
    """Machine-readable headline numbers for cross-experiment summaries."""
    live = [r for r in runs if not r.get("mock")]
    keep = ("problem", "arm", "runs", "seeds", "final_public", "final_min", "final_max", "auc_gain", "final_hidden",
            "spent_usd", "calls", "idea_calls", "evals", "improvements", "matches_record", "wall_s",
            "evals_with_timeout")
    return {
        "runs": len(runs), "reference_arm": reference, "completion_counts": analysis["completion_counts"],
        "anthropic_usd_recorded": round(sum(r["spent_usd"] for r in live), 4),
        "tokens": sum(r["tokens"] for r in live),
        "evaluations": sum(r["evals"] for r in runs),
        "all_within_cap": all(r["within_cap"] for r in runs),
        "full_budget_complete_runs": [{k: row[k] for k in keep} for row in analysis["groups"]],
        "full_budget_vs_reference": analysis["comparisons"],
        "checkpoints_usd": analysis["checkpoints"],
        "checkpoint_by_problem_and_arm": analysis["checkpoint_groups"],
        "checkpoint_vs_reference": analysis["checkpoint_comparisons"],
        "checkpoint_secondary_contrasts": analysis["checkpoint_contrasts"],
        "record_flags": [dict(f, run=r["run_dir"]) for r in runs for f in r.get("record_flags") or []],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+", help="grid folders with one subfolder per run (later ones override)")
    ap.add_argument("--out", help="where to write the report (default: the first folder)")
    ap.add_argument("--reference", default="shinka", help="arm the others are compared with")
    ap.add_argument("--recompute", action="store_true", help="rebuild summaries from the raw logs")
    ap.add_argument("--figure", help="also write the curves as one standalone SVG here")
    ap.add_argument("--headline", help="also write headline numbers as JSON here")
    a = ap.parse_args(argv)
    runs = load_runs(a.folders, a.recompute)
    if not runs:
        raise SystemExit(f"no runs under {a.folders}")
    out = Path(a.out or a.folders[0])
    out.mkdir(parents=True, exist_ok=True)
    arms = sorted({r["arm"] for r in runs}, key=lambda x: (x != a.reference, x))
    analysis = analyse(runs, arms, a.reference)
    title = f"Tournament report: {' + '.join(Path(f).name for f in a.folders)}"
    md_text = markdown(title, runs, analysis, a.reference)
    (out / "report.md").write_text(md_text)
    (out / "report.html").write_text(html_report(title, md_text, runs, arms, analysis["checkpoints"]))
    with open(out / "all_curves.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "arm", "problem", "seed", "cap_usd", "completion", "valid_spend_usd", "valid"] + CURVE_FIELDS)
        for r in runs:
            valid_ts = {c.get("t") for c in valid_curve(r)}
            for c in r["curve"]:
                w.writerow([r["run_dir"], r["arm"], r["problem"], r["seed"], r["cap_usd"], r.get("completion"),
                            r.get("valid_spend_usd"), c.get("t") in valid_ts] + [c.get(k) for k in CURVE_FIELDS])
    (out / "results.json").write_text(json.dumps({**analysis, "runs": [{k: v for k, v in r.items() if k != "curve"}
                                                                       for r in runs]}, indent=2, default=str))
    if a.figure:
        Path(a.figure).write_text(figure_svg(runs, arms, analysis["checkpoints"]))
    if a.headline:
        Path(a.headline).write_text(json.dumps(headline(analysis, runs, a.reference), indent=2, default=str))
    print(md_text)
    print(f"wrote {out / 'report.md'} and {out / 'report.html'}")


if __name__ == "__main__":
    main()
