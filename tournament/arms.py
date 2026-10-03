"""Arm registry. An arm is a function run(ctx) that searches until its budget or time runs out.

Grid files name arms and give each a config whose "type" selects one of the functions below,
so a new variant of an existing framework is a config entry, and a new framework is one
function decorated with @arm("name").

Every arm is measured the same way regardless of its own bookkeeping: all Anthropic calls go
through the budget guard (usage.jsonl) and all evaluations through tournament.evallog
(evals.jsonl).
"""
import json
import os
import time
from argparse import Namespace
from pathlib import Path

from .budget import BudgetExhausted
from .context import Context
from .evallog import PROBLEM_ENV, evaluate_logged

REPO = Path(__file__).resolve().parents[1]
ARMS = {}


def arm(name):
    def register(fn):
        ARMS[name] = fn
        return fn
    return register


@arm("lean")
def lean(ctx: Context):
    from . import lean as lean_loop
    return lean_loop.run(ctx)


@arm("independent")
def independent(ctx: Context):
    """Independent sampling: lean's loop with no history and no parent (see tournament/lean.py)."""
    from . import lean as lean_loop
    ctx.config = {**ctx.config, "independent": True}
    return lean_loop.run(ctx)


@arm("shinka")
def shinka(ctx: Context):
    """Stock ShinkaEvolve through autoresearch/run.py; its own soft cost limit is set to the cap too."""
    from autoresearch import run as shinka_run
    o = ctx.option
    os.environ[PROBLEM_ENV] = str(ctx.problem_dir)
    argv = [str(ctx.problem_dir),
            "--generations", str(o("max_generations", 1000)),
            "--model", o("model", "claude-sonnet-5-5"),
            "--effort", o("effort", "high"),
            "--max-tokens", str(o("max_tokens", 32000)),
            "--results", str(ctx.out / "shinka"),
            "--max-cost", str(ctx.budget.cap),
            "--eval-jobs", str(o("eval_jobs", 2)),
            "--proposal-jobs", str(o("proposal_jobs", 2)),
            "--eval-program", str(REPO / "tournament" / "shinka_eval.py")]
    ctx.event(event="arm_start", arm="shinka", argv=argv)
    # Once the guard refuses a call, report the committed cost as unbounded so ShinkaEvolve stops
    # proposing and finishes the evaluations already paid for (otherwise it retries refused calls).
    from shinka.core.async_runner import ShinkaEvolveRunner
    committed = ShinkaEvolveRunner._get_committed_cost
    ShinkaEvolveRunner._get_committed_cost = lambda self: float("inf") if ctx.budget.exhausted else committed(self)
    try:
        shinka_run.main(argv)
    finally:
        ShinkaEvolveRunner._get_committed_cost = committed
    if ctx.budget.fatal:
        return "fatal_api_error"
    return "budget" if ctx.budget.exhausted else "generations_done"


@arm("triage")
def triage(ctx: Context):
    """autoresearch/triage.py unchanged, with its --budget set to the cap."""
    from autoresearch import triage as tri
    from autoresearch.analyze import summarize, write_notebook
    o = ctx.option
    args = Namespace(problem=str(ctx.problem_dir), rounds=o("max_rounds", 1000), ideas=o("ideas", 6),
                     ranker=o("ranker", "random"), ranker_model=o("ranker_model", "claude-haiku-4-5"),
                     tiers=o("tiers", "claude-opus-5-5,claude-sonnet-5-5,claude-haiku-4-5"),
                     efforts=o("efforts", "high,high,"), uniform=o("uniform", None),
                     uniform_effort=o("uniform_effort", "high"), idea_model=o("idea_model", "claude-opus-5-5"),
                     idea_effort=o("idea_effort", "medium"), swap=o("swap", 0.15),
                     no_promotion=o("no_promotion", False), budget=ctx.budget.cap,
                     max_tokens=o("max_tokens", 32000), workers=o("workers", 6), seed=ctx.seed,
                     out=str(ctx.out / "triage"))
    args.efforts = args.efforts if args.efforts.count(",") == 2 else "high,high,"
    tri.evaluate = lambda problem_dir, program, results: evaluate_logged(problem_dir, program, results, tag="triage")
    run = tri.Run(args)
    rank = run.ranker.rank
    if run.ranker.name == "jev":   # Jev is billed outside Anthropic; count it against the same cap
        def charged_rank(*a, **k):
            for attempt in range(5):  # transient Jev errors must not end the run
                try:
                    out = rank(*a, **k)
                    break
                except Exception as e:
                    ctx.event(event="ranker_error", attempt=attempt, error=f"{type(e).__name__}: {str(e)[:300]}")
                    if attempt == 4:
                        raise
                    time.sleep(5 * 2 ** attempt)
            ctx.budget.charge_external(sum(r.cost for r in out), "jev")
            return out
        run.ranker.rank = charged_rank
    ctx.event(event="arm_start", arm="triage", args=vars(args))
    try:
        run.run()
        return "rounds_done"
    except BudgetExhausted:
        stop = "fatal_api_error" if ctx.budget.fatal else "budget"
        ends = [json.loads(line) for line in open(run.log_path) if '"round_end"' in line]
        start = json.loads(open(run.log_path).readline())
        best = ends[-1]["best_score"] if ends else start["initial_score"]
        run.log({"event": "end", "best_score": best, "stop": stop})
        (run.out / "summary.json").write_text(json.dumps(summarize(run.log_path), indent=2))
        write_notebook(run.log_path, run.out / "notebook.md")
        return stop
