"""Figure: mean bins above the proved optimum against the number of items (fresh Weibull sets, C = 100).

Usage: python experiments/online-beyond-ss-v1/fig.py   (reads summary.json; writes fig_bins_above_opt.png)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
SETS = [("fresh_w1k", 1000), ("fresh_w5k", 5000), ("fresh_w10k", 10000), ("fresh_w100k", 100000)]
# Reference palette slots 1-4 (validated: dataviz validate_palette.js, light mode, all checks pass;
# two slots sit below 3:1 contrast, so every line is direct-labelled and tables.md holds the numbers).
SERIES = [("FWSS", "FWSS (ours, knows item count)", "#2a78d6", "o"),
          ("FWSS-no-finish", "FWSS without the finish (horizon-free)", "#eb6834", "s"),
          ("SS", "Sum-of-Squares (Csirik et al. 2006)", "#1baf7a", "D"),
          ("FS-W", "FunSearch's Weibull heuristic", "#eda100", "^")]
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def main():
    s = json.loads((HERE / "summary.json").read_text())["sets"]
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    xs = [n for name, n in SETS if name in s]
    ends = []
    for key, label, color, marker in SERIES:
        ys = [s[name]["bins_above_OPT"][key] for name, _ in SETS if name in s]
        ax.plot(xs, ys, color=color, lw=2, marker=marker, ms=7, markeredgecolor=SURFACE, markeredgewidth=1.5, label=label)
        ends.append([ys[-1], ys[-1]])
    order = sorted(range(len(ends)), key=lambda i: ends[i][0])   # nudge end labels apart (min 0.7 bins)
    for a, b in zip(order, order[1:]):
        if ends[b][1] - ends[a][1] < 0.7:
            ends[b][1] = ends[a][1] + 0.7
    for (v, ypos) in ends:
        ax.annotate(f"{v:.1f}", (xs[-1], ypos), xytext=(8, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
    ax.axhline(0, color=MUTED, lw=1, ls="--")
    ax.annotate("offline optimum", (xs[0], 0), xytext=(0, 4), textcoords="offset points", fontsize=8, color=MUTED)
    ax.set_xscale("log")
    ax.minorticks_off()
    ax.set_ylim(-0.8, 16)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{n // 1000}k" for n in xs])
    ax.set_xlim(xs[0] * 0.8, xs[-1] * 1.6)
    ax.set_xlabel("items per instance (Weibull(45, 3), capacity 100)", color=MUTED, fontsize=9)
    ax.set_ylabel("mean bins above the proved optimum", color=MUTED, fontsize=9)
    ax.set_title("Online bin packing: waste above the optimum", loc="left", fontsize=11, color=INK)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.legend(frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(0.02, 0.42), labelcolor=INK)
    counts = ", ".join(f"{s[name]['opt_proved']}" for name, _ in SETS if name in s)
    fig.text(0.01, 0.01, f"Fresh instances, seeds 98000–98459; optimum proved by arc flow on {counts} instances. "
             "Best fit (18–1,486 bins above) is off the scale.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(HERE / "fig_bins_above_opt.png", facecolor=SURFACE)
    print("wrote fig_bins_above_opt.png")


if __name__ == "__main__":
    main()
