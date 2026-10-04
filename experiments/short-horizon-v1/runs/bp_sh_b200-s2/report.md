# Research loop report: bp_sh_b200

| | |
|---|---|
| problem | `bp_sh_b200` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0791 of a $0.20 hard cap, 150 calls, 275,183 tokens |
| wall time | search 1353 s, baselines 53 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 150 (145 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9444 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9444 | 0.9634 |  |
| baseline `funsearch_or` | 0.9552 | 0.9711 | `problems/bp_sh_b200/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.8723 | 0.9937 | `problems/bp_sh_b200/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9200 | 0.9950 | `problems/bp_sh_b200/baselines/sum_of_squares.py` |

Audit: public 0.9444 → 0.9444 (+0.0000), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program -0.0190.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9552). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9444 | 0.9444 | $0.0003 | The plain best-fit rule ignores that putting an item into an empty (capacity-100) bin wastes a fr... |
| 2 | edit | not_better | 0.7330 | 0.9444 | $0.0004 | I'll add a standing statistic of the mean arriving item size and bias bins toward a target residu... |
| 3 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Introduce a two-parameter best-fit adjustment: subtract a small bonus proportional to bin fullnes... |
| 4 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Replace pure best-fit with a linear-utility rule that maximizes the sum of remaining capacity aft... |
| 5 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a "best-fit decreasing-like" rule that breaks ties among equally-tight... |
| 6 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Pure best-fit is essentially optimal for online packing of small items, but a subtle improvement ... |
| 7 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch from pure best-fit to a "best-fit with waste minimization" rule that scores bins by t... |
| 8 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Introduce a lightweight "almost-full first, then best-fit" rule: strongly prefer the existing bin... |
| 9 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll try a "harmonic/interval-aware best fit" rule: among bins that fit, prefer the one whose rem... |
| 10 | edit | not_better | 0.7199 | 0.9444 | $0.0005 | Replace pure best-fit with a bounded, stateful "grade" rule: maintain a running estimate of the i... |
| 11 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Best-fit is already strong, so I will add a light tie-breaking refinement: score bins by residual... |
| 12 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I will replace best-fit with a "best-fit for small items, but reserve a mostly-empty bin for larg... |
| 13 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch to a "best-fit with a randomized multi-bin reservation" strategy: maintain a running ... |
| 14 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement the classic "Harmonic++"-style interval packing for small items: bin indices are g... |
| 15 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll keep best-fit but add a stateful "reservation" trick: track the smallest item seen recently ... |
| 16 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a "match the residual to item size" rule: score each fitting bin ... |
| 17 | edit | not_better | 0.7597 | 0.9444 | $0.0004 | Replace best-fit with a "residual-matching" rule: for each fitting bin, score by how close its po... |
| 18 | edit | not_better | 0.8082 | 0.9444 | $0.0006 | I will keep pure best-fit (which already scores ~0.944) but add a small stateful improvement: tra... |
| 19 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll add a stateful "smart best-fit with leftover-packing" tweak: use best-fit normally, but when... |
| 20 | edit | not_better | 0.8431 | 0.9444 | $0.0005 | I'll keep pure best-fit but add a stateful tweak: track a running count and mean of items, and wh... |
| 21 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with a "best-fit with a tunable waste penalty that depends on the item... |
| 22 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with "best-fit among bins whose post-placement residual is less than t... |
| 23 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll implement a proper online bin-packing rule combining best-fit with a "harmonic"-style guard:... |
| 24 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch from pure best-fit to a "best-fit with a two-size-class harmonic guard": maintain a r... |
| 25 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a ranked rule that first places items into a well-fitting partial... |
| 26 | edit | not_better | 0.9442 | 0.9444 | $0.0005 | I'll replace pure best-fit with a size-aware two-mode rule: estimate the maximum item size seen s... |
| 27 | edit | not_better | 0.9347 | 0.9444 | $0.0005 | Replace pure best-fit with a rule that combines best-fit for tight packing with a "sum-of-squares... |
| 28 | edit | invalid | 0.0000 | 0.9444 | $0.0007 | Replace pure best-fit with a size-aware rule that maintains a running histogram of item sizes: fo... |
| 29 | edit | not_better | 0.9173 | 0.9444 | $0.0006 | I'll replace pure best-fit with a rule that reserves finer granularity: when an item would exactl... |
| 30 | edit | not_better | 0.9419 | 0.9444 | $0.0005 | Replace pure best-fit with a "best fit decreasing-aligned" rule that combines best-fit with a tie... |
| 31 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | The current best-fit ties break toward the first (earliest) bin, which tends to keep old bins wit... |
| 32 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a hybrid rule: for each bin compute best-fit residual, but add a ... |
| 33 | edit | invalid | 0.0000 | 0.9444 | $0.0005 | Pure best-fit ignores the total remaining capacity in each bin's neighbourhood: an item of size s... |
| 34 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Keep best-fit as the primary rule, but within a small tolerance band (residuals differing by ≤1) ... |
| 35 | edit | not_better | 0.9173 | 0.9444 | $0.0005 | I'll replace pure best-fit with a "shelf-aware" rule: track a running estimate of the smallest it... |
| 36 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a harmonic/adaptive scoring rule: score each bin by maximizing the fra... |
| 37 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll switch from pure best-fit to a harmonic-style rule that penalizes the size of the residual g... |
| 38 | edit | not_better | 0.8912 | 0.9444 | $0.0005 | Replace pure best-fit with Almost-Worst-Fit on a smoothed fill level: score bins by how close the... |
| 39 | edit | not_better | 0.9422 | 0.9444 | $0.0005 | I'll switch from pure best-fit to a "best-fit with a fill-level preference" hybrid: among bins th... |
| 40 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll add a log-scale "harmonic" bonus to best fit: score = -log1p(residual_after_placement) plus ... |
| 41 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll switch from pure best-fit to a tie-broken best-fit that, among bins leaving an identical pos... |
| 42 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a scale-free "best fit by relative residual" rule: score bins by -resi... |
| 43 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll replace pure best-fit with a two-regime rule: prefer an exact-fit bin (residual 0) if availa... |
| 44 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a best-fit-plus-"leave-a-fittable-gap" rule: score bins so that a... |
| 45 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a "minimum bin usage" rule: prefer placing the item into an alrea... |
| 46 | edit | not_better | 0.3990 | 0.9444 | $0.0005 | I'll combine best-fit with the classic "sum of squares" / harmonic idea used in online bin packin... |
| 47 | edit | no_code | n/a | 0.9444 | $0.0003 | I'll combine best-fit with a smart-capacity filter: reject bins whose post-placement residual is ... |
| 48 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a "worst-fit among the better half" hybrid: keep best-fit as the ... |
| 49 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Replace pure best-fit with a "fullest-fit" variant: among bins that can hold the item, prefer the... |
| 50 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a "best-fit with exact-fit/almost-full prioritization plus a full... |
| 51 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a fractional-style potential rule: score each bin by how full it ... |
| 52 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll add a random tie-breaking "chance of opening a new bin" via a deterministic hash-based pertu... |
| 53 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement a "best-fit with exact-fit bonus and refusal of wasteful bins": prefer exact fits ... |
| 54 | edit | not_better | 0.8916 | 0.9444 | $0.0006 | I'll use Best-Fit but with a learned adaptive threshold: since item sizes are Weibull-shaped (mea... |
| 55 | edit | not_better | 0.9428 | 0.9444 | $0.0006 | I will implement the classic "Best-Fit with a lookahead-free harmonic-style split": instead of pu... |
| 56 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Best-fit wastes small leftovers; I'll add a secondary term that mildly prefers bins whose post-pl... |
| 57 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Replace pure best-fit with a hybrid that uses the "harmonic" split: for small items (≤ capacity/2... |
| 58 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with a "best-fit-decreasing-aware" rule that also avoids leaving unusa... |
| 59 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll implement a learned "capacity-class" best-fit: track the running histogram of item sizes, an... |
| 60 | edit | not_better | 0.9415 | 0.9444 | $0.0005 | Use a tuned variant of best-fit with a small exact-fit bonus and a mild penalty for leaving a nea... |
| 61 | edit | not_better | 0.9431 | 0.9444 | $0.0005 | Replace pure best-fit with a "worst-fit for large items, best-fit for small items" hybrid: the we... |
| 62 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch from pure best-fit to a "best-fit with class-based residual reuse" rule: score each b... |
| 63 | edit | not_better | 0.3990 | 0.9444 | $0.0005 | I'll replace best-fit with a "least-loaded-suitable" (worst-fit-like) rule that spreads items int... |
| 64 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll add a learned size-distribution model: track counts of item sizes seen so far and, for each ... |
| 65 | edit | not_better | 0.9413 | 0.9444 | $0.0005 | I'll switch the base rule to a randomized/adaptive "best-fit with a small worst-fit escape": with... |
| 66 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a small-size-aware hybrid: use best-fit (tightest fit) as the pri... |
| 67 | edit | not_better | 0.9437 | 0.9444 | $0.0006 | I'll switch to a fractional/adaptive "best fit with residual-quality learning" that learns which ... |
| 68 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll switch from pure best-fit to a "best-fit among the two tightest candidates" rule: find the b... |
| 69 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace the pure best-fit score with a scale-aware hybrid: for small items use best-fit (tig... |
| 70 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll add a tie-breaking refinement to best-fit: keep best-fit as the primary rule but, among bins... |
| 71 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll add a one-step lookahead via the empirical size distribution: after trial-placing the item i... |
| 72 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace best-fit with a harmonic-style rule: score each bin by how full it would become using a d... |
| 73 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Add a lightweight online learned "waste penalty" to best-fit: keep best-fit as the backbone by sc... |
| 74 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace best-fit with a bounded "best-fit with periodic cap" rule inspired by ACO/harmonic b... |
| 75 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace the simple best-fit backbone with a "best-fit that prefers the fullest bin" rule: score b... |
| 76 | edit | not_better | 0.9444 | 0.9444 | $0.0007 | I'll implement a size-class-aware two-choice rule: route items into capacity classes inspired by ... |
| 77 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch the backbone rule from best-fit to a "best-fit with a residual-viability bonus": scor... |
| 78 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with a "harmonic-class best-fit" that quantizes the post-placement res... |
| 79 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I will switch the bin-selection backbone from best-fit to a rank-based "worst-viable-fit with emp... |
| 80 | edit | invalid | 0.0000 | 0.9444 | $0.0006 | (no description) |
| 81 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Replace best-fit with a score that strongly prefers partially-used bins over fresh empty bins (de... |
| 82 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Add an exact-fit dominance: score bins so that a bin filled exactly (residual 0 after placement) ... |
| 83 | edit | not_better | 0.8867 | 0.9444 | $0.0005 | I'll replace pure best-fit with a two-choice rule that combines best-fit (tightest residual) for ... |
| 84 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | The current best-fit is essentially optimal for this distribution; I'll add a "complement matchin... |
| 85 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll keep best-fit as the backbone but break near-ties using a conservative "perfect-packing" pre... |
| 86 | edit | not_better | 0.9444 | 0.9444 | $0.0007 | I'll replace pure best-fit with a "best-fit decreasing-aware" rule that maintains an online estim... |
| 87 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace the pure best-fit rule with a randomized two-choice hybrid: with high probability us... |
| 88 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a "best fit with critical-item reservation" rule: maintain an onl... |
| 89 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | The current best-fit is strong, but it opens new bins too often. I'll add a complementary-items h... |
| 90 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll add a small stateful "deferred-use" bias: maintain a running count of how many times each bi... |
| 91 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with a bounded "best-fit + residue-complement" rule: keep best-fit as ... |
| 92 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Pure best-fit is already near-optimal, but it ignores that the very last items each stream (which... |
| 93 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Replace pure best-fit with a two-choice rule: maintain an online histogram of item sizes and, for... |
| 94 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit (which is already near-optimal) by keeping best-fit as the main criter... |
| 95 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with a "best-fit with a small lookahead-free complementary bonus": sco... |
| 96 | edit | not_better | 0.9444 | 0.9444 | $0.0007 | I'll replace pure best-fit with a calibrated score that combines best-fit residual with a penalty... |
| 97 | edit | not_better | 0.3990 | 0.9444 | $0.0006 | I'll try a practical improvement over pure best-fit: use "best fit decreasing"-like behavior with... |
| 98 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a "best-fit with residual-complement grace" rule: primary key is the b... |
| 99 | edit | not_better | 0.9402 | 0.9444 | $0.0005 | I'll replace pure best-fit with a threshold-based "match the residual to the item" rule: when an ... |
| 100 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll add a tiny, conservative secondary term to best-fit that prefers leaving a residual close to... |
| 101 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with the well-known "best fit with a birthday/score-ratio" idea that a... |
| 102 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll add a bounded, self-resetting free-space "waste" penalty: track the multiset of current resi... |
| 103 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace the near-optimal-but-static best-fit rule with an adaptive "matching best-fit" rule:... |
| 104 | edit | not_better | 0.9228 | 0.9444 | $0.0007 | Replace pure best-fit with an adaptive "least-loaded-but-fitting / reserve-small-scraps" hybrid: ... |
| 105 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best fit (which can strand small unusable scraps) with a "best fit with worst-fit es... |
| 106 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I will switch from pure best fit to a “best-fit with tiny-scrap avoidance by residual complement”... |
| 107 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll implement a "reserve bins for typical items" rule: rank bins by best-fit (tightest residual ... |
| 108 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Replace the pure best-fit (tightest residual) rule with an adaptive scoring rule that minimizes i... |
| 109 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Switch from pure best fit to a bounded "best fit plus exact-complement bonus" rule: keep best fit... |
| 110 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Best-fit alone is already near-optimal here; I'll add a small, bounded "exact-fit" bonus to break... |
| 111 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll test whether the score is limited by a flat best-fit tie region: switch the primary rule to ... |
| 112 | edit | not_better | 0.3990 | 0.9444 | $0.0005 | Replace pure best-fit with the "Sum of Squares" (SS) heuristic, ranking bins by the reduction in ... |
| 113 | edit | not_better | 0.4062 | 0.9444 | $0.0006 | I will use a hybrid rule that switches between Best Fit (tightest residual) and Worst Fit (most r... |
| 114 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace the pure best-fit tie-breaking with a "best fit, but break near-ties by preferring t... |
| 115 | edit | not_better | 0.9433 | 0.9444 | $0.0006 | I will replace pure best-fit with a hybrid of Best Fit and an online learned "match residual to f... |
| 116 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll try a rule that keeps best-fit as the primary key but, among the tie/near-tie region of tigh... |
| 117 | edit | invalid | 0.0000 | 0.9444 | $0.0008 | Replace pure best fit with a bid-price rule where each bin's score is the immediate tightness plu... |
| 118 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll make best-fit's tie-break a small, scale-free bonus proportional to how close the post-place... |
| 119 | edit | not_better | 0.9444 | 0.9444 | $0.0007 | Keep best-fit as the primary key, but among placements whose residual falls within a small window... |
| 120 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll implement the classic online heuristic Best Fit Decreasing is not available online, but Harm... |
| 121 | edit | not_better | 0.9444 | 0.9444 | $0.0010 | Replace pure best-fit with a version that keeps tightest-fit as the primary criterion but applies... |
| 122 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with the classic "Best Fit with a reserved slack" idea: keep tightest-... |
| 123 | edit | not_better | 0.9444 | 0.9444 | $0.0005 |  |
| 124 | edit | invalid | 0.0000 | 0.9444 | $0.0006 | I'll replace pure best-fit with a rule that adds a small "future-fit bonus": keep tightest fit as... |
| 125 | edit | not_better | 0.7388 | 0.9444 | $0.0006 | I'll replace pure best fit with a threshold rule: first try best fit, but if the tightest fit wou... |
| 126 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a randomized-dither variant: keep best-fit as the main key but br... |
| 127 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll try a genuine improvement to best fit: prefer exact fits, then bins whose residual after pla... |
| 128 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best fit with a two-key rule: primary is best fit (tightest residual), but I ad... |
| 129 | edit | not_better | 0.5695 | 0.9444 | $0.0005 | I'll switch from pure best-fit to a "worst-fit among bins that still leave room for a typical ite... |
| 130 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Best-fit is hard to beat; add a tiny, size-scaled "exact-fill bonus" so bins that the item fills ... |
| 131 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a bounded "lookahead-free" variant: keep best-fit tightness as the mai... |
| 132 | edit | not_better | 0.8396 | 0.9444 | $0.0006 | I will replace pure best-fit with a well-known stronger online rule: "best fit with a reserved-th... |
| 133 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll use a harmonic-style "Best Fit Decreasing surrogate": primary key is best fit, but break tie... |
| 134 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Switch from best-fit to a "least loaded bin that still fits" (worst-fit) only when the item is sm... |
| 135 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement a two-regime rule: for large items (>= mean item size), use pure best fit (tightes... |
| 136 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll add a tiny tie-breaking perturbation to pure best-fit: rescaled residual closeness to a "goo... |
| 137 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I will replace pure best-fit with a quadratic-cost rule: score each bin by the resulting residual... |
| 138 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a two-regime score: for items large relative to the typical size keep ... |
| 139 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Pure best-fit is already near-optimal for the score; instead of perturbing its ordering, I'll add... |
| 140 | edit | not_better | 0.9444 | 0.9444 | $0.0007 | Pure best-fit is already optimal here, so I'll switch to a genuinely different known-stronger onl... |
| 141 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Replace pure best-fit with a "best-fit with exact-fit bonus" rule that also considers the smalles... |
| 142 | edit | not_better | 0.9391 | 0.9444 | $0.0006 | Replace best-fit with a tuned two-parameter scoring rule that weights residual and full-bin value... |
| 143 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Exploit the structure of the Weibull item stream: instead of pure best-fit, use a "rank by residu... |
| 144 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Pure best-fit is already hard to beat locally, so I'll add a wedge-based improvement: use the cla... |
| 145 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I will switch from pure best-fit to a "worst-fit among bins with small residual" hybrid: compute ... |
| 146 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement a rank-based rule that is still best-fit in spirit but breaks ties among bins with... |
| 147 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a harmonic-style "bin-packing-aware" rule that mimics the classic... |
| 148 | edit | not_better | 0.9362 | 0.9444 | $0.0006 | Pure best-fit ignores how full a bin becomes, which matters for the Weibull mean-40 stream. I'll ... |
| 149 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Add a small deterministic "age" tie-break: keep a persistent counter of arrivals and, among bins ... |
| 150 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement "best fit with a bounded residual window": still prefer the tightest fit, but amon... |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Skipped: priority has nothing to remove (a single return without a +/- chain).

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_b200 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 2
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_b200-s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_b200/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_b200/initial.py` `609927c5ea619a94`
- `problems/bp_sh_b200/problem.md` `190017a698e23cd8`
- `problems/bp_sh_b200/verify.py` `55fde4c12c8b08c5`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
