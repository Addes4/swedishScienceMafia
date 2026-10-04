"""Timeout accounting for short-horizon-v1, added after the coordinator's validity note on machine load.

For each run, read every candidate evaluation's integrity.json from artifacts.tar.gz. Each public and
hidden instance has a status, a reason and the seconds it took. Classify each failed evaluation as
failed by timeout or by a code error. Report how close valid evaluations came to the 60 s per-instance
limit. Writes timeouts.json.

    python experiments/short-horizon-v1/timeouts.py
"""
import json
import tarfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LIMIT = 60.0


def run_stats(run_dir):
    evals = {json.loads(l)["tag"]: json.loads(l) for l in (run_dir / "evals.jsonl").read_text().splitlines()}
    out = {"evals": 0, "invalid": 0, "invalid_timeout_only": 0, "invalid_code_error": 0,
           "evals_any_public_timeout": 0, "evals_any_hidden_timeout": 0, "public_instance_timeouts": 0,
           "valid_public_instance_seconds": [], "valid_evals_max_public_seconds_over_30": 0,
           "valid_evals_max_public_seconds_over_45": 0, "timed_out_tags": []}
    with tarfile.open(run_dir / "artifacts.tar.gz") as tar:
        for m in tar.getmembers():
            if not m.name.endswith("results/integrity.json"):
                continue
            tag = m.name.split("/")[1]
            if tag == "initial" or tag not in evals:
                continue
            integ = json.load(tar.extractfile(m))
            pub, hid = integ.get("public", []), integ.get("hidden", [])
            to = lambda r: "timed out" in str(r.get("reason") or "")
            out["evals"] += 1
            pto = sum(to(r) for r in pub)
            out["public_instance_timeouts"] += pto
            out["evals_any_public_timeout"] += pto > 0
            out["evals_any_hidden_timeout"] += any(to(r) for r in hid)
            if pto:
                out["timed_out_tags"].append(tag)
            if not evals[tag]["correct"]:
                out["invalid"] += 1
                failed = [r for r in pub if r.get("status") != "valid"]
                if failed and all(to(r) for r in failed):
                    out["invalid_timeout_only"] += 1
                elif not integ.get("static_violations"):
                    out["invalid_code_error"] += 1
            else:
                secs = [r.get("seconds", 0.0) for r in pub if r.get("status") == "valid"]
                out["valid_public_instance_seconds"] += secs
                out["valid_evals_max_public_seconds_over_30"] += max(secs, default=0) > 30
                out["valid_evals_max_public_seconds_over_45"] += max(secs, default=0) > 45
    s = out.pop("valid_public_instance_seconds")
    out["valid_public_instance_seconds_median"] = float(np.median(s)) if s else None
    out["valid_public_instance_seconds_p95"] = float(np.percentile(s, 95)) if s else None
    return out


def main():
    runs = {}
    for d in sorted(p for p in (HERE / "runs").iterdir() if (p / "report.md").exists()):
        runs[d.name] = run_stats(d)
    arms = {}
    for name, r in runs.items():
        arm = name.rsplit("-s", 1)[0]
        a = arms.setdefault(arm, {"runs": 0})
        a["runs"] += 1
        for k, v in r.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool) and "median" not in k and "p95" not in k:
                a[k] = a.get(k, 0) + v
    for a in arms.values():
        a["share_evals_any_public_timeout"] = a["evals_any_public_timeout"] / a["evals"] if a["evals"] else None
        a["share_invalid_timeout_only"] = a["invalid_timeout_only"] / a["evals"] if a["evals"] else None
    (HERE / "timeouts.json").write_text(json.dumps({"limit_s": LIMIT, "arms": arms, "runs": runs}, indent=1))
    for arm, a in arms.items():
        print(arm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in a.items()})


if __name__ == "__main__":
    main()
