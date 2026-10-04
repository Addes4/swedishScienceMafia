# Research loop report: bp_sh_c80

| | |
|---|---|
| problem | `bp_sh_c80` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0855 of a $0.20 hard cap, 150 calls, 299,325 tokens |
| wall time | search 1550 s, baselines 101 s, explain 46 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (147 valid), 1 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9349 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9351 | 0.9634 |  |
| baseline `funsearch_or` | 0.9390 | 0.9711 | `problems/bp_sh_c80/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.7852 | 0.9937 | `problems/bp_sh_c80/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.8821 | 0.9950 | `problems/bp_sh_c80/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9349 | 0.9634 | 7 parts removed |

Audit: public 0.9349 → 0.9351 (+0.0002), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program -0.0283.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9390). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9349 | 0.9349 | $0.0003 | Replace pure best-fit with a tuned "best-fit plus small bonus for fuller/earlier bins" scoring th... |
| 2 | edit | not_better | 0.9349 | 0.9349 | $0.0003 | Replace the pure best-fit rule with a classic "best fit decreasing-like" hybrid: score bins by ho... |
| 3 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll replace pure best-fit with a "best fit plus short-horizon hindsight" rule: track the empiric... |
| 4 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace pure best-fit with a "worst-fit within a best-fit region" hybrid: prefer bins where the l... |
| 5 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | The previous attempts all kept the same fine-grained best-fit ranking, so ties essentially never ... |
| 6 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch from best-fit to a "best-fit with a preference for bins whose residual after placemen... |
| 7 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | I'll abandon the fine-grained best-fit ranking and instead use a "sum-of-squares residual matchin... |
| 8 | edit | not_better | 0.8634 | 0.9349 | $0.0006 | Replace pure best-fit with a "best-fit with empirical leave-one-capacity residual matching" rule:... |
| 9 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace hard best-fit with a randomized/tie-broken "best-fit with a bounded capacity threshold": ... |
| 10 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch to a proper score that ranks bins by the residual after placement but breaks near-tie... |
| 11 | edit | not_better | 0.9332 | 0.9349 | $0.0006 | I'll replace the pure best-fit rule with a size-class-aware "residual matching" rule: track the r... |
| 12 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll keep strict best-fit (which is strong here) but break exact ties among equally-tight bins to... |
| 13 | edit | not_better | 0.5280 | 0.9349 | $0.0005 | I will switch from pure best-fit to a "worst-fit with bounded slack" rule: place the item into th... |
| 14 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | The pure best-fit rule is already near-optimal for this distribution, so I'll keep strict best-fi... |
| 15 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Keep strict best-fit, but break ties toward the fullest bin (largest residual exactly equal to it... |
| 16 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll add a lightweight lookahead-free improvement to strict best-fit: track the running histogram... |
| 17 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll keep strict best-fit but add a "gap-filling" secondary criterion: among bins whose post-plac... |
| 18 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will switch from pure best-fit to a "best-fit with frequency-aware perfect matching": among bin... |
| 19 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Implement the classic "best fit decreasing"-style improvement adapted to online streaming: use th... |
| 20 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit with a tie-broken "best fit with lazy emptying": compute each fitting bin's... |
| 21 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will keep best-fit as the primary criterion but subtract a small bonus for bins whose post-plac... |
| 22 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a score that uses best-fit as primary but gives a small bonus whe... |
| 23 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | I'll replace pure best-fit with a score that combines best-fit with a first-fit-like preference f... |
| 24 | edit | not_better | 0.9345 | 0.9349 | $0.0005 | I will replace pure best-fit with a generalized "best fit with fill-biased tie-breaking on near-e... |
| 25 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll add an online-learned "closing" heuristic: since past attempts at tweaking best-fit all tied... |
| 26 | edit | not_better | 0.9304 | 0.9349 | $0.0005 | Best fit wastes bins because it always fills the tightest gap, which fragments capacity; I'll ins... |
| 27 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | I'll try a two-criterion online rule: use best-fit but with a small preference to leave residuals... |
| 28 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit with a harmonic-style "best fit plus quantized residual preference": since ... |
| 29 | edit | not_better | 0.4224 | 0.9349 | $0.0006 | Replace the pure best-fit score with an expected-utility rule: maintain an online histogram of ob... |
| 30 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Refine the tie-break: keep strict best-fit residual as the primary score, but add a tiny bonus fo... |
| 31 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "best fit decreasing-style reserve" hybrid: score bins by the residu... |
| 32 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I will replace strict best-fit residual with a "sum-of-two-largest-fits" score: for each candidat... |
| 33 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace strict best-fit with a residual-picking rule that avoids leaving small fragments: among b... |
| 34 | edit | not_better | 0.4064 | 0.9349 | $0.0004 | I'll switch from best-fit to a "least-loaded / worst-fit among fitting bins" rule, which tends to... |
| 35 | edit | not_better | 0.6045 | 0.9349 | $0.0007 | I'll replace pure best-fit (which always minimizes the post-placement residual, fragmenting bins)... |
| 36 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace strict best-fit with a hybrid that uses best-fit as the default but, when the item exactl... |
| 37 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the pure best-fit score with a hybrid that strongly prefers leaving "reusable" resid... |
| 38 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | The pure best-fit rule can be improved by incorporating a small "fill-aware" adjustment: give a m... |
| 39 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will replace pure best-fit with a best-fit rule that breaks near-ties using a learned estimate ... |
| 40 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will replace pure best-fit with a "best-fit with exact-fit and large-itm avoidance" variant: sc... |
| 41 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace best-fit with a "best-fit with a post-placement quality bonus" rule: keep tightness ... |
| 42 | edit | not_better | 0.8228 | 0.9349 | $0.0005 | Replace pure best-fit with a rule that prefers the bin with the largest remaining capacity that s... |
| 43 | edit | not_better | 0.4953 | 0.9349 | $0.0005 | I will switch from best-fit (which tightly packs early and fragments badly) to a "worst-fit with ... |
| 44 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a harmonic-style scoring that prefers placing an item into a bin ... |
| 45 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Best-fit gets stuck because it cannot distinguish among near-ties; I will add a tie-breaking tie-... |
| 46 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a two-level rule: the primary score strongly prefers exact fits (... |
| 47 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I will replace pure best-fit with collapsed best-fit: try to place each item only into the fulles... |
| 48 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I will switch to a scoring rule that, instead of pure best-fit, uses the "Match" heuristic from o... |
| 49 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll combine best-fit's dominant tightness term with a small additive bonus for bins that current... |
| 50 | edit | not_better | 0.7400 | 0.9349 | $0.0006 | Most attempts failed because the tie-break terms act on post-placement residual (which best-fit a... |
| 51 | edit | not_better | 0.4064 | 0.9349 | $0.0005 | I'll replace pure best-fit with a conservative "almost-worst-fit" only for the largest items: kee... |
| 52 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Pure best-fit greedily minimizes immediate waste but scatters items, leaving many partially-fille... |
| 53 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I will keep exact-fit priority but, when there is no exact fit, use best-fit with a small tie-bre... |
| 54 | edit | not_better | 0.4064 | 0.9349 | $0.0005 | I'll replace pure best-fit with a harmonic "sum of squared residuals" criterion, which is the cla... |
| 55 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a "best fit with exact-fit deferral" rule using a per-stream running mean of item ... |
| 56 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "best-fit with deferred exact-fit avoidance" is unlikely to help; in... |
| 57 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best fit is a strong single-item rule but it fragments; I'll blend it with a "least loaded among ... |
| 58 | edit | not_better | 0.4064 | 0.9349 | $0.0005 | Introduce a "sub-harmonic / sum-of-squares" residual-aware rule that also considers how the resul... |
| 59 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a rule that still prefers the tightest fit but defers the near-ex... |
| 60 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | Replace pure best-fit with a classic harmonic-based rule: instead of minimizing the residual, sco... |
| 61 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement Best-Fit but with a capped-at-100 harmonic residual tie-break: primary criterion r... |
| 62 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a "best-fit with small-residue penalty" rule: prefer the tightest... |
| 63 | edit | not_better | 0.8761 | 0.9349 | $0.0007 | I'll replace pure best-fit with a classic "harmonic" class-based rule: classify the item by size ... |
| 64 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a "Best Fit with a tiny anti-fragmentation tie-break" that keeps exact best-fit as... |
| 65 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace the deterministic best-fit with a randomized "best-fit with occasional second-best tie-br... |
| 66 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a bounded historical-state rule that tracks the observed item-size histogram and scores bins ... |
| 67 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a proper Best-Fit-Decreasing-style "almost-worst-fit" hybrid known as the "Best Fi... |
| 68 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "Best-Fit-with-Aging": keep minimizing the resulting residual as the... |
| 69 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll try a well-founded online rule specifically suited to Weibull(mean 40) items: score bins by ... |
| 70 | edit | not_better | 0.5442 | 0.9349 | $0.0005 | Replace pure best-fit with a size-thresholded rule: items that are at least half the capacity (≥5... |
| 71 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a score that combines best-fit (minimize leftover) with a fractional "fill ratio" ... |
| 72 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a "best fit with a future-fit look-ahead": after placing, prefer bins whose residu... |
| 73 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace best-fit with a "best-fit-decreasing-flavored" rule that uses the known item distribution... |
| 74 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a randomized Best-Fit with a small probability of choosing the second-... |
| 75 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "reserve for complement" rule suited to this distribution: score bin... |
| 76 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll break away from pure best-fit by combining it with a tunable "bin reuse" bonus: among reason... |
| 77 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | I'll switch to a harmonic/ratio-based fill criterion: score each bin by the post-placement residu... |
| 78 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a bounded "reserve capacity" rule tuned to the Weibull-like distributi... |
| 79 | edit | not_better | 0.9343 | 0.9349 | $0.0005 | Many prior tweaks all landed on the same best-fit score, so I'll try a genuinely different rule: ... |
| 80 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | For this Weibull-shaped size distribution (mean ~40), strict best-fit over-packs large items and ... |
| 81 | edit | not_better | 0.7069 | 0.9349 | $0.0005 | All previous micro-variants collapse to best-fit because on this distribution best-fit is already... |
| 82 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll try a hybrid that is mostly best-fit but occasionally (with low probability) diverts to a bi... |
| 83 | edit | improved | 0.9351 | 0.9351 | $0.0006 | Rather than tuning the greedy fill rule (which keeps collapsing to best-fit), I'll add a "deny sm... |
| 84 | edit | not_better | 0.9334 | 0.9351 | $0.0005 | Replace the current heuristic with a fixed-scale scoring rule that strongly prefers exact-fill be... |
| 85 | edit | not_better | 0.9351 | 0.9351 | $0.0008 | I'll augment the penalty with cumulative information: penalize residuals less when they can still... |
| 86 | edit | not_better | 0.9330 | 0.9351 | $0.0009 | Rework the penalty to use an empirical-CDF-based "fillable residual" score normalized and capped,... |
| 87 | edit | not_better | 0.9338 | 0.9351 | $0.0008 | Replace the crisp "residual equals a likely item size" penalty with the empirical CDF P(item ≤ re... |
| 88 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll drop the histogram-based penalty (which has repeatedly failed to beat plain best-fit) and in... |
| 89 | edit | not_better | 0.9351 | 0.9351 | $0.0007 | I'll replace the histogram penalty with a "difficulty-aware" rule: bins whose residual is smaller... |
| 90 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Replace the ad-hoc histogram penalty with a cleaner "best-fit plus reuse potential" score: prefer... |
| 91 | edit | not_better | 0.5822 | 0.9351 | $0.0008 | I'll replace best-fit-with-stranding-penalty by a proper online learned classifier-style rule: ma... |
| 92 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I will drop the empirical-histogram machinery entirely and replace it with a smooth "best-fit + s... |
| 93 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the ad-hoc histogram/quantile penalty machinery with the classic ASUM-style rule use... |
| 94 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the histogram machinery with a principled one-step lookahead: score each bin by best... |
| 95 | edit | not_better | 0.4953 | 0.9351 | $0.0006 | I will replace the ad-hoc scoring with the classic Harmonic/Sum-of-Squares style online rule: sco... |
| 96 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the fragile histogram machinery with a simple, robust best-fit tie-break: purely pre... |
| 97 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the empirical-histogram penalty with a principled "exact-fit + small-residual preser... |
| 98 | edit | not_better | 0.9351 | 0.9351 | $0.0006 | I'll replace the current penalty scheme with a widened "best fit plus empirical reuse" score that... |
| 99 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Change the score to a reuse-bonus form: give residual 0 a large bonus, then subtract residual (be... |
| 100 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Replace the histogram-penalty score with a convex-potential primary rule: give exact fits a stron... |
| 101 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the penalty that fires only when a residual is rare with a two-sided "residual reusa... |
| 102 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll switch from the fragile per-residual histogram penalty to a robust Best-Fit-Decreasing-style... |
| 103 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the score with a "best fit plus exact-fit tie-break using the item's own occurrence"... |
| 104 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the rigid empirical histogram with a fast-converging, smoothed estimation of the ite... |
| 105 | edit | not_better | 0.8812 | 0.9351 | $0.0006 | I'll replace the noisy per-residual empirical penalty with a robust "best-fit plus exact-fit bonu... |
| 106 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the score with a pure best-fit rule (smallest non-negative residual wins, exact fits... |
| 107 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the score with a "best-fit plus look-ahead fill" rule: keep best-fit as the primary ... |
| 108 | edit | not_better | 0.9349 | 0.9351 | $0.0010 | I'll replace the noisy empirical-histogram penalty with a fixed, smooth prior derived from the kn... |
| 109 | edit | not_better | 0.4064 | 0.9351 | $0.0006 | Replace the noisy best-fit-only ranking with First-Fit ordering combined with a "least loaded fit... |
| 110 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the score with the classic "Best Fit with a loud exact-fit bonus" combined with a re... |
| 111 | edit | invalid | 0.0000 | 0.9351 | $0.0007 | I'll replace the noisy empirical histogram with a constant smooth prior plus a "sum of two items"... |
| 112 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I will keep best-fit as the primary ordering but replace the noisy empirical penalty with a smoot... |
| 113 | edit | invalid | 0.0000 | 0.9351 | $0.0007 | The empirical penalty is noisy because it is refreshed only every 50 items and uses raw counts; I... |
| 114 | edit | not_better | 0.9033 | 0.9351 | $0.0006 | Keep best-fit as the dominant term (score = -residual) but add a strong constant bonus when the r... |
| 115 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll add a "perfect-fit priority" that first tries an exact fit (residual 0) with a very high bon... |
| 116 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll combine the current best-fit with a small "worst-fit-like" tie-breaking bonus for larger res... |
| 117 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll combine best-fit with a monotone residual-size bonus that favors larger residuals (which are... |
| 118 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Replace the periodically-refreshed raw histogram with a stable exponentially-weighted moving aver... |
| 119 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Replace the stateful empirical penalty with a fixed smooth prior over item sizes and add a modest... |
| 120 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the noisy, stateful empirical penalty with a parameter-free score that combines best... |
| 121 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll abandon the empirical/stale penalty and use a pure best-fit score (smallest residual wins) w... |
| 122 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Replace the raw best-fit (smallest residual) ranking with a score based on how well the item size... |
| 123 | edit | invalid | 0.0000 | 0.9351 | $0.0006 | I'll replace the noisy periodic histogram with an online EWMA estimate of the item-size pmf updat... |
| 124 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Replace the noisy global empirical penalty with a small, stateful bonus for bins whose residual e... |
| 125 | edit | not_better | 0.4765 | 0.9351 | $0.0006 | Replace the noisy empirical penalty with a clean "opportunity cost" score: strongly prefer exact ... |
| 126 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the noisy empirical penalty with a stable score that strongly prefers small residual... |
| 127 | edit | not_better | 0.4260 | 0.9351 | $0.0007 | Replace the per-call empirical histogram (which is noisy, stale, and dominated by the very item b... |
| 128 | edit | not_better | 0.9349 | 0.9351 | $0.0007 |  |
| 129 | edit | not_better | 0.9351 | 0.9351 | $0.0006 | I'll keep a small stateful histogram but use it only to give a modest bonus to bins whose residua... |
| 130 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Use a partial-sum tail probability from the empirical item-size histogram to reward residuals tha... |
| 131 | edit | not_better | 0.9351 | 0.9351 | $0.0006 | I'll make the scoring a pure best-fit but break ties using an online, stateful "complement reuse"... |
| 132 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the score with an exact "expected future fill" estimate: prefer best-fit, but break ... |
| 133 | edit | invalid | 0.0000 | 0.9351 | $0.0006 | I'll replace the noisy per-item penalty with the classic "best fit decreasing"-style rule but add... |
| 134 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll use the classic smart online rule: prefer the fullest bin that leaves a residual at least as... |
| 135 | edit | not_better | 0.9349 | 0.9351 | $0.0004 | Replace the noisy histogram penalty with a simple, pure best-fit rule (smallest residual), which ... |
| 136 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Replace the per-item noisy histogram penalty with a geometric online fit: use a pure best-fit bas... |
| 137 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll add a stateful "canonical complement" bonus: maintain a decaying histogram of recent item si... |
| 138 | edit | not_better | 0.4064 | 0.9351 | $0.0005 | Replace the score with a "leaky-bin / worst-fit" rule: send the item to the bin with the largest ... |
| 139 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | (no description) |
| 140 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the noisy per-item histogram penalty with a deterministic "reserve fit" rule: base b... |
| 141 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the noisy empirical-histogram penalty with a principled look-ahead: maintain an onli... |
| 142 | edit | not_better | 0.9343 | 0.9351 | $0.0005 | I'll switch to a hybrid that keeps pure best-fit as the dominant rule but adds a deterministic "p... |
| 143 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Keep pure best-fit as the dominant rule but add a small deterministic bonus for residuals that eq... |
| 144 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Replace the noisy empirical-histogram penalty with a well-known online packing rule: "best fit wi... |
| 145 | edit | not_better | 0.9351 | 0.9351 | $0.0006 | I'll strengthen the stranding penalty by making it grow with how much smaller the residual is tha... |
| 146 | edit | not_better | 0.9092 | 0.9351 | $0.0007 | I'll replace the ad-hoc penalty with a principled conservation law from bin packing: prefer placi... |
| 147 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the noisy per-item empirical penalty with the classic "best fit decreasing"-style ru... |
| 148 | edit | gate_rejected | 0.9353 | 0.9351 | $0.0008 | I'll sharpen the existing histogram-based stranding penalty by learning the empirical probability... |
| 149 | edit | not_better | 0.8833 | 0.9351 | $0.0006 | I'll keep best-fit as the base but replace the noisy histogram penalty with a clean deterministic... |
| 150 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | The empirical penalty is noisy and my deterministic variants regressed, so I'll revert to pure be... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,50 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with an online penalty for stranding improbable small residuals."""
 import numpy as np
 
 
+# Online histogram of item sizes seen so far (updated once per call).
+_HIST = np.zeros(101, dtype=np.float64)   # counts for sizes 1..100
+_TOTAL = 0.0
+_RECOMPUTE_EVERY = 50
+_CACHED_PROB = np.zeros(101, dtype=np.float64)
+
+
+def _refresh_prob():
+    global _CACHED_PROB
+    if _TOTAL <= 0:
+        _CACHED_PROB = np.zeros(101, dtype=np.float64)
+        return
+    p = _HIST / _TOTAL
+    # Smooth a bit and drop the empty-size probability (size 0 never arrives).
+    _CACHED_PROB = p
+
+
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every fitting bin; highest score wins (first on ties).
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
+    Base is best fit (smallest post-placement residual).  We add a penalty when the
+    residual r is a size that the empirical item distribution almost never produces,
+    since such a gap is likely to be stranded forever.
     """
-    return -(bins - item)
+    global _TOTAL, _RECOMPUTE_EVERY
+
+    # Record this item (post-decision, but item is given before we rank).
+    _HIST[item] += 1.0
+    _TOTAL += 1.0
+    if int(_TOTAL) % _RECOMPUTE_EVERY == 0:
+        _refresh_prob()
+
+    residual = bins - item  # >= 0 for all shown bins
+    base = -residual.astype(np.float64)
+
+    # Probability that some future item exactly fills the residual.
+    # Use the empirical pmf of the residual size.
+    prob = _CACHED_PROB[residual]
+
+    # Penalize residuals that are unlikely to be reused by a future item.
+    # Scale so it can overturn close best-fit choices but not dominate exact fits.
+    penalty = 60.0 * (1.0 - prob)
+
+    return base - penalty
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (13 parts, 25 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 38 | `residual = bins - item` | -0.9351 | essential: the program fails or turns invalid without it |
| 38 | `term + bins` | -0.9351 | essential: the program fails or turns invalid without it |
| 39 | `base = -residual.astype(np.float64)` | -0.9351 | essential: the program fails or turns invalid without it |
| 43 | `prob = _CACHED_PROB[residual]` | -0.9351 | essential: the program fails or turns invalid without it |
| 49 | `term + base` | -0.0472 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 30: `global _TOTAL, _RECOMPUTE_EVERY`
- line 33: `_HIST[item] += 1.0`
- line 34: `_TOTAL += 1.0`
- line 35: `if int(_TOTAL) % _RECOMPUTE_EVERY == 0: ...`
- line 36: `_refresh_prob()`
- line 38: `term - item`
- line 47: `penalty = 60.0 * (1.0 - prob)`
- line 49: `term - penalty`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9351 | 0.9634 |
| minimal (7 parts removed) | 0.9349 | 0.9634 |

Minimal program:

```python
"""Best fit with an online penalty for stranding improbable small residuals."""
import numpy as np
_HIST = np.zeros(101, dtype=np.float64)
_TOTAL = 0.0
_RECOMPUTE_EVERY = 50
_CACHED_PROB = np.zeros(101, dtype=np.float64)

def _refresh_prob():
    global _CACHED_PROB
    if _TOTAL <= 0:
        _CACHED_PROB = np.zeros(101, dtype=np.float64)
        return
    p = _HIST / _TOTAL
    _CACHED_PROB = p

def priority(item, bins):
    """Return a priority for every fitting bin; highest score wins (first on ties).

    Base is best fit (smallest post-placement residual).  We add a penalty when the
    residual r is a size that the empirical item distribution almost never produces,
    since such a gap is likely to be stranded forever.
    """
    residual = bins
    base = -residual.astype(np.float64)
    prob = _CACHED_PROB[residual]
    return base
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_c80 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 1
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_c80-s1   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_c80/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_c80/initial.py` `609927c5ea619a94`
- `problems/bp_sh_c80/problem.md` `190017a698e23cd8`
- `problems/bp_sh_c80/verify.py` `dc0d05d86db9dbf0`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
