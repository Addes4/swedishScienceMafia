# Research loop report: bin_packing_online_ss

| | |
|---|---|
| problem | `bin_packing_online_ss` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2703 of a $0.60 hard cap, 293 calls, 827,440 tokens |
| wall time | search 5406 s, baselines 14 s, explain 137 s |
| stopped | wall (wall_limit) |
| evaluations | 294 (290 valid), 2 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9942 | 0.9950 | |
| `best_program.py` (final incumbent) | 0.9952 | 0.9947 | **OVERFIT?** public rose, hidden fell |
| baseline `best_fit` | 0.9616 | 0.9604 | `problems/bin_packing_online_ss/baselines/best_fit.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_ss/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_ss/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9945 | 0.9952 | 4 parts removed |

Audit: public 0.9942 → 0.9952 (+0.0010), hidden 0.9950 → 0.9947 (-0.0003); public − hidden gap of the final program 0.0005. **OVERFIT?** The public score rose while the hidden score fell: treat the gain as unconfirmed.

Against the baselines: the final program's public score is above the best baseline (`sum_of_squares`, 0.9942). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9942 | 0.9942 | $0.0006 | Add a small tie-breaking term that prefers the tightest fit among bins with equal sum-of-squares ... |
| 2 | edit | not_better | 0.9942 | 0.9942 | $0.0007 | Replace the fixed 1000*r tie-break margin with a proper lexicographic comparison: score by the su... |
| 3 | edit | not_better | 0.9616 | 0.9942 | $0.0007 | Replace the Sum-of-Squares ranking with the Best-Fit rule restricted among bins where an exact ma... |
| 4 | edit | improved | 0.9947 | 0.9947 | $0.0008 | I'll replace the plain sum-of-squares lookahead with a refined scoring that combines the sum-of-s... |
| 5 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will add a "heavy-item protection" secondary term: when the sum-of-squares deltas tie, prefer l... |
| 6 | edit | not_better | 0.9584 | 0.9947 | $0.0007 | I will replace the fixed sum-of-squares rule with a "best-fit with perfect-fit and near-fit prote... |
| 7 | edit | not_better | 0.9945 | 0.9947 | $0.0009 | I will add a bounded "waste" term to the sum-of-squares delta that gives a mild bonus to residual... |
| 8 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | Replace the sum-of-squares delta with a lookahead that also accounts for the second-order effect ... |
| 9 | edit | invalid | 0.0000 | 0.9947 | $0.0010 | Replace the exact sum-of-squares delta with a smoothed version that uses a lookahead over the exp... |
| 10 | edit | not_better | 0.6341 | 0.9947 | $0.0009 | I will add a graduated "perfect-fit protection" plus a small best-fit bias on top of the SS delta... |
| 11 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will add a lookahead term based on the harmonic/bin-packing lower-bound potential: after placin... |
| 12 | edit | not_better | 0.9947 | 0.9947 | $0.0008 | Add a small tie-breaking bonus for residuals that exactly fill gaps needed by keeping the SS delt... |
| 13 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will add a bounded lookahead term to the sum-of-squares delta that mildly prefers residuals mat... |
| 14 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will add a small bonus to the SS delta that rewards residuals which are multiples of 100 (i.e.,... |
| 15 | edit | not_better | 0.9937 | 0.9947 | $0.0009 | I will replace the SS-delta ranking with a "best-fit decreasing-aware" rule that keeps sum-of-squ... |
| 16 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | Reduce the perfect-fit over-prioritisation: instead of an overwhelming hard preference for residu... |
| 17 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll replace the fixed overwhelming perfect-fit bonus with a bounded, additive bonus that scales ... |
| 18 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I will make the residual term unit-weight (not scaled by 1000) so sum-of-squares deltas genuinely... |
| 19 | edit | not_better | 0.9945 | 0.9947 | $0.0009 | The SS rule's known weakness is that it ignores bin indices; a light "keep bins packed in prefix ... |
| 20 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I will implement a "residual-matching" rule: keep the exact SS delta as the primary ordering, but... |
| 21 | edit | not_better | 0.9945 | 0.9947 | $0.0009 | Replace the fixed perfect-fit bonus with the "best fit decreasing" style Modified First Fit / har... |
| 22 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll switch the primary rule to a best-fit-style rule that selects the bin minimizing the residua... |
| 23 | edit | not_better | 0.9942 | 0.9947 | $0.0010 | I'll replace the pure SS-delta with the "Sum of Squares" rule combined with a proper "Match" adju... |
| 24 | edit | not_better | 0.9942 | 0.9947 | $0.0010 | The sum-of-squares rule can be strengthened by adding a "best fit decreasing"-flavored tie-break:... |
| 25 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I will replace the pure SS-delta primary key with a "best-fit-with-SS-tiebreak" hybrid: rank bins... |
| 26 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I will add a "harmonic/geometric residual-class" bonus: among candidate moves whose SS delta is w... |
| 27 | edit | not_better | 0.9945 | 0.9947 | $0.0009 | I will replace the ad-hoc residual tie-break with the classic "Sum of Squares + Best-Fit conjunct... |
| 28 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll refine the SS rule by scaling the tie-break so it never overrides the primary SS delta (the ... |
| 29 | edit | not_better | 0.9616 | 0.9947 | $0.0008 | I'll replace the sum-of-squares primary key with the "Modified First Fit Decreasing"-style rule u... |
| 30 | edit | not_better | 0.9932 | 0.9947 | $0.0009 | Replace the scaled-key formulation with an exact sum-of-squares ranking: among fitting bins, pick... |
| 31 | edit | not_better | 0.9935 | 0.9947 | $0.0010 | I will make the perfect-fit bonus bounded and exact: replace the fragile `*1000` scaled composite... |
| 32 | edit | not_better | 0.9942 | 0.9947 | $0.0010 | I will add a "cap-sum waste" tie-break layer inside the SS rule: when several bins give (nearly) ... |
| 33 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will make the perfect-fit handling exact by removing the fragile scaled composite key: score bi... |
| 34 | edit | not_better | 0.8686 | 0.9947 | $0.0009 | I will replace the fragile scaled-composite key with a strict lexicographic ranking that (1) alwa... |
| 35 | edit | not_better | 0.9930 | 0.9947 | $0.0009 | I will replace the fragile scaled composite key with a clean lexicographic ranking that keeps the... |
| 36 | edit | not_better | 0.9940 | 0.9947 | $0.0010 | Drop the artificial perfect-fit penalty and the `*1000` scaled composite key; use the exact SS co... |
| 37 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | Add a bounded "perfect-fit chain" bonus: when no exact perfect fit is available, still prefer pla... |
| 38 | edit | not_better | 0.9945 | 0.9947 | $0.0009 | Add a bounded "full-bin reward": actively prefer moves that leave a residual of 0 or an extremely... |
| 39 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I will replace the SS-delta tie-break with an exact "sum-of-squares" primary criterion but add a ... |
| 40 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will switch the primary ranking from the raw SS delta to the exact SS rule's actual objective c... |
| 41 | edit | not_better | 0.9942 | 0.9947 | $0.0018 | Replace the hard 1e9 perfect-fit override with a bounded bonus: score by the exact SS cost change... |
| 42 | edit | not_better | 0.9947 | 0.9947 | $0.0013 | Keep the exact SS cost-change as the primary key (removing the fragile *1000 blend), retain the s... |
| 43 | edit | not_better | 0.9945 | 0.9947 | $0.0010 | Replace the scaled composite key with a clean primary criterion of the exact SS cost change (delt... |
| 44 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | Replace the scaled-composite key with the exact SS cost-change as the primary criterion, keep a b... |
| 45 | edit | not_better | 0.9945 | 0.9947 | $0.0010 | Change the tie-break among placements with equal SS cost-change from preferring the smallest resi... |
| 46 | edit | not_better | 0.9940 | 0.9947 | $0.0009 | I'll replace the fragile scaled composite key with a clean lexicographic scheme: primary key is t... |
| 47 | edit | not_better | 0.9945 | 0.9947 | $0.0011 | Among placements with equal exact SS cost-change, break ties by preferring a residual that equals... |
| 48 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I will incorporate a small, bounded "large-item reserve" tie-break: keep the exact SS cost-change... |
| 49 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | Add a small bounded bonus (equivalent to ~0.02 in the combined key) when a placement creates a re... |
| 50 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | Replace the fragile composite with a clean vectorized approach: compute the exact SS cost change ... |
| 51 | edit | not_better | 0.7068 | 0.9947 | $0.0010 | The current tie-break keys off a scaled integer composite; I'll make the primary criterion a robu... |
| 52 | edit | not_better | 0.9945 | 0.9947 | $0.0011 | Keep the hard perfect-fit override and exact SS cost-change as primary key, but change the tie-br... |
| 53 | edit | invalid | 0.0000 | 0.9947 | $0.0011 | The current code recomputes the fit list each call using a Python loop over all opened bins, and ... |
| 54 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I'll make the perfect-fit override soft rather than an absolute hard override (value 0.5 bonus) s... |
| 55 | edit | not_better | 0.4081 | 0.9947 | $0.0007 | Replace the internal bookkeeping with a fully vectorized SS-rule computation that directly uses t... |
| 56 | edit | not_better | 0.6331 | 0.9947 | $0.0012 | Replace the scalar global array with a vectorized residual-count implementation, and refine the S... |
| 57 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | The current rule ignores the well-known best-fit variant, so I'll add a bounded tie-break: keep e... |
| 58 | edit | invalid | 0.0000 | 0.9947 | $0.0009 | Replace the hard perfect-fit override (which forces filling a zero-residual bin even when it badl... |
| 59 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | Make the perfect-fit override conditional on it not being badly suboptimal: instead of an absolut... |
| 60 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | The hard perfect-fit override is likely too rigid: I'll replace it with a bounded penalty (subtra... |
| 61 | edit | not_better | 0.9013 | 0.9947 | $0.0009 | I'll switch the primary rule from sum-of-squares to a best-fit-with-perfect-fit-priority rule, si... |
| 62 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I'll refine the near-tie handling: keep the exact SS cost-change as primary, but among placements... |
| 63 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I'll keep the SS cost-change as the primary rule but sharpen the tie-break: when deltas are withi... |
| 64 | edit | not_better | 0.9647 | 0.9947 | $0.0012 | Correct the SS cost-change for opening a new bin: a new bin counts as a bin of full remaining cap... |
| 65 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll replace the rigid hard perfect-fit override with a bounded bonus so the sum-of-squares delta... |
| 66 | edit | not_better | 0.9932 | 0.9947 | $0.0009 | I'll replace the hard perfect-fit override with a "best coin" tie-break derived from the sum-of-s... |
| 67 | edit | not_better | 0.9633 | 0.9947 | $0.0009 | I'll try a proper "best-fit with SS primary" hybrid: keep the SS delta as the primary rule but, a... |
| 68 | edit | not_better | 0.9947 | 0.9947 | $0.0008 | I'll keep the SS cost-change as the primary rule but replace the hard perfect-fit override with a... |
| 69 | edit | not_better | 0.9930 | 0.9947 | $0.0009 | I'll remove the fixed 1000x/1e9 scaling that effectively makes the perfect-fit and delta comparis... |
| 70 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I'll add a lightweight "nice fit" secondary criterion based on actual item-size statistics: track... |
| 71 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I'll replace the brittle fixed scaling with a clean SS delta primary rule, but add a bounded perf... |
| 72 | edit | not_better | 0.9616 | 0.9947 | $0.0007 | I'll replace the current per-bin score rule with a "best-fit-decreasing-like" two-factor rule tha... |
| 73 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I'll replace the heuristic with a near-exact online rule based on the sum-of-squares (SS) score, ... |
| 74 | edit | not_better | 0.9945 | 0.9947 | $0.0008 | I will blend the SS delta rule with a "least-loaded-that-still-fits" nudge only when SS deltas ti... |
| 75 | edit | not_better | 0.9942 | 0.9947 | $0.0008 | I'll make the new-bin option use its true sum-of-squares delta (removing the artificial perfect-f... |
| 76 | edit | not_better | 0.9942 | 0.9947 | $0.0008 | I'll replace the hard perfect-fit override with a principled two-level rule: primary is the exact... |
| 77 | edit | not_better | 0.9937 | 0.9947 | $0.0010 | I'll keep the exact sum-of-squares (SS) delta as the primary criterion but fix the tie-breaking: ... |
| 78 | edit | not_better | 0.9945 | 0.9947 | $0.0011 | I'll keep exact SS delta as the primary criterion and improve tie-breaking: replace the unconditi... |
| 79 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll add a "sum-of-squares with a small best-fit tiebreak using the true residual" but more impor... |
| 80 | edit | not_better | 0.9940 | 0.9947 | $0.0012 | Keep the exact sum-of-squares delta as the primary criterion (dropping the brittle hard perfect-f... |
| 81 | edit | not_better | 0.9942 | 0.9947 | $0.0013 | Keep the hard perfect-fit override (which clearly helps) but add a second override tier: when no ... |
| 82 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will keep the SS-delta primary with perfect-fit priority, but replace the fixed "tighter fit" t... |
| 83 | edit | not_better | 0.9942 | 0.9947 | $0.0010 | Replace the ad-hoc perfect-fit/new-bin overrides and fixed scaling with a principled lexicographi... |
| 84 | edit | not_better | 0.9942 | 0.9947 | $0.0008 | I'll make the perfect-fit preference softer and more informative: instead of a hard 1e9 override ... |
| 85 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I'll replace the brittle 1000x/1e9 lexicographic scaling with a principled primary criterion: exa... |
| 86 | edit | not_better | 0.9940 | 0.9947 | $0.0009 | I'll replace the fragile fixed-scale lexicographic scoring with the exact sum-of-squares delta as... |
| 87 | edit | not_better | 0.9942 | 0.9947 | $0.0011 | Keep the exact SS delta as the primary criterion, but remove the hard 1e9 perfect-fit lock and in... |
| 88 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I will keep the sum-of-squares delta as the primary criterion but make the perfect-fit override c... |
| 89 | edit | not_better | 0.9940 | 0.9947 | $0.0009 | Add a "lookahead" refinement to the perfect-fit override: when no perfect fit exists, compute the... |
| 90 | edit | not_better | 0.9937 | 0.9947 | $0.0009 | Replace the fragile lexicographic scaling with a clean primary SS-delta criterion, and instead of... |
| 91 | edit | not_better | 0.9945 | 0.9947 | $0.0010 | I will keep the exact SS delta as the primary criterion and add a lightweight secondary tie-break... |
| 92 | edit | invalid | 0.0000 | 0.9947 | $0.0009 | I'll replace the fragile large-scale lexicographic scoring (1000x/1e9) with a clean single numeri... |
| 93 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | I'll simplify to use the exact sum-of-squares delta as the sole primary criterion (no lexicograph... |
| 94 | edit | not_better | 0.9942 | 0.9947 | $0.0009 | Replace the pure SS rule with the best-fit-style "closest fit wins, but without fragmenting" rule... |
| 95 | edit | not_better | 0.9942 | 0.9947 | $0.0008 | Remove the hard 1e9 perfect-fit override so the sum-of-squares delta fully governs placement, whi... |
| 96 | edit | not_better | 0.9616 | 0.9947 | $0.0008 | Replace the sum-of-squares rule with a pure best-fit rule (choose the fitting bin with the smalle... |
| 97 | edit | not_better | 0.9932 | 0.9947 | $0.0026 | Make the perfect-fit override conditional: take a perfect fit only when its exact sum-of-squares ... |
| 98 | edit | improved | 0.9952 | 0.9952 | $0.0010 | Keep the exact sum-of-squares delta as the dominant integer criterion (remove the hard perfect-fi... |
| 99 | edit | not_better | 0.9942 | 0.9952 | $0.0012 | Keep the exact SS delta as the dominant criterion, but replace the flat larger-residual tie-break... |
| 100 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the fragile `delta*1000 - r` scaling (where residual r up to 99 could overcome a unit SS-... |
| 101 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Encode the score as exact SS delta scaled by 100 (a fixed factor larger than any residual range) ... |
| 102 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the residual tie-break with a "least-full bin among equal SS delta" preference based on t... |
| 103 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Replace the "larger residual" tie-break with the classic Sum-of-Squares optimal tie-break directi... |
| 104 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Add a persistent "sticky" state: after each placement, record the chosen residual capacity class;... |
| 105 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the residual tie-break with a two-part refinement: among equal SS deltas, first prefer pl... |
| 106 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Use a deterministic secondary tie-break that keeps the exact SS delta dominant but, among equal d... |
| 107 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll replace the heuristic tie-break with an exact lexicographic encoding of the SS delta plus a ... |
| 108 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the deterministic tie-break with a tiny random tie-break (seeded RNG) so that among place... |
| 109 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | Introduce a "best-fit with SS-dominant" hybrid: keep the exact SS delta as the dominant criterion... |
| 110 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Numerous tie-break variants all failed, so instead I keep the exact SS-delta as the dominant crit... |
| 111 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll make the tie-break exact and integer-based (avoiding float precision loss) by lexicographica... |
| 112 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll change the dominant criterion from the SS (sum-of-squares) delta to the equivalent-but-finer... |
| 113 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Keep the exact SS-delta as the dominant criterion, but replace the "larger residual" tie-break wi... |
| 114 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll replace the pure SS-delta rule with the "Halving" style rule: the dominant criterion becomes... |
| 115 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the "larger residual" tie-break with a Best-Fit style tie-break: among placements with th... |
| 116 | edit | not_better | 0.9927 | 0.9952 | $0.0009 | The current rule is pure SS (sum-of-squares), whose per-step greedy minimization is provably subo... |
| 117 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The current rule greedily minimises the SS delta, but at the moment no placement avoids opening a... |
| 118 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | Keep exact integer SS-delta as the dominant key, but refine the tie-break: among equal-delta plac... |
| 119 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Use the SS (sum-of-squares) delta as the dominant criterion but replace the tie-break with "best-... |
| 120 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the float tie-break scoring with a pure integer SS-delta criterion plus a small, well-sca... |
| 121 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll add a small "future-fit" correction to the dominant SS delta: after the SS-based placement, ... |
| 122 | edit | not_better | 0.9947 | 0.9952 | $0.0015 | Keep the exact integer SS-delta as the dominant key, but replace the tie-break: among equal-delta... |
| 123 | edit | not_better | 0.9945 | 0.9952 | $0.0013 | Keep the exact integer SS-delta as the dominant key, but replace the tie-break with a one-step lo... |
| 124 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the hard-to-improve tie-break with a hybrid that keeps SS as dominant but, among equal-SS... |
| 125 | edit | not_better | 0.9932 | 0.9952 | $0.0009 | I'll replace the flawed "score = -(delta*K - r)" encoding, which accidentally makes the residual ... |
| 126 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Fix the encoding so the exact integer SS delta is strictly dominant (large multiplier / pure inte... |
| 127 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the "largest residual" tie-break with a "best-fit-like" tie-break that, among equal SS-de... |
| 128 | edit | not_better | 0.9952 | 0.9952 | $0.0021 | Make the tie-break hierarchy explicit and fix a likely flaw: the previous tie-break "largest resi... |
| 129 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current code has a subtle flaw: the tie-break multiplier (1000) is far larger than any possib... |
| 130 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the exact-SS dominant key with a scale-aware scoring that preserves SS as the primary cri... |
| 131 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will make the SS delta strictly dominant using a pure integer primary key (large multiplier) an... |
| 132 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll replace the score encoding with a strictly-dominant integer SS-delta key (greatly scaled) an... |
| 133 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Replace the SS rule entirely with Best Fit: among bins the item fits, choose the one with the sma... |
| 134 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Keep the exact SS rule as the strictly dominant key (so it is not overridden), but change the tie... |
| 135 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The current encoding multiplies the SS delta by 1000 but subtracts residual r (which can be up to... |
| 136 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll implement the classic and provably-good "Sum of Squares with a hard best-fit-style tie-break... |
| 137 | edit | not_better | 0.9952 | 0.9952 | $0.0028 | Make the SS delta strictly dominant (large multiplier), keep "prefer larger residual" as the tie-... |
| 138 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the exact SS delta as the strictly dominant key, but change the tie-break to prefer the plac... |
| 139 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Introduce a harmonic/statistical tie-break that, among placements with equal exact SS delta, pref... |
| 140 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the hand-tuned SS-with-tiebreak heuristic with the principled "Sum of Squares" rule from ... |
| 141 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Introduce a lookahead-free "dual" tie-break: keep the exact SS delta as the strictly dominant key... |
| 142 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The SS rule is asymptotically optimal but its tie-break wastes flexibility: among equal SS deltas... |
| 143 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current code uses `-2*_N[g] + 1 + (2*_N[r] + 1)` as the SS delta, which is actually the chang... |
| 144 | edit | not_better | 0.8179 | 0.9952 | $0.0008 | I'll make the SS delta the strictly dominant key with a larger separation and replace the tie-bre... |
| 145 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | Keep the exact SS delta as the dominant key, but replace the tie-break with the one used by the c... |
| 146 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Use exact integer packing of the SS delta as the dominant key but switch the tie-break to prefer ... |
| 147 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Add a small "dual-SS" secondary key: among placements with equal exact SS delta, instead of the r... |
| 148 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The SS objective alone is being dominated by an arbitrary scale factor; I'll restructure it as a ... |
| 149 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll replace the ad-hoc tie-break with a principled exact "best fit" secondary key derived from t... |
| 150 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | The SS delta is computed with an unnecessary "+1" offset that depends on nothing; more importantl... |
| 151 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | Replace the pure sum-of-squares rule with the classic "best fit within SS" is already tried, so i... |
| 152 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Add a small secondary SS-style "shelf" term: among equal primary SS deltas, prefer the placement ... |
| 153 | edit | not_better | 0.6315 | 0.9952 | $0.0009 | I'll reduce the influence of the flexibility tie-break by making the SS delta dominate more stron... |
| 154 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll switch the secondary tie-break from "largest residual" to a small tie-break that prefers the... |
| 155 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll make the tie-break adaptive: instead of a fixed "prefer largest residual", break SS-delta ti... |
| 156 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll replace the arbitrary fixed-multiplier tie-break with a pure lexicographic key: the exact in... |
| 157 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Add a strict bonus for residual 0 (exact fill) inside the same dominant SS key, so exact-fill pla... |
| 158 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current score maps delta to a float, which risks collisions between distinct integer deltas s... |
| 159 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | The current tie-break treats every bin the same, but the SS-optimal choice among equal deltas sho... |
| 160 | edit | not_better | 0.8179 | 0.9952 | $0.0010 | The SS rule's known weakness is that it ignores the very large items (near capacity); since the i... |
| 161 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current tie-break uses a float multiplier of 1000 for the SS delta, which can collide across ... |
| 162 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll replace the SS-delta objective with the "Power of Two Choices"-style tie-break using a norma... |
| 163 | edit | not_better | 0.9014 | 0.9952 | $0.0009 | The plateau suggests the tie-break doesn't matter much; instead I'll keep the SS rule but scale i... |
| 164 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll replace the SS delta objective with the "best-fit with a flexibility reserve" rule guided by... |
| 165 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | The repeated SS-delta tie-breaks have plateaued, so I'll switch the dominant rule to the well-kno... |
| 166 | edit | not_better | 0.8179 | 0.9952 | $0.0009 | I'll keep the exact Sum-of-Squares rule as the dominant criterion but change the tie-break to a "... |
| 167 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The SS delta is the dominant objective, but ties are frequent and the current tie-break (largest ... |
| 168 | edit | not_better | 0.8163 | 0.9952 | $0.0011 | I will implement the "modified SS" (Sum-of-Squares) rule known as the "Reuse-Then-SS / SS3" hybri... |
| 169 | edit | not_better | 0.9598 | 0.9952 | $0.0008 | I'll switch from the SS rule to a proper "best-fit with a size-class reservation" that is known t... |
| 170 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the exact Sum-of-Squares rule as the dominant criterion, but change the tie-break to pr... |
| 171 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The current tie-break among equal SS deltas favors the largest residual, but a stronger complemen... |
| 172 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll keep the exact Sum-of-Squares (SS) delta as the dominant criterion, but replace the tie-brea... |
| 173 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will add a "capacity reservation" secondary criterion to the SS tie-break: among equal SS delta... |
| 174 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll remove the residual-based tie-break and let the exact SS delta be the sole criterion (ties g... |
| 175 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll keep the exact Sum-of-Squares delta as the dominant criterion, but replace the tie-break wit... |
| 176 | edit | not_better | 0.8182 | 0.9952 | $0.0009 | I will keep the exact SS delta as the dominant criterion, but change the tie-break so that among ... |
| 177 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | I will keep the exact Sum-of-Squares delta as the dominant criterion, but replace the tie-break w... |
| 178 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the ad-hoc residual tie-break with the exact full objective: among placements with equal ... |
| 179 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will break SS ties by preferring the placement that minimizes the resulting number of "small" r... |
| 180 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | The SS delta can be large, so multiplying it by 1000 and subtracting r risks the tie-break term (... |
| 181 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will make the tie-break prefer, among equal SS deltas, the placement whose resulting residual e... |
| 182 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll switch the dominant criterion from the exact Sum-of-Squares delta to a hybrid: use the SS de... |
| 183 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the fixed linear SS tie-break with the exact lexicographic pair (delta, residual) using a... |
| 184 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I will reverse the tie-break to prefer the *smaller* residual among equal SS deltas (best-fit on ... |
| 185 | edit | not_better | 0.8362 | 0.9952 | $0.0010 | Use np.lexsort to rank bins by the exact SS delta as the strictly dominant key (no float scaling,... |
| 186 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will keep the exact Sum-of-Squares delta as the dominant criterion but replace the residual tie... |
| 187 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The SS-delta tie-break has been stuck at 0.995228 with every residual-based variant. I will inste... |
| 188 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | I will replace the SS-delta heuristic entirely with the "Ranking by Weight" / harmonic rule: scor... |
| 189 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The tie-break for equal SS deltas will be changed to deterministic best-fit consolidation anchore... |
| 190 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | The SS rule is already near-optimal; the remaining loss comes from tie-breaking. I will make the ... |
| 191 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Replace the SS-delta-based rule with the "Sum of Squares" variant that instead uses the *exact* S... |
| 192 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | I will switch the dominant criterion from the integer Sum-of-Squares delta to the classic "best-f... |
| 193 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | All previous tie-break variants were stuck at the same value, so I will keep the dominant exact S... |
| 194 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I will keep the exact SS delta dominant and replace the tie-break with an exact worst-fit rule: a... |
| 195 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | All residual-based tie-breaks have plateaued at the same score, so the loss is likely in the domi... |
| 196 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Rather than tweaking the tie-break, I'll replace the dominant criterion with the classic "Best-Fi... |
| 197 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | Replace the flat SS-delta criterion with the "Sum of Squares" rule computed over all residual cla... |
| 198 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | All tie-break tweaks plateaued, so I'll change the dominant criterion to a hybrid that is exactly... |
| 199 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Keep the exact SS delta dominant, but change the tie-break: among equal SS deltas, prefer the pla... |
| 200 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Keep the exact SS delta as the dominant criterion, but flip the tie-break to prefer the *smallest... |
| 201 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll keep the exact SS delta dominant but change the tie-break to prefer fitting into an existing... |
| 202 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the pure SS-delta dominant criterion with a hybrid that stays exact but adds a tiny best-... |
| 203 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact SS delta dominant, but replace the arbitrary tie-break with one that prefers ... |
| 204 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll keep the exact SS delta as the dominant criterion but replace the fragile tie-break with a t... |
| 205 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the SS rule with the well-known "Best-Fit with a residual-class preference" hybrid: keep ... |
| 206 | edit | not_better | 0.5224 | 0.9952 | $0.0008 | I'll replace the block-level tie/dominant scheme with the harmonic (H_k) weighting rule: choose t... |
| 207 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | Keep the exact SS-delta dominant, and make the tie-break a pure integer key: prefer the larger re... |
| 208 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | I'll keep the exact SS-delta as the dominant criterion, but change the tie-break to a two-part ke... |
| 209 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact SS-delta as the dominant criterion but improve the tie-break using a value-aw... |
| 210 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I will keep the exact SS-delta as the dominant criterion but replace the secondary tie-break with... |
| 211 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll switch from the pure SS rule to a hybrid: keep the exact SS-delta as the dominant term, but ... |
| 212 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Keep the exact SS-delta as the dominant criterion but flip the tie-break to prefer the *smaller* ... |
| 213 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will keep the exact SS-delta as the dominant criterion but change the tie-break to prefer the r... |
| 214 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | The repeated tie-break experiments all give small regressions, so the issue is the SS rule itself... |
| 215 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | Instead of SS-delta, use the classic Best-Fit rule (choose the fitting bin with the smallest resi... |
| 216 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll add a "top-off" exception to the SS rule: if a fitting bin can be filled exactly (residual 0... |
| 217 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Replace the flat SS rule with a hybrid "reserve-aware" SS rule: keep the exact SS-delta as the do... |
| 218 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will smooth the SS-delta criterion into a weighted-count rule that avoids the hard Δ∈ℤ granular... |
| 219 | edit | not_better | 0.9907 | 0.9952 | $0.0010 | I'll add a periodic "best-fit" escape: with small probability keyed to item size, choose the tigh... |
| 220 | edit | not_better | 0.9930 | 0.9952 | $0.0009 | The SS-delta tie-break variants all regressed, so instead I'll make the SS criterion itself smart... |
| 221 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Replace the hard integer SS-delta criterion with a smoothed sub-quadratic cost that still rewards... |
| 222 | edit | not_better | 0.9940 | 0.9952 | $0.0011 | Among placements with equal SS delta, break ties by preferring the residual closest to the empiri... |
| 223 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Make the residual-flexibility tie-break choose the *smallest* residual instead of the largest (i.... |
| 224 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Use a residual-waste tie-break that prefers the smallest positive residual (tightest fit) only wi... |
| 225 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | I'll replace the tie-break with a two-level criterion: keep exact SS delta dominant, but among eq... |
| 226 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll keep exact SS-delta dominance but change the tie-break to prefer the residual class that is ... |
| 227 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Use the classic Best-Fit rule with the SS-delta as a secondary criterion: prefer the placement wi... |
| 228 | edit | not_better | 0.9935 | 0.9952 | $0.0009 | Keep the asymptotically-optimal SS rule but add a small, sharp tie-break that penalises creating ... |
| 229 | edit | not_better | 0.7635 | 0.9952 | $0.0009 | The SS-delta is currently treated as an exact dominant integer, which creates coarse ties that th... |
| 230 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll add a "strategic reservation" tie-break: keep exact SS-delta dominance, but among equal-delt... |
| 231 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll refine the tie-break within the SS-tied group: instead of always preferring the larger resid... |
| 232 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The current SS rule is optimal in the limit but its performance is sensitive to how it treats the... |
| 233 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The SS rule's weakness is over-opening unused bins early: I'll keep exact SS-delta dominance amon... |
| 234 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll refine the tie-break so that, among placements with equal SS delta, I prefer the one whose r... |
| 235 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll replace the "prefer larger residual" tie-break with a lookahead-free "least fragmenting" tie... |
| 236 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll change the tie-break within equal-SS-delta placements to prefer the residual value that is m... |
| 237 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | (no description) |
| 238 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll add a strategic "reservation" tie-break that discourages opening brand-new bins early while ... |
| 239 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The SS rule is asymptotically optimal but the current implementation treats all "existing open bi... |
| 240 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | I'll replace the "prefer larger residual" tie-break with a complement-based one: among placements... |
| 241 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will replace the tie-break with a "best-fit" style preference only within equal SS delta: among... |
| 242 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll replace the tie-break with one that breaks equal-SS-delta ties by preferring the placement t... |
| 243 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll replace the tie-break with a backward-looking "future-fit" estimate: among equal SS-delta pl... |
| 244 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll refine the SS rule's tie-break to a "best-fit with SS dominance" that, among equal SS-delta ... |
| 245 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll replace the score encoding with a cleaner two-key ranking that keeps exact SS-delta dominanc... |
| 246 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Among placements with equal exact SS delta, prefer the smaller residual (tighter fit) instead of ... |
| 247 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | Keep exact SS-delta dominance, but break ties by choosing the placement whose residual r is small... |
| 248 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Replace the tie-break with an asymmetric rule: among equal SS-delta placements, prefer the smalle... |
| 249 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I will keep exact SS-delta dominance but replace the tie-break with a scaled two-key score that r... |
| 250 | edit | not_better | 0.9616 | 0.9952 | $0.0007 | I'll switch to the classic Best-Fit priority (minimize residual after placement) with a small bon... |
| 251 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Among equal SS-delta placements, prefer residuals that are exactly fillable by a currently-common... |
| 252 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I'll make the tie-break depend on the item size: large items (which are rare but hard to place) s... |
| 253 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The SS-delta rule is asymptotically optimal, but exact ties are frequent; I'll strengthen the tie... |
| 254 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll add a secondary global tie-break that, among placements with equal SS delta, avoids creating... |
| 255 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I will replace the fixed larger-residual tie-break with a size-aware, waste-minimizing tie-break:... |
| 256 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Keep exact SS-delta dominance, but enhance the tie-break: among equal SS deltas, prefer the place... |
| 257 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Keep the exact SS-delta rule as the dominant criterion but replace the larger-residual tie-break ... |
| 258 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will keep the exact SS-delta as the dominant criterion but replace the tie-break with a forward... |
| 259 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll switch from the unbounded sum-of-squares rule to a bounded "subharmonic" SS rule: use delta ... |
| 260 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I'll implement the classic "best fit decreasing"-style tie-break refined by the empirical result ... |
| 261 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I will make the SS delta the dominant criterion as before, but break ties by preferring the bin t... |
| 262 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current rule uses exact SS-delta dominance, but ties are broken only by larger residual. I wi... |
| 263 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I will replace the SS tie-break with a "best-fit" (smallest feasible residual) preference among e... |
| 264 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | I'll append a tiny index-based perturbation to break exact ties: among placements whose rounded p... |
| 265 | edit | not_better | 0.8203 | 0.9952 | $0.0008 | I'll shift from the exact sum-of-squares rule to a bounded/softened "Modified SS" delta via a sat... |
| 266 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | I'll replace the pure SS rule with the "Sum of Squares + negative residual" (SS with best-fit bia... |
| 267 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | I will replace the SS tie-break with a lexicographic rule that first minimizes the SS delta, then... |
| 268 | edit | not_better | 0.6283 | 0.9952 | $0.0007 | I'll replace the SS rule with the optimal online rule for this setting: the "harmonic/dominant" c... |
| 269 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I will replace the tie-break with a "least-loaded bin among equal SS delta" preference: keep the ... |
| 270 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The SS rule's tie-break is currently arbitrary among equal deltas; I will switch to preferring th... |
| 271 | edit | not_better | 0.9952 | 0.9952 | $0.0008 | The current tie-break strongly rewards large residuals which keeps too many bins half-open; I'll ... |
| 272 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Keep the exact SS delta dominant, but replace the "largest residual" tie-break with a "tightest u... |
| 273 | edit | not_better | 0.8256 | 0.9952 | $0.0007 | I'll replace the SS-style scoring with the "best-fit with a flexibility gate": use classic best-f... |
| 274 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Among placements with equal exact SS delta, prefer the smallest residual that is still at least t... |
| 275 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll make the SS criterion's value function softer by testing the "Almost-SS" rule: keep the quad... |
| 276 | edit | not_better | 0.9942 | 0.9952 | $0.0008 | Replace the "largest residual" tie-break with "smallest nonzero residual" (best-fit tie-break) am... |
| 277 | edit | not_better | 0.9593 | 0.9952 | $0.0008 | Replace the SS delta scoring with the classic "best fit" (smallest residual that fits) plus a sma... |
| 278 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I will keep the exact SS delta dominant but replace the tie-break with a "least discrimination" p... |
| 279 | edit | not_better | 0.9947 | 0.9952 | $0.0008 | The SS delta is exactly optimal only in the limit; in practice the tie-break matters. I'll break ... |
| 280 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | Keep the exact SS delta dominant, but replace the "largest residual" tie-break with one that pref... |
| 281 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll replace the SS-based rule with the well-known "Best Fit" variant that combines the SS object... |
| 282 | edit | not_better | 0.9945 | 0.9952 | $0.0008 | I'll replace the fixed "largest residual" tie-break with an adaptive one based on whether the ite... |
| 283 | edit | not_better | 0.9925 | 0.9952 | $0.0009 | Use a fractional/nonlinear "power" SS objective: instead of penalising sum of N(g)^2, use sum of ... |
| 284 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll add a small tie-break refinement on top of the exact SS delta: among equal SS deltas, prefer... |
| 285 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the rigid "largest residual" tie-break with one that, among placements of equal SS delta,... |
| 286 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current tie-break precision (multiplying SS delta by 1000 and subtracting the residual) is fr... |
| 287 | edit | not_better | 0.9937 | 0.9952 | $0.0009 | I'll replace the pure SS rule with the "SS + flexibility via a residual-closeness tie-break" but ... |
| 288 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll make the tie-break adaptive: among placements with equal SS delta, prefer the residual close... |
| 289 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | The current 1000x scaling of the exact SS delta can be perturbed by the residual tie-break when r... |
| 290 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The exact SS delta is already tight, but the "largest residual" tie-break breaks ties by flexibil... |
| 291 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Replace the raw integer SS delta with a scaled objective that also rewards reducing the number of... |
| 292 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the "largest residual" SS tie-break with a two-step criterion: among equal SS deltas, pre... |
| 293 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll replace the fragile 1000x-scaled single float with a strictly lexicographic key so the SS de... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,11 +1,13 @@
 # EVOLVE-BLOCK-START
-"""Starting program: the Sum-of-Squares rule.
+"""Sum-of-Squares rule with a flexibility-preserving tie-break.
 
-Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining capacity g
-(0 < g < 100); ties go to the tighter fit. The function is shown only the bins the item fits in, so it
-keeps its own record of every opened bin. The harness opens unused bins in index order (ties go to the
-first bin), so used bins are always a prefix of the bin array. Each instance runs in a fresh process,
-so the module-level state starts empty for every instance.
+Each item goes where it minimises sum_g N(g)^2 (the SS rule), which is asymptotically optimal
+for this class of online bin packing. The SS delta is an exact integer, so it is used as the
+dominant criterion; among placements with equal SS delta we prefer the placement that leaves
+the *larger* residual, keeping flexible free space available for future large items (instead
+of fragmenting bins to chase tight/perfect fits). The function is shown only the bins the
+item fits in, so it keeps its own record of every opened bin. Used bins are a prefix of the
+bin array; each instance runs in a fresh process.
 """
 import numpy as np
 
@@ -26,14 +28,18 @@
     fitting = [j for j, g in enumerate(_caps) if g >= s]
     n_unused = len(bins) - len(fitting)
     scores = np.empty(len(bins), dtype=np.float64)
+
     for k, j in enumerate(fitting):
         g = _caps[j]
         r = g - s
         delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)
-        scores[k] = -(delta * 1000 + r)
+        # Dominant: exact SS delta (as large negative as possible).
+        # Tie-break: prefer the larger residual (more flexible free space).
+        scores[k] = -(float(delta) * 1000.0 - r)
+
     r_new = CAP - s
     delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
-    scores[len(fitting):] = -(delta_new * 1000 + r_new)
+    scores[len(fitting):] = -(float(delta_new) * 1000.0 - r_new)
 
     choice = int(np.argmax(scores))          # the harness's choice: first highest score
     if choice < len(fitting):
```

