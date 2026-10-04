"""Timeout analysis for llm-from-ss-v1, added after the coordinator's validity note about machine load
(see RUN_LOG.md). For every run: failed candidate evaluations split into timeouts and code errors. Every
candidate that timed out on a public instance is re-evaluated through the same gate with the same 30 s
per-instance limit, after the runs have finished (so under lower load), and its re-evaluated public score
is compared with the incumbent's public score at that step. A candidate whose re-evaluated score exceeds
the incumbent's would have passed the score test; the archive (non-regression) test is not replayed.
Writes timeouts.json.

    python experiments/llm-from-ss-v1/timeouts.py
"""
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROB = ROOT / "problems" / "bin_packing_online_ss"


def program_dir(ev, unpacked):
    """The candidate's folder: live during a run, or inside artifacts.tar.gz (unpacked) afterwards."""
    live = Path(ev["program"]).parent
    return live if live.exists() else unpacked / "programs" / ev["tag"]


def failure_reasons(ev, unpacked):
    f = program_dir(ev, unpacked) / "results" / "integrity.json"
    if not f.exists():
        return ["(no integrity.json)"]
    ij = json.loads(f.read_text())
    return [p.get("reason") or "" for p in ij.get("public", []) if p.get("status") != "valid"]


def incumbent_scores(run):
    """Public score of the incumbent before each step: from events.jsonl (incumbent events)."""
    out, cur = {}, None
    for line in (run / "events.jsonl").read_text().splitlines():
        e = json.loads(line)
        if e.get("event") == "incumbent":
            cur = e["score"]
        elif e.get("event") == "step":
            out[e["iter"]] = cur
    return out


def reevaluate(program):
    with tempfile.TemporaryDirectory() as tmp:
        t = time.time()
        subprocess.run([sys.executable, str(PROB / "evaluate.py"), "--program_path", program, "--results_dir", tmp],
                       cwd=str(ROOT), check=False, capture_output=True, timeout=900)
        m = Path(tmp) / "metrics.json"
        ij = Path(tmp) / "integrity.json"
        res = {"seconds": round(time.time() - t, 1)}
        if m.exists():
            md = json.loads(m.read_text())
            res["combined"] = md.get("combined_score")
        if ij.exists():
            d = json.loads(ij.read_text())
            res["public_status"] = [p.get("status") for p in d.get("public", [])]
            res["public_seconds"] = [round(p.get("seconds") or 0, 2) for p in d.get("public", [])]
        return res


def main():
    out = {"load_at_analysis": os.getloadavg(), "runs": {}}
    tmp_root = tempfile.TemporaryDirectory()
    for run in sorted(p for p in (HERE / "runs").glob("s*") if p.is_dir()):
        unpacked = Path(tmp_root.name) / run.name
        if (run / "artifacts.tar.gz").exists():
            with tarfile.open(run / "artifacts.tar.gz") as t:
                t.extractall(unpacked, filter="data")
        evals = [json.loads(l) for l in (run / "evals.jsonl").read_text().splitlines()]
        inc = incumbent_scores(run)
        r = {"evals": len(evals), "failed_evals": 0, "timeout_evals": 0, "code_error_evals": 0, "other_failed_evals": 0,
             "timed_out": []}
        for ev in evals:
            if all(s == "valid" for s in ev["public_status"]):
                continue
            r["failed_evals"] += 1
            reasons = failure_reasons(ev, unpacked)
            if ev.get("instance_timeouts") or any("timed out" in x for x in reasons):
                r["timeout_evals"] += 1
                it = int(ev["tag"][2:]) if ev["tag"].startswith("it") else None
                re = reevaluate(str(program_dir(ev, unpacked) / "program.py"))
                incumbent = inc.get(it)
                r["timed_out"].append({"tag": ev["tag"], "seconds_in_run": ev["seconds"], "public_status_in_run": ev["public_status"],
                                       "reevaluated": re, "incumbent_public": incumbent,
                                       "would_pass_score_test": (re.get("combined") is not None and incumbent is not None
                                                                 and re["combined"] > incumbent)})
                print(run.name, r["timed_out"][-1], flush=True)
            elif any(("Traceback" in x) or ("Error" in x) or ('File "' in x) for x in reasons):
                r["code_error_evals"] += 1
            else:
                r["other_failed_evals"] += 1
                r.setdefault("other_reasons", []).append([x[:200] for x in reasons])
        out["runs"][run.name] = r
        print(run.name, {k: v for k, v in r.items() if k != "timed_out"}, flush=True)
    (HERE / "timeouts.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
