"""Tournament report: tables, paired comparisons and best-score-versus-dollars curves.

    python -m tournament.report experiments/tournament-v1/runs/mock-v1 [--reference shinka]

Reads every <run>/summary.json under the folder (recomputing it from the raw logs when
--recompute is given) and writes report.md, report.html (inline SVG, no scripts),
all_curves.csv and results.json into the folder.
"""
import argparse
import csv
import html
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from .metrics import CURVE_FIELDS, summarize

# Categorical slots 1-4 of the validated reference palette (dataviz skill, light surface #fcfcfb).
# Two of them sit below 3:1 contrast, so every chart has a legend and a table view.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def load_runs(folder: Path, recompute=False):
    runs = []
    for d in sorted(p for p in folder.iterdir() if p.is_dir()):
        if recompute and (d / "job.json").exists():
            s = summarize(d)
        elif (d / "summary.json").exists():
            s = json.loads((d / "summary.json").read_text())
        else:
            continue
        s["run_dir"] = d.name
        runs.append(s)
    return runs


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


def bootstrap_ci(diffs, reps=10_000, seed=0):
    if len(diffs) < 2:
        return None
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(diffs, k=len(diffs))) for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


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
            out[arm] = {"n": len(diffs), "mean_diff": statistics.fmean(diffs), "ci95": ci,
                        "wins": sum(d > 1e-9 for d in diffs), "ties": sum(abs(d) <= 1e-9 for d in diffs),
                        "losses": sum(d < -1e-9 for d in diffs)}
    return out


def group_table(runs):
    groups = defaultdict(list)
    for r in runs:
        groups[(r["problem"], r["arm"])].append(r)
    rows = []
    for (problem, arm), rs in sorted(groups.items()):
        finals = [r["final_public"] for r in rs if r["final_public"] is not None]
        rows.append({
            "problem": problem, "arm": arm, "runs": len(rs),
            "final_public": _mean(finals), "final_min": min(finals) if finals else None,
            "final_max": max(finals) if finals else None,
            "auc_gain": _mean(r["auc_gain"] for r in rs), "final_hidden": _mean(r["final_hidden"] for r in rs),
            "spent_usd": _mean(r["spent_usd"] for r in rs), "cap_usd": _mean(r["cap_usd"] for r in rs),
            "improvements": _mean(r["improvements"] for r in rs),
            "usd_per_improvement": _mean(r["usd_per_improvement"] for r in rs),
            "tokens_per_improvement": _mean(r["tokens_per_improvement"] for r in rs),
            "calls": _mean(r["calls"] for r in rs), "evals": _mean(r["evals"] for r in rs),
            "valid_evals": _mean(r["valid_evals"] for r in rs), "wall_s": _mean(r["wall_s"] for r in rs),
            "all_within_cap": all(r["within_cap"] for r in rs),
        })
    return rows


