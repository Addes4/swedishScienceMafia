# Research loop report: bp_sh_e_rand

| | |
|---|---|
| problem | `bp_sh_e_rand` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0836 of a $0.20 hard cap, 150 calls, 292,071 tokens |
| wall time | search 1293 s, baselines 50 s, explain 9 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (148 valid), 1 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9728 | 0.9634 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_e_rand/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_e_rand/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_e_rand/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9727 | 0.9634 | 3 parts removed |

Audit: public 0.9727 → 0.9728 (+0.0002), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program 0.0094.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0003 | The pure best-fit rule wastes leftover space: I'll switch to a hybrid that first prefers an exact... |
| 2 | edit | not_better | 0.5985 | 0.9727 | $0.0003 | Replace pure best-fit with a "least-loaded that still fits" heuristic (worst fit among bins with ... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Implement a best-fit variant that breaks near-ties by preferring bins whose residual after placin... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll implement a "best fit with sum-of-squares residual" scoring: instead of minimizing the post-... |
| 5 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll use a "best fit with a bounded lookahead guard" by preferring the bin that leaves the smalle... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace best-fit with a "best-fit-decreasing-like" rule that is robust online: prefer the *f... |
| 7 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit-decreasing-aware" rule using a learned decrementing... |
| 8 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "best fit but avoid stranding small residuals" rule: primary score still prefers... |
| 9 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll keep the best-fit core but replace its residual ordering with a "waste-aware" score derived ... |
| 10 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best fit with a residual-aware rule that still prefers near-tight fits but penalizes... |
| 11 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure best-fit score with a "best fit + least-loaded-descending hybrid": use best... |
| 12 | edit | not_better | 0.9365 | 0.9727 | $0.0005 | I'll replace best-fit with a proportional "fill-ratio matching" rule: score bins by how close the... |
| 13 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Switch to an "almost best fit" rule that uses best-fit among bins with large residual but prefers... |
| 14 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll refine the pure best-fit rule to also prefer packing into already-used bins when residual is... |
| 15 | edit | not_better | 0.9541 | 0.9727 | $0.0005 | I'll replace the exact best-fit with a "best fit among bins that stay usable" tie-aware rule: pre... |
| 16 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best fit is already near-optimal for this distribution; a known improvement for online packing is... |
| 17 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "least-loaded + best-fit hybrid" that keeps one or two bins n... |
| 18 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Use a harmonic/order-statistic-aware variant of best fit: rank by best fit, but add a small bonus... |
| 19 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | Online bin packing improves when the rule explicitly tries to create residual gaps that future it... |
| 20 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try the classic online bin-packing improvement for best-fit: a "best fit with a lookahead-fr... |
| 21 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The pure best-fit rule already dominates; the main remaining loss is stranded capacity from large... |
| 22 | edit | not_better | 0.9543 | 0.9727 | $0.0008 | Add an adaptive "usability threshold" to best fit: from running statistics of past items, treat r... |
| 23 | edit | invalid | 0.0000 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "shelf-aware best fit" that reserves a small fraction of bins a... |
| 24 | edit | improved | 0.9728 | 0.9728 | $0.0005 | Replace pure best-fit with a "residual-quality" score: penalize residuals that are too small to b... |
| 25 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the fixed tiny-residual penalty with an adaptive one: track the smallest item size seen s... |
| 26 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the fixed tiny-residual penalty with a distribution-aware piecewise penalty that strongly... |
| 27 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the fixed penalty with an adaptive "waste-avoidance" rule: track the running mean it... |
| 28 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll extend best-fit into a "best-fit-decreasing-like" improvement using an adaptive threshold: t... |
| 29 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | The pure best-fit rule is essentially optimal here, and prior tweaks that add penalties only hurt... |
| 30 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace best-fit with a hybrid: primary preference for the tightest fit, but among bins whose res... |
| 31 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I will replace best-fit with a "best-fit with waste-aware tiebreak scaled to item size": keep tig... |
| 32 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Add a light "residual-value" tiebreaker that estimates whether the leftover capacity can actually... |
| 33 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Use a best-fit score with an added tiebreak that prefers placing items into already-used (fuller)... |
| 34 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I will switch from pure best-fit to "best-fit with a one-step lookahead" by tracking, online, how... |
| 35 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll improve on pure best-fit by adding a bounded "waste" term: penalize residuals that are too s... |
| 36 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll try a genuinely different rule: instead of best-fit, use a "worst-fit among sufficiently tig... |
| 37 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | The prior attempts all made tiny perturbations of best-fit (essentially pure best-fit wins on thi... |
| 38 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Introduce a genuinely different rule based on "fullness momentum": score bins by favoring the tig... |
| 39 | edit | not_better | 0.5985 | 0.9728 | $0.0005 | Previous attempts all tweaked a pure best-fit key in ways that did not beat the strong baseline. ... |
| 40 | edit | gate_rejected | 0.9728 | 0.9728 | $0.0005 | Replace the near-tie heuristic with a principled aging scheme: among bins whose residual is withi... |
| 41 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the fixed tiny-residual penalty with an adaptive one that penalizes any residual sma... |
| 42 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the pure best-fit rule with the classic "Best Fit Decreasing–style" improvement for ... |
| 43 | edit | gate_rejected | 0.9728 | 0.9728 | $0.0005 | Replace the heuristic with a stateful rule combining best-fit with a learned cutoff: track the sm... |
| 44 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll add a size-class-aware strict best-fit tiebreak: keep pure best-fit as the primary key, but ... |
| 45 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Pure best-fit is already near-optimal, so I will add only a tie-break on exactly equal residuals:... |
| 46 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll try a stateful "greedy exact-fit tracking" combined with best-fit: keep pure best-fit as the... |
| 47 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll refine the tiny-residual penalty to be continuous and to also mildly reward residuals that e... |
| 48 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll make the residual penalty adapt to the item-size distribution by tracking the empirical item... |
| 49 | edit | not_better | 0.9728 | 0.9728 | $0.0005 | I'll add a small stateful tie-break that, among equal best-fit residuals, prefers the bin whose p... |
| 50 | edit | not_better | 0.6839 | 0.9728 | $0.0005 | I'll switch to a "worst-fit with best-fit fallback on exact fills" style rule used in online pack... |
| 51 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the heuristic with a "Best-Fit plus smallest-residual-that-is-still-usable" rule: after c... |
| 52 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will replace the fixed tiny-residual penalty with a score that prefers the best fit but breaks ... |
| 53 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the heuristic with a tunable "best-fit with adaptive small-residual penalty", but cr... |
| 54 | edit | not_better | 0.9713 | 0.9728 | $0.0005 | I'll replace the fixed tiny-residual penalty with a rule that scores bins by best-fit but adds a ... |
| 55 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll strengthen the small-residual penalty by making it a graded, steeper penalty over residuals ... |
| 56 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll add a stateful, distribution-aware tweak: track the observed maximum item size seen so far, ... |
| 57 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll switch from a fine-grained residual penalty to a coarser strategy that keeps best-fit as the... |
| 58 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll add a stateful, distribution-aware improvement to the tiny-residual penalty: track the empir... |
| 59 | edit | not_better | 0.9695 | 0.9728 | $0.0006 | Replace the heuristic with a proper "best fit decreasing-like" rule is impossible online, so inst... |
| 60 | edit | invalid | 0.0000 | 0.9728 | $0.0005 | I'll add a stateful rule that tracks the recent empirical distribution of item sizes and gives a ... |
| 61 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll make the small-residual penalty stateful and adaptive: track the empirical minimum positive ... |
| 62 | edit | not_better | 0.9728 | 0.9728 | $0.0005 | Replace the pure best-fit rule (which tends to strand tiny gaps) with an "almost-worst-fit plus e... |
| 63 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will replace the fixed best-fit tie with a scaled best-fit that adds a small bonus for leaving ... |
| 64 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the tiny-residual penalty with the classic "match" rule from the MBS'/Harmonic famil... |
| 65 | edit | gate_rejected | 0.9735 | 0.9728 | $0.0006 | I'll replace the heuristic with the classic best-fit rule augmented by a stronger penalty for res... |
| 66 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll combine the current best-fit-plus-tiny-penalty rule (which scored 0.972834) with a stateful ... |
| 67 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll replace the fixed tiny-residual penalty with a smooth, stateful "gap-usefulness" score: prim... |
| 68 | edit | not_better | 0.9725 | 0.9728 | $0.0006 | I'll switch to the classic "best fit decreasing-like" online rule that also gives a bonus to bins... |
| 69 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I will combine best-fit with a "bin-age spreading" secondary term: track the running mean item si... |
| 70 | edit | not_better | 0.9725 | 0.9728 | $0.0006 | I'll replace the heuristic with a proper stateful "best fit plus exact-fill and popular-residual ... |
| 71 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll try a stateful "already-opened bin" policy: track a running mean item size, and among bins w... |
| 72 | edit | not_better | 0.5985 | 0.9728 | $0.0005 | Replace the integer/subtle-penalty rule with a smooth "best-fit with concave residual utility" ru... |
| 73 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will keep best-fit as the primary rule but replace the fixed tiny-residual penalty with a stron... |
| 74 | edit | not_better | 0.9728 | 0.9728 | $0.0005 | Replace the tiny exact penalty with a proper stateful "sum-of-sizes" tie-breaker: keep best-fit a... |
| 75 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the heuristic with a faithful, stateful implementation of the classic "Best Fit with... |
| 76 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll add a stateful "sum of item sizes / total capacity" mechanism that tracks the cumulative ite... |
| 77 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll replace the tiny-residual penalty with a stronger exact-fill dominance plus a "nice residual... |
| 78 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the heuristic with a stateful policy that scores bins by best-fit primary, plus a bo... |
| 79 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the heuristic with pure best-fit but treat the item as rounding to a "quantized" siz... |
| 80 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I will keep best-fit as the primary rule but replace the fixed tiny-residual penalty with an adap... |
| 81 | edit | not_better | 0.9728 | 0.9728 | $0.0005 | I'll add a stateful component that tracks the running average item size and prefers bins whose re... |
| 82 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the score with a "best-fit with harmonic residual penalty" that adds a small bonus p... |
| 83 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll add a small bonus that prefers placing an item into a bin whose residual after placement equ... |
| 84 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will replace the heuristic with a stateful "subtract-and-simulate" rule: maintain a persistent ... |
| 85 | edit | gate_rejected | 0.9731 | 0.9728 | $0.0006 | I'll use a proper best-fit-decreasing style rule with an adaptive tiny-residual penalty proportio... |
| 86 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the ad-hoc penalty with the classic "best fit with a cutoff": use best-fit normally,... |
| 87 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the heuristic with proper Best-Fit-Decreasing-style behavior using a stateful tally ... |
| 88 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will replace the fixed tiny-residual penalty with a size-aware one plus a strong bonus for resi... |
| 89 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the fragile residual-penalty heuristics with a "best fit + match the residual to a c... |
| 90 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll add a proper adaptive "best fit with residual-utility" rule: keep strict best-fit as the pri... |
| 91 | edit | gate_rejected | 0.9730 | 0.9728 | $0.0005 | I'll switch the primary rule from best fit to "best fit among bins that leave a usable residual",... |
| 92 | edit | not_better | 0.9728 | 0.9728 | $0.0007 | I'll keep strict best-fit as primary, but resolve ties (equal residual, which is common with inte... |
| 93 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the fixed tiny-residual penalty with an adaptive one: track the running distribution... |
| 94 | edit | not_better | 0.9728 | 0.9728 | $0.0005 | I'll enrich the score with a "potential future fill" factor: keep best-fit as the dominant term, ... |
| 95 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the heuristic with a proven online bin-packing rule: strict Best-Fit with a small bo... |
| 96 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the ad-hoc residual penalty with a principled "best fit plus a residual-value term" ... |
| 97 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll implement strict Best Fit with lowest-index tie-breaking but add the classic "best fit decre... |
| 98 | edit | not_better | 0.9724 | 0.9728 | $0.0006 | I'll replace the fixed penalty with an adaptive dual-threshold rule: compute the running mean ite... |
| 99 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll keep strict best fit as the dominant term but replace the fixed tiny-residual penalty with a... |
| 100 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll switch from the ad-hoc tiny-residual penalty to a "best fit but avoid stranding" rule that m... |
| 101 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the fixed tiny-residual penalty with a learned cutoff: penalize residuals smaller th... |
| 102 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the heuristic with "Best Fit plus a mild bonus for bins that can host the current it... |
| 103 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the fixed best-fit criterion with a "Worst-Fit among useful bins" rule from the lite... |
| 104 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the crude tiny-residual penalty with an adaptive rule that tracks the recent distrib... |
| 105 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the fixed tiny-residual penalty with a scale-relative penalty based on the fraction ... |
| 106 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the simpler tiny-residual rule with a "post-placement fill density" criterion: among... |
| 107 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I will replace the best-fit-plus-penalty rule with a two-step "leave a potentially useful residua... |
| 108 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the fixed tiny-residual penalty with an adaptive one based on the running average it... |
| 109 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the fixed tiny-residual penalty with a continuous, best-fit-dominant rule that scores bin... |
| 110 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | All prior tweaks edged around the same best-fit behavior, so I'll switch to a principled "best fi... |
| 111 | edit | not_better | 0.9727 | 0.9728 | $0.0004 | I'll test whether a strict pure best-fit rule (no penalty at all, returning the smallest residual... |
| 112 | edit | not_better | 0.9728 | 0.9728 | $0.0005 | I'll switch from best-fit ranking to a "worst-fit among well-chosen candidates" is risky, so inst... |
| 113 | edit | not_better | 0.9725 | 0.9728 | $0.0005 | Replace the best-fit rule with a score that mixes exact-fit dominance, a mild preference for larg... |
| 114 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the residual-only best-fit rule with a "best fit among bins that aren't nearly-full"... |
| 115 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the best-fit rule with a harmonic-style classifier: partition bins by the ratio of remain... |
| 116 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Prior attempts only nudged the best-fit tie-breaking and all landed at the same plateau, so I'll ... |
| 117 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Introduce a "shortest residual" list-based policy: maintain a persistent best-fit structure by tr... |
| 118 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the fixed best-fit tie-breaking with a regret-based rule: choose the bin whose residual, ... |
| 119 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll shift from pure best-fit to a score that combines best-fit with a "fuller bin" preference (c... |
| 120 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the pure best-fit rule with a "best fit with a one-step lookahead penalty" that discourag... |
| 121 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the pure best-fit score with a modified best-fit that prefers exact fits, but among non-e... |
| 122 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the local residual heuristic with the classic "worst fit decreasing around a threshold": ... |
| 123 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Switch from best-fit to a classic "sum-of-squares" / next-fit-aware rule is unlikely to help; ins... |
| 124 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Replace the hand-tuned residual heuristic with the classic "Best Fit Decreasing"-style rule enhan... |
| 125 | edit | gate_rejected | 0.9769 | 0.9728 | $0.0007 | I'll switch from pure best-fit to a score that maximizes the "fillability" of the residual: rewar... |
| 126 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | The short-stream score of 1.0 came from pure best-fit, so I'll keep best-fit as the strict primar... |
| 127 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll make the penalty function depend on the item size relative to a residual's usefulness, and r... |
| 128 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace best-fit with a conservative "best fit with exact-fit bonus and a dry-bin tie-break" lear... |
| 129 | edit | not_better | 0.9727 | 0.9728 | $0.0012 | Replace the fixed tiny-residual penalty with a stateful, size-aware one: track the smallest item ... |
| 130 | edit | not_better | 0.9725 | 0.9728 | $0.0005 | I'll replace the fixed tiny-residual penalty with a stateful rule that tracks, across the stream,... |
| 131 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the fixed tiny-residual penalty with a stateful, distribution-aware penalty that tra... |
| 132 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the fixed "tiny residual" threshold with best-fit plus an exact-fit reward scaled by item... |
| 133 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the fixed tiny-residual penalty with a stateful, distribution-aware scoring that learns t... |
| 134 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the coarse fixed tiny-residual penalty with a size-aware penalty derived from the known i... |
| 135 | edit | not_better | 0.9722 | 0.9728 | $0.0005 | I will replace the hand-tuned tiny-residual penalty with a principled scoring based on the classi... |
| 136 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I will replace the fixed tiny-residual penalty with a stateful harmonic-style scoring that tracks... |
| 137 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will replace the heuristic with a principled "best fit decreasing-aware" rule: use strict best-... |
| 138 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will add a stateful rule that tracks a running histogram of recent item sizes and, when a bin's... |
| 139 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll replace the heuristic with a principled "best-fit plus residual-class matching" rule: keep b... |
| 140 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I will replace the heuristic with a score that preserves strict best-fit ordering but applies an ... |
| 141 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Introduce a stateful "aging"/classic online heuristic: compute the best-fit residual, but add a s... |
| 142 | edit | invalid | 0.0000 | 0.9728 | $0.0006 | I'll replace the ad-hoc penalty with the classic "best fit" rule plus a principled secondary key:... |
| 143 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will use a stateful harmonic-style rule: track a running histogram of item sizes seen so far an... |
| 144 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | Replace the ad-hoc tiny-residual penalty with a stateful "worst-fit tie-break plus exact-fit bonu... |
| 145 | edit | not_better | 0.9727 | 0.9728 | $0.0004 | I will switch the primary rule to a "best fit with a bounded residual-window tie-break toward the... |
| 146 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I'll replace the hardcoded tiny-residual penalty with a smooth stateful rule: track a running mea... |
| 147 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll implement the classic "Best Fit Decreasing"-style trick for online streams: score bins prima... |
| 148 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll remove the ad-hoc tiny-residual penalty entirely and use pure best-fit (smallest residual), ... |
| 149 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll switch to a stateful "subharmonic"-style rule that directly targets the known weak spot of b... |
| 150 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll keep strict best-fit as the primary key but replace the ad-hoc penalty with a stateful "resi... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,24 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with a small penalty for leaving unusable tiny residuals."""
 import numpy as np
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Rank bins by best fit, but penalize residuals too small to be useful.
 
     item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
+    bins: numpy int64 array with the remaining capacity of every bin the item fits in.
     """
-    return -(bins - item)
+    residual = bins - item  # >= 0 for all shown bins
+
+    # Base best-fit preference: smaller residual is better.
+    score = -residual.astype(np.float64)
+
+    # Tiny nonzero residuals are likely stranded capacity; add a mild penalty so that
+    # when a slightly looser bin is available, we prefer it (reduces fragmentation).
+    # A residual of 0 (exact fill) is ideal and must NOT be penalized.
+    tiny = (residual > 0) & (residual < 5)
+    score -= tiny.astype(np.float64) * 1.5
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (6 parts, 12 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 12 | `residual = bins - item` | -0.9728 | essential: the program fails or turns invalid without it |
| 12 | `term + bins` | -0.9728 | essential: the program fails or turns invalid without it |
| 15 | `score = -residual.astype(np.float64)` | -0.9728 | essential: the program fails or turns invalid without it |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 12: `term - item`
- line 20: `tiny = (residual > 0) & (residual < 5)`
- line 21: `score -= tiny.astype(np.float64) * 1.5`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9728 | 0.9634 |
| minimal (3 parts removed) | 0.9727 | 0.9634 |

Minimal program:

```python
"""Best fit with a small penalty for leaving unusable tiny residuals."""
import numpy as np

def priority(item, bins):
    """Rank bins by best fit, but penalize residuals too small to be useful.

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in.
    """
    residual = bins
    score = -residual.astype(np.float64)
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_e_rand --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 3
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_e_rand-s3   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_e_rand/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_e_rand/initial.py` `609927c5ea619a94`
- `problems/bp_sh_e_rand/problem.md` `190017a698e23cd8`
- `problems/bp_sh_e_rand/suite.json` `7e369a6aa9869ab4`
- `problems/bp_sh_e_rand/verify.py` `0f28aa90e2f40f70`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
