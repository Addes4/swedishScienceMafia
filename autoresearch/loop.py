"""One command for the whole research loop: search, audit, baselines, explanation, report.

    python -m autoresearch.loop problems/bin_packing_online --budget 0.10 --provider hf
    python -m autoresearch.loop problems/erdos_squares --mock          # no network, no cost
    python -m autoresearch.loop --report runs/<dir>                    # rebuild the report of a saved run

Every default is the setting that won one of this project's controlled experiments; the
settings the experiments did not support are still available as flags.

  search    lean loop: one LLM call per step proposes and implements a change to the incumbent
            (tournament/lean.py; tournament-v1: lean and independent beat ShinkaEvolve and triage
            on early AUC, partial, 17 of 60 runs)
  score     autoresearch/gate.py: separate process, static scan, strict re-check, hidden
            instances (gate-redteam: 0 of 68 exploit attempts gained a material unearned score)
  keep      better public score and no regression on archived instances (the gate; memory-ablation:
            the archive works as a gate, while prompt memory made the model timid). --no-gate turns it off
  audit     hidden-instance score of the initial and final incumbent, never used for selection;
            OVERFIT? if the public score rose while the hidden score fell
  explain   two-sided ablation of the final program (autoresearch/explain_code.py)
  compare   problems/<name>/baselines/*.py scored by the same gate on the same instances

Off by default: --patience T (the Strategist restart rule; no controlled win yet), --independent
(no history and no parent; tied with lean, so lean is kept for its edit trail).

Writes to --out (default runs/<problem>-<timestamp>): everything tournament/run.py writes (job.json,
usage.jsonl, events.jsonl, evals.jsonl, summary.json, curve.csv, best_program.py, artifacts.tar.gz)
plus loop.json, baselines.json, baselines/, explain.json and report.md. If a run was stopped from
outside (budget or wall-clock hard stop, Ctrl-C), --report DIR finishes the analysis (no LLM calls).
"""
import argparse
import difflib
import json
import os
import shlex
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HF_MODEL = "deepseek-ai/DeepSeek-V4.1-Flash:deepinfra"     # tournament-v2's pinned model and provider
ANTHROPIC_MODEL = "claude-sonnet-5-5"
MOCK_BUDGET = 0.10                                          # simulated dollars; the mock prices calls like the real API


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="python -m autoresearch.loop", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("problem", nargs="?", help="problem folder (or its name under problems/)")
    ap.add_argument("--report", metavar="DIR", help="rebuild the report of a saved run (no LLM calls)")
    ap.add_argument("--budget", type=float, help="hard dollar cap on LLM spend (required unless --mock)")
    ap.add_argument("--provider", choices=["hf", "anthropic"], default="hf")
    ap.add_argument("--model", help=f"default {HF_MODEL} (hf) or {ANTHROPIC_MODEL} (anthropic)")
    ap.add_argument("--max-iters", type=int, default=12, help="LLM steps (default 12)")
    ap.add_argument("--wall", type=float, default=3600, help="wall-clock limit of the search in seconds")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", help="run folder (default runs/<problem>-<timestamp>); never overwritten")
    ap.add_argument("--no-gate", action="store_true", help="keep any public improvement (no non-regression archive)")
    ap.add_argument("--patience", type=int, metavar="T", help="restart from scratch after T non-improving steps")
    ap.add_argument("--independent", action="store_true", help="independent sampling: no history, no parent, no gate")
    ap.add_argument("--gate-workers", type=int, default=os.cpu_count() or 1, help="instances scored in parallel")
    ap.add_argument("--explain-evals", type=int, default=40, help="evaluations for the ablation (0 skips it)")
    ap.add_argument("--mock", action="store_true", help="local mock API: no network, no cost")
    a = ap.parse_args(argv)
    if bool(a.problem) == bool(a.report):
        ap.error("give a problem folder, or --report DIR")
    if a.problem and not a.mock and a.budget is None:
        ap.error("--budget is required for a live run (a hard dollar cap); use --mock for a free run")
    if a.budget is not None and a.budget <= 0:
        ap.error("--budget must be positive")
    if a.independent and a.patience:
        ap.error("--independent has no working line to restart, so it takes no --patience")
    a.model = a.model or (HF_MODEL if a.provider == "hf" else ANTHROPIC_MODEL)
    if a.provider == "hf" and ":" not in a.model:
        ap.error("--model on the HF router must be pinned to a provider, e.g. " + HF_MODEL)
    return a


