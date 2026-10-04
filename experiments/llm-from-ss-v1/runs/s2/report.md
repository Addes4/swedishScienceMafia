# Research loop report: bin_packing_online_ss

| | |
|---|---|
| problem | `bin_packing_online_ss` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2509 of a $0.60 hard cap, 264 calls, 760,832 tokens |
| wall time | search 5420 s, baselines 13 s, explain 82 s |
| stopped | wall (wall_limit) |
| evaluations | 265 (251 valid), 2 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9942 | 0.9950 | |
| `best_program.py` (final incumbent) | 0.9952 | 0.9947 | **OVERFIT?** public rose, hidden fell |
| baseline `best_fit` | 0.9616 | 0.9604 | `problems/bin_packing_online_ss/baselines/best_fit.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_ss/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_ss/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9952 | 0.9947 | 1 parts removed |

Audit: public 0.9942 → 0.9952 (+0.0010), hidden 0.9950 → 0.9947 (-0.0003); public − hidden gap of the final program 0.0005. **OVERFIT?** The public score rose while the hidden score fell: treat the gain as unconfirmed.

Against the baselines: the final program's public score is above the best baseline (`sum_of_squares`, 0.9942). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9942 | $0.0006 | Replace the greedy sum-of-squares heuristic with a "best fit among the fullest bins" rule tuned b... |
| 2 | edit | not_better | 0.9942 | 0.9942 | $0.0006 | Replace the pure sum-of-squares greedy with a hybrid rule that blends the sum-of-squares bin-coun... |
| 3 | edit | not_better | 0.9942 | 0.9942 | $0.0007 | Use a truthful sum-of-squares delta as the primary term, and only use the remaining-capacity r as... |
| 4 | edit | not_better | 0.9942 | 0.9942 | $0.0008 | The current sum-of-squares rule ignores the fact that the harness shows unused bins last and that... |
| 5 | edit | improved | 0.9950 | 0.9950 | $0.0009 | Replace the fixed delta-weighting with a rule that evaluates the sum-of-squares delta exactly (we... |
| 6 | edit | not_better | 0.9940 | 0.9950 | $0.0011 | Replace the binary residual-existence tiebreak with an exact "number of distinct residual classes... |
| 7 | edit | not_better | 0.9945 | 0.9950 | $0.0010 | The lower bound is known and stable, so a mild "fill the fullest bin that still leaves no new cla... |
| 8 | edit | not_better | 0.9945 | 0.9950 | $0.0010 | Add a tiny stochastic-free tie-break that, among placements with equal sum-of-squares delta, pref... |
| 9 | edit | not_better | 0.9947 | 0.9950 | $0.0010 | Replace the sum-of-squares primary rule with a lookahead-flavored "fill to complement expected it... |
| 10 | edit | not_better | 0.9851 | 0.9950 | $0.0009 | Replace the fixed global sum-of-squares tally with a memory-bounded ("exponentially decayed") sum... |
| 11 | edit | not_better | 0.9945 | 0.9950 | $0.0012 | Refine the exact-delta tie-break: maintain a count of item sizes seen so far and, among placement... |
| 12 | edit | not_better | 0.8203 | 0.9950 | $0.0010 | I will widen the primary tie-break margin from exact-delta ties to near-ties by quantizing the su... |
| 13 | edit | not_better | 0.9942 | 0.9950 | $0.0009 | I'll add a "best-fit decreasing" style secondary tiebreak within the sum-of-squares family by pre... |
| 14 | edit | invalid | 0.0000 | 0.9950 | $0.0011 | Add a mild, memory-bounded secondary term that prefers placements producing a post-placement resi... |
| 15 | edit | not_better | 0.9942 | 0.9950 | $0.0010 | Replace the binary residual-existence tiebreak with a decaying (frequency-weighted) count of resi... |
| 16 | edit | not_better | 0.9940 | 0.9950 | $0.0010 | Replace the numeric-key packing (which numpifies small integers) with a clean lexicographic compa... |
| 17 | edit | not_better | 0.9942 | 0.9950 | $0.0011 | I will replace the numeric-key scoring (which loses precision by packing terms into a float) with... |
| 18 | edit | not_better | 0.9616 | 0.9950 | $0.0008 | The scoring currently uses sum-of-squares which tends to spread items evenly. I will switch the p... |
| 19 | edit | not_better | 0.9942 | 0.9950 | $0.0011 | Replace the fragile float-key packing with a clean numpy lexicographic selection: compute exact i... |
| 20 | edit | invalid | 0.0000 | 0.9950 | $0.0010 | I will change the tie-break so that among exact sum-of-squares delta ties, the placement is chose... |
| 21 | edit | not_better | 0.9947 | 0.9950 | $0.0012 | I'll replace the sum-of-squares primary with the classic and theoretically strong "best fit decre... |
| 22 | edit | not_better | 0.9942 | 0.9950 | $0.0011 | I will add a lookahead-style "closing bonus" tiebreak: among placements with equal sum-of-squares... |
| 23 | edit | not_better | 0.7085 | 0.9950 | $0.0012 | I will keep the strong sum-of-squares primary rule but replace the tie-break with one that prefer... |
| 24 | edit | not_better | 0.9942 | 0.9950 | $0.0011 | Keep the sum-of-squares primary rule (which is strong) but replace the tie-break with a "best-fit... |
| 25 | edit | not_better | 0.9940 | 0.9950 | $0.0010 | I will refine the tie-break to a two-level rule that more closely mimics the harmonic/consolidati... |
| 26 | edit | not_better | 0.9616 | 0.9950 | $0.0008 | I will replace the sum-of-squares primary rule with the classic "best fit" rule (place the item i... |
| 27 | edit | not_better | 0.6870 | 0.9950 | $0.0010 | I will keep the sum-of-squares primary rule but refine the tie-break: among equal-delta placement... |
| 28 | edit | not_better | 0.9937 | 0.9950 | $0.0011 | The sum-of-squares rule is strong but the "1e9/1e6" scaling in the tiebreak risks numerical cross... |
| 29 | edit | not_better | 0.9927 | 0.9950 | $0.0011 | I will keep the sum-of-squares primary but widen the tie-break to fire within a small tolerance b... |
| 30 | edit | not_better | 0.9942 | 0.9950 | $0.0009 | I will replace the discrete "prefer existing residual class" tie-break with a continuous score th... |
| 31 | edit | not_better | 0.9942 | 0.9950 | $0.0010 | I will keep the strong sum-of-squares primary rule but change the tie-break to prefer the placeme... |
| 32 | edit | not_better | 0.9950 | 0.9950 | $0.0011 | I'll strengthen the rule by adding an explicit high-priority bonus for placements that produce a ... |
| 33 | edit | invalid | 0.0000 | 0.9950 | $0.0011 | I'll investigate whether the harness's bins array ordering assumption is the bottleneck — instead... |
| 34 | edit | not_better | 0.9950 | 0.9950 | $0.0012 | I'll keep the sum-of-squares delta as the primary term but add a small continuous secondary term ... |
| 35 | edit | not_better | 0.9522 | 0.9950 | $0.0013 | I'll replace the floating-point scaling trick (1e9/1e6) with a clean lexicographic key so the exi... |
| 36 | edit | not_better | 0.9937 | 0.9950 | $0.0010 | I'll add a "best-fit / min residual" fallback that triggers only when the sum-of-squares deltas a... |
| 37 | edit | not_better | 0.9942 | 0.9950 | $0.0012 | I'll make the score exactly -delta plus a fractional tie-break bonus in [0,1) that prefers the ti... |
| 38 | edit | not_better | 0.9942 | 0.9950 | $0.0012 | I'll add item-size frequency tracking and give a bonus to placements that leave a residual matchi... |
| 39 | edit | not_better | 0.9950 | 0.9950 | $0.0011 | Replace the pairwise sum-of-squares primary rule with the well-known "Sum of Squares" applied a b... |
| 40 | edit | not_better | 0.9947 | 0.9950 | $0.0012 | I'll add a small continuous bonus to the score for placements whose post-placement residual match... |
| 41 | edit | gate_rejected | 0.9950 | 0.9950 | $0.0009 | I'll replace the tie-break with one that targets "perfect complement" residuals: give a bonus whe... |
| 42 | edit | not_better | 0.9942 | 0.9950 | $0.0008 | The current rule caps performance because unused bins score the same as any bin that perfectly ze... |
| 43 | edit | not_better | 0.9942 | 0.9950 | $0.0010 | I'll add a small continuous bonus (strictly less than 1 in delta units) that rewards placing into... |
| 44 | edit | not_better | 0.9937 | 0.9950 | $0.0010 | I will replace the fixed tie-break with a two-item lookahead proxy: track a running histogram of ... |
| 45 | edit | not_better | 0.9950 | 0.9950 | $0.0011 | The tie-break will be redesigned so that it no longer merely prefers residuals equal to a common ... |
| 46 | edit | not_better | 0.9942 | 0.9950 | $0.0012 | I'll reorder the tie-break tiers so that among equal sum-of-squares deltas, the tightest fit (sma... |
| 47 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | I'll change the primary rule from "minimize sum of squared residual-class counts" (which behaves ... |
| 48 | edit | not_better | 0.9947 | 0.9950 | $0.0010 | I'll strengthen the residual-class consolidation by replacing the fixed tie-break with a small fr... |
| 49 | edit | not_better | 0.9598 | 0.9950 | $0.0009 | Replace the sum-of-squares primary rule with a Best-Fit-plus-residual-consolidation rule: score e... |
| 50 | edit | not_better | 0.9950 | 0.9950 | $0.0011 | I will add a lightweight two-item lookahead: maintain a running histogram of item sizes and, afte... |
| 51 | edit | not_better | 0.9940 | 0.9950 | $0.0010 | I'll replace the numeric tie-break encoding with a lexicographic sort using pure integer keys, re... |
| 52 | edit | invalid | 0.0000 | 0.9950 | $0.0010 | I will switch the primary rule to a harmonic (1/N-weighted) sum instead of sum-of-squares, which ... |
| 53 | edit | not_better | 0.9616 | 0.9950 | $0.0009 | I'll replace the primary rule with a first-fit-decreasing-emulating "Best Fit" variant: instead o... |
| 54 | edit | not_better | 0.9942 | 0.9950 | $0.0009 | I'll keep the sum-of-squares primary rule but replace the fixed tie-break with a proper "sum of s... |
| 55 | edit | not_better | 0.9940 | 0.9950 | $0.0012 | I'll replace the hand-crafted sum-of-squares heuristic with a proper online algorithm: maintain a... |
| 56 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | I'll add a size-based protection: when the chosen bin would leave a tiny residual (&lt; item min ... |
| 57 | edit | not_better | 0.9950 | 0.9950 | $0.0011 | I'll add a two-item lookahead using a running item-size histogram: after computing the sum-of-squ... |
| 58 | edit | invalid | 0.0000 | 0.9950 | $0.0010 | The sum-of-squares rule behaves like Worst-Fit, which is known to be suboptimal; the best online ... |
| 59 | edit | not_better | 0.9940 | 0.9950 | $0.0010 | I'll refine the tie-break so that when sum-of-squares deltas are equal, we prefer placements that... |
| 60 | edit | not_better | 0.9940 | 0.9950 | $0.0011 | I'll add a small linear Best-Fit-style bias (proportional to the post-placement residual) on top ... |
| 61 | edit | not_better | 0.9945 | 0.9950 | $0.0011 | I'll replace the sum-of-squares primary rule with the classic "Subset-Sum / up-to-the-next-smalle... |
| 62 | edit | not_better | 0.9616 | 0.9950 | $0.0009 | I'll switch the primary criterion from sum-of-squares (which acts like Worst-Fit) to true Best-Fi... |
| 63 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | Add a lookahead-free "subset-sum adaptivity": keep the proven Sum-of-Squares primary rule but bre... |
| 64 | edit | not_better | 0.9947 | 0.9950 | $0.0011 | I'll keep the proven Sum-of-Squares primary rule but add a small adaptive perturbation based on t... |
| 65 | edit | not_better | 0.9950 | 0.9950 | $0.0009 | Implement the classic "Worst-Fit with matching-residual consolidation" variant of the Sum-of-Squa... |
| 66 | edit | not_better | 0.9940 | 0.9950 | $0.0009 | I'll replace the sum-of-squares primary rule with the closed-interval / harmonic "best fit into t... |
| 67 | edit | not_better | 0.9945 | 0.9950 | $0.0011 | I'll keep the sum-of-squares primary rule (which is proven near-optimal) but change the tie-break... |
| 68 | edit | not_better | 0.9947 | 0.9950 | $0.0010 | Keep the sum-of-squares primary delta, but change the tie-break so that instead of preferring res... |
| 69 | edit | not_better | 0.9947 | 0.9950 | $0.0012 | Keep the exact sum-of-squares primary rule, but for exact-delta ties compute a secondary score fr... |
| 70 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | I'll keep the proven sum-of-squares primary rule but replace the residual-consolidation tie-break... |
| 71 | edit | not_better | 0.9940 | 0.9950 | $0.0010 | Keep the exact sum-of-squares primary delta, but for exact-delta ties break in favor of placement... |
| 72 | edit | not_better | 0.9945 | 0.9950 | $0.0011 | Keep the sum-of-squares primary delta, but for exact-delta ties prefer residuals that exactly mat... |
| 73 | edit | invalid | 0.0000 | 0.9950 | $0.0010 | The current tie-break is largely redundant because the sum-of-squares delta itself already ties s... |
| 74 | edit | not_better | 0.9584 | 0.9950 | $0.0010 | Replace the sum-of-squares primary rule with the classic "best fit with capacity-interval (harmon... |
| 75 | edit | not_better | 0.9942 | 0.9950 | $0.0011 | The sum-of-squares rule is near-optimal, but its strongest form uses the exact criterion: minimiz... |
| 76 | edit | not_better | 0.9950 | 0.9950 | $0.0013 | Keep the exact sum-of-squares primary delta, but flip the secondary numeric tie-break so that amo... |
| 77 | edit | not_better | 0.9947 | 0.9950 | $0.0011 | Replace the two-tier residuals-consolidation tie-break with a finer tie-break on exact-delta ties... |
| 78 | edit | not_better | 0.9945 | 0.9950 | $0.0010 | Add a stronger, lookahead-free refinement: among bins with equal sum-of-squares delta, prefer pla... |
| 79 | edit | improved | 0.9952 | 0.9952 | $0.0008 | Replace the "prefer existing residual" tie-break (which is redundant with the sum-of-squares delt... |
| 80 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary rule, but replace the redundant largest-residual tie-... |
| 81 | edit | invalid | 0.0000 | 0.9952 | $0.0009 | Break exact-sum-of-squares-delta ties by preferring the placement whose post-placement residual i... |
| 82 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | The sum-of-squares rule treats residuals as unordered classes, but the actual future cost of a re... |
| 83 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary rule but replace the rigid tie-break with a small sec... |
| 84 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Keep the exact sum-of-squares primary delta but replace the numeric tie-break: among ties, prefer... |
| 85 | edit | not_better | 0.7706 | 0.9952 | $0.0009 | The current code is noisy: it computes scores with a broken tie-break and inputs, and `_caps` nev... |
| 86 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the broken (and now unused) rank/tie-break machinery with a cleaner, cheaper implementati... |
| 87 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The sum-of-squares rule is essentially a proxy for keeping residuals balanced, but the exact delt... |
| 88 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary rule but improve the tie-break: instead of always pre... |
| 89 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | (no description) |
| 90 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll replace the arbitrary largest-residual tie-break with a "best-fit within the minimum-delta c... |
| 91 | edit | not_better | 0.9920 | 0.9952 | $0.0009 | I'll replace the exact sum-of-squares rule with a smoother, more principled cost: score each plac... |
| 92 | edit | not_better | 0.9927 | 0.9952 | $0.0008 | The current implementation is noisy (the `rank` closure reads `g_ref` from the outer scope incorr... |
| 93 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | The exact sum-of-squares proxy is noisy on this distribution; I'll switch to a cleaner "best-fit ... |
| 94 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The primary sum-of-squares rule is good, but its tie-break is weak. I'll combine it with a strong... |
| 95 | edit | not_better | 0.9474 | 0.9952 | $0.0007 | I'll replace the arbitrary largest-residual tie-break with a tie-break that prefers the placement... |
| 96 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll add a lightweight lookahead-free "residual matching" tie-break: among placements whose sum-o... |
| 97 | edit | not_better | 0.9927 | 0.9952 | $0.0009 | I notice the current `rank` closure is buggy: it reads `g_ref` from the enclosing loop variable i... |
| 98 | edit | not_better | 0.9474 | 0.9952 | $0.0010 | I'll replace the buggy tie-break with a clean, exact sum-of-squares delta rule and, among exact t... |
| 99 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | I'll implement a proper "best-fit decreasing"-style rule combined with sum-of-squares: among fitt... |
| 100 | edit | not_better | 0.6283 | 0.9952 | $0.0006 | I'll replace the scoring with a clean, well-known strong rule: choose the fitting bin that minimi... |
| 101 | edit | not_better | 0.8179 | 0.9952 | $0.0009 | The current rule uses only the sum-of-squares delta; I'll add a principled secondary criterion ba... |
| 102 | edit | not_better | 0.9228 | 0.9952 | $0.0009 | I'll rewrite the rule cleanly with the correct exact sum-of-squares delta as the primary key and,... |
| 103 | edit | not_better | 0.9942 | 0.9952 | $0.0012 | I'll keep the exact integer sum-of-squares delta as the strictly dominant primary key (encoded so... |
| 104 | edit | not_better | 0.8203 | 0.9952 | $0.0009 | The current tie-break "prefer larger residual" is the metacoded rule that produced the best score... |
| 105 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | The current rule's real strength is the sum-of-squares delta with a largest-residual tie-break; I... |
| 106 | edit | not_better | 0.8203 | 0.9952 | $0.0008 | I'll keep the exact sum-of-squares primary key but replace the "largest residual" tie-break with ... |
| 107 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll add a small secondary "best-fit-ish" refinement that is only consulted when sum-of-squares d... |
| 108 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll keep the sum-of-squares primary key and largest-residual tie-break that scored best, but add... |
| 109 | edit | not_better | 0.9942 | 0.9952 | $0.0016 | Replace the largest-residual tie-break with a residual-concentration tie-break (prefer larger N[r... |
| 110 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact sum-of-squares delta as the dominant primary key but change the tie-break fro... |
| 111 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | Add a global best-fit correction: track the best-fit (smallest positive residual) placement among... |
| 112 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the exact sum-of-squares delta as the dominant primary key, but replace the largest-res... |
| 113 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The sum-of-squares primary rule is very strong, but its exact-delta ties are broken by the arbitr... |
| 114 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll make the exact sum-of-squares delta strictly dominant (encoded at a much larger scale) and r... |
| 115 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll change the exact-delta tie-break to a cost proxy that anticipates fragmentation: among exact... |
| 116 | edit | not_better | 0.9942 | 0.9952 | $0.0011 | Among exact sum-of-squares delta ties, prefer the placement whose resulting residual belongs to t... |
| 117 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Break exact sum-of-squares ties using a harmonic/"best-fit-ish" secondary that prefers the smalle... |
| 118 | edit | not_better | 0.9945 | 0.9952 | $0.0014 | Keep the sum-of-squares delta as primary, but add an extra bonus for exact fills (r==0) scaled by... |
| 119 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll replace the exact-delta secondary tie-break with a scaling correction that accounts for futu... |
| 120 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll make the exact-delta secondary tie-break prefer the placement with the largest residual, but... |
| 121 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | Among exact sum-of-squares delta ties, prefer the bin whose resulting residual is closest to the ... |
| 122 | edit | not_better | 0.9647 | 0.9952 | $0.0008 | The current program's own tracking of opened bins via `_caps` is redundant and fragile: the harne... |
| 123 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | I'll keep the sum-of-squares primary rule but switch the exact-delta tie-break from "largest resi... |
| 124 | edit | invalid | 0.0000 | 0.9952 | $0.0010 | I'll simplify and strengthen the delta computation: instead of the fragile `_caps` reconstruction... |
| 125 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The tie-break for exact sum-of-squares-delta ties will now prefer the smallest positive residual ... |
| 126 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Add a speculative look-ahead term: when a placement would leave a residual r, estimate how many f... |
| 127 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll replace the largest-residual tie-break (which effectively lowers to best-fit) with an explic... |
| 128 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The sum-of-squares delta currently compares against the old residual g_ref but ignores that the r... |
| 129 | edit | not_better | 0.4037 | 0.9952 | $0.0008 | I'll replace the pure sum-of-squares objective with a smoother exponential-weight version: score ... |
| 130 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | I'll replace the exact sum-of-squares tie-break (which is fragile and often arbitrary) with a sta... |
| 131 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current code recomputes the fitting-bin list and per-bin counts using a Python loop over `_ca... |
| 132 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I'll replace the fragile sum-of-squares-with-scaled-tie-break encoding (which mixes the primary k... |
| 133 | edit | not_better | 0.9910 | 0.9952 | $0.0009 | I'll switch the primary objective to best-fit-with-a-twist: choose the fitting bin with the small... |
| 134 | edit | not_better | 0.9584 | 0.9952 | $0.0008 | I'll switch the primary rule to best-fit (tightest residual) but only among bins whose residual i... |
| 135 | edit | not_better | 0.9616 | 0.9952 | $0.0010 | Switch the primary objective to best-fit (smallest residual r = g-s, preferring exact fill) and b... |
| 136 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current rule is very good but the sum-of-squares tie-break is fragile and often arbitrary; I'... |
| 137 | edit | not_better | 0.7068 | 0.9952 | $0.0010 | Replace the fragile 1e9-scaled single-float key with an exact lexicographic two-key comparison (p... |
| 138 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The current rule already achieves near-optimal sum-of-squares packing, so I'll keep that primary ... |
| 139 | edit | not_better | 0.6347 | 0.9952 | $0.0009 | The sum-of-squares rule is strong, but its biggest weakness is that it treats size-100 openings n... |
| 140 | edit | not_better | 0.9474 | 0.9952 | $0.0009 | I'll keep the sum-of-squares primary objective (which is near-optimal) but replace the fragile fl... |
| 141 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll add a small tie-break preference for residuals that are least likely to be wasted, by prefer... |
| 142 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I'll replace the fragile float-scaled score key with an exact lexicographic ordering computed in ... |
| 143 | edit | invalid | 0.0000 | 0.9952 | $0.0010 | The current scoring key is rebuilt from scratch with per-call Python loops and a large float mult... |
| 144 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll replace the fragile 1e9-scaled float key with an exact lexicographic comparison by encoding ... |
| 145 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | I'll keep the strong sum-of-squares primary objective but make the tie-break smarter: among place... |
| 146 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The sum-of-squares primary objective treats each open-bin residual equally, but pairing rule qual... |
| 147 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The current rule treats all residual capacities in N[g] equally, but a residual that is very smal... |
| 148 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll add an "exact-fit-plus-avoid-small-residuals" refinement: keep the sum-of-squares primary ob... |
| 149 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll improve the primary objective by replacing the pure sum-of-squares rule with a "best-fit dec... |
| 150 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll refine the tie-break so that among placements with equal sum-of-squares delta, I prefer the ... |
| 151 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The sum-of-squares objective is essentially the right primary rule, but the tie-break should favo... |
| 152 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | I'll keep the sum-of-squares primary rule but change the tie-break among equal deltas to prefer t... |
| 153 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The tie-breaks tried so far all perturb an already-near-optimal objective. Instead, I'll replace ... |
| 154 | edit | not_better | 0.9490 | 0.9952 | $0.0008 | I'll try a completely different, well-known online rule: keep the sum-of-squares objective but re... |
| 155 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Keep the sum-of-squares primary objective, but replace the tie-break with one that prefers the po... |
| 156 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | Replace the maxresidual tie-break with a "prefer the residual that has the largest count N[r] of ... |
| 157 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the sum-of-squares primary rule but change the tie-break to a "Harmonic/H1-style best-f... |
| 158 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | Keep the sum-of-squares primary objective but replace the tie-break with a "best-fit emergency es... |
| 159 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The sum-of-squares rule is a strong "open a new bin only when needed" heuristic, but its tie-brea... |
| 160 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll refine the sum-of-squares objective by using a secondary term that penalizes residuals which... |
| 161 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Add a "close a bin when its residual is exactly a future item size seen historically" incentive: ... |
| 162 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Switch the primary rule from sum-of-squares to best-fit (minimize post-placement residual among f... |
| 163 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Keep the sum-of-squares primary objective but replace the tie-break with "best-fit among the best... |
| 164 | edit | not_better | 0.9517 | 0.9952 | $0.0009 | Replace the fragile NaN-prone/no-op-prone scoring with a cleaner implementation of the sum-of-squ... |
| 165 | edit | invalid | 0.0000 | 0.9952 | $0.0009 | Make the sum-of-squares rule an exact lexicographic comparison by encoding the primary delta and ... |
| 166 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll replace the scoring/tie-break with a cleaner and more robust best-fit decreasing-like greedy... |
| 167 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the fragile delta-plus-residual combined float score with a cleaner exact lexicographic e... |
| 168 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | Meta-optimize the tie-break: instead of forcing one fixed secondary rule, use the sum-of-squares ... |
| 169 | edit | not_better | 0.9927 | 0.9952 | $0.0010 | Rewrite the scoring to use exact integer lexicographic keys (no float scaling), make the new-bin ... |
| 170 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Replace the sum-of-squares primary objective with the "hard" harmonic (cube) score that weights v... |
| 171 | edit | not_better | 0.9522 | 0.9952 | $0.0009 | Replace the sum-of-squares primary objective with a "harmonic-mean residual" (sum of 1/g^2 over o... |
| 172 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the primary objective with the better-performing variant of the sum-of-squares rule: use ... |
| 173 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll implement the classic SUM-OF-SQUARES rule correctly but add a small data-driven preference: ... |
| 174 | edit | not_better | 0.8179 | 0.9952 | $0.0009 | I'll fix a correctness bug: the `rank` closure reads the outer loop variable `g_ref` which is ass... |
| 175 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the sum-of-squares primary objective with the classic "best fit but with the sum-of-squar... |
| 176 | edit | not_better | 0.9940 | 0.9952 | $0.0008 | The current implementation uses sum-of-squares deltas but scales them by 1e9 for tie-breaking whi... |
| 177 | edit | not_better | 0.9642 | 0.9952 | $0.0009 | The current rule ignores that the harness includes all unused bins (capacity 100) in the array; t... |
| 178 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The current rule uses the sum-of-squares primary objective but breaks exact-delta ties by the lar... |
| 179 | edit | not_better | 0.8179 | 0.9952 | $0.0009 | I'll change the exact-delta tie-break from "largest residual" to "smallest sufficient residual" (... |
| 180 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | I will replace the fragile, histogram-based sum-of-squares rule with a hybrid: primary key is the... |
| 181 | edit | not_better | 0.9526 | 0.9952 | $0.0011 | Add the exact symmetric sum-of-squares handling for the new-bin case by including N[CAP] (the poo... |
| 182 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll remove the 1e9 float-based lexicographic encoding and replace it with exact integer keys com... |
| 183 | edit | not_better | 0.8179 | 0.9952 | $0.0010 | I'll keep the sum-of-squares delta as the primary key but change the tie-break to prefer the bin ... |
| 184 | edit | not_better | 0.7657 | 0.9952 | $0.0030 | I'll generalize the "largest residual" tie-break into a tolerance band: instead of only breaking ... |
| 185 | edit | invalid | 0.0000 | 0.9952 | $0.0028 | The current SS delta for opening a new bin ignores that unused bins behave like residuals of CAP ... |
| 186 | edit | not_better | 0.9616 | 0.9952 | $0.0006 | I'll replace the sum-of-squares histogram objective with a hybrid best-fit rule that adds a "perf... |
| 187 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | I will add a small best-fit secondary preference within the sum-of-squares framework: when severa... |
| 188 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the fragile float-based lexicographic encoding (delta * 1e9 + residual) with a safe, exac... |
| 189 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Add a light "perfect-fit" bonus to the sum-of-squares rule: when a placement would leave a residu... |
| 190 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the sum-of-squares delta as the primary key but replace the "largest residual" tie-brea... |
| 191 | edit | invalid | 0.0000 | 0.9952 | $0.0009 | Replace the sum-of-squares primary with a hybrid: keep the sum-of-squares delta as primary but ad... |
| 192 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | Simplify to a pure best-fit-decreasing-like rule with a tie-break that prefers a perfect fill (re... |
| 193 | edit | not_better | 0.7209 | 0.9952 | $0.0010 | I'll replace the sum-of-squares primary key with a harmonic (1/(r+1)) residual-utility objective ... |
| 194 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | Add a small secondary term to the sum-of-squares objective that rewards placements where the new ... |
| 195 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | I'll switch the tie-break from "largest residual" to a heuristic that prefers a post-placement re... |
| 196 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll sweep the tie-break exponent by replacing the exact "largest-residual" secondary key with a ... |
| 197 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the tie-break with a two-tier rule: prefer the smallest post-placement residual (best-fit... |
| 198 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The "sum-of-squares" (Stein's) rule minimizes sum N(g)^2 greedily but treats unused-bin opens nai... |
| 199 | edit | not_better | 0.9950 | 0.9952 | $0.0015 | Keep the sum-of-squares delta as the exact primary key, but change the tie-break to a three-tier ... |
| 200 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The sum-of-squares rule's weakness is how it handles opening new bins and near-full bins; I'll ad... |
| 201 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the largest-residual secondary key with a term that rewards resulting residuals close to ... |
| 202 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll replace the fragile integer-encoded tie-break (which can overflow/round float64 precision at... |
| 203 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | I'll replace the sum-of-squares primary rule with the classic "best-fit / tightest residual" rule... |
| 204 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Add a "best-fit among equal-delta" secondary tie-break: keep the exact sum-of-squares delta as pr... |
| 205 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the flat float-encoded tie-break (which can lose precision at 1e9 scale) with an explicit... |
| 206 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I'll keep the exact sum-of-squares delta as the primary criterion (preserving the proven Stein ob... |
| 207 | edit | not_better | 0.9508 | 0.9952 | $0.0009 | I'll replace the "largest residual" tie-break with one that prefers placing the item so the resul... |
| 208 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact sum-of-squares delta as the primary criterion but add a small secondary bias ... |
| 209 | edit | not_better | 0.7084 | 0.9952 | $0.0009 | I will replace the score encoding with a proper lexicographic argmax over the exact integer sum-o... |
| 210 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The current score encoding gives unused bins a launch value of `-delta_new*1e9 + r_new`, but the ... |
| 211 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the proven sum-of-squares primary rule, but replace the simple "largest residual" tie-break ... |
| 212 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The sum-of-squares rule currently only considers exact-delta as primary; I'll add a genuine secon... |
| 213 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The sum-of-squares rule's primary criterion is preserved, but I will remove the fragile float bas... |
| 214 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Keep the exact sum-of-squares delta as the primary criterion, but change the tie-break to prefer ... |
| 215 | edit | invalid | 0.0000 | 0.9952 | $0.0008 | I'll remove the extra bookkeeping overhead and unused `rank` closure by replacing the scoring loo... |
| 216 | edit | not_better | 0.4081 | 0.9952 | $0.0008 | Replace the global bin bookkeeping with a direct computation from the `bins` array: the sum-of-sq... |
| 217 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Replace the "largest residual" tie-break with a "smallest residual" tie-break (classic best-fit t... |
| 218 | edit | invalid | 0.0000 | 0.9952 | $0.0011 | Replace the exact-delta sum-of-squares scoring with a smoothed version that breaks exact-delta ti... |
| 219 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the proven sum-of-squares delta as the primary criterion, but change the exact-delta tie-bre... |
| 220 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | Replace the "largest residual" tie-break with a tie-break that prefers leaving the residual that ... |
| 221 | edit | not_better | 0.8183 | 0.9952 | $0.0009 | The current rule ignores how often each item size actually occurs. I will keep the proven sum-of-... |
| 222 | edit | not_better | 0.9357 | 0.9952 | $0.0006 | I will replace the sum-of-squares primary criterion with the classic "best fit" rule expressed as... |
| 223 | edit | not_better | 0.8203 | 0.9952 | $0.0009 | I'll keep the sum-of-squares primary criterion but change the exact-delta tie-break: instead of "... |
| 224 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Keep the sum-of-squares primary criterion, but replace the exact-delta tie-break with one that pr... |
| 225 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Keep the sum-of-squares primary criterion but replace the exact-delta tie-break: among placements... |
| 226 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The current "largest residual" tie-break is arbitrary for the sum-of-squares rule; for a best-fit... |
| 227 | edit | not_better | 0.9614 | 0.9952 | $0.0009 | I'll replace the sum-of-squares rule with the classic harmonic-matching bin-choice rule: score ea... |
| 228 | edit | not_better | 0.9490 | 0.9952 | $0.0010 | The sum-of-squares rule's weakest point is its treatment of exact-delta ties; the current "larges... |
| 229 | edit | not_better | 0.9942 | 0.9952 | $0.0011 | Keep the sum-of-squares primary criterion (which correctly balances opening new bins vs. filling ... |
| 230 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Keep the sum-of-squares primary criterion, but make the exact-delta tie-break deterministic and w... |
| 231 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll make the exact-delta tie-break adaptive: prefer the largest residual (current best behavior ... |
| 232 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | Add a bounded, self-adaptive weight to the sum-of-squares criterion that penalizes leaving residu... |
| 233 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Replace the delta-based sum-of-squares rule with a direct "Sum of Squares" scoring that subtracts... |
| 234 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Introduce a tiny, deterministic tie-break continuation for exact-delta ties that prefers the plac... |
| 235 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll improve the sum-of-squares rule by adding a small, positive weight on the residual's complem... |
| 236 | edit | not_better | 0.9932 | 0.9952 | $0.0009 | The current code has a subtle bug: it scores only bins from its own `_caps` record, but the harne... |
| 237 | edit | not_better | 0.7260 | 0.9952 | $0.0010 | Replace the sum-of-squares primary criterion with a "match the residual to likely future items" r... |
| 238 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll replace the fragile 1e9-weighted float encoding with a clean lexicographic selection: first ... |
| 239 | edit | not_better | 0.9932 | 0.9952 | $0.0010 | The previous exact-delta sum-of-squares formulation is flawed: minimizing Δ(ΣN²) is not the same ... |
| 240 | edit | not_better | 0.6347 | 0.9952 | $0.0009 | The current sum-of-squares rule is essentially Best-Fit, but a well-known better online rule is t... |
| 241 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Adopt a never-before-tried classic: the "Least-Loaded / Worst-Fit" alternative is worse, but a ge... |
| 242 | edit | not_better | 0.9623 | 0.9952 | $0.0008 | The current code has a correctness bug: it builds `fitting` from its own `_caps` record and maps ... |
| 243 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll tune the tie-break to prefer placing an item so that the resulting residual is a value that ... |
| 244 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary criterion but replace the "largest residual" tie-brea... |
| 245 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | The current code has a mismatch bug: `scores` is indexed by `k` (position within `fitting`) but t... |
| 246 | edit | not_better | 0.9593 | 0.9952 | $0.0009 | The current rule is essentially Best-Fit with a sum-of-squares tiebreak, but it ignores the actua... |
| 247 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will replace the sum-of-squares primary criterion with the classic "Best-Fit" combined with a t... |
| 248 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Replace the sum-of-squares ranking with the proven "Best-Fit with a residual-count tie-break": pr... |
| 249 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current best rule is "sum-of-squares" (SS), which is equivalent to Best-Fit here because it m... |
| 250 | edit | not_better | 0.6347 | 0.9952 | $0.0008 | The scoring loop indexes `scores[k]` by position within `fitting` but should place each score at ... |
| 251 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Add a lightweight "aging"/lookahead tie-break: among placements with identical sum-of-squares del... |
| 252 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I'll keep the proven sum-of-squares primary criterion but replace the tie-break with one that pre... |
| 253 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Replace the sum-of-squares primary with a proper Best-Fit primary computed from the actual `bins`... |
| 254 | edit | not_better | 0.9549 | 0.9952 | $0.0008 | The current sum-of-squares rule is effectively Best-Fit, whose known weakness is that it fragment... |
| 255 | edit | not_better | 0.9935 | 0.9952 | $0.0009 | The current rule is sum-of-squares (best-fit), which is strong but known to fragment. I will add ... |
| 256 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary criterion but replace the tie-break with a "least-fra... |
| 257 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll keep the sum-of-squares primary (Best-Fit) but change the tie-break to prefer the placement ... |
| 258 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | The score encoding via `*1e9 + r` is fragile and the fitting order may not match `bins` positions... |
| 259 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | Replace the fragile `key[0]*1e9 + key[1]` float encoding (which can misorder when deltas are larg... |
| 260 | edit | not_better | 0.6347 | 0.9952 | $0.0009 | The current rule is essentially Best-Fit, which is known to be strong here; I'll keep the exact s... |
| 261 | edit | not_better | 0.9152 | 0.9952 | $0.0011 | I'll replace the exact-delta best-fit primary with a "Best-Fit with a steering term" that breaks ... |
| 262 | edit | not_better | 0.9952 | 0.9952 | $0.0012 | I'll keep the exact sum-of-squares delta as the primary criterion (the proven strong Best-Fit bas... |
| 263 | edit | not_better | 0.9952 | 0.9952 | $0.0007 | Replace the best-fit (sum-of-squares) primary with a proper online "Sum-of-Squares" rule that min... |
| 264 | edit | not_better | 0.4081 | 0.9952 | $0.0010 | I will replace the pure Best-Fit primary rule with the classic Sum-of-Squares heuristic derived d... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,11 +1,14 @@
 # EVOLVE-BLOCK-START
-"""Starting program: the Sum-of-Squares rule.
+"""Sum-of-Squares rule with largest-residual tie-breaking.
 
-Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining capacity g
-(0 < g < 100); ties go to the tighter fit. The function is shown only the bins the item fits in, so it
-keeps its own record of every opened bin. The harness opens unused bins in index order (ties go to the
-first bin), so used bins are always a prefix of the bin array. Each instance runs in a fresh process,
-so the module-level state starts empty for every instance.
+Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining
+capacity g (0 < g < 100). Exact-delta ties are broken by preferring the placement that
+leaves the largest post-placement residual, which keeps more usable free space available
+for future items.
+The function is shown only the bins the item fits in, so it keeps its own record of every
+opened bin. Used bins are always a prefix of the bin array (harness opens unused bins in
+index order and ties go to the first bin). Each instance runs in a fresh process, so the
+module-level state starts empty for every instance.
 """
 import numpy as np
 
@@ -15,27 +18,36 @@
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
-
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
     global _caps, _N
     s = int(item)
+    n_bins = len(bins)
     fitting = [j for j, g in enumerate(_caps) if g >= s]
-    n_unused = len(bins) - len(fitting)
-    scores = np.empty(len(bins), dtype=np.float64)
+    n_unused = n_bins - len(fitting)
+    scores = np.empty(n_bins, dtype=np.float64)
+
+    def rank(r):
+        if r > 0:
+            delta = -2 * _N[g_ref] + 1 + (2 * _N[r] + 1)
+        else:
+            delta = -2 * _N[g_ref] + 1
+        return (-delta, r)
+
     for k, j in enumerate(fitting):
-        g = _caps[j]
-        r = g - s
-        delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)
-        scores[k] = -(delta * 1000 + r)
+        g_ref = _caps[j]
+        r = g_ref - s
+        key = rank(r)
+        scores[k] = key[0] * 1e9 + key[1]
+
     r_new = CAP - s
-    delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
-    scores[len(fitting):] = -(delta_new * 1000 + r_new)
+    g_ref = CAP
+    if r_new > 0:
+        delta_new = 2 * _N[r_new] + 1
+    else:
+        delta_new = 0
+    scores[len(fitting):] = -delta_new * 1e9 + r_new
 
-    choice = int(np.argmax(scores))          # the harness's choice: first highest score
+    choice = int(np.argmax(scores))
     if choice < len(fitting):
         j = fitting[choice]
         g = _caps[j]
```

## Explanation

Two-sided ablation of `priority` (52 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 23 | `s = int(item)` | -0.9952 | essential: the program fails or turns invalid without it |
| 24 | `n_bins = len(bins)` | -0.9952 | essential: the program fails or turns invalid without it |
| 25 | `fitting = [j for j, g in enumerate(_caps) if g >= s]` | -0.9952 | essential: the program fails or turns invalid without it |
| 26 | `n_unused = n_bins - len(fitting)` | -0.9952 | essential: the program fails or turns invalid without it |
| 27 | `scores = np.empty(n_bins, dtype=np.float64)` | -0.9952 | essential: the program fails or turns invalid without it |
| 29 | `def rank(r): ...` | -0.9952 | essential: the program fails or turns invalid without it |
| 30 | `if r > 0: ...` | -0.9952 | essential: the program fails or turns invalid without it |
| 31 | `delta = -2 * _N[g_ref] + 1 + (2 * _N[r] + 1)` | -0.9952 | essential: the program fails or turns invalid without it |
| 33 | `delta = -2 * _N[g_ref] + 1` | -0.9952 | essential: the program fails or turns invalid without it |
| 36 | `for k, j in enumerate(fitting): ...` | -0.9952 | essential: the program fails or turns invalid without it |
| 37 | `g_ref = _caps[j]` | -0.9952 | essential: the program fails or turns invalid without it |
| 38 | `r = g_ref - s` | -0.9952 | essential: the program fails or turns invalid without it |
| 39 | `key = rank(r)` | -0.9952 | essential: the program fails or turns invalid without it |
| 40 | `scores[k] = key[0] * 1000000000.0 + key[1]` | -0.9952 | essential: the program fails or turns invalid without it |
| 42 | `r_new = CAP - s` | -0.9952 | essential: the program fails or turns invalid without it |
| 44 | `if r_new > 0: ...` | -0.9952 | essential: the program fails or turns invalid without it |
| 45 | `delta_new = 2 * _N[r_new] + 1` | -0.9952 | essential: the program fails or turns invalid without it |
| 48 | `scores[len(fitting):] = -delta_new * 1000000000.0 + r_new` | -0.9952 | essential: the program fails or turns invalid without it |
| 50 | `choice = int(np.argmax(scores))` | -0.9952 | essential: the program fails or turns invalid without it |
| 38 | `term - s` | -0.2292 | matters |
| 40 | `term + key[0] * 1000000000.0` | -0.1105 | matters |
| 31 | `term + 2 * _N[r] + 1` | -0.0415 | matters |
| 38 | `term + g_ref` | -0.0364 | matters |
| 26 | `term + n_bins` | -0.0359 | matters |
| 33 | `term + -2 * _N[g_ref]` | -0.0167 | matters |
| 48 | `term + -delta_new * 1000000000.0` | -0.0062 | matters |
| 31 | `term + 1` | -0.0025 | matters |
| 31 | `term + -2 * _N[g_ref]` | -0.0020 | no effect alone |
| 45 | `term + 1` | -0.0015 | no effect alone |
| 40 | `term + key[1]` | -0.0012 | no effect alone |
| 42 | `term + CAP` | -0.0008 | no effect alone |
| 42 | `term - s` | -0.0008 | no effect alone |
| 45 | `term + 2 * _N[r_new]` | -0.0008 | no effect alone |
| 26 | `term - len(fitting)` | +0.0000 | no effect alone |
| 33 | `term + 1` | +0.0000 | no effect alone |
| 43 | `g_ref = CAP` | +0.0000 | no effect alone |
| 47 | `delta_new = 0` | +0.0000 | no effect alone |
| 48 | `term + r_new` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 22: `global _caps, _N`

Not tested (evaluation limit 40): 13 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9952 | 0.9947 |
| minimal (1 parts removed) | 0.9952 | 0.9947 |

Minimal program:

```python
"""Sum-of-Squares rule with largest-residual tie-breaking.

Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining
capacity g (0 < g < 100). Exact-delta ties are broken by preferring the placement that
leaves the largest post-placement residual, which keeps more usable free space available
for future items.
The function is shown only the bins the item fits in, so it keeps its own record of every
opened bin. Used bins are always a prefix of the bin array (harness opens unused bins in
index order and ties go to the first bin). Each instance runs in a fresh process, so the
module-level state starts empty for every instance.
"""
import numpy as np
CAP = 100
_caps = []
_N = [0] * (CAP + 1)

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    s = int(item)
    n_bins = len(bins)
    fitting = [j for j, g in enumerate(_caps) if g >= s]
    n_unused = n_bins - len(fitting)
    scores = np.empty(n_bins, dtype=np.float64)

    def rank(r):
        if r > 0:
            delta = -2 * _N[g_ref] + 1 + (2 * _N[r] + 1)
        else:
            delta = -2 * _N[g_ref] + 1
        return (-delta, r)
    for k, j in enumerate(fitting):
        g_ref = _caps[j]
        r = g_ref - s
        key = rank(r)
        scores[k] = key[0] * 1000000000.0 + key[1]
    r_new = CAP - s
    g_ref = CAP
    if r_new > 0:
        delta_new = 2 * _N[r_new] + 1
    else:
        delta_new = 0
    scores[len(fitting):] = -delta_new * 1000000000.0 + r_new
    choice = int(np.argmax(scores))
    if choice < len(fitting):
        j = fitting[choice]
        g = _caps[j]
        _N[g] -= 1
        _caps[j] = g - s
        if g - s > 0:
            _N[g - s] += 1
    elif n_unused > 0:
        _caps.append(CAP - s)
        if CAP - s > 0:
            _N[CAP - s] += 1
    return scores
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online_ss --budget 0.6 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 2
python -m autoresearch.loop --report experiments/llm-from-ss-v1/runs/s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `1c6bc8836f41e628e06a15cfae8d46a881e347f7`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bin_packing_online_ss/evaluate.py` `0ac9a4a253a299d2`
- `problems/bin_packing_online_ss/initial.py` `15a169ab98ab0da1`
- `problems/bin_packing_online_ss/problem.md` `aa1aa4a2d6d00d6a`
- `problems/bin_packing_online_ss/verify.py` `b3ea67a1c6f94885`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
