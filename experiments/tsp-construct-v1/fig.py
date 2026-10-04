"""Figure: gap to the LKH optimum against time per instance, on MCTS-AHD's test sets.

    python fig.py   # reads summary.json, writes fig_pareto.png

Blue: classical methods run inside the select_next_node interface. Orange: released LLM-designed
heuristics, re-run through the same evaluation loop on the same machine. Dashed line: best published
pure step-by-step gap (literature.md), which has no timing on our machine.
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
CLASSICAL = {"nearest_neighbour": "nearest neighbour", "fi_emit": "farthest insertion (1977)",
             "greedy_ls_emit": "greedy + 2-opt + Or-opt", "lkh_emit": "LKH (emitted)"}
LLM = {"tide_appendix": "TIDE (paper appendix)", "mctsahd_gpt4omini_best": "MCTS-AHD", "hifo_best": "HiFo-Prompt", "reevo_best": "ReEvo",
       "ael_best": "AEL", "refineevo_released": "RefineEvo (released)", "clade_released": "Clade-AHD (released) = NN"}
# label offsets in points and alignment, chosen so labels do not collide
OFF = {"nearest_neighbour": (-8, 2, "right"), "clade_released": (8, 2, "left"), "reevo_best": (-8, -4, "right"),
       "ael_best": (-8, 6, "right"), "refineevo_released": (8, 4, "left"), "mctsahd_gpt4omini_best": (-8, -10, "right"),
       "hifo_best": (8, 4, "left"), "tide_appendix": (8, 4, "left"), "fi_emit": (8, 4, "left"),
       "greedy_ls_emit": (-8, 2, "right"), "lkh_emit": (-8, -2, "right")}
BEST_PUB = {50: ("TIDE", 4.76), 100: ("SimpleEvol", 6.47), 200: ("HiFo-Prompt", 8.877)}
OFF_N = {200: {"tide_appendix": (-8, -24, "right"), "mctsahd_gpt4omini_best": (-8, 0, "right"), "fi_emit": (-8, 7, "right")}}
BEST_DY = {50: -8, 100: -8, 200: -8}


def main():
    S = json.load(open("summary.json"))
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True)
    for ax, n in zip(axes, (50, 100, 200)):
        s = S["sets"].get(f"mctsahd_test{n}")
        if not s:
            continue
        M = s["methods"]
        for names, color, marker in ((CLASSICAL, BLUE, "o"), (LLM, ORANGE, "s")):
            for k, label in names.items():
                if k not in M:
                    continue
                x, y = max(M[k]["sec_per_instance"], 1e-4), M[k]["gap_pct"]
                ax.scatter([x], [y], s=64, color=color, marker=marker, edgecolor="#fcfcfb", linewidth=2, zorder=3)
                note = "" if M[k]["instances"] == s["n_instances"] else f" ({M[k]['instances']})"
                dx, dy, ha = OFF_N.get(n, {}).get(k, OFF.get(k, (6, 4, "left")))
                ax.annotate(label + note, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=8,
                            color=INK, ha=ha, va="center")
        name, g = BEST_PUB[n]
        ax.axhline(g, color=MUTED, linestyle=(0, (4, 3)), linewidth=1.2, zorder=1)
        ax.annotate(f"best published: {name} {g}%", (1e-4, g), xytext=(3, BEST_DY[n]), textcoords="offset points",
                    fontsize=8, color=MUTED, ha="left")
        ax.set_xscale("log")
        ax.set_xlim(1e-4, 3000)
        ax.set_title(f"n = {n} ({s['n_instances']} MCTS-AHD test instances)", fontsize=10, color=INK)
        ax.set_xlabel("median wall seconds per instance (log; loaded shared machine)", fontsize=8, color=MUTED)
        ax.grid(True, color=GRID, linewidth=0.6)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=8, colors=MUTED)
    axes[0].set_ylabel("gap to LKH optimum (%)", fontsize=9, color=INK)
    axes[0].set_ylim(-1, 27)
    h1 = plt.Line2D([], [], marker="o", color=BLUE, linestyle="", label="classical, inside select_next_node")
    h2 = plt.Line2D([], [], marker="s", color=ORANGE, linestyle="", label="released LLM-designed heuristic, re-run")
    h3 = plt.Line2D([], [], color=MUTED, linestyle=(0, (4, 3)), label="best published LLM step-by-step gap")
    fig.legend(handles=[h1, h2, h3], loc="upper center", ncol=3, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig("fig_pareto.png", dpi=160, facecolor="#fcfcfb")
    print("wrote fig_pareto.png")


if __name__ == "__main__":
    main()
