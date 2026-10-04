# Independent reviews

Referee-style reviews of finished studies, written by reviewers who did not run them. Each reviewer read
the study on `main`, recomputed its numbers from the saved data, checked protocol adherence and the
claims, and changed no files. The reviews are findings for the study owners to check. They do not change
the studies.

| Review | Study | Verdict | Headline numbers recompute? | Main issues |
|---|---|---|---|---|
| [2026-10-04-online-frontier-v1.md](2026-10-04-online-frontier-v1.md) | [online-frontier-v1](../../experiments/online-frontier-v1/RESULTS.md) | Sound, with issues | Yes, all | "Interface ceiling" claim overreaches; failed pre-registered OR-optimum check not listed as a deviation; an n = 5 interval in the headline. Issue 9, a wrong OR2 optimum in online-beyond-ss-v1, is **fixed** in that study (u250_12 correction) |
| [2026-10-04-overfit-gates-v1.md](2026-10-04-overfit-gates-v1.md) | [overfit-gates-v1](../../experiments/overfit-gates-v1/RESULTS.md) | Sound, with issues | Yes; `analyze.py` reproduces byte-identical outputs | Wrong attribution of tournament-v2's collapse; "1–2 orders of magnitude" mostly comes from how σ was chosen; a run-weighted mean labelled per promotion; veto contrasts rest on 2–3 runs |
| [2026-10-04-tournament-v2.md](2026-10-04-tournament-v2.md) | [tournament-v2](../../experiments/tournament-v2/RESULTS.md) | Sound, with issues | Yes, 0 mismatches | Undisclosed early cancellation of 13 runs, blamed on the wrong cause; which runs are missing depends on the arm; "agrees with tournament-v1" is wrong (the sign reverses); per-problem claims are within noise |
| [2026-10-04-llm-long-search-v1.md](2026-10-04-llm-long-search-v1.md) | [llm-long-search-v1](../../experiments/llm-long-search-v1/RESULTS.md) | Sound, with issues | Yes | The description of the best rule contradicts its own ablation: the three strong runs converged on "exact fill, else leave a gap near 40" (the mean stated in problem.md); the "running histogram" adds at most about 1% of the gain |

All four primary results stand. The issues are in interpretation, disclosure and secondary claims.
