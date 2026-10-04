# Research loop report: bin_packing_online_informed

| | |
|---|---|
| problem | `bin_packing_online_informed` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2596 of a $0.35 hard cap, 300 calls, 833,795 tokens |
| wall time | search 4783 s, baselines 63 s, explain 67 s |
| stopped | max_iters (stopped_early) |
| evaluations | 301 (296 valid), 12 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9885 | 0.9869 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online_informed/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_informed/baselines/funsearch_weibull.py` |
| baseline `fwss` | 0.9992 | 0.9990 | `problems/bin_packing_online_informed/baselines/fwss.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_informed/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9885 | 0.9869 | 1 parts removed |

Audit: public 0.9616 → 0.9885 (+0.0269), hidden 0.9604 → 0.9869 (+0.0264); public − hidden gap of the final program 0.0017.

Against the baselines: the final program's public score is below the best baseline (`fwss`, 0.9992). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Switch from pure best-fit to an adaptation of the Best-Fit-Decreasing idea: since we can't reorde... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the pure best-fit score with the classic "Subset Sum / minimum bins" style rule: score bi... |
| 3 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a score that combines best-fit tightness with a "residual usefulness" ... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a score that prefers bins whose resulting leftover capacity is "u... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a bounded-size best-fit variant: keep no more than a small "active set... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Add a one-step lookahead: track all open bins (including those the item doesn't fit in) using mod... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will implement a rank-based bin-choice heuristic that blends best-fit with a "least loaded bin"... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Implement the classic "best fit" but improved by a one-step-ahead "Harmonic/Sum-of-squares" style... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0010 | (no description) |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add a bounded "look-ahead conservative" rule: track all open bins in module state, and among... |
| 11 | edit | invalid | 0.0000 | 0.9616 | $0.0006 | Replace pure best-fit with a weighted blend of best-fit tightness and a distribution-aware residu... |
| 12 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a variant that, among bins the item fits in, prefers best-fit but brea... |
| 13 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I will replace the pure best-fit rule with a stateful "best fit decreasing with future-aware resi... |
| 14 | edit | not_better | 0.9357 | 0.9616 | $0.0006 | I'll implement the classic "Best Fit Decreasing"-style improvement adapted online: track all open... |
| 15 | edit | not_better | 0.8424 | 0.9616 | $0.0005 | I will replace pure best-fit with a conservative "best-fit with residual-floor guard": among fitt... |
| 16 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a tuned variant of the classic "best fit + harmonic-style scoring": ch... |
| 17 | edit | not_better | 0.9586 | 0.9616 | $0.0007 | I'll replace pure best-fit with a two-phase rule: run best-fit, but use module state to implement... |
| 18 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a stateless score that prefers tight fits but avoids stranding ti... |
| 19 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with Best-Fit-Decreasing-style "tightest fit with a lookahead residual guar... |
| 20 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll add a stateful "move-to-front on good fits" idea: track, from observed item sizes, the most ... |
| 21 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Implement a full "Best Fit with capacity-class bucketing plus a reserved-empty-bin policy": maint... |
| 22 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a score that combines tightest fit with a small preference for le... |
| 23 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace pure best-fit with a harmonic-style scoring that prefers placing items in bins by si... |
| 24 | edit | not_better | 0.9593 | 0.9616 | $0.0009 | Replace pure best-fit with a stateful "best fit with reserving one empty bin for large items" rul... |
| 25 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | I'll implement a stateful "Best-Fit with a big-item safeguard": track every open bin's remaining ... |
| 26 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll switch from pure best-fit to a size-class "harmonic"-style rule: classify each item by a siz... |
| 27 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace the pure best-fit rule with a variant that uses a capacity-class harmonic bucketing:... |
| 28 | edit | not_better | 0.9593 | 0.9616 | $0.0009 | I'll replace pure best-fit with a stateful "best-fit plus reserving bins whose residual exactly e... |
| 29 | edit | not_better | 0.9607 | 0.9616 | $0.0007 | Replace pure best-fit with a harmonic-style rule based on item size classes: for large items (>=5... |
| 30 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch the scoring from pure best-fit to a residual-based rule that targets a specific "targ... |
| 31 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | The previous attempts tried many static tweaks to pure best-fit and all scored lower. I'll try a ... |
| 32 | edit | not_better | 0.9616 | 0.9616 | $0.0010 | I'll replace pure best-fit with a stateful "best-fit-decreasing-lookahead" rule: track my own vie... |
| 33 | edit | not_better | 0.9595 | 0.9616 | $0.0008 | I'll try a two-stage rule: for each candidate bin, simulate placing the item, then greedily match... |
| 34 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll switch from pure best-fit to a "harmonic + best-fit hybrid" that classifies items into size ... |
| 35 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "least-loaded-fit" variant that deliberately spreads items to k... |
| 36 | edit | not_better | 0.9614 | 0.9616 | $0.0005 | I'll implement the Martello-Toth-style "best fit with a reserve for medium items" but tuned via a... |
| 37 | edit | not_better | 0.9612 | 0.9616 | $0.0006 | Replace pure best-fit with a "modified best-fit" rule: score each bin by residual-after-placement... |
| 38 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "best-fit plus full-bin-aware lookahead": track my own residual... |
| 39 | edit | not_better | 0.9612 | 0.9616 | $0.0007 | I'll replace pure best-fit with a best-fit criterion computed on the residual *after* the item, b... |
| 40 | edit | not_better | 0.9593 | 0.9616 | $0.0012 | I'll add state tracking of all items seen (including sizes of items that didn't fit any bin so I ... |
| 41 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace pure best-fit with a "least-loaded best-fit" hybrid using state: track the item size... |
| 42 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replicate the classic "Best Fit Decreasing"-like advantage online by using the item count and kno... |
| 43 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a state-tracking "best fit with a small-item fill preference": ... |
| 44 | edit | not_better | 0.9584 | 0.9616 | $0.0005 | I'll replace pure best-fit with a guard: keep best-fit normally, but when placing an item would l... |
| 45 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a "best fit with a fraction/pattern heuristic": track all item ... |
| 46 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace the pure best-fit with a "best fit decreasing simulation": since the distribution is... |
| 47 | edit | not_better | 0.9614 | 0.9616 | $0.0007 | I'll implement a learned/statistical "best fit with residual-value scoring" that also considers h... |
| 48 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a hybrid that tracks the empirical item-size distribution: use be... |
| 49 | edit | not_better | 0.9318 | 0.9616 | $0.0005 | I will implement a "Best Fit with small-item prefer-full-under-50" heuristic: use plain best-fit ... |
| 50 | edit | not_better | 0.9572 | 0.9616 | $0.0005 | I'll implement a proper Best-Fit-Decreasing-style improvement by exploiting the known number of i... |
| 51 | edit | not_better | 0.9612 | 0.9616 | $0.0008 | I'll implement a proper "best fit with lookahead-free residual pairing plus anti-fragmentation": ... |
| 52 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Implement a two-choice heuristic: for small items (the ones that cause fragmentation), pick the b... |
| 53 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a "modified best-fit" that adds a tiny tie-breaking term favori... |
| 54 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace pure best-fit with a harmonic/graded best-fit variant: score bins primarily by classic be... |
| 55 | edit | not_better | 0.9593 | 0.9616 | $0.0006 | I will replace pure best-fit with a "residual-aware best fit" that keeps my own full residual-cap... |
| 56 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | I'll replace pure best-fit with a "best fit with near-full-bin preference": among bins where the ... |
| 57 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace pure best-fit with a residual-aware policy that reserves room for large items: keep ... |
| 58 | edit | not_better | 0.7074 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "least-loaded among fitting bins with a cap" strategy: since th... |
| 59 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll add a bounded-lookahead pairing heuristic: track my own residual array, and after a best-fit... |
| 60 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace pure best-fit with a variant that keeps the classic best-fit ordering but adds a s... |
| 61 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a "combined best-fit with sum-of-squares residual minimization": instead of only m... |
| 62 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll implement a "best fit decreasing-style" online heuristic that mimics the effective First-Fit... |
| 63 | edit | not_better | 0.9311 | 0.9616 | $0.0006 | Replace best-fit's linear residual minimization with a nonlinear score that strongly rewards near... |
| 64 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll keep best-fit as the fallback but add an online "reserve a bin for large items" rule: track ... |
| 65 | edit | not_better | 0.9593 | 0.9616 | $0.0004 | I will switch the base rule to first-fit (lowest bin index among bins that fit) instead of best-f... |
| 66 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I will implement an online "best-fit with lazy bin opening" variant: keep pure best-fit ordering,... |
| 67 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a harmony-search style hybrid of best-fit and worst-fit: score each bin primarily ... |
| 68 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will add a state-tracking "best fit with matching-residual consolidation": still rank by result... |
| 69 | edit | not_better | 0.8575 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "best-fit plus sub-40 large-item reservation" rule: track open-... |
| 70 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll implement a "minimum bin slack" style rule that generalizes best-fit: instead of placing the... |
| 71 | edit | not_better | 0.9605 | 0.9616 | $0.0008 | I'll add a "sub-40 tail bin" rule on top of best-fit: track seen item sizes and open-bin residual... |
| 72 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with "best-fit among non-empty bins, else the bin that best preserves ... |
| 73 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will add a stateful online heuristic that tracks open-bin residuals across calls and, on top of... |
| 74 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with "best fit + look-ahead residual pairing": keep the standard best-... |
| 75 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace best-fit with a stateful "Hoffmann-style" rule: track every bin's residual myself and, fo... |
| 76 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "best fit with a perfect-fit-into-residual (dual feasible) tie-... |
| 77 | edit | not_better | 0.9614 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a hybrid "best-fit with score-based sub-optimal acceptance for ... |
| 78 | edit | not_better | 0.9616 | 0.9616 | $0.0012 | I'll replace pure best-fit with a score that values each candidate bin by how close its post-plac... |
| 79 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will implement a full-blown stateful bin-packing heuristic that tracks the residual of every op... |
| 80 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace the pure best-fit rule with a harmonic-style ranking: score each bin by the smallest... |
| 81 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll switch to a size-class-aware best-fit that uses the known number of items and running mean t... |
| 82 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a stateful "sampling + randomized best-fit-with-residual-matching" sch... |
| 83 | edit | not_better | 0.9586 | 0.9616 | $0.0008 | Replace pure best-fit with a stateful "sum-of-squares residual" (lower-bound style) scoring rule:... |
| 84 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace best-fit with a stateful "best fit but reserve a special case for near-perfect fits"... |
| 85 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a stateful rule that tracks all open-bin residuals and uses the "adapt... |
| 86 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "best-fit that reserves room for later large items" rule: maint... |
| 87 | edit | not_better | 0.9612 | 0.9616 | $0.0005 | I'll try a two-size-class rule based on the Weibull mean: for items larger than a threshold use w... |
| 88 | edit | not_better | 0.9586 | 0.9616 | $0.0007 | Replace pure best-fit with a stateful rule that tracks all bin residuals and adds a small bonus f... |
| 89 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Keep pure best-fit ordering but add a tiny epsilon bonus for a bin that gets exactly filled (post... |
| 90 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace pure best-fit with a stateful "least-loaded / worst-fit" scoring only for very large item... |
| 91 | edit | not_better | 0.9593 | 0.9616 | $0.0006 | I'll add a stateful "completion + large-item reservation" tweak: keep pure best-fit as the primar... |
| 92 | edit | invalid | 0.0000 | 0.9616 | $0.0009 | Replace pure best-fit with best-fit plus a score tie-break that prefers bins whose post-placement... |
| 93 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll implement the classic "refined harmonic" / Martello-Toth-style bucketing adapted as a statef... |
| 94 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll switch from pure best-fit to a best-fit rule that only chooses among bins already containing... |
| 95 | edit | improved | 0.9623 | 0.9623 | $0.0005 | Replace pure best-fit with a rule that keeps best-fit as the primary ordering but, when the item ... |
| 96 | edit | not_better | 0.9623 | 0.9623 | $0.0006 | I will add a tiny epsilon bonus (0.5) to bins whose post-placement residual is below a small thre... |
| 97 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll make best-fit smarter by adding a "residual preservation" term: after placing the item, comp... |
| 98 | edit | improved | 0.9626 | 0.9626 | $0.0007 | Add a complementary-pair tracking bonus: when an open bin's post-placement residual would create ... |
| 99 | edit | not_better | 0.9626 | 0.9626 | $0.0007 | I'll replace the noisy frequency-based residual bonus with a cleaner, more reliable rule: strongl... |
| 100 | edit | not_better | 0.9621 | 0.9626 | $0.0007 | I'll track the full bin state myself and use a "best-fit with an anti-fragmentation guard": prefe... |
| 101 | edit | not_better | 0.9623 | 0.9626 | $0.0009 | I'll replace the noisy frequency bonus with a robust "residual-clustering" term: I track my own v... |
| 102 | edit | not_better | 0.9621 | 0.9626 | $0.0008 | I'll add a "same-residual clustering" dynamic term that rewards placing the item where the result... |
| 103 | edit | not_better | 0.9619 | 0.9626 | $0.0008 | I'll replace the fragile cosmetic bonuses with a principled "score = negative post-residual plus ... |
| 104 | edit | not_better | 0.9626 | 0.9626 | $0.0008 | I'll replace the ad-hoc residual bonuses with a principled "pairing value" that estimates, from t... |
| 105 | edit | not_better | 0.9616 | 0.9626 | $0.0007 | I'll replace the noisy frequency/pairing bonuses with a cleaner learned-lookahead: track the empi... |
| 106 | edit | improved | 0.9628 | 0.9628 | $0.0008 | I'll add a lightweight "avoid creating a tiny unusable residual" guard: when the post-placement r... |
| 107 | edit | invalid | 0.0000 | 0.9628 | $0.0008 | I'll replace the weak tiny-orphan nudge with a stronger, principled "waste-aware" score: instead ... |
| 108 | edit | not_better | 0.9628 | 0.9628 | $0.0008 | I'll add a small linear penalty on the total residual left in the target bin (i.e. proportional t... |
| 109 | edit | not_better | 0.9623 | 0.9628 | $0.0007 | I'll replace the noisy frequency/linear penalties with a "largest-fitting-item match" heuristic: ... |
| 110 | edit | not_better | 0.9628 | 0.9628 | $0.0008 | I'll add a mild "sub-100 gap avoidance" term: penalize the target bin by a small amount proportio... |
| 111 | edit | not_better | 0.9626 | 0.9628 | $0.0007 | Replace the noisy empirical bonuses with a clean "residual pairability" score: strong best-fit ba... |
| 112 | edit | not_better | 0.9626 | 0.9628 | $0.0008 | I'll add a lookahead term based on the empirical distribution: for each candidate post-placement ... |
| 113 | edit | not_better | 0.9614 | 0.9628 | $0.0007 | I'll replace the current scoring with a "best fit plus double-match lookahead": keep the strong b... |
| 114 | edit | not_better | 0.9584 | 0.9628 | $0.0007 | I'll replace the noisy histogram bonuses with a principled "residual completion value": since bes... |
| 115 | edit | not_better | 0.9626 | 0.9628 | $0.0008 | I'll sharpen the anti-orphan term: instead of a flat penalty for residuals 1–4, penalize a residu... |
| 116 | edit | not_better | 0.9623 | 0.9628 | $0.0006 | I'll replace the noisy empirical bonuses with a classic robust best-fit plus a single principled ... |
| 117 | edit | improved | 0.9635 | 0.9635 | $0.0008 | I'll replace the ad-hoc bonuses with a principled "best-fit + empirical future-fill probability" ... |
| 118 | edit | not_better | 0.9616 | 0.9635 | $0.0007 | I'll replace the noisy ad-hoc bonuses with a clean, principled score: track a full running histog... |
| 119 | edit | not_better | 0.9628 | 0.9635 | $0.0008 | I will add a "large-residual utility" term: since best-fit alone tends to leave many tiny unfilla... |
| 120 | edit | not_better | 0.9635 | 0.9635 | $0.0009 | I'll strengthen the "complementary pair" logic: strongly prefer placing the item into a bin whose... |
| 121 | edit | not_better | 0.9396 | 0.9635 | $0.0008 | I'll replace the ad-hoc bonus stack with a cleaner score that keeps best-fit as the dominant term... |
| 122 | edit | not_better | 0.9623 | 0.9635 | $0.0009 | I'll add a principled "sum-based fit" refinement: track my own view of each open bin's remaining ... |
| 123 | edit | not_better | 0.9635 | 0.9635 | $0.0010 | I'll estimate the expected future usability of each candidate residual by summing, over the runni... |
| 124 | edit | not_better | 0.9607 | 0.9635 | $0.0007 | Replace the noisy empirical bonuses with a "critical-fill" best-fit rule: keep best-fit dominant,... |
| 125 | edit | not_better | 0.9626 | 0.9635 | $0.0008 | I'll replace the ad-hoc bonus stack with a clean score that keeps best-fit dominant but adds a pr... |
| 126 | edit | not_better | 0.9626 | 0.9635 | $0.0007 | I will replace the ad-hoc score with a clean "best-fit plus exact-fill and complement matching" r... |
| 127 | edit | not_better | 0.9563 | 0.9635 | $0.0009 | I will add a directional learning term: track the histogram of residuals that were later successf... |
| 128 | edit | not_better | 0.9621 | 0.9635 | $0.0008 | Replace the ad-hoc bonus stack with a single principled rule: keep best-fit dominant, but among b... |
| 129 | edit | not_better | 0.9635 | 0.9635 | $0.0010 | I will switch the base tie-breaker from my own negative residual (best-fit) to a "least load then... |
| 130 | edit | not_better | 0.9635 | 0.9635 | $0.0008 | I'll replace the noisy, hand-tuned bonus stack with a cleaner and stronger rule: keep best-fit do... |
| 131 | edit | not_better | 0.9609 | 0.9635 | $0.0007 | I'll replace the ad-hoc bonus stack with a calibrated best-fit rule that only breaks near-ties: p... |
| 132 | edit | not_better | 0.9614 | 0.9635 | $0.0008 | I'll replace the bonus stack with a single principled term: keep best-fit dominant, but reward po... |
| 133 | edit | not_better | 0.9612 | 0.9635 | $0.0008 | I'll replace the ad-hoc bonus stack with a principled term that measures how well each residual c... |
| 134 | edit | improved | 0.9725 | 0.9725 | $0.0009 | I'll replace the best-fit-plus-bonus stack with the classic "Worst-Fit"-style score among a restr... |
| 135 | edit | not_better | 0.9725 | 0.9725 | $0.0009 | I will strengthen the exact-complement pairing rule: give a large bonus when the post-placement r... |
| 136 | edit | improved | 0.9783 | 0.9783 | $0.0017 | I'll convert the one-sided "common residual" bonus into a mean-centered (two-sided) commonness si... |
| 137 | edit | improved | 0.9788 | 0.9788 | $0.0010 | I will add a "sum-completion" lookahead: reward a candidate bin when the residual after placement... |
| 138 | edit | not_better | 0.9778 | 0.9788 | $0.0010 | I'll replace the convolution-based two-item sum-completion term (which rewards matching *any* com... |
| 139 | edit | not_better | 0.9775 | 0.9788 | $0.0011 | I will add an explicit "avoid creating small residual orphans" guard: strongly penalize post-plac... |
| 140 | edit | not_better | 0.9780 | 0.9788 | $0.0011 | I'll make the item-size distribution estimate adaptive and, more importantly, add a soft "reserve... |
| 141 | edit | not_better | 0.9785 | 0.9788 | $0.0010 | I'll replace the histogram-based lookahead terms with a principled "residual completion probabili... |
| 142 | edit | not_better | 0.9780 | 0.9788 | $0.0010 | I will add a "least-loaded-among-fitting" tie-break nudge: when residuals are close (within a few... |
| 143 | edit | not_better | 0.9619 | 0.9788 | $0.0010 | I will replace the multiple heuristic bonus terms with a single principled "residual satisfiabili... |
| 144 | edit | not_better | 0.9756 | 0.9788 | $0.0011 | I'll add a recency-weighted (exponentially decayed) histogram of item sizes used for the exact-fi... |
| 145 | edit | not_better | 0.9716 | 0.9788 | $0.0010 | I'll add a "reserve the least-loaded bin" guard: strongly penalize placing an item into the empty... |
| 146 | edit | not_better | 0.9783 | 0.9788 | $0.0010 | I will add a "worst-fit-slack" penalty term that slightly discourages leaving large residuals in ... |
| 147 | edit | not_better | 0.9637 | 0.9788 | $0.0009 | I'll replace the ad-hoc bonus terms with a single calibrated "expected completion value" that est... |
| 148 | edit | not_better | 0.9637 | 0.9788 | $0.0009 | The current scoring is dominated by the base best-fit term (-post) with large bonus multipliers. ... |
| 149 | edit | not_better | 0.9626 | 0.9788 | $0.0009 | I'll add a small "conflict avoidance" term that, among bins with similar post-placement residual,... |
| 150 | edit | not_better | 0.9621 | 0.9788 | $0.0008 | I will remove the noisy "commonness" and pairwise-sum lookahead terms that have been hurting, and... |
| 151 | edit | not_better | 0.9626 | 0.9788 | $0.0008 | I'll strengthen the exact-fill and pairing bonuses while reducing the noisy convolution-based two... |
| 152 | edit | not_better | 0.9626 | 0.9788 | $0.0010 | I'll replace the convolution-based two-item-sum lookahead with a bounded, computed-empirically pa... |
| 153 | edit | not_better | 0.9788 | 0.9788 | $0.0011 | I'll shift from pure best-fit to a "best-fit with occasional worst-fit on empty bins" strategy in... |
| 154 | edit | not_better | 0.9616 | 0.9788 | $0.0008 | I'll replace the current hand-tuned mixture with a cleaner, well-scaled score dominated by best-f... |
| 155 | edit | not_better | 0.9699 | 0.9788 | $0.0008 | I'll replace the best-fit base with a "best-fit plus score-aware completion" rule that strongly r... |
| 156 | edit | not_better | 0.9626 | 0.9788 | $0.0008 | I'll replace the noisy, over-multiplied mixture with a focused best-fit-plus-completion rule: kee... |
| 157 | edit | not_better | 0.9616 | 0.9788 | $0.0008 | I'll replace the over-multiplied mixture with a clean "best-fit with one-item complementary-compl... |
| 158 | edit | not_better | 0.9626 | 0.9788 | $0.0008 | I'll keep the proven best-fit base and single-item completion bonus, but replace the weak pairwis... |
| 159 | edit | not_better | 0.9616 | 0.9788 | $0.0008 | I'll replace the noisy multiplicative mixture with a clean, calibrated score that keeps best-fit ... |
| 160 | edit | not_better | 0.9778 | 0.9788 | $0.0009 | I'll add a small, bounded "empty-bin penalty" that makes best-fit slightly prefer non-empty bins ... |
| 161 | edit | not_better | 0.9616 | 0.9788 | $0.0008 | I'll replace the current noisy over-multiplied score with a clean best-fit base plus a single, we... |
| 162 | edit | not_better | 0.9515 | 0.9788 | $0.0008 | I'll keep the proven best-fit + exact-fill base unchanged, and fix the lookahead term to use a pr... |
| 163 | edit | not_better | 0.9783 | 0.9788 | $0.0010 | I'll replace the fixed-multiplier lookahead with one scaled by the number of remaining items (kno... |
| 164 | edit | not_better | 0.9725 | 0.9788 | $0.0012 | I'll scale the completion bonuses (single-item fill probability, pairing, immediate-completion, a... |
| 165 | edit | not_better | 0.9775 | 0.9788 | $0.0010 | I'll add a "best-fit decreasing"-style tie-break that prefers placing the item into a bin whose r... |
| 166 | edit | not_better | 0.9785 | 0.9788 | $0.0008 | I'll keep the proven best-fit + exact-fill base and the scaled single-item completion bonus, but ... |
| 167 | edit | not_better | 0.9626 | 0.9788 | $0.0011 | I'll replace the empirical histogram lookahead with a fixed, distribution-aware approach: since i... |
| 168 | edit | not_better | 0.9626 | 0.9788 | $0.0009 | I'll replace the noisy multi-term heuristic with a cleaner, better-scaled best-fit plus exact-fil... |
| 169 | edit | not_better | 0.9616 | 0.9788 | $0.0008 | I'll implement a proper "minimize expected bins" criterion based on the well-known result that a ... |
| 170 | edit | not_better | 0.9623 | 0.9788 | $0.0008 | I'll keep the proven best-fit + exact-fill base but replace the noisy lookahead terms with a sing... |
| 171 | edit | not_better | 0.9783 | 0.9788 | $0.0009 | I'll add a "sum-completion over the residual's most likely single partner" reward using the smoot... |
| 172 | edit | not_better | 0.9522 | 0.9788 | $0.0009 | I'll replace the noisy fixed-scale lookahead bonuses with a single principled term: weight each c... |
| 173 | edit | not_better | 0.9776 | 0.9788 | $0.0010 | I'll add a stronger, well-scaled pairing/completion bonus based on the smoothed probability that ... |
| 174 | edit | not_better | 0.9621 | 0.9788 | $0.0008 | I will replace the noisy multi-term lookahead with a clean best-fit-plus-completion rule: keep be... |
| 175 | edit | not_better | 0.9788 | 0.9788 | $0.0009 | I'll replace the noisy empirical-histogram terms with a calibrated expected-waste criterion: keep... |
| 176 | edit | invalid | 0.0000 | 0.9788 | $0.0012 | I'll add a "fallback" preference for nearly-full bins: instead of only rewarding exact single-ite... |
| 177 | edit | not_better | 0.9616 | 0.9788 | $0.0008 | I'll add a Subset-Sum/"nearly empty bin" signal: after the base best-fit and exact-fill terms, ge... |
| 178 | edit | not_better | 0.9783 | 0.9788 | $0.0008 | I'll replace the noisy multi-term lookahead with a cleaner rule: keep best-fit + exact-fill, but ... |
| 179 | edit | not_better | 0.9749 | 0.9788 | $0.0008 | I'll replace the current noisy fixed-scale lookahead terms (pairing bonus, commonness signal, pai... |
| 180 | edit | not_better | 0.9614 | 0.9788 | $0.0008 | Replace the pile of arbitrary fixed-scale bonuses (pairing, commonness, pairwise convolution) wit... |
| 181 | edit | improved | 0.9846 | 0.9846 | $0.0009 | I'll add a "residual availability" signal that is only applied late in the instance: with few ite... |
| 182 | edit | not_better | 0.9817 | 0.9846 | $0.0008 | I'll add a "complementary pairing" signal: reward placing the item into a bin whose current remai... |
| 183 | edit | not_better | 0.9821 | 0.9846 | $0.0009 | I'll strengthen the terminal-phase behavior: as the instance nears its end, the expected-value lo... |
| 184 | edit | not_better | 0.9819 | 0.9846 | $0.0009 | I'll replace the fixed-scale expected-fill term with a dimensionless "fill likelihood ratio": bon... |
| 185 | edit | not_better | 0.9846 | 0.9846 | $0.0008 | I'll add a "difficulty-aware" exact-fill relaxation: when a bin's residual after placement is sma... |
| 186 | edit | not_better | 0.9846 | 0.9846 | $0.0009 | I'll replace the accumulated fixed-scale bonus terms with a single principled expected-value rule... |
| 187 | edit | improved | 0.9878 | 0.9878 | $0.0009 | I'll add a dual-lookahead that also rewards placing the item so the resulting residual is exactly... |
| 188 | edit | not_better | 0.9875 | 0.9878 | $0.0010 | I'll add a complementary-fill term based on *complementary* pairing: for each bin, the score will... |
| 189 | edit | not_better | 0.9826 | 0.9878 | $0.0010 | I'll add a small late-instance "unfillable residual" penalty: as the instance nears its end, subt... |
| 190 | edit | improved | 0.9880 | 0.9880 | $0.0009 | I will make the histogram time-aware by decaying old observations (exponential forgetting), so th... |
| 191 | edit | not_better | 0.8045 | 0.9880 | $0.0011 | Add a term favoring residuals that are "reachable" by the most common small item sizes (so the bi... |
| 192 | edit | gate_rejected | 0.9880 | 0.9880 | $0.0010 | I'll add a tunable "open-bin targeting" bonus: reward placing the item into a bin such that the r... |
| 193 | edit | improved | 0.9883 | 0.9883 | $0.0010 | I will add a "mode-residual" bonus that rewards bins whose residual after placement equals the cu... |
| 194 | edit | not_better | 0.9880 | 0.9883 | $0.0010 | Replace the crude count-based "remaining items" scaling of the pair-closure term with a fraction-... |
| 195 | edit | not_better | 0.9883 | 0.9883 | $0.0011 | I will add a term that prefers bins whose residual after placement is unlikely to be exactly fill... |
| 196 | edit | not_better | 0.9694 | 0.9883 | $0.0010 | I'll replace the ad-hoc fixed bonuses with a principled "expected future cost" calculation: estim... |
| 197 | edit | not_better | 0.9878 | 0.9883 | $0.0011 | I'll add a "small-residual protection" term: when the residual after placement is very small, the... |
| 198 | edit | not_better | 0.9861 | 0.9883 | $0.0010 | I will add a "remaining-capacity minimization at end-game" term: when few items remain, strongly ... |
| 199 | edit | not_better | 0.9878 | 0.9883 | $0.0010 | I'll replace the decaying per-item histogram (which is slow to adapt and noisy) with a simple cum... |
| 200 | edit | improved | 0.9885 | 0.9885 | $0.0011 | I will add an "open-bin spread" penalty: when many bins are already open with small residuals, pr... |
| 201 | edit | not_better | 0.9883 | 0.9885 | $0.0014 | I'll add a "multi-fill" bonus: reward residuals that are (approximately) an integer multiple of t... |
| 202 | edit | not_better | 0.9875 | 0.9885 | $0.0012 | I will add a small tie-breaking "least-loaded-bin-index stability" bonus that prefers keeping the... |
| 203 | edit | not_better | 0.9878 | 0.9885 | $0.0012 | I'll add a "residual-collision" preference: among bins whose post-placement residual is close, pr... |
| 204 | edit | not_better | 0.9875 | 0.9885 | $0.0014 | I'll add a proper expected-cost lookahead using the empirical item-size distribution to estimate,... |
| 205 | edit | not_better | 0.9878 | 0.9885 | $0.0011 | I'll replace the noisy decaying histogram with a stable cumulative empirical distribution (all it... |
| 206 | edit | not_better | 0.8687 | 0.9885 | $0.0012 | Replace the crude "remaining * p_fill" expected-count estimate with one that also accounts for th... |
| 207 | edit | not_better | 0.9680 | 0.9885 | $0.0010 | I'll reduce the over-aggressive exact-fill/closure bonuses (which can hurt by over-committing bin... |
| 208 | edit | not_better | 0.9878 | 0.9885 | $0.0012 | I'll replace the exponentially-decaying histogram with a stable full-history empirical distributi... |
| 209 | edit | not_better | 0.9616 | 0.9885 | $0.0008 | I'll shrink the huge additive exact-fill/closure/pair bonuses toward a pure best-fit-plus-small-f... |
| 210 | edit | not_better | 0.9878 | 0.9885 | $0.0011 | I will replace the noisy decaying histogram with a stable full-history empirical distribution (no... |
| 211 | edit | not_better | 0.9616 | 0.9885 | $0.0008 | Replace the many large additive bonuses with a cleaner best-fit-dominant rule plus a modest, well... |
| 212 | edit | not_better | 0.9836 | 0.9885 | $0.0009 | I'll implement a proper "expected future-bin-cost" pairing by computing, for each candidate resid... |
| 213 | edit | not_better | 0.9878 | 0.9885 | $0.0012 | I will add a "sum-of-two" complementary-match score that, for each bin residual larger than the c... |
| 214 | edit | not_better | 0.9846 | 0.9885 | $0.0008 | I'll replace the noisy decaying histogram (and its derived pair/mode/prob bonuses) with a stable ... |
| 215 | edit | not_better | 0.9848 | 0.9885 | $0.0008 | I'll keep the core best-fit + exact-fill structure but reduce the over-large constant bonuses tha... |
| 216 | edit | not_better | 0.9856 | 0.9885 | $0.0011 | I'll make the exponentially-decaying histogram decay slower (0.9995 instead of 0.999) and, more i... |
| 217 | edit | not_better | 0.9621 | 0.9885 | $0.0008 | I'll replace the fixed big additive bonuses with a small bonus for exact-fill, and add a light-we... |
| 218 | edit | not_better | 0.9883 | 0.9885 | $0.0012 | I'll add a small "complementary sum" bonus: besides exact single-item fill, reward choosing a bin... |
| 219 | edit | not_better | 0.9614 | 0.9885 | $0.0009 | I will replace the exponentially-decaying histogram with a stable adaptive distribution that blen... |
| 220 | edit | not_better | 0.9880 | 0.9885 | $0.0011 | I'll add a pair-closure term that rewards matching the residual to the sum of two common future i... |
| 221 | edit | not_better | 0.9883 | 0.9885 | $0.0012 | I'll add a "recent-gap" term: track, for each bin index, the residual after our own placement, an... |
| 222 | edit | not_better | 0.9875 | 0.9885 | $0.0012 | I will add a post-placement "waste" penalty based on the fraction of the bin that stays empty aft... |
| 223 | edit | not_better | 0.9878 | 0.9885 | $0.0013 | I'll add a light complementary-pair bonus that only rewards a residual matching the sum of two *c... |
| 224 | edit | not_better | 0.9647 | 0.9885 | $0.0011 | I will replace the current decayed-histogram probability model with a fixed, precomputed Weibull-... |
| 225 | edit | not_better | 0.9487 | 0.9885 | $0.0012 | I'll replace the pair-closure convolution term (which is noisy and was never shown to help) with ... |
| 226 | edit | not_better | 0.9885 | 0.9885 | $0.0011 | I'll sharpen the exact-fill/preferred-fit behavior by replacing the huge fixed bonuses with a cle... |
| 227 | edit | not_better | 0.9654 | 0.9885 | $0.0012 | I'll replace the noisy pair-closure convolution (whose weight was enormous and untuned) with a cl... |
| 228 | edit | not_better | 0.9848 | 0.9885 | $0.0010 | I'll tune the enormous, untuned scale constants (pair_weight*4000 and exp_fill*60) by removing th... |
| 229 | edit | not_better | 0.9848 | 0.9885 | $0.0010 | I'll strengthen the dominant best-fit signal and reduce the over-weighted noisy pair-closure term... |
| 230 | edit | not_better | 0.9878 | 0.9885 | $0.0012 | I will add an adaptive "leave-large-bins-open" tie-break: when the best-fit residual is nearly ti... |
| 231 | edit | not_better | 0.7997 | 0.9885 | $0.0012 | I'll add a "least-loaded-open-bin" spreading signal: when no bin can be filled exactly, prefer bi... |
| 232 | edit | not_better | 0.9856 | 0.9885 | $0.0011 | I'll add a short-horizon lookahead that, among bins with similar best-fit residuals, prefers the ... |
| 233 | edit | not_better | 0.9817 | 0.9885 | $0.0010 | I'll remove the massive untuned pair-closure convolution term and replace it with a controlled si... |
| 234 | edit | not_better | 0.9856 | 0.9885 | $0.0011 | I'll recalibrate the two dominant lookahead constants that were left over-scaled from the origina... |
| 235 | edit | not_better | 0.9848 | 0.9885 | $0.0011 | I'll add a dynamic, self-correcting "open-bin cost" signal: track the realized best-fit behavior ... |
| 236 | edit | not_better | 0.9885 | 0.9885 | $0.0011 | I'll add an adaptive "spread vs. consolidate" controller: track the empirical fraction of open bi... |
| 237 | edit | not_better | 0.9858 | 0.9885 | $0.0012 | I'll replace the fragile, over-scaled pair-closure convolution with a robust deterministic comple... |
| 238 | edit | not_better | 0.9666 | 0.9885 | $0.0009 | I'll replace the over-scaled, hand-tuned lookahead bonuses with a cleaner scoring rule: best-fit ... |
| 239 | edit | not_better | 0.9883 | 0.9885 | $0.0015 | I'll replace the brittle single-mode-residual bonus with a smooth, full-distribution desirability... |
| 240 | edit | not_better | 0.9875 | 0.9885 | $0.0013 | Add a bounded complementary-pair bonus: strongly prefer placing the item into an already-open bin... |
| 241 | edit | not_better | 0.9730 | 0.9885 | $0.0010 | I'll simplify and rebalance: keep best-fit dominant, replace the over-scaled pair-closure (4000) ... |
| 242 | edit | not_better | 0.9616 | 0.9885 | $0.0011 | I'll replace the fragile hand-tuned lookahead bonuses with a single principled "expected future s... |
| 243 | edit | not_better | 0.9880 | 0.9885 | $0.0011 | I'll add a self-tuning "perfect-fit rarity" tracker: record how often an arriving item exactly cl... |
| 244 | edit | not_better | 0.9885 | 0.9885 | $0.0011 | I'll replace the current exact-fill constant (10000) with an adaptive, self-calibrating exact-fil... |
| 245 | edit | not_better | 0.9878 | 0.9885 | $0.0012 | I'll add a second-order best-fit tie-breaker: among candidate bins, mildly prefer the one with th... |
| 246 | edit | not_better | 0.9614 | 0.9885 | $0.0008 | I'll simplify the scoring rule to a clean, well-scaled best-fit with an exact-fill bonus and a mo... |
| 247 | edit | not_better | 0.9856 | 0.9885 | $0.0012 | Replace the brittle single-mode-residual bonus with a smooth sum over all item sizes of prob[resi... |
| 248 | edit | not_better | 0.9883 | 0.9885 | $0.0012 | I will make the exact-fill bonus adaptive: track how many bins have been exactly closed so far ve... |
| 249 | edit | not_better | 0.9875 | 0.9885 | $0.0011 | Add a lightweight surrogate for the "best fit decreasing" / Martello-Toth style rule used offline... |
| 250 | edit | not_better | 0.9870 | 0.9885 | $0.0013 | I will add a "complementary pairing to the smallest open residual" rule: among bins, boost the sc... |
| 251 | edit | not_better | 0.9614 | 0.9885 | $0.0009 | I'll replace the noisy exponential-forgetting histogram and over-scaled pair/mode/fragmentation b... |
| 252 | edit | not_better | 0.9878 | 0.9885 | $0.0011 | I'll switch the item-size histogram to non-decaying (the distribution is fixed per instance), whi... |
| 253 | edit | not_better | 0.9878 | 0.9885 | $0.0011 | Remove the exponential forgetting of the item-size histogram (the distribution is fixed per insta... |
| 254 | edit | not_better | 0.9704 | 0.9885 | $0.0009 | I'll strip out the over-scaled pair-convolution, mode-residual, and fragmentation bonuses that ad... |
| 255 | edit | not_better | 0.9858 | 0.9885 | $0.0012 | I'll add a "least loaded among near-best-fit" tie-break: when several bins have similar post-plac... |
| 256 | edit | not_better | 0.9778 | 0.9885 | $0.0008 | I'll replace the current complex scoring with a clean, principled "best-fit with expected-fill-va... |
| 257 | edit | not_better | 0.9868 | 0.9885 | $0.0011 | Add a small hysteresis tie-break for near-equal residuals that prefers bins with the *largest* po... |
| 258 | edit | not_better | 0.9885 | 0.9885 | $0.0011 | I will add a tie-break that prefers the smallest pre-placement capacity among bins with equal pos... |
| 259 | edit | not_better | 0.9848 | 0.9885 | $0.0010 | I'll add a "waste-avoidance" term that penalizes leaving a residual that no single item of the em... |
| 260 | edit | not_better | 0.9878 | 0.9885 | $0.0010 | Replace the empirical histogram lookahead with a hard-coded parametric estimate of the Weibull-li... |
| 261 | edit | not_better | 0.9656 | 0.9885 | $0.0012 | I'll replace the noisy empirical histogram (which converges slowly over 5000 items and gives poor... |
| 262 | edit | not_better | 0.9848 | 0.9885 | $0.0010 | I'll remove the noisy pair-convolution, mode-residual, and fragmentation terms (which add varianc... |
| 263 | edit | not_better | 0.9616 | 0.9885 | $0.0007 | I'll replace the noisy empirical/probabilistic scoring with a clean best-fit rule: strongly prefe... |
| 264 | edit | not_better | 0.9846 | 0.9885 | $0.0011 | I'll simplify by removing the high-variance pair-convolution and fragmentation scaling terms, and... |
| 265 | edit | not_better | 0.9846 | 0.9885 | $0.0012 | I'll change the base best-fit scaling from an amplifying multiplier (1 + 3*frac_small, which can ... |
| 266 | edit | not_better | 0.9817 | 0.9885 | $0.0012 | I'll add a modest "small-residual defense" term that slightly prefers leaving a post-placement re... |
| 267 | edit | not_better | 0.9875 | 0.9885 | $0.0011 | I'll reduce the pair-convolution weight (which previous attempts suggest is noisy) and strengthen... |
| 268 | edit | not_better | 0.9863 | 0.9885 | $0.0012 | I'll switch the base ranking from raw best-fit to a "waste-minimizing" rule that avoids leaving t... |
| 269 | edit | not_better | 0.9616 | 0.9885 | $0.0009 | The current program is essentially a tuned Best-Fit with noisy empirical lookahead terms. I'll re... |
| 270 | edit | not_better | 0.9812 | 0.9885 | $0.0009 | I'll remove the noisy pair-convolution and mode terms and instead make the exact-fill/single-fill... |
| 271 | edit | not_better | 0.9853 | 0.9885 | $0.0010 | I'll refine the lookahead terms: replace the coverage-scaled pair probability with a sharper, bet... |
| 272 | edit | not_better | 0.9812 | 0.9885 | $0.0011 | I'll add an online "best-fit-decreasing emulation": maintain a coarse map of open-bin residual ca... |
| 273 | edit | not_better | 0.9878 | 0.9885 | $0.0013 | I will add a deterministic "residual coverage" tie-breaker based on the empirical distribution: s... |
| 274 | edit | not_better | 0.9699 | 0.9885 | $0.0009 | I'll simplify toward a robust, low-variance rule: make the base a clean best-fit and use a single... |
| 275 | edit | not_better | 0.9848 | 0.9885 | $0.0009 | I'll reintroduce a mild adaptive component: keep the proven best-fit + exact-fill + single-fill l... |
| 276 | edit | not_better | 0.9858 | 0.9885 | $0.0012 | Replace the best-fit base with a scale-invariant "best fit" that measures the residual fraction o... |
| 277 | edit | not_better | 0.9851 | 0.9885 | $0.0014 | I'll add a one-step lookahead that scores each bin by how well the *next* item (estimated from th... |
| 278 | edit | not_better | 0.9678 | 0.9885 | $0.0010 | I'll replace the noisy absolute-value bonuses with a cleaner, better-scaled rule: keep best-fit a... |
| 279 | edit | not_better | 0.9616 | 0.9885 | $0.0009 | Replace the noisy and possibly over-tuned pair/mode/fragmentation bonuses with a single principle... |
| 280 | edit | not_better | 0.9870 | 0.9885 | $0.0009 | I'll replace the noisy pair-convolution and mode/fragmentation bonuses with a principled, well-sc... |
| 281 | edit | not_better | 0.9878 | 0.9885 | $0.0013 | I will add a complementary-pairing term: strongly reward choosing a bin whose remaining capacity,... |
| 282 | edit | not_better | 0.9616 | 0.9885 | $0.0009 | Replace the noisy empirical-distribution bonuses (fragmentation multiplier, single-fill, mode, an... |
| 283 | edit | not_better | 0.9616 | 0.9885 | $0.0007 | I'll simplify away the noisy, over-tuned empirical terms and replace them with a single robust ti... |
| 284 | edit | not_better | 0.9883 | 0.9885 | $0.0012 | I will quantize the item-size distribution into coarse buckets (grouping nearby sizes) to make th... |
| 285 | edit | not_better | 0.4156 | 0.9885 | $0.0008 | I will replace the over-tuned constant-heavy bonuses with a cleaner two-part rule: keep best-fit ... |
| 286 | edit | not_better | 0.9647 | 0.9885 | $0.0010 | I'll add a "waste-penalty" refinement: instead of only rewarding small residuals, penalize openin... |
| 287 | edit | not_better | 0.5959 | 0.9885 | $0.0010 | I will replace the empirical-histogram lookahead terms with a principled harmonic "expected futur... |
| 288 | edit | not_better | 0.9848 | 0.9885 | $0.0010 | I will keep the proven best-fit base and exact-fill/complement bonuses, but replace the noisy dec... |
| 289 | edit | not_better | 0.9656 | 0.9885 | $0.0011 | I will replace the fragile, over-tuned mixture of empirical bonuses with a stable best-fit base p... |
| 290 | edit | not_better | 0.9656 | 0.9885 | $0.0012 | I will replace the noisy decayed-empirical-histogram lookahead terms with a stable fixed-Weibull ... |
| 291 | edit | not_better | 0.9880 | 0.9885 | $0.0012 | I will keep the proven best-fit base and exact-fill bonus but replace the noisy decayed-histogram... |
| 292 | edit | not_better | 0.9885 | 0.9885 | $0.0011 | I will cap the residual-index used for the noisy empirical lookahead to only the relevant range a... |
| 293 | edit | invalid | 0.0000 | 0.9885 | $0.0013 | The empirical histogram is too noisy early on and the many arbitrary coefficients (10k, 300, 400,... |
| 294 | edit | not_better | 0.9873 | 0.9885 | $0.0011 | (no description) |
| 295 | edit | not_better | 0.9307 | 0.9885 | $0.0011 | I will remove the multiplicative fragmentation scaling and noisy decayed-histogram lookahead, rep... |
| 296 | edit | gate_rejected | 0.9888 | 0.9885 | $0.0011 | I will add a small "perfect complement to a likely single future item" adjustment based on the re... |
| 297 | edit | not_better | 0.9853 | 0.9885 | $0.0010 | I'll replace the unstable multiplicative fragmentation scaling and the noisy empirical histogram ... |
| 298 | edit | not_better | 0.9885 | 0.9885 | $0.0012 | I'll strengthen the complementary-pair (two-item closure) signal, which is what actually consolid... |
| 299 | edit | not_better | 0.9878 | 0.9885 | $0.0013 | I will add a scan-based complementary-pair bonus: for residuals that equal the sum of two of the ... |
| 300 | edit | not_better | 0.9465 | 0.9885 | $0.0009 | The current code adds a huge exact-fill bonus (10000) that swamps everything, while the useful be... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,96 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with exact-fill preference, empirical future-fill lookahead
+scaled by the number of items left, complementary pairing, and a
+pair-closure signal, with exponential forgetting of past items."""
 import numpy as np
+
+_state = {
+    "n": 0.0,
+    "hist": np.zeros(101, dtype=np.float64),   # decayed counts of items seen
+}
+
+_DECAY = 0.999
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Rank bins by best-fit, exact fill, and probability of a future fill.
 
     item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
+    bins: numpy int64 array with remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    st = _state
+    st["n"] += 1.0
+    hist = st["hist"]
+    # exponential forgetting so the distribution reflects recent items
+    hist *= _DECAY
+    hist[item] += 1.0
+    total = float(hist.sum())
+
+    n_items = float(len(bins))
+
+    post = bins - item  # residual after placing item here
+
+    # Base: best fit -> prefer the smallest post-placement residual.
+    score = -post.astype(np.float64)
+
+    # Scale best-fit strength with fragmentation: when many open bins have
+    # small residuals, consolidating (best-fit) matters more.
+    mean_item = float((hist * np.arange(101, dtype=np.float64)).sum() / max(total, 1.0))
+    if mean_item < 1.0:
+        mean_item = 40.0
+    small_resid = np.count_nonzero((bins > 0) & (bins < mean_item))
+    frac_small = small_resid / max(len(bins), 1)
+    score *= (1.0 + 3.0 * frac_small)
+
+    # Exact fill: perfect, strongly preferred.
+    score += (post == 0).astype(np.float64) * 10000.0
+
+    # Laplace-smoothed item-size distribution.
+    prob = (hist + 1.0) / (total + 100.0)
+
+    post_idx = post.astype(np.int64)
+    valid = (post_idx >= 1) & (post_idx <= 100)
+    p_fill = np.zeros_like(score)
+    if valid.any():
+        idx = post_idx[valid]
+        p_fill[valid] = prob[idx]
+
+    # Expected number of future exact single-item fills for this residual.
+    remaining = max(n_items - st["n"], 0.0)
+    exp_fill = remaining * p_fill
+
+    score += p_fill * 300.0
+
+    # Reward placing into a bin whose residual before placement == item,
+    # closing the bin exactly.
+    score += (bins == item).astype(np.float64) * 400.0
+
+    score += exp_fill * 60.0
+
+    # Pair-closure lookahead: probability that this residual can be exactly
+    # filled by a *pair* of typical future items (convolution of prob with
+    # itself), which consolidates leftovers that a single item cannot close.
+    pair_prob = np.zeros(101, dtype=np.float64)
+    p = prob[1:101]
+    conv = np.convolve(p, p)
+    pair_prob[1:101] = conv[:100]
+    p_pair = np.zeros_like(score)
+    if valid.any():
+        p_pair[valid] = pair_prob[post_idx[valid]]
+
+    # Scale by estimated number of future item-pairs available.
+    n_pairs = remaining * max(remaining - 1.0, 0.0) * 0.5
+    # Only meaningful while plenty of items remain; shrink near the end.
+    pair_weight = min(n_pairs / max(n_items, 1.0), 5.0)
+    score += p_pair * pair_weight * 4000.0
+
+    # Mode-residual bonus: prefer leaving a residual equal to the most common
+    # recent item size, weighted by how common it is.
+    mode_idx = int(np.argmax(prob[1:101])) + 1
+    p_mode = float(prob[mode_idx])
+    score += (post_idx == mode_idx).astype(np.float64) * p_mode * 800.0
+
+    return score
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (47 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 22 | `st = _state` | -0.9885 | essential: the program fails or turns invalid without it |
| 24 | `hist = st['hist']` | -0.9885 | essential: the program fails or turns invalid without it |
| 28 | `total = float(hist.sum())` | -0.9885 | essential: the program fails or turns invalid without it |
| 30 | `n_items = float(len(bins))` | -0.9885 | essential: the program fails or turns invalid without it |
| 32 | `post = bins - item` | -0.9885 | essential: the program fails or turns invalid without it |
| 32 | `term + bins` | -0.9885 | essential: the program fails or turns invalid without it |
| 35 | `score = -post.astype(np.float64)` | -0.9885 | essential: the program fails or turns invalid without it |
| 39 | `mean_item = float((hist * np.arange(101, dtype=np.float64)).sum() / max(total, 1.0))` | -0.9885 | essential: the program fails or turns invalid without it |
| 42 | `small_resid = np.count_nonzero((bins > 0) & (bins < mean_item))` | -0.9885 | essential: the program fails or turns invalid without it |
| 43 | `frac_small = small_resid / max(len(bins), 1)` | -0.9885 | essential: the program fails or turns invalid without it |
| 50 | `prob = (hist + 1.0) / (total + 100.0)` | -0.9885 | essential: the program fails or turns invalid without it |
| 52 | `post_idx = post.astype(np.int64)` | -0.9885 | essential: the program fails or turns invalid without it |
| 53 | `valid = (post_idx >= 1) & (post_idx <= 100)` | -0.9885 | essential: the program fails or turns invalid without it |
| 54 | `p_fill = np.zeros_like(score)` | -0.9885 | essential: the program fails or turns invalid without it |
| 56 | `idx = post_idx[valid]` | -0.9885 | essential: the program fails or turns invalid without it |
| 60 | `remaining = max(n_items - st['n'], 0.0)` | -0.9885 | essential: the program fails or turns invalid without it |
| 61 | `exp_fill = remaining * p_fill` | -0.9885 | essential: the program fails or turns invalid without it |
| 74 | `pair_prob = np.zeros(101, dtype=np.float64)` | -0.9885 | essential: the program fails or turns invalid without it |
| 75 | `p = prob[1:101]` | -0.9885 | essential: the program fails or turns invalid without it |
| 76 | `conv = np.convolve(p, p)` | -0.9885 | essential: the program fails or turns invalid without it |
| 78 | `p_pair = np.zeros_like(score)` | -0.9885 | essential: the program fails or turns invalid without it |
| 27 | `hist[item] += 1.0` | -0.3156 | matters |
| 55 | `if valid.any(): ...` | -0.2824 | matters |
| 57 | `p_fill[valid] = prob[idx]` | -0.2824 | matters |
| 69 | `score += exp_fill * 60.0` | -0.2807 | matters |
| 47 | `score += (post == 0).astype(np.float64) * 10000.0` | -0.1116 | matters |
| 32 | `term - item` | -0.0495 | matters |
| 77 | `pair_prob[1:101] = conv[:100]` | -0.0037 | matters |
| 79 | `if valid.any(): ...` | -0.0037 | matters |
| 80 | `p_pair[valid] = pair_prob[post_idx[valid]]` | -0.0037 | matters |
| 44 | `term + 1.0` | +0.0012 | no effect alone |
| 23 | `st['n'] += 1.0` | +0.0007 | no effect alone |
| 26 | `hist *= _DECAY` | -0.0007 | no effect alone |
| 63 | `score += p_fill * 300.0` | -0.0002 | no effect alone |
| 44 | `score *= 1.0 + 3.0 * frac_small` | -0.0002 | no effect alone |
| 44 | `term + 3.0 * frac_small` | -0.0002 | no effect alone |
| 67 | `score += (bins == item).astype(np.float64) * 400.0` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 40: `if mean_item < 1.0: ...`
- line 41: `mean_item = 40.0`

Not tested (evaluation limit 40): 8 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9885 | 0.9869 |
| minimal (1 parts removed) | 0.9885 | 0.9869 |

Minimal program:

```python
"""Best fit with exact-fill preference, empirical future-fill lookahead
scaled by the number of items left, complementary pairing, and a
pair-closure signal, with exponential forgetting of past items."""
import numpy as np
_state = {'n': 0.0, 'hist': np.zeros(101, dtype=np.float64)}
_DECAY = 0.999

def priority(item, bins):
    """Rank bins by best-fit, exact fill, and probability of a future fill.

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    st = _state
    st['n'] += 1.0
    hist = st['hist']
    hist *= _DECAY
    hist[item] += 1.0
    total = float(hist.sum())
    n_items = float(len(bins))
    post = bins - item
    score = -post.astype(np.float64)
    mean_item = float((hist * np.arange(101, dtype=np.float64)).sum() / max(total, 1.0))
    small_resid = np.count_nonzero((bins > 0) & (bins < mean_item))
    frac_small = small_resid / max(len(bins), 1)
    score *= 1.0 + 3.0 * frac_small
    score += (post == 0).astype(np.float64) * 10000.0
    prob = (hist + 1.0) / (total + 100.0)
    post_idx = post.astype(np.int64)
    valid = (post_idx >= 1) & (post_idx <= 100)
    p_fill = np.zeros_like(score)
    if valid.any():
        idx = post_idx[valid]
        p_fill[valid] = prob[idx]
    remaining = max(n_items - st['n'], 0.0)
    exp_fill = remaining * p_fill
    score += p_fill * 300.0
    score += (bins == item).astype(np.float64) * 400.0
    score += exp_fill * 60.0
    pair_prob = np.zeros(101, dtype=np.float64)
    p = prob[1:101]
    conv = np.convolve(p, p)
    pair_prob[1:101] = conv[:100]
    p_pair = np.zeros_like(score)
    if valid.any():
        p_pair[valid] = pair_prob[post_idx[valid]]
    n_pairs = remaining * max(remaining - 1.0, 0.0) * 0.5
    pair_weight = min(n_pairs / max(n_items, 1.0), 5.0)
    score += p_pair * pair_weight * 4000.0
    mode_idx = int(np.argmax(prob[1:101])) + 1
    p_mode = float(prob[mode_idx])
    score += (post_idx == mode_idx).astype(np.float64) * p_mode * 800.0
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online_informed --budget 0.35 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 3
python -m autoresearch.loop --report experiments/llm-informed-v1/runs/s3   # rebuild this report
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