# -- SVG ---------------------------------------------------------------------------------------
def svg_chart(problem, runs, arms, width=640, height=360):
    pad_l, pad_r, pad_t, pad_b = 56, 16, 16, 44
    cap = max(r["cap_usd"] for r in runs) or 1.0
    ys = [c["incumbent_public"] for r in runs for c in r["curve"]] or [0, 1]
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
        parts.append(f'<text x="{X(usd):.1f}" y="{height - pad_b + 16}" text-anchor="middle" fill="{INK2}">${usd:.2f}</text>')
    parts.append(f'<text x="{pad_l + pw / 2:.1f}" y="{height - 8}" text-anchor="middle" fill="{INK2}">dollars spent</text>')
    parts.append(f'<text x="12" y="{pad_t + ph / 2:.1f}" text-anchor="middle" fill="{INK2}" '
                 f'transform="rotate(-90 12 {pad_t + ph / 2:.1f})">best public score</text>')

    grid_x = [cap * i / 100 for i in range(101)]
    for k, arm in enumerate(arms):
        color = COLORS[k % len(COLORS)]
        mine = [r for r in runs if r["arm"] == arm and r["curve"]]
        for r in mine:   # thin per-seed step lines
            pts, y_prev = [], r["curve"][0]["incumbent_public"]
            for c in r["curve"]:
                pts += [(X(c["spent_usd"]), Y(y_prev)), (X(c["spent_usd"]), Y(c["incumbent_public"]))]
                y_prev = c["incumbent_public"]
            pts.append((X(max(r["spent_usd"], r["curve"][-1]["spent_usd"])), Y(y_prev)))
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-opacity="0.35" stroke-width="1">'
                         f'<title>{html.escape(arm)} seed {r["seed"]}: final {r["final_public"]:.4f}, '
                         f'${r["spent_usd"]:.2f} spent</title></polyline>')
        if mine:         # bold mean over seeds (each run holds its last value to the cap)
            means = [statistics.fmean(step_value(r["curve"], x, r["curve"][0]["incumbent_public"]) for r in mine)
                     for x in grid_x]
            pts = []
            for i, (x, m) in enumerate(zip(grid_x, means)):
                if i and m != means[i - 1]:
                    pts.append((X(x), Y(means[i - 1])))
                pts.append((X(x), Y(m)))
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2" '
                         f'stroke-linejoin="round" stroke-linecap="round"><title>{html.escape(arm)} mean of '
                         f'{len(mine)} seeds: final {means[-1]:.4f}</title></polyline>')
    parts.append("</svg>")
    return "".join(parts)


def legend(arms):
    items = "".join(f'<span style="margin-right:16px;white-space:nowrap"><svg width="18" height="10">'
                    f'<line x1="0" x2="18" y1="5" y2="5" stroke="{COLORS[k % len(COLORS)]}" stroke-width="2"/></svg> '
                    f'{html.escape(a)}</span>' for k, a in enumerate(arms))
    return f'<div style="margin:8px 0;color:{INK}">{items}</div>'


# -- outputs -----------------------------------------------------------------------------------
TABLE_COLS = [("problem", "problem"), ("arm", "arm"), ("runs", "runs"), ("final_public", "final public (mean)"),
              ("final_min", "min"), ("final_max", "max"), ("auc_gain", "AUC gain"), ("final_hidden", "final hidden"),
              ("spent_usd", "$ spent"), ("improvements", "improvements"), ("usd_per_improvement", "$/improvement"),
              ("tokens_per_improvement", "tokens/improvement"), ("calls", "calls"), ("valid_evals", "valid evals"),
              ("evals", "evals"), ("wall_s", "wall s"), ("all_within_cap", "within cap")]


