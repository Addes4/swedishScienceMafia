# Research loop report: bin_packing_online_ss

| | |
|---|---|
| problem | `bin_packing_online_ss` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2687 of a $0.60 hard cap, 300 calls, 824,012 tokens |
| wall time | search 5306 s, baselines 14 s, explain 127 s |
| stopped | max_iters (stopped_early) |
| evaluations | 301 (294 valid), 3 improvements accepted |

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
| 1 | edit | improved | 0.9942 | 0.9942 | $0.0008 | Add a mild penalty for creating very small residuals (which often go unused), by subtracting a sm... |
| 2 | edit | improved | 0.9945 | 0.9945 | $0.0007 | Add a tunable penalty on the *magnitude* of the residual (proportional to residual size times a s... |
| 3 | edit | not_better | 0.9942 | 0.9945 | $0.0008 | Replace the crude tiny-residual step penalty with a smoother, distribution-aware "waste acceptabi... |
| 4 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | Replace the hand-tuned penalty with a proper expected-waste estimate: track the empirical distrib... |
| 5 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | Replace the hardcoded residual penalty with a hybrid that keeps the sum-of-squares choice but adj... |
| 6 | edit | not_better | 0.9945 | 0.9945 | $0.0008 | Add a "best-fit" tiebreaker inside the existing sum-of-squares rule: when two candidate residuals... |
| 7 | edit | not_better | 0.8179 | 0.9945 | $0.0008 | Replace the hand-tuned penalty with the classic "best-fit decreasing"-style tiebreak: keep the st... |
| 8 | edit | not_better | 0.9945 | 0.9945 | $0.0010 | Replace the residual-size tiebreaker with a smoothed "acceptability" tiebreak: among candidates w... |
| 9 | edit | not_better | 0.9942 | 0.9945 | $0.0008 | Replace the arbitrary residual penalty with a simple, well-scaled "best-fit" secondary term: nega... |
| 10 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | Replace the hard-coded residual penalty with an adaptive one based on the empirical item-size dis... |
| 11 | edit | not_better | 0.9945 | 0.9945 | $0.0009 | Scale the sum-of-squares scoring weight with the item size, so that placing a large item into a b... |
| 12 | edit | not_better | 0.9945 | 0.9945 | $0.0010 | I will add a light "perfect-fit avoidance" refinement: because the sum-of-squares rule already fa... |
| 13 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | Replace the fixed tiny-residual penalty with a residual-value function derived from the empirical... |
| 14 | edit | not_better | 0.9945 | 0.9945 | $0.0009 | Replace the sum-of-squares primary rule with a "best-fit with randomized/among-ties preference fo... |
| 15 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | I will keep the strong sum-of-squares primary rule but make the tiny-residual penalty conditional... |
| 16 | edit | not_better | 0.9616 | 0.9945 | $0.0007 | I will replace the current rule with the classic "best-fit decreasing-style" heuristic: among all... |
| 17 | edit | not_better | 0.9616 | 0.9945 | $0.0008 | I'll replace the sum-of-squares primary rule with the "best-fit" rule augmented by a small "resid... |
| 18 | edit | not_better | 0.9616 | 0.9945 | $0.0008 | I will replace the sum-of-squares primary rule with a "best-fit with deferred exact-fit matching"... |
| 19 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | I will replace the fixed tiny-residual penalty with a size-aware one: the penalty for leaving a v... |
| 20 | edit | not_better | 0.9945 | 0.9945 | $0.0010 | I will replace the hand-tuned residual penalty with a principled "future-fit value" term: instead... |
| 21 | edit | not_better | 0.9945 | 0.9945 | $0.0009 | I will keep the sum-of-squares primary rule but reduce the penalty scale so it stays well below t... |
| 22 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | I will keep the sum-of-squares ranking but make the within-tie preference aim for residuals that ... |
| 23 | edit | not_better | 0.9942 | 0.9945 | $0.0009 | The published "sum of squares" rule is near-optimal but its tiebreaker currently prefers the tigh... |
| 24 | edit | not_better | 0.9945 | 0.9945 | $0.0009 | I will switch the primary objective from the pure sum-of-squares rule to a size-aware hybrid: kee... |
| 25 | edit | not_better | 0.9942 | 0.9945 | $0.0011 | I'll remove the hand-tuned residual penalty entirely so the score is the pure sum-of-squares obje... |
| 26 | edit | improved | 0.9952 | 0.9952 | $0.0009 | I will flip the within-tie tiebreaker from tightest-fit to loosest-fit: among bins with equal sum... |
| 27 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Make the tiebreaker strictly lexicographic by encoding delta in a high-precision way and separati... |
| 28 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I will make the ranking strictly lexicographic via explicit tiered encoding: primary = sum-of-squ... |
| 29 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I will keep the sum-of-squares primary objective and loosest-fit tiebreak, but add an intermediat... |
| 30 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will replace the pure sum-of-squares objective with the best-fit decreasing-inspired "best fit"... |
| 31 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will replace the pure sum-of-squares delta with a blended objective that adds a small expected-... |
| 32 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I'll add a lightweight online histogram of recent item sizes and, among sum-of-squares ties, pref... |
| 33 | edit | not_better | 0.9937 | 0.9952 | $0.0010 | I will change the tiebreaker among exact sum-of-squares ties to prefer the bin whose residual is ... |
| 34 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | I will add a learned "best fit" tiebreaker: among exact sum-of-squares ties, prefer the bin whose... |
| 35 | edit | not_better | 0.9418 | 0.9952 | $0.0009 | I'll replace the sum-of-squares objective with the online "best fit" rule that considers only res... |
| 36 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | The current tiebreaker (prefer largest residual) undermines tight consolidation. I will change it... |
| 37 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | I will replace the exact sum-of-squares objective with the classic best-fit rule (choose the bin ... |
| 38 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The tiebreaker will prefer the largest residual only among bins whose residual is at least the ma... |
| 39 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | The current rule already uses the optimal quadratic potential; I will keep it but change the tieb... |
| 40 | edit | not_better | 0.9593 | 0.9952 | $0.0007 | I will keep the sum-of-squares rule but change the tie-break: instead of preferring the largest r... |
| 41 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Keep the sum-of-squares objective exactly, but flip the tiebreaker to prefer the smallest resulti... |
| 42 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Keep the sum-of-squares objective and its loosest-fit tiebreaker, but add a small perturbation ba... |
| 43 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The sum-of-squares rule can be improved by using the residual-count difference more accurately: i... |
| 44 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares objective but make the tie-breaker choose the bin whose resi... |
| 45 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Use the exact best-fit-decreasing-style "match largest possible exact fit" rule: replace the sum-... |
| 46 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Add a learned item-size histogram and give a small bonus to bins whose resulting residual is a si... |
| 47 | edit | not_better | 0.9940 | 0.9952 | $0.0008 | I will keep the exact sum-of-squares objective as the primary term but refine the tiebreaker: amo... |
| 48 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The sum-of-squares delta is currently approximated by the marginal change; I will replace it with... |
| 49 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I will replace the myopic sum-of-squares delta with a lookahead that also values keeping at least... |
| 50 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Add an explicit "exact-fit" bonus on top of the sum-of-squares objective: give a large positive b... |
| 51 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | The current exact sum-of-squares delta is a strict greedy criterion but ignores the "future" bene... |
| 52 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will replace the approximate marginal delta with the true exact change in sum-of-squares that a... |
| 53 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Change the tiebreaker from loosest-fit (largest residual) to best-fit (smallest residual), which ... |
| 54 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will add a learned "small-residual avoidance" tiebreaker: keep the exact sum-of-squares delta a... |
| 55 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | I will switch the primary criterion to the classic "best-fit" rule combined with sum-of-squares: ... |
| 56 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The current rule minimizes the exact sum-of-squares delta but uses a weak additive tiebreaker. I'... |
| 57 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | I'll keep the exact sum-of-squares delta as the primary criterion but add a moderate reward for c... |
| 58 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreaker with a data-driven one: among bins tied on the exact sum-of-sq... |
| 59 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Combine the sum-of-squares primary objective with a "best-fit-like" residual preference that spec... |
| 60 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will replace the sum-of-squares ranking with the "best-fit with a capacity-gap penalty" rule: a... |
| 61 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll implement the "Sum of Squares" rule exactly but replace the weak scaled tiebreaker with a pr... |
| 62 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will replace the ad-hoc scaled tiebreaker with a true lexicographic score: encode the exact sum... |
| 63 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | I'll replace the loosest-fit tiebreaker with a "fractional-fit" tiebreaker that prefers the resid... |
| 64 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The sum-of-squares objective is near-optimal but the simple scaled tiebreaker weakly favors loose... |
| 65 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | I will replace the sum-of-squares rule with the classic "Best Fit Decreasing + fallback" competit... |
| 66 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I will switch the primary rule from exact sum-of-squares to a lexicographic objective that first ... |
| 67 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The scaled tiebreaker can distort the exact sum-of-squares delta, so I will make the comparison t... |
| 68 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the sum-of-squares "spread" rule with a hybrid: primary key remains the exact sum-of-squa... |
| 69 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Add a warm-up phase: for the first few items, use a Best-Fit-Decreasing-like rule based on a prec... |
| 70 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The current scaled tiebreaker leaves a subtle issue: among exact sum-of-squares ties it prefers t... |
| 71 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll replace the sum-of-squares delta with an exact "pair-and-residual packing" heuristic: primar... |
| 72 | edit | not_better | 0.9940 | 0.9952 | $0.0008 | The sum-of-squares rule is essentially the right primary objective, but the scaled tiebreaker can... |
| 73 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The sum-of-squares rule is near-optimal, but its tiebreaker is arbitrary; I will switch the tiebr... |
| 74 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Use a true lexicographic ordering by making the sum-of-squares delta the primary key with a large... |
| 75 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The current tiebreaker sorts by primary delta time a large multiplier, but `_N[r]` for the residu... |
| 76 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | Replace the fragile scaled tiebreaker with a proper lexicographic key, and make the tiebreaker re... |
| 77 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll replace the arbitrary/tuned tiebreaker with a principled one based on the actual objective: ... |
| 78 | edit | not_better | 0.9940 | 0.9952 | $0.0010 | I'll add a small look-ahead correction to the sum-of-squares primary objective that accounts for ... |
| 79 | edit | invalid | 0.0000 | 0.9952 | $0.0008 | I'll switch the primary rule from sum-of-squares to the well-known "best fit with a capacity-awar... |
| 80 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The tiebreaker in the current winning version scales delta by 1000, which can overflow into the r... |
| 81 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The primary sum-of-squares objective stays exact via integer deltas, but I replace the arbitrary ... |
| 82 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the exact integer sum-of-squares primary objective, but replace the loosest-fit secondary by... |
| 83 | edit | not_better | 0.6283 | 0.9952 | $0.0007 | Replace the sum-of-squares rule with the classic "best fit decreasing-like" greedy that instead m... |
| 84 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll add a lightweight residual-pairing lookahead: keep the exact integer sum-of-squares primary ... |
| 85 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact integer sum-of-squares primary objective but change the tiebreaker to favor t... |
| 86 | edit | invalid | 0.0000 | 0.9952 | $0.0010 | I will add a bounded, self-adapting lookahead that breaks exact sum-of-squares ties using the rec... |
| 87 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Keep the exact integer sum-of-squares primary objective, but replace the arbitrary loosest-fit ti... |
| 88 | edit | not_better | 0.8179 | 0.9952 | $0.0008 | The tiebreaker currently breaks exact sum-of-squares ties by preferring larger residuals, which w... |
| 89 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreaker with one that prefers the candidate residual that maximizes th... |
| 90 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will replace the loosest-fit tiebreaker with an exact triple-based tiebreaker: among equal sum-... |
| 91 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the exact sum-of-squares primary objective, but replace the arbitrary loosest-fit tiebreaker... |
| 92 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The exact sum-of-squares rule has ties that matter; since the item sizes come from a fixed smooth... |
| 93 | edit | not_better | 0.9940 | 0.9952 | $0.0010 | Keep the exact integer sum-of-squares primary objective, but change the tiebreaker so that among ... |
| 94 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll replace the arbitrary loosest-fit tiebreaker with a bounded lookahead: among equal sum-of-sq... |
| 95 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | The primary objective currently uses the exact sum-of-squares delta, but many exact ties occur; I... |
| 96 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Replace the exact sum-of-squares objective with a sum-of-squares objective weighted by the recent... |
| 97 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Refine the tiebreaker: among equal sum-of-squares deltas, prefer the placement whose residual is ... |
| 98 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Among equal sum-of-squares deltas, switch the tiebreaker from loosest fit to best fit (prefer the... |
| 99 | edit | not_better | 0.9593 | 0.9952 | $0.0009 | The tiebreaker choice between loosest-fit and best-fit among equal sum-of-squares deltas is a coi... |
| 100 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I'll replace the tiebreaker with a windowed/aging sum-of-squares: instead of counting all open bi... |
| 101 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Recompute the sum-of-squares primary objective's tiebreaker to be a genuine "best fit" via residu... |
| 102 | edit | not_better | 0.9616 | 0.9952 | $0.0005 | Switch the primary objective from sum-of-squares to a "best fit" rule that maximizes the residual... |
| 103 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Replace the exact sum-of-squares objective with an exponential (softly-weighted) score: rank each... |
| 104 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Add a "reserve for big items" term: when the arriving item is small, mildly prefer bins whose res... |
| 105 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll change the primary objective to a smooth combination: minimize sum-of-squares delta plus a s... |
| 106 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Replace the fixed loosest-fit tiebreaker with one that prefers leaving a residual that matches a ... |
| 107 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | The sum-of-squares rule is essentially tied with alternatives, so I'll instead switch the primary... |
| 108 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The sum-of-squares rule is already near-optimal, so I'll add a mild "perfect-fit / near-perfect" ... |
| 109 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll use a score dominated by sum-of-squares (with a larger multiplier to make it the true primar... |
| 110 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The sum-of-squares delta is exact and ties abound; I'll keep it as primary but break ties with a ... |
| 111 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreaker (largest residual) with best-fit tiebreaking (smallest nonzero... |
| 112 | edit | not_better | 0.6283 | 0.9952 | $0.0008 | Replace the sum-of-squares primary objective with a direct linear score on the resulting residual... |
| 113 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Keep the sum-of-squares primary objective, but replace the heuristic loosest-fit tiebreaker with ... |
| 114 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the exact sum-of-squares delta primary objective with a fractional/soft version: score bi... |
| 115 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Keep the sum-of-squares delta as primary, but add a strong (yet bounded) bonus for placements tha... |
| 116 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact sum-of-squares delta as the primary objective (it is the key near-optimal ter... |
| 117 | edit | not_better | 0.9893 | 0.9952 | $0.0012 | I will keep the exact sum-of-squares primary, but replace the simple loosest-fit tiebreaker with ... |
| 118 | edit | invalid | 0.0000 | 0.9952 | $0.0013 | I will replace the heuristic tiebreakers with an exact one-step lookahead over the sum-of-squares... |
| 119 | edit | not_better | 0.9952 | 0.9952 | $0.0017 | Keep the exact sum-of-squares primary objective (which already proved best) but refine the tiebre... |
| 120 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The current best uses sum-of-squares with a loosest-fit tiebreak; I'll try reversing the tiebreak... |
| 121 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll replace the loosest-fit tiebreaker with a "match residual to bin population" heuristic: amon... |
| 122 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll replace the sum-of-squares primary objective with the "difference of squares" rule that dire... |
| 123 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | Replace the primary objective with a weighted "best-fit-compatible" score that balances sum-of-sq... |
| 124 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The current best uses sum-of-squares with a loosest-fit tiebreak, but that spreads load without e... |
| 125 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I will keep the exact sum-of-squares primary objective (tracking N[g] counts), but replace the si... |
| 126 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll switch the primary objective to score placements by the negative change in the sum of square... |
| 127 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll keep the exact sum-of-squares primary objective but change the tiebreak to a "best-fit that ... |
| 128 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | I'll replace the sum-of-squares rule with the classic "best fit decreasing"-style choice expresse... |
| 129 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Keep the sum-of-squares primary objective but replace the loosest-fit tiebreaker with a residual-... |
| 130 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Add a light "practice-mode" counterfactual tiebreak: among placements with equal sum-of-squares d... |
| 131 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll strengthen the sum-of-squares primary objective by adding a small bonus term that rewards pl... |
| 132 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll keep the sum-of-squares primary objective but replace the loosest-fit tiebreaker with a best... |
| 133 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the exact sum-of-squares primary objective and loosest-fit tiebreak, but add a distinct mode... |
| 134 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary objective and loosest-fit tiebreak, but add a small s... |
| 135 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I will keep the sum-of-squares objective and loosest-fit tiebreak, but add a bonus for placements... |
| 136 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Keep the exact sum-of-squares (SOS) primary objective, but replace the loosest-fit tiebreaker wit... |
| 137 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will keep the proven sum-of-squares primary objective and loosest-fit tiebreak, but add a "clos... |
| 138 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I will replace the pure loosest-fit tiebreak with a "least-small-residual / best-fit" tiebreak on... |
| 139 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreaker with a "prefer closing / best-fit" tiebreaker on exact SOS tie... |
| 140 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | I will keep the proven sum-of-squares primary objective, but replace the pure loosest-fit tiebrea... |
| 141 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | I will keep the proven sum-of-squares primary objective, but instead of loosest-fit on exact SOS ... |
| 142 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Keep the sum-of-squares objective, but make exact-fill a strongly dominant secondary term: among ... |
| 143 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will keep the sum-of-squares population objective but replace the loosest-fit tiebreak with a t... |
| 144 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I will keep the proven sum-of-squares primary objective and the loosest-fit tiebreak, but add a s... |
| 145 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Replace the loosest-fit tiebreak with a best-fit tiebreak (smallest nonzero residual, with residu... |
| 146 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | I will refine the tiebreak by preferring the largest residual that is still less than or equal to... |
| 147 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll replace the pure loosest-fit tiebreak with a hybrid: keep the SOS primary objective, but bre... |
| 148 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The current tiebreak budget is likely fine, but the main SOS objective ignores a crucial asymmetr... |
| 149 | edit | not_better | 0.9950 | 0.9952 | $0.0015 | Keep the proven sum-of-squares primary objective and the loosest-fit tiebreak, but on exact SOS t... |
| 150 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Introduce a small "pairing" bonus based on the count of bins whose remaining capacity exactly equ... |
| 151 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The SOS primary objective treats every capacity bucket equally, but bins with residual below the ... |
| 152 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will change the primary objective's tiebreak from "largest residual" to a bucketed best-fit-wit... |
| 153 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll replace the SOS rule's sensitivity to the whole capacity histogram with a focused "match res... |
| 154 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Observation: the current rule's SOS objective already works well; the real remaining loss comes f... |
| 155 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Keep the sum-of-squares primary objective exactly as-is, but change the tiebreak: among exact SOS... |
| 156 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I will replace the pure loosest-fit tiebreak with a tiebreak that, among exact SOS ties, prefers ... |
| 157 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the hardcoded 1000 multiplier and loosest-fit tiebreak with a lexicographic-style compari... |
| 158 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Instead of relying only on the SOS delta of the chosen bin, I will compute the full change in the... |
| 159 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll make the SOS objective hard-constrained by choosing the item's bin purely to minimize the su... |
| 160 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll refine the tiebreak in the valid SOS rule: among exact SOS ties, prefer a residual that has ... |
| 161 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the hardcoded tiebreak with an exact lexicographic comparison: primary key minimizes the ... |
| 162 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | The fixed tiebreaks have all failed to improve on plain SOS, so I'll instead make the SOS objecti... |
| 163 | edit | not_better | 0.9616 | 0.9952 | $0.0006 | I'll replace the sum-of-squares objective with the classic "best-fit" rule but keep the loosest-f... |
| 164 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I will keep the proven sum-of-squares primary objective but change the tiebreak among exact SOS t... |
| 165 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the SOS primary objective but replace the tiebreak with the classic "best-fit" preferen... |
| 166 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | The previous tiebreaks all tried to reason about future residuals, which lost against plain SOS +... |
| 167 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will keep the sum-of-squares primary objective but replace the loosest-fit tiebreaker with a "f... |
| 168 | edit | not_better | 0.9642 | 0.9952 | $0.0009 | Most tiebreaks have failed because the SOS delta is already nearly decisive; the real remaining l... |
| 169 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll keep the proven SOS primary objective but change the tiebreak to prefer the bin that exactly... |
| 170 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll widen the primary SOS comparison into a full lexicographic ordering so the tiebreak only mat... |
| 171 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The sum-of-squares objective only counts residual capacities, but a stronger local criterion also... |
| 172 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will keep the proven SOS primary objective and loosest-fit tiebreak, but make the objective mor... |
| 173 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The current rule's SOS objective is static (counts bins only by exact residual), so I'll add a ch... |
| 174 | edit | invalid | 0.0000 | 0.9952 | $0.0010 | Replace the exact-capacity SOS bucket counting with a smoothed/weighted histogram: the greedy "su... |
| 175 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | Replace the pure "sum of N(g)^2" primary key with a slightly modified objective that adds a small... |
| 176 | edit | not_better | 0.9935 | 0.9952 | $0.0009 | I'll replace the exact-residual sum-of-squares key with a "smoothed" sum-of-squares that groups n... |
| 177 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll keep the SOS primary objective but change the tiebreak from "loosest fit" (largest residual)... |
| 178 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Among exact SOS ties, replace the pure loosest-fit tiebreak with a hybrid: prefer the residual th... |
| 179 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The exact-residual SOS rule ignores that a residual capacity below the smallest item size can nev... |
| 180 | edit | not_better | 0.9940 | 0.9952 | $0.0011 | Keep the SOS primary objective but replace the pure loosest-fit tiebreak with "tightest fit that ... |
| 181 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The current rule's primary SOS objective is exact, but the "loosest fit" tiebreak is often harmfu... |
| 182 | edit | not_better | 0.9925 | 0.9952 | $0.0012 | I will keep the exact SOS primary objective but weight each residual bucket's contribution by its... |
| 183 | edit | not_better | 0.9875 | 0.9952 | $0.0009 | The SOS objective currently treats all residual capacities as equally valuable, but a residual be... |
| 184 | edit | invalid | 0.0000 | 0.9952 | $0.0008 | I will fix a performance bug/limitation: the current code builds the `fitting` list with a Python... |
| 185 | edit | not_better | 0.9642 | 0.9952 | $0.0008 | I'll replace the fragile hand-maintained Python bookkeeping (which caused a prior crash) with vec... |
| 186 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will make the tiebreak prefer filling a residual that exactly equals the arriving item (creatin... |
| 187 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares primary objective but replace the residual-based tiebreaker ... |
| 188 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The loosest-fit tiebreaker is the only remaining lever, and past attempts to replace it all regre... |
| 189 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Past tweaks to the tiebreaker all regressed, so I'll keep the loosest-fit tiebreak but make it a ... |
| 190 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll switch the residual tiebreaker from loosest-fit to best-fit (smallest residual that still fi... |
| 191 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares primary objective and the loosest-fit tiebreak, but add a sm... |
| 192 | edit | not_better | 0.9950 | 0.9952 | $0.0008 | The SOS objective optimizes the global state but ignores the immediate waste; I'll add a small se... |
| 193 | edit | not_better | 0.9932 | 0.9952 | $0.0009 | Among exact SOS ties, use a randomized (but deterministic per-call) tiebreak that prefers looser ... |
| 194 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Keep the exact sum-of-squares primary objective, but make the loosest-fit tiebreak strictly subor... |
| 195 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The SOS primary objective and loosest-fit tiebreak are strong, but the current *1000 scaling risk... |
| 196 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the strong sum-of-squares primary objective but replace the pure loosest-fit tiebreak w... |
| 197 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Replace the pure sum-of-squares objective's tiebreaker by using the residual r to break exact SOS... |
| 198 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | (no description) |
| 199 | edit | not_better | 0.6347 | 0.9952 | $0.0008 | The current code wastes O(n) time per call rebuilding a Python list comprehension over all opened... |
| 200 | edit | not_better | 0.9950 | 0.9952 | $0.0008 | I'll keep the proven SOS primary objective but change the tiebreaker among exact SOS ties to pref... |
| 201 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Retain the proven sum-of-squares primary objective, but replace the pure loosest-fit tiebreak wit... |
| 202 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | Keep the exact sum-of-squares primary objective, but replace the loosest-fit tiebreak with one th... |
| 203 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Keep the exact sum-of-squares primary rule, but refine the tiebreak by preferring bins whose resi... |
| 204 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the proven sum-of-squares primary objective, but replace the pure loosest-fit tiebreak ... |
| 205 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will replace the pure loosest-fit tiebreaker with a dynamic "future-fitting" tiebreak: among ex... |
| 206 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Keep the proven sum-of-squares primary objective, but add a secondary penalty term that discourag... |
| 207 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will keep the SOS primary objective but reorder it as a lexicographic (primary, secondary) comp... |
| 208 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Keep the proven sum-of-squares primary objective, but change the tiebreak to prefer leaving a res... |
| 209 | edit | invalid | 0.0000 | 0.9952 | $0.0008 | The current code spends most of its time rebuilding the fitting list and Python-looping over ever... |
| 210 | edit | not_better | 0.6347 | 0.9952 | $0.0008 | Reduce the efficiency drag from repeatedly rebuilding the fitting list and Python loop: maintain ... |
| 211 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares primary objective (proven best) and change only the tiebreak... |
| 212 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Keep the proven sum-of-squares primary objective unchanged, but improve the tiebreak: instead of ... |
| 213 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares primary objective, but change the secondary tiebreak among e... |
| 214 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the ad-hoc tiebreak with a cutoff/reserve pairing rule: keep the exact sum-of-squares pri... |
| 215 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Keep the sum-of-squares primary objective, but skip updating/using bins whose remaining capacity ... |
| 216 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | I'll keep the exact sum-of-squares primary objective but change the SIMPLERELS tiebreak: among ex... |
| 217 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares primary objective, but make the tiebreak prefer the bin that... |
| 218 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | I'll replace the sum-of-squares primary with the classic "best-fit-decreasing-like" online rule t... |
| 219 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | I'll keep the exact sum-of-squares primary objective, but replace the tiebreak with a lightweight... |
| 220 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will keep the exact sum-of-squares primary objective but replace the ad-hoc tiebreak with a lea... |
| 221 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | I will keep the exact sum-of-squares primary objective but replace the loosest-fit tiebreak (+r) ... |
| 222 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | I'll keep the exact sum-of-squares primary objective but replace the loosest-fit tiebreak with a ... |
| 223 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I will replace the integer-scaled SOS score with the exact un-scaled sum-of-squares delta, and am... |
| 224 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Replace the ad-hoc tiebreak with a principled one: keep the exact sum-of-squares delta as the pri... |
| 225 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Use a scaled combined key that blends the exact SOS delta with the loosest-fit tiebreak more grad... |
| 226 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | I will keep the exact sum-of-squares primary key but add a bounded-history "bin aging" tiebreak: ... |
| 227 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | The current tiebreak among exact sum-of-squares ties uses "loosest fit" (+r), which is somewhat a... |
| 228 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the exact sum-of-squares primary objective but replace the "loosest fit" (+r) tiebreak ... |
| 229 | edit | not_better | 0.9945 | 0.9952 | $0.0016 | Keep the exact SOS delta as the primary key, but change the tiebreaker so that a perfect fit (res... |
| 230 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | Switch the primary key from sum-of-squares delta to tightest-fit (minimize residual capacity afte... |
| 231 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I will keep the sum-of-squares primary rule but replace the arbitrary loosest-fit tiebreak with a... |
| 232 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Use a prospectively safer tiebreak: among exact SOS deltas, prefer the bin whose resulting residu... |
| 233 | edit | invalid | 0.0000 | 0.9952 | $0.0008 | I'll replace the hand-rolled per-step Python loop over fitting bins with a fully vectorized numpy... |
| 234 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Add a light "aging/urgency" tiebreak that, among exact SOS ties, prefers the bin whose resulting ... |
| 235 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will replace the flat histogram-count objective with a weighted one that penalizes "stranded" r... |
| 236 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The tiebreaker matters less than the primary rule, but a known improvement over pure SOS in onlin... |
| 237 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | Replace the loosest-fit tiebreak with a tiebreak that prefers placing the item so the resulting r... |
| 238 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | I'll keep the SOS delta as the dominant term but replace the flat "+r" loosest-fit tiebreak with ... |
| 239 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll keep the SOS delta as the dominant term, but scale it so that a bin producing residual exact... |
| 240 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | Change the primary rule to Best Fit (prefer the fitting bin with the smallest current remaining c... |
| 241 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | I'll keep the strong SOS objective but replace the "+r" loosest-fit tiebreak with a tiebreaker th... |
| 242 | edit | not_better | 0.9927 | 0.9952 | $0.0008 | I'll replace the SOS objective's first-difference delta term with the exact SOS increment compute... |
| 243 | edit | not_better | 0.9927 | 0.9952 | $0.0009 | I'll replace the loosest-fit "+r" tiebreaker with one that prefers residuals which exactly comple... |
| 244 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll keep the SOS delta as the primary rule but change the tiebreaker from loosest-fit ("+r") to ... |
| 245 | edit | not_better | 0.9945 | 0.9952 | $0.0018 | The exact SOS increment can be written as delta = 2*N[r] - 2*N[g] + 1 (for r>0) or 2*N[0]... ; I'... |
| 246 | edit | not_better | 0.9927 | 0.9952 | $0.0009 | I'll add a light "best-fit within the SOS optimum" refinement: keep the SOS delta dominant, but a... |
| 247 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll keep the strong sum-of-squares delta as the primary rule but replace the loosest-fit tiebrea... |
| 248 | edit | not_better | 0.9925 | 0.9952 | $0.0007 | I'll replace the SOS primary rule with a hybrid that uses the exact SOS increment as the dominant... |
| 249 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll replace the sum-of-squares primary objective with a "best-fit with limited residual" rule th... |
| 250 | edit | not_better | 0.6283 | 0.9952 | $0.0007 | Replace the SOS-delta primary rule with classic Best-Fit (choose the bin whose remaining capacity... |
| 251 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | Keep the dominant sum-of-squares delta, but replace the loosest-fit tiebreaker with a residual-pr... |
| 252 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | Add a lightweight adaptive tiebreaker: track a histogram of past item sizes and, among exact SOS ... |
| 253 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll replace the "loosest-fit" tiebreaker with a smoother secondary term based on the total numbe... |
| 254 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreaker with a sharper lexicographic tiebreak that, among exact SOS ti... |
| 255 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreaker with a smoother secondary term (scale strictly less than one S... |
| 256 | edit | not_better | 0.9950 | 0.9952 | $0.0008 | Add a deterministic "residual-list matching" tiebreaker to the SOS primary: among placements with... |
| 257 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the sum-of-squares primary with a "dual" scoring that mixes the SOS-delta with a best-fit... |
| 258 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll switch the primary rule from sum-of-squares-delta to a lexicographic "smallest residual ≥ it... |
| 259 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Switch the primary rule to a "best-fit" score based on the fraction of the bin filled (prefer sma... |
| 260 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | Introduce a stateful online "dual-tracking" enhancement to the sum-of-squares rule: maintain a sl... |
| 261 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | Replace the fixed loosest-fit tiebreaker with a tiebreaker that prefers leaving a residual equal ... |
| 262 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the loosest-fit tiebreaker with a two-stage tiebreaker: among exact SOS ties prefer the r... |
| 263 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | Replace the loosest-fit tiebreaker with a tiebreaker that prefers leaving a residual exactly equa... |
| 264 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the SOS-delta-primary with a hybrid that uses the SOS delta but breaks ties by preferring... |
| 265 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The sum-of-squares rule can be improved by using the exact "sum of squares" objective but weighti... |
| 266 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Replace the fragile scaled tiebreaker with a clean lexicographic comparison: keep the sum-of-squa... |
| 267 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the O(num_bins) per-item Python loop with an exact-equivalent vectorized numpy computatio... |
| 268 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | The previous attempts all added speculative heuristics that hurt. A cleaner, well-founded improve... |
| 269 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I will keep the sum-of-squares primary rule but drop the ad-hoc loosest-fit tiebreak and replace ... |
| 270 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Keep the sum-of-squares primary rule, but replace the loosest-fit tiebreak with a small penalty t... |
| 271 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | Keep the sum-of-squares primary rule but replace the scaled loosest-fit tiebreak with an explicit... |
| 272 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | I will replace the loosest-fit tiebreak with a tiebreak that prefers the bin whose resulting resi... |
| 273 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The history shows that all speculative tiebreakers hurt. Instead I'll use the exact sum-of-square... |
| 274 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current tie-breaking heuristics have all failed to improve on the plain SOS delta with looses... |
| 275 | edit | not_better | 0.9593 | 0.9952 | $0.0009 | I will improve robustness by adding a tiny per-bin-index preference so ties among equal SOS delta... |
| 276 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will switch from the incremental SOS delta with a loosest-fit tiebreak to the exact sum-of-squa... |
| 277 | edit | not_better | 0.9950 | 0.9952 | $0.0008 | All tiebreaking heuristics have failed to beat the plain SOS rule, so I will strengthen the prima... |
| 278 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will replace the incremental SOS delta with the exact sum-of-squares objective evaluated after ... |
| 279 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll replace the SOS ranking with a well-known strong online heuristic: a "best-fit with a matchi... |
| 280 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | Replace the SOS-with-loosest-fit rule with a Best-Fit rule (minimize resulting residual), which i... |
| 281 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll add a "perfect fit / exact-residual reuse" bonus to the proven SOS rule: among candidates wi... |
| 282 | edit | not_better | 0.9619 | 0.9952 | $0.0009 | I will key all residual calculations off the harness's authoritative `bins` array (not the recons... |
| 283 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | Keep the SOS primary ranking but replace the tiebreak so that, among candidates with the minimal ... |
| 284 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | I will keep the SOS primary objective (minimize the sum-of-squares delta) but change the tiebreak... |
| 285 | edit | not_better | 0.9932 | 0.9952 | $0.0009 | I will re-derive the SOS delta correctly and make the objective rank bins by the true post-placem... |
| 286 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I will keep the SOS-delta primary ranking but multiply the delta by a larger factor (100000) and ... |
| 287 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the hand-maintained `_caps` reconstruction with the harness's authoritative `bins` array ... |
| 288 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Add a "session reset" guard so module state resets whenever a fresh instance begins (detected by ... |
| 289 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the loosest-fit tiebreak with a "healthy residual" tiebreak: among equal SOS deltas, scor... |
| 290 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Keep the SOS-delta primary objective, but replace the loosest-fit tiebreak with a preference amon... |
| 291 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Replace the pure SOS-delta primary objective with a look-ahead-aware objective: minimize the SOS ... |
| 292 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will keep the proven SOS-delta primary objective and loosest-fit tiebreak, but make the tiebrea... |
| 293 | edit | not_better | 0.9952 | 0.9952 | $0.0013 | Keep the proven SOS-delta primary (delta*1000) but replace the loosest-fit tiebreak with a waste-... |
| 294 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The pure sum-of-squares rule minimizes the sum of squared bin loads, which is the classic greedy ... |
| 295 | edit | not_better | 0.9616 | 0.9952 | $0.0006 | Replace the sum-of-squares objective with the classic Best-Fit rule primary (minimise residual), ... |
| 296 | edit | not_better | 0.9593 | 0.9952 | $0.0009 | Keep the proven SOS-delta minimization with loosest-fit tiebreak, but restore a robust session/st... |
| 297 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Keep the proven SOS-delta primary objective, but replace the loosest-fit tiebreak with a Best-Fit... |
| 298 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will keep the proven SOS-delta primary objective, but replace the loosest-fit tiebreak with a "... |
| 299 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the loosest-fit tiebreak with a "least residue mass" tiebreak: among bins with equal SOS ... |
| 300 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | I will switch the primary objective from sum-of-squares delta minimization to the classic Best-Fi... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,11 +1,12 @@
 # EVOLVE-BLOCK-START
-"""Starting program: the Sum-of-Squares rule.
+"""Sum-of-Squares rule with a loosest-fit tiebreaker.
 
 Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining capacity g
-(0 < g < 100); ties go to the tighter fit. The function is shown only the bins the item fits in, so it
-keeps its own record of every opened bin. The harness opens unused bins in index order (ties go to the
-first bin), so used bins are always a prefix of the bin array. Each instance runs in a fresh process,
-so the module-level state starts empty for every instance.
+(0 < g < 100). Among exact sum-of-squares ties, prefer the bin with the largest remaining capacity
+(loosest fit), which spreads load and avoids prematurely creating tiny unusable residuals.
+The function keeps its own record of every opened bin. The harness opens unused bins in index order
+(ties go to the first bin), so used bins are always a prefix of the bin array. Each instance runs in a
+fresh process, so the module-level state starts empty for every instance.
 """
 import numpy as np
 
@@ -26,14 +27,16 @@
     fitting = [j for j, g in enumerate(_caps) if g >= s]
     n_unused = len(bins) - len(fitting)
     scores = np.empty(len(bins), dtype=np.float64)
+
     for k, j in enumerate(fitting):
         g = _caps[j]
         r = g - s
         delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)
-        scores[k] = -(delta * 1000 + r)
+        # primary: minimise delta; tiebreak: prefer larger residual (loosest fit)
+        scores[k] = -(delta * 1000) + r
     r_new = CAP - s
     delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
-    scores[len(fitting):] = -(delta_new * 1000 + r_new)
+    scores[len(fitting):] = -(delta_new * 1000) + r_new
 
     choice = int(np.argmax(scores))          # the harness's choice: first highest score
     if choice < len(fitting):
```

## Explanation

Two-sided ablation of `priority` (40 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 26 | `s = int(item)` | -0.9952 | essential: the program fails or turns invalid without it |
| 27 | `fitting = [j for j, g in enumerate(_caps) if g >= s]` | -0.9952 | essential: the program fails or turns invalid without it |
| 28 | `n_unused = len(bins) - len(fitting)` | -0.9952 | essential: the program fails or turns invalid without it |
| 29 | `scores = np.empty(len(bins), dtype=np.float64)` | -0.9952 | essential: the program fails or turns invalid without it |
| 31 | `for k, j in enumerate(fitting): ...` | -0.9952 | essential: the program fails or turns invalid without it |
| 32 | `g = _caps[j]` | -0.9952 | essential: the program fails or turns invalid without it |
| 33 | `r = g - s` | -0.9952 | essential: the program fails or turns invalid without it |
| 34 | `delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)` | -0.9952 | essential: the program fails or turns invalid without it |
| 36 | `scores[k] = -(delta * 1000) + r` | -0.9952 | essential: the program fails or turns invalid without it |
| 37 | `r_new = CAP - s` | -0.9952 | essential: the program fails or turns invalid without it |
| 38 | `delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0` | -0.9952 | essential: the program fails or turns invalid without it |
| 39 | `scores[len(fitting):] = -(delta_new * 1000) + r_new` | -0.9952 | essential: the program fails or turns invalid without it |
| 41 | `choice = int(np.argmax(scores))` | -0.9952 | essential: the program fails or turns invalid without it |
| 51 | `if CAP - s > 0: ...` | -0.5991 | matters |
| 46 | `_caps[j] = g - s` | -0.2355 | matters |
| 46 | `term - s` | -0.2355 | matters |
| 33 | `term - s` | -0.2292 | matters |
| 44 | `g = _caps[j]` | -0.2198 | matters |
| 47 | `if g - s > 0: ...` | -0.2029 | matters |
| 48 | `_N[g - s] += 1` | -0.2029 | matters |
| 46 | `term + g` | -0.1109 | matters |
| 36 | `term + -(delta * 1000)` | -0.1105 | matters |
| 43 | `j = fitting[choice]` | -0.0510 | matters |
| 34 | `term + 2 * _N[r] + 1 if r > 0 else 0` | -0.0415 | matters |
| 33 | `term + g` | -0.0364 | matters |
| 28 | `term + len(bins)` | -0.0359 | matters |
| 42 | `if choice < len(fitting): ...` | -0.0359 | matters |
| 49 | `if n_unused > 0: ...` | -0.0359 | matters |
| 50 | `_caps.append(CAP - s)` | -0.0359 | matters |
| 45 | `_N[g] -= 1` | -0.0253 | matters |
| 34 | `term + -2 * _N[g]` | -0.0089 | matters |
| 39 | `term + -(delta_new * 1000)` | -0.0062 | matters |
| 36 | `term + r` | -0.0012 | no effect alone |
| 37 | `term + CAP` | -0.0008 | no effect alone |
| 37 | `term - s` | -0.0008 | no effect alone |
| 28 | `term - len(fitting)` | +0.0000 | no effect alone |
| 34 | `term + 1` | +0.0000 | no effect alone |
| 39 | `term + r_new` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 25: `global _caps, _N`

Not tested (evaluation limit 40): 1 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9952 | 0.9947 |
| minimal (1 parts removed) | 0.9952 | 0.9947 |

Minimal program:

```python
"""Sum-of-Squares rule with a loosest-fit tiebreaker.

Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining capacity g
(0 < g < 100). Among exact sum-of-squares ties, prefer the bin with the largest remaining capacity
(loosest fit), which spreads load and avoids prematurely creating tiny unusable residuals.
The function keeps its own record of every opened bin. The harness opens unused bins in index order
(ties go to the first bin), so used bins are always a prefix of the bin array. Each instance runs in a
fresh process, so the module-level state starts empty for every instance.
"""
import numpy as np
CAP = 100
_caps = []
_N = [0] * (CAP + 1)

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    s = int(item)
    fitting = [j for j, g in enumerate(_caps) if g >= s]
    n_unused = len(bins) - len(fitting)
    scores = np.empty(len(bins), dtype=np.float64)
    for k, j in enumerate(fitting):
        g = _caps[j]
        r = g - s
        delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)
        scores[k] = -(delta * 1000) + r
    r_new = CAP - s
    delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
    scores[len(fitting):] = -(delta_new * 1000) + r_new
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
python -m autoresearch.loop problems/bin_packing_online_ss --budget 0.6 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 1
python -m autoresearch.loop --report experiments/llm-from-ss-v1/runs/s1   # rebuild this report
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
