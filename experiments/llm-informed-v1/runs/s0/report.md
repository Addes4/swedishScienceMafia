# Research loop report: bin_packing_online_informed

| | |
|---|---|
| problem | `bin_packing_online_informed` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2537 of a $0.35 hard cap, 236 calls, 780,038 tokens |
| wall time | search 5425 s, baselines 43 s, explain 152 s |
| stopped | wall (wall_limit) |
| evaluations | 236 (231 valid), 17 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9905 | 0.9903 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online_informed/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online_informed/baselines/funsearch_weibull.py` |
| baseline `fwss` | 0.9992 | 0.9990 | `problems/bin_packing_online_informed/baselines/fwss.py` |
| baseline `sum_of_squares` | 0.9942 | 0.9950 | `problems/bin_packing_online_informed/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9900 | 0.9895 | 7 parts removed |

Audit: public 0.9616 → 0.9905 (+0.0289), hidden 0.9604 → 0.9903 (+0.0299); public − hidden gap of the final program 0.0002.

Against the baselines: the final program's public score is below the best baseline (`fwss`, 0.9992). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the pure best-fit rule with a hybrid: apply best fit for items that are relatively large,... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a size-aware best-fit variant that reserves/deprioritizes essentially-empty bins f... |
| 3 | edit | not_better | 0.7087 | 0.9616 | $0.0004 | Implement a "best fit with recent-item anti-fragmentation" rule: track the running mean item size... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use a size-thresholded hybrid that applies best fit for the current item, but when an item is sma... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | The pure best-fit ties are broken by bin order; I will add a better tie-breaking/secondary criter... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will add a "smart" best-fit that, instead of always taking the bin whose residual after placing... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace the pure best-fit with a "harmonic/almost-worst-fit for near-empty bins" hybrid: for... |
| 8 | edit | not_better | 0.9010 | 0.9616 | $0.0006 | Replace the greedy rule with an online "sum of squares" / least-loaded replenishment strategy: si... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Implement a best-fit-with-"viability" tie-break: keep pure best fit as the primary score, but add... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a size-class/"reserve" heuristic: for large items (size above a threshold) use bes... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll implement a true online "best fit decreasing" mimic: since we know the total number of items... |
| 12 | edit | improved | 0.9678 | 0.9678 | $0.0007 | I will replace best fit's residual metric with a "harmonic" score that equals the fraction of the... |
| 13 | edit | improved | 0.9704 | 0.9704 | $0.0007 | I'll blend the current "target residual" score with a best-fit term: the current rule ignores how... |
| 14 | edit | not_better | 0.9699 | 0.9704 | $0.0007 | I'll refine the target set so bins are biased to leave residuals that correspond to frequent item... |
| 15 | edit | not_better | 0.9701 | 0.9704 | $0.0007 | I'll replace the static harmonic target set with an adaptive "fit-quality" score: primary rank by... |
| 16 | edit | not_better | 0.9628 | 0.9704 | $0.0009 | I'll make the target-residual approach adaptive: the dominant item size is ~40, so a bin whose re... |
| 17 | edit | not_better | 0.9616 | 0.9704 | $0.0010 | I will replace the static target list with a data-driven "expected future fit" score: estimate th... |
| 18 | edit | not_better | 0.9616 | 0.9704 | $0.0007 |  |
| 19 | edit | not_better | 0.9616 | 0.9704 | $0.0006 | I'll switch the primary ranking to pure best-fit (smallest post-placement residual) which is know... |
| 20 | edit | not_better | 0.9678 | 0.9704 | $0.0007 | I'll keep the static target-residual ranking but add a "close the bin" bonus: strongly reward pla... |
| 21 | edit | invalid | 0.0000 | 0.9704 | $0.0008 | I'll switch to a distribution-aware "match quality" score: estimate the empirical item-size distr... |
| 22 | edit | not_better | 0.9704 | 0.9704 | $0.0009 | I'll keep the static harmonic-target ranking but strengthen the "sealing" behavior: add a strong ... |
| 23 | edit | not_better | 0.8828 | 0.9704 | $0.0007 | Add an explicit "waste" term that, for each candidate bin, estimates the leftover capacity that c... |
| 24 | edit | not_better | 0.9609 | 0.9704 | $0.0006 | I'll replace the static target list with a score based on the expected number of "typical" items ... |
| 25 | edit | not_better | 0.9616 | 0.9704 | $0.0007 | I'll add an adaptive "reserved capacity" term: since the distribution is Weibull with mean ~40, m... |
| 26 | edit | not_better | 0.9616 | 0.9704 | $0.0007 | I'll replace the static target-residual closeness with a two-part score: a strong best-fit term (... |
| 27 | edit | invalid | 0.0000 | 0.9704 | $0.0008 | I'll replace the static target list with a smooth, distribution-aware scoring function: estimate ... |
| 28 | edit | not_better | 0.9704 | 0.9704 | $0.0007 | I'll replace the heuristic with the classic "best-fit with a reserved harmonic threshold": score ... |
| 29 | edit | not_better | 0.9538 | 0.9704 | $0.0009 | I'll add an adaptive, self-avoiding "filling" component: track the empirical item-size histogram ... |
| 30 | edit | not_better | 0.9616 | 0.9704 | $0.0007 | I'll replace the distance-to-multiple-of-mean heuristic with a distribution-free, well-known effe... |
| 31 | edit | not_better | 0.9616 | 0.9704 | $0.0006 | I'll replace the static target-residual heuristic with a "best-fit + reserved gap" rule that stro... |
| 32 | edit | not_better | 0.9616 | 0.9704 | $0.0007 | I'll replace the target-residual heuristic with a "best-fit but avoid leaving tiny unusable gaps"... |
| 33 | edit | not_better | 0.9616 | 0.9704 | $0.0006 | The prior attempts show gains from making bin choice more "adaptively best-fit" but failures from... |
| 34 | edit | improved | 0.9708 | 0.9708 | $0.0008 | I'll add an online-learned "fill boost": track the empirical distribution of item sizes seen so f... |
| 35 | edit | not_better | 0.9614 | 0.9708 | $0.0008 | I'll replace the online-histogram fill boost with a stronger, less noisy signal: a fixed "magic r... |
| 36 | edit | not_better | 0.9616 | 0.9708 | $0.0008 | Replace the noisy histogram bonus and multi-target distance heuristic with a single blended rule:... |
| 37 | edit | not_better | 0.9682 | 0.9708 | $0.0008 | I'll sharpen the online histogram signal into a proper "harmonically-guided best-fit": keep the t... |
| 38 | edit | not_better | 0.9616 | 0.9708 | $0.0007 | I'll replace the static harmonic targets with an adaptive best-fit rule: score bins primarily by ... |
| 39 | edit | not_better | 0.9682 | 0.9708 | $0.0008 | The online histogram bonus uses frequency divided by total, which becomes a vanishing signal as t... |
| 40 | edit | improved | 0.9727 | 0.9727 | $0.0007 | Replace the online frequency bonus, which decays as the instance grows, with a normalized "attain... |
| 41 | edit | not_better | 0.9616 | 0.9727 | $0.0010 | I'll shift the balance toward a tighter best-fit primary signal (which consolidates bins), keep o... |
| 42 | edit | not_better | 0.9616 | 0.9727 | $0.0007 | I'll replace the static harmonic targets with a small set of data-driven "magic residuals" learne... |
| 43 | edit | not_better | 0.9706 | 0.9727 | $0.0007 | I'll replace the fragile "normalize by the max count" histogram bonus (which lets one rare size d... |
| 44 | edit | not_better | 0.9616 | 0.9727 | $0.0007 | I'll replace the static harmonic-target set and noisy max-normalized histogram bonus with a distr... |
| 45 | edit | not_better | 0.9616 | 0.9727 | $0.0007 | I'll strengthen the fit-quality of the priority by using a concave (square-root) reward on exact/... |
| 46 | edit | not_better | 0.9292 | 0.9727 | $0.0007 | I'll tune the weights of the existing target-residual rule: reduce the best-fit penalty term (whi... |
| 47 | edit | not_better | 0.9633 | 0.9727 | $0.0007 | I will replace the static harmonic-target bonus with a proper best-fit-plus-residual rule whose k... |
| 48 | edit | not_better | 0.9616 | 0.9727 | $0.0006 | I will replace the static harmonic target set with a best-fit-plus-fill-likelihood rule: primary ... |
| 49 | edit | not_better | 0.9682 | 0.9727 | $0.0007 | I'll add a dynamic harmonic target derived from the empirical mean item size (≈40), since the opt... |
| 50 | edit | not_better | 0.9711 | 0.9727 | $0.0008 | I'll keep the effective static-target structure but raise the residual count by adding a small se... |
| 51 | edit | not_better | 0.9616 | 0.9727 | $0.0007 | I'll replace the noisy max-normalized histogram bonus and the static target set with a purely geo... |
| 52 | edit | not_better | 0.9640 | 0.9727 | $0.0007 | The residual penalty of 0.20 over-consolidates by always favoring fuller bins; I'll reduce it to ... |
| 53 | edit | not_better | 0.9406 | 0.9727 | $0.0008 | I'll keep the target-residual structure intact but retune: increase the histogram (attainable-rem... |
| 54 | edit | not_better | 0.9607 | 0.9727 | $0.0010 | I'll switch from the hand-set target list to an adaptive target set: track the empirical distribu... |
| 55 | edit | not_better | 0.9708 | 0.9727 | $0.0008 | I'll keep the harmonic target-residual structure but replace the noisy max-normalized histogram b... |
| 56 | edit | improved | 0.9739 | 0.9739 | $0.0008 | I'll replace the hand-set static target list with a harmonic target set derived dynamically from ... |
| 57 | edit | not_better | 0.9739 | 0.9739 | $0.0008 | I'll shift the residual-penalty term to act on the bin's fill level rather than the post-placemen... |
| 58 | edit | not_better | 0.9616 | 0.9739 | $0.0007 | I'll simplify the scoring to a robust best-fit rule: strongly prefer the smallest residual after ... |
| 59 | edit | not_better | 0.9420 | 0.9739 | $0.0009 | I'll add a stronger switch to a "leave a residual that exactly equals a frequent observed item si... |
| 60 | edit | not_better | 0.6963 | 0.9739 | $0.0008 | I will keep the harmonic target-residual structure but replace the max-normalized histogram bonus... |
| 61 | edit | not_better | 0.9616 | 0.9739 | $0.0008 | I'll replace the ad-hoc score with a well-founded "best-fit with a reserved-slack penalty": stron... |
| 62 | edit | not_better | 0.9616 | 0.9739 | $0.0009 | I'll make the target-residual set purely data-driven by using a robust quantile-based "value of r... |
| 63 | edit | not_better | 0.9661 | 0.9739 | $0.0008 | Replace the hard-clipped running mean with a smoothed (EWMA-like) mean of item sizes and use it t... |
| 64 | edit | not_better | 0.9682 | 0.9739 | $0.0008 | I'll add a dedicated "exact-fit / best-fit" preference by boosting bins whose post-placement resi... |
| 65 | edit | not_better | 0.9668 | 0.9739 | $0.0009 | I'll replace the histogram bonus (which is noisy and scale-sensitive) with a score derived from t... |
| 66 | edit | not_better | 0.3961 | 0.9739 | $0.0009 | I'll substitute per-bin "waste" scoring that prefers bins whose post-placement residual is small ... |
| 67 | edit | not_better | 0.9614 | 0.9739 | $0.0008 | I'll replace the ad-hoc score with a bin-packing-specific rule that prefers best-fit (smallest re... |
| 68 | edit | not_better | 0.9737 | 0.9739 | $0.0008 | I will replace the noisy max-normalized histogram bonus with a smooth kernel-density "future-fit ... |
| 69 | edit | not_better | 0.9704 | 0.9739 | $0.0008 | I will replace the noisy max-normalized histogram bonus with a less aggressive, unnormalized coun... |
| 70 | edit | improved | 0.9754 | 0.9754 | $0.0008 | I'll sweep the two key hyperparameters (the target-residual fraction set and the linear residual ... |
| 71 | edit | improved | 0.9773 | 0.9773 | $0.0008 | I'll strengthen consolidation of nearly-full bins by adding a tie-aware exact-fit bonus that grow... |
| 72 | edit | not_better | 0.9545 | 0.9773 | $0.0009 | I will add a Sum-of-Squares style dual term: reward bins whose post-placement residual is a commo... |
| 73 | edit | not_better | 0.9763 | 0.9773 | $0.0009 | I'll add a per-bin aging/recency term: track each open bin's last-use index and give a small bonu... |
| 74 | edit | not_better | 0.9766 | 0.9773 | $0.0008 | I will replace the linear residual penalty with a piecewise utility that sharply favors exact clo... |
| 75 | edit | not_better | 0.9614 | 0.9773 | $0.0009 | I'll replace the static harmonic target set plus mean-based multiples with a data-driven target s... |
| 76 | edit | not_better | 0.9771 | 0.9773 | $0.0008 | I will add a light global "largest-first awareness" by tracking the maximum item size seen so far... |
| 77 | edit | not_better | 0.9761 | 0.9773 | $0.0009 | I will add a score bonus that favors leaving a post-placement residual equal to or just above the... |
| 78 | edit | not_better | 0.9616 | 0.9773 | $0.0007 | I will replace the harmonic-target scoring with a pure best-fit term plus a linear reward for lar... |
| 79 | edit | not_better | 0.9768 | 0.9773 | $0.0009 | I will sharpen the exact/near-exact closing bonus into a nonlinear (squared) fullness-weighted te... |
| 80 | edit | not_better | 0.9773 | 0.9773 | $0.0009 | I will add a "leave-a-usable-remainder" guard: subtract a penalty when the post-placement residua... |
| 81 | edit | invalid | 0.0000 | 0.9773 | $0.0007 | I'll replace the static/target-based scoring with an explicit Best-Fit-Decreasing-style rule augm... |
| 82 | edit | not_better | 0.9771 | 0.9773 | $0.0008 | I will sharpen the fullness-weighted exact-fit bonus so near-closing placements (residual just ab... |
| 83 | edit | not_better | 0.9616 | 0.9773 | $0.0007 | I will replace the multi-target residual scoring with a pure "best-fit with tunable waste cost" r... |
| 84 | edit | not_better | 0.9766 | 0.9773 | $0.0009 | I'll add a term that rewards leaving a post-placement residual equal to a common future item size... |
| 85 | edit | not_better | 0.9751 | 0.9773 | $0.0009 | I will add a decaying "fragment penalty" that detects when the current placement would strand a p... |
| 86 | edit | not_better | 0.9579 | 0.9773 | $0.0007 | I will replace the target-residual scoring with a proper online lookahead-aware bin ranking: scor... |
| 87 | edit | not_better | 0.9773 | 0.9773 | $0.0008 | I will add a small Best-Fit component: strongly penalize leaving a post-placement residual larger... |
| 88 | edit | not_better | 0.9607 | 0.9773 | $0.0009 | I will swap the fixed harmonic target set for an online-learned target set: track the running his... |
| 89 | edit | not_better | 0.9616 | 0.9773 | $0.0006 | I will replace the residual-target distance scoring with a direct Best-Fit-plus-consolidation rul... |
| 90 | edit | not_better | 0.9768 | 0.9773 | $0.0009 | I'll add a "worst-fit reserve" flavor by blending the current harmonic-target residual score with... |
| 91 | edit | not_better | 0.9766 | 0.9773 | $0.0007 | I will remove the harmful dynamic target terms (which pull the residual toward complements of the... |
| 92 | edit | not_better | 0.9754 | 0.9773 | $0.0007 | I will give the residual-target scoring a Best-Fit tie-break instead of a uniform residual penalt... |
| 93 | edit | not_better | 0.9766 | 0.9773 | $0.0010 | I will add a "likelihood of closing" term based on the running item-size distribution: estimate t... |
| 94 | edit | not_better | 0.9481 | 0.9773 | $0.0009 | I will replace the hand-tuned harmonic target set with a data-driven one: use the running empiric... |
| 95 | edit | not_better | 0.9763 | 0.9773 | $0.0009 | I will add a "complement of common item sizes" component to the target set: since future items ca... |
| 96 | edit | not_better | 0.9616 | 0.9773 | $0.0008 | I'll replace the scoring with a best-fit-dominant rule that adds a monotone "awkwardness" penalty... |
| 97 | edit | not_better | 0.9773 | 0.9773 | $0.0007 | I will sharpen the exact-fit bonus (higher weight, steeper decay) and add an explicit strong rewa... |
| 98 | edit | not_better | 0.9773 | 0.9773 | $0.0009 | I'll add a "future-fit" term that rewards placing the item so the resulting residual equals a val... |
| 99 | edit | not_better | 0.9616 | 0.9773 | $0.0007 | I will replace the full harmonic target set with a smaller, carefully chosen set and combine the ... |
| 100 | edit | not_better | 0.9761 | 0.9773 | $0.0009 | I'll add a "smart closure" term: reward bins whose post-placement residual is itself a plausible ... |
| 101 | edit | not_better | 0.9766 | 0.9773 | $0.0009 | I'll add a strong "near-exact-fit" term that specifically targets residuals in the awkward range ... |
| 102 | edit | not_better | 0.9749 | 0.9773 | $0.0010 | I'll add score-sensitive "pair-fit" tracking: maintain a small map of open-bin residuals and, for... |
| 103 | edit | not_better | 0.9616 | 0.9773 | $0.0006 | I will replace the harmonic-target residual-distance ranking with a pure best-fit rule (choose th... |
| 104 | edit | not_better | 0.9773 | 0.9773 | $0.0012 | I'll make the target geometry adaptive by learning, online, which post-placement residuals histor... |
| 105 | edit | not_better | 0.9633 | 0.9773 | $0.0008 | I'll replace the fixed harmonic target set with a hybrid that ranks bins primarily by close-to-be... |
| 106 | edit | not_better | 0.9654 | 0.9773 | $0.0009 | I will add an adaptive "awkward residual" penalty: track the running empirical histogram of item ... |
| 107 | edit | not_better | 0.9766 | 0.9773 | $0.0009 | I will keep the harmonic/dynamic-target geometry but add a score term that favors placing the ite... |
| 108 | edit | not_better | 0.9756 | 0.9773 | $0.0010 | I will replace the static harmonic target array with a learned target set: maintain a running his... |
| 109 | edit | not_better | 0.9677 | 0.9773 | $0.0008 | Increase the best-fit (residual minimization) weight from 0.10 to 0.22 while keeping the harmonic... |
| 110 | edit | invalid | 0.0000 | 0.9773 | $0.0010 | I'll add an adaptive term that directly rewards placing the item into the bin whose resulting res... |
| 111 | edit | not_better | 0.9771 | 0.9773 | $0.0009 | I'll blend in a second, purely geometric term: reward bins whose post-placement residual is an in... |
| 112 | edit | not_better | 0.9619 | 0.9773 | $0.0009 | I'll replace the target-distance scoring with a direct "future fillability" heuristic: score each... |
| 113 | edit | not_better | 0.9773 | 0.9773 | $0.0009 | I will add a small adaptive "largest-observed-size" aware penalty: when the post-placement residu... |
| 114 | edit | not_better | 0.9616 | 0.9773 | $0.0007 | I will change the scoring to a pure best-fit-like rule with a small tie-break that slightly prefe... |
| 115 | edit | not_better | 0.9768 | 0.9773 | $0.0009 | I will add a score term that prefers, among bins, the one whose post-placement residual is closes... |
| 116 | edit | improved | 0.9858 | 0.9858 | $0.0008 | I'll replace the fixed target-distance scoring with an adaptive residual-target set learned from ... |
| 117 | edit | improved | 0.9863 | 0.9863 | $0.0009 | I will add a "future-fitability" guard that penalizes bins whose post-placement residual is a sma... |
| 118 | edit | not_better | 0.9861 | 0.9863 | $0.0009 | I'll refine the target set to also include complements of the most common sizes with weights base... |
| 119 | edit | not_better | 0.9863 | 0.9863 | $0.0010 | I'll make the wasted-residual guard adaptive to the largest observed size as well: a nonempty res... |
| 120 | edit | not_better | 0.9616 | 0.9863 | $0.0010 | I'll replace the frequency-based target set with a set of harmonic/canonical targets but weight e... |
| 121 | edit | not_better | 0.9856 | 0.9863 | $0.0011 | I will add a small "exact-fit plus frequent-complement" bonus that directly rewards leaving a res... |
| 122 | edit | not_better | 0.9856 | 0.9863 | $0.0010 | Add a "pairing" bonus that rewards placing the current item so the residual exactly matches a fre... |
| 123 | edit | not_better | 0.9856 | 0.9863 | $0.0009 | I'll switch the tie-break from "prefer smaller residual" (which prefers full bins) toward a prope... |
| 124 | edit | not_better | 0.9720 | 0.9863 | $0.0011 | I will replace the fixed 0.05 best-fit pressure with an adaptive term based on the fraction of bi... |
| 125 | edit | not_better | 0.7464 | 0.9863 | $0.0009 | I'll replace the empirical target-set/keyword logic with a "residual fill-probability" score: est... |
| 126 | edit | not_better | 0.9846 | 0.9863 | $0.0011 | I will add a small "future-fit" bonus computed from the empirical size histogram: for each candid... |
| 127 | edit | not_better | 0.9751 | 0.9863 | $0.0009 | I'll strengthen the tie-break to a proper "best fit with fillability" by combining the empirical ... |
| 128 | edit | not_better | 0.9171 | 0.9863 | $0.0010 | I'll replace the current scoring with a classic "best-fit with a harmonic-target distance primary... |
| 129 | edit | not_better | 0.9616 | 0.9863 | $0.0008 | I will replace the empirical distance-to-targets primary term with a pairwise-compatibility scori... |
| 130 | edit | not_better | 0.9856 | 0.9863 | $0.0009 | I'll keep the empirical target-distance primary but add a small "waste-free completion" bonus tha... |
| 131 | edit | gate_rejected | 0.9890 | 0.9863 | $0.0009 | I'll replace the distance-to-targets primary term with a direct frequency-weighted "exact fill" r... |
| 132 | edit | not_better | 0.9858 | 0.9863 | $0.0010 | The current rule leaves many bins at residuals just below the smallest observed item (unfillable ... |
| 133 | edit | not_better | 0.9642 | 0.9863 | $0.0011 | I'll switch the primary signal to an explicit "expected future-fit value" of each residual: compu... |
| 134 | edit | not_better | 0.9848 | 0.9863 | $0.0011 | I'll keep the empirical target-distance primary term but make the tie-break a small best-fit pres... |
| 135 | edit | not_better | 0.9614 | 0.9863 | $0.0010 | I'll replace the brittle periodic target-rebuild and fixed top-10 targets with a smoothly decayin... |
| 136 | edit | not_better | 0.9863 | 0.9863 | $0.0009 | I'll soften the hard tie-break into a residual-value term that directly estimates the probability... |
| 137 | edit | improved | 0.9875 | 0.9875 | $0.0010 | I'll replace the fragile periodic full-rebuild of the top-10 target set with an incrementally mai... |
| 138 | edit | not_better | 0.9535 | 0.9875 | $0.0011 | I'll expand the target set from a fixed top-12 to all sizes whose observed frequency exceeds a sm... |
| 139 | edit | not_better | 0.9616 | 0.9875 | $0.0009 | I'll replace the multi-target nearest-distance term with a direct "expected one-item exact-fill p... |
| 140 | edit | not_better | 0.9623 | 0.9875 | $0.0011 | I will keep the empirical target-distance + scaled best-fit scoring but replace the fixed 12 targ... |
| 141 | edit | improved | 0.9878 | 0.9878 | $0.0012 | Add a second "lookahead value" term that rewards residuals which are hard to leave empty because ... |
| 142 | edit | not_better | 0.9875 | 0.9878 | $0.0014 | Add a residual-value bonus based on the smoothed probability that a leftover can be exactly close... |
| 143 | edit | not_better | 0.9616 | 0.9878 | $0.0011 | Replace the periodic full rebuild of the target list with an incrementally maintained top-size ca... |
| 144 | edit | not_better | 0.9616 | 0.9878 | $0.0012 | I'll replace the "nearest target distance" primary with a stronger best-fit rule: score each bin ... |
| 145 | edit | not_better | 0.9878 | 0.9878 | $0.0014 | I'll add a known-horizon term: since we know how many items remain, when few items are left we sh... |
| 146 | edit | not_better | 0.9861 | 0.9878 | $0.0013 | I'll add a second guard for the endgame: once few bins are open or few items remain, the best-fit... |
| 147 | edit | not_better | 0.9878 | 0.9878 | $0.0014 | I'll add an exact-fill endgame rule: when the current item can exactly close an open bin (residua... |
| 148 | edit | not_better | 0.9878 | 0.9878 | $0.0014 | I will add a "perfect-pair" memory term: track the most frequent item sizes and, for each bin, ad... |
| 149 | edit | gate_rejected | 0.9880 | 0.9878 | $0.0014 | Add a deterministic "closing" rule that checks, for each candidate bin, whether placing the item ... |
| 150 | edit | not_better | 0.9616 | 0.9878 | $0.0015 | I'll keep the existing overall structure but improve the target construction: use a smoothed (rec... |
| 151 | edit | not_better | 0.9875 | 0.9878 | $0.0015 | Add a "residual reuse" term: track the running counts of residuals that bins were left at when th... |
| 152 | edit | gate_rejected | 0.9880 | 0.9878 | $0.0013 | I'll tune the best-fit pressure to be stronger and more front-loaded, since previous experiments ... |
| 153 | edit | not_better | 0.9878 | 0.9878 | $0.0012 | I'll add a strong, deterministic exact-fill bonus (when a bin's residual exactly equals the item ... |
| 154 | edit | not_better | 0.9870 | 0.9878 | $0.0013 | I'll replace the coarse top-12-item target set with a much denser, recency-weighted set of attrac... |
| 155 | edit | not_better | 0.9616 | 0.9878 | $0.0013 | The current scorer's main target term is a min-distance to a target set, which gives a basin of f... |
| 156 | edit | improved | 0.9885 | 0.9885 | $0.0013 | I will expand the pair-fill bonus into a stronger, more informative term: instead of a flat 0.015... |
| 157 | edit | not_better | 0.9883 | 0.9885 | $0.0014 | Introduce a "waste-aware best-fit" correction: instead of penalizing residuals below the minimum ... |
| 158 | edit | not_better | 0.9878 | 0.9885 | $0.0014 | I'll strengthen the pair-fill bonus into a forward-looking term scaled by the remaining-fraction ... |
| 159 | edit | not_better | 0.9885 | 0.9885 | $0.0013 | Reduce the number of bins by making the pair-fill/exact-fill logic coherent with the target set: ... |
| 160 | edit | not_better | 0.9885 | 0.9885 | $0.0016 | I'll add a recency-weighted "useful residual" memory: track the residual that each placed item le... |
| 161 | edit | not_better | 0.9883 | 0.9885 | $0.0014 | Add an explicit, dominant exact-fill bonus: when a bin's post-placement residual equals the arriv... |
| 162 | edit | improved | 0.9890 | 0.9890 | $0.0013 | I'll add a classic first-fit-decreasing-style free-capacity preference that is modulated by the s... |
| 163 | edit | gate_rejected | 0.9890 | 0.9890 | $0.0014 | I'll add a forward-looking "large-item reservation" term: for small arriving items, explicitly pe... |
| 164 | edit | not_better | 0.9885 | 0.9890 | $0.0013 | I'll change the fit-pressure term so it always (mildly) prefers tighter fits but with strength th... |
| 165 | edit | not_better | 0.9614 | 0.9890 | $0.0014 | I'll replace the fixed 12-size target set with a direct, probability-weighted "expected next-item... |
| 166 | edit | not_better | 0.9890 | 0.9890 | $0.0013 | I'll replace the target-distance/table machinery with a cleaner, more robust relative score: keep... |
| 167 | edit | not_better | 0.9890 | 0.9890 | $0.0014 | I'll add a "per-bin age/creation" tracking so that the fit-pressure preference can favor filling ... |
| 168 | edit | not_better | 0.9890 | 0.9890 | $0.0013 | I'll add a "future completeness" term that estimates, for each candidate bin, the probability the... |
| 169 | edit | improved | 0.9893 | 0.9893 | $0.0016 | I'll strengthen the "clean close" preference: give a large bonus to post-placement residuals that... |
| 170 | edit | not_better | 0.9890 | 0.9893 | $0.0016 | Replace the crude exact-fill bonus with a smooth, probability-weighted "closability" term: for ea... |
| 171 | edit | invalid | 0.0000 | 0.9893 | $0.0010 | I'll replace the ad-hoc size-asymmetric fit pressure with a proper "Match" (best-fit) baseline th... |
| 172 | edit | not_better | 0.9890 | 0.9893 | $0.0015 | I'll add a small, size-independent tie-break bonus for candidate bins whose post-placement residu... |
| 173 | edit | improved | 0.9898 | 0.9898 | $0.0013 | I'll replace the deterministic "top-12 frequent sizes" target set with a smooth probability-weigh... |
| 174 | edit | not_better | 0.9893 | 0.9898 | $0.0015 | Add a smooth "absorbs-many-future-items" bonus: for each candidate post-placement residual r, cre... |
| 175 | edit | gate_rejected | 0.9898 | 0.9898 | $0.0014 | I will add a "packing-efficiency" term that mildly prefers putting the current item into the bin ... |
| 176 | edit | not_better | 0.9335 | 0.9898 | $0.0012 | I'll replace the hard "top-12 frequent sizes" target set with a soft, weighted target score: for ... |
| 177 | edit | not_better | 0.9898 | 0.9898 | $0.0014 | I'll add a complementary exact-fill bonus: in addition to crediting residuals that equal a freque... |
| 178 | edit | not_better | 0.9870 | 0.9898 | $0.0014 | I'll add a scale-free "fractional emptiness" consolidation pressure tied to the current item's si... |
| 179 | edit | not_better | 0.9616 | 0.9898 | $0.0011 | I'll replace the "distance to nearest attractive target" term with a proper best-fit-on-empirical... |
| 180 | edit | not_better | 0.9898 | 0.9898 | $0.0015 | I'll replace the generic convolution-based pair bonus with a targeted "closable residual" score: ... |
| 181 | edit | not_better | 0.9895 | 0.9898 | $0.0014 | I'll add an adaptive "target list" that also includes residuals reachable as a frequent-complemen... |
| 182 | edit | gate_rejected | 0.9898 | 0.9898 | $0.0013 | I'll replace the binary "nearest top-12 target" distance with a smooth, tie-break-friendly best-f... |
| 183 | edit | not_better | 0.9893 | 0.9898 | $0.0015 | I will add a small, continuous "sub-bin waste avoidance" term that penalizes leaving a nonzero re... |
| 184 | edit | improved | 0.9903 | 0.9903 | $0.0015 | I'll strengthen the exact-fill signal and add a "fractional complement" bonus: since items are dr... |
| 185 | edit | not_better | 0.9895 | 0.9903 | $0.0017 | I'll reduce the tie-break best-fit pressure when it causes early fragmentation, and instead add a... |
| 186 | edit | not_better | 0.9863 | 0.9903 | $0.0016 | I'll raise the best-fit pressure weight and make it item-size-scaled with an additional snug-fit ... |
| 187 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I'll make the closability signal distribution-aware in a smoother way: replace the coarse integer... |
| 188 | edit | not_better | 0.9880 | 0.9903 | $0.0016 | I'll add a "consolidation" signal that rewards leaving a residual which is close to an integer mu... |
| 189 | edit | not_better | 0.9895 | 0.9903 | $0.0018 | I will add a "future-fillability" guard that computes, for each candidate bin, the expected numbe... |
| 190 | edit | not_better | 0.9898 | 0.9903 | $0.0016 | I'll add a mild hard-guard against opening brand-new bins in the early/mid game: bins with residu... |
| 191 | edit | not_better | 0.9898 | 0.9903 | $0.0015 | I'll replace the hard integer-index lookup of the closability bonuses with smooth linear interpol... |
| 192 | edit | not_better | 0.6881 | 0.9903 | $0.0011 | I'll replace the hand-tuned composite bonus with a principled score: reward bins by the empirical... |
| 193 | edit | not_better | 0.9898 | 0.9903 | $0.0016 | I'll add a "reserve the largest bins for future big items" heuristic: track the largest item size... |
| 194 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I'll strengthen the guard against opening new bins when an existing bin can still absorb the item... |
| 195 | edit | not_better | 0.9900 | 0.9903 | $0.0017 | I'll add a size-class-aware "reserve big bins for big items" rule: learn the largest item size se... |
| 196 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I'll replace the integer-bin lookup of the empirical exact-fill and near-fill scores with smooth ... |
| 197 | edit | not_better | 0.9900 | 0.9903 | $0.0017 | Increase the weight on the smooth `_NEAR_SCORE` closability bonus and reduce reliance on the spik... |
| 198 | edit | not_better | 0.9898 | 0.9903 | $0.0017 | I'll switch the best-fit tie-break from a fixed small weight to a stronger, more principled "leas... |
| 199 | edit | not_better | 0.9903 | 0.9903 | $0.0018 | Add a mild penalty for placing the item into a completely unused bin (residual_after == 100, i.e.... |
| 200 | edit | not_better | 0.9898 | 0.9903 | $0.0017 | I'll add a strong "must be able to fit the currently-known largest item" coupling: compute the la... |
| 201 | edit | not_better | 0.9898 | 0.9903 | $0.0016 | Add a super-additive "longest-processing-time"-style reserve: after choosing a bin, track the dis... |
| 202 | edit | no_code | n/a | 0.9903 | $0.0006 | I'll make the target/closability bonus continuous rather than integer-snapped by using the actual... |
| 203 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | (no description) |
| 204 | edit | not_better | 0.9851 | 0.9903 | $0.0016 | I'll strengthen the best-fit (smallest post-placement residual) pressure by making the fit weight... |
| 205 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I'll replace the integer-snapped closability lookup with continuous linear interpolation of the e... |
| 206 | edit | not_better | 0.9898 | 0.9903 | $0.0016 | I'll add a look-ahead "try the item in each candidate bin, then greedily simulate packing the mos... |
| 207 | edit | not_better | 0.9242 | 0.9903 | $0.0013 | Replace the ad-hoc target/closability scoring with a proper "best-fit-decreasing-like" rule guide... |
| 208 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I'll make the near-score lookup continuous by interpolating all three closability tables (exact, ... |
| 209 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I will add a dedicated "perfect-fit priority": when a bin's post-placement residual is small but ... |
| 210 | edit | not_better | 0.9903 | 0.9903 | $0.0013 | I'll replace the integer-snapped closability lookups with a proper linear interpolation helper so... |
| 211 | edit | not_better | 0.8771 | 0.9903 | $0.0014 | I'll replace the heuristic blend with a cleaner, well-known strong online rule: score each bin pr... |
| 212 | edit | not_better | 0.9626 | 0.9903 | $0.0013 | Replace the integer-snapped exact/near/pair bonus with a single smooth closability score: the emp... |
| 213 | edit | not_better | 0.9898 | 0.9903 | $0.0016 | Add a light "avoid creating tiny unfillable gaps" refinement by penalizing non-zero post-placemen... |
| 214 | edit | not_better | 0.9903 | 0.9903 | $0.0016 | I'll replace the discrete integer-snapped closability lookup with a smooth linear interpolation o... |
| 215 | edit | not_better | 0.9900 | 0.9903 | $0.0016 | I'll add an explicit Sum-of-Squares / harmonic "quadratic fit" refinement: dynamically estimate t... |
| 216 | edit | not_better | 0.9903 | 0.9903 | $0.0014 | I'll swap the target-set "nearest attractive residual" term for a direct estimate of the expected... |
| 217 | edit | not_better | 0.9898 | 0.9903 | $0.0018 | I'll replace the fixed target-set distance term with an adaptive best-fit pressure plus a direct ... |
| 218 | edit | not_better | 0.9895 | 0.9903 | $0.0016 | I'll add a "reserve the last bin" guard: when only a few items remain and open bins are plentiful... |
| 219 | edit | not_better | 0.9628 | 0.9903 | $0.0014 | I'll add an adaptive best-fit dominance that strengthens with instance progress but bounds closin... |
| 220 | edit | not_better | 0.9893 | 0.9903 | $0.0017 | I'll add an adaptive capacity-reservation guard that discourages leaving residuals in the hard-to... |
| 221 | edit | not_better | 0.9903 | 0.9903 | $0.0013 | I will make the bin choice depend on the empirical pair-sum fillability of the *combined* open-bi... |
| 222 | edit | not_better | 0.9614 | 0.9903 | $0.0013 | I'll sharpen the closability signal: replace the diluted combination with a dominant term rewardi... |
| 223 | edit | improved | 0.9905 | 0.9905 | $0.0015 | I'll add a "complement pair" reward that accounts for two-item closure more directly: score each ... |
| 224 | edit | not_better | 0.9883 | 0.9905 | $0.0016 | I'll replace the flat target-set distance with a continuous, empirically-weighted "closability" s... |
| 225 | edit | not_better | 0.9905 | 0.9905 | $0.0017 | I'll replace the hard "distance to nearest target" term with a smooth, empirically-weighted score... |
| 226 | edit | not_better | 0.9898 | 0.9905 | $0.0015 | I will strengthen the pair-sum (two-item closure) bonus and tune the score weights by making the ... |
| 227 | edit | not_better | 0.9900 | 0.9905 | $0.0016 | I will make the fit pressure adaptive to the empirical fillability of the resulting residual inst... |
| 228 | edit | not_better | 0.9609 | 0.9905 | $0.0016 | I'll replace the hard nearest-target distance term with a smooth, empirically-weighted closabilit... |
| 229 | edit | not_better | 0.9800 | 0.9905 | $0.0015 | I'll stop letting the "fit pressure" term shrink residuals unconditionally and instead let the em... |
| 230 | edit | not_better | 0.9829 | 0.9905 | $0.0017 | I'll add a "fillability-aware best-fit": among bins whose post-placement residual is likely closa... |
| 231 | edit | not_better | 0.9905 | 0.9905 | $0.0016 | I'll blend in a well-known strong online bin-packing heuristic, best-fit-decreasing-like tightnes... |
| 232 | edit | not_better | 0.9900 | 0.9905 | $0.0016 | I'll add a deterministic "reservoir" correction: track the running mean item size and, when the a... |
| 233 | edit | not_better | 0.9898 | 0.9905 | $0.0014 | I'll replace the weighted-sum scoring with a learned-style decision that explicitly simulates one... |
| 234 | edit | not_better | 0.9880 | 0.9905 | $0.0017 | Add an empirically-tuned complement bonus: track the most frequent item sizes and give a strong b... |
| 235 | edit | not_better | 0.9905 | 0.9905 | $0.0016 | I'll reduce the harmful tiny-residual penalty and replace the discretized (integer-rounding) clos... |
| 236 | edit | not_better | 0.9903 | 0.9905 | $0.0016 | I'll add an adaptive "hard-to-place large item" guard: when the arriving item is large relative t... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,137 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Adaptive combo bin choice: leave residuals that arrive often, break ties by
+size-aware best fit.
+
+Capacity is 100. Items arrive online. We learn which residual values are actually
+useful: the most frequent item sizes seen so far are the residuals a future item
+is most likely to (nearly) fill. We score each bin by how close its post-placement
+residual is to a small set of such empirically attractive values, then break
+near-ties toward tighter fits, with the strength of that pressure scaled by how
+large the arriving item is.
+
+Guard 1: a residual that is nonzero but smaller than the smallest item size seen
+so far can never be filled by any future item (wasted space) -> mild penalty.
+
+Guard 2: closability. For each candidate post-placement residual r we add a
+probability-weighted bonus: the empirical probability that a future item is near
+r (single-item close, with a small bandwidth) plus a discounted probability that
+r is hittable by two items (pair-sum table). This is smooth, so near-perfect
+residuals still get partial credit.
+"""
 import numpy as np
+
+_CAP = 100.0
+
+# Histogram of observed item sizes -> drives the "good residual" targets.
+_SIZE_COUNT = np.zeros(101, dtype=np.float64)
+_TOTAL = 0.0
+_SIZE_SUM = 0.0
+_MIN_SIZE = 101.0
+
+# Cached arrays, refreshed as the histogram grows.
+_TARGETS = np.array([0.0, _CAP], dtype=np.float64)
+_PAIR_SCORE = np.zeros(101, dtype=np.float64)
+_EXACT_SCORE = np.zeros(101, dtype=np.float64)
+_NEAR_SCORE = np.zeros(101, dtype=np.float64)
+_REFRESH = 16
+_N_ITEMS = 0.0  # number of items in the instance (known on first call)
+
+# Small bandwidth kernel over residuals for "near a frequent size" credit.
+_KERNEL_R = 3
+_KR = np.arange(-_KERNEL_R, _KERNEL_R + 1, dtype=np.float64)
+_KERNEL = np.exp(-0.5 * (_KR / 1.5) ** 2)
+
+
+def _rebuild_targets():
+    global _TARGETS, _PAIR_SCORE, _EXACT_SCORE, _NEAR_SCORE
+    counts = _SIZE_COUNT[1:101]
+    order = np.argsort(counts, kind="stable")
+    top = order[::-1][:12] + 1  # item sizes with the largest counts
+    top = top[counts[top - 1] > 0]
+    targets = set([0.0, _CAP])
+    for s in top:
+        s = float(s)
+        targets.add(s)          # a leftover equal to this size closes cleanly
+        targets.add(_CAP - s)   # complement also leaves a fillable residual
+    _TARGETS = np.array(sorted(targets), dtype=np.float64)
+
+    # Probability-weighted two-item sum table over residuals 0..100.
+    support = np.zeros(101, dtype=np.float64)
+    plausible = np.nonzero(_SIZE_COUNT[1:101] > 0)[0] + 1
+    if plausible.size:
+        w = _SIZE_COUNT[plausible]
+        support[plausible] = w / w.sum()
+    conv = np.convolve(support, support)
+    n = min(101, conv.size)
+    pair = np.zeros(101, dtype=np.float64)
+    pair[:n] = conv[:n]
+    m = pair.max()
+    if m > 0:
+        pair = pair / m
+    _PAIR_SCORE = pair
+
+    # Smooth exact-fill score: empirical probability a future item equals r.
+    exact = support.copy()
+    mx = exact.max()
+    if mx > 0:
+        exact = exact / mx
+    _EXACT_SCORE = exact
+
+    # Smooth "near a frequent size" score: convolve the support with a small
+    # Gaussian kernel so residuals within a few units of a frequent size still
+    # get partial credit (items are roughly continuous, not discrete).
+    near = np.convolve(support, _KERNEL, mode="same")
+    near = near[:101]
+    if near.size < 101:
+        pad = np.zeros(101, dtype=np.float64)
+        pad[: near.size] = near
+        near = pad
+    mn = near.max()
+    if mn > 0:
+        near = near / mn
+    _NEAR_SCORE = near
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin; the item goes to the highest (first on ties)."""
+    global _TOTAL, _SIZE_SUM, _MIN_SIZE, _N_ITEMS
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    if _N_ITEMS == 0.0:
+        _N_ITEMS = float(len(bins))
+
+    if _TOTAL == 0.0 or (_TOTAL % _REFRESH == 0.0):
+        _rebuild_targets()
+
+    residual_after = bins - item
+
+    # Distance to the nearest attractive residual.
+    d = np.abs(residual_after[:, None] - _TARGETS[None, :])
+    best = d.min(axis=1)
+
+    # Size-aware best-fit pressure: larger arriving items prefer snug bins.
+    frac = _TOTAL / _N_ITEMS if _N_ITEMS > 0.0 else 0.0
+    base_w = 0.02 + 0.06 * frac
+    size_lean = (item - 50.0) / 50.0
+    fit_weight = base_w * (1.0 + 0.6 * size_lean)
+
+    score = -best - fit_weight * residual_after
+
+    # Guard 1: penalize tiny nonzero residuals no seen item could fill.
+    if _MIN_SIZE <= _CAP:
+        waste = (residual_after > 0.0) & (residual_after < _MIN_SIZE)
+        score -= 0.02 * waste
+
+    # Guard 2: smooth closability bonus (single-, near- and two-item).
+    ri = np.clip(residual_after, 0.0, _CAP).astype(np.int64)
+    score += 0.35 * _PAIR_SCORE[ri]
+    score += 0.5 * _EXACT_SCORE[ri]
+    score += 0.15 * _NEAR_SCORE[ri]
+
+    _SIZE_COUNT[item] += 1.0
+    _TOTAL += 1.0
+    _SIZE_SUM += item
+    if item < _MIN_SIZE:
+        _MIN_SIZE = float(item)
+    return score
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (31 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 97 | `global _TOTAL, _SIZE_SUM, _MIN_SIZE, _N_ITEMS` | -0.9905 | essential: the program fails or turns invalid without it |
| 105 | `residual_after = bins - item` | -0.9905 | essential: the program fails or turns invalid without it |
| 105 | `term + bins` | -0.9905 | essential: the program fails or turns invalid without it |
| 108 | `d = np.abs(residual_after[:, None] - _TARGETS[None, :])` | -0.9905 | essential: the program fails or turns invalid without it |
| 109 | `best = d.min(axis=1)` | -0.9905 | essential: the program fails or turns invalid without it |
| 112 | `frac = _TOTAL / _N_ITEMS if _N_ITEMS > 0.0 else 0.0` | -0.9905 | essential: the program fails or turns invalid without it |
| 113 | `base_w = 0.02 + 0.06 * frac` | -0.9905 | essential: the program fails or turns invalid without it |
| 114 | `size_lean = (item - 50.0) / 50.0` | -0.9905 | essential: the program fails or turns invalid without it |
| 115 | `fit_weight = base_w * (1.0 + 0.6 * size_lean)` | -0.9905 | essential: the program fails or turns invalid without it |
| 117 | `score = -best - fit_weight * residual_after` | -0.9905 | essential: the program fails or turns invalid without it |
| 125 | `ri = np.clip(residual_after, 0.0, _CAP).astype(np.int64)` | -0.9905 | essential: the program fails or turns invalid without it |
| 117 | `term - fit_weight * residual_after` | -0.2528 | matters |
| 105 | `term - item` | -0.1747 | matters |
| 117 | `term + -best` | -0.0284 | matters |
| 102 | `if _TOTAL == 0.0 or _TOTAL % _REFRESH == 0.0: ...` | -0.0279 | matters |
| 103 | `_rebuild_targets()` | -0.0279 | matters |
| 130 | `_SIZE_COUNT[item] += 1.0` | -0.0279 | matters |
| 131 | `_TOTAL += 1.0` | -0.0199 | matters |
| 99 | `if _N_ITEMS == 0.0: ...` | -0.0196 | matters |
| 100 | `_N_ITEMS = float(len(bins))` | -0.0196 | matters |
| 113 | `term + 0.06 * frac` | -0.0196 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 113: `term + 0.02`
- line 120: `if _MIN_SIZE <= _CAP: ...`
- line 121: `waste = (residual_after > 0.0) & (residual_after < _MIN_SIZE)`
- line 122: `score -= 0.02 * waste`
- line 126: `score += 0.35 * _PAIR_SCORE[ri]`
- line 127: `score += 0.5 * _EXACT_SCORE[ri]`
- line 128: `score += 0.15 * _NEAR_SCORE[ri]`
- line 132: `_SIZE_SUM += item`
- line 133: `if item < _MIN_SIZE: ...`
- line 134: `_MIN_SIZE = float(item)`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9905 | 0.9903 |
| minimal (7 parts removed) | 0.9900 | 0.9895 |

Minimal program:

```python
"""Adaptive combo bin choice: leave residuals that arrive often, break ties by
size-aware best fit.

Capacity is 100. Items arrive online. We learn which residual values are actually
useful: the most frequent item sizes seen so far are the residuals a future item
is most likely to (nearly) fill. We score each bin by how close its post-placement
residual is to a small set of such empirically attractive values, then break
near-ties toward tighter fits, with the strength of that pressure scaled by how
large the arriving item is.

Guard 1: a residual that is nonzero but smaller than the smallest item size seen
so far can never be filled by any future item (wasted space) -> mild penalty.

Guard 2: closability. For each candidate post-placement residual r we add a
probability-weighted bonus: the empirical probability that a future item is near
r (single-item close, with a small bandwidth) plus a discounted probability that
r is hittable by two items (pair-sum table). This is smooth, so near-perfect
residuals still get partial credit.
"""
import numpy as np
_CAP = 100.0
_SIZE_COUNT = np.zeros(101, dtype=np.float64)
_TOTAL = 0.0
_SIZE_SUM = 0.0
_MIN_SIZE = 101.0
_TARGETS = np.array([0.0, _CAP], dtype=np.float64)
_PAIR_SCORE = np.zeros(101, dtype=np.float64)
_EXACT_SCORE = np.zeros(101, dtype=np.float64)
_NEAR_SCORE = np.zeros(101, dtype=np.float64)
_REFRESH = 16
_N_ITEMS = 0.0
_KERNEL_R = 3
_KR = np.arange(-_KERNEL_R, _KERNEL_R + 1, dtype=np.float64)
_KERNEL = np.exp(-0.5 * (_KR / 1.5) ** 2)

def _rebuild_targets():
    global _TARGETS, _PAIR_SCORE, _EXACT_SCORE, _NEAR_SCORE
    counts = _SIZE_COUNT[1:101]
    order = np.argsort(counts, kind='stable')
    top = order[::-1][:12] + 1
    top = top[counts[top - 1] > 0]
    targets = set([0.0, _CAP])
    for s in top:
        s = float(s)
        targets.add(s)
        targets.add(_CAP - s)
    _TARGETS = np.array(sorted(targets), dtype=np.float64)
    support = np.zeros(101, dtype=np.float64)
    plausible = np.nonzero(_SIZE_COUNT[1:101] > 0)[0] + 1
    if plausible.size:
        w = _SIZE_COUNT[plausible]
        support[plausible] = w / w.sum()
    conv = np.convolve(support, support)
    n = min(101, conv.size)
    pair = np.zeros(101, dtype=np.float64)
    pair[:n] = conv[:n]
    m = pair.max()
    if m > 0:
        pair = pair / m
    _PAIR_SCORE = pair
    exact = support.copy()
    mx = exact.max()
    if mx > 0:
        exact = exact / mx
    _EXACT_SCORE = exact
    near = np.convolve(support, _KERNEL, mode='same')
    near = near[:101]
    if near.size < 101:
        pad = np.zeros(101, dtype=np.float64)
        pad[:near.size] = near
        near = pad
    mn = near.max()
    if mn > 0:
        near = near / mn
    _NEAR_SCORE = near

def priority(item, bins):
    """Return a priority for every bin; the item goes to the highest (first on ties)."""
    global _TOTAL, _SIZE_SUM, _MIN_SIZE, _N_ITEMS
    if _N_ITEMS == 0.0:
        _N_ITEMS = float(len(bins))
    if _TOTAL == 0.0 or _TOTAL % _REFRESH == 0.0:
        _rebuild_targets()
    residual_after = bins - item
    d = np.abs(residual_after[:, None] - _TARGETS[None, :])
    best = d.min(axis=1)
    frac = _TOTAL / _N_ITEMS if _N_ITEMS > 0.0 else 0.0
    base_w = 0.06 * frac
    size_lean = (item - 50.0) / 50.0
    fit_weight = base_w * (1.0 + 0.6 * size_lean)
    score = -best - fit_weight * residual_after
    ri = np.clip(residual_after, 0.0, _CAP).astype(np.int64)
    _SIZE_COUNT[item] += 1.0
    _TOTAL += 1.0
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online_informed --budget 0.35 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 0
python -m autoresearch.loop --report experiments/llm-informed-v1/runs/s0   # rebuild this report
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