## Explanation

Two-sided ablation of `priority` (36 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 27 | `s = int(item)` | -0.9952 | essential: the program fails or turns invalid without it |
| 28 | `fitting = [j for j, g in enumerate(_caps) if g >= s]` | -0.9952 | essential: the program fails or turns invalid without it |
| 29 | `n_unused = len(bins) - len(fitting)` | -0.9952 | essential: the program fails or turns invalid without it |
| 30 | `scores = np.empty(len(bins), dtype=np.float64)` | -0.9952 | essential: the program fails or turns invalid without it |
| 32 | `for k, j in enumerate(fitting): ...` | -0.9952 | essential: the program fails or turns invalid without it |
| 33 | `g = _caps[j]` | -0.9952 | essential: the program fails or turns invalid without it |
| 34 | `r = g - s` | -0.9952 | essential: the program fails or turns invalid without it |
| 35 | `delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)` | -0.9952 | essential: the program fails or turns invalid without it |
| 38 | `scores[k] = -(float(delta) * 1000.0 - r)` | -0.9952 | essential: the program fails or turns invalid without it |
| 40 | `r_new = CAP - s` | -0.9952 | essential: the program fails or turns invalid without it |
| 41 | `delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0` | -0.9952 | essential: the program fails or turns invalid without it |
| 42 | `scores[len(fitting):] = -(float(delta_new) * 1000.0 - r_new)` | -0.9952 | essential: the program fails or turns invalid without it |
| 44 | `choice = int(np.argmax(scores))` | -0.9952 | essential: the program fails or turns invalid without it |
| 54 | `if CAP - s > 0: ...` | -0.5991 | matters |
| 55 | `_N[CAP - s] += 1` | -0.5991 | matters |
| 49 | `_caps[j] = g - s` | -0.2355 | matters |
| 49 | `term - s` | -0.2355 | matters |
| 34 | `term - s` | -0.2292 | matters |
| 47 | `g = _caps[j]` | -0.2198 | matters |
| 50 | `if g - s > 0: ...` | -0.2029 | matters |
| 51 | `_N[g - s] += 1` | -0.2029 | matters |
| 49 | `term + g` | -0.1109 | matters |
| 46 | `j = fitting[choice]` | -0.0510 | matters |
| 35 | `term + 2 * _N[r] + 1 if r > 0 else 0` | -0.0415 | matters |
| 34 | `term + g` | -0.0364 | matters |
| 29 | `term + len(bins)` | -0.0359 | matters |
| 45 | `if choice < len(fitting): ...` | -0.0359 | matters |
| 52 | `if n_unused > 0: ...` | -0.0359 | matters |
| 53 | `_caps.append(CAP - s)` | -0.0359 | matters |
| 48 | `_N[g] -= 1` | -0.0253 | matters |
| 35 | `term + -2 * _N[g]` | -0.0089 | matters |
| 40 | `term - s` | -0.0008 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 26: `global _caps, _N`
- line 29: `term - len(fitting)`
- line 35: `term + 1`
- line 40: `term + CAP`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9952 | 0.9947 |
| minimal (4 parts removed) | 0.9945 | 0.9952 |

Minimal program:

```python
"""Sum-of-Squares rule with a flexibility-preserving tie-break.

Each item goes where it minimises sum_g N(g)^2 (the SS rule), which is asymptotically optimal
for this class of online bin packing. The SS delta is an exact integer, so it is used as the
dominant criterion; among placements with equal SS delta we prefer the placement that leaves
the *larger* residual, keeping flexible free space available for future large items (instead
of fragmenting bins to chase tight/perfect fits). The function is shown only the bins the
item fits in, so it keeps its own record of every opened bin. Used bins are a prefix of the
bin array; each instance runs in a fresh process.
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
    n_unused = len(bins)
    scores = np.empty(len(bins), dtype=np.float64)
    for k, j in enumerate(fitting):
        g = _caps[j]
        r = g - s
        delta = -2 * _N[g] + (2 * _N[r] + 1 if r > 0 else 0)
        scores[k] = -(float(delta) * 1000.0 - r)
    r_new = -s
    delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
    scores[len(fitting):] = -(float(delta_new) * 1000.0 - r_new)
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
python -m autoresearch.loop problems/bin_packing_online_ss --budget 0.6 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 0
python -m autoresearch.loop --report experiments/llm-from-ss-v1/runs/s0   # rebuild this report
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
