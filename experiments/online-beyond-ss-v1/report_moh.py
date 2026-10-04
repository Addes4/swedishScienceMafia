"""Amendment 1 report: FWSS against the published MoH/HMACE online bin-packing leaderboard.

Usage: python experiments/online-beyond-ss-v1/report_moh.py   (reads results_moh.json; writes tables_moh.md)

Published numbers are transcribed from the PDFs' text:
- MoH, Shi et al., ICLR 2026, arXiv 2505.20881, Table 2 (100 Weibull instances per setting, excess over L1);
- HMACE, Yan et al., arXiv 2605.07214, Table 2. It repeats MoH's rows and adds EoH*, CORAL* and HMACE*
  (GPT-5.4).
Their instances are not public, so ours are new draws from the same generator (see PROTOCOL.md,
Amendment 1).
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
METHODS = ["Best Fit", "First Fit", "FunSearch", "EoH", "ReEvo", "HSEvo", "MCTS-AHD", "MoH", "EoH*", "CORAL*", "HMACE*"]
PUBLISHED = {  # (C, n) -> excess % per METHODS, in order
    (100, 1000): [4.621, 5.038, 3.165, 3.294, 3.475, 3.748, 2.543, 2.553, 3.214, 3.091, 2.595],
    (100, 5000): [4.149, 4.488, 2.165, 0.827, 2.022, 1.088, 1.769, 0.600, 0.801, 0.820, 0.585],
    (100, 10000): [4.030, 4.308, 2.008, 0.436, 1.821, 0.734, 1.647, 0.414, 0.421, 0.558, 0.404],
    (200, 1000): [1.825, 2.025, 0.938, 1.645, 1.825, 1.825, 1.238, 0.848, 1.604, 1.288, 0.819],
    (200, 5000): [1.555, 1.665, 0.543, 0.366, 1.549, 1.555, 1.062, 0.262, 0.379, 0.844, 0.223],
    (200, 10000): [1.489, 1.578, 0.459, 0.188, 1.489, 1.489, 1.036, 0.141, 0.176, 0.748, 0.101],
    (300, 1000): [1.131, 1.265, 0.654, 1.086, 1.131, 1.131, 0.922, 0.581, 1.042, 0.829, 0.600],
    (300, 5000): [0.919, 0.984, 0.352, 0.254, 0.919, 0.919, 0.785, 0.161, 0.243, 0.502, 0.138],
    (300, 10000): [0.882, 0.924, 0.316, 0.115, 0.882, 0.882, 0.765, 0.079, 0.118, 0.440, 0.055],
    (400, 1000): [0.815, 0.835, 0.519, 0.815, 0.815, 0.815, 0.755, 0.498, 0.792, 0.641, 0.488],
    (400, 5000): [0.624, 0.672, 0.275, 0.191, 0.621, 0.624, 0.608, 0.104, 0.183, 0.338, 0.088],
    (400, 10000): [0.603, 0.639, 0.243, 0.098, 0.595, 0.603, 0.579, 0.054, 0.094, 0.301, 0.038],
    (500, 1000): [0.546, 0.522, 0.324, 0.695, 0.546, 0.546, 0.496, 0.373, 0.708, 0.451, 0.379],
    (500, 5000): [0.472, 0.507, 0.214, 0.119, 0.472, 0.472, 0.447, 0.090, 0.111, 0.262, 0.079],
    (500, 10000): [0.448, 0.487, 0.196, 0.075, 0.445, 0.448, 0.430, 0.032, 0.071, 0.219, 0.020],
}
OURS = ["FWSS", "FWSS-no-finish", "SS+finish", "SS", "BF", "FS-W", "FS-OR"]


def excess(rs, p):
    L = sum(r["L1"] for r in rs)
    return 100 * (sum(r["bins"][p] for r in rs) - L) / L


def se_excess(rs, p, reps=2000, seed=20261004):
    rng = np.random.default_rng(seed)
    b = np.array([r["bins"][p] for r in rs], float)
    L = np.array([r["L1"] for r in rs], float)
    idx = rng.integers(0, len(rs), size=(reps, len(rs)))
    return float(np.std(100 * (b[idx].sum(1) - L[idx].sum(1)) / L[idx].sum(1)))


def main():
    data = json.loads((HERE / "results_moh.json").read_text())
    by = {}
    for r in data["instances"]:
        by.setdefault((r["C"], r["n"]), []).append(r)
    lines = ["# Amendment 1: FWSS against the MoH/HMACE online bin-packing leaderboard", "",
             "Excess over L1 (%), lower is better.", "",
             "- Published columns: MoH Table 2 (arXiv 2505.20881) and HMACE Table 2 (arXiv 2605.07214), each "
             "on their own 100 instances per setting.",
             "- Our columns: 100 new instances per setting from the same generator (EoH's), so the two sides "
             "are different draws from one distribution.",
             "- Our best fit (BF) is the calibration row against their Best Fit.",
             "- ± is a bootstrap standard error over instances.",
             "- FWSS knows the item count; FWSS-no-finish does not.", "",
             "| C | n | their BF | our BF | best published (method) | FWSS ± se | FWSS-no-finish | SS | FS-W | calibrated | FWSS < best published | by > 2 se |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    summary, wins, counted, clear_wins = {}, 0, 0, 0
    for (C, n), pub in PUBLISHED.items():
        rs = by.get((C, n))
        if not rs:
            continue
        ours = {p: excess(rs, p) for p in OURS}
        se = se_excess(rs, "FWSS")
        best_i = int(np.argmin(pub[2:])) + 2           # best LLM-designed method
        best_pub = min(pub)
        best_name = METHODS[int(np.argmin(pub))]
        calibrated = abs(ours["BF"] - pub[0]) <= 0.1
        win = ours["FWSS"] < best_pub
        clear = ours["FWSS"] + 2 * se < best_pub    # added after the protocol: margin beyond 2 standard errors
        if calibrated:
            counted += 1
            wins += win
            clear_wins += clear
        summary[f"c{C}_n{n}"] = {"instances": len(rs), "ours": ours, "fwss_se": se, "published": dict(zip(METHODS, pub)),
                                 "best_published": best_pub, "best_published_method": best_name,
                                 "best_llm_method": METHODS[best_i], "calibrated": calibrated, "fwss_below_best_published": win, "fwss_below_by_2se": clear}
        lines.append(f"| {C} | {n} | {pub[0]:.3f} | {ours['BF']:.3f} | {best_pub:.3f} ({best_name}) | **{ours['FWSS']:.3f}** ± {se:.3f} | "
                     f"{ours['FWSS-no-finish']:.3f} | {ours['SS']:.3f} | {ours['FS-W']:.3f} | {'yes' if calibrated else 'NO'} | {'yes' if win else 'no'} | {'yes' if clear else 'no'} |")
    avg_pub = {m: float(np.mean([v[j] for v in PUBLISHED.values()])) for j, m in enumerate(METHODS)}
    avg_ours = {p: float(np.mean([summary[k]["ours"][p] for k in summary])) for p in OURS} if len(summary) == 15 else {}
    lines += ["", f"**FWSS is below the best published number in {wins} of {counted} calibrated settings** "
              f"({len(summary)} settings run). By more than 2 standard errors of our mean (a stricter view added after "
              f"the protocol; it ignores the published numbers' own sampling error): {clear_wins} of {counted}.", ""]
    if avg_ours:
        lines += ["Average over the 15 settings (the leaderboard's 'Average' row):", "",
                  "| Method | average excess (%) |", "|---|---|"]
        for m, v in sorted(list(avg_pub.items()) + [(f"{p} (ours)", v) for p, v in avg_ours.items()], key=lambda x: x[1]):
            lines.append(f"| {m} | {v:.3f} |")
    (HERE / "tables_moh.md").write_text("\n".join(lines) + "\n")
    (HERE / "summary_moh.json").write_text(json.dumps({"wins": wins, "wins_by_2se": clear_wins, "calibrated_settings": counted,
                                                         "settings": summary, "average_published": avg_pub,
                                                         "average_ours": avg_ours}, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
