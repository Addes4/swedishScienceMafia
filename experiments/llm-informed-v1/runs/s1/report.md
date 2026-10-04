# Research loop report: bin_packing_online_informed

| | |
|---|---|
| problem | `bin_packing_online_informed` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2650 of a $0.35 hard cap, 300 calls, 868,840 tokens |
| wall time | search 4634 s, baselines 58 s, explain 78 s |
| stopped | max_iters (stopped_early) |
| evaluations | 301 (297 valid), 12 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9836 | 0.9791 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online_informed/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_informed/baselines/funsearch_weibull.py` |
| baseline `fwss` | 0.9992 | 0.9990 | `problems/bin_packing_online_informed/baselines/fwss.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_informed/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9836 | 0.9791 | 1 parts removed |

Audit: public 0.9616 → 0.9836 (+0.0220), hidden 0.9604 → 0.9791 (+0.0187); public − hidden gap of the final program 0.0045.

Against the baselines: the final program's public score is below the best baseline (`fwss`, 0.9992). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a hybrid that reserves empty bins (remaining 100) only for items above... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll implement a "best fit with a reserved empty bin" policy: rank partially filled bins by tight... |
| 3 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Implement a two-phase "average-fit" heuristic: track item sizes to estimate the mean, and for eac... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best fit with a "best fit decreasing-like" scoring that strongly prefers tight fits ... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0039 | Add a data-driven tie-breaker: track the empirical histogram of item sizes seen so far, and give ... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace pure best-fit with a size-class-aware policy: maintain the empirical distribution ... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll implement a "score by waste + lookahead potential" rule: for each bin, compute the leftover ... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Switch from pure best-fit to a hybrid that uses best-fit on partially-filled bins but, when no ti... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | Reward exact fills (leftover 0) far more strongly than mere best fit does: score each bin by a la... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll switch to a "harmonic/interval-based" bin-selection rule that mimics Harmonic-M best-fit: cl... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the pure best-fit with a bounded-lookahead "best fit with a reservation threshold": ... |
| 12 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace pure best-fit with a scoring rule that prefers places leaving a small but nonzero ... |
| 13 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a bounded best-fit with a "reserve-when-small" rule: for items below a threshold, ... |
| 14 | edit | not_better | 0.9616 | 0.9616 | $0.0010 | I will switch to a two-stage policy: use Best-Fit for items above a size threshold, but for small... |
| 15 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll replace the static rule with a myopic one-step-lookahead: since items are drawn i.i.d. from ... |
| 16 | edit | not_better | 0.4549 | 0.9616 | $0.0008 | Implement a myopic expected-waste rule: keep a running histogram of seen item sizes, and for each... |
| 17 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a variant of best-fit that, when the item leaves a modest residua... |
| 18 | edit | not_better | 0.9584 | 0.9616 | $0.0006 | I'll replace pure Best-Fit with a "Best-Fit with a small-bin-size cap": since the lower bound is ... |
| 19 | edit | not_better | 0.9614 | 0.9616 | $0.0006 | I'll combine best-fit with a lookahead that avoids creating residuals smaller than the smallest i... |
| 20 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll implement a proper myopic one-step-lookahead using the empirical item-size distribution: for... |
| 21 | edit | invalid | 0.0000 | 0.9616 | $0.0008 | I will track the number of items already placed in each bin (via module-level state keyed by bin ... |
| 22 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace pure best-fit with a score that balances tightest-fit against keeping the smallest residu... |
| 23 | edit | not_better | 0.9077 | 0.9616 | $0.0005 | Replace best-fit with a "modified best-fit" that caps the target residual: prefer the tightest fi... |
| 24 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll implement a hybrid: start with best-fit, but maintain a running empirical item-size distribu... |
| 25 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | I'll implement a one-step lookahead using a static estimate of the item-size distribution: for ea... |
| 26 | edit | not_better | 0.8816 | 0.9616 | $0.0005 | I'll implement a hybrid rule: use best-fit (tightest residual) but when the best placement leaves... |
| 27 | edit | not_better | 0.8225 | 0.9616 | $0.0005 | Implement a "next-fit-ish" hybrid: run standard best-fit, but track a global "open bin" pointer a... |
| 28 | edit | not_better | 0.9616 | 0.9616 | $0.0016 | Replace best-fit with a stateful rule that builds an empirical item-size distribution and rewards... |
| 29 | edit | not_better | 0.8690 | 0.9616 | $0.0007 | Replace best-fit with a self-correcting "any-fit with slack guard": track the running item-size a... |
| 30 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add a score that lets a "substitute" bin be created about once per half-item: when the incoming i... |
| 31 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace the pure best-fit rule with a "best-fit with capacity-aware index" heuristic: choose the ... |
| 32 | edit | not_better | 0.7090 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "worst-fit-ish among tight bins" rule: score bins by how close ... |
| 33 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a stateful "best-fit with periodic fresh-bin reservation": main... |
| 34 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the pure best-fit with a two-parameter rule: use best-fit residual preference, but nudge ... |
| 35 | edit | not_better | 0.9556 | 0.9616 | $0.0007 | Replace pure best-fit with a lookahead-aware rule: track the empirical item-size distribution, an... |
| 36 | edit | not_better | 0.8675 | 0.9616 | $0.0006 | I'll replace pure best-fit with a hybrid "reserve one open bin" rule: keep best-fit normally, but... |
| 37 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a score that combines best-fit (smallest sufficient residual) with a s... |
| 38 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I will add a stateful tie-break that tracks how often each post-placement residual has historical... |
| 39 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a stateful "sum-of-squares-aware" variant: track the running mean... |
| 40 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a "best fit plus fresh-bin guard" rule: track the count of open (non-f... |
| 41 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "harmonic / subharmonic-aware" rule: track the empirical item-s... |
| 42 | edit | not_better | 0.3961 | 0.9616 | $0.0004 | Best fit is nearly optimal for online packing at this distribution, so I'll test a well-known alt... |
| 43 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a hybrid that uses best-fit for most items but, when an item ca... |
| 44 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Best fit wastes capacity by opening a new bin when any small residual could still absorb the item... |
| 45 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a score that prefers the bin whose residual after placement is cl... |
| 46 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Best-fit alone is essentially unbeatable on this distribution, so I will layer a provably safe re... |
| 47 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll add a stateful "pairing" rule: track all open bins' residuals, and when the arriving item ex... |
| 48 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | Replace pure best-fit with a "reserve awareness" rule based on the empirical size distribution: m... |
| 49 | edit | not_better | 0.9388 | 0.9616 | $0.0006 | I'll replace pure best-fit with a rule that maintains a numpy histogram of past item sizes and, a... |
| 50 | edit | not_better | 0.7133 | 0.9616 | $0.0007 | I'll implement a stateful variant of "best fit with a buffer": because item sizes are drawn conti... |
| 51 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "cap-aware best fit" that maintains the full packing state and,... |
| 52 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "harmonic-aware"/interval best-fit: maintain the full packing state ... |
| 53 | edit | not_better | 0.9522 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "best-fit + late perfect-fill consolidation": track the full pa... |
| 54 | edit | not_better | 0.9584 | 0.9616 | $0.0007 | I'll replace pure best-fit with a "best-fit-decreasing-aware" rule using a learned harmonic thres... |
| 55 | edit | improved | 0.9623 | 0.9623 | $0.0008 | I'll switch from pure best-fit to a "best-fit with residual reusability" rule: maintain full pack... |
| 56 | edit | not_better | 0.9616 | 0.9623 | $0.0009 | The current rule gives a bonus to any residual at or above the observed minimum size, which can d... |
| 57 | edit | not_better | 0.9616 | 0.9623 | $0.0010 | I'll replace the min-item-based "reusability" bonus with a data-driven estimate of the smallest i... |
| 58 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I'll switch the scoring to pure best-fit (smallest residual, with exact fills naturally favored) ... |
| 59 | edit | not_better | 0.9616 | 0.9623 | $0.0010 | I'll replace the ad-hoc reusability bonus with a proper "best-fit plus histogram-based future-fil... |
| 60 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | Add a "sum-aware" tie-break to best fit: maintain the total remaining capacity and use the known ... |
| 61 | edit | not_better | 0.9616 | 0.9623 | $0.0010 | I'll keep best-fit as the primary rule but change the tie-break/perturbation to act only on an ex... |
| 62 | edit | not_better | 0.9616 | 0.9623 | $0.0009 | Best fit is already near-optimal, so I will keep its exact ordering but replace the wasteful "reu... |
| 63 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Pure best-fit is already near-optimal for this distribution, so I'll remove the reusability pertu... |
| 64 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I'll replace the ad-hoc reusability bonus with the exact "best fit" rule, but add a deterministic... |
| 65 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | Replace the ad-hoc min-based reusability bonus with plain best-fit ordering so the residual order... |
| 66 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll replace the ad-hoc reusability bonus with a principled "best-fit with exact-fit bonus only" ... |
| 67 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | Switch from best-fit to a weighted combination of "worst fit" signals that exploit the known mean... |
| 68 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace plain best-fit with a "best-fit-with-exact-completion" rule that also considers the *pre-... |
| 69 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace the heuristic best-fit/perturbation with the classic online rule that is known to be near... |
| 70 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I will replace the ad-hoc reusability perturbation with a principled one-sided variant: keep stri... |
| 71 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I'll replace the pure best-fit heuristic with the classic "Best Fit Decreasing"-style online rule... |
| 72 | edit | not_better | 0.9616 | 0.9623 | $0.0009 | Replace the tie-perturbing heuristics with a near-continuous best-fit that also reserves bins pro... |
| 73 | edit | not_better | 0.9616 | 0.9623 | $0.0010 | Replace the observed-minimum floor with an online-estimated low quantile (≈5th percentile) of ite... |
| 74 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | Replace the residual-based ranking with a proper "best fit decreasing"-flavored rule that combine... |
| 75 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I will replace the ad-hoc residual perturbation with a clean, principled "best fit with exact-fil... |
| 76 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I will replace the best-fit scoring with a "best fit plus least-loaded fallback" rule: rank by sm... |
| 77 | edit | not_better | 0.9616 | 0.9623 | $0.0010 | I'll implement the classic online **Harmonic/Sum-of-Squares-aware best fit** but with a key insig... |
| 78 | edit | improved | 0.9637 | 0.9637 | $0.0008 | I'll switch from the pure best-fit family to a randomized/quantile-aware best-fit hybrid: rank by... |
| 79 | edit | not_better | 0.9637 | 0.9637 | $0.0008 | I'll replace the ad-hoc reusability bonus with a proper "best fit decreasing"-flavored two-factor... |
| 80 | edit | not_better | 0.9637 | 0.9637 | $0.0009 | I'll add online lookahead-aware scoring: track the observed mean/quantile of item sizes and, inst... |
| 81 | edit | not_better | 0.9637 | 0.9637 | $0.0008 | I'll replace the ad-hoc residual bonuses with a principled "best fit plus sum-of-squares" hybrid:... |
| 82 | edit | not_better | 0.9633 | 0.9637 | $0.0009 | I'll add a "buddy/slack-awareness" term: since best-fit is strong but strands waste, I'll bias de... |
| 83 | edit | not_better | 0.9616 | 0.9637 | $0.0008 | Conditional best-fit: when the tightest fitting residual is small (≤ empirical q10) use pure tigh... |
| 84 | edit | not_better | 0.9623 | 0.9637 | $0.0009 | (no description) |
| 85 | edit | not_better | 0.9616 | 0.9637 | $0.0009 | I'll add a proper "Harmonic-style" class-based ranking: bucket the post-placement residual into s... |
| 86 | edit | invalid | 0.0000 | 0.9637 | $0.0008 | I'll replace the ad-hoc bonuses with a "match-and-seal" rule based on the observed item distribut... |
| 87 | edit | not_better | 0.9616 | 0.9637 | $0.0008 | I'll implement a principled "best fit with a residual-viability tie-break" based on the empirical... |
| 88 | edit | not_better | 0.8285 | 0.9637 | $0.0009 | I'll implement a proper size-class (Harmonic/Sum-of-Squares style) first-fit rule: map each item ... |
| 89 | edit | not_better | 0.9616 | 0.9637 | $0.0008 | I'll replace the residual bonuses with a principled best-fit that, among placements leaving a sma... |
| 90 | edit | not_better | 0.9616 | 0.9637 | $0.0005 | I'll switch to a pure best-fit rule (put the item in the bin with the smallest resulting residual... |
| 91 | edit | not_better | 0.9612 | 0.9637 | $0.0008 | I'll augment pure best-fit (which alone scores ~0.9616) with a "perfect-fit-lookahead" bonus: str... |
| 92 | edit | not_better | 0.9616 | 0.9637 | $0.0008 | I'll keep pure best-fit as the primary rule but add a targeted "avoid perfect bins whose residual... |
| 93 | edit | not_better | 0.9616 | 0.9637 | $0.0008 | I'll implement the well-known "best fit decreasing-like" insight for the online case: pure best-f... |
| 94 | edit | not_better | 0.9616 | 0.9637 | $0.0007 | I'll replace the ad-hoc bonuses with a "viability"-based best-fit that explicitly models which re... |
| 95 | edit | not_better | 0.9616 | 0.9637 | $0.0007 | I'll switch from best-fit-style scoring to a classic "worst-fit-within-threshold" hybrid: put the... |
| 96 | edit | not_better | 0.9616 | 0.9637 | $0.0007 | I'll add a "residual that matches the current item size" avoidance bonus to best-fit: if the best... |
| 97 | edit | not_better | 0.9586 | 0.9637 | $0.0008 | I'll adjust the residual-viability bonus to be based on the empirical probability mass of the exa... |
| 98 | edit | not_better | 0.9616 | 0.9637 | $0.0007 | I'll replace the heuristic bonuses with a "best fit among bins that leave a viable residual" rule... |
| 99 | edit | not_better | 0.9616 | 0.9637 | $0.0007 | I'll switch the ranking from "best fit" to a score that estimates future fillability using the em... |
| 100 | edit | not_better | 0.9628 | 0.9637 | $0.0008 | Replace the quantile-based ad-hoc bonuses with a principled "expected future usefulness" score: f... |
| 101 | edit | improved | 0.9663 | 0.9663 | $0.0008 | I'll replace the current best-fit-plus-bonuses with a "Worst Fit Decreasing"-style strategy that ... |
| 102 | edit | not_better | 0.9642 | 0.9663 | $0.0008 | I'll keep the current rule but make the "usable residual" threshold adaptive in a smarter way: in... |
| 103 | edit | gate_rejected | 0.9668 | 0.9663 | $0.0008 | I'll make the bin-choice rule follow the empirically-derived "best viable residual" more robustly... |
| 104 | edit | not_better | 0.9654 | 0.9663 | $0.0008 | I'll replace the ad-hoc bonuses with a "best fit with adaptive residual-viability threshold" wher... |
| 105 | edit | not_better | 0.9051 | 0.9663 | $0.0013 | I'll replace the flat q10 usability cliff with a smooth, graded viability bonus keyed to the empi... |
| 106 | edit | not_better | 0.8211 | 0.9663 | $0.0011 | I'll replace the additive bonus scheme with an explicit lexicographic ordering: strongly prefer e... |
| 107 | edit | not_better | 0.9626 | 0.9663 | $0.0008 | I'll replace the hard-cliff q10 bonus with a smooth "best-fit plus viability" score that interpol... |
| 108 | edit | not_better | 0.9619 | 0.9663 | $0.0008 | Add a light "clingy-bin" tie-breaker: among bins whose post-placement residual stays above the em... |
| 109 | edit | not_better | 0.8969 | 0.9663 | $0.0008 | I'll switch from the q10-cliff bonus to a classic "best fit with a small reserve" rule: identify ... |
| 110 | edit | not_better | 0.9635 | 0.9663 | $0.0008 | Replace the binary q10 usability cliff with a smooth, graded bonus that rewards leaving a residua... |
| 111 | edit | not_better | 0.9645 | 0.9663 | $0.0007 | I'll replace the ad-hoc static bonuses with a principled ratio-based score: prefer bins whose pos... |
| 112 | edit | not_better | 0.9647 | 0.9663 | $0.0008 | I'll replace the heuristic scoring with a "best fit minimizing the resulting residual, but only a... |
| 113 | edit | not_better | 0.9628 | 0.9663 | $0.0008 | I'll add a lightweight "harmonic/ROUND-ish" refinement: keep the current best-fit-with-q10-viabil... |
| 114 | edit | not_better | 0.9647 | 0.9663 | $0.0007 | I'll switch the core rule from "prefer best fit among viable residuals" to a proper "best fit wit... |
| 115 | edit | not_better | 0.9626 | 0.9663 | $0.0007 | I'll replace the current q10-viability heuristic with a score that directly minimizes expected wa... |
| 116 | edit | not_better | 0.9612 | 0.9663 | $0.0008 | I'll replace the ad-hoc heuristic with a proper "best fit decreasing on the fly" rule that keeps ... |
| 117 | edit | not_better | 0.9612 | 0.9663 | $0.0007 | I'll replace the heuristic scoring with a classic offline-style rule adapted online: cap the item... |
| 118 | edit | not_better | 0.9616 | 0.9663 | $0.0009 | Replace the hand-tuned threshold heuristic with a proven online rule: a version of "Sum of Square... |
| 119 | edit | not_better | 0.9612 | 0.9663 | $0.0007 | The current rule never uses the full residual information properly: best-fit alone strands many p... |
| 120 | edit | not_better | 0.9663 | 0.9663 | $0.0007 | I'll replace the ad-hoc threshold heuristic with a principled "best fit with a reserve" rule: pla... |
| 121 | edit | not_better | 0.9645 | 0.9663 | $0.0011 | I'll implement the classic "Harmonic" online bin packing rule, which is a proven improvement over... |
| 122 | edit | improved | 0.9668 | 0.9668 | $0.0009 | I'll replace the static q10 viability bonus with an adaptive reserve that targets the most-loaded... |
| 123 | edit | not_better | 0.9616 | 0.9668 | $0.0011 | I'll replace the flat q10-viability bonus (which is coarse and dominates the score) with a smooth... |
| 124 | edit | not_better | 0.9628 | 0.9668 | $0.0009 | I'll refine the residual-desirability score into a smoother, better-normalized combination: keep ... |
| 125 | edit | not_better | 0.9467 | 0.9668 | $0.0008 | I'll replace the fixed heuristic constants with a cleaner, stronger rule: pure best-fit over the ... |
| 126 | edit | not_better | 0.9586 | 0.9668 | $0.0007 | I'll try a classic yet strong approach: score each bin by a "best-fit-decreasing-like" criterion,... |
| 127 | edit | not_better | 0.9575 | 0.9668 | $0.0009 | I'll switch from the ad-hoc scored heuristic to a principled "least-loaded viable fit" rule groun... |
| 128 | edit | not_better | 0.8221 | 0.9668 | $0.0007 | I'll replace the heuristic score with the classic "best fit with a reserve threshold" where bins ... |
| 129 | edit | not_better | 0.9633 | 0.9668 | $0.0008 | I'll add a learned "impossible residual" penalty: track residuals that were left open but never f... |
| 130 | edit | not_better | 0.9600 | 0.9668 | $0.0009 | I'll replace the q10-viability + exact-fill heuristics with a principled "fixture" score: for eac... |
| 131 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the branchy heuristic with a single clean, well-scaled score: a best-fit core plus a... |
| 132 | edit | not_better | 0.9577 | 0.9668 | $0.0008 | I'll replace the heuristic with a principled "best-fit with a distribution-aware tie-break on sma... |
| 133 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the heuristic scoring with a principled "best-fit with distribution-aware expected-f... |
| 134 | edit | not_better | 0.9619 | 0.9668 | $0.0009 | I'll add a learned "waste" penalty derived from the residual-value statistics the packer itself o... |
| 135 | edit | not_better | 0.9640 | 0.9668 | $0.0008 | I'll drop the blunt "usable" flat bonus and the q10 loop, and instead use a smooth, normalized be... |
| 136 | edit | not_better | 0.8221 | 0.9668 | $0.0009 | I will replace the ad-hoc q10/exact-fill blending with a classic "best-fit-decreasing-aware" scor... |
| 137 | edit | not_better | 0.9656 | 0.9668 | $0.0009 | I'll replace the blunt +40 flat "usable" bonus (residual ≥ q10) with a smooth, probability-weight... |
| 138 | edit | not_better | 0.9656 | 0.9668 | $0.0008 | I'll generalize the binary q10 "usable" jump into a smooth, distribution-aware viability bonus: r... |
| 139 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll sharpen the fitted distribution estimate by switching from a raw histogram to a Laplace-smoo... |
| 140 | edit | not_better | 0.9538 | 0.9668 | $0.0009 | I'll replace the score's flat bonuses with a distribution-aware "expected future fit" term comput... |
| 141 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll replace the ad-hoc bonuses with a "best-fit with remaining-item-awareness" rule: prefer the ... |
| 142 | edit | not_better | 0.8221 | 0.9668 | $0.0008 | I'll switch from the ad-hoc flat bonuses to a principled leftover-value estimate: score each bin ... |
| 143 | edit | not_better | 0.9626 | 0.9668 | $0.0008 | I'll replace the ad-hoc bonuses with a principled "best-fit with a strong exact-drop bonus": keep... |
| 144 | edit | not_better | 0.9470 | 0.9668 | $0.0008 | I'll keep the successful best-fit core but replace the ad-hoc bonus with a direct "will a future ... |
| 145 | edit | not_better | 0.9483 | 0.9668 | $0.0008 | Replace the ad-hoc flat bonuses with a principled Hamiltonian/energy view: score each bin by the ... |
| 146 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | Replace the hard-coded q10 loop and flat bonuses with a smooth concave fill-value term: score = b... |
| 147 | edit | not_better | 0.9623 | 0.9668 | $0.0008 | I'll replace the ad-hoc bonus with a proper "best-fit-decreasing-like" rule that uses the known i... |
| 148 | edit | not_better | 0.9666 | 0.9668 | $0.0009 | I'll add a "waste-avoidance" tie-breaker: keep the best-fit core, but scale the exact-fill and vi... |
| 149 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll keep pure best-fit as the dominant term (score = -residual) but add only a tiny, well-scaled... |
| 150 | edit | not_better | 0.9647 | 0.9668 | $0.0009 | I'll switch the core rule from best-fit to a "worst-fit within the viable set" strategy: among bi... |
| 151 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the ad-hoc scoring with a clean best-fit rule that uses the exact-residual-match histogra... |
| 152 | edit | not_better | 0.9458 | 0.9668 | $0.0009 | I'll replace the hand-tuned bonuses with a principled score that keeps the best-fit core but expl... |
| 153 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll strip the rule down to pure best-fit (score = -residual, i.e. smallest resulting residual wi... |
| 154 | edit | not_better | 0.9635 | 0.9668 | $0.0008 | Replace the hand-tuned additive bonuses with a score based on the empirical distribution of the *... |
| 155 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll replace the ad-hoc bonuses with a single principled score based on the expected future value... |
| 156 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | The current rule is essentially best-fit with noisy bonuses; I will replace it with a cleaner, mo... |
| 157 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll replace the noisy additive bonuses with a principled "best-fit with a small de-fragmentation... |
| 158 | edit | not_better | 0.9659 | 0.9668 | $0.0008 | I'll replace the ad-hoc bonuses with a "least-loaded-that-still-fits-most-often" idea: keep best-... |
| 159 | edit | not_better | 0.9623 | 0.9668 | $0.0008 | I'll replace best-fit with a lookahead rule based on the empirical item-size distribution: score ... |
| 160 | edit | not_better | 0.9631 | 0.9668 | $0.0007 | I'll test the classic "best fit decreasing"-style insight adapted to online: prefer the bin whose... |
| 161 | edit | not_better | 0.7735 | 0.9668 | $0.0007 | I'll switch from best-fit to a clean "worst-fit among viable bins" rule: since the item distribut... |
| 162 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I will switch from the ad-hoc additive bonuses to a classic "best-fit" but with a strong de-fragm... |
| 163 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | Replace the ad-hoc additive bonuses with a single expected-fill score: for each candidate residua... |
| 164 | edit | not_better | 0.9616 | 0.9668 | $0.0010 | I'll replace the ad-hoc bonuses with a monotone "best-fit plus sum-of-squares consolidation" rule... |
| 165 | edit | not_better | 0.9623 | 0.9668 | $0.0007 | Replace the ad-hoc heuristic with a principled residual-viability rule: keep the best-fit core (s... |
| 166 | edit | not_better | 0.8970 | 0.9668 | $0.0010 | Replace the ad-hoc constant bonuses with a time-aware best-fit rule: keep score = -residual as th... |
| 167 | edit | improved | 0.9713 | 0.9713 | $0.0009 | I'll switch to a "competitive best-fit with future-fill viability" rule: keep score=-residual as ... |
| 168 | edit | not_better | 0.9647 | 0.9713 | $0.0008 | I will replace the hard-coded additive bonuses with a cleaner, distribution-aware "best-fit with ... |
| 169 | edit | not_better | 0.9701 | 0.9713 | $0.0010 | I'll make the tiny-residual penalty and exact-fill bonus scale with how many items remain (early ... |
| 170 | edit | not_better | 0.9172 | 0.9713 | $0.0010 | Replace hard-coded constants with adaptive, remaining-count-scaled weights: keep score=-residual,... |
| 171 | edit | not_better | 0.9616 | 0.9713 | $0.0006 | Replace the ad-hoc heuristic with a principled dynamic-programming-style rule: since best-fit (sc... |
| 172 | edit | not_better | 0.9628 | 0.9713 | $0.0008 | Replace the ad-hoc bonuses with a distribution-aware "best-fit plus exact-fit-probability" rule t... |
| 173 | edit | not_better | 0.9659 | 0.9713 | $0.0009 | I will tighten the two key weights: reduce the flexibility bonus from 8.0 to 4.0 (it was rewardin... |
| 174 | edit | not_better | 0.9711 | 0.9713 | $0.0009 | I will make the exact-fill reward focus on the common small-to-mid residuals by using the empiric... |
| 175 | edit | not_better | 0.9706 | 0.9713 | $0.0009 | I will change the too-small penalty from a fixed 35 to a value proportional to the empirical prob... |
| 176 | edit | not_better | 0.9616 | 0.9713 | $0.0007 | I will simplify the rule to a pure best-fit with a small, empirically-scaled "perfect-seal" bonus... |
| 177 | edit | not_better | 0.9654 | 0.9713 | $0.0009 | I will replace the noisy hand-tuned bonuses with a cleaner, more principled rule: score = -residu... |
| 178 | edit | not_better | 0.9663 | 0.9713 | $0.0008 | I will make the exact-fill and perfect-seal rewards depend on the empirical probability of future... |
| 179 | edit | improved | 0.9723 | 0.9723 | $0.0010 | I will add a "future-sum" scoring term: instead of only ranking by the current residual, also rew... |
| 180 | edit | not_better | 0.9670 | 0.9723 | $0.0010 | I will drop the mean-multiple waste term (which competes with the best-fit core and adds noise) a... |
| 181 | edit | not_better | 0.9661 | 0.9723 | $0.0010 | The mean-multiple waste term was the only recent change that helped, so I will strengthen it (0.1... |
| 182 | edit | gate_rejected | 0.9723 | 0.9723 | $0.0016 | The mean-multiple waste term was the only recent change that helped, but its round-based formula ... |
| 183 | edit | not_better | 0.9711 | 0.9723 | $0.0011 | The mean-multiple waste term was the only recent change that helped, so I will keep it but make i... |
| 184 | edit | not_better | 0.9616 | 0.9723 | $0.0008 | I will replace the noisy per-residual bonuses with a focused rule: keep the best-fit core, add a ... |
| 185 | edit | not_better | 0.9633 | 0.9723 | $0.0009 | I'll replace the noisy median/fill-mass/fit-mass bonuses with a single principled "waste-aware be... |
| 186 | edit | not_better | 0.9723 | 0.9723 | $0.0011 | I will add an "endgame fill-value" term: estimate the expected number of items still to come from... |
| 187 | edit | not_better | 0.9097 | 0.9723 | $0.0010 | I'll add a "sub-mean waste" penalty that is much stronger than the existing round-based mean-mult... |
| 188 | edit | not_better | 0.9614 | 0.9723 | $0.0008 | I'll simplify by removing the noisy statistical bonus terms (median, fill_mass, fit_mass) which a... |
| 189 | edit | improved | 0.9730 | 0.9730 | $0.0011 | I will add a tie-breaking preference among near-best-fit bins: keep the best-fit core and perfect... |
| 190 | edit | not_better | 0.9730 | 0.9730 | $0.0011 | Add a small bonus for residuals that are close to the running mean (single item nearly seals the ... |
| 191 | edit | improved | 0.9735 | 0.9735 | $0.0011 | I'll make the best-fit core slightly asymmetric: reward residuals just above the running mean alm... |
| 192 | edit | not_better | 0.9621 | 0.9735 | $0.0010 | I'll replace the fragile histogram/median machinery with a cheap, self-normalizing signal: track ... |
| 193 | edit | not_better | 0.9735 | 0.9735 | $0.0012 | I'll add a mild "exact fill counter" tie-break that rewards residuals whose value has historicall... |
| 194 | edit | not_better | 0.9689 | 0.9735 | $0.0012 | I will add an "open-bin preference": when the current best-fit residual is large (i.e., nothing i... |
| 195 | edit | not_better | 0.9647 | 0.9735 | $0.0010 | I'll replace the heavily-tuned noisy statistical terms with a cleaner, more principled rule: keep... |
| 196 | edit | not_better | 0.9619 | 0.9735 | $0.0010 | I'll replace the noisy statistical bonus terms with a cleaner and more principled best-fit plus "... |
| 197 | edit | not_better | 0.9656 | 0.9735 | $0.0009 | I'll strip the fragile histogram/median/mean-multiple tuning and replace it with a cleaner, well-... |
| 198 | edit | not_better | 0.9616 | 0.9735 | $0.0008 | I will keep the proven best-fit + perfect-seal core but replace the noisy histogram/median/mean-m... |
| 199 | edit | gate_rejected | 0.9735 | 0.9735 | $0.0012 | I will add a mild "gap-packing" bonus that rewards residuals which are close to an integer multip... |
| 200 | edit | not_better | 0.9616 | 0.9735 | $0.0009 | I'll replace the noisy histogram/median/mean-multiple tuning with a cleaner rule that keeps the p... |
| 201 | edit | not_better | 0.9735 | 0.9735 | $0.0011 | I'll strengthen the perfect-seal logic: instead of only rewarding residual==0, reward bins whose ... |
| 202 | edit | not_better | 0.9735 | 0.9735 | $0.0012 | I'll strengthen consolidation by adding a bonus that targets residuals which, when the current it... |
| 203 | edit | not_better | 0.9614 | 0.9735 | $0.0011 | I'll replace the noisy hand-tuned statistical bonuses with a principled "expectation-of-future-wa... |
| 204 | edit | not_better | 0.9687 | 0.9735 | $0.0012 | I'll add a powerful consolidation signal: strongly prefer the bin whose residual exactly matches ... |
| 205 | edit | not_better | 0.9647 | 0.9735 | $0.0009 | I'll replace the fragile hand-tuned statistical bonuses with a robust, principled "best-fit with ... |
| 206 | edit | not_better | 0.9735 | 0.9735 | $0.0012 | I will add a light "seal-pairing" term that rewards the bin whose residual after placing the item... |
| 207 | edit | not_better | 0.9701 | 0.9735 | $0.0012 | I will strengthen the perfect-seal reward by making it grow sharply for residuals that are small ... |
| 208 | edit | not_better | 0.9609 | 0.9735 | $0.0011 | I'll replace the flat best-fit core (score = -residual) with a saturating best-fit signal: compre... |
| 209 | edit | not_better | 0.9663 | 0.9735 | $0.0009 | I'll replace the many overlapping, noisy statistical bonuses with a single principled term: expec... |
| 210 | edit | not_better | 0.9647 | 0.9735 | $0.0008 | Simplify and strengthen the core: use pure best-fit (score = -residual) plus a perfect-seal bonus... |
| 211 | edit | not_better | 0.9666 | 0.9735 | $0.0010 | Replace the hand-tuned scoring with a two-phase rule: keep best-fit as the core, but instead of a... |
| 212 | edit | not_better | 0.9735 | 0.9735 | $0.0012 | I'll make the perfect-seal reward adaptive: when the packing is getting tight (few remaining item... |
| 213 | edit | not_better | 0.9735 | 0.9735 | $0.0011 | I will track the fraction of remaining items and, when the instance is near its end (few items le... |
| 214 | edit | not_better | 0.9616 | 0.9735 | $0.0007 | I'll replace the noisy statistical bonuses with a pure best-fit core plus a large perfect-seal re... |
| 215 | edit | not_better | 0.8955 | 0.9735 | $0.0009 | I'll replace the ad-hoc statistical bonuses with a "best-fit with dominance" rule: use pure best-... |
| 216 | edit | not_better | 0.9631 | 0.9735 | $0.0008 | Replace the noisy histogram/mean-based bonuses with a cleaner "expected future usability" score: ... |
| 217 | edit | not_better | 0.9626 | 0.9735 | $0.0012 | Replace the fragile hand-tuned histogram/median/mean bonuses with a principled "expected residual... |
| 218 | edit | not_better | 0.8950 | 0.9735 | $0.0009 | Replace the flat best-fit core with a "least-fillable residual" tiebreak: among bins whose residu... |
| 219 | edit | invalid | 0.0000 | 0.9735 | $0.0012 | I'll add an "aging" exponential decay on the empirical histogram so the rule reacts to the local ... |
| 220 | edit | not_better | 0.9626 | 0.9735 | $0.0008 | I will make the rule adaptive to horizon: keep the best-fit/perfect-seal core, but late in the in... |
| 221 | edit | not_better | 0.9616 | 0.9735 | $0.0009 | I'll replace the noisy histogram/median/mean bonuses with a cleaner rule that keeps best-fit as t... |
| 222 | edit | not_better | 0.9635 | 0.9735 | $0.0011 | I'll replace the whole rule with a principled "expected future waste" score: for each candidate r... |
| 223 | edit | not_better | 0.9635 | 0.9735 | $0.0009 | I'll keep the proven best-fit/perfect-seal core but add a targeted "small-item compatibility" ter... |
| 224 | edit | not_better | 0.9538 | 0.9735 | $0.0009 | I'll keep the proven best-fit core, but replace the noisy histogram/mean/median bonuses with a si... |
| 225 | edit | not_better | 0.9694 | 0.9735 | $0.0011 | I'll tighten the proven best-fit core by making the perfect-seal bonus strong enough to dominate ... |
| 226 | edit | not_better | 0.9675 | 0.9735 | $0.0012 | I'll module-cache the empirical histogram and compute per-call terms more cheaply, but more impor... |
| 227 | edit | not_better | 0.9663 | 0.9735 | $0.0008 | I'll replace the noisy histogram/median/mean bonus stack with a cleaner, more aggressive variant ... |
| 228 | edit | not_better | 0.9640 | 0.9735 | $0.0009 | I will keep the proven best-fit core intact but replace the noisy empirical-histogram add-ons wit... |
| 229 | edit | not_better | 0.9730 | 0.9735 | $0.0011 | I'll keep the proven rule but stabilize the noisy per-call terms: instead of recomputing the medi... |
| 230 | edit | not_better | 0.9524 | 0.9735 | $0.0011 | I'll keep the proven best-fit/perfect-seal core but replace the histogram-based bonuses with a pr... |
| 231 | edit | not_better | 0.9575 | 0.9735 | $0.0009 | (no description) |
| 232 | edit | not_better | 0.9626 | 0.9735 | $0.0008 | I'll replace the noisy bonus stack with a sharper, principled rule: strict best-fit plus a large ... |
| 233 | edit | not_better | 0.9685 | 0.9735 | $0.0011 | I'll add a "waste-aware" term that penalizes residuals which a mean-sized future item cannot usef... |
| 234 | edit | not_better | 0.9616 | 0.9735 | $0.0008 | I'll strip the rule down to a pure, proven best-fit core (score = -residual) with a single light ... |
| 235 | edit | invalid | 0.0000 | 0.9735 | $0.0009 | I'll add a mild tie-breaking preference for the fullest bins among near-equal-residual candidates... |
| 236 | edit | not_better | 0.9678 | 0.9735 | $0.0013 | I will keep the proven best-fit/perfect-seal core but add a bounded, state-decayed bonus that rew... |
| 237 | edit | not_better | 0.9633 | 0.9735 | $0.0009 | I'll keep the proven best-fit/perfect-seal core but tune the two dominant coefficients (perfect-s... |
| 238 | edit | not_better | 0.9663 | 0.9735 | $0.0009 | I'll keep the proven best-fit/perfect-seal core but replace the noisy histogram/median/mean stack... |
| 239 | edit | not_better | 0.9708 | 0.9735 | $0.0009 | I'll replace the complex scoring stack with a cleaner asymptotic best-fit that also considers how... |
| 240 | edit | not_better | 0.9616 | 0.9735 | $0.0009 | I'll simplify to a strong-best-fit core with two well-founded terms: a perfect-seal reward and a ... |
| 241 | edit | not_better | 0.9565 | 0.9735 | $0.0008 | I'll replace the complex scoring stack with a clean linear combination fit by reasoning about the... |
| 242 | edit | not_better | 0.9065 | 0.9735 | $0.0009 | I'll keep the exact proven scoring stack but remove the noisy per-call median loop and the brittl... |
| 243 | edit | not_better | 0.9713 | 0.9735 | $0.0010 | I will keep the proven best-fit/perfect-seal core exactly, but replace the expensive per-call med... |
| 244 | edit | not_better | 0.9626 | 0.9735 | $0.0010 | I'll keep the proven best-fit/perfect-seal core but replace the per-call O(100) median scan and b... |
| 245 | edit | improved | 0.9800 | 0.9800 | $0.0011 | Keep the proven best-fit/perfect-seal core, but replace the brittle near-mean/multiple "waste" te... |
| 246 | edit | not_better | 0.9626 | 0.9800 | $0.0009 | The current scoring is dominated by a hard "too small" penalty using the median, which is noisy a... |
| 247 | edit | not_better | 0.8220 | 0.9800 | $0.0009 | Replace the hard median penalty with a smooth logistic "stranding risk" term based on the running... |
| 248 | edit | not_better | 0.9647 | 0.9800 | $0.0008 | I'll shift the balance toward true best-fit by removing the strong rewards that pull items away f... |
| 249 | edit | not_better | 0.9626 | 0.9800 | $0.0008 | I will keep the proven best-fit core and perfect-seal/fill-mass terms but replace the brittle med... |
| 250 | edit | not_better | 0.9800 | 0.9800 | $0.0010 | I'll keep the proven scoring stack intact but tune the two dominant, well-founded terms: increase... |
| 251 | edit | not_better | 0.9800 | 0.9800 | $0.0011 | I will keep the proven best-fit/perfect-seal/fill-mass core but add a lightweight "perfect-pair" ... |
| 252 | edit | not_better | 0.9645 | 0.9800 | $0.0012 | Keep the proven best-fit/perfect-seal/fill-mass/near-mean structure, but replace the brittle hard... |
| 253 | edit | improved | 0.9831 | 0.9831 | $0.0012 | I'll add a "future-fit" term that scores each candidate bin by how many distinct future item size... |
| 254 | edit | not_better | 0.9112 | 0.9831 | $0.0012 | I'll replace the brittle median "too_small" penalty and the loose near-mean Gaussian with a princ... |
| 255 | edit | not_better | 0.9800 | 0.9831 | $0.0012 | I'll replace the noisy "future-fit" terms with a cleaner, stronger signal: track the exact multis... |
| 256 | edit | not_better | 0.9628 | 0.9831 | $0.0008 | I'll simplify to a clean best-fit core plus a strong exact-fill reward derived from the empirical... |
| 257 | edit | improved | 0.9834 | 0.9834 | $0.0013 | I'll keep the current proven scoring stack but make the best-fit core slightly subservient to the... |
| 258 | edit | not_better | 0.9834 | 0.9834 | $0.0015 | I will add a "future-fit reachability" term: for each candidate residual r, compute the probabili... |
| 259 | edit | improved | 0.9836 | 0.9836 | $0.0014 | I will add a strong "exact-pair-seal" term: reward placing the item so the resulting residual equ... |
| 260 | edit | not_better | 0.9621 | 0.9836 | $0.0012 | Replace the hard median-based "too_small" penalty (and the loose near-mean/mid-range extras) with... |
| 261 | edit | not_better | 0.9761 | 0.9836 | $0.0013 | I will add a "closing" score bonus that gently favors residual 0 via a smooth term and slightly r... |
| 262 | edit | not_better | 0.9362 | 0.9836 | $0.0011 | I will replace the many hand-tuned heuristic bonuses/penalties with a single principled "expected... |
| 263 | edit | not_better | 0.9749 | 0.9836 | $0.0012 | I'll make the pair-seal term active from the very first call and bias it toward exact residual ma... |
| 264 | edit | not_better | 0.9797 | 0.9836 | $0.0014 | I'll strengthen the exact-pair-seal signal by making it a precise indicator: reward a candidate r... |
| 265 | edit | not_better | 0.9766 | 0.9836 | $0.0012 | I'll add a one-step expected-waste lookahead that rewards a candidate residual r based on the emp... |
| 266 | edit | not_better | 0.9119 | 0.9836 | $0.0013 | I will add a "small-residual salvage" avoidance term that penalizes leaving residuals in the rang... |
| 267 | edit | not_better | 0.9836 | 0.9836 | $0.0015 | I will add a complementary "matching residual" affinity term: when two open bins have residuals w... |
| 268 | edit | not_better | 0.9640 | 0.9836 | $0.0010 | I'll add a "waste-avoidance" term that directly targets the real failure mode of best-fit here: l... |
| 269 | edit | not_better | 0.9834 | 0.9836 | $0.0016 | I'll replace the current weak "pair_score" block with a true pairwise-seal signal computed from t... |
| 270 | edit | not_better | 0.9628 | 0.9836 | $0.0009 | I will replace the noisy hand-tuned scoring pile with a clean best-fit core plus a single calibra... |
| 271 | edit | not_better | 0.9630 | 0.9836 | $0.0009 | I'll strip the noisy hand-tuned score pile down to a clean best-fit core plus one principled sign... |
| 272 | edit | not_better | 0.9614 | 0.9836 | $0.0009 | I'll replace the hand-tuned score pile with a principled "small-residual cutoff" rule: pure best-... |
| 273 | edit | not_better | 0.9558 | 0.9836 | $0.0009 | I will replace the noisy hand-tuned score pile with a simple, well-known "best-fit decreasing-lik... |
| 274 | edit | not_better | 0.9100 | 0.9836 | $0.0010 | I'll add a "reserve-for-large-items" term: if the observed distribution has many large items (siz... |
| 275 | edit | not_better | 0.9668 | 0.9836 | $0.0009 | I will replace the hand-tuned scoring pile with a cleaner, better-calibrated rule: keep best-fit ... |
| 276 | edit | not_better | 0.9637 | 0.9836 | $0.0010 | I'll replace the noisy hand-tuned score pile with a principled "residual utilization" rule: keep ... |
| 277 | edit | not_better | 0.9612 | 0.9836 | $0.0009 | I will replace the noisy hand-tuned scoring pile with a much simpler and more robust rule: pure b... |
| 278 | edit | not_better | 0.9621 | 0.9836 | $0.0011 | I'll add a "waste-avoidance" bonus/penalty based on exact-histogram one-step reachability: strong... |
| 279 | edit | not_better | 0.9628 | 0.9836 | $0.0009 | I'll replace the hand-tuned score pile with a cleaner, more principled rule: keep best-fit as the... |
| 280 | edit | not_better | 0.9614 | 0.9836 | $0.0011 | I'll replace the scoring rule with a hybrid that combines best-fit core with a "fill-to-common-si... |
| 281 | edit | not_better | 0.9633 | 0.9836 | $0.0010 | I'll replace the noisy hand-tuned score pile with a well-grounded improvement over best-fit: keep... |
| 282 | edit | not_better | 0.9605 | 0.9836 | $0.0008 | I'll simplify to pure best-fit (score = -residual) but add a single well-calibrated term: a penal... |
| 283 | edit | not_better | 0.9616 | 0.9836 | $0.0010 | I'll shift from residual-shaping to an age-aware scoring rule: keep best-fit as the core, but add... |
| 284 | edit | not_better | 0.9647 | 0.9836 | $0.0008 | Replace the noisy heuristic pile with the classic and well-proven "best fit decreasing-style" rul... |
| 285 | edit | not_better | 0.9656 | 0.9836 | $0.0010 | I will keep the existing scoring rule but add a per-instance adaptive "viability floor": instead ... |
| 286 | edit | not_better | 0.9616 | 0.9836 | $0.0010 | I will replace the complex, noisy heuristic with a cleaner rule that keeps best-fit as the core b... |
| 287 | edit | not_better | 0.9575 | 0.9836 | $0.0011 | Replace the noisy hand-tuned score pile with a principled rule: best-fit core (score = -residual)... |
| 288 | edit | not_better | 0.9614 | 0.9836 | $0.0010 | I will replace the fragile hand-tuned residual-shaping score with a principled "best-fit with fil... |
| 289 | edit | not_better | 0.9836 | 0.9836 | $0.0014 | Since the repeated attempts to beat best-fit with residual-shaping all regress, I'll restore esse... |
| 290 | edit | not_better | 0.9577 | 0.9836 | $0.0009 | Replace the brittle, hand-tuned residual-region constants with an adaptive "perfect-fit attractor... |
| 291 | edit | not_better | 0.9602 | 0.9836 | $0.0009 | I'll make the core best-fit tie-breaking exact: keep score = -residual but replace the noisy bonu... |
| 292 | edit | not_better | 0.9616 | 0.9836 | $0.0015 | Make the best-fit core strictly dominant by multiplying `-residual` by a large constant (1000), s... |
| 293 | edit | not_better | 0.9661 | 0.9836 | $0.0013 | I will keep the proven best-fit core but add a single strong, principled term: a large bonus when... |
| 294 | edit | not_better | 0.9079 | 0.9836 | $0.0013 | I'll add a cheap, principled "waste avoidance" term: penalize residuals that are smaller than the... |
| 295 | edit | not_better | 0.9616 | 0.9836 | $0.0010 | I'll invert the sign of the seal/viability bonuses so they act as tie-breakers *within* the best-... |
| 296 | edit | not_better | 0.9616 | 0.9836 | $0.0009 | I'll stop layering hand-tuned bonuses and instead make the rule a clean best-fit with a single we... |
| 297 | edit | not_better | 0.9616 | 0.9836 | $0.0010 | I'll replace the hand-tuned additive bonus pile with a clean, strictly-dominant best-fit core and... |
| 298 | edit | not_better | 0.9616 | 0.9836 | $0.0008 | I'll replace the noisy additive bonus pile with a clean, principled variant of best-fit: score = ... |
| 299 | edit | not_better | 0.9616 | 0.9836 | $0.0010 | Keep the dominant best-fit core but add a principled, bounded "exact-fit" term: strongly (but not... |
| 300 | edit | not_better | 0.9616 | 0.9836 | $0.0009 | I'll replace the hand-tuned additive pile with a two-stage rule: a dominant best-fit core (score ... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,130 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Competitive best-fit with future-fill viability (histogram reachability).
+
+Pure best fit leaves a few bins with tiny residuals that no future item can
+ever use, and it never rebalances toward bins that can still accept typical
+items.  Since sizes come from a fixed Weibull-like distribution (mean ~40),
+a residual is *useful* only if some future item fits it, and it is *valuable*
+if future items are likely to exactly fill it.
+
+This rule keeps best-fit as the core (score = -residual) but:
+  * penalizes residuals below the empirical median item size,
+  * rewards residuals whose size has high empirical histogram mass,
+  * gives a strong reward for residuals that equal 0 (perfect seal),
+  * rewards residuals reachable by common small future items (one-step
+    reachability via the empirical histogram),
+  * mildly nudges residuals toward sizes that admit typical items.
+"""
 import numpy as np
+
+_n_items = None
+_seen = 0
+_residuals = None
+_hist = None
+_sum = 0
+_cum = None
+
+
+def _init(n):
+    global _n_items, _seen, _residuals, _hist, _sum, _cum
+    _n_items = n
+    _seen = 0
+    _residuals = np.full(n, 100, dtype=np.int64)
+    _hist = np.zeros(101, dtype=np.int64)
+    _sum = 0
+    _cum = np.zeros(101, dtype=np.float64)
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    global _seen, _sum
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    n = len(bins)
+    if _n_items is None or _n_items != n or _residuals is None or len(_residuals) != n:
+        _init(n)
+
+    _seen += 1
+    _hist[item] += 1
+    _sum += item
+
+    residual = bins - item  # >= 0 for shown bins
+
+    total = max(_seen - 1, 1)
+    mean = _sum / _seen
+
+    # Empirical median item size (approx) via cumulative histogram.
+    target = 0.5 * total
+    cum = 0.0
+    median = 1
+    for s in range(1, 101):
+        cum += _hist[s]
+        if cum >= target:
+            median = s
+            break
+
+    # Cumulative histogram (fraction of items <= s).
+    _cum[:] = np.cumsum(_hist) / total
+
+    r = residual.astype(np.float64)
+    idx = np.clip(residual, 0, 100)
+    fill_mass = _hist[idx].astype(np.float64) / total
+    fit_mass = _cum[idx]
+
+    # Best-fit core.
+    score = -r * 1.0
+
+    # Perfect seal: strong reward.
+    score += (residual == 0).astype(np.float64) * 70.0
+
+    # Penalize residuals too small to accept a typical (median) item,
+    # but only if they are not a perfect seal.
+    too_small = ((residual > 0) & (residual < median)).astype(np.float64)
+    score -= too_small * 35.0
+
+    # Reward residuals that a future item can exactly fill.
+    score += fill_mass * 45.0
+
+    # Exact-pair-seal: if the resulting residual matches a size that, together
+    # with some other open bin's residual, sums to a common item size, then one
+    # future item can exactly seal that other bin. Reward such residuals.
+    # residual sizes with high histogram mass are best candidates to be sealed.
+    pair_score = np.zeros_like(r)
+    if _seen > 1:
+        # mass-weighted presence of residuals in a useful range
+        useful = fill_mass * fit_mass
+        pair_score = useful * 15.0
+    score += pair_score
+
+    # Reward residuals reachable by a common small item: for a residual r,
+    # some future item of size s (s <= r) leaves r-s which is itself likely
+    # to be fillable.  Approximate one-step reachability: the probability
+    # that at least one common item size s <= r has positive histogram mass,
+    # weighted by that mass.  Cheap: use cumulative mass of small items.
+    # A residual r is "reachable" if many item sizes can chip at it.
+    reach = np.zeros_like(r)
+    # min(r, mean_item) items are the useful chippers; approximate with a
+    # smooth kernel over small item sizes.
+    small_mass = _hist[1:].astype(np.float64)  # skip 0
+    # weight each residual by total mass of items <= r (already fit_mass);
+    # additionally reward residuals in the mid range where chipping is safe.
+    mid_lo = 20.0
+    mid_hi = 70.0
+    in_mid = ((residual >= mid_lo) & (residual <= mid_hi)).astype(np.float64)
+    score += in_mid * 3.0
+
+    # Reward residuals that admit at least some future item (flexibility).
+    score += fit_mass * 8.0
+
+    # Nudge residuals toward the running mean: a single typical future item
+    # nearly seals such a bin, so prefer it.  Use a smooth Gaussian-like
+    # window rather than brittle nearest-multiple bookkeeping.
+    if mean > 0:
+        near_mean = np.abs(r - mean)
+        score += np.exp(-(near_mean / (0.5 * mean + 1.0)) ** 2) * 4.0
+
+        # Mild monotone preference for residuals that can still hold typical
+        # items, avoiding stranding of mid-sized leftovers.
+        score += (r >= median).astype(np.float64) * 2.0
+
+    return score
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (46 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 39 | `global _seen, _sum` | -0.9836 | essential: the program fails or turns invalid without it |
| 41 | `n = len(bins)` | -0.9836 | essential: the program fails or turns invalid without it |
| 42 | `if _n_items is None or _n_items != n or _residuals is None or (len(_residuals) != n): ...` | -0.9836 | essential: the program fails or turns invalid without it |
| 43 | `_init(n)` | -0.9836 | essential: the program fails or turns invalid without it |
| 45 | `_seen += 1` | -0.9836 | essential: the program fails or turns invalid without it |
| 49 | `residual = bins - item` | -0.9836 | essential: the program fails or turns invalid without it |
| 49 | `term + bins` | -0.9836 | essential: the program fails or turns invalid without it |
| 51 | `total = max(_seen - 1, 1)` | -0.9836 | essential: the program fails or turns invalid without it |
| 52 | `mean = _sum / _seen` | -0.9836 | essential: the program fails or turns invalid without it |
| 55 | `target = 0.5 * total` | -0.9836 | essential: the program fails or turns invalid without it |
| 56 | `cum = 0.0` | -0.9836 | essential: the program fails or turns invalid without it |
| 67 | `r = residual.astype(np.float64)` | -0.9836 | essential: the program fails or turns invalid without it |
| 68 | `idx = np.clip(residual, 0, 100)` | -0.9836 | essential: the program fails or turns invalid without it |
| 69 | `fill_mass = _hist[idx].astype(np.float64) / total` | -0.9836 | essential: the program fails or turns invalid without it |
| 70 | `fit_mass = _cum[idx]` | -0.9836 | essential: the program fails or turns invalid without it |
| 73 | `score = -r * 1.0` | -0.9836 | essential: the program fails or turns invalid without it |
| 80 | `too_small = ((residual > 0) & (residual < median)).astype(np.float64)` | -0.9836 | essential: the program fails or turns invalid without it |
| 90 | `pair_score = np.zeros_like(r)` | -0.9836 | essential: the program fails or turns invalid without it |
| 93 | `useful = fill_mass * fit_mass` | -0.9836 | essential: the program fails or turns invalid without it |
| 109 | `mid_lo = 20.0` | -0.9836 | essential: the program fails or turns invalid without it |
| 110 | `mid_hi = 70.0` | -0.9836 | essential: the program fails or turns invalid without it |
| 76 | `score += (residual == 0).astype(np.float64) * 70.0` | -0.0234 | matters |
| 46 | `_hist[item] += 1` | -0.0227 | matters |
| 49 | `term - item` | -0.0224 | matters |
| 58 | `for s in range(1, 101): ...` | -0.0208 | matters |
| 59 | `cum += _hist[s]` | -0.0208 | matters |
| 60 | `if cum >= target: ...` | -0.0208 | matters |
| 61 | `median = s` | -0.0208 | matters |
| 62 | `break` | -0.0208 | matters |
| 81 | `score -= too_small * 35.0` | -0.0206 | matters |
| 65 | `_cum[:] = np.cumsum(_hist) / total` | -0.0144 | matters |
| 47 | `_sum += item` | -0.0063 | matters |
| 84 | `score += fill_mass * 45.0` | -0.0010 | no effect alone |
| 91 | `if _seen > 1: ...` | -0.0002 | no effect alone |
| 94 | `pair_score = useful * 15.0` | -0.0002 | no effect alone |
| 95 | `score += pair_score` | -0.0002 | no effect alone |
| 103 | `reach = np.zeros_like(r)` | +0.0000 | no effect alone |
| 106 | `small_mass = _hist[1:].astype(np.float64)` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 57: `median = 1`

Not tested (evaluation limit 40): 7 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9836 | 0.9791 |
| minimal (1 parts removed) | 0.9836 | 0.9791 |

Minimal program:

```python
"""Competitive best-fit with future-fill viability (histogram reachability).

Pure best fit leaves a few bins with tiny residuals that no future item can
ever use, and it never rebalances toward bins that can still accept typical
items.  Since sizes come from a fixed Weibull-like distribution (mean ~40),
a residual is *useful* only if some future item fits it, and it is *valuable*
if future items are likely to exactly fill it.

This rule keeps best-fit as the core (score = -residual) but:
  * penalizes residuals below the empirical median item size,
  * rewards residuals whose size has high empirical histogram mass,
  * gives a strong reward for residuals that equal 0 (perfect seal),
  * rewards residuals reachable by common small future items (one-step
    reachability via the empirical histogram),
  * mildly nudges residuals toward sizes that admit typical items.
"""
import numpy as np
_n_items = None
_seen = 0
_residuals = None
_hist = None
_sum = 0
_cum = None

def _init(n):
    global _n_items, _seen, _residuals, _hist, _sum, _cum
    _n_items = n
    _seen = 0
    _residuals = np.full(n, 100, dtype=np.int64)
    _hist = np.zeros(101, dtype=np.int64)
    _sum = 0
    _cum = np.zeros(101, dtype=np.float64)

def priority(item, bins):
    global _seen, _sum
    n = len(bins)
    if _n_items is None or _n_items != n or _residuals is None or (len(_residuals) != n):
        _init(n)
    _seen += 1
    _hist[item] += 1
    _sum += item
    residual = bins - item
    total = max(_seen - 1, 1)
    mean = _sum / _seen
    target = 0.5 * total
    cum = 0.0
    for s in range(1, 101):
        cum += _hist[s]
        if cum >= target:
            median = s
            break
    _cum[:] = np.cumsum(_hist) / total
    r = residual.astype(np.float64)
    idx = np.clip(residual, 0, 100)
    fill_mass = _hist[idx].astype(np.float64) / total
    fit_mass = _cum[idx]
    score = -r * 1.0
    score += (residual == 0).astype(np.float64) * 70.0
    too_small = ((residual > 0) & (residual < median)).astype(np.float64)
    score -= too_small * 35.0
    score += fill_mass * 45.0
    pair_score = np.zeros_like(r)
    if _seen > 1:
        useful = fill_mass * fit_mass
        pair_score = useful * 15.0
    score += pair_score
    reach = np.zeros_like(r)
    small_mass = _hist[1:].astype(np.float64)
    mid_lo = 20.0
    mid_hi = 70.0
    in_mid = ((residual >= mid_lo) & (residual <= mid_hi)).astype(np.float64)
    score += in_mid * 3.0
    score += fit_mass * 8.0
    if mean > 0:
        near_mean = np.abs(r - mean)
        score += np.exp(-(near_mean / (0.5 * mean + 1.0)) ** 2) * 4.0
        score += (r >= median).astype(np.float64) * 2.0
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online_informed --budget 0.35 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 1
python -m autoresearch.loop --report experiments/llm-informed-v1/runs/s1   # rebuild this report
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