# -- stages -----------------------------------------------------------------------------------------
def show(e: dict):
    """One terminal line per search step, printed as the arm logs it."""
    if e.get("event") == "incumbent" and e.get("tag") == "initial":
        print(f"  initial          score {e['score']:.4f}", flush=True)
    elif e.get("event") == "step":
        score = "  n/a " if e.get("score") is None else f"{e['score']:.4f}"
        text = e.get("summary") or e.get("detail") or ""
        print(f"  step {e['iter']:>2} {e['op']:<7} {e['outcome']:<13} score {score}  best {e.get('best') or 0:.4f}"
              f"  ${e.get('cost') or 0:.4f}  {text[:60]}", flush=True)


def search(a, problem_dir: Path, out: Path):
    from tournament import run as trun
    from tournament.context import Context
    from tournament.evallog import EVAL_LOG_ENV, PROBLEM_ENV
    arm = "independent" if a.independent else "lean"
    cfg = {"type": arm, "gate": not (a.no_gate or a.independent), "max_iters": a.max_iters, "model": a.model,
           "patience": a.patience}
    job = {"job_id": f"loop__{problem_dir.name}__s{a.seed}", "grid": "loop", "arm": arm, "arm_config": cfg,
           "problem": str(problem_dir), "seed": a.seed, "budget_usd": a.budget, "wall_limit_s": a.wall,
           "mock": a.mock, "provider": a.provider, "gate_workers": a.gate_workers}
    if a.provider == "hf":
        job["hf_models"] = [a.model]
    log = Context.event

    def event(self, **rec):   # the arm's own event log, echoed to the terminal as it is written
        log(self, **rec)
        show(rec)
    Context.event = event
    cwd = os.getcwd()
    try:
        trun.main(["--job", json.dumps(job), "--out", str(out)])
    finally:   # tournament.run changes directory and sets the private eval log for its arms
        Context.event = log
        os.chdir(cwd)
        for key in (EVAL_LOG_ENV, PROBLEM_ENV):
            os.environ.pop(key, None)


def score_baselines(problem_dir: Path, out: Path) -> list:
    """Every problems/<name>/baselines/*.py through the same gate; [] if the folder does not exist."""
    from autoresearch.gate import evaluate
    rows = []
    for prog in sorted((problem_dir / "baselines").glob("*.py")):
        d = out / "baselines" / prog.stem
        metrics = evaluate(problem_dir, str(prog), str(d))
        correct = json.loads((d / "correct.json").read_text())
        note = next((l.lstrip("# ").strip() for l in prog.read_text().splitlines() if l.startswith("#")), "")
        rows.append({"name": prog.stem, "file": str(prog.relative_to(REPO) if prog.is_relative_to(REPO) else prog),
                     "public": metrics["combined_score"], "hidden": metrics["private"].get("hidden_mean"),
                     "valid": correct["correct"], "error": correct["error"], "note": note})
        print(f"  baseline {prog.stem:<22} public {_f(rows[-1]['public'])}  hidden {_f(rows[-1]['hidden'])}", flush=True)
    return rows


def analyse(out: Path, problem_dir: Path, explain_evals: int, timings: dict):
    """Baselines and the explanation, each computed once and saved (a rebuilt report reuses them)."""
    from autoresearch.explain_code import explain_program
    if not (out / "baselines.json").exists():
        t0 = time.time()
        (out / "baselines.json").write_text(json.dumps(score_baselines(problem_dir, out), indent=2))
        timings["baselines_s"] = round(time.time() - t0, 1)
    if not (out / "explain.json").exists() and (out / "best_program.py").exists():
        t0 = time.time()
        if explain_evals > 0:
            print(f"  explaining best_program.py (up to {explain_evals} evaluations)", flush=True)
            r = explain_program(problem_dir, out / "best_program.py", tol=0.002, max_evals=explain_evals)
        else:
            r = {"skipped": "--explain-evals 0"}
        (out / "explain.json").write_text(json.dumps(r, indent=2))
        timings["explain_s"] = round(time.time() - t0, 1)


