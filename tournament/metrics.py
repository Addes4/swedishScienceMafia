"""Per-run metrics from the three logs every run writes.

    usage.jsonl   every Anthropic call (and external charge) with the running total spent
    evals.jsonl   every program evaluation: public score, validity, hidden-instance scores
    events.jsonl  arm events; arms that choose their incumbent explicitly log "incumbent" events

The incumbent is the program the arm would submit. Arms that log incumbent events (lean) are
taken at their word; for the others it is the best valid program by public score so far, which
is exactly how ShinkaEvolve and triage pick their best. Spend at an evaluation is the total of
all calls settled before the evaluation finished.
"""
import bisect
import csv
import json
from pathlib import Path


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass  # a line cut short by a hard stop
    return out


class Spend:
    """Cumulative dollars and tokens as step functions of wall-clock time."""

    def __init__(self, usage):
        rows = sorted((r for r in usage if r.get("event") in ("call", "external")), key=lambda r: r["t"])
        self.t, self.usd, self.tokens = [], [], []
        usd = tokens = 0.0
        for r in rows:
            usd += r.get("cost_usd") or 0.0
            tokens += (r.get("input_tokens") or 0) + (r.get("output_tokens") or 0) + \
                (r.get("cache_read_input_tokens") or 0) + (r.get("cache_creation_input_tokens") or 0)
            self.t.append(r["t"])
            self.usd.append(usd)
            self.tokens.append(tokens)

    def at(self, t):
        i = bisect.bisect_right(self.t, t) - 1
        return (self.usd[i], self.tokens[i]) if i >= 0 else (0.0, 0.0)

    @property
    def total(self):
        return (self.usd[-1], self.tokens[-1]) if self.usd else (0.0, 0.0)


def incumbents(evals, events):
    """[(t, score, sha)] each time the incumbent changes."""
    explicit = [e for e in events if e.get("event") == "incumbent"]
    if explicit:
        return [(e["t"], e["score"], e["sha"]) for e in sorted(explicit, key=lambda e: e["t"])]
    out, best = [], None
    for e in sorted(evals, key=lambda e: e["t"]):
        if e["correct"] and not e.get("static_rejected") and (best is None or e["combined"] > best + 1e-9):
            best = e["combined"]
            out.append((e["t"], e["combined"], e["sha"]))
    return out


def area(points, cap, y0):
    """Area under the incumbent score over budget fraction [0, 1] (step function, last value held)."""
    if cap <= 0:
        return None
    total, x_prev, y_prev = 0.0, 0.0, y0
    for usd, y in points:
        x = min(max(usd / cap, 0.0), 1.0)
        total += y_prev * (x - x_prev)
        x_prev, y_prev = x, y
    return total + y_prev * (1.0 - x_prev)


def summarize(run_dir) -> dict:
    run_dir = Path(run_dir)
    job = json.loads((run_dir / "job.json").read_text()) if (run_dir / "job.json").exists() else {}
    usage, evals, events = (load_jsonl(run_dir / n) for n in ("usage.jsonl", "evals.jsonl", "events.jsonl"))
    spend = Spend(usage)
    cap = float(job.get("budget_usd") or 0.0)
    t0 = job.get("started_at") or min([r["t"] for r in usage + evals + events] or [0.0])
    by_sha = {}
    for e in sorted(evals, key=lambda e: e["t"]):
        by_sha[e["sha"]] = e

    inc = incumbents(evals, events)
    curve = []
    for t, score, sha in inc:
        usd, tokens = spend.at(t)
        hidden = by_sha.get(sha, {}).get("hidden_mean")
        curve.append({"spent_usd": round(usd, 6), "budget_frac": round(usd / cap, 6) if cap else None,
                      "tokens": int(tokens), "wall_s": round(t - t0, 1), "incumbent_public": score,
                      "incumbent_hidden": hidden, "sha": sha})
    initial = curve[0] if curve else None
    final = curve[-1] if curve else None
    y0 = initial["incumbent_public"] if initial else 0.0
    auc = area([(c["spent_usd"], c["incumbent_public"]) for c in curve], cap, y0) if curve else None
    improvements = max(len(curve) - 1, 0)
    total_usd, total_tokens = spend.total
    valid = [e for e in evals if e["correct"] and not e.get("static_rejected")]
    best_seen = max(valid, key=lambda e: e["combined"]) if valid else None
    calls = [r for r in usage if r.get("event") == "call"]
    end = next((e for e in reversed(events) if e.get("event") in ("run_end",)), {})
    last_t = max([r["t"] for r in usage + evals + events] or [t0])
    return {
        "job_id": job.get("job_id"), "arm": job.get("arm"), "arm_type": (job.get("arm_config") or {}).get("type"),
        "problem": job.get("problem"), "seed": job.get("seed"), "mock": job.get("mock"),
        "cap_usd": cap, "spent_usd": round(total_usd, 6), "within_cap": total_usd <= cap + 1e-9,
        "tokens": int(total_tokens), "calls": len(calls),
        "failed_calls": sum(1 for r in calls if r.get("error")),
        "refusals": sum(1 for r in usage if r.get("event") == "refused"),
        "stop_reason_counts": _counts(r.get("stop_reason") for r in calls),
        "evals": len(evals), "valid_evals": len(valid),
        "initial_public": y0, "initial_hidden": initial["incumbent_hidden"] if initial else None,
        "final_public": final["incumbent_public"] if final else None,
        "final_hidden": final["incumbent_hidden"] if final else None,
        "final_sha": final["sha"] if final else None,
        "max_public_seen": best_seen["combined"] if best_seen else None,
        "hidden_of_max_public_seen": best_seen.get("hidden_mean") if best_seen else None,
        "improvements": improvements,
        "usd_per_improvement": round(total_usd / improvements, 6) if improvements else None,
        "tokens_per_improvement": int(total_tokens / improvements) if improvements else None,
        "auc": round(auc, 6) if auc is not None else None,
        "auc_gain": round((auc - y0) / (1 - y0), 6) if auc is not None and y0 < 1 else None,
        "flags": sorted({f for e in evals for f in (e.get("flags") or [])}),
        "record_flags": [dict(f, sha=e["sha"]) for e in evals for f in (e.get("record_flags") or [])],
        "wall_s": round(last_t - t0, 1),
        "status": end.get("status"), "arm_result": end.get("arm_result"),
        "curve": curve,
    }


def _counts(values):
    out = {}
    for v in values:
        out[str(v)] = out.get(str(v), 0) + 1
    return out


CURVE_FIELDS = ["spent_usd", "budget_frac", "tokens", "wall_s", "incumbent_public", "incumbent_hidden", "sha"]


def write_curve(summary: dict, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CURVE_FIELDS)
        w.writeheader()
        for row in summary["curve"]:
            w.writerow({k: row.get(k) for k in CURVE_FIELDS})
