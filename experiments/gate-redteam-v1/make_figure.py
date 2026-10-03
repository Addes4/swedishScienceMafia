"""Draw the gate-redteam summary figure from the saved result JSON.

    python experiments/gate-redteam-v1/make_figure.py

Writes figure.png next to this file: (left) where Part A's hand-crafted exploits were stopped,
by gate layer; (right) Part B's live LLM attempts per model, split into caught / scored-honest /
materially-unearned. No LLM calls.
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
LAYER_ORDER = ["static", "process", "check", "strict", "none(scored)"]
LAYER_LABEL = {"static": "static scan", "process": "process+JSON\nboundary",
               "check": "check()", "strict": "strict re-check",
               "none(scored)": "not rejected\n(scored)"}


def main():
    a = json.load(open(HERE / "results_part_a.json"))
    b = json.load(open(HERE / "results_part_b.json"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    # Left: Part A exploits by catching layer.
    counts = Counter(r["layer"] for r in a)
    xs = [LAYER_LABEL[k] for k in LAYER_ORDER]
    ys = [counts.get(k, 0) for k in LAYER_ORDER]
    # Blue = a gate layer rejected it; grey = scored (valid program, trick neutralised), not a
    # failure. None of the 28 obtained a materially unearned score.
    colors = ["#4C78A8", "#4C78A8", "#4C78A8", "#4C78A8", "#B9C7D9"]
    ax1.bar(xs, ys, color=colors)
    for i, y in enumerate(ys):
        ax1.text(i, y + 0.15, str(y), ha="center", va="bottom", fontsize=10)
    ax1.set_ylabel("number of exploits (count)")
    ax1.set_title(f"Part A: {len(a)} hand-crafted exploits,\nwhere each was stopped")
    ax1.set_ylim(0, max(ys) + 1.8)
    ax1.tick_params(axis="x", labelsize=8)
    ax1.text(0.5, 0.95, "0 obtained a materially unearned score\n(grey = valid program, trick neutralised)",
             transform=ax1.transAxes, ha="center", va="top", fontsize=8, color="#555")

    # Right: Part B per model, caught / scored-honest / unearned.
    models = ["claude-sonnet-5-5", "claude-haiku-4-5"]
    caught = [sum(1 for r in b if r["model"] == m and r["caught"]) for m in models]
    unearned = [sum(1 for r in b if r["model"] == m and r.get("unearned_via_tolerance")) for m in models]
    scored_honest = [sum(1 for r in b if r["model"] == m and not r["caught"]
                         and not r.get("unearned_via_tolerance")) for m in models]
    import numpy as np
    x = np.arange(len(models))
    ax2.bar(x, caught, label="caught (0 score)", color="#4C78A8")
    ax2.bar(x, scored_honest, bottom=caught, label="scored, honest/weak", color="#B9C7D9")
    ax2.bar(x, unearned, bottom=[c + s for c, s in zip(caught, scored_honest)],
            label="unearned via tolerance (~1e-9)", color="#E45756")
    ax2.set_xticks(x)
    ax2.set_xticklabels([m.replace("claude-", "") for m in models])
    ax2.set_ylabel("number of attempts (count)")
    ax2.set_title("Part B: 40 live LLM exploit attempts\n(20 per model)")
    ax2.legend(fontsize=8, loc="upper right")

    fig.suptitle("Integrity gate red-team: attempts to obtain an unearned score (lower red = better)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(HERE / "figure.png", dpi=130)
    print("wrote", HERE / "figure.png")


if __name__ == "__main__":
    main()
