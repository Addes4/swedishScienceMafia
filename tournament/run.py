"""Run one tournament job: one arm on one problem with one seed and one dollar cap.

    python -m tournament.run --arm lean --problem erdos_squares --seed 0 --budget 1 --out runs/lean-es-0
    python -m tournament.run --arm lean --arm-config '{"type": "lean", "gate": true, "patience": 5}' ...
    python -m tournament.run --job '{"job_id": ..., "arm": ..., ...}' --out DIR      (what Modal runs)
    add --mock to replace the Anthropic API by a local fake (no network, no cost)

Writes to --out: job.json (config, source hashes, versions), usage.jsonl, evals.jsonl,
events.jsonl, summary.json, curve.csv, best_program.py, stdout of the arm, and the arm's own
files packed into artifacts.tar.gz.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HASHED = ["tournament/*.py", "autoresearch/*.py", "strategist/controller.py", "requirements.txt"]
PACKAGES = ["anthropic", "shinka-evolve", "typesafe-sdk", "numpy", "scipy"]
ARM_DIRS = ["programs", "shinka", "triage"]


def source_hashes(problem_dir: Path) -> dict:
    files = [p for pat in HASHED for p in sorted(REPO.glob(pat))] + sorted(problem_dir.glob("*"))
    return {str(p.relative_to(REPO)) if p.is_relative_to(REPO) else str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files if p.is_file()}


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True,
                              timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def resolve_problem(name: str) -> Path:
    p = Path(name)
    if not p.is_absolute() and not (p / "verify.py").exists():
        p = REPO / "problems" / name
    p = p.resolve()
    for f in ("problem.md", "initial.py", "verify.py"):
        if not (p / f).exists():
            raise SystemExit(f"{p} is not a problem folder (missing {f}); see problems/README.md")
    return p


def max_eval_seconds(problem_dir: Path) -> float:
    from autoresearch.gate import _load_verify, _timeout
    v = _load_verify(problem_dir)
    return (len(v.PUBLIC) + len(getattr(v, "HIDDEN", []))) * _timeout(v)


AMENDMENT = ("\n\nTime limit in this run: {t:g} seconds per instance (this replaces any limit stated above). "
             "A program that runs longer on an instance fails on it.\n")


def apply_time_limit(problem_dir: Path, out: Path, seconds: float) -> Path:
    """Copy the problem folder into the run and tell the model the run's per-instance limit.
    verify.py is copied unchanged; the gate applies the limit through GATE_TIMEOUT_S."""
    copy = out / "problem"
    shutil.copytree(problem_dir, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (copy / "problem.md").write_text((problem_dir / "problem.md").read_text().rstrip("\n") + AMENDMENT.format(t=seconds))
    os.environ["GATE_TIMEOUT_S"] = str(seconds)
    return copy


class Finisher:
    """Writes summary.json, curve.csv and the artifact archive exactly once, from whichever thread ends first."""

    def __init__(self, out: Path, ctx_event):
        self.out, self.ctx_event = out, ctx_event
        self.lock = threading.Lock()
        self.done = False

    def __call__(self, status: str, arm_result=None, pack=True):
        from .metrics import summarize, write_curve
        with self.lock:
            if self.done:
                return
            self.done = True
            from . import guard
            budget = guard.current()
            self.ctx_event(event="run_end", status=status, arm_result=arm_result,
                           budget=budget.snapshot() if budget else None)
            summary = summarize(self.out)
            write_curve(summary, self.out / "curve.csv")
            (self.out / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
            best = self.out / "best_program.py"
            if summary["final_sha"] and not best.exists():   # arms that do not write it themselves
                from .metrics import load_jsonl
                src = next((Path(e["program"]) for e in load_jsonl(self.out / "evals.jsonl")
                            if e["sha"] == summary["final_sha"] and Path(e["program"]).exists()), None)
                if src:
                    shutil.copyfile(src, best)
            if pack:
                dirs = [d for d in ARM_DIRS if (self.out / d).exists()]
                if dirs:
                    with tarfile.open(self.out / "artifacts.tar.gz", "w:gz") as tar:
                        for d in dirs:
                            tar.add(self.out / d, arcname=d)
                    for d in dirs:
                        shutil.rmtree(self.out / d, ignore_errors=True)


def watchdog(budget, deadline: float, grace: float, finish, finisher, poll: float = 2.0):
    """Hard stop: once the budget is exhausted (after a grace period for evaluations already paid for)
    or the wall-clock limit has passed, write the summary and exit the process. Returns as soon as
    the run has finished normally."""
    exhausted_at = None
    while not finisher.done:
        time.sleep(poll)
        if finisher.done:
            return
        now = time.time()
        if budget.exhausted and exhausted_at is None:
            exhausted_at = now
        if exhausted_at is not None and now > exhausted_at + grace:
            finish("budget_hard_stop")
            os._exit(0)
        if now > deadline + grace:
            finish("wall_hard_stop")
            os._exit(0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job", help="full job as JSON (overrides the flags below)")
    ap.add_argument("--arm", default="lean", help="arm name (also the type unless --arm-config gives one)")
    ap.add_argument("--arm-config", default="{}", help="arm config as JSON")
    ap.add_argument("--problem", default="erdos_squares")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--budget", type=float, default=1.0, help="hard dollar cap for this run")
    ap.add_argument("--wall-limit", type=float, default=3 * 3600, help="seconds")
    ap.add_argument("--mock", action="store_true", help="use the local mock API (no network, no cost)")
    ap.add_argument("--grid", default="adhoc")
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true", help="rerun even if summary.json exists")
    ap.add_argument("--no-pack", action="store_true")
    a = ap.parse_args(argv)

    if a.job:
        job = json.loads(a.job)
    else:
        cfg = json.loads(a.arm_config)
        cfg.setdefault("type", a.arm)
        job = {"job_id": f"{a.arm}__{Path(a.problem).name}__s{a.seed}", "grid": a.grid, "arm": a.arm,
               "arm_config": cfg, "problem": a.problem, "seed": a.seed, "budget_usd": a.budget,
               "wall_limit_s": a.wall_limit, "mock": a.mock}
    out = Path(a.out).resolve()
    if (out / "summary.json").exists() and not a.force:
        print(f"[skip] {out} already has summary.json")
        return 0
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    sys.path.insert(0, str(REPO))
    from .arms import ARMS
    from .budget import Budget, BudgetExhausted
    from .context import Context
    from .evallog import EVAL_LOG_ENV, PROBLEM_ENV
    from . import guard

    problem_dir = resolve_problem(job["problem"])
    arm_type = job["arm_config"].get("type", job["arm"])
    if arm_type not in ARMS:
        raise SystemExit(f"unknown arm type {arm_type!r}; known: {sorted(ARMS)}")
    job.update(started_at=time.time(), problem_dir=str(problem_dir), git_commit=git_commit(),
               python=platform.python_version(), host=platform.node(),
               packages={p: _version(p) for p in PACKAGES}, source_hashes=source_hashes(problem_dir))
    (out / "job.json").write_text(json.dumps(job, indent=2))

    os.chdir(out)  # ShinkaEvolve loads .env from the launch directory; keep it away from the repo's
    provider = job.get("provider", "anthropic")
    if job.get("gate_workers"):
        os.environ["GATE_WORKERS"] = str(int(job["gate_workers"]))
    limit = (job.get("timeout_overrides") or {}).get(Path(job["problem"]).name)
    if limit:
        problem_dir = apply_time_limit(problem_dir, out, float(limit))
        job.update(time_limit_s=float(limit), problem_amendment=AMENDMENT.format(t=float(limit)).strip())
        (out / "job.json").write_text(json.dumps(job, indent=2))
    mock = None
    if job.get("mock"):
        from .mockapi import MockAnthropic
        mock = MockAnthropic(seed=job["seed"], latency=job.get("mock_latency", 0.05)).start()
        failure = job.get("mock_failure")   # tests only: e.g. {"after": 3, "status": 400, "message": "credit balance..."}
        if failure:
            mock.fail_after, mock.fail_status = failure["after"], failure.get("status", 400)
            mock.fail_type = failure.get("type", "invalid_request_error")
            mock.fail_message = failure.get("message", "Your credit balance is too low to access the Anthropic API.")
    else:
        from autoresearch.env import load_env, require
        load_env()
        if provider == "hf":
            from . import hf
            hf.token()   # raises if no token; never printed
            if os.environ.get(hf.BASE_ENV):
                raise SystemExit(f"{hf.BASE_ENV} is set; refusing a live run against a non-default endpoint")
        else:
            require("ANTHROPIC_API_KEY", "live tournament runs call Claude")
            if os.environ.get("ANTHROPIC_BASE_URL"):
                raise SystemExit("ANTHROPIC_BASE_URL is set; refusing a live run against a non-default endpoint")

    budget = Budget(job["budget_usd"], out / "usage.jsonl", min_output_tokens=job.get("min_output_tokens", 2048))
    guard.install(budget)
    if provider == "hf":   # prices from the router's own list, recorded with the run
        from . import hf
        from .budget import register_prices
        prices = hf.fetch_prices(job["hf_models"])
        register_prices(prices)
        hf.install(budget)
        job["prices_usd_per_mtok"] = {m: list(p) for m, p in prices.items()}
        (out / "job.json").write_text(json.dumps(job, indent=2))
    os.environ[EVAL_LOG_ENV] = str(out / "evals.jsonl")
    os.environ[PROBLEM_ENV] = str(problem_dir)
    deadline = time.time() + float(job.get("wall_limit_s", 3 * 3600))
    ctx = Context(problem_dir=problem_dir, out=out, seed=job["seed"], budget=budget,
                  config={k: v for k, v in job["arm_config"].items() if k != "type"}, deadline=deadline,
                  provider=provider)
    finish = Finisher(out, ctx.event)
    grace = max_eval_seconds(problem_dir) + 60
    threading.Thread(target=watchdog, args=(budget, deadline, grace, lambda s: finish(s, pack=not a.no_pack), finish),
                     daemon=True).start()

    print(f"[start] {job['job_id']}: arm {job['arm']} ({arm_type}) on {Path(job["problem"]).name}, seed {job['seed']}, "
          f"cap ${budget.cap:.2f}{' (mock API)' if mock else ''}", flush=True)
    status, result = "ok", None
    try:
        result = ARMS[arm_type](ctx)
    except BudgetExhausted:
        status = "budget"
    except BaseException as e:  # record and still write the summary
        status = f"error: {type(e).__name__}"
        (out / "error.txt").write_text(traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr, flush=True)
    if budget.fatal:   # the arm stopped because the API refused fatally: not a budget-matched run
        status = "fatal_api_error"
    finish(status, arm_result=result, pack=not a.no_pack)
    guard.uninstall()
    if provider == "hf":
        from . import hf
        hf.uninstall()
    if mock:
        mock.stop()
    s = json.loads((out / "summary.json").read_text())
    print(f"[done] {job['job_id']}: status {status}, spent ${s['spent_usd']:.4f} of ${s['cap_usd']:.2f}, "
          f"{s['calls']} calls, {s['evals']} evals, public {s['initial_public']} -> {s['final_public']}, "
          f"hidden {s['final_hidden']}", flush=True)
    return 0


def _version(pkg):
    try:
        return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError:
        return None


if __name__ == "__main__":
    sys.exit(main())
