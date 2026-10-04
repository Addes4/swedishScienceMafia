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
    if os.environ.get("GATE_WORKERS"):   # its eval jobs are separate processes: share the cores between them
        os.environ["GATE_WORKERS"] = str(max(1, int(os.environ["GATE_WORKERS"]) // int(o("eval_jobs", 2))))
    model = o("model", "claude-sonnet-5-5")
    if ctx.provider == "hf":   # ShinkaEvolve's own OpenAI-compatible client, pointed at the router
        from .hf import base_url
        model = f"local/{model}@{base_url()}?api_key_env=HF_TOKEN"
    argv = [str(ctx.problem_dir),
            "--generations", str(o("max_generations", 1000)),
            "--model", model,
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