def audit(s: dict) -> dict:
    ip, fp, ih, fh = s["initial_public"], s["final_public"], s["initial_hidden"], s["final_hidden"]
    overfit = None not in (ip, fp, ih, fh) and fh < ih - 1e-9 and fp > ip + 1e-9
    return {"public_gain": None if None in (ip, fp) else fp - ip, "hidden_gain": None if None in (ih, fh) else fh - ih,
            "gap": None if None in (fp, fh) else fp - fh, "overfit": overfit}


# -- report -----------------------------------------------------------------------------------------
def _f(x, d=4):
    return "n/a" if x is None else f"{x:.{d}f}"


def _cell(text, n=100):
    text = " ".join(str(text or "").split()).replace("|", "\\|")
    return text if len(text) <= n else text[:n - 3] + "..."


def command_line(cfg: dict, problem_dir: Path) -> str:
    p = problem_dir.relative_to(REPO) if problem_dir.is_relative_to(REPO) else problem_dir
    args = [str(p)] + (["--mock"] if cfg["mock"] else ["--budget", f"{cfg['budget']:g}"])
    args += ["--provider", cfg["provider"], "--model", cfg["model"], "--max-iters", str(cfg["max_iters"]),
             "--seed", str(cfg["seed"])]
    args += ["--no-gate"] * cfg["no_gate"] + ["--independent"] * cfg["independent"]
    args += ["--patience", str(cfg["patience"])] if cfg["patience"] else []
    return "python -m autoresearch.loop " + shlex.join(args)


