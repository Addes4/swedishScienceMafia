# Research loop report: bin_packing_online_ss

| | |
|---|---|
| problem | `bin_packing_online_ss` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.3095 of a $0.60 hard cap, 286 calls, 923,539 tokens |
| wall time | search 5404 s, baselines 10 s, explain 54 s |
| stopped | wall (wall_limit) |
| evaluations | 287 (285 valid), 6 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9942 | 0.9950 | |
| `best_program.py` (final incumbent) | 0.9965 | 0.9957 |  |
| baseline `best_fit` | 0.9616 | 0.9604 | `problems/bin_packing_online_ss/baselines/best_fit.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_ss/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_ss/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9965 | 0.9957 | 1 parts removed |

Audit: public 0.9942 → 0.9965 (+0.0023), hidden 0.9950 → 0.9957 (+0.0007); public − hidden gap of the final program 0.0007.

Against the baselines: the final program's public score is above the best baseline (`sum_of_squares`, 0.9942). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9940 | 0.9942 | $0.0007 | Add a secondary tie-break that, among bins with equal SoS delta, prefers the bin whose remaining ... |
| 2 | edit | not_better | 0.8203 | 0.9942 | $0.0007 | I will replace hardcoded magic constants with a more principled "weighted sum-of-squares" score t... |
| 3 | edit | not_better | 0.9616 | 0.9942 | $0.0006 | Replace the Sum-of-Squares delta rule with the classic "Best Fit" rule based on remaining capacit... |
| 4 | edit | not_better | 0.9942 | 0.9942 | $0.0007 | The SoS rule tends to spread items too evenly; a hybrid that adds a small "best-fit" bonus for ve... |
| 5 | edit | not_better | 0.9942 | 0.9942 | $0.0008 | Replace the sum-of-squares objective with the "Sum of Squares" variant that uses the classic Subs... |
| 6 | edit | improved | 0.9947 | 0.9947 | $0.0008 | I will add a bounded "perfect-fit" override: when some fitting bin has residual 0 (exact fit), se... |
| 7 | edit | not_better | 0.9915 | 0.9947 | $0.0010 | I will extend the exact-fit override to a "near-exact-fit" tier: when no bin fits exactly, but so... |
| 8 | edit | not_better | 0.9598 | 0.9947 | $0.0010 | Extend the override: after the exact-fit check, if no exact fit exists, prefer (via the same over... |
| 9 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I'll add a "subset-sum completion" override: when no exact fit exists, check whether placing the ... |
| 10 | edit | not_better | 0.9935 | 0.9947 | $0.0010 | I'll add a low-residual override tier: after the exact-fit check, if some fitting bin would be le... |
| 11 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I'll make the SoS tie-break prefer the bin whose post-placement residual is already an open capac... |
| 12 | edit | not_better | 0.9614 | 0.9947 | $0.0010 | I'll extend the exact-fit override into a "subset-sum completion" check: after the exact-fit test... |
| 13 | edit | not_better | 0.9616 | 0.9947 | $0.0009 | Replace the SoS delta with the classic "best fit + avoid rare residual sizes" rule: choose the bi... |
| 14 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll change the encoding so that the SoS delta is the primary key and the residual is only a tie-... |
| 15 | edit | not_better | 0.9947 | 0.9947 | $0.0009 | I'll test a hybrid: keep the exact-fit and SoS rule, but add a tie-break (and small override) tha... |
| 16 | edit | not_better | 0.9940 | 0.9947 | $0.0012 | Add an override (after the exact-fit check) that detects when the chosen SoS placement would leav... |
| 17 | edit | not_better | 0.9616 | 0.9947 | $0.0010 | I'll replace the sum-of-squares rule with the classic "best fit decreasing"-style rule for online... |
| 18 | edit | not_better | 0.9577 | 0.9947 | $0.0010 | I'll implement the "Sum of Squares" rule with a corrected exact-fit override that also handles th... |
| 19 | edit | not_better | 0.9940 | 0.9947 | $0.0010 | Add a size-dependent "avoid creating residually-reusable-but-rare" tie-break: keep the SoS delta ... |
| 20 | edit | not_better | 0.9940 | 0.9947 | $0.0010 | Replace the exact-fit override with a "closure" rule: prefer a placement (from a fitting bin or a... |
| 21 | edit | not_better | 0.9945 | 0.9947 | $0.0011 | Keep the SoS delta as the primary key (exact float ordering), but change the tie-break among equa... |
| 22 | edit | not_better | 0.8944 | 0.9947 | $0.0010 | The exact-fit override is a known-optimal greedy for online bin packing (it never hurts to close ... |
| 23 | edit | not_better | 0.9947 | 0.9947 | $0.0010 | I will replace the exact-fit override plus greedy SoS scoring with a "best fit" primary rule comb... |
| 24 | edit | not_better | 0.9942 | 0.9947 | $0.0014 | Keep the exact-fit override and the primary SoS delta ordering, but change the tie-break among eq... |
| 25 | edit | improved | 0.9950 | 0.9950 | $0.0009 | Make the exact-fit override more selective so it only fires when an exact fit exists among the cu... |
| 26 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | The exact-fit override can occasionally misfire, so I will instead fold exact-fit into the primar... |
| 27 | edit | not_better | 0.9947 | 0.9950 | $0.0011 | Keep the exact-fit override and the primary SoS delta ordering, but change the tie-break among eq... |
| 28 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | Fold the exact-fit override into the primary ordering more cheaply and consistently: keep the SoS... |
| 29 | edit | not_better | 0.9616 | 0.9950 | $0.0011 | I'll replace the hand-rolled tie-break with the classic Best-Fit primary rule (minimize resulting... |
| 30 | edit | not_better | 0.9950 | 0.9950 | $0.0020 | Add a second-level penalty against opening an unused bin: when an existing placement ties the SoS... |
| 31 | edit | not_better | 0.9947 | 0.9950 | $0.0009 | I will replace the fragile hand-tuned tie-break with a cleaner two-key rule: primary key is the e... |
| 32 | edit | not_better | 0.9947 | 0.9950 | $0.0010 | Replace the exact-fit override and hand-tuned class-concentration tie-break with a cleaner two-ke... |
| 33 | edit | not_better | 0.9950 | 0.9950 | $0.0012 | Keep the exact-fit override and SoS-delta primary key, but simplify and clean the secondary tie-b... |
| 34 | edit | not_better | 0.9950 | 0.9950 | $0.0010 | I will keep the exact-fit override and SoS-delta primary key, but replace the tie-break with a "c... |
| 35 | edit | not_better | 0.9950 | 0.9950 | $0.0009 | Keep the exact-fit override and SoS-delta primary key, but add a global safeguard: whenever the e... |
| 36 | edit | not_better | 0.9947 | 0.9950 | $0.0009 | The tie-break magnitudes (100000 for delta, then concentration/residual) risked making tiny nonze... |
| 37 | edit | not_better | 0.9942 | 0.9950 | $0.0010 | Replace the hand-tuned multiplicative tie-break with a clean lexicographic key: primary = SoS del... |
| 38 | edit | invalid | 0.0000 | 0.9950 | $0.0010 | I will add a "best-fit-decreasing-style" refinement: keep the SoS-delta primary key and exact-fit... |
| 39 | edit | not_better | 0.9947 | 0.9950 | $0.0010 | (no description) |
| 40 | edit | not_better | 0.9942 | 0.9950 | $0.0009 | Keep the exact-fit override and the SoS-delta primary key, but replace the hand-tuned multiplicat... |
| 41 | edit | not_better | 0.9942 | 0.9950 | $0.0009 | Replace the ad-hoc tie-break/override with the classic best-fit rule filtered by an SoS gate: kee... |
| 42 | edit | improved | 0.9952 | 0.9952 | $0.0010 | Replace the hand-tuned multiplicative tie-break with a residual-class-match tie-break: among plac... |
| 43 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Replace the "match if N[r]>=2" tie-break with a coupling-aware tie-break: among equal-delta place... |
| 44 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Add a light "best-fit after SoS ties" refinement: keep the exact-fit override and the SoS-delta p... |
| 45 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Replace the residual-class-match tie-break with a coupling-aware tie-break that, among placements... |
| 46 | edit | not_better | 0.9947 | 0.9952 | $0.0014 | Change the residual-class-match tie-break threshold from N[r]>=2 to N[r]>=1 (for both fitting-bin... |
| 47 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | Replace the exact-fit override and SoS-delta primary key with a "best-fit with residual-class tie... |
| 48 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | Replace the brittle SoS-delta primary key with a provably-optimal online rule that tracks, for ea... |
| 49 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Introduce a bounded lookahead that anticipates the next item's most likely size range: keep the S... |
| 50 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Keep the SoS-delta primary key but replace the brittle fixed-scale tie-breaks with a cleaner lexi... |
| 51 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Replace the fragile hard-coded tie-break weights with a single well-scaled score combining the So... |
| 52 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | Add a "worst-fit among tied bins" secondary tie-break instead of the match heuristic: among place... |
| 53 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Keep the exact-fit override and SoS-delta primary key, but change the secondary tie-break to pref... |
| 54 | edit | not_better | 0.9515 | 0.9952 | $0.0011 | Replace the SoS-delta primary key with a randomized fixed-fraction approach: use the classic "har... |
| 55 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | The exact-fit override only looks at existing bins even though the best-fit math already prefers ... |
| 56 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | I'll replace the hand-crafted SoS rule with the classic Best-Fit rule (place the item in the fitt... |
| 57 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll keep the sum-of-squares primary key, but replace the brittle match/smaller-residual tie-brea... |
| 58 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | The exact-fit override currently searches only existing bins, but the SoS primary key already han... |
| 59 | edit | not_better | 0.9947 | 0.9952 | $0.0013 | Refine the secondary tie-break to reward complementarity directly: among equal SoS-delta placemen... |
| 60 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | I'll replace the brittle SoS-delta + heuristic tie-break with a cleaner formulation: primary key ... |
| 61 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | Add a lookahead-style adjustment: instead of ranking placements purely by the immediate sum-of-sq... |
| 62 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | The exact-fit override currently only considers existing bins, but a fresh bin can also produce a... |
| 63 | edit | not_better | 0.9942 | 0.9952 | $0.0011 | Remove the fragile multiplicative tie-break encoding (the 1e5/100/+1.0 weighting) which can disto... |
| 64 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | I'll add an adaptive "bucket-pairing" tie-break to the exact-fit override: when no exact fit exis... |
| 65 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | Replace the noisy multiplicative tie-break encoding with a clean lexicographic float key: primary... |
| 66 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The tie-break on SoS deltas has been consistently hurting or neutral, and the exact-fit override ... |
| 67 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I'll change the tie-break from a heuristic-based encoding to a much stronger, well-known rule: am... |
| 68 | edit | not_better | 0.9614 | 0.9952 | $0.0009 | Replace the fragile sum-of-squares objective with the standard "best fit with complement pairing"... |
| 69 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Use a scale-free SoS delta (divide by current open-bin count) so the comparison is by relative gr... |
| 70 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | The exact-fit override currently ignores a fresh bin when the item size is 100; more importantly,... |
| 71 | edit | not_better | 0.9942 | 0.9952 | $0.0011 | I'll replace the fragile weighted-score encoding with a clean, mathematically-principled selectio... |
| 72 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll switch the primary ranking to a rotation-aware metric that penalizes creating a residual unl... |
| 73 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | All recent tie-break heuristics have been neutral or harmful, so I'll revert to the clean pure So... |
| 74 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I'll add a "permanent pair-closure" mechanism: maintain a second count N2[g] of bins that are "co... |
| 75 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | I'll switch the primary rule from sum-of-squares to a scale-free "best-fit with look-ahead weight... |
| 76 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | The previous tie-break attempts all failed because they added ad-hoc terms, so I'll instead keep ... |
| 77 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the heuristic exact-fit override and tie-breaks with a "best-fit + sum-of-squares" hybrid... |
| 78 | edit | not_better | 0.9673 | 0.9952 | $0.0009 | I'll keep pure SoS-delta as the primary key (that was the best-performing), but replace the hard ... |
| 79 | edit | not_better | 0.9616 | 0.9952 | $0.0009 | I'll replace the SoS rule with a "best-fit decreasing-like" scale-aware rule that is the classic ... |
| 80 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | Replace the ad-hoc secondary/tertiary tie-breaks with a principled consolidation tie-break: among... |
| 81 | edit | not_better | 0.9940 | 0.9952 | $0.0010 | I'll add a targeted "complementary exact-fit reservation" rule: among non-exact SoS-optimal place... |
| 82 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the hard exact-fit override and the ad-hoc tie-breaks with a single clean formulation: ra... |
| 83 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | Keep the pure SoS-delta primary key and the exact-fit override, but change the tie-break among So... |
| 84 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Keep the exact-fit override and the pure SoS-delta primary key, but refine the tie-break: among S... |
| 85 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | I'll replace the heuristic secondary/tertiary tie-breaks with a principled "best-fit among SoS-op... |
| 86 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Add a small look-ahead-free "pairing" bonus: among SoS-optimal non-exact placements, prefer the r... |
| 87 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I will keep the exact-fit override and the SoS-delta primary key, but change the tie-break to the... |
| 88 | edit | not_better | 0.9940 | 0.9952 | $0.0010 | The ad-hoc tie-breaks are unreliable; instead, I'll make the exact-fit override smarter by additi... |
| 89 | edit | not_better | 0.9952 | 0.9952 | $0.0009 | I'll replace the fixed tertiary tie-break with a small randomized perturbation that depends on th... |
| 90 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll exact-fit-override the SoS rule with a proper "harmonic/dominant-pair" secondary criterion: ... |
| 91 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | I will replace the exact-fit override plus SoS-delta primary with a strict lexicographic comparis... |
| 92 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I'll make the exact-fit override smarter: when no exact fit exists, keep the SoS-delta primary ke... |
| 93 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I will keep the exact-fit override and the SoS-delta primary key, but replace the hand-tuned seco... |
| 94 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | I'll replace the exact-fit override with a principled one-step-lookahead that, among all placemen... |
| 95 | edit | not_better | 0.9593 | 0.9952 | $0.0009 | I'll switch the primary criterion from the SoS-delta (which is a myopic greedy on the class-count... |
| 96 | edit | not_better | 0.9947 | 0.9952 | $0.0012 | I'll implement the classic "sum of squares" delta but with the exact-fit override chosen only whe... |
| 97 | edit | not_better | 0.9952 | 0.9952 | $0.0014 | I unify the exact-fit into a secondary tie-break within the SoS-delta primary (instead of a hard ... |
| 98 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | I'll refine the exact-fit override so that it fires not only on an exact fit but also when the pl... |
| 99 | edit | not_better | 0.9942 | 0.9952 | $0.0012 | I will compute, for each candidate placement, the exact post-placement sum-of-squares cost of the... |
| 100 | edit | not_better | 0.9905 | 0.9952 | $0.0011 | I'll add a "future-fit" tie-break: among placements with the minimal SoS delta (with the exact-fi... |
| 101 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | I'll add a lightweight randomized/greedy class-merging refinement: keep the exact-fit override an... |
| 102 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | I'll replace the fragile multi-magic-multiplier key with a single exact integer-valued primary ke... |
| 103 | edit | not_better | 0.9950 | 0.9952 | $0.0011 | Replace the fragile magic-multiplier key with a clean lexicographic key: primary = exact SoS-delt... |
| 104 | edit | not_better | 0.6756 | 0.9952 | $0.0011 | I'll replace the magic-multiplier scoring with a single exact integer primary key = true change i... |
| 105 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll replace the heuristic tie-break with a "best-fit decreasing-aware" rule: primary key stays t... |
| 106 | edit | not_better | 0.9605 | 0.9952 | $0.0010 | I'll replace the SoS-delta primary score with a bounded variant that caps each residual-class cou... |
| 107 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | I'll keep the exact-fit override and the SoS-delta primary key, but replace the fragile magic-mul... |
| 108 | edit | not_better | 0.9940 | 0.9952 | $0.0010 | I'll keep the exact-fit override and SoS-delta primary key, but change the tie-break to prefer th... |
| 109 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll introduce a small, cheap look‑ahead using the known item distribution: keep the exact-fit ov... |
| 110 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I will keep the exact-fit override and SoS-delta primary key, but break ties by explicitly favour... |
| 111 | edit | not_better | 0.9478 | 0.9952 | $0.0010 | Keep the exact-fit hard override and the exact integer SoS-delta primary key, but change the tie-... |
| 112 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | Increase the influence of the "matching" tie-break by making the secondary key depend on compleme... |
| 113 | edit | not_better | 0.9947 | 0.9952 | $0.0015 | I'll keep the exact-fit override and the exact SoS-delta primary key, but replace the tie-break w... |
| 114 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | Add a light look-ahead using the known item distribution: among placements with equal SoS delta, ... |
| 115 | edit | not_better | 0.9598 | 0.9952 | $0.0010 | I'll eliminate the fragile `_caps` mirror entirely and derive everything directly from `bins`: fi... |
| 116 | edit | invalid | 0.0000 | 0.9952 | $0.0010 | I'll keep the exact-fit override and SoS-delta primary key, but change the tie-break to prefer th... |
| 117 | edit | not_better | 0.9623 | 0.9952 | $0.0009 | I'll keep the exact-fit override and the SoS-delta primary key, but replace the fragile `_caps` b... |
| 118 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | I will keep the SoS-delta primary key but replace the tie-break with a distribution-aware expecte... |
| 119 | edit | not_better | 0.9952 | 0.9952 | $0.0016 | I'll replace the ad-hoc tie-break with a proper one-step look-ahead: among placements with equal ... |
| 120 | edit | not_better | 0.9947 | 0.9952 | $0.0012 | Introduce a small randomized/exploratory element that occasionally deviates from the greedy SoS r... |
| 121 | edit | not_better | 0.9940 | 0.9952 | $0.0009 | I'll replace the exact-fit hard override with the pure SoS-delta primary key (exact fit already y... |
| 122 | edit | not_better | 0.9947 | 0.9952 | $0.0012 | I'll change the primary criterion from the SoS-delta to a direct estimate of the number of bins c... |
| 123 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | I'll keep the proven SoS-delta primary key and exact-fit override, but improve the tie-break by p... |
| 124 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | I will add a bias against opening unused bins when the item also fits in existing bins: rather th... |
| 125 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | Keep the SoS-delta primary key, but change the tie-break: instead of the weak "match" flag, prefe... |
| 126 | edit | not_better | 0.9947 | 0.9952 | $0.0016 | Replace the ad-hoc match/smaller-residual tie-break with a one-step expected-SoS look-ahead: amon... |
| 127 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | The SoS delta tie-break has been a source of noise. I'll replace the weak "match" flag tie-break ... |
| 128 | edit | not_better | 0.9616 | 0.9952 | $0.0008 | The is simplified to a clean Best-Fit / tightest-fit rule: among all fitting bins (including unus... |
| 129 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | I'll add a bounded one-step look-ahead that, among placements, chooses the one minimizing the SoS... |
| 130 | edit | not_better | 0.9497 | 0.9952 | $0.0010 | The SoS tie-breaks have been adding noise. I'll keep the exact-fit override and the SoS-delta pri... |
| 131 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Replace the noisy tiered tie-break with a clean comparison: keep the exact-fit override and the S... |
| 132 | edit | not_better | 0.9945 | 0.9952 | $0.0009 | The current code breaks the SoS-delta tie-break in a way that adds noise. I'll remove the seconda... |
| 133 | edit | not_better | 0.9947 | 0.9952 | $0.0012 | I'll replace the noisy tiered tie-break with a principled secondary key derived directly from the... |
| 134 | edit | not_better | 0.9947 | 0.9952 | $0.0019 | I'll compute the Exact-Fit override but then use the SoS delta as primary with a tie-break that m... |
| 135 | edit | not_better | 0.9478 | 0.9952 | $0.0010 | Replace the fragile tiered tie-break with a clean scalar score: primary SoS delta, and among equa... |
| 136 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll keep the exact-fit override and the SoS-delta as the primary criterion, but replace the fixe... |
| 137 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | I'll replace the ad-hoc tiered tie-break with a principled secondary key: among placements, keep ... |
| 138 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | I'll replace the noisy tiered tie-break with a clean, exact one-step lookahead: keep exact-fit ov... |
| 139 | edit | not_better | 0.9952 | 0.9952 | $0.0012 | I'll add a primary key that penalizes opening a brand-new bin: since opening a new bin is never c... |
| 140 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | The current scores encode a new-bin opening as delta=0, so a gap equal to the item size (which ze... |
| 141 | edit | not_better | 0.9593 | 0.9952 | $0.0009 | I'll replace the fragile floating-point tiered tie-break with a robust lexicographic scoring usin... |
| 142 | edit | not_better | 0.9947 | 0.9952 | $0.0028 | Keep the exact-fit override and the exact SoS-delta as the primary key, but replace the ad-hoc "m... |
| 143 | edit | not_better | 0.9950 | 0.9952 | $0.0011 | I'll replace the noisy hand-tuned tiered tie-break with an exact one-step tie-break that, among e... |
| 144 | edit | not_better | 0.9947 | 0.9952 | $0.0013 | I'll replace the fragile `>=2` match tier with a robust consolidation tie-break: among placements... |
| 145 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | Replace the exact-fit-only override with a stronger "leave the smallest positive residual" heuris... |
| 146 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | The current code uses exact-fit as the only override and otherwise a hand-tuned tiered tie-break;... |
| 147 | edit | not_better | 0.9947 | 0.9952 | $0.0009 | Replace the hand-tuned tiered tie-break with a "least-loaded valid fit" secondary key: keep the e... |
| 148 | edit | not_better | 0.9947 | 0.9952 | $0.0013 | Replace the fragile float-magic tiered scoring with a robust lexicographic key: primary = exact S... |
| 149 | edit | not_better | 0.9950 | 0.9952 | $0.0009 | I will keep the exact SoS-delta primary and exact-fit override, but replace the fragile float-enc... |
| 150 | edit | not_better | 0.9942 | 0.9952 | $0.0010 | Replace the ad-hoc hand-tuned tie-break tiers with a principled secondary key: among placements w... |
| 151 | edit | not_better | 0.9942 | 0.9952 | $0.0009 | Replace the exact-fit override and hand-tuned tie-break with the classic "best-fit over the SoS-o... |
| 152 | edit | not_better | 0.9947 | 0.9952 | $0.0010 | Keep the SoS-delta primary but replace the hand-tuned "match" tier with a cleaner rule: among equ... |
| 153 | edit | not_better | 0.9945 | 0.9952 | $0.0010 | The current exact-fit override is too rigid: it always closes an exactly-filled bin, but this can... |
| 154 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | Keep the current best-performing structure (exact-fit override + SoS-delta primary + hand-tuned t... |
| 155 | edit | not_better | 0.9950 | 0.9952 | $0.0011 | Add a one-step "future fit" override: before using the SoS delta, check whether some placement cr... |
| 156 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | The exact-fit override skips the SoS-delta calculation entirely, but closing a bin isn't always o... |
| 157 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | I will keep the proven SoS-delta primary, exact-fit override, and tiered tie-break, but change th... |
| 158 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | I will keep the proven structure but fix a subtle flaw: the exact-fit override currently selects ... |
| 159 | edit | not_better | 0.9952 | 0.9952 | $0.0011 | Replace the per-bin O(n) Python loop in `priority` with vectorized numpy over the item's fitting ... |
| 160 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | Add a "complementary fit" override: when no exact fit exists, prefer placing the item so that the... |
| 161 | edit | not_better | 0.9945 | 0.9952 | $0.0011 | I will keep the proven SoS-delta primary and exact-fit override, but enrich the tie-break: instea... |
| 162 | edit | not_better | 0.9952 | 0.9952 | $0.0010 | The current rule never exploits the fact that the best bin packing heuristics for this distributi... |
| 163 | edit | not_better | 0.9950 | 0.9952 | $0.0010 | I will adjust the primary SoS-delta computation so it treats the exact-fit override as redundant:... |
| 164 | edit | not_better | 0.9947 | 0.9952 | $0.0011 | I'll add a one-step "closeability" bonus to the tie-break: among placements with equal primary So... |
| 165 | edit | improved | 0.9957 | 0.9957 | $0.0016 | I'll replace the plain sum-of-squares potential with a capacity-weighted one: minimize sum_g (100... |
| 166 | edit | not_better | 0.9945 | 0.9957 | $0.0011 | I'll strengthen the class weight from 100/g to (100/g)^1.5, which penalizes multiplying near-full... |
| 167 | edit | improved | 0.9960 | 0.9960 | $0.0012 | The weight exponent 1.0 improved over 1.5 (which was too aggressive), suggesting the optimum lies... |
| 168 | edit | not_better | 0.9950 | 0.9960 | $0.0011 | Raise the capacity-weight exponent from 0.8 to 0.85, since 0.8 beat both 0.0 and 1.0 and the opti... |
| 169 | edit | not_better | 0.9960 | 0.9960 | $0.0011 | I'll replace the binary class-match tie-break with a graded one that rewards residuals matching a... |
| 170 | edit | not_better | 0.9960 | 0.9960 | $0.0011 | The class-match tie-break currently rewards a placement only when the resulting residual matches ... |
| 171 | edit | not_better | 0.9955 | 0.9960 | $0.0011 | I will make the capacity-weight exponent adaptive: instead of a fixed 0.8, use a slightly larger ... |
| 172 | edit | not_better | 0.9952 | 0.9960 | $0.0013 | I'll add a "complementary closure" bonus at the primary decision level: beyond the exact-fit over... |
| 173 | edit | not_better | 0.9952 | 0.9960 | $0.0012 | I'll increase the capacity-weight exponent slightly from 0.8 to 0.82 (a fine step toward the regi... |
| 174 | edit | not_better | 0.9960 | 0.9960 | $0.0011 | I'll add a secondary "complementary closure" term that rewards placements whose resulting residua... |
| 175 | edit | not_better | 0.9957 | 0.9960 | $0.0011 | I'll shift from a hard exact-fit override to a smoother rule: keep the weighted sum-of-squares po... |
| 176 | edit | not_better | 0.9955 | 0.9960 | $0.0011 | Replace the hardcoded item-size-independent tie-break scale with a scale that depends only on the... |
| 177 | edit | not_better | 0.9616 | 0.9960 | $0.0008 | I'll replace the heavily hand-tuned potential-plus-tiebreak rule with the classic Best Fit rule (... |
| 178 | edit | not_better | 0.9960 | 0.9960 | $0.0011 | The class-match tie-break is applied too coarsely; I'll change it to reward the resulting residua... |
| 179 | edit | not_better | 0.9957 | 0.9960 | $0.0012 | I will replace the fixed exponent with a value derived from a running estimate of the mean item s... |
| 180 | edit | not_better | 0.9960 | 0.9960 | $0.0012 | I'll replace the ad-hoc class-match tie-break with a graded bonus proportional to the observed fr... |
| 181 | edit | not_better | 0.9960 | 0.9960 | $0.0011 | I'll keep the weighted sum-of-squares potential but replace the item-agnostic class-count tie-bre... |
| 182 | edit | gate_rejected | 0.9960 | 0.9960 | $0.0012 | The current rule treats all residual classes symmetrically through the weighted sum-of-squares po... |
| 183 | edit | improved | 0.9965 | 0.9965 | $0.0012 | I'll keep the weighted sum-of-squares potential with exponent 0.8, but change the tie-break direc... |
| 184 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | I'll replace the fixed myopic exact-fit-only override with a broader "closure-friendly" override:... |
| 185 | edit | not_better | 0.9960 | 0.9965 | $0.0010 | I'll replace the coarse per-candidate potential scoring with a Cython-free vectorized "dual feasi... |
| 186 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll keep the potential (exponent 0.8) and exact-fit override, but replace the tie-break with one... |
| 187 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | I will add a deterministic look-ahead "sum" override: before applying the potential rule, if the ... |
| 188 | edit | not_better | 0.9960 | 0.9965 | $0.0013 | I'll replace the fixed potential exponent 0.8 with a small adaptive scheme: track the total item ... |
| 189 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | Replace the exact-fit-only override with a broader "match an existing open residual" override: if... |
| 190 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I will add a small asymmetric weighting to the potential that slightly favors placing items into ... |
| 191 | edit | not_better | 0.9945 | 0.9965 | $0.0011 | I'll switch the penalty exponent for residual-class counts from the smooth 0.8 to a sharper near-... |
| 192 | edit | not_better | 0.9945 | 0.9965 | $0.0011 | I will replace the current fixed exponential class-weight potential with a vectorized linear/quad... |
| 193 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I will introduce a running histogram of observed item sizes and add a small bonus to the potentia... |
| 194 | edit | not_better | 0.9957 | 0.9965 | $0.0012 | Keep the sum-of-squares potential and exact-fit override, but generalize the exact-fit override i... |
| 195 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | The exact-fit override is essentially never hit for large items, and the main failure is fragment... |
| 196 | edit | not_better | 0.9903 | 0.9965 | $0.0013 | I'll extend the exact-fit override into a bounded "complement" override: if a fitting bin's resid... |
| 197 | edit | not_better | 0.9952 | 0.9965 | $0.0010 | The exact-fit override currently requires residual 0 exactly, which is rare; I'll add a bounded "... |
| 198 | edit | not_better | 0.9955 | 0.9965 | $0.0012 | I'll revert to the original 0.996478 configuration and tune the potential exponent down slightly ... |
| 199 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | Add a small "closing" bonus to the potential-based score that rewards placements whose resulting ... |
| 200 | edit | not_better | 0.9957 | 0.9965 | $0.0012 | I will make the exact placement-choice deterministic and score-free by computing the best candida... |
| 201 | edit | not_better | 0.9957 | 0.9965 | $0.0017 | I will replace the fixed hand-tuned potential with a small, principled search over the exponent p... |
| 202 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I'll set the weighting exponent to p=1.0 (the unweighted sum-of-squares potential, which is known... |
| 203 | edit | not_better | 0.9616 | 0.9965 | $0.0009 | Replace the weighted potential rule with the well-known "best-fit decreasing"-style greedy expres... |
| 204 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll switch the tie-break from a dense float encoding to a cleaner lexicographic rule that prefer... |
| 205 | edit | not_better | 0.9965 | 0.9965 | $0.0013 | Add an adaptive term that tracks the frequency of recently-arrived item sizes and gives a small b... |
| 206 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | I will add an adaptive "residual matches a frequently-seen recent item size" bonus to the placeme... |
| 207 | edit | not_better | 0.9605 | 0.9965 | $0.0009 | Replace the heuristic weighted sum-of-squares potential with a "best-fit with exact-fit override"... |
| 208 | edit | not_better | 0.9593 | 0.9965 | $0.0012 | I'll reduce the magic multiplier 100000.0 (which can cause float precision loss when delta differ... |
| 209 | edit | not_better | 0.9955 | 0.9965 | $0.0013 | Introduce a numeric heuristic "complement pairing" rule: in addition to the weighted sum-of-squar... |
| 210 | edit | not_better | 0.9962 | 0.9965 | $0.0012 | I'll replace the blended-float score (prec) with a strict lexicographic tuple comparison: primary... |
| 211 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | Change the weighting exponent _P from 0.8 to 0.7, which shifts the balance between penalizing nea... |
| 212 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | Introduce a "closing discount": when a placement's resulting residual r is exactly 0 OR matches a... |
| 213 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | Replace the fixed exponential class weight (100/g)^0.8 with a tunable exponent that also applies ... |
| 214 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I will add a "perfect complement" override: if no exact fit exists, but placing the item leaves a... |
| 215 | edit | not_better | 0.9960 | 0.9965 | $0.0011 | I'll replace the fixed exponential class weight with a dynamic programming-style "look-ahead-free... |
| 216 | edit | not_better | 0.9950 | 0.9965 | $0.0011 | I'll sweep the weighting exponent p more finely and also test a variant where the match bonus use... |
| 217 | edit | not_better | 0.9947 | 0.9965 | $0.0011 | Replace the exponential class weight (100/g)^p with a "harmonic" weight 1/g probability-style ter... |
| 218 | edit | not_better | 0.9429 | 0.9965 | $0.0011 | Replace the static potential with a "best-fit with residual-class matching" rule: primary key pre... |
| 219 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | The current potential treats all open-bin residual classes independently; I will add a small "ite... |
| 220 | edit | not_better | 0.9965 | 0.9965 | $0.0015 | Add a small "future-fit value" refinement to the secondary key: track the empirical frequency of ... |
| 221 | edit | not_better | 0.9957 | 0.9965 | $0.0012 | I'll replace the fixed secondary tie-break with a smarter one that prefers placements which reduc... |
| 222 | edit | not_better | 0.9965 | 0.9965 | $0.0022 | I'll simplify the tie-break: the graded "match" bonus (weight 100) only fires on near-equal poten... |
| 223 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll add a "best-fit-decreasing-like" secondary refinement: among placements with equal potential... |
| 224 | edit | not_better | 0.9960 | 0.9965 | $0.0010 | I'll replace the deterministic rule's tie-break with a randomized restart-free approach: keep the... |
| 225 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I will treat the residual left behind as having value for the next item rather than just a weight... |
| 226 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I will tune the potential exponent p from 0.8 to 0.6 (adjusting only the module-level `_P` consta... |
| 227 | edit | not_better | 0.9962 | 0.9965 | $0.0009 | Replace the crude 0/1 "exact-fit override" with a full-greedy that still uses the potential delta... |
| 228 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll change the potential exponent p from 0.8 to 0.7 and simplify the final tie-break to pure bes... |
| 229 | edit | not_better | 0.9957 | 0.9965 | $0.0010 | I'll implement a two-tier scoring rule that first targets the exact-fit/potential objective but a... |
| 230 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll add a small secondary preference for placing the item into an existing bin before opening a ... |
| 231 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll add a light "residual pairing" term to the tie-break: among placements with (nearly) equal p... |
| 232 | edit | not_better | 0.9942 | 0.9965 | $0.0010 | I'll replace the weighted-class-count potential with a finer-grained "residual usefulness" potent... |
| 233 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | I will replace the fixed class-count potential with a scaled additive tie-break that gives a bonu... |
| 234 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | Add a scaled "completion-value" tie-break: among placements with (nearly) equal potential delta, ... |
| 235 | edit | not_better | 0.9957 | 0.9965 | $0.0010 | Replace the disable-by-default perturbation with a genuine, deterministic improvement: change the... |
| 236 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll refine the sum-of-squares rule by raising the exact-fit override to also cover the case wher... |
| 237 | edit | not_better | 0.9957 | 0.9965 | $0.0010 | I'll make the weighted sum-of-squares potential use the observed item-size distribution: weight e... |
| 238 | edit | not_better | 0.9960 | 0.9965 | $0.0010 | I'll add a bounded "best-fit-decreasing-inspired" refinement to the potential: instead of always ... |
| 239 | edit | not_better | 0.9947 | 0.9965 | $0.0012 | I'll add a "residual diversity" refinement: within placements whose potential delta is essentiall... |
| 240 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I will replace the heuristic potential-delta ranking with a direct "future-expected-waste" evalua... |
| 241 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | The current rule is a strong packed-class potential but it ignores the actual sequence: I'll add ... |
| 242 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll make the exact-fit override more effective by also closing bins via a perfect complement: wh... |
| 243 | edit | not_better | 0.9947 | 0.9965 | $0.0014 | I'll replace the heuristic delta ranking with a lookahead that evaluates each candidate placement... |
| 244 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I'll reduce the exact-fit override's fragility by removing the "graded match bonus" and the resid... |
| 245 | edit | not_better | 0.9950 | 0.9965 | $0.0010 | I'll replace the hard exact-fit override with a soft bonus proportional to the potential savings,... |
| 246 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I'll increase the potential exponent _P from 0.8 to 1.0 so the rule penalizes scattering residual... |
| 247 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll change the potential exponent _P from 0.8 to 0.9 (a midpoint between the best-known 0.8 and ... |
| 248 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll make the exact-fit override cooperate with the potential rule by also treating near-exact fi... |
| 249 | edit | not_better | 0.9965 | 0.9965 | $0.0010 | I'll replace the ad-hoc fixed tie-break multipliers with a single unified priority that uses the ... |
| 250 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | The exact-fit override currently gives up when no bin is exactly full, so I'll generalize it: com... |
| 251 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll add a small, data-driven tie-break to the exact-fit override: among all exact-fitting bins c... |
| 252 | edit | not_better | 0.9950 | 0.9965 | $0.0012 | I'll replace the fixed exponent rule with an adaptive one: track the number of items processed an... |
| 253 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | The current rule's tie-break uses arbitrary multipliers and ignores the interaction between the i... |
| 254 | edit | not_better | 0.9960 | 0.9965 | $0.0011 | I'll replace the exact-fit override (which only fires on residual 0 and ignores the bin-selection... |
| 255 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I'll replace the hard-coded exact-fit override with a small residual-closure bonus inside the pot... |
| 256 | edit | not_better | 0.9957 | 0.9965 | $0.0012 | I'll replace the ad-hoc match bonus with a learned, distribution-aware tie-break: track the histo... |
| 257 | edit | not_better | 0.9952 | 0.9965 | $0.0010 | I'll retune the potential exponent and, more importantly, replace the crude tie-break with a prin... |
| 258 | edit | not_better | 0.9965 | 0.9965 | $0.0012 | I'll add a "perfect-completion" bias: compute for each candidate placement the residual r, and if... |
| 259 | edit | not_better | 0.9957 | 0.9965 | $0.0010 | The ad-hoc match/100x/100000x tie-break weights are arbitrary and hurt on some instances; I'll sh... |
| 260 | edit | not_better | 0.9957 | 0.9965 | $0.0012 | I'll lower the potential exponent from 0.8 to 0.65 (a value not yet tested that stays close to th... |
| 261 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll replace the potential exponent with a sum-of-nonlinear-cost formulation that better captures... |
| 262 | edit | not_better | 0.9960 | 0.9965 | $0.0010 | The current rule's per-class linear/quadratic potential ignores that most items are large, so res... |
| 263 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll add a light "compatibility" refinement: replace the arbitrary graded match bonus with a per-... |
| 264 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll make the exact-fit override smarter: currently it greedily takes the first exact-fit bin, bu... |
| 265 | edit | not_better | 0.9960 | 0.9965 | $0.0012 | I'll keep the exact-fit override and the weighted sum-of-squares potential as the primary key, bu... |
| 266 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | The current primary key scales the potential delta by 100000 and folds residual-size into the sam... |
| 267 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | I'll strengthen the primary rule by replacing the ad-hoc weighted-sum-of-squares potential with a... |
| 268 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll tune the potential exponent p upward from 0.8 to 0.9 — the sum-of-squares term (2N+1) is mor... |
| 269 | edit | not_better | 0.9955 | 0.9965 | $0.0012 | I'll lower the potential exponent from 0.8 to 0.7, which reduces the over-penalization of splitti... |
| 270 | edit | not_better | 0.9957 | 0.9965 | $0.0011 | I'll normalize the item sizes into a coarse "harmony" objective: instead of the raw potential del... |
| 271 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | The current score key packs the potential delta and tie-breaks into one float with a huge 100000 ... |
| 272 | edit | not_better | 0.9950 | 0.9965 | $0.0012 | The scoring used a single packed float with a 100000x multiplier, which let the tie-break terms l... |
| 273 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | The many recent tie-break variations all regressed, so I'll revert to the proven structure but re... |
| 274 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | Replace the potential-delta primary key with a dedicated Best-Fit-style score: among fitting bins... |
| 275 | edit | not_better | 0.9962 | 0.9965 | $0.0010 | The exact-fit override is currently only checked among bins I have already opened (the "fitting" ... |
| 276 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | I'll keep the proven potential-delta structure but cleanly separate the exact-fit override from t... |
| 277 | edit | not_better | 0.9878 | 0.9965 | $0.0012 | I'll add a small "perfect-complement" override that fires before the potential-delta comparison: ... |
| 278 | edit | not_better | 0.9962 | 0.9965 | $0.0013 | The scoring currently uses a single packed float whose 100000x multiplier lets the match/residual... |
| 279 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | I'll retain the exact-fit override and primary potential-delta key, but replace the crude float-p... |
| 280 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | I'll replace the fixed exponent p=0.8 weighted potential with a parameterized class-weight that a... |
| 281 | edit | not_better | 0.9955 | 0.9965 | $0.0011 | Recent small tweaks all regressed, so I'll make a more substantive change: rather than a fixed ex... |
| 282 | edit | not_better | 0.9593 | 0.9965 | $0.0008 | I'll replace the capacity-weighted sum-of-squares potential (which uses a fixed exponent p) with ... |
| 283 | edit | not_better | 0.9616 | 0.9965 | $0.0009 | I'll switch the primary placement rule from the fixed-exponent potential-delta to a "Best-Fit wit... |
| 284 | edit | not_better | 0.9965 | 0.9965 | $0.0011 | The current rule ignores bin index ordering when the residual is 100 (unused bins): a tie among u... |
| 285 | edit | not_better | 0.9962 | 0.9965 | $0.0012 | Added an exponentially-smoothed arrival-size histogram and a strictly subordinate "future-fill" t... |
| 286 | edit | not_better | 0.9962 | 0.9965 | $0.0011 | I'll keep the proven capacity-weighted sum-of-squares potential as the primary rule but change th... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,17 +1,23 @@
 # EVOLVE-BLOCK-START
-"""Starting program: the Sum-of-Squares rule.
+"""Capacity-weighted sum-of-squares rule with exact-fit override and fuller-bin tie-break.
 
-Each item goes where it minimises sum_g N(g)^2, where N(g) counts open bins with remaining capacity g
-(0 < g < 100); ties go to the tighter fit. The function is shown only the bins the item fits in, so it
-keeps its own record of every opened bin. The harness opens unused bins in index order (ties go to the
-first bin), so used bins are always a prefix of the bin array. Each instance runs in a fresh process,
-so the module-level state starts empty for every instance.
+Each item goes where it minimises the potential P = sum_g (100/g)^p * N(g)^2, where N(g) counts
+open bins with remaining capacity g (0 < g < 100). The weighting exponent p balances how much the
+rule penalizes multiplying near-full residual classes versus counts of large-residual classes.
+If some fitting bin can take the item exactly (residual 0), that bin is chosen instead, since
+closing a bin is always at least as good as any other placement. Ties on the potential delta go to
+the placement whose resulting residual matches a more common existing open class (graded by count),
+and then to the bin leaving the smaller residual (fuller bin first). The function is shown only the
+bins the item fits in, so it keeps its own record of every opened bin; used bins are always a prefix
+of the bin array. Each instance runs in a fresh process, so module-level state starts empty.
 """
 import numpy as np
 
 CAP = 100
+_P = 0.8
 _caps = []                     # remaining capacity of every opened bin, in bin-index order
 _N = [0] * (CAP + 1)           # N[g]: open bins with remaining capacity g, 0 < g < CAP
+_W = [((CAP / g) ** _P) if g > 0 else 0.0 for g in range(CAP + 1)]  # class weight
 
 
 def priority(item, bins):
@@ -26,16 +32,35 @@
     fitting = [j for j, g in enumerate(_caps) if g >= s]
     n_unused = len(bins) - len(fitting)
     scores = np.empty(len(bins), dtype=np.float64)
+
+    # Exact-fit override: only when an existing fitting bin's residual after placement is 0.
+    exact_pos = -1
     for k, j in enumerate(fitting):
-        g = _caps[j]
-        r = g - s
-        delta = -2 * _N[g] + 1 + (2 * _N[r] + 1 if r > 0 else 0)
-        scores[k] = -(delta * 1000 + r)
-    r_new = CAP - s
-    delta_new = 2 * _N[r_new] + 1 if r_new > 0 else 0
-    scores[len(fitting):] = -(delta_new * 1000 + r_new)
+        if _caps[j] == s:
+            exact_pos = k
+            break
+    if exact_pos >= 0:
+        scores[:] = 0.0
+        scores[exact_pos] = 1.0
+        choice = exact_pos
+    else:
+        for k, j in enumerate(fitting):
+            g = _caps[j]
+            r = g - s
+            # weighted potential delta: -w_g*(2N[g]-1) + (w_r*(2N[r]+1) if r>0 else 0)
+            delta = -_W[g] * (2 * _N[g] - 1)
+            if r > 0:
+                delta += _W[r] * (2 * _N[r] + 1)
+            # graded match bonus: reward residuals matching a more common open class
+            match = _N[r] if r > 0 else 0
+            # tie-break prefers fuller bins (smaller residual)
+            scores[k] = -(delta * 100000.0 + match * 100.0 + r)
+        r_new = CAP - s
+        delta_new = _W[r_new] * (2 * _N[r_new] + 1) if r_new > 0 else 0.0
+        match_new = _N[r_new] if r_new > 0 else 0
+        scores[len(fitting):] = -(delta_new * 100000.0 + match_new * 100.0 + r_new)
+        choice = int(np.argmax(scores))
 
-    choice = int(np.argmax(scores))          # the harness's choice: first highest score
     if choice < len(fitting):
         j = fitting[choice]
         g = _caps[j]
```

