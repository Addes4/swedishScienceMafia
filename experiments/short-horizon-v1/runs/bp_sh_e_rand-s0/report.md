# Research loop report: bp_sh_e_rand

| | |
|---|---|
| problem | `bp_sh_e_rand` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0857 of a $0.20 hard cap, 150 calls, 297,605 tokens |
| wall time | search 2000 s, baselines 209 s, explain 29 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (146 valid), 1 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9761 | 0.9655 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_e_rand/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_e_rand/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_e_rand/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9761 | 0.9655 | 0 parts removed |

Audit: public 0.9727 → 0.9761 (+0.0034), hidden 0.9634 → 0.9655 (+0.0021); public − hidden gap of the final program 0.0106.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0003 | Replace pure best-fit with a hybrid rule: mostly best-fit, but occasionally (based on bin fullnes... |
| 2 | edit | not_better | 0.9727 | 0.9727 | $0.0003 | I'll implement a "best fit with bounded waste" variant of first-fit-decreasing-style logic: score... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a two-region rule: prefer the tightest fit among bins that remain... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | The previous attempts all stayed close to best-fit and lost because the sample instances contain ... |
| 5 | edit | invalid | 0.0000 | 0.9727 | $0.0006 | I'll implement a small, safe twist on best-fit: keep pure best-fit as the primary rule, but break... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a score that adds a learned bias: bins whose post-placement resid... |
| 7 | edit | improved | 0.9761 | 0.9761 | $0.0005 | I'll implement a harmonic-style rule: prefer best-fit but with a strong bonus for filling the cur... |
| 8 | edit | not_better | 0.9698 | 0.9761 | $0.0005 | I'll switch to the classic "Best Fit with harmonic residual scaling": rank by tightest fit but mu... |
| 9 | edit | not_better | 0.9753 | 0.9761 | $0.0005 | I'll generalize the residual-waste penalty so any residual at or below roughly half the mean item... |
| 10 | edit | not_better | 0.9685 | 0.9761 | $0.0006 | I'll replace the fixed waste threshold with a dynamic one derived from a running histogram of ite... |
| 11 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the fixed waste penalty with a width-adaptive "gap-closing" score that rewards placi... |
| 12 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll implement a "smart best-fit with active-bin concentration" that keeps best-fit but adds a st... |
| 13 | edit | not_better | 0.9753 | 0.9761 | $0.0006 | Build on the current harmonic best-fit by adding a mild "gap-filling" preference: when a placemen... |
| 14 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the fixed waste threshold with a scale-invariant rule: score bins by a harmonic-styl... |
| 15 | edit | not_better | 0.9739 | 0.9761 | $0.0006 | I'll implement the classic Harmonic-K style bin-choice: rank bins primarily by which "size class"... |
| 16 | edit | not_better | 0.9761 | 0.9761 | $0.0006 | I'll add a small tie-breaking bonus that favors leaving a residual which exactly equals a size cl... |
| 17 | edit | not_better | 0.9685 | 0.9761 | $0.0006 | I'll shift from a fixed waste threshold to a scale-relative one: penalize post-placement residual... |
| 18 | edit | not_better | 0.9736 | 0.9761 | $0.0007 | I'll replace the waste-threshold penalty with a cleaner "residual targeting" rule: keep best-fit ... |
| 19 | edit | not_better | 0.9633 | 0.9761 | $0.0005 | I'll make the waste penalty finer-grained: instead of a flat penalty for residuals 1–19, penalize... |
| 20 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the fixed waste penalty with a learned approach: keep pure best-fit as the dominant ... |
| 21 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | Replace the threshold-based waste penalty with a smooth scale-invariant "residual quality" score:... |
| 22 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | Switch the base rule from best-fit (fullest bin) to a "residual targeting" fit that prefers placi... |
| 23 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | Replace the hand-tuned waste penalty with a principled bounded-score refinement: use best-fit as ... |
| 24 | edit | not_better | 0.9761 | 0.9761 | $0.0006 | I'll implement a proper Harmonic-style ranking: instead of pure best-fit, classify each bin by th... |
| 25 | edit | gate_rejected | 0.9769 | 0.9761 | $0.0006 | Replace pure best-fit with the classic Harmonic rule: partition items by size class (1/2, 1/3, ..... |
| 26 | edit | not_better | 0.9719 | 0.9761 | $0.0006 | Replace the flat waste penalty with a "least-waste best-fit": keep best fit as the main signal, b... |
| 27 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll switch the tie-break from "waste penalty" to a scale-free one that also reduces fragmentatio... |
| 28 | edit | not_better | 0.9761 | 0.9761 | $0.0005 | I'll replace the hand-tuned waste penalty with a proper Harmonic-style rule: classify the arrivin... |
| 29 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll implement a proper Harmonic-style class rule: classify the arriving item by its size, then w... |
| 30 | edit | not_better | 0.9718 | 0.9761 | $0.0005 | I will replace the ad-hoc waste penalty with a bounded "best-fit plus residue-utility" score: ran... |
| 31 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll keep best-fit as the primary key but replace the flat waste penalty with a linear-near thres... |
| 32 | edit | invalid | 0.0000 | 0.9761 | $0.0006 | I'll replace the heuristic with a principled "best-fit with monotone decreasing dead-space thresh... |
| 33 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the heuristic scoring with a proper Harmonic-style rule that classifies the arriving... |
| 34 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I will add a second-phase tie-break that prefers placing into a bin whose residual after placemen... |
| 35 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll implement the classic "best fit plus a small constant bonus for bins that are already nearly... |
| 36 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the fixed waste penalty with a data-driven "residual utility" score: track the empir... |
| 37 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll switch from a heuristic waste penalty to a first-fit-decreasing-style rule that keeps bins s... |
| 38 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste penalty with a bounded score that primarily ranks by best fit but a... |
| 39 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll replace the heuristic with a Djang & Finch-style "best fit with bounded fallback": rank bins... |
| 40 | edit | not_better | 0.9682 | 0.9761 | $0.0006 | I will implement a "rank by best-fit but skip bins that would strand a small unusable residual, c... |
| 41 | edit | not_better | 0.9727 | 0.9761 | $0.0004 | I'll switch the rule to classic Best-Fit (rank by smallest post-placement residual, i.e. fullest ... |
| 42 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll switch to a Harmonic-style rule: partition bin capacities into size classes and prefer bins ... |
| 43 | edit | not_better | 0.9718 | 0.9761 | $0.0007 | Implement a learned online "residual value" ranking: maintain an empirical item-size histogram an... |
| 44 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a capacity-class "harmonic" bias that favors leaving r... |
| 45 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll add a bounded bonus for bins whose post-placement residual is 0 (exact fill) combined with a... |
| 46 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste penalty with the classic Best-Fit-Decreasing-like "best fit" rankin... |
| 47 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll tune the existing best-fit-plus-waste-penalty rule by making the waste threshold and penalty... |
| 48 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll add a smarter tie-break: rank primarily by smallest post-placement residual (best fit), but ... |
| 49 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | The waste penalty should only punish residuals too small to ever be usable; I'll learn the minimu... |
| 50 | edit | not_better | 0.9742 | 0.9761 | $0.0005 | Introduce a two-term score that combines the classic "best fit" tightness with an explicit penalt... |
| 51 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc penalty with a proper "least-likely-to-waste" rule: rank by smallest post... |
| 52 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll switch from the hand-tuned waste penalty to a cleaner formulation: pure best-fit tightening ... |
| 53 | edit | invalid | 0.0000 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste penalty with a principled rule that mimics "Best Fit" while avoidin... |
| 54 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll implement a "best fit with harmonic/almost-worst tie handling" that ranks primarily by small... |
| 55 | edit | not_better | 0.9724 | 0.9761 | $0.0005 | Replace the ad-hoc waste penalty with a "best fit decreasing-flavored" rule that uses pure best f... |
| 56 | edit | not_better | 0.9725 | 0.9761 | $0.0005 | I'll try the classic "harmonic/dominant" online heuristic: rank by smallest post-placement residu... |
| 57 | edit | not_better | 0.9701 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste penalty with the classic "Best Fit" rule augmented by a self-consis... |
| 58 | edit | not_better | 0.9718 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a score based on the actual empirical item-size distri... |
| 59 | edit | not_better | 0.9730 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a "best fit plus scale-aware residual penalty": rank b... |
| 60 | edit | not_better | 0.9718 | 0.9761 | $0.0007 | The current waste penalty is a fixed threshold applied uniformly; I'll make the rule adaptively l... |
| 61 | edit | not_better | 0.7236 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste penalty with "Worst Fit" among bins that still leave a reusable res... |
| 62 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the fixed-threshold waste penalty with an online-learned empirical distribution: acc... |
| 63 | edit | not_better | 0.9708 | 0.9761 | $0.0005 | I'll change the base rule from best-fit to a scaled "almost-worst-fit-with-integer-residual-align... |
| 64 | edit | not_better | 0.9535 | 0.9761 | $0.0005 | The current rule is best-fit with a small waste penalty. The strongest known competitive online r... |
| 65 | edit | not_better | 0.6509 | 0.9761 | $0.0006 | I'll replace the fixed waste threshold with a data-driven penalty that adapts to the observed ite... |
| 66 | edit | not_better | 0.9747 | 0.9761 | $0.0006 | I'll switch the base rule from best-fit to worst-fit-among-fitting-bins for large items while kee... |
| 67 | edit | not_better | 0.9738 | 0.9761 | $0.0005 | I'll refine the waste penalty to use a two-tier scheme with a tunable knee: penalize tiny unusabl... |
| 68 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the ad-hoc fixed waste penalty with a principled "expected leftover compatibility" s... |
| 69 | edit | invalid | 0.0000 | 0.9761 | $0.0007 | I'll add a small data-driven residual-matching bonus/penalty: track an online histogram of item s... |
| 70 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll replace the simplistic fixed-threshold waste penalty with a monotone concave penalty on the ... |
| 71 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the fixed waste penalty with a smooth, adaptive penalty based on the empirical item-... |
| 72 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the ad-hoc waste penalty with an online-learned "fit potential" score: for each cand... |
| 73 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a principled "match the residual to the item distribut... |
| 74 | edit | not_better | 0.9761 | 0.9761 | $0.0005 | I'll revert to the simple best-fit plus flat waste penalty (which scored 0.976) and extend the pe... |
| 75 | edit | not_better | 0.9724 | 0.9761 | $0.0006 | I'll replace the flat waste penalty with an asymmetric rule: keep the best-fit base, heavily pena... |
| 76 | edit | not_better | 0.9759 | 0.9761 | $0.0005 | I'll switch from pure best-fit to a "best fit with a residual-fit bonus": keep best-fit as the ba... |
| 77 | edit | not_better | 0.9761 | 0.9761 | $0.0005 | I'll add a small tie-breaking bonus that prefers placing the item into a bin whose post-placement... |
| 78 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the ad-hoc waste penalty with a smooth, distribution-aware reward based on the empir... |
| 79 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | Replace the ad-hoc waste penalty with the well-known Harmonic bin-packing weighting: score each b... |
| 80 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll replace the tie-breaking-only tweaks with a genuinely different rule: best-fit combined with... |
| 81 | edit | not_better | 0.9725 | 0.9761 | $0.0005 | I'll bias best-fit toward keeping bins on the "capacity class boundaries" of the classic Harmonic... |
| 82 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | Best-fit alone ignores whether the leftover capacity is usable, and prior ad-hoc penalties hurt. ... |
| 83 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll switch to a scale-aware best-fit rule that derives the waste penalty from the actual item-si... |
| 84 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I will replace the wasteful heuristic tweaks with a principled scale-aware best-fit: score bins b... |
| 85 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | (no description) |
| 86 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the current heuristic with a scale-aware "residual usability" rule: estimate the emp... |
| 87 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll switch from the ad-hoc waste penalty to a well-aged "best fit with large-residual preference... |
| 88 | edit | not_better | 0.9728 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste heuristic with a proper Worst-Fit-style exploration: score bins by ... |
| 89 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll discard the ad-hoc waste penalty and go back to a clean, strong-fit scoring: reward exact fi... |
| 90 | edit | not_better | 0.9725 | 0.9761 | $0.0007 | Implement the classic Harmonic (H_k) online bin-packing rule: classify each item into harmonic si... |
| 91 | edit | not_better | 0.9728 | 0.9761 | $0.0006 | Refine the waste penalty to be maximized for the smallest non-zero residuals (a near-zero leftove... |
| 92 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll implement a "best fit with aging/spread" variant used in the literature (a.k.a. Best-Fit wit... |
| 93 | edit | not_better | 0.9727 | 0.9761 | $0.0008 | Add an online-learned "waste" correction: track the empirical distribution of item sizes seen so ... |
| 94 | edit | not_better | 0.9704 | 0.9761 | $0.0006 | I'll replace the flat waste penalty with a data-driven "residual usability" score that learns the... |
| 95 | edit | not_better | 0.9716 | 0.9761 | $0.0005 | I'll replace the ad-hoc penalty with a classic, theory-backed approach: score each bin so that pl... |
| 96 | edit | not_better | 0.6047 | 0.9761 | $0.0006 | The current rule is essentially Best Fit plus a small penalty for tiny residuals. Best Fit is wea... |
| 97 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll keep the best-fit base but replace the flat tiny-residual penalty with a graded penalty plus... |
| 98 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc residual penalty with the classic Best-Fit-Decreasing-style "almost-worst... |
| 99 | edit | not_better | 0.8689 | 0.9761 | $0.0006 | I'll replace the residual-threshold heuristic with a proper online "harmonic"-style scoring: rank... |
| 100 | edit | not_better | 0.9724 | 0.9761 | $0.0005 | The current best-fit-plus-small-waste-penalty is strong; I'll refine it by making the tiny-residu... |
| 101 | edit | not_better | 0.9716 | 0.9761 | $0.0005 | I'll add a small deterministic tie-breaking refinement: keep pure best-fit as the dominant term b... |
| 102 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | Strengthen the pure best-fit rule by removing the destabilizing waste penalty entirely and instea... |
| 103 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | Best Fit alone is already near-optimal here, so I'll switch to a full "First-Fit-with-sum-of-squa... |
| 104 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the fixed waste penalty with an adaptive "best-fit with a tunable exponential residu... |
| 105 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll discard the ad-hoc waste penalty and implement a proper online variant of Harmonic/Sum-of-Sq... |
| 106 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | Replace the fragile hand-tuned waste penalty with pure, exact Best-Fit (smallest remaining capaci... |
| 107 | edit | not_better | 0.9733 | 0.9761 | $0.0008 | I'll implement a proper harmonic-style bucketing on the item size (not just residual), which is a... |
| 108 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll keep the strong best-fit core but replace the fixed waste penalty with a principled "least-f... |
| 109 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a proper Best-Fit-Decreasing-style "residual class" we... |
| 110 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a harmonic-class hybrid: keep best-fit as the dominant... |
| 111 | edit | not_better | 0.9727 | 0.9761 | $0.0008 | I'll replace the ad-hoc heuristic with a proper Best-Fit-Decreasing-informed rule: since items ar... |
| 112 | edit | not_better | 0.9728 | 0.9761 | $0.0005 | I'll strengthen the original waste-penalty idea into a principled two-sided residual target: domi... |
| 113 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | The ad-hoc fixed-threshold waste penalty is fragile; I'll replace it with a smoother, more princi... |
| 114 | edit | not_better | 0.9652 | 0.9761 | $0.0005 | I'll replace the ad-hoc fixed waste penalty with an exact Best-Fit core plus a small bonus that t... |
| 115 | edit | not_better | 0.9738 | 0.9761 | $0.0007 | I'll replace the ad-hoc fixed waste penalty with a principled residual-harmonic scheme: bins whos... |
| 116 | edit | not_better | 0.9722 | 0.9761 | $0.0005 | I'll switch the core ranking from "best fit" (which greedily minimizes the immediate residual) to... |
| 117 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll generalize the ad-hoc fixed waste penalty into a tunable two-part rule: keep best-fit as the... |
| 118 | edit | not_better | 0.9725 | 0.9761 | $0.0006 | The fixed waste penalty is too blunt; I'll replace it with a best-fit core plus a penalty that ta... |
| 119 | edit | not_better | 0.9687 | 0.9761 | $0.0006 | I'll switch to a lower-bound-aware "score = -remaining unless it strands capacity" rule by using ... |
| 120 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll keep the best-fit core but replace the blunt fixed-threshold waste penalty with a sharper, s... |
| 121 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I notice instances 1 and 2 score ~0.964 while instance 3 is perfect, meaning the ranking is close... |
| 122 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll switch from a heuristic penalty to a proper online-learning approach: maintain per-residual-... |
| 123 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll try the classic Harmonic-style rule directly: for each bin, compute the residual after placi... |
| 124 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the ad-hoc residual-waste penalty with a proper "best fit decreasing awareness" rule... |
| 125 | edit | gate_rejected | 0.9775 | 0.9761 | $0.0005 | I'll replace the whole scoring rule with the classic online harmonic rule: classify each bin by t... |
| 126 | edit | not_better | 0.9750 | 0.9761 | $0.0006 | I'll keep the proven best-fit core but make the waste penalty adaptive and directional: penalize ... |
| 127 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll keep the best-fit core but replace the ad-hoc residual penalty with a two-sided rule that al... |
| 128 | edit | not_better | 0.9722 | 0.9761 | $0.0005 | I'll gate the tiniest-residual waste penalty on the item's own scale rather than a fixed threshol... |
| 129 | edit | not_better | 0.9711 | 0.9761 | $0.0006 | I'll keep the best-fit core but add a directional penalty based on a learned running distribution... |
| 130 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | Replace the fixed residual waste penalty with a principled "best-fit plus small residual dash" th... |
| 131 | edit | not_better | 0.9724 | 0.9761 | $0.0006 | I'll switch the waste penalty from a hard threshold to a smooth, scale-aware rule: keep the best-... |
| 132 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the heuristic waste penalty with a proper harmonic-style packing rule: prefer the bi... |
| 133 | edit | not_better | 0.9725 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with the well-known "best fit decreasing"-style tie-broken ... |
| 134 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | The fixed waste penalty threshold of 19 is arbitrary; I'll instead implement a smooth, principled... |
| 135 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | Replace the ad-hoc best-fit-with-waste-penalty with the classic "best fit with a small-item apert... |
| 136 | edit | not_better | 0.9752 | 0.9761 | $0.0008 | I'll replace the fixed residual waste threshold (19) with an adaptive one derived from the runnin... |
| 137 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I will replace the ad-hoc waste penalty with the classic "best-fit plus shared-capacity reward": ... |
| 138 | edit | not_better | 0.9484 | 0.9761 | $0.0006 | I'll strengthen the concentration effect by making the residual penalty depend on the item size: ... |
| 139 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the hard-threshold waste penalty with a principled "scrap" penalty that uses a runni... |
| 140 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll keep the strong best-fit core but replace the fixed residual penalty with the well-known "be... |
| 141 | edit | invalid | 0.0000 | 0.9761 | $0.0005 | I'll replace the ad-hoc waste penalty with a refinement of the best-fit rule that breaks ties by ... |
| 142 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll keep the best-fit core but replace the ad-hoc waste penalty with the classic "best fit with ... |
| 143 | edit | not_better | 0.9727 | 0.9761 | $0.0006 | I'll replace the ad-hoc waste penalty with a principled "residual value" score: dominant best-fit... |
| 144 | edit | not_better | 0.9727 | 0.9761 | $0.0007 | I'll replace the sharp-threshold waste penalty with a soft ramp that penalizes small post-placeme... |
| 145 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I will replace the ad-hoc penalty with the classic "best fit with a fill-level bonus" tuned by a ... |
| 146 | edit | not_better | 0.9728 | 0.9761 | $0.0005 | I'll switch from the fixed best-fit-plus-waste rule to a harmonic-style score that balances tight... |
| 147 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll replace the fixed residual-waste penalty with a smooth, best-fit-dominant score that adds a ... |
| 148 | edit | not_better | 0.9727 | 0.9761 | $0.0005 | I'll switch to the standard "best fit decreasing"-inspired rule that is provably strong for onlin... |
| 149 | edit | not_better | 0.9731 | 0.9761 | $0.0005 | The previous attempts all hovered near 0.972 while the current ad-hoc rule scores 0.976; I'll str... |
| 150 | edit | not_better | 0.9713 | 0.9761 | $0.0005 | I'll use a two-phase rule: keep the strong best-fit concentration but explicitly detect exact/nea... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,5 +1,5 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Harmonic-flavored best fit: concentrate items into the fullest fitting bin."""
 import numpy as np
 
 
@@ -10,5 +10,12 @@
     bins: numpy int64 array with the remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    # Use best fit as the base ranking, but bias toward bins that stay fullest after
+    # placing the item, so we concentrate packing into fewer, tighter bins.
+    remaining = bins - item
+    best_fit = -remaining  # higher is tighter fit
+    # Penalize leaving small leftover residuals (hard-to-reuse capacity).
+    # Residual <= some threshold is considered waste.
+    waste = np.where((remaining > 0) & (remaining <= 19), remaining, 0)
+    return best_fit.astype(np.float64) - 2.0 * waste
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (7 parts, 8 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 15 | `remaining = bins - item` | -0.9761 | essential: the program fails or turns invalid without it |
| 15 | `term + bins` | -0.9761 | essential: the program fails or turns invalid without it |
| 16 | `best_fit = -remaining` | -0.9761 | essential: the program fails or turns invalid without it |
| 19 | `waste = np.where((remaining > 0) & (remaining <= 19), remaining, 0)` | -0.9761 | essential: the program fails or turns invalid without it |
| 15 | `term - item` | -0.0215 | matters |
| 20 | `term + best_fit.astype(np.float64)` | -0.0124 | matters |
| 20 | `term - 2.0 * waste` | -0.0034 | matters |

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9761 | 0.9655 |
| minimal (0 parts removed) | 0.9761 | 0.9655 |

Minimal program:

```python
"""Harmonic-flavored best fit: concentrate items into the fullest fitting bin."""
import numpy as np

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    remaining = bins - item
    best_fit = -remaining
    waste = np.where((remaining > 0) & (remaining <= 19), remaining, 0)
    return best_fit.astype(np.float64) - 2.0 * waste
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_e_rand --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 0
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_e_rand-s0   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_e_rand/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_e_rand/initial.py` `609927c5ea619a94`
- `problems/bp_sh_e_rand/problem.md` `190017a698e23cd8`
- `problems/bp_sh_e_rand/suite.json` `7e369a6aa9869ab4`
- `problems/bp_sh_e_rand/verify.py` `0f28aa90e2f40f70`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