def write_report(out: Path) -> dict:
    from tournament.metrics import load_jsonl, summarize, write_curve
    job = json.loads((out / "job.json").read_text())
    loop = json.loads((out / "loop.json").read_text()) if (out / "loop.json").exists() else {}
    s = summarize(out)
    (out / "summary.json").write_text(json.dumps(s, indent=2, default=str))
    write_curve(s, out / "curve.csv")
    problem_dir = Path(job["problem_dir"])
    cfg = job["arm_config"]
    base = json.loads((out / "baselines.json").read_text()) if (out / "baselines.json").exists() else []
    expl = json.loads((out / "explain.json").read_text()) if (out / "explain.json").exists() else None
    au = audit(s)
    steps = [e for e in load_jsonl(out / "events.jsonl") if e.get("event") == "step"]
    mock = bool(job.get("mock"))
    spend = (f"$0 real (mock API; ${s['spent_usd']:.4f} simulated at listed prices)" if mock
             else f"${s['spent_usd']:.4f} of a ${s['cap_usd']:.2f} hard cap")
    keep = "independent samples, best kept" if cfg["type"] == "independent" else \
        "better public score" + (" and no regression on archived instances (gate)" if cfg.get("gate") else " (no gate)")
    model = cfg.get("model")
    L = [f"# Research loop report: {problem_dir.name}", "",
         "| | |", "|---|---|",
         f"| problem | `{problem_dir.name}` |",
         f"| search | {cfg['type']}, {cfg.get('max_iters')} steps max" + (f", restart after {cfg['patience']} stalls" if cfg.get("patience") else "") + " |",
         f"| keep rule | {keep} |",
         f"| model | `{model}` via {job.get('provider', 'anthropic')}{' (mock API)' if mock else ''} |",
         f"| spend | {spend}, {s['calls']} calls, {s['tokens']:,} tokens |",
         f"| wall time | search {s['wall_s']:.0f} s" + "".join(f", {k[:-2]} {v:.0f} s" for k, v in (loop.get("timings") or {}).items() if k != "search_s") + " |",
         f"| stopped | {s.get('arm_result') or s.get('status')} ({s['completion']}) |",
         f"| evaluations | {s['evals']} ({s['valid_evals']} valid), {s['improvements']} improvements accepted |", "",
         "## Scores", "",
         "Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model "
         "and never used for any decision; they are the fresh audit.", "",
         "| program | public | hidden | note |", "|---|---|---|---|",
         f"| `initial.py` (starting program) | {_f(s['initial_public'])} | {_f(s['initial_hidden'])} | |",
         f"| `best_program.py` (final incumbent) | {_f(s['final_public'])} | {_f(s['final_hidden'])} | "
         f"{'**OVERFIT?** public rose, hidden fell' if au['overfit'] else ''} |"]
    L += [f"| baseline `{b['name']}` | {_f(b['public'])} | {_f(b['hidden'])} | {_cell(b['note'], 70) if b['valid'] else 'invalid: ' + _cell(b['error'], 60)} |"
          for b in base]
    if expl and not expl.get("skipped"):
        m = expl["minimal"]
        L.append(f"| minimal program (ablation) | {_f(m['public'])} | {_f(m['hidden'])} | {len(m['removed'])} parts removed |")
    L += ["", f"Audit: public {_f(s['initial_public'])} → {_f(s['final_public'])} "
              f"({'+' if (au['public_gain'] or 0) >= 0 else ''}{_f(au['public_gain'])}), hidden {_f(s['initial_hidden'])} → "
              f"{_f(s['final_hidden'])} ({'+' if (au['hidden_gain'] or 0) >= 0 else ''}{_f(au['hidden_gain'])}); "
              f"public − hidden gap of the final program {_f(au['gap'])}."
              + (" **OVERFIT?** The public score rose while the hidden score fell: treat the gain as unconfirmed." if au["overfit"] else ""),
          ""]
    if base:
        best_b = max((b for b in base if b["valid"]), key=lambda b: b["public"], default=None)
        if best_b and s["final_public"] is not None:
            rel = "above" if s["final_public"] > best_b["public"] + 1e-9 else "below" if s["final_public"] < best_b["public"] - 1e-9 else "equal to"
            L += [f"Against the baselines: the final program's public score is {rel} the best baseline "
                  f"(`{best_b['name']}`, {_f(best_b['public'])}). Any gain should be stated against these numbers.", ""]
    if s["record_flags"]:
        L += [f"Record flags (scores above the best known value, for human review): {len(s['record_flags'])}; see summary.json.", ""]
    L += ["## Steps", "", "| step | op | outcome | score | best | cost | change (model's own description) |",
          "|---|---|---|---|---|---|---|"]
    L += [f"| {e['iter']} | {e['op']} | {e['outcome']} | {_f(e.get('score'))} | {_f(e.get('best'))} | "
          f"${e.get('cost') or 0:.4f} | {_cell(e.get('summary') or e.get('detail'))} |" for e in steps]
    if not steps:
        L.append("| | | no steps recorded | | | | |")
    L += ["", "## Change: `initial.py` → `best_program.py`", ""]
    initial = (problem_dir / "initial.py").read_text() if (problem_dir / "initial.py").exists() else ""
    best = (out / "best_program.py").read_text() if (out / "best_program.py").exists() else ""
    diff = list(difflib.unified_diff(initial.splitlines(), best.splitlines(), "initial.py", "best_program.py", lineterm=""))
    L += ["```diff", *diff, "```", ""] if diff else ["The run kept the starting program: no candidate was accepted.", ""]
    L += ["## Explanation", ""]
    if expl:
        from autoresearch.explain_code import to_markdown
        L += [to_markdown(expl)]
    else:
        L += ["Not computed yet: run the `--report` command below.", ""]
    hashes = job.get("source_hashes") or {}
    key = [k for k in hashes if k.startswith(("tournament/lean.py", "autoresearch/gate.py", "autoresearch/sandbox.py"))
           or Path(k).parent.name == problem_dir.name]
    L += ["## Reproduce", "", "```bash", command_line(loop["config"], problem_dir) if loop.get("config") else "(see job.json)",
          f"python -m autoresearch.loop --report {out.relative_to(REPO) if out.is_relative_to(REPO) else out}   # rebuild this report",
          "```", "",
          "Live runs are not deterministic (the model samples); mock runs are." if not mock else "Mock runs repeat exactly for a given seed.", "",
          f"Git commit `{job.get('git_commit')}`, Python {job.get('python')}. SHA-256 of the files that define this run "
          f"(all {len(hashes)} in `job.json`):", ""]
    L += [f"- `{Path(k).name if Path(k).is_absolute() else k}` `{hashes[k][:16]}`" for k in key]
    L += ["", "Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` "
              "(every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` "
              "(every candidate program).", ""]
    (out / "report.md").write_text("\n".join(L))
    return {"summary": s, "audit": au, "baselines": base, "explain": expl, "job": job}


