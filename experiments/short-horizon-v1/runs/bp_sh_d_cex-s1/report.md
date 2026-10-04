# Research loop report: bp_sh_d_cex

| | |
|---|---|
| problem | `bp_sh_d_cex` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0814 of a $0.20 hard cap, 150 calls, 287,704 tokens |
| wall time | search 1525 s, baselines 83 s, explain 49 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (150 valid), 3 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9894 | 0.9846 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_d_cex/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_d_cex/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_d_cex/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9894 | 0.9846 | 2 parts removed |

Audit: public 0.9727 → 0.9894 (+0.0168), hidden 0.9634 → 0.9846 (+0.0212); public − hidden gap of the final program 0.0048.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with a two-phase rule: best-fit for items that nearly fill a bin (small lef... |
| 2 | edit | improved | 0.9776 | 0.9776 | $0.0003 | I will switch to a "worst-fit with a twist": instead of always choosing the tightest fit, use a s... |
| 3 | edit | not_better | 0.9725 | 0.9776 | $0.0004 | I'll replace the fixed target-residual rule with a score that preferentially fills bins to near-c... |
| 4 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | I'll replace the fixed-target residual rule with a best-fit rule that picks the bin leaving the s... |
| 5 | edit | not_better | 0.9727 | 0.9776 | $0.0003 | Replace the fixed target with a simple best-fit rule that strongly prefers the smallest non-negat... |
| 6 | edit | not_better | 0.9747 | 0.9776 | $0.0005 | I'll replace the static target-residual rule with an adaptive one that tracks the running mean of... |
| 7 | edit | gate_rejected | 0.9780 | 0.9776 | $0.0005 | I'll make the target residual adaptive: track a running estimate of the item distribution's mean ... |
| 8 | edit | not_better | 0.9770 | 0.9776 | $0.0005 | I'll replace the fixed target residual with a small set of candidate target residuals chosen adap... |
| 9 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the fixed target with a best-fit-plus-residual rule that strongly prefers the tighte... |
| 10 | edit | not_better | 0.9747 | 0.9776 | $0.0005 | I'll make the residual target adaptive by tracking a running mean of past items and targeting a r... |
| 11 | edit | not_better | 0.9747 | 0.9776 | $0.0005 | I'll replace the fixed residual target with a score that combines a strong exact-fit bonus with a... |
| 12 | edit | gate_rejected | 0.9805 | 0.9776 | $0.0006 | I'll keep the target-residual structure but replace the single target with a softly peaked prefer... |
| 13 | edit | not_better | 0.9766 | 0.9776 | $0.0007 | I'll keep the fixed target residual of 30 (which preserves short-stream behavior) but add a small... |
| 14 | edit | not_better | 0.9775 | 0.9776 | $0.0005 | (no description) |
| 15 | edit | not_better | 0.9730 | 0.9776 | $0.0005 | Replace the fixed target residual (which only works well when the item mean is near 40) with a tw... |
| 16 | edit | gate_rejected | 0.9894 | 0.9776 | $0.0008 |  |
| 17 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0005 | I'll exploit the structure of the Weibull-ish mean-40 distribution by giving an exact-fit bonus p... |
| 18 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | I'll make the priority use a Best-Fit-like rule (prefer the smallest remaining capacity that stil... |
| 19 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll switch to a Best-Fit-style rule where the priority is simply the smallest leftover after pla... |
| 20 | edit | gate_rejected | 0.9780 | 0.9776 | $0.0005 | I'll replace the fixed target-residual rule with an adaptive "score gap" approach: after placing ... |
| 21 | edit | not_better | 0.9764 | 0.9776 | $0.0005 | I'll combine the fixed target-residual rule with a Best-Fit tie-break only among bins whose resid... |
| 22 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | I'll replace the hard 1e6/1000 bonuses with a smooth, saturating exact-fit preference (arctan-lik... |
| 23 | edit | not_better | 0.9766 | 0.9776 | $0.0005 | I'll add adaptivity that is safe for short streams: keep the proven target-residual rule but trac... |
| 24 | edit | not_better | 0.9775 | 0.9776 | $0.0005 | Change the fixed target residual from 30 to 35 (closer to the mean item size, improving long-stre... |
| 25 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll use a two-component rule: strongly prefer exact fits, then use a Best-Fit (smallest leftover... |
| 26 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | I will change the target residual to adaptively track the expected leftover after placing a typic... |
| 27 | edit | gate_rejected | 0.9780 | 0.9776 | $0.0006 | I'll make the target residual adaptive and distribution-aware by estimating the mean item size fr... |
| 28 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0005 | I'll replace the fixed target with a two-sided target chosen from the item distribution's structu... |
| 29 | edit | not_better | 0.9747 | 0.9776 | $0.0006 | Keep the exact-fit and near-exact bonuses strong (so short streams are unaffected) but make the r... |
| 30 | edit | gate_rejected | 0.9780 | 0.9776 | $0.0005 | I'll keep the proven target-residual structure but replace the crude fixed bonuses with a cleaner... |
| 31 | edit | not_better | 0.9775 | 0.9776 | $0.0005 | I'll keep the strong exact-fit/near-exact bonuses (essential for the near-perfect short-stream sc... |
| 32 | edit | gate_rejected | 0.9780 | 0.9776 | $0.0005 | I'll replace the fixed target-residual rule with a hybrid that keeps the strong exact/near-exact ... |
| 33 | edit | not_better | 0.9727 | 0.9776 | $0.0006 | I'll add a small adaptive "fill toward 100" term that prefers bins whose remaining capacity is ju... |
| 34 | edit | not_better | 0.9776 | 0.9776 | $0.0006 | Introduce a "next-fit fallback": in addition to the exact/near-exact bonuses and the target-resid... |
| 35 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | Add a Best-Fit tiebreaker among non-exact placements: replace the symmetric target-residual penal... |
| 36 | edit | not_better | 0.9727 | 0.9776 | $0.0006 | Replace the residual-target heuristic with a proper Best-Fit plus a "residual matching" term: pre... |
| 37 | edit | not_better | 0.9759 | 0.9776 | $0.0010 | Keep the exact/fixed-target behavior unchanged for the first many items (so the 519 short streams... |
| 38 | edit | not_better | 0.9721 | 0.9776 | $0.0005 | I'll refine the near-exact bonus threshold (currently 5) and add a slightly wider graduated bonus... |
| 39 | edit | not_better | 0.9773 | 0.9776 | $0.0006 | I'll blend a gentle Best-Fit preference scaled so it only breaks ties among far-from-exact placem... |
| 40 | edit | gate_rejected | 0.9783 | 0.9776 | $0.0005 | I'll add a mild reverse-Best-Fit preference that favors bins leaving a larger leftover among non-... |
| 41 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | I'll replace the fixed target-residual with an adaptive "pairing" rule: track the running mean it... |
| 42 | edit | not_better | 0.9772 | 0.9776 | $0.0006 | I'll make the residual target adaptive: keep it at 30.0 initially, but after a warm-up (so short ... |
| 43 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0007 | I'll replace the fixed residual target with an item-size-aware target: for the current item, pref... |
| 44 | edit | gate_rejected | 0.9814 | 0.9776 | $0.0006 | I'll add a lightweight, state-tracked "pairing score": for each candidate bin, reward placements ... |
| 45 | edit | not_better | 0.9776 | 0.9776 | $0.0005 | I'll replace the hard-coded target of 30 with an adaptive target equal to the running average lef... |
| 46 | edit | not_better | 0.9776 | 0.9776 | $0.0005 | I'll change the tie-breaking logic so that among bins with identical residuals (a common tie situ... |
| 47 | edit | not_better | 0.9769 | 0.9776 | $0.0005 | I'll add a small Best-Fit term (favor the bin with the smallest leftover) with a weight large eno... |
| 48 | edit | not_better | 0.9776 | 0.9776 | $0.0005 | I'll replace the fixed target-residual with a nonlinear residual-cost that rewards leaving a resi... |
| 49 | edit | not_better | 0.9776 | 0.9776 | $0.0005 | I'll add a "best-fit-ish" tie-break that, among bins with equal target-residual cost, prefers the... |
| 50 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the fixed 30.0 target-residual with a weighted combination of two complementary stra... |
| 51 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | Replace the fixed target-residual with a strictly monotone decreasing function of leftover (true ... |
| 52 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | I'll simplify to a pure Best-Fit rule (choose the bin with the smallest leftover, i.e. the fulles... |
| 53 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the pure target-residual cost with a Best-Fit-with-tolerance rule: strongly prefer n... |
| 54 | edit | gate_rejected | 0.9778 | 0.9776 | $0.0006 |  |
| 55 | edit | invalid | 0.0000 | 0.9776 | $0.0005 | Replace the target-residual approximation with a monotone increasing residual penalty (favor larg... |
| 56 | edit | not_better | 0.9766 | 0.9776 | $0.0005 | I'll add an adaptive target residual based on a running mean of past item sizes (kept in module s... |
| 57 | edit | gate_rejected | 0.9789 | 0.9776 | $0.0005 | (no description) |
| 58 | edit | not_better | 0.9752 | 0.9776 | $0.0005 | Replace the fixed target-residual with a two-regime rule: strongly prefer exact/small leftovers (... |
| 59 | edit | not_better | 0.9762 | 0.9776 | $0.0005 | I'll keep the strong exact/near-fit bonuses but replace the fixed target residual with an adaptiv... |
| 60 | edit | not_better | 0.9714 | 0.9776 | $0.0005 | I'll replace the fixed target-residual with a harmonic-mean ("sum" essentially) rule derived from... |
| 61 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll use a Best-Fit rule with a small dominance margin for perfect fits, then add a fractional "w... |
| 62 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the residual-target rule with a robust Best-Fit core (minimize leftover) augmented b... |
| 63 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | I'll replace the fixed residual target with a two-part rule: keep strong exact/tight-fit bonuses,... |
| 64 | edit | not_better | 0.9776 | 0.9776 | $0.0005 | I'll replace the fixed target-residual steer with a tuned quadratic residual penalty that favors ... |
| 65 | edit | not_better | 0.9749 | 0.9776 | $0.0007 | I will make the residual target adaptive to the observed item sizes by tracking a running mean in... |
| 66 | edit | gate_rejected | 0.9781 | 0.9776 | $0.0006 | I'll combine the best-fit residual steering with a small tie-breaking "future-fit" term: keep str... |
| 67 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | I'll replace the ad-hoc bonus scheme with a monotonically-decreasing concave score based on the l... |
| 68 | edit | gate_rejected | 0.9794 | 0.9776 | $0.0005 | I'll make the residual target proportional to the item size (steering toward leaving a residual n... |
| 69 | edit | not_better | 0.9769 | 0.9776 | $0.0005 | I'll replace the fixed residual target with a per-stream adaptive target equal to half the runnin... |
| 70 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the heuristic bonus weights with a cleaner, well-known strong online rule: Best-Fit ... |
| 71 | edit | not_better | 0.9762 | 0.9776 | $0.0007 | I'll keep the successful exact/tight-fit bonus structure but retune the residual target and resha... |
| 72 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the ad-hoc bonuses with a single well-shaped score that strongly prefers near-zero l... |
| 73 | edit | gate_rejected | 0.9830 | 0.9776 | $0.0005 | I will keep the exact/tight-fit bonuses but replace the residual target with a harmonic-style ter... |
| 74 | edit | gate_rejected | 0.9784 | 0.9776 | $0.0006 | I'll keep the strong exact/tight-fit bonuses and replace the residual steer with a term that favo... |
| 75 | edit | not_better | 0.9773 | 0.9776 | $0.0005 | I'll add a small, size-aware second-order steering term that rewards leaving a leftover just unde... |
| 76 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll keep the proven exact/tight-fit bonus structure but replace the residual steer with a linear... |
| 77 | edit | gate_rejected | 0.9797 | 0.9776 | $0.0007 | I'll keep the proven exact/tight-fit bonuses dominant (preserving short-stream behavior) and add ... |
| 78 | edit | not_better | 0.9775 | 0.9776 | $0.0005 | I'll replace the fixed residual target with a Best-Fit-Dominated rule: keep exact/tight-fit bonus... |
| 79 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | I'll replace the fixed-target residual steer with a dynamic exponential-fill rule: strongly prefe... |
| 80 | edit | not_better | 0.9775 | 0.9776 | $0.0006 | I'll blend the proven exact/tight-fit bonuses with a Best-Fit-style penalty scaled so it only mat... |
| 81 | edit | not_better | 0.9725 | 0.9776 | $0.0005 | Replace the absolute-distance-to-target steer with a size-aware "harmonic" score that combines a ... |
| 82 | edit | not_better | 0.9772 | 0.9776 | $0.0005 | I'll add a fractional-usage "sum-of-squares" fill term (Harmonic/FFD-style: prefer bins that afte... |
| 83 | edit | gate_rejected | 0.9784 | 0.9776 | $0.0006 | I'll add a mild "leave room for exactly one more average item" term (prefer leftover ≈ running me... |
| 84 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the fixed target residual with a two-stage rule: keep exact/tight-fit bonuses, but a... |
| 85 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | Replace the residual-target heuristic with a scored Best-Fit variant that keeps exact/tight-fit d... |
| 86 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0006 | Replace the fixed residual target with a dynamic target equal to the running mean item size (so n... |
| 87 | edit | gate_rejected | 0.9781 | 0.9776 | $0.0005 | I'll add a dynamic, size-aware Best-Fit tie-breaker that only activates among bins that receive n... |
| 88 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll keep the proven exact/tight-fit bonuses but replace the target-residual steer with a Best-Fi... |
| 89 | edit | gate_rejected | 0.9890 | 0.9776 | $0.0006 | Switch the fixed target residual to a dynamic target = running mean item size blended with the fi... |
| 90 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the multi-term heuristic with a single clean scoring function that combines a strong... |
| 91 | edit | gate_rejected | 0.9894 | 0.9776 | $0.0005 | I'll replace the fixed target residual with a dynamic target equal to the running mean item size ... |
| 92 | edit | gate_rejected | 0.9797 | 0.9776 | $0.0005 | I'll replace the fixed target with a small mismatch: since best-fit-like variants regressed on th... |
| 93 | edit | gate_rejected | 0.9865 | 0.9776 | $0.0005 | I'll keep the exact/tight-fit bonuses (which preserve the near-perfect short-stream behavior) but... |
| 94 | edit | gate_rejected | 0.9781 | 0.9776 | $0.0005 | I'll stop perturbing the delicate short-stream behavior and instead add a small, strictly seconda... |
| 95 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll keep the exact/tight-fit bonuses intact for short streams, but replace the residual-target s... |
| 96 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | Replace the fixed residual target with a score that prefers the bin with the smallest remaining c... |
| 97 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the fixed-target residual penalty with a score that blends Best-Fit (prefer smallest... |
| 98 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | I will keep the exact/tight-fit bonuses exactly as they are (preserving the near-perfect short-st... |
| 99 | edit | not_better | 0.9721 | 0.9776 | $0.0006 | I'll keep the fixed target residual and the exact/tight-fit bonuses, but scale the target by item... |
| 100 | edit | not_better | 0.9718 | 0.9776 | $0.0005 | I'll make the residual target depend gently on item size — target = 0.5*item (bounded), so large ... |
| 101 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll keep the exact/tight-fit bonuses (crucial for short streams) but replace the mis-tuned fixed... |
| 102 | edit | gate_rejected | 0.9805 | 0.9776 | $0.0005 | I'll replace the fixed residual target with a preference that rewards leaving a leftover matching... |
| 103 | edit | gate_rejected | 0.9894 | 0.9776 | $0.0005 | I'll leave the exact-fit bonus untouched but replace the fixed residual target with a score that ... |
| 104 | edit | gate_rejected | 0.9894 | 0.9776 | $0.0005 | I'll keep the dominant exact/tight-fit bonuses for short streams but replace the fixed residual t... |
| 105 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | I'll replace the fixed target residual with a rule based on minimizing a convex potential: place ... |
| 106 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I will keep the exact-fit and tight-fit bonuses unchanged (they drive the near-perfect behavior o... |
| 107 | edit | gate_rejected | 0.9891 | 0.9776 | $0.0005 | Short streams need near-perfect fill, but long streams need good pairing; I'll keep the exact/tig... |
| 108 | edit | not_better | 0.9718 | 0.9776 | $0.0005 | I'll replace the fixed residual target with a target equal to half the item's own size (so an ite... |
| 109 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll keep the exact-fit and tight-fit bonuses unchanged, but replace the fixed residual target wi... |
| 110 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0006 | Keep the exact-fit and tight-fit bonuses and the residual structure byte-identical, but set the t... |
| 111 | edit | not_better | 0.9764 | 0.9776 | $0.0005 | I'll make the tight-fit bonus saturate more gently and widen its reach (so any moderately small l... |
| 112 | edit | not_better | 0.6968 | 0.9776 | $0.0005 | I'll replace the residual-steering term with a "worst-fit"-style rule that, once the exact/tight-... |
| 113 | edit | not_better | 0.9727 | 0.9776 | $0.0008 | I'll switch the residual-steering term to a monotone preference for the smallest leftover (pure "... |
| 114 | edit | gate_rejected | 0.9904 | 0.9776 | $0.0005 | I'll replace the exact-fit bonus with a probabilistic "dot-product" scoring learned online: track... |
| 115 | edit | not_better | 0.9718 | 0.9776 | $0.0005 | I'll keep the short-stream behavior byte-identical by retaining the exact/tight-fit bonuses, but ... |
| 116 | edit | gate_rejected | 0.9881 | 0.9776 | $0.0006 | I'll add a small learned "pair-fit" term: besides the exact-fit and tight-fit bonuses, reward bin... |
| 117 | edit | gate_rejected | 0.9898 | 0.9776 | $0.0021 | I'll keep the exact-fit, tight-fit bonuses and the target-30 residual term byte-identical (so sho... |
| 118 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I will keep the exact-fit and tight-fit bonuses unchanged, and replace the fixed-target residual ... |
| 119 | edit | gate_rejected | 0.9794 | 0.9776 | $0.0005 | I'll keep the exact-fit and tight-fit bonuses (so short streams stay perfect) and replace the fix... |
| 120 | edit | not_better | 0.9733 | 0.9776 | $0.0006 | Keep the exact-fit and tight-fit bonuses byte-identical (preserving perfect short-stream behavior... |
| 121 | edit | not_better | 0.9718 | 0.9776 | $0.0005 | I'll replace the fixed residual target term with a smooth mix of "smallest non-zero leftover" (be... |
| 122 | edit | not_better | 0.9749 | 0.9776 | $0.0006 | I'll keep the exact-fit and tight-fit bonuses byte-identical (preserving instance-3 behavior) and... |
| 123 | edit | not_better | 0.9770 | 0.9776 | $0.0008 | Keep the exact-fit bonus but narrow the tight-fit window from 5 to 2 and reduce its magnitude (fr... |
| 124 | edit | gate_rejected | 0.9885 | 0.9776 | $0.0005 | Keep the exact-fit and tight-fit bonuses byte-identical (preserving instance-3 perfect behavior),... |
| 125 | edit | not_better | 0.9766 | 0.9776 | $0.0006 | I'll keep the exact-fit and tight-fit bonuses byte-identical (preserving instance-3 near-perfect ... |
| 126 | edit | not_better | 0.9718 | 0.9776 | $0.0005 | I'll keep the exact-fit bonus and replace the fixed target-30 residual term with a best-fit term ... |
| 127 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0005 | I'll keep the exact-fit and tight-fit bonuses byte-identical (preserving short-stream behavior), ... |
| 128 | edit | not_better | 0.9718 | 0.9776 | $0.0005 | I'll introduce a small, self-normalizing best-fit tiebreaker: keep the exact-fit and tight-fit bo... |
| 129 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll replace the fixed target-30 residual term with a scale-aware "waste" penalty: prefer the bin... |
| 130 | edit | not_better | 0.9701 | 0.9776 | $0.0005 | I'll keep exact-fit and tight-fit bonuses unchanged, and replace the fixed target-30 residual ter... |
| 131 | edit | not_better | 0.9727 | 0.9776 | $0.0004 | Replace the fixed target-30 residual with a best-fit rule (prefer smallest leftover after placeme... |
| 132 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0005 | I'll keep the exact-fit and tight-fit bonuses byte-identical (preserving the perfect short-stream... |
| 133 | edit | not_better | 0.9727 | 0.9776 | $0.0005 | I'll keep the exact-fit and tight-fit bonuses byte-identical (preserving short-stream behavior) a... |
| 134 | edit | gate_rejected | 0.9898 | 0.9776 | $0.0005 | I'll replace the fixed target-residual term with a "leave-a-slot" rule: still keep the exact-fit ... |
| 135 | edit | not_better | 0.9776 | 0.9776 | $0.0005 | I'll add a small score bonus for bins that leave a leftover just below the item size (a tight-fit... |
| 136 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0007 | Replace the fixed target-30 with a target residual equal to the Weibull mean item size (~40), so ... |
| 137 | edit | not_better | 0.9728 | 0.9776 | $0.0005 | I'll replace the fixed target-residual penalty with a two-regime rule that keeps the exact/tight ... |
| 138 | edit | not_better | 0.9481 | 0.9776 | $0.0006 | I keep the exact-fit and tight-fit bonuses byte-identical (preserving instance 3), but replace th... |
| 139 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0010 | Keep the exact-fit and tight-fit bonuses byte-identical, and make the target residual adaptive on... |
| 140 | edit | not_better | 0.9596 | 0.9776 | $0.0006 | I'll keep the exact-fit and tight-fit bonuses byte-identical, but replace the fixed target-30 res... |
| 141 | edit | not_better | 0.9775 | 0.9776 | $0.0005 | I'll add a small randomized tie-breaking / exploration term based on the bin's leftover position ... |
| 142 | edit | not_better | 0.9727 | 0.9776 | $0.0008 | Replace the `- \|leftover - 30\|` term with a pure best-fit term `-leftover`, keeping exact-fit a... |
| 143 | edit | gate_rejected | 0.9893 | 0.9776 | $0.0005 | I'll replace the target-residual penalty with a proper "best-fit-decreasing-style" rule: strongly... |
| 144 | edit | improved | 0.9891 | 0.9891 | $0.0007 | Keep exact/tight bonuses byte-identical, and raise the target residual from 30 to a distribution-... |
| 145 | edit | improved | 0.9894 | 0.9894 | $0.0005 | I'll replace the fixed target residual with an adaptive target that tracks the running mean of it... |
| 146 | edit | not_better | 0.9888 | 0.9894 | $0.0006 | I will replace the two flat exact/tight bonuses with a smoother monotone residual penalty that al... |
| 147 | edit | not_better | 0.9780 | 0.9894 | $0.0006 | Replace the adaptive target (running mean) with a shrunk adaptive target: after warmup use k * ru... |
| 148 | edit | not_better | 0.9883 | 0.9894 | $0.0007 | Replace the target-residual penalty with a hybrid rule: exact fits get a huge bonus; otherwise st... |
| 149 | edit | not_better | 0.9894 | 0.9894 | $0.0006 | I'll refine the residual steering so that after warmup the target is the running mean item size b... |
| 150 | edit | not_better | 0.9883 | 0.9894 | $0.0006 | The current rule uses a symmetric target-residual penalty, which wastes space by treating too-lar... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,33 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Target-residual fit: prefer bins whose leftover after placement is closest to a running mean."""
 import numpy as np
+
+_TARGET_SHORT = 30.0
+_WARMUP = 35
+
+_count = 0
+_sum = 0.0
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
+    global _count, _sum
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    leftover = bins - item
+
+    # Adapt the target residual to the running mean item size; fall back to a fixed
+    # short-stream target until enough items have been observed.
+    if _count < _WARMUP:
+        target = _TARGET_SHORT
+    else:
+        target = _sum / _count
+
+    _count += 1
+    _sum += item
+
+    # Strongly reward near-perfect fits (small leftovers), otherwise steer toward the target residual.
+    exact_bonus = np.where(leftover == 0, 1e6, 0.0)
+    tight_bonus = np.maximum(0.0, 5.0 - leftover) * 1000.0
+    return exact_bonus + tight_bonus - np.abs(leftover - target)
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (14 parts, 28 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 14 | `global _count, _sum` | -0.9894 | essential: the program fails or turns invalid without it |
| 16 | `leftover = bins - item` | -0.9894 | essential: the program fails or turns invalid without it |
| 16 | `term + bins` | -0.9894 | essential: the program fails or turns invalid without it |
| 20 | `if _count < _WARMUP: ...` | -0.9894 | essential: the program fails or turns invalid without it |
| 21 | `target = _TARGET_SHORT` | -0.9894 | essential: the program fails or turns invalid without it |
| 30 | `tight_bonus = np.maximum(0.0, 5.0 - leftover) * 1000.0` | -0.9894 | essential: the program fails or turns invalid without it |
| 23 | `target = _sum / _count` | -0.6561 | matters |
| 16 | `term - item` | -0.0530 | matters |
| 26 | `_sum += item` | -0.0168 | matters |
| 31 | `term - np.abs(leftover - target)` | -0.0155 | matters |
| 25 | `_count += 1` | -0.0118 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 29: `exact_bonus = np.where(leftover == 0, 1000000.0, 0.0)`
- line 31: `term + exact_bonus`

**REPAIRED (not an explanation)**: removing these raises the public score by more than the tolerance. The found program is worse than a simpler one; these are repairs, not parts of an explanation.

- line 31: `term + tight_bonus` (Δ +0.0061)

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9894 | 0.9846 |
| minimal (2 parts removed) | 0.9894 | 0.9846 |

Minimal program:

```python
"""Target-residual fit: prefer bins whose leftover after placement is closest to a running mean."""
import numpy as np
_TARGET_SHORT = 30.0
_WARMUP = 35
_count = 0
_sum = 0.0

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _count, _sum
    leftover = bins - item
    if _count < _WARMUP:
        target = _TARGET_SHORT
    else:
        target = _sum / _count
    _count += 1
    _sum += item
    tight_bonus = np.maximum(0.0, 5.0 - leftover) * 1000.0
    return tight_bonus - np.abs(leftover - target)
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_d_cex --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 1
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_d_cex-s1   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_d_cex/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_d_cex/initial.py` `609927c5ea619a94`
- `problems/bp_sh_d_cex/problem.md` `190017a698e23cd8`
- `problems/bp_sh_d_cex/suite.json` `c10c239f751ffc5f`
- `problems/bp_sh_d_cex/verify.py` `12d8663a195dbe46`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
