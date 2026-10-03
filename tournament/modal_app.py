"""Modal app ssm-tournament: one container per (arm, problem, seed, budget) job.

    modal run tournament/modal_app.py --grid experiments/tournament-v1/grids/mock.json
    modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/full.json   # live grid
    python -m tournament.pull mock-v1        # copy results from the Volume into experiments/tournament-v1/runs/

Each container runs `python -m tournament.run --job ...` with its own hard dollar cap, writes
to the Volume ssm-tournament under /<grid>/<job_id>/, and returns the run summary. Live grids
get API keys from the Modal secret ssm-llm-keys; mock grids get no secret at all. Only the code
directories are copied into the image (never .env).
"""
import gzip
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import modal

REPO = Path(__file__).resolve().parents[1]
if modal.is_local() and str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
APP_NAME = "ssm-tournament"
VOLUME_NAME = "ssm-tournament"
SECRET_NAME = "ssm-llm-keys"
CODE_DIRS = ["autoresearch", "problems", "strategist", "tournament", "falsify"]
IGNORE = ["**/__pycache__/**", "**/*.pyc", "**/*.so", "**/*.dylib", "**/.env", "**/results/**"]
PINS = ["anthropic==1.11.0", "shinka-evolve==0.0.7", "typesafe-sdk==0.7.2", "numpy==2.5.3", "scipy==1.18.1"]

image = (modal.Image.debian_slim(python_version="3.12")
         .apt_install("build-essential", "git")
         .pip_install_from_requirements(str(REPO / "requirements.txt"))
         .pip_install(*PINS)
         .env({"PYTHONUNBUFFERED": "1"}))
for d in CODE_DIRS:
    image = image.add_local_dir(REPO / d, f"/repo/{d}", ignore=IGNORE)
image = image.add_local_file(REPO / "requirements.txt", "/repo/requirements.txt")

app = modal.App(APP_NAME, image=image)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


@app.function(volumes={"/vol": volume}, cpu=2.0, memory=4096, timeout=6 * 3600, retries=0, max_containers=100)
def run_job(job: dict) -> dict:
    out = Path("/vol") / job["grid"] / job["job_id"]
    if (out / "summary.json").exists():
        return {"job_id": job["job_id"], "skipped": True, **json.loads((out / "summary.json").read_text())}
    if not job.get("mock") and not os.environ.get("ANTHROPIC_API_KEY"):
        return {"job_id": job["job_id"], "error": "live job without ANTHROPIC_API_KEY (secret not attached)"}
    out.parent.mkdir(parents=True, exist_ok=True)
    log_path = Path("/tmp") / f"{job['job_id']}.log"
    t0 = time.time()
    with open(log_path, "w") as log:
        proc = subprocess.Popen([sys.executable, "-m", "tournament.run", "--job", json.dumps(job), "--out", str(out),
                                 "--force"], cwd="/repo", stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        rc = proc.wait()
    try:
        os.killpg(proc.pid, signal.SIGKILL)   # stray evaluation processes left by a hard stop
    except (ProcessLookupError, PermissionError):
        pass
    out.mkdir(parents=True, exist_ok=True)
    with gzip.open(out / "stdout.log.gz", "wt") as f:
        f.write(log_path.read_text())
    volume.commit()
    summary_path = out / "summary.json"
    result = {"job_id": job["job_id"], "returncode": rc, "container_seconds": round(time.time() - t0, 1)}
    if summary_path.exists():
        s = json.loads(summary_path.read_text())
        s.pop("curve", None)
        result.update(s)
    else:
        result["error"] = "no summary.json; see stdout.log"
    return result


@app.local_entrypoint()
def main(grid: str, only: str = "", dry_run: bool = False, experiment_cap: float = -1.0):
    from tournament import grid as grids
    g = grids.load(grid)
    job_list = grids.jobs(g)
    if only:
        keep = set(only.split(","))
        job_list = [j for j in job_list if j["job_id"] in keep or j["arm"] in keep or j["problem"] in keep]
    caps = grids.check_caps(g, job_list, experiment_cap=None if experiment_cap < 0 else experiment_cap)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO, capture_output=True,
                           text=True).stdout.strip()
    if g["mode"] == "live" and dirty and not dry_run:
        raise SystemExit("tracked files have uncommitted changes; commit before a live launch so runs name their code")
    for j in job_list:
        j["launch_commit"], j["launch_dirty"] = commit, bool(dirty)
    print(f"grid {g['name']} ({g['mode']}): {caps}, commit {commit[:10]}{' (dirty)' if dirty else ''}")
    if dry_run:
        for j in job_list:
            print("  ", j["job_id"], f"${j['budget_usd']:.2f}")
        return
    fn = run_job
    if g["mode"] == "live":
        fn = run_job.with_options(secrets=[modal.Secret.from_name(SECRET_NAME)])
    fn = fn.with_options(cpu=float(g.get("cpu", 2)), memory=int(g.get("memory_mb", 4096)),
                         timeout=int(g.get("wall_limit_s", 3 * 3600)) + 1800)
    results = []
    for res in fn.map(job_list, return_exceptions=True, order_outputs=False):
        if isinstance(res, Exception):
            res = {"error": f"{type(res).__name__}: {res}"}
        results.append(res)
        print(json.dumps({k: res.get(k) for k in ("job_id", "error", "spent_usd", "cap_usd", "calls", "evals",
                                                  "initial_public", "final_public", "final_hidden", "status",
                                                  "container_seconds", "skipped")}, default=str), flush=True)
    local = REPO / "experiments" / "tournament-v1" / "launches"
    local.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    (local / f"{g['name']}_{stamp}.json").write_text(json.dumps({"grid": g, "caps": caps, "results": results},
                                                                indent=2, default=str))
    errors = [r for r in results if r.get("error")]
    print(f"done: {len(results)} jobs, {len(errors)} errors, "
          f"Anthropic spend ${sum(r.get('spent_usd') or 0 for r in results if not r.get('mock')):.4f}")