## Explanation

Two-sided ablation of `priority` (46 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 31 | `s = int(item)` | -0.9965 | essential: the program fails or turns invalid without it |
| 32 | `fitting = [j for j, g in enumerate(_caps) if g >= s]` | -0.9965 | essential: the program fails or turns invalid without it |
| 33 | `n_unused = len(bins) - len(fitting)` | -0.9965 | essential: the program fails or turns invalid without it |
| 34 | `scores = np.empty(len(bins), dtype=np.float64)` | -0.9965 | essential: the program fails or turns invalid without it |
| 37 | `exact_pos = -1` | -0.9965 | essential: the program fails or turns invalid without it |
| 42 | `if exact_pos >= 0: ...` | -0.9965 | essential: the program fails or turns invalid without it |
| 43 | `scores[:] = 0.0` | -0.9965 | essential: the program fails or turns invalid without it |
| 45 | `choice = exact_pos` | -0.9965 | essential: the program fails or turns invalid without it |
| 47 | `for k, j in enumerate(fitting): ...` | -0.9965 | essential: the program fails or turns invalid without it |
| 48 | `g = _caps[j]` | -0.9965 | essential: the program fails or turns invalid without it |
| 49 | `r = g - s` | -0.9965 | essential: the program fails or turns invalid without it |
| 51 | `delta = -_W[g] * (2 * _N[g] - 1)` | -0.9965 | essential: the program fails or turns invalid without it |
| 55 | `match = _N[r] if r > 0 else 0` | -0.9965 | essential: the program fails or turns invalid without it |
| 57 | `scores[k] = -(delta * 100000.0 + match * 100.0 + r)` | -0.9965 | essential: the program fails or turns invalid without it |
| 58 | `r_new = CAP - s` | -0.9965 | essential: the program fails or turns invalid without it |
| 59 | `delta_new = _W[r_new] * (2 * _N[r_new] + 1) if r_new > 0 else 0.0` | -0.9965 | essential: the program fails or turns invalid without it |
| 60 | `match_new = _N[r_new] if r_new > 0 else 0` | -0.9965 | essential: the program fails or turns invalid without it |
| 61 | `scores[len(fitting):] = -(delta_new * 100000.0 + match_new * 100.0 + r_new)` | -0.9965 | essential: the program fails or turns invalid without it |
| 62 | `choice = int(np.argmax(scores))` | -0.9965 | essential: the program fails or turns invalid without it |
| 66 | `g = _caps[j]` | -0.9965 | essential: the program fails or turns invalid without it |
| 68 | `_caps[j] = g - s` | -0.2136 | matters |
| 68 | `term + g` | -0.1697 | matters |
| 65 | `j = fitting[choice]` | -0.0484 | matters |
| 44 | `scores[exact_pos] = 1.0` | -0.0395 | matters |
| 33 | `term + len(bins)` | -0.0372 | matters |
| 64 | `if choice < len(fitting): ...` | -0.0372 | matters |
| 49 | `term + g` | -0.0355 | matters |
| 52 | `if r > 0: ...` | -0.0355 | matters |
| 53 | `delta += _W[r] * (2 * _N[r] + 1)` | -0.0355 | matters |
| 67 | `_N[g] -= 1` | -0.0351 | matters |
| 58 | `term + CAP` | -0.0107 | matters |
| 49 | `term - s` | -0.0047 | matters |
| 58 | `term - s` | -0.0015 | no effect alone |
| 38 | `for k, j in enumerate(fitting): ...` | -0.0007 | no effect alone |
| 39 | `if _caps[j] == s: ...` | -0.0007 | no effect alone |
| 40 | `exact_pos = k` | -0.0007 | no effect alone |
| 33 | `term - len(fitting)` | +0.0000 | no effect alone |
| 41 | `break` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 30: `global _caps, _N`

Not tested (evaluation limit 40): 7 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9965 | 0.9957 |
| minimal (1 parts removed) | 0.9965 | 0.9957 |

Minimal program:

```python
"""Capacity-weighted sum-of-squares rule with exact-fit override and fuller-bin tie-break.

Each item goes where it minimises the potential P = sum_g (100/g)^p * N(g)^2, where N(g) counts
open bins with remaining capacity g (0 < g < 100). The weighting exponent p balances how much the
rule penalizes multiplying near-full residual classes versus counts of large-residual classes.
If some fitting bin can take the item exactly (residual 0), that bin is chosen instead, since
closing a bin is always at least as good as any other placement. Ties on the potential delta go to
the placement whose resulting residual matches a more common existing open class (graded by count),
and then to the bin leaving the smaller residual (fuller bin first). The function is shown only the
bins the item fits in, so it keeps its own record of every opened bin; used bins are always a prefix
of the bin array. Each instance runs in a fresh process, so module-level state starts empty.
"""
import numpy as np
CAP = 100
_P = 0.8
_caps = []
_N = [0] * (CAP + 1)
_W = [(CAP / g) ** _P if g > 0 else 0.0 for g in range(CAP + 1)]

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
    exact_pos = -1
    for k, j in enumerate(fitting):
        if _caps[j] == s:
            exact_pos = k
            break
    if exact_pos >= 0:
        scores[:] = 0.0
        scores[exact_pos] = 1.0
        choice = exact_pos
    else:
        for k, j in enumerate(fitting):
            g = _caps[j]
            r = g - s
            delta = -_W[g] * (2 * _N[g] - 1)
            if r > 0:
                delta += _W[r] * (2 * _N[r] + 1)
            match = _N[r] if r > 0 else 0
            scores[k] = -(delta * 100000.0 + match * 100.0 + r)
        r_new = CAP - s
        delta_new = _W[r_new] * (2 * _N[r_new] + 1) if r_new > 0 else 0.0
        match_new = _N[r_new] if r_new > 0 else 0
        scores[len(fitting):] = -(delta_new * 100000.0 + match_new * 100.0 + r_new)
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
python -m autoresearch.loop problems/bin_packing_online_ss --budget 0.6 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 3
python -m autoresearch.loop --report experiments/llm-from-ss-v1/runs/s3   # rebuild this report
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
