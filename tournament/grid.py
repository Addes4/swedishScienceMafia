"""Grid files: which arms, problems, seeds and dollar budget a tournament runs, and its spend caps.

A grid is JSON:

    {"name": "mock-v1", "mode": "mock" | "live", "budget_usd": 0.5, "seeds": [0, 1],
     "problems": ["erdos_squares", "circle_packing"],
     "arms": {"lean": {"type": "lean"}, "lean_gate_patience": {"type": "lean", "gate": true, "patience": 5}, ...},
     "jobs": ["lean__erdos_squares__s0", ...],        # optional: run only these jobs of the cross product
     "experiment": "tournament-v2",                   # optional: folder under experiments/ (default tournament-v1)
     "provider": "hf", "hf_models": ["model:provider", ...],   # optional: Hugging Face router instead of Anthropic
     "gate_workers": 8,                               # optional: evaluate instances in parallel (scores unchanged)
     "timeout_overrides": {"erdos_squares": 20},      # optional: per-instance time limit, told to the model too
     "anthropic_cap_usd": 0, "modal_cap_usd": 5,
     "experiment_cap_usd": 75,                        # optional: cap on all live spend in the experiment
     "wall_limit_s": 1800, "cpu": 2, "memory_mb": 4096}

Adding a problem is adding its folder name to "problems" (any folder that follows
problems/README.md). Adding an arm variant is adding an entry to "arms".

Caps checked before launch: the grid's job budgets against anthropic_cap_usd; its worst-case Modal
cost against modal_cap_usd; and, with experiment_cap_usd, the Anthropic spend already recorded by
every live run pulled into the experiment's runs/ folder plus this grid's job budgets. Pull each
live grid (python -m tournament.pull <grid>) before launching the next, so the ledger is complete.
"""
import json
from pathlib import Path

from .metrics import load_jsonl

# Modal list prices (`modal billing rates`, 3 Oct 2026): CPU $0.0473 per core-hour, memory $0.008 per GiB-hour.
MODAL_CPU_PER_CORE_HOUR = 0.0473
MODAL_MEM_PER_GIB_HOUR = 0.008
CONTAINER_OVERHEAD_S = 600       # image pull, startup and the post-budget grace period, per job
EXPERIMENTS = Path(__file__).resolve().parents[1] / "experiments"
RUNS = EXPERIMENTS / "tournament-v1" / "runs"


def experiment_dir(grid: dict) -> Path:
    """experiments/<grid "experiment", default tournament-v1>/: holds runs/ and launches/."""
    return EXPERIMENTS / grid.get("experiment", "tournament-v1")


def load(path) -> dict:
    grid = json.loads(Path(path).read_text())
    for key in ("name", "mode", "budget_usd", "seeds", "problems", "arms"):
        if key not in grid:
            raise SystemExit(f"grid {path} is missing {key!r}")
    if grid["mode"] not in ("mock", "live"):
        raise SystemExit("grid mode must be 'mock' or 'live'")
    return grid


def jobs(grid: dict) -> list:
    out = []
    for arm, cfg in grid["arms"].items():
        cfg = dict(cfg)
        cfg.setdefault("type", arm)
        for problem in grid["problems"]:
            for seed in grid["seeds"]:
                budget = grid.get("budget_by_arm", {}).get(arm, grid["budget_usd"])   # only for checks; the
                # comparison grids give every arm and problem the same budget
                out.append({"job_id": f"{arm}__{problem}__s{seed}", "grid": grid["name"], "arm": arm,
                            "arm_config": cfg, "problem": problem, "seed": seed, "budget_usd": budget,
                            "wall_limit_s": grid.get("wall_limit_s", 3 * 3600),
                            "mock": grid["mode"] == "mock", "mock_latency": grid.get("mock_latency", 0.05),
                            "provider": grid.get("provider", "anthropic"), "hf_models": grid.get("hf_models", []),
                            "gate_workers": grid.get("gate_workers"), "timeout_overrides": grid.get("timeout_overrides")})
    if "jobs" in grid:
        wanted = list(grid["jobs"])
        unknown = sorted(set(wanted) - {j["job_id"] for j in out})
        if unknown or len(set(wanted)) != len(wanted):
            raise SystemExit(f"grid {grid['name']}: unknown or repeated job ids {unknown or wanted}")
        out = [j for j in out if j["job_id"] in set(wanted)]
    return out


def worst_case_modal_usd(grid: dict, n_jobs: int) -> float:
    hours = (grid.get("wall_limit_s", 3 * 3600) + CONTAINER_OVERHEAD_S + 900) / 3600   # +900: hard-stop grace
    per_job = hours * (grid.get("cpu", 2) * MODAL_CPU_PER_CORE_HOUR + grid.get("memory_mb", 4096) / 1024 * MODAL_MEM_PER_GIB_HOUR)
    return n_jobs * per_job


def recorded_spend(runs_dir: Path = RUNS, exclude_grid: str = None) -> dict:
    """Anthropic (and Jev) spend recorded by every live run under runs_dir, per grid folder."""
    out = {}
    if not runs_dir.exists():
        return out
    for grid_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir() and p.name != exclude_grid):
        total = 0.0
        for run in grid_dir.iterdir():
            job = run / "job.json"
            if not job.exists() or json.loads(job.read_text()).get("mock"):
                continue
            total += sum(r.get("cost_usd") or 0 for r in load_jsonl(run / "usage.jsonl")
                         if r.get("event") in ("call", "external"))
        if total:
            out[grid_dir.name] = round(total, 4)
    return out


def check_caps(grid: dict, job_list: list, experiment_cap: float = None, runs_dir: Path = None) -> dict:
    """Refuse grids whose worst case exceeds the declared Anthropic, Modal or experiment caps."""
    anthropic_total = 0.0 if grid["mode"] == "mock" else sum(j["budget_usd"] for j in job_list)
    modal_worst = worst_case_modal_usd(grid, len(job_list))
    if anthropic_total > grid.get("anthropic_cap_usd", 0.0) + 1e-9:
        raise SystemExit(f"grid {grid['name']}: job budgets sum to ${anthropic_total:.2f}, above anthropic_cap_usd "
                         f"${grid.get('anthropic_cap_usd', 0.0):.2f}")
    if modal_worst > grid.get("modal_cap_usd", 0.0) + 1e-9:
        raise SystemExit(f"grid {grid['name']}: worst-case Modal cost ${modal_worst:.2f} is above modal_cap_usd "
                         f"${grid.get('modal_cap_usd', 0.0):.2f}")
    out = {"jobs": len(job_list), "anthropic_worst_usd": round(anthropic_total, 2), "modal_worst_usd": round(modal_worst, 2)}
    cap = experiment_cap if experiment_cap is not None else grid.get("experiment_cap_usd")
    if cap is not None and grid["mode"] == "live":
        prior = recorded_spend(runs_dir or experiment_dir(grid) / "runs", exclude_grid=grid["name"])
        total = sum(prior.values()) + anthropic_total
        out.update(experiment_recorded_usd=prior, experiment_worst_total_usd=round(total, 2), experiment_cap_usd=cap)
        if total > cap + 1e-9:
            raise SystemExit(f"grid {grid['name']}: spend already recorded in this experiment (${sum(prior.values()):.2f}: "
                             f"{prior}) plus this grid's job budgets (${anthropic_total:.2f}) is ${total:.2f}, above the "
                             f"experiment cap ${cap:.2f}. Raise it only with approval (--experiment-cap).")
    return out
