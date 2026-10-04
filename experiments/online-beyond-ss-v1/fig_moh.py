"""Figure: the MoH/HMACE leaderboard's average excess over 15 settings, with our policies added.

Usage: python experiments/online-beyond-ss-v1/fig_moh.py   (reads summary_moh.json; writes fig_leaderboard.png)
Published methods are on their own instances; ours are new draws from the same generator (PROTOCOL.md, Amendment 1).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
OURS = {"FWSS": "FWSS (ours, knows item count)", "SS": "Sum-of-Squares, 2006 (no LLM)",
        "FWSS-no-finish": "FWSS without finish (horizon-free)"}
BLUE, AQUA, GRAY, INK, MUTED, GRID, SURFACE = "#2a78d6", "#1baf7a", "#a3a29d", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def main():
    s = json.loads((HERE / "summary_moh.json").read_text())
    rows = [(m, v, "pub") for m, v in s["average_published"].items()]
    rows += [(OURS[k], s["average_ours"][k], "ours") for k in OURS]
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for i, (name, v, kind) in enumerate(rows):
        color = BLUE if name.startswith("FWSS (ours") else (AQUA if kind == "ours" else GRAY)
        ax.barh(i, v, height=0.62, color=color)
        ax.annotate(f"{v:.3f}%", (v, i), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("average excess over L1 across 15 settings (capacity 100–500 × 1k/5k/10k items), %", fontsize=8, color=MUTED)
    ax.set_title("Online bin packing: MoH/HMACE leaderboard plus classical policies", loc="left", fontsize=10, color=INK)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    fig.text(0.01, 0.01, "Gray: published LLM-designed and classic rows (their 100 instances per setting). Blue/green: ours, "
             "100 new instances per setting from the same generator.", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(HERE / "fig_leaderboard.png", facecolor=SURFACE)
    print("wrote fig_leaderboard.png")


if __name__ == "__main__":
    main()
