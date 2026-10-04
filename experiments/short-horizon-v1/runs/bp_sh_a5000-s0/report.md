# Research loop report: bp_sh_a5000

| | |
|---|---|
| problem | `bp_sh_a5000` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0902 of a $0.20 hard cap, 150 calls, 306,807 tokens |
| wall time | search 2040 s, baselines 240 s, explain 229 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (147 valid), 4 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9590 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9945 | 0.9803 |  |
| baseline `funsearch_or` | 0.9702 | 0.9711 | `problems/bp_sh_a5000/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9938 | 0.9937 | `problems/bp_sh_a5000/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9952 | 0.9950 | `problems/bp_sh_a5000/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9935 | 0.9910 | 9 parts removed |

Audit: public 0.9590 → 0.9945 (+0.0355), hidden 0.9634 → 0.9803 (+0.0169); public − hidden gap of the final program 0.0142.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9952). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9590 | 0.9590 | $0.0003 | Replace pure best-fit with a score that adds a small bonus for bins that are more "full" relative... |
| 2 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | (no description) |
| 3 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll implement a hybrid "best-fit with a reserved-large-bin guard": the item goes to the tightest... |
| 4 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll switch from pure best-fit to a "worst-fit among tight fits" hybrid: use best-fit normally, b... |
| 5 | edit | improved | 0.9593 | 0.9593 | $0.0007 | I'll implement a harmonic/almost-worst-fit style rule that prefers bins which, after the item, wi... |
| 6 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Introduce a small bonus for bins that would end up with a remainder in a learned "target band" — ... |
| 7 | edit | not_better | 0.9590 | 0.9593 | $0.0004 | I'll add a small bonus that actively prefers filling a bin almost exactly (remainder near 0) usin... |
| 8 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the heuristic bonus with a tunable score that interpolates between best-fit and a "least-... |
| 9 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the hand-tuned heuristic with a principled "best fit with a superlinear (squared) remaind... |
| 10 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the fixed best-fit with a best-fit that uses a small, smoothly-decaying reward for n... |
| 11 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the scalar best-fit score with a classic improvement for this setting: "best fit dec... |
| 12 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll switch to a scale-aware convex best-fit: score = -rem^p with a mild exponent (p≈1.3) plus a ... |
| 13 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the ad-hoc bonus with a proper "best fit with a harmonic tail" rule: the classic onl... |
| 14 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the heuristic bonus with a "best fit" rule that additionally discourages leaving sma... |
| 15 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the ad-hoc bonus with the classic "best fit" combined with a smart rejection of bins... |
| 16 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the hand-tuned bonus with a principled "best fit" that additionally rewards leaving a rem... |
| 17 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | Most recent attempts added bonuses that all scored the same, suggesting the bonus is too weak/red... |
| 18 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the greedy best-fit with a proper online heuristic: score bins by minimizing the pos... |
| 19 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the weak, hand-tuned bonuses (which all scored identically, implying they rarely cha... |
| 20 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Implement Best-Fit-Decreasing-style pairing by giving a strong bonus to bins that would be left w... |
| 21 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace plain best-fit with a rule that greedily minimizes wasted capacity by preferring the... |
| 22 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I will replace the ad-hoc bonuses, which all scored identically (meaning they rarely changed the ... |
| 23 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll switch from best-fit to a hybrid: prefer the bin that maximizes the resulting fill fraction ... |
| 24 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the weak bonus with a strong deterministic pairing rule: use best fit, but if some bin wo... |
| 25 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the piecewise bonus with a smooth, strictly-monotone convex penalty on the post-placement... |
| 26 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll use the "minimum bin slack" idea via a randomized tie-break among the best fits: score bins ... |
| 27 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll stop tweaking best-fit bonuses (which all collapse to the same argmax) and instead implement... |
| 28 | edit | not_better | 0.9574 | 0.9593 | $0.0007 | Replace the best-fit scoring with a one-step-lookahead expected-waste rule: score each bin by -E[... |
| 29 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll replace the scalar score with a two-stage policy that first tries to close a bin exactly (re... |
| 30 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll implement an adaptive-threshold Best-Fit: since plain best-fit is already near-optimal, I'll... |
| 31 | edit | invalid | 0.0000 | 0.9593 | $0.0006 | Add a light one-step expected-waste lookahead term to best-fit using a small empirical histogram ... |
| 32 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the weakly-effective scoring with tied-best-fit plus an explicit "equal-pairing" tie-brea... |
| 33 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll stop trying to modify the primary best-fit argmin and instead replace the weak threshold bon... |
| 34 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Implement the classic "Best Fit" but break ties by choosing the bin with the largest current fill... |
| 35 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I will replace the simple best-fit with a capped best-fit that reserves a small amount of "slack"... |
| 36 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll switch from best-fit to a "least-waste with a reserve penalty" rule calibrated to the item d... |
| 37 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the ad-hoc bonus with a calibrated "waste-utility" score: prefer the bin whose post-place... |
| 38 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll try a "harmonic" hybrid that linearly interpolates between best-fit (minimize remainder) and... |
| 39 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the ad-hoc nonlinear bonus with a proper "almost-exact fit" priority that strongly prefer... |
| 40 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll replace the pure best-fit with a score based on the post-placement remainder's "fill potenti... |
| 41 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll implement the classic Harmonic/Sum-of-Squares packing heuristic's core idea: for each bin, s... |
| 42 | edit | not_better | 0.4511 | 0.9593 | $0.0008 | I'll try a distribution-aware "expected waste" score: instead of minimizing the raw remainder, mi... |
| 43 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll switch to a "best fit with exact-fit priority" variant: give a large bonus when placement le... |
| 44 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the rule with Best-Fit-Decreasing-style behavior driven by an empirical size histogr... |
| 45 | edit | not_better | 0.3978 | 0.9593 | $0.0005 | Replace the score with the classic Sum-of-Squares (SS) bin-packing heuristic: for each bin comput... |
| 46 | edit | not_better | 0.9593 | 0.9593 | $0.0012 | I'll extend the current best-fit-plus-bonus rule with a smooth convex (quadratic) emphasis on the... |
| 47 | edit | invalid | 0.0000 | 0.9593 | $0.0007 | I'll add a distribution-aware "future fill" bonus: track the empirical histogram of item sizes se... |
| 48 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll refine the near-exact-fill bonus by making it a smooth convex function of the remainder that... |
| 49 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the hand-tuned bonus with the classic "Best Fit with a large penalty for leaving a r... |
| 50 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll implement a proper distribution-aware expected-waste rule based on the known Weibull(mean≈40... |
| 51 | edit | not_better | 0.9593 | 0.9593 | $0.0006 | I'll add a small "fill-fit" secondary term that prefers placing the item into a bin whose post-pl... |
| 52 | edit | not_better | 0.9593 | 0.9593 | $0.0005 | I'll shift from pure best-fit to a "best-fit among bins with a good remainder" rule by adding a s... |
| 53 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll implement the classic "Harmonic/quantized best-fit" idea calibrated to this Weibull distribu... |
| 54 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the flat threshold bonus with a learned "future-fit" score: maintain a small online ... |
| 55 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the near-exact-fill threshold with a proper two-parameter ranking: first minimize th... |
| 56 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll add a small dynamic tie-break that prefers placing the item where the resulting remainder ex... |
| 57 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the rule with a perturbed best-fit that occasionally chooses a lower priority bin wh... |
| 58 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll replace the ad-hoc near-exact bonus with the well-known "Best Fit with a residual-based tie-... |
| 59 | edit | not_better | 0.5841 | 0.9593 | $0.0008 | I'll replace the heuristic with the classic "Worst Fit Decreasing"-style rule tuned for online pa... |
| 60 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll switch from pure best-fit to the classic "Almost-Worst-Fit with best-fit fallback": rank bin... |
| 61 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the ad-hoc rule with a proper Best-Fit that breaks ties using an online estimate of ... |
| 62 | edit | not_better | 0.3990 | 0.9593 | $0.0005 | I'll keep the dominant best-fit ordering but replace the tiny threshold bonus with a smooth, stri... |
| 63 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the ad-hoc near-exact-fill bonus with the theoretically-motivated "Best Fit with a sum-of... |
| 64 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the fixed-threshold best-fit with a smooth nonlinear score that strongly rewards near-exa... |
| 65 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the static rule with a data-driven best-fit: track an online histogram of past item ... |
| 66 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I will add an online "bounded best-fit with reserved slack" rule: keep best-fit dominant, but whe... |
| 67 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace best-fit with a "best-fit with future-aware residual preference": rank bins by ascen... |
| 68 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll switch from best-fit to a two-sided rule: strictly prefer exact fills, otherwise pick the bi... |
| 69 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the score with a best-fit where near-ties are broken by preferring remainders that a... |
| 70 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the ad-hoc threshold with an exact-fit–aware best-fit: rank strictly by ascending po... |
| 71 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll mainly keep plain best-fit, but change the tie-breaking direction: instead of always preferr... |
| 72 | edit | not_better | 0.9590 | 0.9593 | $0.0008 | I will replace the ad-hoc small-remainder bonus with a probabilistic best-fit: use the known Weib... |
| 73 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Replace the static rule with plain best-fit (ascending post-placement remainder) as a clean basel... |
| 74 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I will keep best-fit dominant but add a strong exact-fill bonus and, more importantly, a "worst-f... |
| 75 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll add a conservative "aging"/lookahead heuristic: keep plain best-fit (ascending post-placemen... |
| 76 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the score with a harmonic-mean-based fill heuristic: rank by ascending post-placemen... |
| 77 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | Since the tie-break/aging tweaks all flopped, I'll revert to plain best-fit but add a proper "exa... |
| 78 | edit | not_better | 0.8849 | 0.9593 | $0.0006 | I'll switch from pure best-fit to a "Best Fit with usability threshold" rule: compute the post-pl... |
| 79 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the ad-hoc tweak with a clean Best-Fit-Decreasing-style heuristic adapted for online... |
| 80 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | Replace the ad-hoc bonus with an empirical "fill-probability" score: track a running histogram of... |
| 81 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll add a distribution-aware bonus: maintain a running histogram of past item sizes and bonus bi... |
| 82 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll keep best-fit dominant (ascending post-placement remainder) but strengthen the near-exact-fi... |
| 83 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll implement a "best fit with exponential tight-fit bias" that keeps best-fit ordering but adds... |
| 84 | edit | not_better | 0.9533 | 0.9593 | $0.0005 | Add a small bonus for bins whose post-placement remainder is exactly zero AND simultaneously stro... |
| 85 | edit | not_better | 0.9590 | 0.9593 | $0.0004 | The current rule is essentially best-fit, but adding any bin-specific bonus tends to hurt. I'll t... |
| 86 | edit | not_better | 0.7104 | 0.9593 | $0.0005 | I'll switch to a distribution-aware "least loaded that still fits effectively" rule: instead of b... |
| 87 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll add a tiny amount of state tracking the mean item size and use it to break ties only among b... |
| 88 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll replace the crude best-fit rule with the classic "best fit decreasing-style" exact-fit-first... |
| 89 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll replace the ad-hoc bonus with a proper distribution-aware score: maintain an online histogra... |
| 90 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll keep best-fit ordering but add a learned, distribution-aware tie-break only among near-equal... |
| 91 | edit | not_better | 0.9590 | 0.9593 | $0.0005 | I'll add the classic "best fit decreasing"-style improvement used in online settings: prefer an e... |
| 92 | edit | improved | 0.9935 | 0.9935 | $0.0006 | Replace best-fit with a rule that, after ensuring the item fits, ranks bins by a distribution-awa... |
| 93 | edit | not_better | 0.9930 | 0.9935 | $0.0007 | I'll change the gap scoring from symmetric closeness to the mean toward an asymmetric "reusable g... |
| 94 | edit | not_better | 0.9590 | 0.9935 | $0.0006 | I'll replace the fixed target-40 gap score with a classic Best-Fit rule (minimize post-placement ... |
| 95 | edit | improved | 0.9940 | 0.9940 | $0.0006 | I'll refine the tie-break granularity: instead of a single fixed target of 40, use an online runn... |
| 96 | edit | not_better | 0.5258 | 0.9940 | $0.0008 | I'll replace the simple mean-target gap score with a distribution-aware "expected residual packin... |
| 97 | edit | not_better | 0.5542 | 0.9940 | $0.0007 | I'll replace the single mean-target gap score with a distribution-aware "expected usable-gap" sco... |
| 98 | edit | not_better | 0.9915 | 0.9940 | $0.0007 | I'll replace the online-mean target with a Hybrid Best-Fit / target-gap rule: compute the post-pl... |
| 99 | edit | not_better | 0.9595 | 0.9940 | $0.0007 | I'll switch the gap target from the running mean to a value tuned to the Weibull distribution: us... |
| 100 | edit | not_better | 0.5854 | 0.9940 | $0.0006 | I'll keep exact-fit priority but replace the continuous mean-target gap score with a two-tier rul... |
| 101 | edit | not_better | 0.9915 | 0.9940 | $0.0006 | I'll refine the existing distribution-aware target-gap rule by making the target asymmetric: pref... |
| 102 | edit | not_better | 0.9590 | 0.9940 | $0.0007 | I'll keep the strong exact-fit bonus but replace the mean-target gap score with a hybrid that ble... |
| 103 | edit | not_better | 0.9590 | 0.9940 | $0.0006 | I'll make the exact-fill priority a proper lexicographic tie-break (exact fills first, then small... |
| 104 | edit | not_better | 0.9590 | 0.9940 | $0.0006 | I'll shift from "target-gap" scoring to a principled Best-Fit variant that breaks exact-fit ties ... |
| 105 | edit | not_better | 0.9590 | 0.9940 | $0.0005 | Replace the mean-target gap score with a Best-Fit rule that minimizes post-placement remainder, b... |
| 106 | edit | not_better | 0.9590 | 0.9940 | $0.0008 | I'll replace the target-gap scoring with a hybrid that combines classic Best-Fit (minimize remain... |
| 107 | edit | not_better | 0.9623 | 0.9940 | $0.0007 | I will replace the mean-target gap rule with a calibrated "residual reuse" score that rewards lea... |
| 108 | edit | not_better | 0.9835 | 0.9940 | $0.0007 | I'll keep the exact-fill bonus but change the gap target from the estimated mean to the most prob... |
| 109 | edit | not_better | 0.9590 | 0.9940 | $0.0006 | I'll shift the priority from a hard threshold to a smooth lexicographic ordering: rank bins prima... |
| 110 | edit | not_better | 0.9938 | 0.9940 | $0.0006 | The mean-target gap rule is leaving suboptimal remainders; I'll switch the secondary signal to an... |
| 111 | edit | not_better | 0.9859 | 0.9940 | $0.0007 | I'll replace the mean-based gap target with an online estimate of the largest common item size (e... |
| 112 | edit | not_better | 0.9913 | 0.9940 | $0.0007 | I'll keep the strong exact-fill bonus but switch the gap target from the running mean to the medi... |
| 113 | edit | not_better | 0.9876 | 0.9940 | $0.0007 | Replace the single-mean gap target with a small set of the most frequent observed item sizes (onl... |
| 114 | edit | not_better | 0.9590 | 0.9940 | $0.0006 | I'll blend the current mean-target gap score with the classic Best-Fit (smallest-remainder) signa... |
| 115 | edit | not_better | 0.9590 | 0.9940 | $0.0007 | Switch the primary secondary signal to classic Best-Fit (smallest post-placement remainder), whic... |
| 116 | edit | not_better | 0.9864 | 0.9940 | $0.0006 | I'll sharpen the gap target by using the empirical mode of item sizes (rounded histogram peak) in... |
| 117 | edit | not_better | 0.9588 | 0.9940 | $0.0006 | I'll keep the strong exact-fill bonus but change the secondary signal from a single mean-target g... |
| 118 | edit | not_better | 0.9590 | 0.9940 | $0.0005 | I'll combine exact-fill preference with a scaled best-fit signal: rank bins primarily by smallest... |
| 119 | edit | not_better | 0.9590 | 0.9940 | $0.0006 | Introduce a "worst-fit among near-best" rule: prefer the bin whose post-placement remainder is cl... |
| 120 | edit | not_better | 0.9590 | 0.9940 | $0.0007 | I'll replace the mean-target gap score with a distribution-aware rule: strongly prefer exact fill... |
| 121 | edit | not_better | 0.9634 | 0.9940 | $0.0007 | Replace the absolute-error gap score with a distribution-aware score that rewards remainders whic... |
| 122 | edit | not_better | 0.9822 | 0.9940 | $0.0008 | I'll replace the mean-target gap score with a tunable "greedy harmonic" style signal: strongly pr... |
| 123 | edit | not_better | 0.9646 | 0.9940 | $0.0007 | I'll make the exact-fill bonus depend on how "full" the bin is, using classic best-fit as primary... |
| 124 | edit | not_better | 0.9856 | 0.9940 | $0.0006 | I'll keep the strong exact-fill bonus and the mean-target gap scoring, but replace the single mea... |
| 125 | edit | not_better | 0.9623 | 0.9940 | $0.0007 | Replace the soft mean-target gap score with a distribution-aware "residual usability" score: keep... |
| 126 | edit | not_better | 0.9940 | 0.9940 | $0.0007 | I will keep the strong exact-fill bonus and the reusable-gap logic, but make the gap target adapt... |
| 127 | edit | not_better | 0.9609 | 0.9940 | $0.0006 | I'll refine the gap target to be a blend of the running mean with a smaller "residual-useful" tar... |
| 128 | edit | not_better | 0.9693 | 0.9940 | $0.0009 | I'll keep the exact-fill bonus and mean-matching structure but target a slightly smaller remainde... |
| 129 | edit | not_better | 0.9903 | 0.9940 | $0.0006 | I'll replace the single-mean gap target with a two-sided "sum-match" score: prefer placing the it... |
| 130 | edit | not_better | 0.9590 | 0.9940 | $0.0005 | I'll switch from the soft mean-gap score to a robust "best-fit with usable-gap tie-break": use be... |
| 131 | edit | improved | 0.9945 | 0.9945 | $0.0007 | I'll replace the mean-based gap target with a robust "residual matching" score computed against t... |
| 132 | edit | not_better | 0.9896 | 0.9945 | $0.0007 | I'll keep the reservoir-median gap target but weight the score by how plausible each bin's remain... |
| 133 | edit | not_better | 0.9590 | 0.9945 | $0.0007 | I will replace the fragile reservoir-median target with a smooth, online estimate of the item dis... |
| 134 | edit | not_better | 0.9940 | 0.9945 | $0.0006 | I'll replace the median target with the online mean of the item distribution (which is already tr... |
| 135 | edit | not_better | 0.9620 | 0.9945 | $0.0007 |  |
| 136 | edit | not_better | 0.9597 | 0.9945 | $0.0007 | I'll add a small online histogram of item sizes and score remainders by their expected "fillabili... |
| 137 | edit | not_better | 0.9223 | 0.9945 | $0.0007 | I'll keep the reservoir-median target but replace the hard sign-based exact-fill bonus with a con... |
| 138 | edit | not_better | 0.9935 | 0.9945 | $0.0007 | I'll add a small "sum-complement" bonus: prefer bins whose remainder after placement equals the i... |
| 139 | edit | not_better | 0.9627 | 0.9945 | $0.0007 | I'll replace the noisy reservoir-median gap target with a stable online linear-interpolation esti... |
| 140 | edit | not_better | 0.9910 | 0.9945 | $0.0007 | I'll keep the reservoir-median gap target but make the exact-fill preference smooth and add a mil... |
| 141 | edit | not_better | 0.9910 | 0.9945 | $0.0008 | I'll add a mild "potential waste" penalty that discourages leaving remainders too small to fit an... |
| 142 | edit | not_better | 0.9743 | 0.9945 | $0.0007 | I'll shift the gap target from the median toward a somewhat smaller order statistic (roughly the ... |
| 143 | edit | not_better | 0.9928 | 0.9945 | $0.0007 | I'll keep the strong exact-fill bonus and median gap-matching, but add a tiny deterministic best-... |
| 144 | edit | not_better | 0.9526 | 0.9945 | $0.0008 | Replace the hard 1000-point exact-fill bonus with a smooth, LP-inspired "residual fit" score: rew... |
| 145 | edit | invalid | 0.0000 | 0.9945 | $0.0007 | I'll replace the noisy reservoir-median with a smooth online kernel-density estimate of the item ... |
| 146 | edit | not_better | 0.9528 | 0.9945 | $0.0007 | Replace the exotic/slow approaches with a clean hybrid: score bins by how well the post-placement... |
| 147 | edit | not_better | 0.9925 | 0.9945 | $0.0007 | I'll keep the current structure but switch the gap target from the median to a weighted blend tha... |
| 148 | edit | not_better | 0.9590 | 0.9945 | $0.0006 | I'll replace the reservoir/median machinery with a simple, well-founded online estimate: keep a r... |
| 149 | edit | not_better | 0.9913 | 0.9945 | $0.0007 | I'll add a small tie-break toward tighter packing by breaking near-equal gap scores using the act... |
| 150 | edit | invalid | 0.0000 | 0.9945 | $0.0008 | I'll reduce the reservoir noise by replacing the median over a random reservoir with a determinis... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,52 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Distribution-aware best fit with reservoir-based residual matching.
+
+Items come from a fixed Weibull-shaped distribution (mean ~40). Pure best fit
+minimizes the immediate remainder but leaves tiny unusable gaps. Here we:
+  1. Strongly prefer exact fills (remainder 0).
+  2. Otherwise prefer the post-placement remainder closest to a robust estimate
+     of a typical future item size (an online reservoir median), so leftover
+     gaps stay reusable.
+"""
 import numpy as np
+import random
+
+_state = {"n": 0.0, "mean": 40.0, "res": [], "seen": 0}
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; highest wins, ties to first."""
+    # Online estimates of the item size distribution.
+    n = _state["n"]
+    m = _state["mean"]
+    _state["mean"] = (m * n + float(item)) / (n + 1.0)
+    _state["n"] = n + 1.0
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    # Reservoir sample of past item sizes to estimate a robust typical size.
+    _state["seen"] += 1
+    res = _state["res"]
+    if len(res) < 128:
+        res.append(float(item))
+    else:
+        j = random.randint(0, _state["seen"] - 1)
+        if j < 128:
+            res[j] = float(item)
+
+    if res:
+        target = float(np.median(res))
+        if target < 1.0:
+            target = 1.0
+    else:
+        target = _state["mean"]
+
+    rem = (bins - item).astype(np.float64)  # capacity left after placing
+
+    # Distance of the leftover gap from a typical future item size.
+    gap_score = -np.abs(rem - target)
+
+    # Strong bonus for exact fills (fully closed bins).
+    exact_bonus = np.where(rem <= 0.0, 1000.0, 0.0)
+
+    return gap_score + exact_bonus
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (23 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 27 | `res = _state['res']` | -0.9940 | essential: the program fails or turns invalid without it |
| 35 | `if res: ...` | -0.9940 | essential: the program fails or turns invalid without it |
| 42 | `rem = (bins - item).astype(np.float64)` | -0.9940 | essential: the program fails or turns invalid without it |
| 45 | `gap_score = -np.abs(rem - target)` | -0.9940 | essential: the program fails or turns invalid without it |
| 48 | `exact_bonus = np.where(rem <= 0.0, 1000.0, 0.0)` | -0.9940 | essential: the program fails or turns invalid without it |
| 50 | `term + exact_bonus` | -0.2729 | matters |
| 50 | `term + gap_score` | -0.0368 | matters |
| 40 | `target = _state['mean']` | -0.0049 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 20: `n = _state['n']`
- line 21: `m = _state['mean']`
- line 22: `_state['mean'] = (m * n + float(item)) / (n + 1.0)`
- line 23: `_state['n'] = n + 1.0`
- line 23: `term + n`
- line 23: `term + 1.0`
- line 26: `_state['seen'] += 1`
- line 28: `if len(res) < 128: ...`
- line 29: `res.append(float(item))`
- line 31: `j = random.randint(0, _state['seen'] - 1)`
- line 32: `if j < 128: ...`
- line 33: `res[j] = float(item)`
- line 36: `target = float(np.median(res))`
- line 37: `if target < 1.0: ...`
- line 38: `target = 1.0`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9940 | 0.9903 |
| minimal (9 parts removed) | 0.9935 | 0.9910 |

Minimal program:

```python
"""Distribution-aware best fit with reservoir-based residual matching.

Items come from a fixed Weibull-shaped distribution (mean ~40). Pure best fit
minimizes the immediate remainder but leaves tiny unusable gaps. Here we:
  1. Strongly prefer exact fills (remainder 0).
  2. Otherwise prefer the post-placement remainder closest to a robust estimate
     of a typical future item size (an online reservoir median), so leftover
     gaps stay reusable.
"""
import numpy as np
import random
_state = {'n': 0.0, 'mean': 40.0, 'res': [], 'seen': 0}

def priority(item, bins):
    """Return a priority for every bin in `bins`; highest wins, ties to first."""
    res = _state['res']
    if res:
        pass
    else:
        target = _state['mean']
    rem = (bins - item).astype(np.float64)
    gap_score = -np.abs(rem - target)
    exact_bonus = np.where(rem <= 0.0, 1000.0, 0.0)
    return gap_score + exact_bonus
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_a5000 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 0
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_a5000-s0   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `9f2bbd0772b0ec63759bdd119a5e2d9aa72eaa76`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_a5000/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_a5000/initial.py` `609927c5ea619a94`
- `problems/bp_sh_a5000/problem.md` `190017a698e23cd8`
- `problems/bp_sh_a5000/verify.py` `0c52b77a6e5ec18a`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