def terminal_summary(out: Path, r: dict) -> str:
    s, au, job, expl = r["summary"], r["audit"], r["job"], r["explain"]
    cfg = job["arm_config"]
    spent = f"$0 real (mock), ${s['spent_usd']:.4f} simulated" if job.get("mock") else f"${s['spent_usd']:.4f} of ${s['cap_usd']:.2f} cap"
    lines = [f"== {Path(job['problem_dir']).name}: {cfg['type']}{' + gate' if cfg.get('gate') else ''}, {cfg.get('model')} ({job.get('provider')})",
             f"spend     {spent}, {s['calls']} calls, {s['evals']} evals, search {s['wall_s']:.0f} s",
             f"public    {_f(s['initial_public'])} -> {_f(s['final_public'])}   (initial -> final incumbent; selected on)",
             f"hidden    {_f(s['initial_hidden'])} -> {_f(s['final_hidden'])}   (fresh audit, never selected on)"
             + ("   OVERFIT?" if au["overfit"] else "")]
    if r["baselines"]:
        lines.append("baselines " + ", ".join(f"{b['name']} {_f(b['public'])}/{_f(b['hidden'])}" for b in r["baselines"]))
    if expl and not expl.get("skipped"):
        verdicts = [p["verdict"] for p in expl["parts"]]
        lines.append(f"explain   {len(verdicts)} parts: {sum(v.startswith('can go') for v in verdicts)} can go, "
                     f"{len(expl['repaired'])} REPAIRED; minimal program public {_f(expl['minimal']['public'])}, "
                     f"hidden {_f(expl['minimal']['hidden'])}")
    elif expl:
        lines.append(f"explain   skipped: {expl['skipped']}")
    lines.append(f"report    {out / 'report.md'}")
    return "\n".join(lines)


# -- entry point ------------------------------------------------------------------------------------
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    a = parse_args(argv)
    sys.path.insert(0, str(REPO))
    os.environ["GATE_WORKERS"] = str(max(1, a.gate_workers))
    if a.report:
        out = Path(a.report).resolve()
        if not (out / "job.json").exists():
            raise SystemExit(f"{out} is not a run folder (no job.json)")
        loop = json.loads((out / "loop.json").read_text()) if (out / "loop.json").exists() else {}
        timings = loop.get("timings", {})
        analyse(out, Path(json.loads((out / "job.json").read_text())["problem_dir"]), a.explain_evals, timings)
        if loop:
            (out / "loop.json").write_text(json.dumps(dict(loop, timings=timings), indent=2))
        print(terminal_summary(out, write_report(out)))
        return 0

    from tournament.run import resolve_problem
    problem_dir = resolve_problem(a.problem)
    if a.mock and a.budget is None:
        a.budget = MOCK_BUDGET
    out = Path(a.out or Path("runs") / f"{problem_dir.name}-{time.strftime('%Y%m%d-%H%M%S')}").resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} already exists and is not empty; choose another --out (runs are never overwritten)")
    config = {"budget": a.budget, "provider": a.provider, "model": a.model, "max_iters": a.max_iters, "wall": a.wall,
              "seed": a.seed, "no_gate": a.no_gate, "patience": a.patience, "independent": a.independent,
              "gate_workers": a.gate_workers, "explain_evals": a.explain_evals, "mock": a.mock}
    print(f"[loop] {problem_dir.name} -> {out}", flush=True)
    t0 = time.time()
    search(a, problem_dir, out)
    timings = {"search_s": round(time.time() - t0, 1)}
    (out / "loop.json").write_text(json.dumps({"argv": argv, "config": config, "timings": timings}, indent=2))
    status = json.loads((out / "summary.json").read_text()).get("status") or ""
    if "KeyboardInterrupt" in status:
        print(f"[loop] interrupted; finish the analysis with: python -m autoresearch.loop --report {out}")
    else:
        analyse(out, problem_dir, a.explain_evals, timings)
        (out / "loop.json").write_text(json.dumps({"argv": argv, "config": config, "timings": timings}, indent=2))
    print(terminal_summary(out, write_report(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
