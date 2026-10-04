# Research loop report: bp_sh_c80

| | |
|---|---|
| problem | `bp_sh_c80` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0874 of a $0.20 hard cap, 150 calls, 299,084 tokens |
| wall time | search 1302 s, baselines 44 s, explain 44 s |
| stopped | max_iters (stopped_early) |
| evaluations | 149 (149 valid), 6 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9349 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9423 | 0.9683 |  |
| baseline `funsearch_or` | 0.9390 | 0.9711 | `problems/bp_sh_c80/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.7852 | 0.9937 | `problems/bp_sh_c80/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.8821 | 0.9950 | `problems/bp_sh_c80/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9407 | 0.9695 | 3 parts removed |

Audit: public 0.9349 → 0.9423 (+0.0074), hidden 0.9634 → 0.9683 (+0.0049); public − hidden gap of the final program -0.0260.

Against the baselines: the final program's public score is above the best baseline (`funsearch_or`, 0.9390). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit with a size-threshold-aware rule: track a running estimate of the item dist... |
| 2 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Switch to a best-fit-decreasing style rule by using the classic "almost worst fit" twist tailored... |
| 3 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace pure best-fit with a harmonic-aware rule: compute a score that prefers tight fits but str... |
| 4 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Modify the best-fit rule to add a small tie-breaking bonus rewarding residual capacities that fal... |
| 5 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Use the exact Best-Fit-Decreasing analogue that is known to be optimal-ish online: keep a running... |
| 6 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Refine best-fit by biasing toward bins whose post-placement residual is either 0 (perfect fit) or... |
| 7 | edit | not_better | 0.4064 | 0.9349 | $0.0004 | Replace best-fit with the classic "Worst Fit" rule (place the item in the bin with the most remai... |
| 8 | edit | not_better | 0.9304 | 0.9349 | $0.0005 | Use the classic "First Fit" rule: scan bins in index order and place the item in the first bin it... |
| 9 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Implement a lightweight learned lookup table: since the item distribution is fixed and unknown, I... |
| 10 | edit | no_code | n/a | 0.9349 | $0.0004 | Replace pure best-fit with a "best-fit with residual-class awareness" rule based on the classic o... |
| 11 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Keep best-fit as the primary criterion but break exact ties in remaining capacity by preferring t... |
| 12 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace pure best-fit with a hybrid rule: normally use best-fit (tightest residual), but when the... |
| 13 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | Replace pure best-fit with a "subset-sum aware" rule: score each bin by how useful its post-place... |
| 14 | edit | improved | 0.9351 | 0.9351 | $0.0004 | Replace the pure best-fit score with a bounded best-fit that caps the residual at 25 before negat... |
| 15 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll add a small tie-breaker to the capped best-fit rule: among bins whose (capped) residual is e... |
| 16 | edit | gate_rejected | 0.9355 | 0.9351 | $0.0005 | I will replace the fixed residual cap of 25 with a data-driven cap derived from observed item siz... |
| 17 | edit | not_better | 0.9268 | 0.9351 | $0.0005 | I'll add a persistent per-stream counter and switch to a strength-ordered "worst-fit small" is wr... |
| 18 | edit | not_better | 0.9336 | 0.9351 | $0.0006 | I'll implement a "bounded best-fit with harmonic residual preference": keep the residual cap at 2... |
| 19 | edit | not_better | 0.9313 | 0.9351 | $0.0005 | I'll replace the hard residual cap with a smooth penalty function that strongly prefers tight fit... |
| 20 | edit | not_better | 0.9340 | 0.9351 | $0.0005 | I will add a lightweight online "flip" that, for each item, compares capped best-fit against wors... |
| 21 | edit | not_better | 0.9336 | 0.9351 | $0.0006 | I will replace the capped best-fit rule with a "best-fit-decreasing-style" harmonic rule: score e... |
| 22 | edit | not_better | 0.9343 | 0.9351 | $0.0006 | I will use a two-sided adaptive cap derived from the observed item sizes: cap residuals below the... |
| 23 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I will make the residual cap adaptive by bounding it with a small value derived from the running ... |
| 24 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the capped best-fit with a proper Best-Fit-Decreasing-aware rule: keep best-fit resi... |
| 25 | edit | not_better | 0.9351 | 0.9351 | $0.0005 | The capped best-fit rule is already near-optimal for online packing, but many attempts over-pertu... |
| 26 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Replace the fixed residual cap of 25 with a cap equal to a small adaptive value derived from the ... |
| 27 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the heuristic with a clean Best-Fit implementation but add a small tie-break that pr... |
| 28 | edit | no_code | n/a | 0.9351 | $0.0006 | (no description) |
| 29 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I will replace the capped best-fit with a weighted best-fit that strongly prefers the tightest fi... |
| 30 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the heuristic with a proper harmonic-style scoring that combines tightest-fit with a... |
| 31 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll switch from capped best-fit to a smooth "harmonic"-style score that strongly prefers near-pe... |
| 32 | edit | not_better | 0.9349 | 0.9351 | $0.0004 | I'll implement a proper Best-Fit with a deterministic tie-break that, among bins with equal resid... |
| 33 | edit | not_better | 0.9349 | 0.9351 | $0.0009 | Remove the residual cap and use pure best-fit, so that among loose bins (residual > 25) we still ... |
| 34 | edit | not_better | 0.9310 | 0.9351 | $0.0005 | I'll replace the heuristic with a Best-Fit rule augmented by a "harmonic" penalty that discourage... |
| 35 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the heuristic with a linear-programming-informed "best fit" variant that uses a frac... |
| 36 | edit | not_better | 0.9349 | 0.9351 | $0.0011 | I'll switch to a sharp harmonic (reciprocal) score on the post-placement residual so that near-ex... |
| 37 | edit | not_better | 0.9328 | 0.9351 | $0.0005 | I'll replace the deterministic best-fit with a waste-aware score that combines tightest fit with ... |
| 38 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I will replace the pure best-fit rule with a weighted combination of best-fit and a "sum of squar... |
| 39 | edit | not_better | 0.9151 | 0.9351 | $0.0007 | I'll switch to a "target residual" rule: prefer the bin whose post-placement residual lands neare... |
| 40 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll add a light stateful touch: among essentially-equal tight fits, prefer the bin that was open... |
| 41 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Replace the capped best-fit with a "best-fit with a small future-fit bonus": among bins, prefer t... |
| 42 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I will switch from the capped best-fit to an exact best-fit plus a mild "perfect-fit reuse" bonus... |
| 43 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the pure best-fit with a "worst-fit among tight fits" tie-breaker: rank primarily by... |
| 44 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the capped best-fit with a harmonic (reciprocal-residual) best-fit that strongly pre... |
| 45 | edit | not_better | 0.9203 | 0.9351 | $0.0005 | I'll try a harmonic best-fit variant that maximizes 1/(1+residual) (equivalently strongly prefers... |
| 46 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I will replace the fixed cap/rule with a learned-style "best fit plus gap-filling" score that pre... |
| 47 | edit | not_better | 0.9340 | 0.9351 | $0.0005 | I'll adopt a two-parameter score that combines tight fit with a soft penalty on tiny unusable sli... |
| 48 | edit | not_better | 0.9351 | 0.9351 | $0.0005 | I'll try a two-parameter hybrid: a capped best-fit (cap 25, as the current best) but with a small... |
| 49 | edit | not_better | 0.9349 | 0.9351 | $0.0004 | I'll try replacing the hard cap at 25 with a smooth concave transform of the residual (score = -r... |
| 50 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the hard cap with an exact best-fit combined with a penalization of residuals that f... |
| 51 | edit | not_better | 0.9338 | 0.9351 | $0.0006 | Introduce a stateful gap-aware score: default to capped best-fit, but when a bin's residual exact... |
| 52 | edit | improved | 0.9366 | 0.9366 | $0.0005 | I will switch from capped best-fit to a "worst-fit with tightness guard": normally place an item ... |
| 53 | edit | not_better | 0.9362 | 0.9366 | $0.0005 | I'll tune the target residual from 30 to 25 and add a mild preference among large-residual bins b... |
| 54 | edit | improved | 0.9403 | 0.9403 | $0.0005 | I will tune the target-residual sweet spot from 30 to a slightly larger value around 35, which be... |
| 55 | edit | not_better | 0.9386 | 0.9403 | $0.0007 | (no description) |
| 56 | edit | not_better | 0.9403 | 0.9403 | $0.0005 | I'll refine the tight-fit bonus so it applies only to residuals that can actually hold a likely f... |
| 57 | edit | not_better | 0.9362 | 0.9403 | $0.0006 | I'll add a stateful, distribution-adaptive sweet spot: track a small histogram of past item sizes... |
| 58 | edit | not_better | 0.9379 | 0.9403 | $0.0007 | I'll keep the proven target-residual score but make the tight-fit bonus scaled to the actual arri... |
| 59 | edit | not_better | 0.9347 | 0.9403 | $0.0006 | I'll replace the fixed "target residual" heuristic with a combined score that is primarily a capp... |
| 60 | edit | not_better | 0.9349 | 0.9403 | $0.0005 | I will replace the soft target-residual scoring with a hard "best-fit" core (tightest feasible re... |
| 61 | edit | not_better | 0.9384 | 0.9403 | $0.0006 | I will broaden the near-exact tight-fit plateau: instead of an unbounded linear 1e6 reward that m... |
| 62 | edit | not_better | 0.8785 | 0.9403 | $0.0006 | I will replace the fixed sweet spot with a two-mode score: exhaustively prefer filling a residual... |
| 63 | edit | not_better | 0.9379 | 0.9403 | $0.0005 | I'll add a stateful running histogram of past item sizes and use it to pick the sweet-spot target... |
| 64 | edit | not_better | 0.9381 | 0.9403 | $0.0005 | I'll strengthen the reward for residuals that exactly match a small set of likely future item siz... |
| 65 | edit | not_better | 0.9362 | 0.9403 | $0.0005 | I'll tune the fixed target residual and the tight-fit parameters via a small sweep, since the exi... |
| 66 | edit | not_better | 0.9399 | 0.9403 | $0.0006 | I'll keep the proven target-residual structure but make the tight-fit reward depend on the actual... |
| 67 | edit | not_better | 0.9247 | 0.9403 | $0.0009 | I'll switch from the linear "sweet spot" target to a proper expected-waste minimization: score ea... |
| 68 | edit | not_better | 0.9360 | 0.9403 | $0.0005 | I'll keep the proven target-residual score but tune the sweet-spot target and tight-fit cutoff by... |
| 69 | edit | not_better | 0.9362 | 0.9403 | $0.0006 | I'll shift the sweet-spot target from 35 to 32 and slightly widen the tight-fit window from 8 to ... |
| 70 | edit | not_better | 0.9323 | 0.9403 | $0.0006 | The best-scoring family so far uses a fixed target residual; I'll make the tight-fit completion b... |
| 71 | edit | not_better | 0.9349 | 0.9403 | $0.0006 | Replace the symmetric \|residual - target\| score with a lexicographic-style score: heavily rewar... |
| 72 | edit | not_better | 0.9349 | 0.9403 | $0.0007 | Shift from the symmetric "target residual" score to a best-fit base (smaller residual is always b... |
| 73 | edit | not_better | 0.9397 | 0.9403 | $0.0007 | I'll refine the best-known target-residual form: keep the sweet-spot target at 35 but make the sc... |
| 74 | edit | not_better | 0.8448 | 0.9403 | $0.0007 | Replace the fixed-width tight-fit window with a distribution-aware one: maintain a running histog... |
| 75 | edit | not_better | 0.9377 | 0.9403 | $0.0007 | Keep the proven \|residual - 35\| base score, but add a bonus proportional to the running-histogr... |
| 76 | edit | not_better | 0.6369 | 0.9403 | $0.0006 | I'll add a sum-based lookahead: for each candidate bin, approximate the probability that the resi... |
| 77 | edit | not_better | 0.9338 | 0.9403 | $0.0005 | I'll replace the fixed sweet-spot target with a two-piece-fit reward: keep a mild best-fit base (... |
| 78 | edit | not_better | 0.9349 | 0.9403 | $0.0006 | I'll simplify the proven target-residual rule and tune the two constants (target and tight-fit wi... |
| 79 | edit | not_better | 0.9399 | 0.9403 | $0.0006 | I'll add a distribution-aware "fillability" bonus on top of the proven \|residual-35\| score: mai... |
| 80 | edit | not_better | 0.9358 | 0.9403 | $0.0005 | I'll keep the proven \|residual - 35\| base but replace the fixed tight-fit bonus with an asymmet... |
| 81 | edit | improved | 0.9407 | 0.9407 | $0.0006 | Adjust the proven target-residual rule's constants: raise the sweet-spot target to ~38 (closer to... |
| 82 | edit | improved | 0.9414 | 0.9414 | $0.0006 | I'll refine the proven target-residual rule by making the sweet-spot target itself adapt to the s... |
| 83 | edit | not_better | 0.9412 | 0.9414 | $0.0006 | Make the tight-fit completion bonus smoother and slightly wider (window ~10 with a gentler slope)... |
| 84 | edit | not_better | 0.9349 | 0.9414 | $0.0005 | Replace the \|residual - target\| sweet-spot with a direct best-fit base (minimizing residual) co... |
| 85 | edit | not_better | 0.9373 | 0.9414 | $0.0007 | I'll keep the proven target-residual base with the tight-fit completion bonus, but make the sweet... |
| 86 | edit | not_better | 0.9397 | 0.9414 | $0.0006 | I'll replace the mean-based sweet spot with a more robust "expected next-fit" target estimated fr... |
| 87 | edit | not_better | 0.9390 | 0.9414 | $0.0006 | The current rule ranks purely by residual, ignoring that a residual can be filled exactly by a fu... |
| 88 | edit | not_better | 0.9414 | 0.9414 | $0.0006 | I'll add a small bin-index/age preference so that, among bins with similar scores, the algorithm ... |
| 89 | edit | not_better | 0.9397 | 0.9414 | $0.0006 | The hand-tuned target of 0.92*mean is good, but it can be improved by shifting the objective: ins... |
| 90 | edit | not_better | 0.9410 | 0.9414 | $0.0006 | I'll make the sweet-spot fraction itself adaptive: keep the proven target-residual base but repla... |
| 91 | edit | not_better | 0.9399 | 0.9414 | $0.0006 | Keep the proven target-residual base, but make the completion bonus use a smooth, mean-scaled thr... |
| 92 | edit | not_better | 0.7189 | 0.9414 | $0.0006 | I'll replace the fixed additive tight-fit bonus with a lexicographic two-key ranking: bins whose ... |
| 93 | edit | not_better | 0.9410 | 0.9414 | $0.0006 | I'll keep the proven target-residual base and tight-fit bonus, but add a small "perfect-fit prior... |
| 94 | edit | not_better | 0.9377 | 0.9414 | $0.0006 | I'll keep the proven target-residual base but replace the global running mean with a windowed/dec... |
| 95 | edit | not_better | 0.9381 | 0.9414 | $0.0006 | I'll replace the hardcoded sweet-spot target with a principled "best-fit with lookahead" score th... |
| 96 | edit | not_better | 0.9349 | 0.9414 | $0.0005 | I'll replace the ad-hoc target-residual rule with the classic Best-Fit-Decreasing-style choice (s... |
| 97 | edit | not_better | 0.9349 | 0.9414 | $0.0006 | The tight-fit window is too aggressive (fixed residual ≤ 8), which locks small residuals early an... |
| 98 | edit | not_better | 0.9399 | 0.9414 | $0.0006 | I'll keep the proven target-residual base and tight-fit bonus, but tune the tight-fit window and ... |
| 99 | edit | not_better | 0.9349 | 0.9414 | $0.0006 | I will replace the hard tight-fit bonus with a rank-preserving two-tier score that first seeks th... |
| 100 | edit | improved | 0.9423 | 0.9423 | $0.0007 | I will derive the sweet-spot target from a running estimate of the item distribution's mean and s... |
| 101 | edit | not_better | 0.9349 | 0.9423 | $0.0007 | Replace the additive tight bonus with a lexicographic-style score: encode best-fit residual with ... |
| 102 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | I'll keep the target-residual sweet-spot base but replace the ad hoc multiplicative tight-fit bon... |
| 103 | edit | not_better | 0.7902 | 0.9423 | $0.0006 | I will replace the running mean/sd "target residual" heuristic with a learned estimate of the ite... |
| 104 | edit | not_better | 0.9358 | 0.9423 | $0.0006 | The current rule uses an absolute target residual (0.90*mean + 0.15*sd), but the sweet spot shoul... |
| 105 | edit | not_better | 0.9384 | 0.9423 | $0.0006 | (no description) |
| 106 | edit | not_better | 0.9381 | 0.9423 | $0.0006 | I'll keep the proven target-residual base but replace the arbitrary additive tight-fit bonus with... |
| 107 | edit | not_better | 0.9414 | 0.9423 | $0.0006 | I will add a "concentration" bonus that rewards using already-open, partially-filled bins over fr... |
| 108 | edit | not_better | 0.9349 | 0.9423 | $0.0008 | I will replace the fixed 0.90*mean+0.15*sd target with a principled expected-waste target: for ea... |
| 109 | edit | not_better | 0.7082 | 0.9423 | $0.0006 | I'll replace the fixed additive tight-fit bonus with a smooth, always-active best-fit preference ... |
| 110 | edit | not_better | 0.9349 | 0.9423 | $0.0007 | I'll improve the target-residual sweet spot by estimating the item distribution's terciles from p... |
| 111 | edit | not_better | 0.9414 | 0.9423 | $0.0006 | I will keep the proven target-residual base but let the target adapt to the current item's size b... |
| 112 | edit | not_better | 0.9349 | 0.9423 | $0.0005 | I'll replace the learned mean/sd target with a small set of fixed quantile-based targets and add ... |
| 113 | edit | not_better | 0.9407 | 0.9423 | $0.0006 | The strongest known bin-packing heuristic is a scaled "best fit" that targets a small residual ra... |
| 114 | edit | not_better | 0.9399 | 0.9423 | $0.0006 | I'll make the completion bonus slope scale with the item size, so large items decisively prefer n... |
| 115 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | I'll sharpen the main score by using a steeper (quadratic-in-deviation) penalty instead of the li... |
| 116 | edit | not_better | 0.9416 | 0.9423 | $0.0006 | I'll make the target residual depend on the arriving item's size using a simple convex blend that... |
| 117 | edit | not_better | 0.9353 | 0.9423 | $0.0006 | I'll keep the proven target-residual base score but replace the discontinuous `np.where` tight-fi... |
| 118 | edit | not_better | 0.9358 | 0.9423 | $0.0007 | Blend the proven target (0.90*mean+0.15*sd) with the item's own complement gap (100-item), so ite... |
| 119 | edit | not_better | 0.9418 | 0.9423 | $0.0006 | I will add a mild "avoid leaving a residual that is smaller than the smallest likely item" penalt... |
| 120 | edit | not_better | 0.9420 | 0.9423 | $0.0006 |  |
| 121 | edit | not_better | 0.7977 | 0.9423 | $0.0006 | I'll add a smooth, bounded completion bonus that grows as the residual approaches zero (scaled to... |
| 122 | edit | not_better | 0.9412 | 0.9423 | $0.0005 | I'll replace the fixed target with a "best-fit within a class" approach: rank bins by the classic... |
| 123 | edit | not_better | 0.9410 | 0.9423 | $0.0006 | I'll add an adaptive "residual waste" guard: bins whose residual is too small to fit the current ... |
| 124 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | The previous attempts all tweaked the target/bonus and lost ground; instead I'll return to the ex... |
| 125 | edit | not_better | 0.9412 | 0.9423 | $0.0006 | Replace the fixed sweet-spot target with a per-item adaptive target based on the current item's s... |
| 126 | edit | not_better | 0.8600 | 0.9423 | $0.0006 | I'll fit the target residual to the observed distribution of item sizes rather than a fixed linea... |
| 127 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | I'll remove the extra "tight" completion-bonus term (which recent ablations show perturbs the pro... |
| 128 | edit | not_better | 0.9412 | 0.9423 | $0.0005 | I'll tune the target residual to use a slightly larger weight on the standard deviation and shift... |
| 129 | edit | not_better | 0.9349 | 0.9423 | $0.0007 | I'll replace the heuristic sweet-spot with a proper "best fit in the smallest viable bin" rule: r... |
| 130 | edit | not_better | 0.9112 | 0.9423 | $0.0005 | I'll switch from a fixed residual sweet spot to a classic best-fit rule but with an adaptive mini... |
| 131 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | I'll keep the proven target-residual base but make the target item-size-aware in a targeted way: ... |
| 132 | edit | not_better | 0.9178 | 0.9423 | $0.0008 | I'll replace the fixed linear residual sweet spot with a principled target derived from the empir... |
| 133 | edit | not_better | 0.9412 | 0.9423 | $0.0007 | I'll add a term that blends the target-residual ranking with a best-fit (smallest-residual) ranki... |
| 134 | edit | not_better | 0.7370 | 0.9423 | $0.0006 | Replace the hard-stepped "tight" bonus with a smooth Gaussian-like bonus centered slightly below ... |
| 135 | edit | not_better | 0.9368 | 0.9423 | $0.0006 | The residual target currently ignores how many bins are still empty; early in a stream when many ... |
| 136 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | I'll refine the tight-completion bonus into a narrowly targeted "exact fill" reward: strongly pre... |
| 137 | edit | not_better | 0.9351 | 0.9423 | $0.0006 | I'll replace the hard 0.90*mean target with an adaptive target that shifts toward classic best-fi... |
| 138 | edit | not_better | 0.9423 | 0.9423 | $0.0007 | Add a narrow exact-fit bonus that strongly prefers residuals in a small window near 0 (where an i... |
| 139 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | The current rule lets a large item go into a bin whose residual is far from the item size, fragme... |
| 140 | edit | not_better | 0.9300 | 0.9423 | $0.0010 | I'll scale the completion bonus adaptively: instead of a fixed huge constant that dominates the t... |
| 141 | edit | not_better | 0.9399 | 0.9423 | $0.0006 | I'll replace the absolute-residual sweet-spot ranking with a "best fit decreasing-ish" hybrid tha... |
| 142 | edit | not_better | 0.9366 | 0.9423 | $0.0006 | The current hard `tight` bonus only rewards residuals ≤ 10 with a constant jump, ignoring whether... |
| 143 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | The current rule completely ignores the case where an item can nearly fill a bin from the "top" s... |
| 144 | edit | not_better | 0.9414 | 0.9423 | $0.0011 | I'll switch the sweet-spot target from a slightly-sub-mean value (0.90*mean + 0.15*sd) to the ful... |
| 145 | edit | not_better | 0.9403 | 0.9423 | $0.0007 | I'll replace the hard-coded sweet-spot target with a value matched to the conditional expected si... |
| 146 | edit | not_better | 0.7997 | 0.9423 | $0.0006 | I'll replace the crude `tight` completion bonus with a small-term that strongly rewards near-exac... |
| 147 | edit | not_better | 0.7462 | 0.9423 | $0.0006 | I'll reframe scoring as an approximate "expected future waste" estimate: score each bin by the ne... |
| 148 | edit | not_better | 0.7405 | 0.9423 | $0.0006 | I'll replace the saturating `tight` bonus (a flat 4e4 cap that creates a discontinuous jump rewar... |
| 149 | edit | not_better | 0.9405 | 0.9423 | $0.0006 | I'll add a tie-breaking amplification term that treats the best-fit residual as an almost-linear ... |
| 150 | edit | not_better | 0.9423 | 0.9423 | $0.0006 | I'll replace the current rule with a "best-fit with a residual-range sweet spot" that combines th... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,36 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Target-residual best fit with a distribution-derived sweet spot."""
 import numpy as np
+
+_TOTAL = 0
+_COUNT = 0
+_SQ = 0.0
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
+    global _TOTAL, _COUNT, _SQ
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    _TOTAL += item
+    _COUNT += 1
+    _SQ += float(item) * item
+    mean = _TOTAL / _COUNT
+    var = max(_SQ / _COUNT - mean * mean, 0.0)
+    sd = var ** 0.5
+
+    residual = bins - item
+
+    if _COUNT >= 30:
+        # Target residual: aim to leave a gap a typical item can fill.  A slightly
+        # sub-mean target reduces large residual waste for skewed (Weibull) sizes.
+        target = 0.90 * mean + 0.15 * sd
+    else:
+        target = 38.0
+
+    score = -np.abs(residual - target)
+
+    # Gentle completion bonus: reward small residuals, but with a softer slope so
+    # medium bins aren't starved of items that would land near the sweet spot.
+    tight = np.where(residual <= 10, 4e4 - residual * 2e3, 0.0)
+    return score + tight
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (19 parts, 38 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 12 | `global _TOTAL, _COUNT, _SQ` | -0.9423 | essential: the program fails or turns invalid without it |
| 15 | `_COUNT += 1` | -0.9423 | essential: the program fails or turns invalid without it |
| 17 | `mean = _TOTAL / _COUNT` | -0.9423 | essential: the program fails or turns invalid without it |
| 18 | `var = max(_SQ / _COUNT - mean * mean, 0.0)` | -0.9423 | essential: the program fails or turns invalid without it |
| 21 | `residual = bins - item` | -0.9423 | essential: the program fails or turns invalid without it |
| 21 | `term + bins` | -0.9423 | essential: the program fails or turns invalid without it |
| 23 | `if _COUNT >= 30: ...` | -0.9423 | essential: the program fails or turns invalid without it |
| 26 | `target = 0.9 * mean + 0.15 * sd` | -0.9423 | essential: the program fails or turns invalid without it |
| 28 | `target = 38.0` | -0.9423 | essential: the program fails or turns invalid without it |
| 30 | `score = -np.abs(residual - target)` | -0.9423 | essential: the program fails or turns invalid without it |
| 34 | `tight = np.where(residual <= 10, 40000.0 - residual * 2000.0, 0.0)` | -0.9423 | essential: the program fails or turns invalid without it |
| 35 | `term + tight` | -0.2111 | matters |
| 21 | `term - item` | -0.0343 | matters |
| 35 | `term + score` | -0.0061 | matters |
| 14 | `_TOTAL += item` | -0.0033 | matters |
| 26 | `term + 0.9 * mean` | -0.0033 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 16: `_SQ += float(item) * item`
- line 19: `sd = var ** 0.5`
- line 26: `term + 0.15 * sd`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9423 | 0.9683 |
| minimal (3 parts removed) | 0.9407 | 0.9695 |

Minimal program:

```python
"""Target-residual best fit with a distribution-derived sweet spot."""
import numpy as np
_TOTAL = 0
_COUNT = 0
_SQ = 0.0

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _TOTAL, _COUNT, _SQ
    _TOTAL += item
    _COUNT += 1
    mean = _TOTAL / _COUNT
    var = max(_SQ / _COUNT - mean * mean, 0.0)
    residual = bins - item
    if _COUNT >= 30:
        target = 0.9 * mean
    else:
        target = 38.0
    score = -np.abs(residual - target)
    tight = np.where(residual <= 10, 40000.0 - residual * 2000.0, 0.0)
    return score + tight
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_c80 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 2
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_c80-s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_c80/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_c80/initial.py` `609927c5ea619a94`
- `problems/bp_sh_c80/problem.md` `190017a698e23cd8`
- `problems/bp_sh_c80/verify.py` `dc0d05d86db9dbf0`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
