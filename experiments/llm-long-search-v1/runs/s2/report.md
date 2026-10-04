# Research loop report: bin_packing_online

| | |
|---|---|
| problem | `bin_packing_online` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.1928 of a $0.75 hard cap, 300 calls, 654,824 tokens |
| wall time | search 1826 s, baselines 45 s, explain 75 s |
| stopped | max_iters (stopped_early) |
| evaluations | 300 (287 valid), 7 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9809 | 0.9776 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online/baselines/funsearch_weibull.py` |
| minimal program (ablation) | 0.9805 | 0.9793 | 3 parts removed |

Audit: public 0.9616 → 0.9809 (+0.0193), hidden 0.9604 → 0.9776 (+0.0172); public − hidden gap of the final program 0.0033.

Against the baselines: the final program's public score is below the best baseline (`funsearch_weibull`, 0.9925). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | I will add a small "almost full bin" preference: bins whose remaining capacity is close to the it... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace the pure best-fit score with a bounded best-fit that also slightly prefers fuller bins ov... |
| 3 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | I'll replace the plain best-fit rule with Best-Fit-Decreasing-style "residual-aware" scoring: pre... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll add a learned-style "residual threshold" heuristic: rank bins primarily by tightest fit, but... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll switch from pure best-fit to a "best fit with almost-full-bin avoidance" hybrid: primary ran... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace best-fit with a residual-threshold "harmonic-like" rule: score bins by preferring th... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace best-fit with a randomized/round-robin perturbation of best-fit is not viable, so instead... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "residual-aware harmonic" rule: bins are scored by preferring t... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add adaptive online statistics (per-instance running mean and count of items) to build a "fi... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the per-item greedy best-fit with a scheme that reserves some near-empty space: among bin... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Pure per-item best-fit ignores the distribution's small-item tail, which best-fit tends to bury i... |
| 12 | edit | not_better | 0.8067 | 0.9616 | $0.0005 | I'll replace pure best-fit with a size-aware "almost-worst-fit for large items" variant: compute ... |
| 13 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll add a light online-capacity-class ("harmonic") twist to best-fit: score each bin by the resu... |
| 14 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a hybrid that tracks the online mean item size and, only for items tha... |
| 15 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the score with a multiplicative normalized fit: score each bin by the resulting residual ... |
| 16 | edit | not_better | 0.9584 | 0.9616 | $0.0006 | Track the smallest item size seen so far, and among bins that fit, prefer those whose resulting r... |
| 17 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll add a small deterministic score jitter derived from the bin's index to break ties among equa... |
| 18 | edit | not_better | 0.9298 | 0.9616 | $0.0004 | Replace pure best-fit with a "reservation"-style rule: define a threshold T (a size class around ... |
| 19 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Best fit leaves a residual (bin capacity after placing the item) that is often just barely too sm... |
| 20 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a "fullest-bin-that-still-fits-but-not-quite" rule: use best fit but, ... |
| 21 | edit | not_better | 0.9593 | 0.9616 | $0.0005 | I'll replace pure best-fit with a First-Fit variant that keeps bins in index order: since bin ind... |
| 22 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I will add a "large-item lookahead" heuristic: track the maximum item size seen so far and, in ad... |
| 23 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a "largest fill fraction" rule: score bins by how fully the arriving i... |
| 24 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a "good-fit with bin-open awareness" rule: score bins by how cl... |
| 25 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "worst-fit for mid-range residuals" hybrid: among bins that fit... |
| 26 | edit | improved | 0.9649 | 0.9649 | $0.0006 | Pure best-fit scores 0.9616, close to the ~0.957-0.99 range of greedy heuristics. A well-known im... |
| 27 | edit | not_better | 0.9647 | 0.9649 | $0.0006 | I will refine the tie-break by replacing the histogram-usefulness term with a "residual-sum minim... |
| 28 | edit | not_better | 0.9616 | 0.9649 | $0.0007 | I will replace the static histogram usefulness tie-break with a dynamic residual-deficit term: tr... |
| 29 | edit | not_better | 0.9647 | 0.9649 | $0.0006 | Replace the fixed 0.5 coefficient and hard tightness term with a normalized best-fit score plus a... |
| 30 | edit | gate_rejected | 0.9652 | 0.9649 | $0.0005 | Replace the ad-hoc histogram bonus with a scale-free "expected future use" tie-break: best-fit's ... |
| 31 | edit | not_better | 0.9616 | 0.9649 | $0.0006 | I will replace the histogram-usefulness tie-break with a global best-fit-decreasing-style adjustm... |
| 32 | edit | not_better | 0.9442 | 0.9649 | $0.0006 | Replace the hard histogram lookup with a smoothed, weighted usefulness term: score near-ties by h... |
| 33 | edit | not_better | 0.9616 | 0.9649 | $0.0006 | I'll strengthen the best-fit tie-break using a smoothed estimate of the probability that a bin's ... |
| 34 | edit | not_better | 0.9616 | 0.9649 | $0.0006 | Replace the histogram tie-break with a two-part rule that is robust online: primary score is pure... |
| 35 | edit | not_better | 0.9616 | 0.9649 | $0.0004 | Replace the bounded best-fit-plus-tiebreak family (which has plateaued and is sensitive on instan... |
| 36 | edit | not_better | 0.9649 | 0.9649 | $0.0006 | I'll replace the histogram-based tie-break with a principled "expected leftover utility" score th... |
| 37 | edit | not_better | 0.9616 | 0.9649 | $0.0006 | I'll replace the ad-hoc histogram tie-break with a mean-based "expected fit" test: rank bins by s... |
| 38 | edit | not_better | 0.9616 | 0.9649 | $0.0006 | Replace best-fit's raw tightness with a scale-free "usefulness of leftover capacity" score based ... |
| 39 | edit | not_better | 0.9616 | 0.9649 | $0.0007 | I'll replace the ad-hoc histogram tie-break with a principled score based on the probability that... |
| 40 | edit | improved | 0.9661 | 0.9661 | $0.0006 | Add a small "hole-size awareness" term to the current best-fit-plus-histogram rule: instead of ju... |
| 41 | edit | not_better | 0.9654 | 0.9661 | $0.0006 | I'll refine the smoothed-histogram tie-break by using a slightly wider/less peaked kernel (offset... |
| 42 | edit | gate_rejected | 0.9668 | 0.9661 | $0.0008 | I'll make the residual-usefulness tie-break adaptive by replacing the fixed weight 0.5 with a sma... |
| 43 | edit | not_better | 0.9661 | 0.9661 | $0.0006 | I'll keep the best-fit primary term but replace the fixed 0.5 usefulness weight with a slightly l... |
| 44 | edit | not_better | 0.9649 | 0.9661 | $0.0006 | The current rule is essentially best-fit with a weak smoothed-histogram bonus, which leaves a lot... |
| 45 | edit | not_better | 0.9563 | 0.9661 | $0.0006 | The current smoothed-histogram tie-break is too weak; I'll replace it with a direct estimate of "... |
| 46 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll replace the smoothed-histogram usefulness bonus with a simpler and stronger scheme: keep bes... |
| 47 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll switch from best-fit (min residual) to a score that blends tightness with a multiplicative "... |
| 48 | edit | not_better | 0.9649 | 0.9661 | $0.0007 | (no description) |
| 49 | edit | not_better | 0.9656 | 0.9661 | $0.0006 | Replace the best-fit primary term with an approximate "worst-fit-improving" rule: prefer the bin ... |
| 50 | edit | not_better | 0.9661 | 0.9661 | $0.0006 | I will replace the additive smoothed-histogram bonus with a proper "expected future fill" estimat... |
| 51 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll keep best-fit as the primary rule (it is near-optimal for this distribution) but sharpen the... |
| 52 | edit | not_better | 0.9654 | 0.9661 | $0.0006 | I'll replace the pure best-fit (min residual) primary term with a hybrid: keep exact-fit as a lar... |
| 53 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll keep the near-optimal best-fit primary term but make the tie-break adaptive and statisticall... |
| 54 | edit | gate_rejected | 0.9663 | 0.9661 | $0.0006 | Introduce a converging, decaying exploration bonus: bias residual 0 with a strong fixed bonus (be... |
| 55 | edit | not_better | 0.9661 | 0.9661 | $0.0006 | I will replace the smoothed-histogram additive tie-break with a "sum-of-future-fit-probabilities"... |
| 56 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll refine the tie-break to prefer residuals that equal a common future item size exactly (so th... |
| 57 | edit | not_better | 0.9654 | 0.9661 | $0.0007 | I will change the primary rule from pure best-fit to a linear combination of best-fit tightness a... |
| 58 | edit | not_better | 0.9616 | 0.9661 | $0.0009 | I'll add a small, properly-scaled exact-match reward (not a large override) plus a bounded "resid... |
| 59 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | I'll replace the additive smoothed-histogram bonus with a "post-placement residual desirability" ... |
| 60 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | The current tie-break coefficient (0.5) seems too large, causing regressions; I will shrink it to... |
| 61 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | I'll replace the weak additive histogram bonus with a proper one-step-lookahead expected-value ti... |
| 62 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | I will replace the histogram tie-break with a simple, well-known strong online rule: best-fit (ti... |
| 63 | edit | not_better | 0.9616 | 0.9661 | $0.0009 | I'll replace the weak additive histogram bonus with a proper residual-specific "expected waste" s... |
| 64 | edit | not_better | 0.9616 | 0.9661 | $0.0005 | I'll replace the weak histogram bonus with an exact-fit-dominant rule: score bins whose post-plac... |
| 65 | edit | not_better | 0.9616 | 0.9661 | $0.0005 | The current smoothed-histogram bonus is too weak and slightly noisy; I'll replace the priority wi... |
| 66 | edit | invalid | 0.0000 | 0.9661 | $0.0008 | Switch from an additive bonus (which perturbs the tightness ordering and caused regressions) to a... |
| 67 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll replace the smoothed-histogram additive bonus with a clean lexicographic best-fit rule: prim... |
| 68 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | I'll replace the current rule with a pure best-fit (tightest residual) primary key, but break res... |
| 69 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | The empirical evidence across many attempts shows that any monotone transform of "smallest residu... |
| 70 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | Replace the smoothed-histogram tie-break with a "worst-fit among near-tight bins" idea is risky, ... |
| 71 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I will keep the smoothed-histogram usefulness bonus but replace the fixed-shape kernel with a dat... |
| 72 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | The additive histogram bonus clearly hurts (every pure best-fit variant scores 0.9616, below the ... |
| 73 | edit | no_code | n/a | 0.9661 | $0.0004 | I'll switch to a proper "best fit decreasing"-style heuristic that is well known to beat plain be... |
| 74 | edit | invalid | 0.0000 | 0.9661 | $0.0005 | I'll replace the fixed kernel with a running histogram of past item sizes and break exact-residua... |
| 75 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll break residual ties using the exact empirical frequency of the residual (probability that a ... |
| 76 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | The key insight: the current rule adds `0.5 * use` to `-residual`, but `use` is bounded (histogra... |
| 77 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | Replace the potentially-dominating histogram bonus with a much smaller, normalized tie-break: kee... |
| 78 | edit | not_better | 0.9661 | 0.9661 | $0.0006 | I'll keep the exact current rule (pure best-fit plus the existing smoothed-histogram usefulness t... |
| 79 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll replace the smoothed-histogram usefulness bonus with a hybrid rule: prefer exact fills, othe... |
| 80 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll replace the histogram-based usefulness term with a "residual-fit" score that favors leaving ... |
| 81 | edit | not_better | 0.9616 | 0.9661 | $0.0005 | I'll drop the histogram/usefulness term entirely and switch to pure best-fit (tightest residual) ... |
| 82 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | Normalize the smoothed histogram bonus into a probability (divide by total count) so its scale st... |
| 83 | edit | not_better | 0.9598 | 0.9661 | $0.0006 | The best-fit key should stay a *tie-breaker* only: I'll make the primary key a coarse "size class... |
| 84 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | Replace the per-step cumulative-count bonus (which drifts in scale and overrides best-fit late) w... |
| 85 | edit | not_better | 0.9607 | 0.9661 | $0.0005 | Replace the histogram-usefulness tie-break with a "least-fit / leave-fragmentation-minimizing" ru... |
| 86 | edit | not_better | 0.9616 | 0.9661 | $0.0005 | Implement a dual-signal rule: strongly prefer exact fits, then use best-fit (smallest residual), ... |
| 87 | edit | not_better | 0.9661 | 0.9661 | $0.0019 | Keep the proven `-residual + 0.5*smoothed_use` formula intact, but add a targeted bonus for bins ... |
| 88 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll add a mild secondary preference that among bins with very similar residuals (near-ties) favo... |
| 89 | edit | not_better | 0.9616 | 0.9661 | $0.0006 | I'll modify the smoothed-usefulness tie-break so that, instead of rewarding a residual that a fut... |
| 90 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | I will replace the heuristic tie-break with a provably strong online rule combining best-fit and ... |
| 91 | edit | not_better | 0.9616 | 0.9661 | $0.0007 | I'll keep the proven best-fit dominant term (`-residual`) but replace the smoothed-usefulness sec... |
| 92 | edit | not_better | 0.9661 | 0.9661 | $0.0006 | Boost the exact-fill preference to be effectively absolute, and add a small bonus for putting the... |
| 93 | edit | improved | 0.9663 | 0.9663 | $0.0008 | Keep the proven `-residual + 0.5*smoothed_use` formula, but make the secondary coefficient adapti... |
| 94 | edit | not_better | 0.9661 | 0.9663 | $0.0008 | The running mean is a poor summary of a Weibull distribution; I'll replace the mean-based reusabi... |
| 95 | edit | gate_rejected | 0.9663 | 0.9663 | $0.0007 | Replace the single-kernel smoothed-usefulness tie-break with a two-term approach: keep best-fit `... |
| 96 | edit | not_better | 0.9616 | 0.9663 | $0.0007 | I'll replace the hand-tuned single-kernel usefulness with a direct probabilistic estimate of futu... |
| 97 | edit | gate_rejected | 0.9663 | 0.9663 | $0.0008 | I'll keep the proven best-fit dominant term and smoothed-usefulness secondary, but replace the me... |
| 98 | edit | not_better | 0.9616 | 0.9663 | $0.0009 | Replace the single hand-tuned smoothing kernel with a directly computed expected-waste estimate f... |
| 99 | edit | not_better | 0.9647 | 0.9663 | $0.0008 | I'll keep the proven best-fit dominant term and smoothed-usefulness secondary, but add a tiny, sh... |
| 100 | edit | not_better | 0.9663 | 0.9663 | $0.0007 | Replace the mean-based reusability bonus with a tiny bonus rewarding residuals that equal the sum... |
| 101 | edit | not_better | 0.9647 | 0.9663 | $0.0008 | I'll strengthen the smoothed-usefulness term (raise its coefficient to 1.0) and use a sharply pea... |
| 102 | edit | not_better | 0.9616 | 0.9663 | $0.0007 | I'll replace the heuristic smoothed-usefulness bonus with a principled tie-break based on the cla... |
| 103 | edit | not_better | 0.9616 | 0.9663 | $0.0008 | I'll switch the tie-break from a raw residual-frequency bonus to a score that weights each candid... |
| 104 | edit | not_better | 0.9659 | 0.9663 | $0.0007 | Replace the per-call Python loop that rebuilds the smoothed histogram with a cached running-sum a... |
| 105 | edit | invalid | 0.0000 | 0.9663 | $0.0007 | I will replace the mean-based reusability bonus with a tie-break that prefers residuals closely m... |
| 106 | edit | not_better | 0.9633 | 0.9663 | $0.0008 | I'll strengthen the best-fit dominance by making the primary term a steeper function of residual ... |
| 107 | edit | not_better | 0.9616 | 0.9663 | $0.0007 | I'll replace the smoothed-histogram tie-break and mean-based reuse bonus with a leave-the-leftove... |
| 108 | edit | not_better | 0.9616 | 0.9663 | $0.0005 | I'll simplify to pure best-fit (smallest residual), which is the strongest known online rule for ... |
| 109 | edit | not_better | 0.9616 | 0.9663 | $0.0005 | I'll replace the current heuristic bonuses with the classic "best fit" rule combined with a same-... |
| 110 | edit | not_better | 0.9616 | 0.9663 | $0.0006 | I'll try the classic "worst fit"-style complementary approach: instead of pure best-fit, prefer t... |
| 111 | edit | invalid | 0.0000 | 0.9663 | $0.0006 | I will switch the primary rule to pure best-fit (smallest residual, strongly dominant via a large... |
| 112 | edit | not_better | 0.9661 | 0.9663 | $0.0007 | I'll replace the fixed shifted-window smoothing with a proper symmetric Gaussian-smoothed histogr... |
| 113 | edit | not_better | 0.9649 | 0.9663 | $0.0007 | I'll keep the proven structure but replace the hard-coded 5-tap smoothing kernel with a Gaussian-... |
| 114 | edit | not_better | 0.9621 | 0.9663 | $0.0007 | Replace the fixed 5-tap loop with a cached full-length Gaussian-smoothed histogram (convolved onc... |
| 115 | edit | not_better | 0.9647 | 0.9663 | $0.0007 | I'll strengthen the exact-fill signal by looking one step ahead: instead of scoring a bin only by... |
| 116 | edit | not_better | 0.9616 | 0.9663 | $0.0007 | I'll revert to the strongest structure but make best-fit the dominant primary rule with a much sm... |
| 117 | edit | not_better | 0.9616 | 0.9663 | $0.0007 | The key insight from the failed attempts is that any usefulness bonus large enough to override be... |
| 118 | edit | not_better | 0.9616 | 0.9663 | $0.0006 | Replace the smoothed-usefulness tie-break with a principled "expected waste reduction" one-step l... |
| 119 | edit | not_better | 0.9616 | 0.9663 | $0.0006 | I will replace the smoothed-usefulness term with a proper one-step lookahead using the empirical ... |
| 120 | edit | invalid | 0.0000 | 0.9663 | $0.0007 | I'll switch the tie-break to a one-step expected-waste lookahead: keep best-fit dominant, but rep... |
| 121 | edit | improved | 0.9668 | 0.9668 | $0.0007 | I'll revert to the best-scoring structure but make the usefulness tie-break strictly smaller than... |
| 122 | edit | not_better | 0.9668 | 0.9668 | $0.0008 | I'll replace the mean-based reuse Gaussian with a sharper, plateau-tolerant tie-break that reward... |
| 123 | edit | not_better | 0.9654 | 0.9668 | $0.0007 | I'll make the best-fit primary rule strictly dominant with a unit gap, and replace the mean-based... |
| 124 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll enforce best-fit as a strictly dominant primary rule by scaling the residual term with a lar... |
| 125 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the ad-hoc mixed tie-break with a cleaner strictly-dominated structure: best-fit as ... |
| 126 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | The current tie-break adds a reuse bonus and a usefulness term that only act on exact best-fit ti... |
| 127 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll replace the ad-hoc mixed tie-break with a principled bounded best-fit variant: use the resid... |
| 128 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the tie-break with a statistical "expected future waste" score: for each bin residua... |
| 129 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Try a provably strong competitive rule instead of the smoothed best-fit: add a "best fit plus 1/8... |
| 130 | edit | not_better | 0.9616 | 0.9668 | $0.0010 | The current tie-break Gaussian centered on the historical mean item size is ad-hoc. I'll replace ... |
| 131 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | The reuse bonus currently uses the running mean, which is noisy early and doesn't reflect the tru... |
| 132 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll strengthen the exact-match tie-break by making it depend on a decayed, recency-weighted item... |
| 133 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the ad-hoc tie-break terms with a single principled "expected future fit" tie-break: for ... |
| 134 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the noisy running-mean Gaussian reuse bonus with a principled "expected next-fit" ti... |
| 135 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | Replace the hand-tuned reuse/bonus logic with a principled best-fit that, among equal residuals, ... |
| 136 | edit | not_better | 0.9616 | 0.9668 | $0.0010 | I'll replace the ad-hoc reuse bonus with a principled "expected future waste" tie-break based on ... |
| 137 | edit | not_better | 0.9663 | 0.9668 | $0.0007 | I'll add a light "harmonic-like" worst-fit tie-break on top of the existing best-fit dominant rul... |
| 138 | edit | not_better | 0.9668 | 0.9668 | $0.0006 | I'll replace the running-mean Gaussian reuse bonus with a constant small bonus for larger residua... |
| 139 | edit | not_better | 0.9668 | 0.9668 | $0.0006 | Replace the noisy running-mean Gaussian reuse bonus with a principled tie-break based on the empi... |
| 140 | edit | not_better | 0.9649 | 0.9668 | $0.0006 | Replace the noisy Gaussian reuse bonus with a principled score that keeps best-fit strictly domin... |
| 141 | edit | invalid | 0.0000 | 0.9668 | $0.0006 | Replace the exact-residual tie-break with a sub-1.0 "future-fit" score that dominates only exact ... |
| 142 | edit | not_better | 0.9422 | 0.9668 | $0.0006 | I'll replace the ad-hoc bonuses with a clean two-level rule: keep best-fit strictly dominant (sco... |
| 143 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll make the tie-break term adaptive and safe: keep best-fit strictly dominant with score = -res... |
| 144 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll make the tie-break more decisive by keeping best-fit strictly dominant using a large multipl... |
| 145 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the ad-hoc reuse Gaussian with a principled "sum-of-two" packing bonus: among candid... |
| 146 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the smooth histogram-based residual bonus with a strong "least-loaded bin that still fits... |
| 147 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the noisy Gaussian reuse bonus and smoothed-histogram tie-break with a simple, robust bes... |
| 148 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | Keep best-fit strictly dominant but replace the noisy Gaussian reuse bonus with a proper best-fit... |
| 149 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll keep the proven best-fit-dominant rule (score = -residual with an exact-fit bonus) and resto... |
| 150 | edit | not_better | 0.9668 | 0.9668 | $0.0008 | I'll replace the fixed reuse Gaussian with an adaptive term that estimates the empirical residual... |
| 151 | edit | invalid | 0.0000 | 0.9668 | $0.0007 | I'll replace the crude Gaussian reuse bonus with a principled "complementary-fit" tie-break: amon... |
| 152 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | Keep pure best-fit dominance (score = -residual) and replace the Gaussian reuse term with a smoot... |
| 153 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I will replace the noisy Gaussian reuse term with a bin-density-aware tie-break: keep best-fit do... |
| 154 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the noisy Gaussian/mean-based reuse bonus with a scaled histographic "complementary-... |
| 155 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll add a principled "perfect-pack pairing" tie-break: among bins at the best-fit residual, pref... |
| 156 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I will replace the reuse/mean term with a "smallest residual tie-break within equal best-fit" tha... |
| 157 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the noisy historical/Gaussian reuse terms with a deterministic best-fit-dominant rule plu... |
| 158 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Remove the noisy Gaussian/mean-based reuse term and the smoothed-histogram bonus, and use pure be... |
| 159 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll replace the noisy Gaussian reuse term with a sum-of-two-exponentials "pairing" bonus that re... |
| 160 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the mean-centered Gaussian reuse term with a deterministic complementary-fit bonus derive... |
| 161 | edit | not_better | 0.9661 | 0.9668 | $0.0007 | I'll replace the mean-centered Gaussian reuse term with a smooth, strictly-monotone function of t... |
| 162 | edit | not_better | 0.9663 | 0.9668 | $0.0023 | I'll refine the reuse tie-break by adding a second Gaussian component centered at the complement ... |
| 163 | edit | not_better | 0.9666 | 0.9668 | $0.0007 | Widen the smoothing kernel to a flatter 7-wide window (offsets -3..+3) for a lower-variance estim... |
| 164 | edit | not_better | 0.9649 | 0.9668 | $0.0007 | I will add a bounded "complement fit" bonus computed from the smoothed histogram of past items, r... |
| 165 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll make the score a pure, deterministic best-fit rule (score = -residual, exact fit boosted) wi... |
| 166 | edit | not_better | 0.5224 | 0.9668 | $0.0005 | I'll replace the noisy historical terms with a deterministic "least-loaded bin that still fits" r... |
| 167 | edit | not_better | 0.9649 | 0.9668 | $0.0009 | Increase the bounded smoothed-histogram usefulness weight to 0.8 (still below the residual gap of... |
| 168 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Add a small best-fit-consistent tie-break that rewards residuals equal to a frequently-seen past ... |
| 169 | edit | not_better | 0.9649 | 0.9668 | $0.0006 | I'll add a deterministic "expected future waste" term: score = -residual plus a bounded penalty p... |
| 170 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the noisy historical/Gaussian adjustments with a scaled best-fit core plus a small d... |
| 171 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll add a deterministic "leftover quality" tie-break that favors residuals which are themselves ... |
| 172 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll add a small, strictly sub-1.0 tie-break that prefers residuals which exactly equal a common ... |
| 173 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I will replace the weak tie-break with a strong best-fit core scaled by a large factor plus a bou... |
| 174 | edit | not_better | 0.9668 | 0.9668 | $0.0008 | Replace the mean-item-keyed reuse Gaussian with one keyed on the empirical mode (argmax of the sm... |
| 175 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the noisy distance-to-mean reuse bonus with a term that prefers bin residuals which are c... |
| 176 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the historical-statistics heuristic with a simple weighted best-fit-plus-residual-fi... |
| 177 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll replace the fixed reuse Gaussian with one keyed on the empirical mode of the smoothed histog... |
| 178 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the smoothed-histogram/ad-hoc bonuses with the classic best-fit choice plus a small learn... |
| 179 | edit | not_better | 0.9668 | 0.9668 | $0.0006 | The current smoothed-histogram tie-break is noisy and hasn't helped. I'll replace it with a well-... |
| 180 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the noisy histogram-based tie-break with a principled "least-likely-to-leave-useful-... |
| 181 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the noisy histogram/mode tie-break (which never helped) with a clean, strictly-domin... |
| 182 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll replace the noisy histogram-based tie-break bonuses with a clean, strongly-dominant best-fit... |
| 183 | edit | invalid | 0.0000 | 0.9668 | $0.0007 | Remove the noisy histogram/reuse bonuses entirely (they hurt or tie at best) and replace with a c... |
| 184 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll strip out the noisy histogram/reuse bonuses and keep a strictly-dominant best-fit primary te... |
| 185 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | Replace the noisy deterministic tie-breaks with pure best-fit-dominant scoring (primary term scal... |
| 186 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | Replace the ad-hoc smoothing/reuse terms with a principled "best-fit plus expected-waste" rule: k... |
| 187 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the noisy histogram/reuse tie-breaks with a principled "best-fit plus gap-filling ex... |
| 188 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | The best-fit primary term should be scaled by a large constant (e.g. 1000) so that best-fit order... |
| 189 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I will keep the dominant best-fit primary term but replace the current histogram/reuse bonuses wi... |
| 190 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll add a score-based multiplicative "balance" term: keep the dominant best-fit primary term, bu... |
| 191 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | Simplify to the empirically strongest rule seen so far: remove the noisy histogram smoothing and ... |
| 192 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I will keep the best-fit-dominant structure but replace the heuristic histogram/reuse bonuses wit... |
| 193 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | Replace the smoothed-histogram and Gaussian reuse bonuses with a bounded bonus based on a "pairin... |
| 194 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the T3-constraint with a stronger "modified best-fit" that tracks the effective mean... |
| 195 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll strengthen best-fit dominance by scaling the primary -residual term by 1000 so it strictly o... |
| 196 | edit | not_better | 0.9661 | 0.9668 | $0.0007 | Increase the smoothed-histogram usefulness weight from 0.4 to 0.6 and sharpen the smoothing kerne... |
| 197 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | The dominant best-fit term uses `tight = -residual` which gives integer-spaced scores; any bonus ... |
| 198 | edit | not_better | 0.9659 | 0.9668 | $0.0007 | I'll add a bounded "perfect-complement" bonus: after the strict best-fit primary term, boost resi... |
| 199 | edit | invalid | 0.0000 | 0.9668 | $0.0006 | Replace the smoothed-histogram/kernel machinery with a simpler, strictly-dominant best-fit and a ... |
| 200 | edit | not_better | 0.9616 | 0.9668 | $0.0010 | Replace the histogram/reuse bonuses with a clean "avoid-waste" rule: keep best-fit as the primary... |
| 201 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll add a bounded "future-fit" bonus that favors residuals likely to be exactly filled by a futu... |
| 202 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the fixed integer-best-fit ordering with a rule that keeps best-fit dominance but rewards... |
| 203 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the current smoothed-histogram/reuse bonuses with an online learned "perfect-fit" score: ... |
| 204 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll replace the complicated bonus machinery with a clean, strictly-dominant best-fit plus a tie-... |
| 205 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the ad-hoc reuse Gaussian with a single tie-breaking rule that only breaks exact-tie resi... |
| 206 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll keep best-fit as the strict primary term but add a bounded tie-breaking bonus that prefers t... |
| 207 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the bonus machinery with a stricter, strictly-dominant best-fit that additionally prefers... |
| 208 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the history-based bonuses with a simple "best-fit with a small exact-fit tie-break" ... |
| 209 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll replace the tie-breaking bonus machinery with a variant of the classic "best fit with reuse ... |
| 210 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the soft histogram/Gaussian bonuses (which are dominated by strict best-fit and only brea... |
| 211 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the dominated tie-break bonuses with a genuine, but bounded, improvement over pure b... |
| 212 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll replace the residual-usefulness bonus with a lookahead of the online item-size distribution:... |
| 213 | edit | not_better | 0.9642 | 0.9668 | $0.0006 | I'll replace the fragile history/Gaussian machinery with a robust "best fit" that strictly minimi... |
| 214 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I will add a bounded "match advantage" term that estimates, from the online item-size histogram, ... |
| 215 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the dominated Gaussian/mean-based reuse bonus with a strictly tie-breaking "sum-matc... |
| 216 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Add a bounded "waste from pairing": among bins with the minimal best-fit residual, prefer the res... |
| 217 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | Replace the dominated tie-break bonuses with a small, bounded "exact-fit-hint" that stays strictl... |
| 218 | edit | not_better | 0.9666 | 0.9668 | $0.0008 | Add a "future-fit" refinement: keep best-fit as the primary rule, but among bins whose residual i... |
| 219 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I will add a "least-loaded fragmentation" tie-break: keep best-fit dominant, but among bins with ... |
| 220 | edit | not_better | 0.9661 | 0.9668 | $0.0007 | I will restructure the scoring so that best-fit (smallest residual) is strictly the primary key (... |
| 221 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I will keep best-fit as the strict primary rule but make the within-tie preference sharper: inste... |
| 222 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll replace the current dominant best-fit-plus-tie-break heuristic with a proper "best fit decre... |
| 223 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the hand-crafted heuristic with the classic "best fit" rule implemented cleanly, but reso... |
| 224 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I will replace the heuristic scoring with a strictly dominant best-fit primary term (residual sca... |
| 225 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the weak tie-break with a bounded "matching-fit" bonus that favors residuals equal to a l... |
| 226 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Use a "best-fit with a small look-ahead tie-break that prefers residuals which leave a gap fillab... |
| 227 | edit | not_better | 0.9621 | 0.9668 | $0.0007 | I will replace the memoryless best-fit rule with a "best fit with a bounded residual-utility tie-... |
| 228 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I will modify the tie-break so it targets the exact-fit case more aggressively: keep best-fit dom... |
| 229 | edit | not_better | 0.9656 | 0.9668 | $0.0007 | I will add a bounded, sign-aware "waste" adjustment: keep best-fit strictly dominant, but let the... |
| 230 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll replace the fixed hand-tuned constants with a "law of cosines"/subset-sum-aware tie-break: k... |
| 231 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | The current heuristic perturbs best-fit with a weak margin, which lost score; I'll revert to a st... |
| 232 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I will remove the leaked per-instance state that persists across instances (the module-level coun... |
| 233 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll keep the dominant best-fit term but replace the weak histogram tie-break with a "fillable ga... |
| 234 | edit | not_better | 0.9668 | 0.9668 | $0.0008 | I'll replace the heuristic tie-break with a simple, robust "best fit decreasing"-style rule: use ... |
| 235 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the pure best-fit tie-break with a "residual-matching" key: keep strict best-fit dom... |
| 236 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the weak tie-break with a self-tuning best-fit that adds a tiny bonus for bins whose resu... |
| 237 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I will switch from pure best-fit to a two-scale rule that keeps best-fit dominant but, for bins w... |
| 238 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Add a small, bounded "fillability" bonus that rewards putting the item in a bin so that the resul... |
| 239 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the tie-break with a principled "future-fit" score: keep strict best-fit dominant by... |
| 240 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll replace the histogram-based tie-break with a pure best-fit rule (smallest residual wins) tha... |
| 241 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the weak smoothed-histogram tie-break with a principled "harmonic/sum-of-squares" bias: k... |
| 242 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll drop the noisy histogram/reuse tie-breaks and instead use a pure, deterministic best-fit rul... |
| 243 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll replace the current tie-break machinery with a pure best-fit dominance (large residual multi... |
| 244 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll make the scoring a strict lexicographic best-fit where the primary key is exact-fill prefere... |
| 245 | edit | not_better | 0.9666 | 0.9668 | $0.0007 | I'll replace the residual-usefulness tie-break with a revised best-fit that uses a stronger reuse... |
| 246 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Add a bounded "pairing" bonus that, among bins whose residual differs from the item by at most a ... |
| 247 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll shift from a purely local best-fit bias to a "worst-fit-aware" secondary term: keep best-fit... |
| 248 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll keep pure best-fit as the strictly dominant primary key, but replace the noisy histogram tie... |
| 249 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the smoothed-histogram/reuse heuristics (which did not help) with a score that keeps best... |
| 250 | edit | not_better | 0.9668 | 0.9668 | $0.0007 | I'll replace the fixed Gaussian "reuse" bonus (which targets the mean and is mostly noise) with a... |
| 251 | edit | not_better | 0.9630 | 0.9668 | $0.0007 | I'll keep exact-fill dominant but replace the linear residual term (-residual) with a strictly-co... |
| 252 | edit | not_better | 0.5224 | 0.9668 | $0.0005 | I'll switch from best-fit residual ranking to a "worst-fit (least-full bin)" primary rule combine... |
| 253 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the smoothed-histogram/reuse heuristics with a principled best-fit plus a small "perfect-... |
| 254 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Keep best-fit (−residual) dominant, but add a small secondary term that favors residuals which ar... |
| 255 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | I'll replace the noisy smoothed-histogram and Gaussian reuse bonuses with a much finer-grained, d... |
| 256 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll keep exact-fill and best-fit dominant, but replace the noisy secondary bonuses with a single... |
| 257 | edit | not_better | 0.9614 | 0.9668 | $0.0006 | I will replace the noisy smoothed-histogram and Gaussian reuse bonuses with a cleaner and cheaper... |
| 258 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll remove all the noisy secondary heuristics (smoothed histogram, Gaussian reuse) and instead u... |
| 259 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | I'll replace the noisy histogram/reuse bonuses with a bounded "sum-of-two-items" fit bonus: since... |
| 260 | edit | not_better | 0.9663 | 0.9668 | $0.0007 | I'll keep best-fit dominant but strengthen and sharpen the residual-usefulness signal: use a narr... |
| 261 | edit | gate_rejected | 0.9670 | 0.9668 | $0.0007 | I'll strengthen the residual-usefulness tie-break by making the smoothed histogram sharper (narro... |
| 262 | edit | not_better | 0.9666 | 0.9668 | $0.0007 | I'll replace the noisy smoothed-histogram usefulness term with a sharper, narrower-kernel histogr... |
| 263 | edit | not_better | 0.9616 | 0.9668 | $0.0007 | Replace the 5-tap smoothed histogram with a sharper single-spike-plus-narrow read of the exact it... |
| 264 | edit | not_better | 0.9663 | 0.9668 | $0.0006 | I will sharpen the usefulness tie-break by replacing the symmetric 5-tap kernel with an asymmetri... |
| 265 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | I'll replace the noisy secondary heuristics with a deterministic, strictly-best-fit rule that onl... |
| 266 | edit | not_better | 0.9649 | 0.9668 | $0.0006 | Replace the smoothed 5-tap kernel with a sharp single-tap read of the cumulative item-size histog... |
| 267 | edit | invalid | 0.0000 | 0.9668 | $0.0006 | I will keep the strictly best-fit-dominant ordering (tight residual) and replace the smoothed 5-t... |
| 268 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | The best-fit gap is the dominant signal, so I'll make exact-tie comparisons break toward the bin ... |
| 269 | edit | not_better | 0.9663 | 0.9668 | $0.0007 | I'll add a light "sum-of-residuals" consolidation objective: among bins with equal best-fit resid... |
| 270 | edit | not_better | 0.9649 | 0.9668 | $0.0006 | I'll make the tie-break term depend on the item size in a scale-invariant way, using a sharp hist... |
| 271 | edit | not_better | 0.9654 | 0.9668 | $0.0006 | I'll replace the heuristic tie-breaking with a deterministic random-like "hash of the residual an... |
| 272 | edit | not_better | 0.9616 | 0.9668 | $0.0008 | I'll make the tie-break deterministic and stably beneficial: keep strict best-fit dominance, and ... |
| 273 | edit | not_better | 0.9616 | 0.9668 | $0.0005 | Replace the noisy smoothed-histogram and Gaussian-reuse tie-breakers with a strictly-best-fit dom... |
| 274 | edit | not_better | 0.9637 | 0.9668 | $0.0007 | I will strengthen the reuse of nearly-full bins by making the exact-fit bonus scale correctly (cu... |
| 275 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the fixed smoothed-histogram / Gaussian-reuse tie-breaks with a clean strictly-best-fit r... |
| 276 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | The current tie-break only fires on exact equal residuals, which is rare; I'll introduce a sub-in... |
| 277 | edit | invalid | 0.0000 | 0.9668 | $0.0007 | Replace the smoothed-kernel and Gaussian-reuse tie-breakers with a single crisp bounded bonus: am... |
| 278 | edit | not_better | 0.9616 | 0.9668 | $0.0006 | Replace the smoothed-kernel histogram and Gaussian reuse bonus with a single crisp bounded bonus ... |
| 279 | edit | improved | 0.9747 | 0.9747 | $0.0007 | I'll replace the fixed -residual + small bonuses with a scale-invariant transform of the residual... |
| 280 | edit | gate_rejected | 0.9749 | 0.9747 | $0.0008 | Make the tie-break among equal-residual bins context-dependent on the arriving item size: keep th... |
| 281 | edit | not_better | 0.9706 | 0.9747 | $0.0007 | I'll replace the somewhat arbitrary log-penalty coefficients with a stronger best-fit emphasis (h... |
| 282 | edit | not_better | 0.9701 | 0.9747 | $0.0008 | Increase the dominance of the proven log tight-fit term from 4.0 to a higher weight (e.g. 8.0) wh... |
| 283 | edit | improved | 0.9749 | 0.9749 | $0.0007 | Add a small bonus that rewards bins whose exact leftover capacity equals the most common item siz... |
| 284 | edit | not_better | 0.9749 | 0.9749 | $0.0007 | I will make the smoothed-frequency bonus depend on the arriving item's size, rewarding bins whose... |
| 285 | edit | gate_rejected | 0.9749 | 0.9749 | $0.0008 | I'll add a targeted "sum-complement" bonus: in addition to rewarding bins whose exact residual ma... |
| 286 | edit | not_better | 0.9616 | 0.9749 | $0.0006 | I'll replace the noisy smoothed-kernel histogram and the reuse/Gaussian terms with a cleaner sign... |
| 287 | edit | not_better | 0.9749 | 0.9749 | $0.0008 | (no description) |
| 288 | edit | invalid | 0.0000 | 0.9749 | $0.0008 | I'll strengthen the exact-residual reuse signal by giving the well-proven best-fit dominance an a... |
| 289 | edit | not_better | 0.9749 | 0.9749 | $0.0008 | I'll replace the fixed Gaussian reuse term's constant 0.25-mean window with a signal tied to the ... |
| 290 | edit | not_better | 0.9614 | 0.9749 | $0.0006 | I'll calibrate the reuse-term bonus so it is driven by the two dominant integer best-fit gaps: I'... |
| 291 | edit | not_better | 0.9614 | 0.9749 | $0.0006 | The smoothed frequency convolution is noisy and adds cost each call; I'll replace it with a direc... |
| 292 | edit | not_better | 0.9616 | 0.9749 | $0.0006 | I'll strengthen best-fit dominance (raise the log-penalty weight so tightness clearly beats the t... |
| 293 | edit | not_better | 0.9616 | 0.9749 | $0.0007 | I'll replace the smoothed-kernel convolution (noisy and order-dependent) with a cheap direct raw-... |
| 294 | edit | not_better | 0.9614 | 0.9749 | $0.0006 | Replace the noisy Gaussian reuse term with a deterministic "score residual as a typical item-size... |
| 295 | edit | not_better | 0.9614 | 0.9749 | $0.0006 | I'll make the tie-break signal purely predictive and stable: replace the Gaussian reuse term and ... |
| 296 | edit | not_better | 0.9616 | 0.9749 | $0.0007 | The best-fit dominance term is currently a log penalty that makes non-exact fits nearly tie; I'll... |
| 297 | edit | not_better | 0.9616 | 0.9749 | $0.0006 | The Gaussian reuse term is the only part that ever helped, so I'll simplify by removing the noisy... |
| 298 | edit | not_better | 0.9614 | 0.9749 | $0.0006 | I'll replace the noisy smoothed-kernel convolution and the Gaussian reuse term with a single dete... |
| 299 | edit | invalid | 0.0000 | 0.9749 | $0.0008 | I'll add an adaptive "fullness matching" term: instead of only rewarding residuals near the mean ... |
| 300 | edit | improved | 0.9809 | 0.9809 | $0.0007 | I'll rebuild from the original 0.9749 version but simplify the smoothed-kernel frequency lookup t... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,40 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Log-penalty best fit with neighbor-blended frequency lookup and reuse bonus."""
 import numpy as np
+
+_counts = np.zeros(101, dtype=np.float64)
+_n = 0.0
+_sum = 0.0
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
+    global _n, _sum
+    residual = bins - item  # >= 0 for all bins shown
+    rf = residual.astype(np.float64)
+    r = residual.astype(np.int64)
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    freq = _counts
+    # neighbor-blended frequency lookup: raw frequency plus half-weight neighbors
+    use = freq[r]
+    use = use + 0.5 * np.where(r > 0, freq[np.clip(r - 1, 0, 100)], 0.0)
+    use = use + 0.5 * np.where(r < 100, freq[np.clip(r + 1, 0, 100)], 0.0)
+
+    # log penalty preserves best-fit dominance (monotone decreasing in residual)
+    tight = -np.log1p(rf)
+    score = 4.0 * tight + 0.4 * use
+
+    if _n > 0.0:
+        mean_item = _sum / _n
+        reuse = 0.25 * np.exp(-((rf - mean_item) ** 2) /
+                              (2.0 * (0.25 * mean_item + 1.0) ** 2))
+        score = score + reuse
+
+    score[residual == 0] += 1000.0
+
+    _counts[item] += 1.0
+    _n += 1.0
+    _sum += item
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (28 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 12 | `global _n, _sum` | -0.9809 | essential: the program fails or turns invalid without it |
| 13 | `residual = bins - item` | -0.9809 | essential: the program fails or turns invalid without it |
| 13 | `term + bins` | -0.9809 | essential: the program fails or turns invalid without it |
| 14 | `rf = residual.astype(np.float64)` | -0.9809 | essential: the program fails or turns invalid without it |
| 15 | `r = residual.astype(np.int64)` | -0.9809 | essential: the program fails or turns invalid without it |
| 17 | `freq = _counts` | -0.9809 | essential: the program fails or turns invalid without it |
| 19 | `use = freq[r]` | -0.9809 | essential: the program fails or turns invalid without it |
| 24 | `tight = -np.log1p(rf)` | -0.9809 | essential: the program fails or turns invalid without it |
| 25 | `score = 4.0 * tight + 0.4 * use` | -0.9809 | essential: the program fails or turns invalid without it |
| 33 | `score[residual == 0] += 1000.0` | -0.1749 | matters |
| 13 | `term - item` | -0.0676 | matters |
| 25 | `term + 0.4 * use` | -0.0193 | matters |
| 35 | `_counts[item] += 1.0` | -0.0193 | matters |
| 21 | `term + use` | -0.0125 | matters |
| 20 | `term + use` | -0.0094 | matters |
| 20 | `use = use + 0.5 * np.where(r > 0, freq[np.clip(r - 1, 0, 100)], 0.0)` | -0.0058 | matters |
| 20 | `term + 0.5 * np.where(r > 0, freq[np.clip(r - 1, 0, 100)], 0.0)` | -0.0058 | matters |
| 21 | `use = use + 0.5 * np.where(r < 100, freq[np.clip(r + 1, 0, 100)], 0.0)` | -0.0029 | matters |
| 21 | `term + 0.5 * np.where(r < 100, freq[np.clip(r + 1, 0, 100)], 0.0)` | -0.0029 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 27: `if _n > 0.0: ...`
- line 28: `mean_item = _sum / _n`
- line 29: `reuse = 0.25 * np.exp(-(rf - mean_item) ** 2 / (2.0 * (0.25 * mean_item + 1.0) ** 2))`
- line 31: `score = score + reuse`
- line 31: `term + score`
- line 31: `term + reuse`
- line 36: `_n += 1.0`
- line 37: `_sum += item`

**REPAIRED (not an explanation)**: removing these raises the public score by more than the tolerance. The found program is worse than a simpler one; these are repairs, not parts of an explanation.

- line 25: `term + 4.0 * tight` (Δ +0.0088)

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9809 | 0.9776 |
| minimal (3 parts removed) | 0.9805 | 0.9793 |

Minimal program:

```python
"""Log-penalty best fit with neighbor-blended frequency lookup and reuse bonus."""
import numpy as np
_counts = np.zeros(101, dtype=np.float64)
_n = 0.0
_sum = 0.0

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _n, _sum
    residual = bins - item
    rf = residual.astype(np.float64)
    r = residual.astype(np.int64)
    freq = _counts
    use = freq[r]
    use = use + 0.5 * np.where(r > 0, freq[np.clip(r - 1, 0, 100)], 0.0)
    use = use + 0.5 * np.where(r < 100, freq[np.clip(r + 1, 0, 100)], 0.0)
    tight = -np.log1p(rf)
    score = 4.0 * tight + 0.4 * use
    score[residual == 0] += 1000.0
    _counts[item] += 1.0
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online --budget 0.75 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 2
python -m autoresearch.loop --report experiments/llm-long-search-v1/runs/s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `adb7fe98e2b1a4de003a9248cda56b4f0f74b6e5`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bin_packing_online/evaluate.py` `0ac9a4a253a299d2`
- `problems/bin_packing_online/initial.py` `609927c5ea619a94`
- `problems/bin_packing_online/problem.md` `aa1aa4a2d6d00d6a`
- `problems/bin_packing_online/verify.py` `b3ea67a1c6f94885`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
