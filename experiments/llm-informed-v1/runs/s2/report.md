# Research loop report: bin_packing_online_informed

| | |
|---|---|
| problem | `bin_packing_online_informed` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2936 of a $0.35 hard cap, 300 calls, 930,752 tokens |
| wall time | search 5114 s, baselines 48 s, explain 75 s |
| stopped | max_iters (stopped_early) |
| evaluations | 300 (294 valid), 9 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9927 | 0.9913 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online_informed/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_informed/baselines/funsearch_weibull.py` |
| baseline `fwss` | 0.9992 | 0.9990 | `problems/bin_packing_online_informed/baselines/fwss.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_informed/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9922 | 0.9896 | 1 parts removed |

Audit: public 0.9616 → 0.9927 (+0.0311), hidden 0.9604 → 0.9913 (+0.0309); public − hidden gap of the final program 0.0015.

Against the baselines: the final program's public score is below the best baseline (`fwss`, 0.9992). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace pure best-fit with a "best fit except reserve a few empty bins" strategy: for most items ... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a hybrid: use best-fit normally, but when an item would perfectly/comp... |
| 3 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll switch from pure best-fit to a "best fit decreasing-inspired" rule that scores bins by the r... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a tuned "first-fit with a best-fit tie-break toward earlier/lower-inde... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | The best-fit baseline wastes capacity when a medium item exactly fills an empty bin while another... |
| 6 | edit | not_better | 0.9561 | 0.9616 | $0.0005 | I'll replace pure best-fit with a harmonic-inspired scoring rule: bins are grouped by remaining c... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "gap-aware best fit" that tracks total free space and, when an item ... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll add a scoring rule that blends best-fit with a preference for leaving a residual capacity ma... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit + empty-bin reservation via deferred perfect fits" rule: s... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace best-fit with a randomized/measured "best fit with item-count-aware empty-bin reservation... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a two-level rule: classify each fitting bin by resulting residual into... |
| 12 | edit | improved | 0.9683 | 0.9683 | $0.0007 | I'll implement a proper Best-Fit-Decreasing-style improvement by switching to a "worst-fit among ... |
| 13 | edit | improved | 0.9730 | 0.9730 | $0.0007 | I'll switch the residual-utility rule to prefer leaving residual gaps that match the most probabl... |
| 14 | edit | not_better | 0.9542 | 0.9730 | $0.0008 | I'll switch the target typical-residual from a mode/mean blend to the observed distribution's mea... |
| 15 | edit | not_better | 0.9616 | 0.9730 | $0.0007 | I'll replace the residual-distance heuristic with a "best fit plus future-fill value" rule: score... |
| 16 | edit | not_better | 0.9670 | 0.9730 | $0.0008 | I'll replace the hand-tuned residual-distance formula with a principled expected-waste criterion:... |
| 17 | edit | not_better | 0.9616 | 0.9730 | $0.0007 | I'll replace the current heuristic with a "best-fit-decreasing-style" rule that combines exact/ne... |
| 18 | edit | not_better | 0.9694 | 0.9730 | $0.0008 | I'll add a term that rewards placing the item into a bin whose residual (after placement) is smal... |
| 19 | edit | not_better | 0.9616 | 0.9730 | $0.0006 | I'll switch to a pure Best-Fit rule (choose the bin that leaves the smallest residual, with a tin... |
| 20 | edit | improved | 0.9793 | 0.9793 | $0.0007 | I'll replace the residual-distance heuristic with Best-Fit-Decreasing-inspired scoring but add a ... |
| 21 | edit | not_better | 0.9778 | 0.9793 | $0.0008 | I'll add a score bonus for residuals that equal a common item size observed so far (the most freq... |
| 22 | edit | not_better | 0.6817 | 0.9793 | $0.0008 | I'll replace the single-median usable-gap target with a multi-target approach: reward residuals t... |
| 23 | edit | invalid | 0.0000 | 0.9793 | $0.0008 | I'll refine the usable-gap bonus to use the empirical distribution's quantiles (choose the residu... |
| 24 | edit | improved | 0.9817 | 0.9817 | $0.0008 | I'll keep the current median-based usable-gap structure intact but add a mild "prefer starting a ... |
| 25 | edit | not_better | 0.9802 | 0.9817 | $0.0008 | I'll make the usable-gap target adaptive to the elapsed fraction of the instance: early on, gaps ... |
| 26 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll replace the expensive per-call histogram/CDF recomputation with incremental tracking, and mo... |
| 27 | edit | not_better | 0.9800 | 0.9817 | $0.0009 | I'll add a "fillability" bonus based on the empirical probability that some future item fits exac... |
| 28 | edit | not_better | 0.9614 | 0.9817 | $0.0008 | I'll replace the crude median single-target usable-gap with a residual-choice rule based on the e... |
| 29 | edit | not_better | 0.9728 | 0.9817 | $0.0008 | Use the scale of the instance (number of items, known from len(bins)) to anticipate the expected ... |
| 30 | edit | not_better | 0.9798 | 0.9817 | $0.0009 | I'll sharpen the exact-fit and near-exact-fit preference by scaling the exact-fit bonus with the ... |
| 31 | edit | not_better | 0.9797 | 0.9817 | $0.0008 | I'll replace the fixed "tie-break toward smaller residual" with a proper Best-Fit dominance: inst... |
| 32 | edit | not_better | 0.9614 | 0.9817 | $0.0007 | Reduce the exact-fit bonus and stop penalizing large usable residuals, instead using a pure best-... |
| 33 | edit | not_better | 0.9802 | 0.9817 | $0.0009 | I'll add a small "large-residual penalty" proportional to the amount of leftover space that is li... |
| 34 | edit | not_better | 0.9737 | 0.9817 | $0.0008 | I'll change the metric from a symmetric distance-to-multiple-of-typical to an asymmetric "waste" ... |
| 35 | edit | not_better | 0.9790 | 0.9817 | $0.0009 | I'll replace the heuristic with a distribution-aware "expected future waste" score: for each bin,... |
| 36 | edit | not_better | 0.9577 | 0.9817 | $0.0008 | I'll replace the hand-tuned heuristic with a learned "expected future fillability" score: for eac... |
| 37 | edit | not_better | 0.9690 | 0.9817 | $0.0008 | The current score mostly rewards exact fits and penalizes slivers, but ignores that a residual of... |
| 38 | edit | not_better | 0.5224 | 0.9817 | $0.0008 | I'll shift from a purely static best-fit variant to a "least-loaded bin that still fits" (Worst-F... |
| 39 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | The exact-fit bonus is too small relative to the distance term: I'll make exact fits dominate str... |
| 40 | edit | gate_rejected | 0.9841 | 0.9817 | $0.0008 | I'll make the score a proper expected-waste estimate: use the empirical item histogram to compute... |
| 41 | edit | not_better | 0.9752 | 0.9817 | $0.0008 | I'll adjust the sliver penalty threshold from 0.5*t to 0.7*t and increase the tiny-sliver coeffic... |
| 42 | edit | not_better | 0.9656 | 0.9817 | $0.0008 | I'll introduce a mild "least-full bin that still fits" balance term proportional to the residual ... |
| 43 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll add a look-ahead term based on the empirical distribution of item sizes: for each candidate ... |
| 44 | edit | not_better | 0.9781 | 0.9817 | $0.0009 | I'll add a "smallest residual that still fits well" bootstrap phase: for the first items, behave ... |
| 45 | edit | invalid | 0.0000 | 0.9817 | $0.0010 | I'll replace the hand-tuned heuristic with a principled "expected bins used" model: for each cand... |
| 46 | edit | not_better | 0.9602 | 0.9817 | $0.0007 | I'll add a simple, robust "best-fit with a small preference for residuals near the empirical mean... |
| 47 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll shrink the "typical" reference size used in the multiple-of-typical spacing term toward the ... |
| 48 | edit | gate_rejected | 0.9817 | 0.9817 | $0.0009 | I'll replace the heuristic scoring with a learned-style "expected future bins" value: maintain th... |
| 49 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll make pure best-fit (smallest residual) the dominant decision term with a much larger coeffic... |
| 50 | edit | not_better | 0.9602 | 0.9817 | $0.0007 | I'll implement classic best-fit with the sliver penalty re-keyed to the empirical minimum-item es... |
| 51 | edit | not_better | 0.9800 | 0.9817 | $0.0008 | I'll sharpen the exact-fit bias by treating residuals that equal any previously-seen item size (a... |
| 52 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I will remove the median-multiple "distance to typical fill size" term entirely and replace it wi... |
| 53 | edit | no_code | n/a | 0.9817 | $0.0006 | (no description) |
| 54 | edit | not_better | 0.5505 | 0.9817 | $0.0009 | Replace the linear multiple-of-typical distance term with a multiplicative (log-ratio) spacing me... |
| 55 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll replace the pure heuristic scoring with a "best-fit with a sliver penalty keyed to the empir... |
| 56 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll change the score to a pure best-fit (dominant residual-minimization) with a monotone concave... |
| 57 | edit | not_better | 0.9612 | 0.9817 | $0.0010 | I'll replace the crude "distance to nearest multiple of the median" with a proper best-fit-sum he... |
| 58 | edit | not_better | 0.9778 | 0.9817 | $0.0008 | I'll keep the current best-fit-plus-sliver-penalty backbone but sharpen the exact-fit preference ... |
| 59 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the heuristic scoring with a "best-fit with a tuned sliver penalty" backbone where t... |
| 60 | edit | not_better | 0.4170 | 0.9817 | $0.0011 | I'll add a look-ahead "fill potential" term keyed to the empirical item-size distribution: score ... |
| 61 | edit | not_better | 0.9790 | 0.9817 | $0.0008 | I'll sharpen the exact-fit and near-fit preference by scoring candidate residuals with the empiri... |
| 62 | edit | not_better | 0.9605 | 0.9817 | $0.0008 | I'll replace the heuristic score with a best-fit variant that additionally prefers bins whose res... |
| 63 | edit | not_better | 0.9803 | 0.9817 | $0.0008 | I will add a small "negative-residual pairing" term: prefer placing the current item into a bin w... |
| 64 | edit | not_better | 0.9420 | 0.9817 | $0.0008 | I'll switch from best-fit to a "sum-of-squares/least-loaded that avoids slivers" style rule: pref... |
| 65 | edit | not_better | 0.9616 | 0.9817 | $0.0012 | I'll replace the per-bin heuristic with a size-class based best-fit rule: discretize the empirica... |
| 66 | edit | not_better | 0.9732 | 0.9817 | $0.0010 | I'll switch the backbone to a hybrid that keeps best-fit as the default but explicitly applies th... |
| 67 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll replace the continuous heuristic scoring with a "dual-criterion" rule from the bin-packing l... |
| 68 | edit | not_better | 0.9810 | 0.9817 | $0.0012 | I'll make the heuristic adaptive by fitting the empirical distribution (mean and shape via observ... |
| 69 | edit | not_better | 0.9281 | 0.9817 | $0.0008 | I'll refine the heuristic so the "typical fill" bonus uses a size drawn from the empirical distri... |
| 70 | edit | not_better | 0.9619 | 0.9817 | $0.0007 | I'll replace the ad-hoc penalty heuristic with a scored rule based on the expected number of futu... |
| 71 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll shift the backbone from raw best-fit toward a "best-fit + moderate preference for leaving re... |
| 72 | edit | not_better | 0.9747 | 0.9817 | $0.0009 | I'll add a "reserve for large items" adjustment: since large items (>50) can only fit in bins wit... |
| 73 | edit | not_better | 0.9725 | 0.9817 | $0.0007 | I'll change the backbone from a soft monotone best-fit-like score to the classic "best-fit-decrea... |
| 74 | edit | gate_rejected | 0.9821 | 0.9817 | $0.0009 | The failed attempts suggest the current score is near a local optimum for pure best-fit with a sm... |
| 75 | edit | not_better | 0.9615 | 0.9817 | $0.0009 | I'll switch the backbone to a proper Best-Fit-Decreasing-style rule: since items are i.i.d. and t... |
| 76 | edit | not_better | 0.9386 | 0.9817 | $0.0010 | The heuristic is near a local optimum; the main structural improvement is to shift the backbone f... |
| 77 | edit | not_better | 0.9616 | 0.9817 | $0.0010 | I'll replace the ad-hoc penalty terms with a principled "expected future wastage" score: for each... |
| 78 | edit | not_better | 0.9647 | 0.9817 | $0.0009 | I will add the classic "first-fit-decreasing" structural insight in an online-safe way: since rep... |
| 79 | edit | not_better | 0.9737 | 0.9817 | $0.0008 | I'll keep the best-fit backbone but replace the fragile "exact multiple of the median" bonus with... |
| 80 | edit | not_better | 0.9614 | 0.9817 | $0.0010 | I'll replace the fragile median-multiple bonus with a principled "expected future fill" value com... |
| 81 | edit | not_better | 0.9612 | 0.9817 | $0.0008 | I'll switch to a "best-fit with a strong penalty for leaving tiny unusable slivers, plus a bonus ... |
| 82 | edit | not_better | 0.9614 | 0.9817 | $0.0008 | Add a smooth "match-likelihood" bonus: score each candidate residual r by the empirical probabili... |
| 83 | edit | not_better | 0.8836 | 0.9817 | $0.0009 | I'll add a "reserve large bins" term: since large items (near 100) are relatively rare but must n... |
| 84 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll strengthen the backbone toward a smooth "best-fit with residual-utility" rule: keep exact-fi... |
| 85 | edit | not_better | 0.9764 | 0.9817 | $0.0009 | I'll keep the exact-fit reward and best-fit backbone but modestly increase the sliver penalty and... |
| 86 | edit | not_better | 0.9602 | 0.9817 | $0.0006 | I will replace the fragile median-multiple and histogram-mass heuristics with a simpler, well-fou... |
| 87 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll replace the fragile median-multiple bonus with a robust "residual fillability" term: estimat... |
| 88 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the fragile median-multiple term and its many tuned penalties with a cleaner backbon... |
| 89 | edit | not_better | 0.9661 | 0.9817 | $0.0008 | I'll strengthen the exact-fit reward further and add a mild bonus for residuals that are at least... |
| 90 | edit | not_better | 0.9800 | 0.9817 | $0.0008 | I'll add a small "avoid closing bins with unusable gaps" refinement: keep the best-fit backbone b... |
| 91 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the fragile median-multiple distance term with a cleaner backbone: strong exact-fit ... |
| 92 | edit | not_better | 0.9607 | 0.9817 | $0.0009 | Keep the best-fit backbone and exact-fit reward unchanged, but make the "unusable sliver" penalti... |
| 93 | edit | not_better | 0.9616 | 0.9817 | $0.0009 | I'll replace the fragile median-multiple term with a direct empirical fillability bonus: reward a... |
| 94 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I will add a forward-looking expected-waste term based on the empirical item distribution: for ea... |
| 95 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | Add the classic "sum of remaining capacities if the item is placed" spread heuristic from bin-pac... |
| 96 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | Replace the fragile median/sliver machinery with a clean best-fit backbone plus a single well-mot... |
| 97 | edit | not_better | 0.9609 | 0.9817 | $0.0008 | I'll switch the backbone from plain best-fit to a harmonic/dual-aware rule: score each bin by (bi... |
| 98 | edit | not_better | 0.9817 | 0.9817 | $0.0010 | Increase the exact-fit reward from 5.0 to a large value (e.g. 100.0) so an exact fit is always ch... |
| 99 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | The exact-fit bonus at 5.0 can be overwhelmed by the distance-to-multiple term; I'll boost it to ... |
| 100 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | Replace the "distance to nearest multiple of the median" term with a direct fillability measure: ... |
| 101 | edit | not_better | 0.9786 | 0.9817 | $0.0008 | I'll add a "no-new-bin" nudge: when the current item can fit into an existing bin, slightly prefe... |
| 102 | edit | not_better | 0.9607 | 0.9817 | $0.0008 | I will replace the fragile "distance to nearest multiple of median" term with a small "residual f... |
| 103 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll replace the fragile median-multiple term with a smarter dual-feasibility signal: track the e... |
| 104 | edit | not_better | 0.8939 | 0.9817 | $0.0008 | Inject a small deterministic "reserve for large items" tie-break: keep the proven best-fit-with-m... |
| 105 | edit | not_better | 0.9778 | 0.9817 | $0.0008 | Refine the sliver penalty so it only penalizes residuals that are truly unusable (below the small... |
| 106 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll make the exact-fit reward absolutely dominant by raising it to 1e6, so any bin that the item... |
| 107 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the residual ranking with a pure Best-Fit rule (minimize residual) for the main term... |
| 108 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll add a "future-fit feasibility" term that estimates, from the empirical item histogram, the p... |
| 109 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I will make the exact-fit bonus scale cleanly and add a "close-to-exact-fit" tier that dominates ... |
| 110 | edit | not_better | 0.9605 | 0.9817 | $0.0006 | I'll switch the backbone from the fragile median-multiple distance to a proper Best-Fit with a sm... |
| 111 | edit | gate_rejected | 0.9819 | 0.9817 | $0.0012 | I'll keep the best-fit backbone but replace the median-multiple "fillability" term with a learned... |
| 112 | edit | not_better | 0.9616 | 0.9817 | $0.0009 | I'll keep the strong best-fit backbone but replace the median-multiple fillability term with a pr... |
| 113 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll add a lightweight "aging"/reuse structure by preferring bins that have been open longest (sm... |
| 114 | edit | not_better | 0.9807 | 0.9817 | $0.0008 | The exact-fit bonus is currently swamped by the residual-based terms only in near-tie cases, so i... |
| 115 | edit | not_better | 0.9623 | 0.9817 | $0.0012 | I will replace the median-multiple distance term with a proper distribution-based "expected lefto... |
| 116 | edit | not_better | 0.9767 | 0.9817 | $0.0008 | I'll keep the proven best-fit backbone but switch the fillability key from the empirical median t... |
| 117 | edit | not_better | 0.9795 | 0.9817 | $0.0008 | I will sharpen the classic best-fit rule by adding a small "leave a usable residual" bonus: compu... |
| 118 | edit | not_better | 0.9817 | 0.9817 | $0.0007 | The exact-fit short-circuit hurt because it forced tiny bins open too early; instead I'll keep th... |
| 119 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I will replace the hand-tuned median-multiple fillability term with a classic, well-proven bin pa... |
| 120 | edit | not_better | 0.9598 | 0.9817 | $0.0008 | I will replace the hand-tuned heuristic with a learned-style approach: a "best-fit with deferred ... |
| 121 | edit | not_better | 0.9793 | 0.9817 | $0.0008 | I'll keep the proven best-fit backbone (smallest usable residual) but improve the tie-break: inst... |
| 122 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll keep the proven best-fit backbone (smallest usable residual) but replace the fixed exact-fit... |
| 123 | edit | not_better | 0.9600 | 0.9817 | $0.0007 | I will refine the proven best-fit backbone by strongly prioritizing a fillable residual: rank bin... |
| 124 | edit | not_better | 0.9754 | 0.9817 | $0.0008 | I will keep the best-fit backbone but make the "typical fill size" tracking more robust by using ... |
| 125 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll replace the multi-term hand-tuned heuristic with a cleaner, lighter rule: pure best-fit (sma... |
| 126 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll replace the hand-tuned multi-term heuristic with a principled rule: pure best-fit (smallest ... |
| 127 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll keep the proven best-fit backbone but strengthen the reward for leaving a residual that is e... |
| 128 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll replace the heuristic with pure best-fit (smallest usable residual, i.e. the classic Best Fi... |
| 129 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | I'll keep the best-fit backbone but add a "waste-elimination" bonus scaled by the item-size distr... |
| 130 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I will keep the proven best-fit backbone but replace the exact-fit bonus with a "residual equals ... |
| 131 | edit | not_better | 0.5413 | 0.9817 | $0.0008 | I will keep the best-fit backbone but replace the heuristic fill bonuses with a lookahead-based "... |
| 132 | edit | invalid | 0.0000 | 0.9817 | $0.0008 | I will keep the proven best-fit backbone but add a small, distribution-aware "exact-fill" bonus: ... |
| 133 | edit | not_better | 0.9616 | 0.9817 | $0.0010 | I'll keep the best-fit backbone but add a distribution-aware "gap fillability" bonus: for each ca... |
| 134 | edit | not_better | 0.9614 | 0.9817 | $0.0009 | I'll keep the best-fit backbone but add a "fillability" bonus for residuals that can be exactly c... |
| 135 | edit | not_better | 0.9616 | 0.9817 | $0.0005 | I will replace the heuristic scoring with a clean best-fit rule augmented by a strong exact-fit b... |
| 136 | edit | not_better | 0.9788 | 0.9817 | $0.0008 | I'll keep the proven best-fit backbone (dominates scoring) but add one targeted, well-supported i... |
| 137 | edit | not_better | 0.9668 | 0.9817 | $0.0008 | Replace the median-based "typical" fill size with a running mean of item sizes, which better matc... |
| 138 | edit | not_better | 0.9795 | 0.9817 | $0.0007 | I'll keep the best-fit backbone but correct the "sliver" penalty threshold: instead of penalizing... |
| 139 | edit | not_better | 0.7086 | 0.9817 | $0.0007 | I'll replace the median-keyed residual-distance heuristic with a cleaner formulation: sort/reward... |
| 140 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll replace the median-keyed residual-distance bonus with the classic best-fit rule (minimize re... |
| 141 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | Keep the proven best-fit backbone but replace the fragile "distance to multiple of median" term w... |
| 142 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll replace the fragile median-multiple "distance" term with a cleaner two-term rule: strong exa... |
| 143 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I will keep the exact-fit reward and best-fit backbone, but replace the fragile median-multiple d... |
| 144 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll keep the best-fit backbone but treat the exact-fit bonus and the "distance to multiple of me... |
| 145 | edit | not_better | 0.9793 | 0.9817 | $0.0009 | I'll keep the proven best-fit backbone and exact-fit reward, but make the "sliver" penalty adapti... |
| 146 | edit | not_better | 0.9788 | 0.9817 | $0.0008 | I'll add a "hard-to-fit-waste" penalty: when placing the item leaves a residual that is small rel... |
| 147 | edit | not_better | 0.9614 | 0.9817 | $0.0009 | Replace the noisy median-multiple distance term with a distribution-aware "closeable residual" re... |
| 148 | edit | rejected | 0.0000 | 0.9817 | $0.0008 | I'll keep the proven best-fit backbone and exact-fit reward, but replace the noisy "distance to n... |
| 149 | edit | not_better | 0.9704 | 0.9817 | $0.0008 | I will keep the proven best-fit backbone and exact-fit reward, but soften the median-multiple "di... |
| 150 | edit | not_better | 0.7179 | 0.9817 | $0.0009 | I'll strengthen the proven best-fit backbone by replacing the noisy median-multiple distance term... |
| 151 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | Strengthen the proven best-fit backbone: drop the noisy median-multiple distance term and the sma... |
| 152 | edit | not_better | 0.9783 | 0.9817 | $0.0009 | I'll keep the proven best-fit backbone plus exact-fit bonus, but add a greedy "pair the residual ... |
| 153 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll keep the proven best-fit backbone and exact-fit reward, but replace the noisy median-multipl... |
| 154 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the noisy median-multiple target with the classic best-fit backbone plus a "pair-up"... |
| 155 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | Replace the hand-tuned sliver/tiny penalties and median-multiple distance with a cleaner best-fit... |
| 156 | edit | not_better | 0.9607 | 0.9817 | $0.0006 | I'll replace the failing median-multiple heuristic with a threshold-based hybrid: use best-fit (s... |
| 157 | edit | not_better | 0.9616 | 0.9817 | $0.0009 | I'll keep the proven best-fit + exact-fit backbone but replace the hand-tuned median-multiple/sli... |
| 158 | edit | not_better | 0.9798 | 0.9817 | $0.0009 | I'll keep the proven best-fit backbone but sharpen the exact-fit preference and add a "perfect-pa... |
| 159 | edit | not_better | 0.9612 | 0.9817 | $0.0008 | Replace the noisy median-multiple distance term with a scaled "match-to-common-future-item" rewar... |
| 160 | edit | not_better | 0.9605 | 0.9817 | $0.0008 | Replace the heuristic median-multiple/sliver scoring with a sub-bin-level "best-fit plus exact-fi... |
| 161 | edit | not_better | 0.9798 | 0.9817 | $0.0009 | I'll keep the proven best-fit + exact-fit + sliver/tiny backbone, but replace the fixed median-mu... |
| 162 | edit | not_better | 0.9602 | 0.9817 | $0.0008 | I'll keep the proven best-fit + exact-fit backbone but strengthen the tie-breaking and the exact-... |
| 163 | edit | not_better | 0.9602 | 0.9817 | $0.0008 | The previous attempts to add histogram-based "common item size" bonuses consistently hurt, so I'l... |
| 164 | edit | not_better | 0.9591 | 0.9817 | $0.0007 | I'll replace the fragile hand-tuned median-multiple term with a principled threshold rule: use st... |
| 165 | edit | not_better | 0.9614 | 0.9817 | $0.0008 | Keep the proven best-fit + exact-fit + sliver/tiny backbone, but make the sliver penalty adaptive... |
| 166 | edit | not_better | 0.9598 | 0.9817 | $0.0007 | I'll keep the proven best-fit + exact-fit + sliver/tiny backbone but replace the noisy median-mul... |
| 167 | edit | not_better | 0.9817 | 0.9817 | $0.0009 | I'll replace the noisy best-fit-with-sliver-penalty backbone with a clean, well-established rule:... |
| 168 | edit | not_better | 0.9790 | 0.9817 | $0.0009 | I'll keep the proven best-fit backbone but add a targeted improvement: reward leaving a residual ... |
| 169 | edit | not_better | 0.5433 | 0.9817 | $0.0007 | I'll replace the noisy median-multiple gap term with a robust "future-fit count" signal: score bi... |
| 170 | edit | not_better | 0.9790 | 0.9817 | $0.0009 | I'll keep the strong best-fit + exact-fit backbone (which scored 0.9817) but sharpen the tie-brea... |
| 171 | edit | not_better | 0.9616 | 0.9817 | $0.0009 | I'll keep the proven best-fit + exact-fit backbone but replace the noisy median-multiple distance... |
| 172 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | Keep the exact-fit bonus and best-fit backbone, but add a proven harmonic "sum-of-squares" packin... |
| 173 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll keep the proven best-fit + exact-fit backbone but replace the noisy residual-distance terms ... |
| 174 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll keep the best-fit + exact-fit backbone but add a light "match residual to next-item-size ran... |
| 175 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the fragile median-multiple geometry terms with a cleaner, well-validated rule: stri... |
| 176 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the hand-tuned geometric heuristics with a principled Best-Fit-plus-double-fit rule:... |
| 177 | edit | gate_rejected | 0.9836 | 0.9817 | $0.0008 | I'll keep the proven best-fit + exact-fit backbone but change the sliver penalty from a fixed 0.5... |
| 178 | edit | not_better | 0.9783 | 0.9817 | $0.0008 | I'll keep the proven best-fit + exact-fit backbone and add a small "double-fit" bonus that favors... |
| 179 | edit | not_better | 0.9783 | 0.9817 | $0.0009 | I'll keep the proven best-fit + exact-fit backbone but add a "future-fill probability" term: rewa... |
| 180 | edit | not_better | 0.9814 | 0.9817 | $0.0008 | I will add a "close-bin" bias: among non-exact placements, prefer the bin whose residual after pl... |
| 181 | edit | not_better | 0.9616 | 0.9817 | $0.0010 | I'll keep the proven best-fit + exact-fit backbone but replace the median-multiple geometry with ... |
| 182 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll switch the primary ordering from the current mixed heuristic to a clean Best-Fit-Descending-... |
| 183 | edit | not_better | 0.9616 | 0.9817 | $0.0009 | I'll replace the multiplicative-median geometry with a cleaner "best-fit + prefer closing bins" r... |
| 184 | edit | not_better | 0.5326 | 0.9817 | $0.0009 | I'll add a bounded "waste estimate" penalty based on the expected number of items still to come v... |
| 185 | edit | not_better | 0.8573 | 0.9817 | $0.0008 | I'll keep the proven best-fit + exact-fit backbone and add a modest "second-fit" bonus: reward re... |
| 186 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll keep the best-fit + exact-fit backbone but strengthen the tie-break to prefer the fullest bi... |
| 187 | edit | not_better | 0.9817 | 0.9817 | $0.0008 | I'll leave the best-fit + exact-fit backbone intact but make the residual geometry aware of the c... |
| 188 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the median-multiple geometry with a fixed, robust set of "preferred residual" target... |
| 189 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll replace the fragile median-multiple geometry with a robust scoring that combines pure best-f... |
| 190 | edit | not_better | 0.9741 | 0.9817 | $0.0009 | I'll replace the fragile geometry with a score that strongly rewards exact fits while adding a bo... |
| 191 | edit | not_better | 0.9616 | 0.9817 | $0.0005 | I'll switch the scoring to a pure, aggressive best-fit rule: only the exact-fit bonus (large) and... |
| 192 | edit | not_better | 0.9670 | 0.9817 | $0.0009 | I'll add a lightweight, bounded "future-fit expectation" term: track the empirical distribution o... |
| 193 | edit | not_better | 0.9575 | 0.9817 | $0.0008 | I'll keep the best-fit + exact-fit backbone but make the sliver penalty sharper and adaptive: ins... |
| 194 | edit | not_better | 0.8857 | 0.9817 | $0.0007 | I'll switch the final tie-break from a soft residual preference to an explicit "least-waste that ... |
| 195 | edit | not_better | 0.9616 | 0.9817 | $0.0008 | Replace the median-multiple geometry with a lookup over the empirical item-size histogram: reward... |
| 196 | edit | not_better | 0.9616 | 0.9817 | $0.0007 | I'll add a "best-fit with reuse-aware tie-break" rule: keep the dominant smallest-residual (best-... |
| 197 | edit | not_better | 0.9614 | 0.9817 | $0.0008 | I'll shift from a "best-fit plus heuristic bonuses" rule to the classic near-optimal bin-packing ... |
| 198 | edit | not_better | 0.9814 | 0.9817 | $0.0007 | I'll replace the geometry with a "best-fit-decreasing-like" rule that scores each bin by the esti... |
| 199 | edit | not_better | 0.3966 | 0.9817 | $0.0008 | I'll replace the fragile per-item geometry with a value-function approximation: score each bin by... |
| 200 | edit | not_better | 0.8533 | 0.9817 | $0.0009 | I'll keep the current best-fit-plus-bonus backbone but replace the fixed median-multiple geometry... |
| 201 | edit | not_better | 0.9616 | 0.9817 | $0.0006 | I'll simplify to a pure best-fit rule with a much stronger exact-fit bonus and a sharper unusable... |
| 202 | edit | improved | 0.9893 | 0.9893 | $0.0008 | Add a harmonic-weighted exact-fill bonus: in addition to the exact-fit bonus, reward bins whose r... |
| 203 | edit | improved | 0.9915 | 0.9915 | $0.0009 | Add a proactive "future-fit" term: for each candidate bin, quantify how well the resulting residu... |
| 204 | edit | not_better | 0.9898 | 0.9915 | $0.0010 | I'll add a "mode-fit" term that rewards residuals close to the empirical mode (most frequent item... |
| 205 | edit | not_better | 0.9517 | 0.9915 | $0.0010 | I'll replace the hand-tuned geometry with a proper one-step look-ahead score: for each candidate ... |
| 206 | edit | not_better | 0.9912 | 0.9915 | $0.0010 | I'll replace the mid-range "fit_future" term (reward residuals near the mean) with a sharper sign... |
| 207 | edit | improved | 0.9917 | 0.9917 | $0.0011 | I'll add a small "residual conservation" term that rewards placing an item into a bin whose resid... |
| 208 | edit | improved | 0.9920 | 0.9920 | $0.0013 | Replace the generic band/peak kernel with a histogram-weighted residual reward: for each candidat... |
| 209 | edit | gate_rejected | 0.9920 | 0.9920 | $0.0014 | I'll add an adaptive anti-fragmentation term: penalize placing into a bin whose resulting residua... |
| 210 | edit | not_better | 0.9915 | 0.9920 | $0.0012 | I'll strengthen the dominant signal by increasing the weight on residuals that exactly match a fr... |
| 211 | edit | gate_rejected | 0.9922 | 0.9920 | $0.0014 | I'll add a small one-step "pairing" look-ahead: for each candidate bin, reward residuals that are... |
| 212 | edit | invalid | 0.0000 | 0.9920 | $0.0015 | I'll replace the fragile per-residual histogram matching with a bounded "expected exact-completio... |
| 213 | edit | improved | 0.9927 | 0.9927 | $0.0015 | I'll add a cheap local-search "repack" improvement: whenever the greedy choice would leave a sliv... |
| 214 | edit | not_better | 0.9925 | 0.9927 | $0.0015 | I'll add a cheap online "residual-sum" statistic: track the frequency-weighted expectation that a... |
| 215 | edit | not_better | 0.9885 | 0.9927 | $0.0015 | Sharpen and strengthen the exact-histogram-match signal (the dominant useful term) while damping ... |
| 216 | edit | invalid | 0.0000 | 0.9927 | $0.0017 | I'll switch the dominant signal from "residual near a common item size" to a one-step expected-co... |
| 217 | edit | not_better | 0.9927 | 0.9927 | $0.0014 | I'll add a fast, bounded "bin kind" tie-break that tracks the current residual profile and prefer... |
| 218 | edit | not_better | 0.9903 | 0.9927 | $0.0016 | I'll add a bounded one-step look-ahead "pairing" bonus: for each candidate residual r, credit it ... |
| 219 | edit | not_better | 0.9761 | 0.9927 | $0.0011 | I'll replace the hand-tuned mixture of weak terms (band, fit_future, frac, sliver) with a single ... |
| 220 | edit | not_better | 0.9640 | 0.9927 | $0.0016 | I'll damp the noisy sharp histogram-match term and replace it with a smoother, mode-focused compl... |
| 221 | edit | not_better | 0.9922 | 0.9927 | $0.0015 | I'll replace the brittle per-integer sharp histogram match with a smooth residual-completion bonu... |
| 222 | edit | not_better | 0.9915 | 0.9927 | $0.0015 | I will add a one-step "expected future-fit" bonus that rewards placing the item so the resulting ... |
| 223 | edit | not_better | 0.9907 | 0.9927 | $0.0017 | Add a one-step-ahead "sum-completion" bonus: precompute the empirical distribution of the sum of ... |
| 224 | edit | not_better | 0.9628 | 0.9927 | $0.0016 | I'll reduce the noisy histogram-weighting bonus (which recent experiments repeatedly showed to hu... |
| 225 | edit | not_better | 0.9609 | 0.9927 | $0.0013 | Replace the noisy histogram-match bonus with a robust "near-perfect-fit" reward that strongly pre... |
| 226 | edit | not_better | 0.9888 | 0.9927 | $0.0016 | I'll add a "deny-bad-fit" term that penalizes a candidate bin more when the resulting residual is... |
| 227 | edit | not_better | 0.9616 | 0.9927 | $0.0008 | I'll simplify and stabilize the scoring by dropping the noisy histogram-match and band terms that... |
| 228 | edit | not_better | 0.9616 | 0.9927 | $0.0008 | I will replace the noisy per-integer histogram-match bonus with a compact closed-form best-fit-pl... |
| 229 | edit | not_better | 0.9910 | 0.9927 | $0.0016 | I will add a linear "hindsight-guided" term that rewards residuals close to the average remaining... |
| 230 | edit | not_better | 0.9912 | 0.9927 | $0.0015 | I will replace the noisy histogram-match term with a robust "score as negative residual gap to th... |
| 231 | edit | not_better | 0.9907 | 0.9927 | $0.0014 | I will replace the spiky, noise-prone histogram frequency bonus with a smoothed, robust "future-c... |
| 232 | edit | not_better | 0.9912 | 0.9927 | $0.0014 | I'll replace the noisy per-size histogram match bonus with a small direct optimization: for each ... |
| 233 | edit | not_better | 0.9915 | 0.9927 | $0.0015 | I'll replace the noisy per-residual histogram terms with a stronger, cleaner best-fit-plus-exact-... |
| 234 | edit | not_better | 0.9917 | 0.9927 | $0.0016 | I will add a "two-item completion" potential term: using the online histogram, reward residuals r... |
| 235 | edit | not_better | 0.9624 | 0.9927 | $0.0013 | I'll add a "projected leftover" term that, for each candidate bin, estimates the expected remaini... |
| 236 | edit | not_better | 0.9927 | 0.9927 | $0.0015 | I'll add a mild "fragment-avoidance" tie-break term that penalizes residuals which are just sligh... |
| 237 | edit | not_better | 0.9607 | 0.9927 | $0.0015 | I'll replace the small constant tie-break term with a full best-fit residual (favoring the fulles... |
| 238 | edit | not_better | 0.9898 | 0.9927 | $0.0015 | I will multiply the sliver penalty by the probability that the upcoming items can actually be exp... |
| 239 | edit | not_better | 0.9917 | 0.9927 | $0.0015 | I will replace the noisy histogram-based residual bonus with a cleaner, cheaper "exact-fill proba... |
| 240 | edit | not_better | 0.9438 | 0.9927 | $0.0016 | I'll replace the histogram-based residual bonus (which is noisy) with a scale-aware residual rewa... |
| 241 | edit | not_better | 0.9915 | 0.9927 | $0.0015 | I'll add a modest "≥2 future items fit" bonus: reward residuals large enough to hold at least two... |
| 242 | edit | not_better | 0.9920 | 0.9927 | $0.0016 | I'll add a subtle "avoid creating an unfillable medium sliver" term: penalize residuals that are ... |
| 243 | edit | not_better | 0.9915 | 0.9927 | $0.0016 | I'll add a "closing-residual" bonus that strongly rewards leaving a residual that is small enough... |
| 244 | edit | not_better | 0.9616 | 0.9927 | $0.0009 | I'll replace the whole scoring rule with a cleaner best-fit-with-exact-fill-bonus formulation: th... |
| 245 | edit | not_better | 0.9915 | 0.9927 | $0.0015 | I will reduce the magnitude of the histogram-weighted residual bonus term (8.0 → 2.0) since the m... |
| 246 | edit | not_better | 0.9910 | 0.9927 | $0.0015 | I will reduce the sliver penalty coefficient (0.75 → 0.6) and tiny penalty (0.5 → 0.4) modestly, ... |
| 247 | edit | not_better | 0.9600 | 0.9927 | $0.0010 | I will simplify the residual scoring by dropping the noisy histogram/band bonuses and the exact-m... |
| 248 | edit | not_better | 0.9890 | 0.9927 | $0.0015 | I'll add a "weighted best-fit" tilt: among bins that fit, prefer ones whose residual (after placi... |
| 249 | edit | not_better | 0.9912 | 0.9927 | $0.0015 | I'll strengthen the exact-fill signal by rewarding residuals that equal a common item size with a... |
| 250 | edit | not_better | 0.9917 | 0.9927 | $0.0015 | (no description) |
| 251 | edit | not_better | 0.9614 | 0.9927 | $0.0011 | I'll replace the noisy histogram/band/multiples bonuses with a simpler, more robust rule: best-fi... |
| 252 | edit | not_better | 0.9927 | 0.9927 | $0.0014 | I'll strengthen the best-fit tie-break by making it prefer bins whose residual is closest to a ty... |
| 253 | edit | not_better | 0.9922 | 0.9927 | $0.0015 | I will replace the fixed "exact fill" bonus constant by making the perfect-fit bonus grow when ma... |
| 254 | edit | not_better | 0.9903 | 0.9927 | $0.0016 | I'll add a light "sum-2 items" future-fit term: reward residuals that equal the sum of two common... |
| 255 | edit | not_better | 0.9907 | 0.9927 | $0.0015 | I will lean on a robust best-fit core but additionally protect residuals that are "almost exactly... |
| 256 | edit | not_better | 0.9616 | 0.9927 | $0.0009 | I'll simplify and strengthen the core: replace the noisy multi-term scoring with a clean best-fit... |
| 257 | edit | not_better | 0.9925 | 0.9927 | $0.0015 | Introduce a "large-item reserve" term: since future items have mean ~40, when the current item is... |
| 258 | edit | not_better | 0.9910 | 0.9927 | $0.0015 | I'll add a compact "exact complement" lookup: precompute, for each residual 0..100, the probabili... |
| 259 | edit | not_better | 0.9920 | 0.9927 | $0.0016 | I'll strengthen the histogram-driven exact-fill bonus by making it depend on the actual observed ... |
| 260 | edit | not_better | 0.9922 | 0.9927 | $0.0014 | I will remove the weak/noisy future-fit and band terms and instead sharpen the proven best-fit co... |
| 261 | edit | not_better | 0.9616 | 0.9927 | $0.0014 | I'll replace the current multi-term scoring with a significantly stronger "best fit plus short-lo... |
| 262 | edit | not_better | 0.9920 | 0.9927 | $0.0015 | I will keep the proven best-fit core intact and add one cheap, robust improvement: a "second-chan... |
| 263 | edit | not_better | 0.9584 | 0.9927 | $0.0011 | I'll replace the noisy multi-term score with a clean, well-tuned best-fit core combined with a ca... |
| 264 | edit | not_better | 0.9846 | 0.9927 | $0.0015 | Add a "sum-of-two-complements" bonus: precompute the empirical probability that a single future i... |
| 265 | edit | not_better | 0.9917 | 0.9927 | $0.0013 | I will add a small "residual equals a frequent future item size" bonus using the raw empirical fr... |
| 266 | edit | not_better | 0.9614 | 0.9927 | $0.0010 | Replace the noisy multi-term scoring with a pure tamed best-fit that minimizes residual while add... |
| 267 | edit | not_better | 0.9858 | 0.9927 | $0.0014 | I'll keep the proven core but replace the noisy integer-index histogram terms with a smooth, well... |
| 268 | edit | not_better | 0.9614 | 0.9927 | $0.0010 | I'll replace the convoluted, noisy multi-term score with a clean pure best-fit core (minimize res... |
| 269 | edit | not_better | 0.9915 | 0.9927 | $0.0013 | I will remove the noisy Gaussian-smoothed integer-histogram near term and the band kernel term, r... |
| 270 | edit | not_better | 0.9903 | 0.9927 | $0.0015 | I'll add a simple, robust "best-fit decreasing-like" tie-breaker improvement: track the empirical... |
| 271 | edit | not_better | 0.9917 | 0.9927 | $0.0015 | I will add a small "worst-fit tie-break under equal exactness" adjustment: when several bins give... |
| 272 | edit | not_better | 0.9903 | 0.9927 | $0.0016 | I'll refine the sliver/tiny penalties and the future-fit term so that the algorithm avoids leavin... |
| 273 | edit | not_better | 0.9761 | 0.9927 | $0.0016 | I will add a lightweight, periodically-rebuilt lookup table scoring each possible residual by the... |
| 274 | edit | not_better | 0.9752 | 0.9927 | $0.0014 | I'll replace the ad-hoc combination of penalties with a single principled "expected residual qual... |
| 275 | edit | not_better | 0.9920 | 0.9927 | $0.0015 | I'll add a pairwise "matching" mechanism: before falling back to the current scoring, if the curr... |
| 276 | edit | not_better | 0.9905 | 0.9927 | $0.0017 | I'll retune the existing score's coefficients by using a small search-free analytic insight: stre... |
| 277 | edit | not_better | 0.9134 | 0.9927 | $0.0011 | I'll replace the fragile polynomial+empirical scoring with a principled "online best-fit with res... |
| 278 | edit | not_better | 0.9614 | 0.9927 | $0.0013 | I'll add a first-fit-decreasing-inspired fallback: when the item's size is larger than a threshol... |
| 279 | edit | not_better | 0.9927 | 0.9927 | $0.0015 | I will replace the ad-hoc residual scoring with a direct "best-fit with a small future-fit tie-br... |
| 280 | edit | not_better | 0.9910 | 0.9927 | $0.0015 | I'll add a targeted "perfect-completion" table: periodically compute, for each possible residual ... |
| 281 | edit | not_better | 0.9927 | 0.9927 | $0.0015 | I'll add a lightweight "avoid orphaning" term: penalize creating a residual that is smaller than ... |
| 282 | edit | not_better | 0.9908 | 0.9927 | $0.0014 | I'll add a "pair-closure" table rebuilt periodically: for each candidate residual r, estimate the... |
| 283 | edit | not_better | 0.9912 | 0.9927 | $0.0015 | I will add a "order-preserving pairwise closure" term: track, for each pair of recently seen item... |
| 284 | edit | not_better | 0.9915 | 0.9927 | $0.0016 | I'll add a "conservation-weighted best-fit" term: penalize the fraction of capacity wasted when o... |
| 285 | edit | not_better | 0.9893 | 0.9927 | $0.0015 | I'll replace the empirical-frequency residual reward with a "close to a common item size" kernel ... |
| 286 | edit | not_better | 0.9920 | 0.9927 | $0.0015 | I'll make the residual bonus scale with item size: when the current item is small, creating a res... |
| 287 | edit | not_better | 0.9907 | 0.9927 | $0.0013 | I'll add a mild item-size-adaptive best-fit tightening: for large items (above the median), prefe... |
| 288 | edit | not_better | 0.9849 | 0.9927 | $0.0014 | I'll reduce the harmonic waste-fraction penalty's coefficient and make it scale down as bins fill... |
| 289 | edit | not_better | 0.9927 | 0.9927 | $0.0016 | I'll add an "opening-cost awareness" term: when no fitting bin is sufficiently full, opening a ne... |
| 290 | edit | not_better | 0.9907 | 0.9927 | $0.0016 | I'll replace the fixed best-fit tie-break coefficient with a mild "fuller-bin" preference that is... |
| 291 | edit | not_better | 0.9920 | 0.9927 | $0.0016 | I will add a "post-placement residual usefulness" term that scores a bin by how valuable the *res... |
| 292 | edit | not_better | 0.9927 | 0.9927 | $0.0014 | I will change the exact-fill bonus logic so that it is only applied when the residual is exactly ... |
| 293 | edit | not_better | 0.9917 | 0.9927 | $0.0014 | I'll simplify the empirical residual reward to use the exact histogram probability at the rounded... |
| 294 | edit | not_better | 0.9912 | 0.9927 | $0.0014 | I'll drop the noisy histogram-based residual reward (which past attempts show is unhelpful) and i... |
| 295 | edit | not_better | 0.9922 | 0.9927 | $0.0011 | I'll replace the heuristic mix with a cleaner, stronger best-fit variant: keep the exact-fit bonu... |
| 296 | edit | not_better | 0.9912 | 0.9927 | $0.0015 | I'll add a "reserve tracker" over open bins' residuals so the heuristic prefers leaving residuals... |
| 297 | edit | not_better | 0.9900 | 0.9927 | $0.0015 | I'll add a per-bin "age" statistic: track each bin's residual and reward placing the current item... |
| 298 | edit | not_better | 0.9616 | 0.9927 | $0.0010 | I'll strip out the many heuristic terms and replace the score with a pure best-fit (minimize resu... |
| 299 | edit | not_better | 0.9616 | 0.9927 | $0.0010 | I will replace the noisy median-multiple and harmonic terms with a cleaner best-fit core plus a s... |
| 300 | edit | not_better | 0.9616 | 0.9927 | $0.0007 | I'll replace the noisy heuristic with a clean "best-fit plus exact-fit" rule: choose the bin whos... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,123 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best-fit with usable-gap bonus, empirical future-fit term, and a
+histogram-weighted residual reward that favors residuals matching common
+future item sizes (likely to be completed exactly). Uses a periodically
+rebuilt lookup table to stay fast."""
 import numpy as np
+
+# Module-level state (fresh per instance).
+_sum = 0.0
+_n = 0
+_hist = np.zeros(101, dtype=np.float64)
+_median = 40.0
+_min_item = 1.0
+_mean = 40.0
+_pmax = 0.02  # max single-size probability estimate
+_q25 = 25.0
+_q75 = 55.0
+
+# Cached lookup tables (rebuilt periodically, cheap).
+_pfreq_tab = np.zeros(101, dtype=np.float64)   # surviving frequency prob per integer size
+_band_tab = np.zeros(101, dtype=np.float64)    # band kernel per residual 0..100
+_near_tab = np.zeros(101, dtype=np.float64)    # near kernel weight for integer match
+_last_build = -1
+
+
+def _rebuild():
+    global _pfreq_tab, _band_tab, _near_tab, _median, _min_item, _mean, _pmax, _q25, _q75
+    total = float(np.sum(_hist[1:101]))
+    if total <= 0:
+        return
+    cdf = np.cumsum(_hist[1:101])
+    idx = np.searchsorted(cdf, 0.5 * total)
+    _median = float(idx + 1)
+    i25 = np.searchsorted(cdf, 0.25 * total)
+    i75 = np.searchsorted(cdf, 0.75 * total)
+    _q25 = float(i25 + 1)
+    _q75 = float(i75 + 1)
+    nz = np.nonzero(_hist[1:101])[0]
+    if nz.size > 0:
+        _min_item = float(nz[0] + 1)
+    _mean = _sum / _n
+    _pmax = max(float(np.max(_hist[1:101]) / total), 1e-3)
+
+    _pfreq_tab[:] = _hist / total
+    # band kernel over residual integer values 0..100
+    lo, hi = _q25, _q75
+    width = max(hi - lo, 1.0) * 0.5 + 1.0
+    mid = 0.5 * (lo + hi)
+    x = np.arange(101, dtype=np.float64)
+    _band_tab[:] = np.exp(-((x - mid) ** 2) / (2.0 * width * width))
+    # near kernel: weight for residual matching the nearest integer (r - ri)^2
+    _near_tab[:] = np.exp(-1.0)
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Score each fitting bin; highest score wins (first on ties)."""
+    global _sum, _n, _median, _min_item, _mean, _pmax, _q25, _q75, _last_build
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    _sum += item
+    _n += 1
+    _hist[item] += 1.0
+
+    if _n >= 30 and (_n - _last_build >= 200 or _last_build < 0):
+        _rebuild()
+        _last_build = _n
+
+    typical = max(min(_median, 100.0), 1.0)
+    mean = max(min(_mean, 100.0), 1.0)
+
+    residual = bins.astype(np.float64) - item  # >= 0 for all shown bins
+    r = residual
+
+    # Exact fill: residual is 0 -> perfect, huge bonus.
+    exact = (r < 0.5).astype(np.float64)
+
+    # Distance of residual to multiples of a typical item size.
+    t = typical
+    k = np.rint(r / t)
+    dk = np.abs(r - k * t)
+    d0 = r
+    dist = np.minimum(d0, dk)
+
+    # Reward residuals that can host a typical (median/mean) future item well.
+    fit_future = np.abs(r - mean)
+
+    # Sliver penalty: too small to be usefully filled.
+    sliver = np.where((r > 0) & (r < 0.5 * t), 0.5 * t - r, 0.0)
+    tiny = np.where((r > 0) & (r < _min_item), _min_item - r, 0.0)
+
+    # Harmonic-style waste fraction term.
+    used = 100.0 - r
+    frac = np.where(used > 0, r / used, 0.0)
+
+    score = -(dist + 0.75 * sliver + 0.5 * tiny) + 5.0 * exact
+
+    # Moderate reward for residuals that can host a future average item.
+    score = score - 1.0 * fit_future * 0.05
+
+    score = score - 1.5 * frac
+
+    # Histogram-weighted residual reward: a residual equal to (or near) a
+    # frequently observed item size is likelier to be completed exactly soon.
+    if _n >= 30:
+        # nearest integer size to each residual (round, clamp to 1..100)
+        ri = np.clip(np.rint(r), 1.0, 100.0).astype(np.int64)
+        pfreq = _pfreq_tab[ri]
+        # fractional distance to that integer size, to soften the matching
+        near = np.exp(-((r - ri) ** 2) / (2.0 * 1.0))
+        score = score + 8.0 * pfreq * near
+
+        # Soft residual-conservation kernel: gentle bonus for residuals in the
+        # common future-item size range (25-75 percentile).
+        ri2 = np.clip(r, 0.0, 100.0)
+        score = score + 0.3 * np.interp(ri2, np.arange(101, dtype=np.float64), _band_tab)
+
+    # Exact fits get extra weight proportional to how likely that item is.
+    score = score + 20.0 * _pmax * exact
+
+    # Tie-break toward fuller placements (smaller residual).
+    score = score - 1e-3 * r
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (52 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 57 | `global _sum, _n, _median, _min_item, _mean, _pmax, _q25, _q75, _last_build` | -0.9927 | essential: the program fails or turns invalid without it |
| 67 | `typical = max(min(_median, 100.0), 1.0)` | -0.9927 | essential: the program fails or turns invalid without it |
| 68 | `mean = max(min(_mean, 100.0), 1.0)` | -0.9927 | essential: the program fails or turns invalid without it |
| 70 | `residual = bins.astype(np.float64) - item` | -0.9927 | essential: the program fails or turns invalid without it |
| 70 | `term + bins.astype(np.float64)` | -0.9927 | essential: the program fails or turns invalid without it |
| 71 | `r = residual` | -0.9927 | essential: the program fails or turns invalid without it |
| 74 | `exact = (r < 0.5).astype(np.float64)` | -0.9927 | essential: the program fails or turns invalid without it |
| 77 | `t = typical` | -0.9927 | essential: the program fails or turns invalid without it |
| 78 | `k = np.rint(r / t)` | -0.9927 | essential: the program fails or turns invalid without it |
| 79 | `dk = np.abs(r - k * t)` | -0.9927 | essential: the program fails or turns invalid without it |
| 80 | `d0 = r` | -0.9927 | essential: the program fails or turns invalid without it |
| 81 | `dist = np.minimum(d0, dk)` | -0.9927 | essential: the program fails or turns invalid without it |
| 84 | `fit_future = np.abs(r - mean)` | -0.9927 | essential: the program fails or turns invalid without it |
| 87 | `sliver = np.where((r > 0) & (r < 0.5 * t), 0.5 * t - r, 0.0)` | -0.9927 | essential: the program fails or turns invalid without it |
| 88 | `tiny = np.where((r > 0) & (r < _min_item), _min_item - r, 0.0)` | -0.9927 | essential: the program fails or turns invalid without it |
| 91 | `used = 100.0 - r` | -0.9927 | essential: the program fails or turns invalid without it |
| 92 | `frac = np.where(used > 0, r / used, 0.0)` | -0.9927 | essential: the program fails or turns invalid without it |
| 94 | `score = -(dist + 0.75 * sliver + 0.5 * tiny) + 5.0 * exact` | -0.9927 | essential: the program fails or turns invalid without it |
| 70 | `term - item` | -0.1121 | matters |
| 97 | `term + score` | -0.0694 | matters |
| 99 | `term + score` | -0.0304 | matters |
| 94 | `term + -(dist + 0.75 * sliver + 0.5 * tiny)` | -0.0285 | matters |
| 91 | `term + 100.0` | -0.0135 | matters |
| 99 | `score = score - 1.5 * frac` | -0.0135 | matters |
| 99 | `term - 1.5 * frac` | -0.0135 | matters |
| 91 | `term - r` | -0.0086 | matters |
| 94 | `term + 5.0 * exact` | -0.0081 | matters |
| 59 | `_sum += item` | -0.0035 | matters |
| 60 | `_n += 1` | -0.0030 | matters |
| 61 | `_hist[item] += 1.0` | -0.0030 | matters |
| 63 | `if _n >= 30 and (_n - _last_build >= 200 or _last_build < 0): ...` | -0.0030 | matters |
| 64 | `_rebuild()` | -0.0030 | matters |
| 65 | `_last_build = _n` | -0.0007 | no effect alone |
| 97 | `score = score - 1.0 * fit_future * 0.05` | -0.0007 | no effect alone |
| 97 | `term - 1.0 * fit_future * 0.05` | -0.0007 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 103: `if _n >= 30: ...`
- line 105: `ri = np.clip(np.rint(r), 1.0, 100.0).astype(np.int64)`
- line 106: `pfreq = _pfreq_tab[ri]`
- line 108: `near = np.exp(-(r - ri) ** 2 / (2.0 * 1.0))`
- line 109: `score = score + 8.0 * pfreq * near`
- line 109: `term + score`
- line 109: `term + 8.0 * pfreq * near`
- line 113: `ri2 = np.clip(r, 0.0, 100.0)`
- line 114: `score = score + 0.3 * np.interp(ri2, np.arange(101, dtype=np.float64), _band_tab)`
- line 114: `term + score`
- line 114: `term + 0.3 * np.interp(ri2, np.arange(101, dtype=np.float64), _band_tab)`

Not tested (evaluation limit 40): 13 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9927 | 0.9913 |
| minimal (1 parts removed) | 0.9922 | 0.9896 |

Minimal program:

```python
"""Best-fit with usable-gap bonus, empirical future-fit term, and a
histogram-weighted residual reward that favors residuals matching common
future item sizes (likely to be completed exactly). Uses a periodically
rebuilt lookup table to stay fast."""
import numpy as np
_sum = 0.0
_n = 0
_hist = np.zeros(101, dtype=np.float64)
_median = 40.0
_min_item = 1.0
_mean = 40.0
_pmax = 0.02
_q25 = 25.0
_q75 = 55.0
_pfreq_tab = np.zeros(101, dtype=np.float64)
_band_tab = np.zeros(101, dtype=np.float64)
_near_tab = np.zeros(101, dtype=np.float64)
_last_build = -1

def _rebuild():
    global _pfreq_tab, _band_tab, _near_tab, _median, _min_item, _mean, _pmax, _q25, _q75
    total = float(np.sum(_hist[1:101]))
    if total <= 0:
        return
    cdf = np.cumsum(_hist[1:101])
    idx = np.searchsorted(cdf, 0.5 * total)
    _median = float(idx + 1)
    i25 = np.searchsorted(cdf, 0.25 * total)
    i75 = np.searchsorted(cdf, 0.75 * total)
    _q25 = float(i25 + 1)
    _q75 = float(i75 + 1)
    nz = np.nonzero(_hist[1:101])[0]
    if nz.size > 0:
        _min_item = float(nz[0] + 1)
    _mean = _sum / _n
    _pmax = max(float(np.max(_hist[1:101]) / total), 0.001)
    _pfreq_tab[:] = _hist / total
    lo, hi = (_q25, _q75)
    width = max(hi - lo, 1.0) * 0.5 + 1.0
    mid = 0.5 * (lo + hi)
    x = np.arange(101, dtype=np.float64)
    _band_tab[:] = np.exp(-(x - mid) ** 2 / (2.0 * width * width))
    _near_tab[:] = np.exp(-1.0)

def priority(item, bins):
    """Score each fitting bin; highest score wins (first on ties)."""
    global _sum, _n, _median, _min_item, _mean, _pmax, _q25, _q75, _last_build
    _sum += item
    _n += 1
    _hist[item] += 1.0
    if _n >= 30 and (_n - _last_build >= 200 or _last_build < 0):
        _rebuild()
        _last_build = _n
    typical = max(min(_median, 100.0), 1.0)
    mean = max(min(_mean, 100.0), 1.0)
    residual = bins.astype(np.float64) - item
    r = residual
    exact = (r < 0.5).astype(np.float64)
    t = typical
    k = np.rint(r / t)
    dk = np.abs(r - k * t)
    d0 = r
    dist = np.minimum(d0, dk)
    fit_future = np.abs(r - mean)
    sliver = np.where((r > 0) & (r < 0.5 * t), 0.5 * t - r, 0.0)
    tiny = np.where((r > 0) & (r < _min_item), _min_item - r, 0.0)
    used = 100.0 - r
    frac = np.where(used > 0, r / used, 0.0)
    score = -(dist + 0.75 * sliver + 0.5 * tiny) + 5.0 * exact
    score = score - 1.0 * fit_future * 0.05
    score = score - 1.5 * frac
    score = score + 20.0 * _pmax * exact
    score = score - 0.001 * r
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online_informed --budget 0.35 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 2
python -m autoresearch.loop --report experiments/llm-informed-v1/runs/s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `e2e4b819db731494ff3f073c8d5d83829038485d`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bin_packing_online_informed/evaluate.py` `0ac9a4a253a299d2`
- `problems/bin_packing_online_informed/initial.py` `609927c5ea619a94`
- `problems/bin_packing_online_informed/problem.md` `79846770d846c318`
- `problems/bin_packing_online_informed/verify.py` `b3ea67a1c6f94885`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
