# Research loop report: bp_sh_d_cex

| | |
|---|---|
| problem | `bp_sh_d_cex` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0877 of a $0.20 hard cap, 150 calls, 292,974 tokens |
| wall time | search 1686 s, baselines 67 s, explain 15 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (149 valid), 1 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9728 | 0.9634 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_d_cex/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_d_cex/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_d_cex/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9727 | 0.9634 | 4 parts removed |

Audit: public 0.9727 → 0.9728 (+0.0002), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program 0.0094.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace the pure best-fit rule with a smarter rule: among bins where the item leaves the least wa... |
| 2 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Implement a "best fit with de-randomized reserve" rule: use best-fit but, when the best fit would... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Add a small experiment: break ties toward the lowest bin index is already default, but change the... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Add a first-fit-like tie-breaking twist to best fit: rank bins by best fit but break exact ties (... |
| 5 | edit | not_better | 0.9725 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a dual-criteria rule that combines best-fit tightness for large... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a classic and strong online heuristic for unknown distributions: "Best Fit with a ... |
| 7 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Implement a size-class-based harmonic/dual rule: always choose the tightest fit (best-fit) for la... |
| 8 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a simple "reserve" mechanism based on item size classes: for genuinely small items (whic... |
| 9 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace the score with a "best-fit-decreasing style harmonic" rule: rank bins mainly by best... |
| 10 | edit | not_better | 0.9705 | 0.9727 | $0.0005 | I'll try "Worst-Fit with cautious ramp": for each item, prefer the fullest bin that still leaves ... |
| 11 | edit | not_better | 0.9710 | 0.9727 | $0.0005 | I'll add a "harmonic/next-fit hybrid": for items larger than a threshold, use best fit; for small... |
| 12 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "modified best fit" that considers pairing: for each bin, after placing the item... |
| 13 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a small "load-balancing via exact-fit pairing" tweak: rank primarily by residual (best-f... |
| 14 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace the plain best-fit score with a "best fit + adaptability" rule: keep best-fit as the... |
| 15 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit with capped residual" rule: for each bin compute th... |
| 16 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try a size-class aware best-fit: items are mapped to harmonic-like size classes, and a bin i... |
| 17 | edit | not_better | 0.9441 | 0.9727 | $0.0005 | I'll replace pure best-fit with a hybrid that switches to worst-fit-like behavior for the smalles... |
| 18 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a "best-fit with future-size awareness" rule: score bins primarily by best fit (re... |
| 19 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with "sum-of-squares / harmonious best-fit": among bins that fit, prefer th... |
| 20 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace best-fit with a reimplemented "best fit decreasing-style" online rule: track a running es... |
| 21 | edit | not_better | 0.9412 | 0.9727 | $0.0008 | Implement a two-mode rule: for items larger than a threshold use best-fit (tightest residual), bu... |
| 22 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "best-fit with a capacity-waste penalty tiebreak": primary key is best-fit (smal... |
| 23 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement the classic "Almost-Worst-Fit with best-fit fallback" idea in a robust way: use a ... |
| 24 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch the primary rule to "worst-fit" for small items combined with best-fit for large item... |
| 25 | edit | gate_rejected | 0.9753 | 0.9727 | $0.0005 | Replace pure best-fit with a harmonic-class rule: prefer bins whose post-placement residual lands... |
| 26 | edit | not_better | 0.9690 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit + bounded residual" rule inspired by the observation ... |
| 27 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Keep best-fit as the primary key, but break ties among the minimum residual by preferring the bin... |
| 28 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll make the primary score best-fit but add a small bonus (via an epsilon-scaled term) that pref... |
| 29 | edit | not_better | 0.9535 | 0.9727 | $0.0005 | I'll replace pure best-fit with a hybrid that uses the Sum-of-Squares/Almost-Worst-Fit idea: for ... |
| 30 | edit | not_better | 0.9076 | 0.9727 | $0.0005 | I'll add stateful "bin index" tracking to implement a hybrid of best-fit and worst-fit: compute b... |
| 31 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a stateful "drain small shards" rule: keep best-fit as the primary key, but mainta... |
| 32 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement the classical Harmonic-K style rule by scoring each bin on how close its post-plac... |
| 33 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll combine best-fit with the classic "consolidate near-full bins" idea but make it stateful and... |
| 34 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure best-fit with "best fit decreasing-esque" improvement that deviates for ver... |
| 35 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "best-fit with best-fit-decreasing-like reservation" rule that ... |
| 36 | edit | gate_rejected | 0.9748 | 0.9727 | $0.0005 | I'll implement a stateful "residual-class consolidation" rule: keep best-fit as the base, but whe... |
| 37 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a two-key rule: primary key prefers exact/near-exact fills by wei... |
| 38 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a stateful "best-fit with bounded worst-fit for large items" hybrid grounded in th... |
| 39 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll implement the well-known "best fit with a small item threshold" rule from the bin-packing li... |
| 40 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll use best-fit but add a penalty for creating tiny unusable residuals (residual below a small ... |
| 41 | edit | not_better | 0.8566 | 0.9727 | $0.0005 | Replace pure best-fit with a "Huggins-style" winner: for each fitting bin, prefer residuals large... |
| 42 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try "best-fit decreasing" style by pre-sorting into buckets isn't possible online, so instea... |
| 43 | edit | not_better | 0.8999 | 0.9727 | $0.0005 | I'll use a score that ranks bins by the residual left after placing the item, but with a tiered "... |
| 44 | edit | not_better | 0.9725 | 0.9727 | $0.0006 | I'll switch from best-fit to an online "sum-of-squares" / matching strategy: score each fitting b... |
| 45 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a stateful online harmonic-style rule: track the empirical distribution of item si... |
| 46 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to the classic "best fit with a sub-100 residual avoidance" but make it adaptive: use... |
| 47 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll try a score of the negative resulting residual raised to a convex power (e.g. squared) combi... |
| 48 | edit | not_better | 0.8069 | 0.9727 | $0.0005 | I'll implement a stateful "best-fit with complementary pairing": track the number of bins used so... |
| 49 | edit | not_better | 0.8757 | 0.9727 | $0.0005 | I'll compress each bin's remaining capacity to a "used space" and apply a weighted score: strongl... |
| 50 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The previous attempts kept tuning local heuristics near best-fit. A better online rule is the cla... |
| 51 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement the classic online "Refined Harmonic / Harmonic-K" style rule: classify the arrivi... |
| 52 | edit | not_better | 0.9569 | 0.9727 | $0.0006 | I'll replace the pure best-fit rule with a population-aware stateful rule: track the empirical it... |
| 53 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a hybrid that prefers an exact fit, then a bin whose leftover after pl... |
| 54 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a stateful "best-fit with small-item consolidation" rule: for items at most half the cap... |
| 55 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add a small stateful "perfect-fit memory": keep a count of bins whose current residual matches an... |
| 56 | edit | not_better | 0.9682 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a score that prefers bins whose residual after placing the item... |
| 57 | edit | not_better | 0.9719 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "least-loaded bin that still fits" rule (worst-fit) for large i... |
| 58 | edit | not_better | 0.9722 | 0.9727 | $0.0008 | I'll replace pure best-fit with a stateful "residual-matching" rule: maintain an estimate of the ... |
| 59 | edit | not_better | 0.9606 | 0.9727 | $0.0007 | Add a stateful "avoid tiny shard" penalty combined with residual-matching: maintain a histogram o... |
| 60 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Reproduce best-fit exactly (it is hard to beat), but add a stateful rule that reserves a bin with... |
| 61 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit is already near-optimal; the main remaining loss comes from ties in the residual after p... |
| 62 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll keep best-fit as the core but add a stateful histogram of item sizes and use a small tie-bre... |
| 63 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the score with best-fit plus a tie-break bonus that prefers bins which already contain it... |
| 64 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a light stateful tie-break to pure best-fit that, among bins with the same resulting res... |
| 65 | edit | invalid | 0.0000 | 0.9727 | $0.0005 | I'll keep pure best-fit (hard to beat) but add a stateful tie-break: track a running histogram of... |
| 66 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll combine best-fit with a targeted "fill-exactly" bonus: track a running histogram of item siz... |
| 67 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a hybrid that uses best-fit normally but, when the current item would ... |
| 68 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "best-fit plus future-fit avoidance" rule: among bins with the small... |
| 69 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace best-fit with a fixed-score "harmonic"-style rule: map each bins-entry to a priority that... |
| 70 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a two-stage policy: normally best-fit, but use a stateful histogram of... |
| 71 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add a stateful "reserve best-fit for a future match" tweak: among bins whose best-fit residual wo... |
| 72 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with an online adaptation of the classical "best-fit decreasing"-like behav... |
| 73 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a rank-based rule that strongly prioritizes exact fits (residual ... |
| 74 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a two-choice hybrid: keep best-fit but when the item is "large" relati... |
| 75 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace best-fit with a deliberate randomized tie-breaking scheme using a stateful linear co... |
| 76 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit is already near-optimal for online packing, and all prior tweaks failed to beat it, so I... |
| 77 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I will replace pure best-fit with an exponential (soft-min) weighting over the residual capacitie... |
| 78 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll implement a proper online adaptation of best-fit-decreasing using a learned item-size histog... |
| 79 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll combine best-fit with a virtual "matching" idea: instead of always minimizing the immediate ... |
| 80 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with a "best-fit with residual-utility shaping": score each bin by the... |
| 81 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best-fit leaves many bins with small, unusable residuals. I'll add a stateful histogram of observ... |
| 82 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a stateful "best-fit plus reserved-fit" rule: track the exact ite... |
| 83 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will replace pure best-fit by an "almost-worst-fit for large residuals, exact-match boost" hybr... |
| 84 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | All previous stateful tweaks failed because they perturb best-fit's tight packing; instead I will... |
| 85 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a stateful rule that scores each bin by preferring (a) exact complemen... |
| 86 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with a stateful hybrid that strongly prefers placing an item so the bin bec... |
| 87 | edit | not_better | 0.9727 | 0.9727 | $0.0009 | I'll try a randomized restart-free improvement: use pure best-fit but break ties (equal residual)... |
| 88 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace pure best-fit with a stateful "sum-aware" rule: track a running catalog of which residual... |
| 89 | edit | not_better | 0.9727 | 0.9727 | $0.0006 |  |
| 90 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit-decreasing-like" rule using the empirical item-size... |
| 91 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a score that combines best-fit with a small preference for leaving a residual equal to a... |
| 92 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "worst-fit among the smallest sufficient bins" strategy: first restr... |
| 93 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a scale-invariant "harmonic-ish" rule: score each bin primarily by the... |
| 94 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace pure best-fit with a stateful "best-fit with exact-fit bonus and residual-distribution aw... |
| 95 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace the myopic best-fit rule with a stateful linear-regression scorer: track observed item si... |
| 96 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace the myopic best-fit with a bounded stateful rule that keeps a per-bin "age/usage" counter... |
| 97 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit with aging/consolidation pressure": prefer exact fits... |
| 98 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll keep the near-optimal best-fit rule but add a stateful exact-fit bonus and a small "leave a ... |
| 99 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll replace myopic best-fit with a "Best-Fit Decreasing proxy via reservation": keep best-fit as... |
| 100 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try the opposite of best-fit for consolidating small items: use a two-regime rule — if the i... |
| 101 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a harmonic-style bin-choice rule (classic Harmonic/ScaleFit family for online pack... |
| 102 | edit | not_better | 0.9557 | 0.9727 | $0.0010 | Replace the myopic rule with a stateful "residual-filling" scorer: maintain an empirical distribu... |
| 103 | edit | invalid | 0.0000 | 0.9727 | $0.0006 | Add a stateful histogram of observed item sizes, and score bins by a combination of best-fit plus... |
| 104 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a proper "residual threshold" variant of best-fit inspired by the classic Richey/A... |
| 105 | edit | not_better | 0.9716 | 0.9727 | $0.0009 | Use a Harmonic-style rule: partition items by size class, and for each class assign to the bin in... |
| 106 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add a light stateful "exact-fill preference": track a running histogram of past item sizes and gi... |
| 107 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch from myopic best-fit to a "Best-Fit + reservation for large items" hybrid driven by t... |
| 108 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Implement a bounded "empty-bin preservation" rule: score is best-fit by default, but give a small... |
| 109 | edit | not_better | 0.9727 | 0.9727 | $0.0010 | I'll replace the pure best-fit rule with a stateful distribution-aware scorer: track the empirica... |
| 110 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement the classic Advanced/Modified Best-Fit heuristic from the bin-packing literature: ... |
| 111 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | (no description) |
| 112 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Use a stateful "sum-of-squares / best-fit with exact-fill lookahead" rule: track a histogram of p... |
| 113 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a two-mode rule: best-fit by default, but for small items (≤ 40 o... |
| 114 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace myopic best-fit with a "least residual entropy" rule inspired by Sum-of-Squares: score ea... |
| 115 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will replace pure best-fit with a randomized threshold rule that occasionally applies "best fit... |
| 116 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "reserve the last partially empty bin" rule: apply best-fit over non-empty bins ... |
| 117 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a refined best-fit that tracks the running optimal bin count and,... |
| 118 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace pure best-fit with a size-class-aware rule: track item-size statistics online and, instea... |
| 119 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace the myopic best-fit with a proper "Sum of Squares"-style bin ranking: score each bin... |
| 120 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Introduce a stateful "best-fit with level correction": still primarily best-fit, but on each call... |
| 121 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | I'll replace myopic best-fit with a "harmonic floor" rule that uses the online item-size distribu... |
| 122 | edit | not_better | 0.9232 | 0.9727 | $0.0005 | Replace best-fit with a "worst-fit among fitting bins with residual below a threshold, else best-... |
| 123 | edit | improved | 0.9728 | 0.9728 | $0.0006 | I'll switch from pure best-fit to a "best-fit-decreasing-style" rule that uses the online-observe... |
| 124 | edit | not_better | 0.9721 | 0.9728 | $0.0005 | Add a mild capacity-14 penalty only for medium items too (not just small ones), so bins whose pos... |
| 125 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Extend the best-fit baseline with a "class-aware" nudge: for medium and large items, slightly pre... |
| 126 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Add a small priority bonus for bins whose post-placement residual is "reusable" (not a stranded t... |
| 127 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the hard item-size threshold and fixed awkward range with a smooth, distribution-aware sc... |
| 128 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll strengthen the awkward-gap penalty into a "usable residual" bonus that scales with the obser... |
| 129 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the simplistic item-size threshold and fixed awkward-gap penalty with a distribution-awar... |
| 130 | edit | not_better | 0.9727 | 0.9728 | $0.0010 | Replace the ad-hoc thresholds with a single clean best-fit-dominant rule: rank by negative post-p... |
| 131 | edit | not_better | 0.9727 | 0.9728 | $0.0007 |  |
| 132 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Replace the current small/awkward-gap heuristic with a size-invariant residual-quality score: alw... |
| 133 | edit | not_better | 0.9725 | 0.9728 | $0.0006 | Introduce a running estimate of the item-size distribution and use a "waste" score that penalizes... |
| 134 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Many bin-packing gains come from occasionally *not* using best fit for mid-sized items: a "harmon... |
| 135 | edit | not_better | 0.9721 | 0.9728 | $0.0006 | I will make the item-size cutoff adaptive to the observed mean item size rather than a fixed 40, ... |
| 136 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the hard large/small item threshold with a continuous blend: always base the score on bes... |
| 137 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the rule with an adaptive-reserve best fit that uses a running histogram of observed... |
| 138 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Use a "best fit decreasing-style" rule with a running histogram of item sizes: score each bin by ... |
| 139 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the hard item>=40 threshold and awkward-gap penalty with a single continuous best-fit sco... |
| 140 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the ad-hoc residual-gap penalty with a proper "best fit decreasing"-flavored rule: always... |
| 141 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Pure best-fit (residual minimization) is the strongest base rule; the previous drift toward resid... |
| 142 | edit | not_better | 0.9725 | 0.9728 | $0.0026 | I'll make the tie-breaking term item-aware and strong: reward perfect fits heavily, reward result... |
| 143 | edit | not_better | 0.6393 | 0.9728 | $0.0007 | I'll replace the heuristic with a size-class-aware best-fit that uses a fixed number of capacity ... |
| 144 | edit | not_better | 0.9708 | 0.9728 | $0.0011 | Replace the flat awkward-gap penalty with a graduated penalty (peaking at residual=1) and lower t... |
| 145 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | The current rule uses a hard threshold at item>=40 and a flat penalty for residuals [1,15]. I'll ... |
| 146 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Pure best-fit is hard to beat, but the one exception where it can waste space is when a small ite... |
| 147 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the fixed item>=40 threshold with a smooth, continuous best-fit score (always domina... |
| 148 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll add a "same-size matching" tie-breaker to pure best fit: keep residual minimization dominant... |
| 149 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll try a "reserve for large items" rule that is stronger but still mostly best-fit: when the cu... |
| 150 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll switch the small-item rule from a flat awkward-gap penalty to an explicit "match into an exi... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,5 +1,5 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Distribution-aware best fit: keep large residuals for large items (Weibull mean ~40)."""
 import numpy as np
 
 
@@ -10,5 +10,19 @@
     bins: numpy int64 array with the remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    residual = bins - item  # remaining capacity after placing the item
+
+    # For large items, standard best fit (pack tightly).
+    # For small items, avoid wasting big residuals by prefering to place into
+    # bins that are already fairly full, leaving large empty bins available for
+    # future large items. Use a soft monotone score toward fuller bins.
+    if item >= 40:
+        return -(residual)
+    # Small item: favor bins with small residual (fuller bins get filled), but
+    # with a mild preference to not create tiny unusable residuals (residual
+    # below item-typical sizes) -- nudge away from residuals in [1, 15].
+    score = -residual.astype(np.float64)
+    awkward = (residual >= 1) & (residual <= 15)
+    score[awkward] -= 2.0
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (8 parts, 15 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 13 | `residual = bins - item` | -0.9728 | essential: the program fails or turns invalid without it |
| 13 | `term + bins` | -0.9728 | essential: the program fails or turns invalid without it |
| 24 | `score = -residual.astype(np.float64)` | -0.9728 | essential: the program fails or turns invalid without it |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 13: `term - item`
- line 19: `if item >= 40: ...`
- line 20: `return -residual`
- line 25: `awkward = (residual >= 1) & (residual <= 15)`
- line 26: `score[awkward] -= 2.0`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9728 | 0.9634 |
| minimal (4 parts removed) | 0.9727 | 0.9634 |

Minimal program:

```python
"""Distribution-aware best fit: keep large residuals for large items (Weibull mean ~40)."""
import numpy as np

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    residual = bins
    score = -residual.astype(np.float64)
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_d_cex --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 3
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_d_cex-s3   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_d_cex/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_d_cex/initial.py` `609927c5ea619a94`
- `problems/bp_sh_d_cex/problem.md` `190017a698e23cd8`
- `problems/bp_sh_d_cex/suite.json` `c10c239f751ffc5f`
- `problems/bp_sh_d_cex/verify.py` `12d8663a195dbe46`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