def markdown(title, runs, rows, comparisons, reference):
    total = sum(r["spent_usd"] for r in runs if not r.get("mock"))
    lines = [f"# {title}", "", f"{len(runs)} runs. Anthropic spend (live runs only): ${total:.2f}. "
             "Scores are normalized so 1.0 matches the best known result. AUC gain is the area under the "
             "best-score-versus-budget-fraction curve, minus the starting score, divided by the headroom "
             "(1 - starting score).", "",
             "| " + " | ".join(h for _, h in TABLE_COLS) + " |", "|" + "---|" * len(TABLE_COLS)]
    counts = {"improvements", "calls", "valid_evals", "evals", "wall_s", "tokens_per_improvement"}
    for row in rows:
        lines.append("| " + " | ".join(_fmt(row[k], 1 if k in counts else 4) for k, _ in TABLE_COLS) + " |")
    if comparisons:
        lines += ["", f"## Paired differences against `{reference}` (matched problem and seed)", "",
                  "| metric | arm | n | mean difference | bootstrap 95% CI | wins / ties / losses |", "|---|---|---|---|---|---|"]
        for metric, comp in comparisons.items():
            for arm, c in comp.items():
                ci = f"[{c['ci95'][0]:.4f}, {c['ci95'][1]:.4f}]" if c["ci95"] else "–"
                lines.append(f"| {metric} | {arm} | {c['n']} | {c['mean_diff']:.4f} | {ci} | "
                             f"{c['wins']} / {c['ties']} / {c['losses']} |")
    lines += ["", "## Runs", "", "| run | status | $ spent | cap | calls | evals | start | final public | final hidden | AUC gain |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(runs, key=lambda r: (r["problem"], r["arm"], r["seed"])):
        lines.append(f"| {r['run_dir']} | {r.get('status')} | {r['spent_usd']:.4f} | {r['cap_usd']:.2f} | {r['calls']} | "
                     f"{r['evals']} | {_fmt(r['initial_public'])} | {_fmt(r['final_public'])} | {_fmt(r['final_hidden'])} | "
                     f"{_fmt(r['auc_gain'])} |")
    return "\n".join(lines) + "\n"


def html_report(title, md_text, runs, arms):
    charts = []
    for problem in sorted({r["problem"] for r in runs}):
        rs = [r for r in runs if r["problem"] == problem]
        charts.append(f"<h2>{html.escape(problem)}</h2>{legend(arms)}{svg_chart(problem, rs, arms)}")
    body = "".join(charts)
    table_html = _md_tables_to_html(md_text)
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>body{{font-family:system-ui,sans-serif;color:{INK};background:{SURFACE};max-width:1100px;"
            f"margin:24px auto;padding:0 16px}}table{{border-collapse:collapse;font-size:12px;margin:8px 0 24px}}"
            f"td,th{{border-bottom:1px solid {GRID};padding:3px 8px;text-align:right}}td:first-child,th:first-child,"
            f"td:nth-child(2),th:nth-child(2){{text-align:left}}p{{color:{INK2}}}</style></head><body>"
            f"<h1>{html.escape(title)}</h1><p>Thin lines: one run each. Bold line: mean over seeds, each run holding "
            f"its final value up to the cap. Hover a line for its numbers; the tables below carry every value.</p>"
            f"{body}{table_html}</body></html>")


def _md_tables_to_html(md_text):
    out, table = [], []
    for line in md_text.splitlines():
        if line.startswith("|"):
            table.append(line)
            continue
        if table:
            out.append(_table(table))
            table = []
        if line.startswith("## "):
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--reference", default="shinka", help="arm the others are compared with")
    ap.add_argument("--recompute", action="store_true", help="rebuild summaries from the raw logs")
    a = ap.parse_args(argv)
    folder = Path(a.folder)
    runs = load_runs(folder, a.recompute)
    if not runs:
        raise SystemExit(f"no runs with summary.json under {folder}")
    arms = sorted({r["arm"] for r in runs}, key=lambda x: (x != a.reference, x))
    rows = group_table(runs)
    comparisons = {}
    if a.reference in arms:
        comparisons = {m: paired(runs, a.reference, m) for m in ("auc_gain", "final_public", "final_hidden")}
    title = f"Tournament report: {folder.name}"
    md_text = markdown(title, runs, rows, comparisons, a.reference)
    (folder / "report.md").write_text(md_text)
    (folder / "report.html").write_text(html_report(title, md_text, runs, arms))
    with open(folder / "all_curves.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "arm", "problem", "seed", "cap_usd"] + CURVE_FIELDS)
        for r in runs:
            for c in r["curve"]:
                w.writerow([r["run_dir"], r["arm"], r["problem"], r["seed"], r["cap_usd"]] + [c.get(k) for k in CURVE_FIELDS])
    (folder / "results.json").write_text(json.dumps({"groups": rows, "comparisons": comparisons,
                                                     "runs": [{k: v for k, v in r.items() if k != "curve"} for r in runs]},
                                                    indent=2, default=str))
    print(md_text)
    print(f"wrote {folder / 'report.md'} and {folder / 'report.html'}")


if __name__ == "__main__":
    main()
