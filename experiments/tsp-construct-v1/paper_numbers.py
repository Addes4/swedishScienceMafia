"""Write the paper's numbers that depend on the slow runs (numbers.tex) from summary.json.

    python paper_numbers.py <output .tex path>
"""
import json
import sys

from analyze import ensure_results

ensure_results()

S = json.load(open("summary.json"))
M = {n: S["sets"][f"mctsahd_test{n}"]["methods"] for n in (50, 100, 200)}
H = S.get("hypotheses", {})


def cell(n, h, digits=2):
    m = M[n].get(h)
    if not m:
        return "pending", "--", "--"
    sec = m["sec_per_instance"]
    s = f"{sec:.2g}" if sec < 10 else f"{sec:.0f}"
    return f"{m['gap_pct']:.{digits}f}", s, str(m["instances"])


out = []
for macro, (n, h) in {"Tide": (200, "tide_appendix"), "Mcts": (200, "mctsahd_gpt4omini_best"),
                      "Hifo": (200, "hifo_best"), "HifoH": (100, "hifo_best")}.items():
    g, s, k = cell(n, h)
    base = macro if macro != "HifoH" else "Hifo"
    suf = "" if macro != "HifoH" else "H"
    out += [f"\\newcommand{{\\{base}Gap{suf}}}{{{g}}}", f"\\newcommand{{\\{base}Sec{suf}}}{{{s}}}",
            f"\\newcommand{{\\{base}N{suf}}}{{{k}}}"]

# H2 sentence
pre = ["mctsahd_gpt4omini_best", "hifo_best", "reevo_best", "ael_best", "refineevo_released"]
names = {"mctsahd_gpt4omini_best": "MCTS-AHD", "hifo_best": "HiFo-Prompt", "reevo_best": "ReEvo", "ael_best": "AEL",
         "refineevo_released": "RefineEvo's file"}
ok, missing = [], []
for h in pre:
    vals = [H.get(str(n), H.get(n, {})).get("H2", {}).get(h) for n in (50, 100, 200)]
    if all(v and v["holds"] for v in vals):
        ok.append(names[h])
    else:
        missing.append(names[h])
if not missing:
    h2 = ("For each of MCTS-AHD, HiFo-Prompt, ReEvo, AEL and RefineEvo's file, at every size, an interface method "
          "has shorter tours (paired 95\\% CI below zero) and no larger time per instance, so the pre-registered "
          "H2, which covers all six released files, fails only because of Clade-AHD's.")
else:
    h2 = (f"For {', '.join(ok)}, at every size, an interface method has shorter tours (paired 95\\% CI below zero) "
          f"and no larger time per instance; for {', '.join(missing)} this does not hold at every size (see the repository).")
out.append(f"\\newcommand{{\\HtwoSentence}}{{{h2}}}")
h4 = H.get("H4", {})
same = sum(1 for v in h4.values() if v["same"])
out.append("\\newcommand{\\HfourSentence}{On fresh instances from our own seeds (1,000 / 1,000 / 200), "
           f"{same} of {len(h4)} pre-registered paired comparisons keep their sign (six of them are exact ties between nearest neighbour and Clade-AHD's file).}}")
NC = json.load(open("results/nocache_summary.json"))
g = [NC[f"greedy_ls_emit_test{n}"]["uncached_median_sec"] for n in (50, 100, 200)]
out.append(f"\\newcommand{{\\NoCacheAbstract}}{{{g[0]:.2f}--{g[2]:.1f}\\,s per instance, still faster than every rollout-based LLM heuristic}}")
out.append("\\newcommand{\\NoCacheHtwo}{Greedy + 2-opt + Or-opt's times use a per-instance cache of its plan. Without it the tours are identical "
           f"and it takes {g[0]:.2f} / {g[1]:.1f} / {g[2]:.1f}\\,s per instance, still faster than MCTS-AHD, HiFo-Prompt and TIDE. "
           "The dominance over MCTS-AHD, HiFo-Prompt and RefineEvo's file also holds through farthest insertion, which has no cache. "
           "ReEvo and AEL, however, are faster than any uncached method we ran that beats them, so for those two the dominance relies on the cache.}")
out.append(f"\\newcommand{{\\NoCacheRow}}{{{g[0]:.2f}}}")
out.append(f"\\newcommand{{\\NoCacheRowH}}{{{g[1]:.1f}}}")
out.append(f"\\newcommand{{\\NoCacheRowT}}{{{g[2]:.1f}}}")
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("\n".join(out))
