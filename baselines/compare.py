"""Compare arms of an equal-budget benchmark: the best value per instance for each arm, as a markdown table.

    python baselines/compare.py runs/bench6-mosa runs/bench6-oneshot runs/bench6-basin baselines/out/bench6-coding-agent

An arm is a Mosa workspace (its notebook's results) or a coding-agent directory (its verified report.json). Lower is
better. The best value for each instance is in bold; the last row counts how often each arm was best (ties count for
every arm that reached the best value within 1e-9 relative).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mosa.store import Notebook


def arm(path):
    """(label, {n: best value}, runs, budget note) for one arm."""
    path = Path(path)
    if (path/"report.json").exists():
        report = json.loads((path/"report.json").read_text())
        best = {int(n): v["value"] for n, v in report["sizes"].items() if v.get("valid")}
        used = {int(n): v["relax_calls"] for n, v in report["sizes"].items()}
        return "Plain coding agent", best, f"relax calls used: {', '.join(f'{u}' for u in used.values())}"
    events = Notebook(path).read()
    name = next((e["name"] for e in reversed(events) if e["type"] == "name"), None) \
        or next((e.get("name") for e in events if e["type"] == "lab"), path.name) or path.name
    best, runs = {}, 0
    for e in events:
        if e["type"] == "result" and not e.get("error") and e.get("polished") is not None:
            runs += 1
            best[e["n"]] = min(best.get(e["n"], float("inf")), e["polished"])
    return name.split(": ", 1)[-1], best, f"{runs} runs"


def main(paths):
    arms = [arm(p) for p in paths]
    sizes = sorted({n for _, best, _ in arms for n in best})
    wins = [0]*len(arms)
    rows = []
    for n in sizes:
        values = [best.get(n) for _, best, _ in arms]
        top = min(v for v in values if v is not None)
        cells = []
        for k, v in enumerate(values):
            if v is None:
                cells.append("—")
            elif abs(v-top) <= 1e-9*max(1., abs(top)):
                wins[k] += 1
                cells.append(f"**{v:.6f}**")
            else:
                cells.append(f"{v:.6f} (+{v-top:.3g})")
        rows.append(f"| {n} | " + " | ".join(cells) + " |")
    print("| n | " + " | ".join(label for label, _, _ in arms) + " |")
    print("|---|" + "---|"*len(arms))
    print("\n".join(rows))
    print("| best on | " + " | ".join(f"{w} of {len(sizes)}" for w in wins) + " |")
    print("\n" + "; ".join(f"{label}: {note}" for label, _, note in arms))


if __name__ == "__main__":
    main(sys.argv[1:])
