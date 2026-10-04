# Research loop report: bp_sh_e_rand

| | |
|---|---|
| problem | `bp_sh_e_rand` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0844 of a $0.20 hard cap, 150 calls, 286,215 tokens |
| wall time | search 1672 s, baselines 83 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (148 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9727 | 0.9634 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_e_rand/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_e_rand/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_e_rand/baselines/sum_of_squares.py` |

Audit: public 0.9727 → 0.9727 (+0.0000), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program 0.0093.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0003 | I'll replace pure best-fit with a best-fit-dominant rule that still prefers tightest fit but adds... |
| 2 | edit | not_better | 0.9727 | 0.9727 | $0.0003 | Replace pure best-fit with a "best fit except reserve one empty bin" strategy: use best fit among... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll replace pure best-fit with a fractional/adaptive rule that keeps best-fit dominance but give... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a parameterized "best-fit-decreasing-like" rule that blends tightest-f... |
| 5 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with a "worst-fit among bins that leave a small residual, else best-fit" hy... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Reframe the rule as a scaled "best-fit" with a tie-breaking bonus for bins that currently sit exa... |
| 7 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Introduce state to track average item size and use a "best fit with a harmonic-style residual pen... |
| 8 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add per-stream state that emulates a restricted "best fit decreasing"-style lookahead: track... |
| 9 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a near-optimal "best fit with a lookahead-aware residual bonus": score... |
| 10 | edit | not_better | 0.9710 | 0.9727 | $0.0005 | Replace pure best-fit with a rule that mimics the "Modified First Fit Decreasing" / harmonic pack... |
| 11 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a rule that keeps best-fit as the primary key but adds a secondary tie... |
| 12 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add mild per-stream state that tracks the average item size and apply a small score adjustment on... |
| 13 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Implement a size-class / harmonic bin packing rule: precompute item size class boundaries (like h... |
| 14 | edit | not_better | 0.9713 | 0.9727 | $0.0005 | Replace pure best-fit with the classic "best fit with a small lookahead-style bonus for exact res... |
| 15 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement the classic Best Fit with a "fuller-bin-first" secondary key: primary = maximize p... |
| 16 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace best-fit with a "least-loaded fitting bin" rule only when the item is large (>= 50), and ... |
| 17 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a harmonic/class-based rule: partition capacity into geometric size cl... |
| 18 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace the pure best-fit primary key with "best fit among the bins that, after placement, either... |
| 19 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a hybrid that behaves like best-fit for most items but, for large item... |
| 20 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a proper "Best Fit Decreasing"-style harmonic class rule: classify each item by it... |
| 21 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace best-fit with a subtype of the "Modified First Fit" / "Best Fit with reserve" idea: keep ... |
| 22 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best fit with "best fit plus multi-capacity residual matching": primary is still the... |
| 23 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | The prior "modified/best-fit" hybrids all scored the same, so I'll change the tie-breaking in a w... |
| 24 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best fit alone wastes the "least full" bins. I'll switch to a score that combines fit quality wit... |
| 25 | edit | not_better | 0.7639 | 0.9727 | $0.0008 | I will replace pure best-fit with a size-class (harmonic-style) rule that also keeps bins "reserv... |
| 26 | edit | gate_rejected | 0.9841 | 0.9727 | $0.0006 | Replace the fixed best-fit key with an adaptive rule: track the running distribution of item size... |
| 27 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the fixed best-fit score with a smooth "fill to a likely residual" rule: track a running ... |
| 28 | edit | not_better | 0.9637 | 0.9727 | $0.0007 | I'll implement a proper harmonic-style size-class rule where bins are tagged by the class of item... |
| 29 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll make the priority strictly best-fit but with a tiny, deterministic tie-break that favors fil... |
| 30 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with "best fit decreasing-style lookahead": score bins primarily by sm... |
| 31 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "reserve large bins" best-fit variant: pure best-fit but with a small additive bonus f... |
| 32 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "best fit with exact-size matching priority" that first checks, for each bin, wh... |
| 33 | edit | not_better | 0.9024 | 0.9727 | $0.0005 | Replace pure best-fit with a two-segment scoring: for large items (>= ~some threshold) use pure b... |
| 34 | edit | not_better | 0.9727 | 0.9727 | $0.0010 | I'll keep pure best-fit as the dominant term but add a bounded secondary preference: when the ite... |
| 35 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch from pure best-fit to a "worst-fit among bins that leave a residual that can still fi... |
| 36 | edit | not_better | 0.9727 | 0.9727 | $0.0010 | Replace the pure best-fit score with a best-fit primary plus a tiny bounded secondary term that r... |
| 37 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The pure best-fit baseline at 0.9727 appears near the practical limit for a purely myopic rule on... |
| 38 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the myopic best-fit rule with a bounded "least-loaded among tolerable residuals" rule: pr... |
| 39 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will add a small bounded tie-break that favors closing a bin exactly or leaving a residual that... |
| 40 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try "best fit but never exactly fill to zero unless the item is large": prefer the smallest ... |
| 41 | edit | not_better | 0.9364 | 0.9727 | $0.0006 | Best fit ties among many bins with identical remaining capacity; I'll bias that tie by preferring... |
| 42 | edit | not_better | 0.8729 | 0.9727 | $0.0005 | Best-fit closes bins too early; I'll add a stateful "reserve-fraction" rule: for items not large ... |
| 43 | edit | invalid | 0.0000 | 0.9727 | $0.0006 | I'll add a stateful "match-to-complement" tie-break on top of best-fit: keep a running histogram ... |
| 44 | edit | invalid | 0.0000 | 0.9727 | $0.0005 | I'll replace pure best-fit with a one-step "best fit with dual-bin packing" heuristic: keep best-... |
| 45 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll keep best-fit as the primary key, but add a deterministic stateful tie-break: track a runnin... |
| 46 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The improvements are likely to come from not always making the greedy best-fit choice. I'll imple... |
| 47 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch from one-step best-fit to a bounded one-step lookahead "subset-sum awareness": mainta... |
| 48 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a size-class-aware rule: for large items (≥60) use strict best-fit to ... |
| 49 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add a stateful bin-index-aware tie-break to best-fit: track the running mean item size and, when ... |
| 50 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Introduce a stateful "reserve and pair" rule: keep an exponentially weighted mean of recent items... |
| 51 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with a "best-fit with a one-step harmonic bonus": keep best-fit as the... |
| 52 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replacing pure best-fit with a two-parameter family is risky, but the feedback shows all my local... |
| 53 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best-fit is already near-optimal for most items; the main loss on long streams is that small item... |
| 54 | edit | not_better | 0.9489 | 0.9727 | $0.0005 | I will replace the pure best-fit rule with a two-parameter "reserve" family: for small items (bel... |
| 55 | edit | not_better | 0.9401 | 0.9727 | $0.0008 | I'll switch from best-fit to a "global bin-packing with recency-weighted harmonic matching" rule:... |
| 56 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will replace pure best-fit with a conservative "best-fit + tiny future-fit bonus": keep the int... |
| 57 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from best-fit to a two-key rule: primary key is best fit, but for items that are larg... |
| 58 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Pure best-fit is hard to beat, so I'll make a targeted, low-risk tweak: use best-fit for all item... |
| 59 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try a classic and effective online improvement over pure best-fit: apply best-fit but forbid... |
| 60 | edit | not_better | 0.9716 | 0.9727 | $0.0006 | I'll switch to a convex-combination scoring rule that blends best-fit with a "reserve" bias: scor... |
| 61 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "Best-Fit with lookahead for leftover" rule based on a running estimate of the n... |
| 62 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will add a state-dependent "aging" tie-break to best-fit: track how many items each bin slot ha... |
| 63 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll add a "reserve" rule that combines best-fit with a modest bonus for leaving a residual that ... |
| 64 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll implement a scaled best-fit that leaves a "reserve" with a logarithmic penalty on residual c... |
| 65 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace the pure best-fit score with a probabilistic "reuse value" score: keep best-fit as the do... |
| 66 | edit | invalid | 0.0000 | 0.9727 | $0.0005 | I'll implement a proper "least-loaded / wider-bin" variant: best-fit ties (equal residual) are co... |
| 67 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit decreasing simulation" heuristic: buffer nothing, but... |
| 68 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit ties among equally-tight bins are broken by bin order; I'll add an explicit tie-break th... |
| 69 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "reserve" best-fit: strongly prefer exact fits (residual 0), then pr... |
| 70 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch from pure best-fit to a "first-fit with best-fit tie-break within a window" that expl... |
| 71 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit plus simulated annealing of optimal offline matching"... |
| 72 | edit | not_better | 0.9666 | 0.9727 | $0.0005 | I'll replace pure best-fit with a bounded look-ahead "best-fit with first-fit fallback for fragme... |
| 73 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Add a tie-aware refinement to best-fit: when several bins leave the same minimal leftover, prefer... |
| 74 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Implement a proper matching-based heuristic inspired by "Best Fit Decreasing" with a global view:... |
| 75 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the pure best-fit score with a "best-fit + sub-unity-residue consolidation" rule: strongl... |
| 76 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace plain best-fit with a scaled "best-fit + almost-exact-fit" rule that favors leaving ... |
| 77 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a two-mode rule: strongly prefer exact/near-exact fits (residual of 0 ... |
| 78 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit plus balancing" rule: normalize the residual after pl... |
| 79 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "best-fit + harmonic/dual-fit" scoring rule: rank bins primarily by ... |
| 80 | edit | not_better | 0.6839 | 0.9727 | $0.0005 | Replace pure best-fit with a "worst-fit plus exactness" hybrid: strongly prefer bins exactly fill... |
| 81 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace plain best-fit with a hybrid that combines best-fit with a tie-break toward "almost-... |
| 82 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Implement "best fit plus sub-unit consolidation with tie-breaking by bin order": rank primarily b... |
| 83 | edit | gate_rejected | 0.9960 | 0.9727 | $0.0009 | I'll replace best-fit with a "matching" rule that scores bins by how close their post-placement r... |
| 84 | edit | gate_rejected | 0.9955 | 0.9727 | $0.0005 | I'll implement a "best-fit with mean-residual matching" rule: rank bins by how close the post-pla... |
| 85 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Best-fit ties are currently broken toward the first bin; I'll keep pure best-fit (which is optima... |
| 86 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a "double-fit" fallback: keep pure best-fit as the primary criterion (it is optimal on t... |
| 87 | edit | gate_rejected | 0.9960 | 0.9727 | $0.0005 | I'll switch to a "best-fit with residual matching to the running mean item size" rule that also r... |
| 88 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a best-fit rule with a strong exact-fit bonus plus a "residual reuse" bonus that r... |
| 89 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll use a hybrid: pure best-fit (tightest post-placement residual) as the main criterion but add... |
| 90 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a hybrid scoring rule: primary criterion is tightest post-placeme... |
| 91 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a small "dual-fit" preference to best-fit: keep tightest post-placement residual as the ... |
| 92 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace the pure best-fit score with a combined score: a dominant best-fit term (negative po... |
| 93 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "worst-fit among near-best" hybrid: keep post-placement residual as the primary ... |
| 94 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from a deterministic best-fit to a small randomized "best-fit with occasional near-fi... |
| 95 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with the classic "Best-Fit Decreasing-inspired" score but add a strong exac... |
| 96 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "dual-criterion" score: dominant tightest-residual term plus a bonus... |
| 97 | edit | not_better | 0.9727 | 0.9727 | $0.0011 | None of the previous variants changed the behavior because the "huge bonus" and tolerances were d... |
| 98 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | The previous tolerance-based variants collapse to pure best-fit; instead I'll implement a genuine... |
| 99 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with a Harmonic-style rule: score each bin by how well the item fits a... |
| 100 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The repeated attempts all collapsed to plain best-fit because their extra terms never overcome th... |
| 101 | edit | not_better | 0.7429 | 0.9727 | $0.0006 | I'll implement a size-class-aware best-fit rule inspired by Harmonic/Modified-Harmonic packing: g... |
| 102 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll try a genuinely different approach: rather than only best-fit on residuals, use a "Least-Loa... |
| 103 | edit | not_better | 0.9696 | 0.9727 | $0.0006 | Replace the pure best-fit priority with an "almost-worst-fit fallback": keep exact fits (residual... |
| 104 | edit | not_better | 0.7228 | 0.9727 | $0.0006 | The repeated best-fit variants all plateau at ~0.9727. I'll switch to a genuinely different, well... |
| 105 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure best-fit residual ordering with a "best-fit with exact-fit/consolidation pr... |
| 106 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit with a small-item consolidation bonus": keep best-f... |
| 107 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a tie-breaking best-fit variant that prefers exact/near-exact fits more aggressively by ... |
| 108 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a Harmonic/Modified-Harmonic-inspired rule: score bins so that medium items prefer... |
| 109 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "best-fit with exact-fit bonus plus a tiny deterministic tie-break toward lower bin in... |
| 110 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace the pure best-fit residual rule with a size-aware "best-fit with late-stage load balancin... |
| 111 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll try a "usable-residual" scoring: strongly prefer exact fits, otherwise rank by residual but ... |
| 112 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a stateful "good-bin ledger": track each bin's residual and, instead of pure best-fit, p... |
| 113 | edit | gate_rejected | 0.9748 | 0.9727 | $0.0006 | I'll replace pure best-fit with a proper "best-fit decreasing"-style rule enhanced by a learned i... |
| 114 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a size-threshold hybrid rule: large items (above a tunable threshold) use pure bes... |
| 115 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a two-criteria best-fit that, when no exact/near-exact fit exists, prefers the bin... |
| 116 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a stateful "age-aware best fit" rule: keep best-fit as the primary criterion, but ... |
| 117 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the stateless best-fit rule with a stateless "harmony"-style scoring that picks the ... |
| 118 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a stateful "reserve best fit" rule: track the running mean item size in the stream and, ... |
| 119 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace best-fit with a stateful rule that reserves a small "safety" bin for large items: am... |
| 120 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a stateless "first-fit with best-fit fallback for tight fits" hybrid: scan bins in... |
| 121 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll switch to a distribution-aware "complement matching" rule: compute a small histogram over it... |
| 122 | edit | not_better | 0.9705 | 0.9727 | $0.0004 | I'll test the classic "first fit" rule which keeps bins densely packed in index order (using the ... |
| 123 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a stateful twist to best-fit: track the mean item size seen so far, and use best-fit as ... |
| 124 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Add a stateful tie-break to best-fit: when multiple bins give residuals close to the minimum (wit... |
| 125 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll implement a stateful rule that tracks the empirical item-size distribution and scores each b... |
| 126 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch the per-bin ranking from plain best-fit to a "best-fit with restricted opening" hybri... |
| 127 | edit | not_better | 0.9221 | 0.9727 | $0.0005 | I'll try the classic "worst-fit decreasing"-inspired online rule in reverse: worst-fit (place ite... |
| 128 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | I'll replace the pure best-fit key with a residual-aware score that strongly prefers exact fits b... |
| 129 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a stateful "best-fit with periodic full-bin detection" hybrid: primary key is best... |
| 130 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Introduce a "subset-sum aware" best-fit: while keeping best-fit as the main key, break near-ties ... |
| 131 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace plain best-fit with a stateful rule that tracks the running mean item size and uses ... |
| 132 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a residual-tiered best-fit that adds a tie-break based on the bin's in... |
| 133 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a stateful "best-fit with sum-pairing opportunity" rule: after finding the best-fi... |
| 134 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace plain best-fit with a two-step rule: among bins that can hold the item, choose the one wh... |
| 135 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit is nearly optimal but fails on the residual "scrap" problem; the strongest known online ... |
| 136 | edit | gate_rejected | 0.9748 | 0.9727 | $0.0007 | I'll replace the pure best-fit key with a classic harmonic-style partition rule: bins are ranked ... |
| 137 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace the fixed best-fit key with a stateful harmonic-style rule that buckets bins by resi... |
| 138 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll make the rule a stateful "best-fit with scrap-avoidance": keep best-fit as the primary key, ... |
| 139 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll implement a stateful best-fit variant that tracks the running distribution of item sizes and... |
| 140 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a stateful "best-fit except avoid opening new bins needlessly" rule: p... |
| 141 | edit | not_better | 0.9682 | 0.9727 | $0.0006 | I'll replace pure best-fit (which is what `-(bins-item)` implements) with a stateful "best-fit de... |
| 142 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a stateful variant that solves the "scrap" problem directly using... |
| 143 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit key with a key that inverts the tightest-fit but nudges ties using a hash o... |
| 144 | edit | not_better | 0.9553 | 0.9727 | $0.0007 | I'll switch from pure best-fit to a stateful "best-fit with dominance rescue": keep best-fit as t... |
| 145 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with a stateful harmonic-style rule: partition residual capacities int... |
| 146 | edit | gate_rejected | 0.9728 | 0.9727 | $0.0006 | Replace pure best-fit with a stateful "best-fit with threshold postponement": track the running m... |
| 147 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a stateful rule that, among bins giving a tight fit, prefers resi... |
| 148 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace best-fit with a two-parameter rule: primary score is tightest fit (best-fit), but br... |
| 149 | edit | not_better | 0.8300 | 0.9727 | $0.0005 | I will replace pure best-fit with Good-Fit-style score that deliberately prefers leaving a residu... |
| 150 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Keep best-fit primary; break near-ties (residuals within a small tolerance) by preferring the bin... |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Skipped: priority has nothing to remove (a single return without a +/- chain).

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_e_rand --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 1
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_e_rand-s1   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_e_rand/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_e_rand/initial.py` `609927c5ea619a94`
- `problems/bp_sh_e_rand/problem.md` `190017a698e23cd8`
- `problems/bp_sh_e_rand/suite.json` `7e369a6aa9869ab4`
- `problems/bp_sh_e_rand/verify.py` `0f28aa90e2f40f70`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
