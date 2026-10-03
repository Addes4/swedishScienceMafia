"""Grid files: which arms, problems, seeds and dollar budget a tournament runs, and its spend caps.

A grid is JSON:

    {"name": "mock-v1", "mode": "mock" | "live", "budget_usd": 0.5, "seeds": [0, 1],
     "problems": ["erdos_squares", "circle_packing"],
     "arms": {"lean": {"type": "lean"}, "lean_gate_patience": {"type": "lean", "gate": true, "patience": 5}, ...},
     "anthropic_cap_usd": 0, "modal_cap_usd": 5,
     "wall_limit_s": 1800, "cpu": 2, "memory_mb": 4096}

Adding a problem is adding its folder name to "problems" (any folder that follows
problems/README.md). Adding an arm variant is adding an entry to "arms".
"""
import json
from pathlib import Path

# Modal list prices (`modal billing rates`, 3 Oct 2026): CPU $0.0473 per core-hour, memory $0.008 per GiB-hour.
MODAL_CPU_PER_CORE_HOUR = 0.0473
MODAL_MEM_PER_GIB_HOUR = 0.008
CONTAINER_OVERHEAD_S = 600       # image pull, startup and the post-budget grace period, per job


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
                            "mock": grid["mode"] == "mock", "mock_latency": grid.get("mock_latency", 0.05)})
    return out


def worst_case_modal_usd(grid: dict, n_jobs: int) -> float:
    hours = (grid.get("wall_limit_s", 3 * 3600) + CONTAINER_OVERHEAD_S + 900) / 3600   # +900: hard-stop grace
    per_job = hours * (grid.get("cpu", 2) * MODAL_CPU_PER_CORE_HOUR + grid.get("memory_mb", 4096) / 1024 * MODAL_MEM_PER_GIB_HOUR)
    return n_jobs * per_job


def check_caps(grid: dict, job_list: list) -> dict:
    """Refuse grids whose worst case exceeds the declared Anthropic or Modal caps."""
    anthropic_total = 0.0 if grid["mode"] == "mock" else sum(j["budget_usd"] for j in job_list)
    modal_worst = worst_case_modal_usd(grid, len(job_list))
    if anthropic_total > grid.get("anthropic_cap_usd", 0.0) + 1e-9:
        raise SystemExit(f"grid {grid['name']}: job budgets sum to ${anthropic_total:.2f}, above anthropic_cap_usd "
                         f"${grid.get('anthropic_cap_usd', 0.0):.2f}")
    if modal_worst > grid.get("modal_cap_usd", 0.0) + 1e-9:
        raise SystemExit(f"grid {grid['name']}: worst-case Modal cost ${modal_worst:.2f} is above modal_cap_usd "
                         f"${grid.get('modal_cap_usd', 0.0):.2f}")
    return {"jobs": len(job_list), "anthropic_worst_usd": round(anthropic_total, 2), "modal_worst_usd": round(modal_worst, 2)}
