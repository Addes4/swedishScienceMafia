# Research loop report: bp_sh_b200

| | |
|---|---|
| problem | `bp_sh_b200` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0941 of a $0.20 hard cap, 150 calls, 323,113 tokens |
| wall time | search 1328 s, baselines 58 s, explain 54 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (147 valid), 4 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9444 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9480 | 0.9671 |  |
| baseline `funsearch_or` | 0.9552 | 0.9711 | `problems/bp_sh_b200/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.8723 | 0.9937 | `problems/bp_sh_b200/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9200 | 0.9950 | `problems/bp_sh_b200/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9462 | 0.9648 | 5 parts removed |

Audit: public 0.9444 → 0.9480 (+0.0036), hidden 0.9634 → 0.9671 (+0.0037); public − hidden gap of the final program -0.0191.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9552). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9444 | 0.9444 | $0.0003 | I will add a small tie-breaking bias toward *fuller* bins (smaller remaining capacity even among ... |
| 2 | edit | improved | 0.9446 | 0.9446 | $0.0004 | I'll switch from pure best-fit to a hybrid rule that prefers filling bins to capacity but falls b... |
| 3 | edit | not_better | 0.9446 | 0.9446 | $0.0004 | I'll replace the ad-hoc awkward-gap penalty with a principled "residual waste" rule: score each u... |
| 4 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the heuristic with a proper "best fit decreasing"-style rule: prefer the fullest bin... |
| 5 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I will replace the heuristic with a threshold-based rule derived from the item distribution: a us... |
| 6 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll implement a proper "residual waste" score based on the online-estimated item-size distributi... |
| 7 | edit | not_better | 0.9446 | 0.9446 | $0.0008 | I'll replace the ad-hoc awkward-gap heuristic with a principled rule that estimates the item-size... |
| 8 | edit | not_better | 0.5990 | 0.9446 | $0.0006 | I'll replace the ad-hoc heuristic with a well-tuned "modified first fit" style rule: score by rem... |
| 9 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the heuristic with a "best fit plus a capped matching bonus": score by smallest left... |
| 10 | edit | not_better | 0.9446 | 0.9446 | $0.0005 | I will replace the heuristic scoring with a proper Best-Fit Decreasing-style rule enhanced by an ... |
| 11 | edit | not_better | 0.9446 | 0.9446 | $0.0005 | I'll replace the ad-hoc penalty with a well-known strong online heuristic: a scaled "best-fit wit... |
| 12 | edit | not_better | 0.9426 | 0.9446 | $0.0006 | Replace the scoring with an online-distribution-aware rule that estimates the empirical CDF of it... |
| 13 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll switch from this ad-hoc penalty to the classic "best-fit with a small penalty for opening fr... |
| 14 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the heuristic with a distribution-aware "expected leftover usefulness" rule: estimat... |
| 15 | edit | not_better | 0.3990 | 0.9446 | $0.0005 | I'll replace the heuristic with a classic "Almost-Worst-Fit" rule that has proven near-optimal fo... |
| 16 | edit | not_better | 0.9444 | 0.9446 | $0.0007 | I'll add a small "completability" bonus: keep best-fit as the dominant term, but slightly reward ... |
| 17 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Add a "medium-fit" term that slightly favors bins leaving a leftover close to the current item si... |
| 18 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc penalty with a principled "best-fit + small fresh-bin bonus proportional ... |
| 19 | edit | not_better | 0.9446 | 0.9446 | $0.0006 | I'll add a small "exact-fit / near-exact-fill" priority: keep best-fit as the base, but give a st... |
| 20 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc penalty with the well-known "Best-Fit with a threshold on small items" hy... |
| 21 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the current heuristic with a harmonic/weighted best-fit rule: score each bin by a de... |
| 22 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc penalty with the classic "Best Fit Decreasing"-style rule refined by a tu... |
| 23 | edit | not_better | 0.9446 | 0.9446 | $0.0005 | I'll switch to a rank-based "best-fit with fresh-bin preference when best leftover is large" rule... |
| 24 | edit | gate_rejected | 0.9446 | 0.9446 | $0.0005 | I'll replace the heuristic with the classic "almost-worst-fit with a cap": among bins whose lefto... |
| 25 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc "awkward gap" penalty with a cleaner rule: dominant best-fit (smallest le... |
| 26 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll implement a proper Best-Fit with an adaptive "fill-the-smallest-adequate-gap" priority that ... |
| 27 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | Replace the ad-hoc heuristic with the classic Best-Fit rule (smallest leftover after placing), wh... |
| 28 | edit | not_better | 0.9440 | 0.9446 | $0.0006 | I'll keep best-fit dominant but strengthen and refine the awkward-gap penalty: only penalize non-... |
| 29 | edit | not_better | 0.9446 | 0.9446 | $0.0007 | Replace the ad-hoc linear "awkward" penalty with a convex penalty on the leftover relative to the... |
| 30 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll switch from a leftover-based penalty to a suboptimality-style rule: score each bin by how mu... |
| 31 | edit | not_better | 0.9444 | 0.9446 | $0.0008 |  |
| 32 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll add a "good pairing" bonus that rewards placing the item so the leftover closely equals the ... |
| 33 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc awkward-gap penalty with a principled rule based on the item distribution... |
| 34 | edit | gate_rejected | 0.9451 | 0.9446 | $0.0006 | I'll replace the ad-hoc awkward penalty with a threshold rule: score = -(leftover) for used bins,... |
| 35 | edit | not_better | 0.9397 | 0.9446 | $0.0007 | I'll replace the absolute "awkward gap" penalty with a relative-waste criterion: score used bins ... |
| 36 | edit | gate_rejected | 0.9449 | 0.9446 | $0.0006 | I'll implement a clean threshold-based rule: use best-fit scoring for used bins, but if even the ... |
| 37 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | The ad-hoc awkward penalty is being applied too eagerly; I'll replace it with a proper "almost-fu... |
| 38 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | Replace the ad-hoc awkward-gap penalty with a "subharmonic best-fit" rule: score used bins by bes... |
| 39 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I will replace the ad-hoc awkward-gap penalty with a "power-of-two / harmonic" style rule: keep b... |
| 40 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc squared/awkward penalties with the classic, theoretically-grounded "harmo... |
| 41 | edit | not_better | 0.9442 | 0.9446 | $0.0006 | I'll replace the rule with the classic "best-fit with a single threshold that opens a new bin whe... |
| 42 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I will switch to a well-known online packing heuristic tuned for this item distribution: score us... |
| 43 | edit | not_better | 0.9415 | 0.9446 | $0.0006 | I'll replace the ad-hoc awkward penalty with a clean best-fit-plus-consolidation rule: rank used ... |
| 44 | edit | not_better | 0.9437 | 0.9446 | $0.0006 | I'll replace the ad-hoc penalty with the well-established "best fit decreasing-style" scoring plu... |
| 45 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | The recent tweaks all hover around the same best-fit family. I'll switch to a genuinely different... |
| 46 | edit | not_better | 0.9382 | 0.9446 | $0.0007 | I'll replace the ad-hoc awkward penalty with a rule that penalizes creating bins whose resulting ... |
| 47 | edit | not_better | 0.9444 | 0.9446 | $0.0011 | Replace the ad-hoc awkward-gap penalty with a distribution-aware residual-matching rule: keep bes... |
| 48 | edit | not_better | 0.9446 | 0.9446 | $0.0007 | I'll replace the awkward-gap penalty with a threshold-based best-fit: keep best-fit as base, but ... |
| 49 | edit | not_better | 0.9444 | 0.9446 | $0.0007 | I'll replace the rule with a "best-fit plus bounded residual matching" that uses the empirically ... |
| 50 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll simplify to a robust baseline: score by best-fit (smallest leftover) with a strong bonus for... |
| 51 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc penalty with a principled "best-fit with exact-fill reward and empty-bin ... |
| 52 | edit | not_better | 0.9444 | 0.9446 | $0.0007 | I'll switch from the ad-hoc awkward-gap penalty to a well-founded "best fit with a residual-compa... |
| 53 | edit | not_better | 0.8733 | 0.9446 | $0.0006 | I'll replace the fragile awkward-gap penalty with the classic and well-founded "best fit decreasi... |
| 54 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc awkward penalty with an exponential moving average of the actual "waste c... |
| 55 | edit | invalid | 0.0000 | 0.9446 | $0.0008 | I'll replace the heuristic with a principled "second-best-fit / least-regret" rule: best-fit can ... |
| 56 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll revert to the clean best-fit base but add a carefully-scaled empty-bin penalty that grows wi... |
| 57 | edit | not_better | 0.9446 | 0.9446 | $0.0005 | I'll test a "harmonic/interval-matching" rule: keep best-fit as the base, but add a substantial b... |
| 58 | edit | not_better | 0.9442 | 0.9446 | $0.0005 | I'll refine the awkward-gap penalty: instead of clipping at zero, add a quadratic penalty on left... |
| 59 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Replace the heuristic scoring with the classic "best fit" rule (pure smallest post-placement left... |
| 60 | edit | invalid | 0.0000 | 0.9446 | $0.0006 | I'll replace the rule with a scale-free "relative best fit" that scores bins by the fraction of t... |
| 61 | edit | not_better | 0.9439 | 0.9446 | $0.0005 | I'll implement a two-parameter "best-fit with empty-bin bonus" using a smooth comparison: score u... |
| 62 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll switch to a "modified best-fit" that prioritizes filling a bin exactly (residual 0) or, fail... |
| 63 | edit | not_better | 0.9444 | 0.9446 | $0.0008 | Implement a "fill-target best-fit": keep tight-fit preference but add a bonus to bins whose post-... |
| 64 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | Introduce "fit-aware best fit": keep best-fit as the base but add a strong bonus when the post-pl... |
| 65 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll implement "best-fit with a small empty-bin bonus proportional to how poorly the item fits an... |
| 66 | edit | not_better | 0.9422 | 0.9446 | $0.0006 | I'll implement the classic "best fit decreasing-like" rule with a targeted improvement: score bin... |
| 67 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll add a score term that explicitly rewards reusing an existing bin (any non-empty bin) over op... |
| 68 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the score with a "tie-broken best fit": primary term is best-fit (smallest residual)... |
| 69 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the heuristic with a learned-style "best-fit with a residual-target bonus": track an... |
| 70 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Many recent tweaks plateaued around 0.944. I'll replace the hand-tuned penalty with a principled ... |
| 71 | edit | not_better | 0.9310 | 0.9446 | $0.0006 | I'll replace the heuristic with a "worst-fit with a freshness gate": use best-fit for the bulk of... |
| 72 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll implement a proper "best-fit with a capacity-waste guard" based on the observation that best... |
| 73 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll switch the tie-break to a well-known superior rule for this distribution: score by "best fit... |
| 74 | edit | not_better | 0.9019 | 0.9446 | $0.0007 | I'll replace the heuristic with a "best-fit avoiding tiny unfillable gaps": among bins, strongly ... |
| 75 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Replace the ad-hoc penalty with the classic Best-Fit-Decreasing-style rule combined with a small ... |
| 76 | edit | invalid | 0.0000 | 0.9446 | $0.0005 | I'll replace the heuristic with a "best-fit plus bounded-waste threshold" rule: primary best-fit,... |
| 77 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc penalty with a cleaner rule based on the known strong behavior for Weibul... |
| 78 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Replace the heuristic scoring with a "fuller-bin-first" rule: score primarily by pre-placement re... |
| 79 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Pure best-fit is near-optimal here, but its failures come from creating small unfillable residual... |
| 80 | edit | not_better | 0.9408 | 0.9446 | $0.0006 | I'll add a learned-style threshold: instead of penalizing awkward gaps with a raw leftover term, ... |
| 81 | edit | not_better | 0.9429 | 0.9446 | $0.0006 | I'll replace the heuristic with the classic "modified best fit" that prefers an exact/near-exact ... |
| 82 | edit | not_better | 0.9173 | 0.9446 | $0.0006 | I'll adaptively track the minimum item size seen so far in the stream, and penalize leaving a res... |
| 83 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc heuristic with a "best-fit with smart empty-bin avoidance" rule: rank pri... |
| 84 | edit | not_better | 0.9422 | 0.9446 | $0.0005 | I'll switch the primary criterion from post-placement residual to a fractional "waste ratio" only... |
| 85 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll implement a well-known improvement: Best-Fit with a small "look-ahead" threshold, replacing ... |
| 86 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll switch from the ad-hoc awkward-gap penalty to a principled "Best-Fit Decreasing-style" rule:... |
| 87 | edit | not_better | 0.9429 | 0.9446 | $0.0006 | I'll replace the ad-hoc awkward-gap penalty with a principled score that combines best-fit (small... |
| 88 | edit | not_better | 0.9382 | 0.9446 | $0.0006 | (no description) |
| 89 | edit | not_better | 0.9444 | 0.9446 | $0.0004 | I'll replace the ad-hoc heuristic with the classic "Best Fit" rule that simply ranks bins by smal... |
| 90 | edit | improved | 0.9462 | 0.9462 | $0.0006 | Replace the ad-hoc awkward penalty with a cleaner rule: rank by post-placement residual (best fit... |
| 91 | edit | not_better | 0.9440 | 0.9462 | $0.0005 | I'll add a light "residual-match" bonus: among used bins, after best-fit ranking, nudge scores to... |
| 92 | edit | not_better | 0.9455 | 0.9462 | $0.0006 | I'll make the "wasteful" test relative rather than absolute: promote an empty bin when the best u... |
| 93 | edit | improved | 0.9464 | 0.9464 | $0.0007 | The key fix: rather than an absolute "residual > item" test, gate the empty-bin promotion on item... |
| 94 | edit | invalid | 0.0000 | 0.9464 | $0.0008 | Replace the fixed thresholds/bonus with a data-driven residual-quality score: keep best-fit as th... |
| 95 | edit | not_better | 0.9440 | 0.9464 | $0.0007 | Rework the empty-bin promotion into a principled "future-fit" score: keep best-fit as the primary... |
| 96 | edit | not_better | 0.9431 | 0.9464 | $0.0007 | I'll replace the ad-hoc thresholds with the classic Best-Fit-Decreasing-style rule augmented by a... |
| 97 | edit | not_better | 0.9462 | 0.9464 | $0.0006 | I'll add a small constant bias that promotes empty bins a bit more aggressively for large items a... |
| 98 | edit | not_better | 0.9453 | 0.9464 | $0.0006 | I'll replace the crude linear empty-bin promotion with a smoother, better-calibrated rule: keep b... |
| 99 | edit | not_better | 0.9444 | 0.9464 | $0.0008 | I will replace the fixed item-size gating with an adaptive rule that promotes an empty bin whenev... |
| 100 | edit | not_better | 0.9347 | 0.9464 | $0.0010 | I'll add a smooth best-fit rule with a data-driven "fillability" score: primary term is best-fit ... |
| 101 | edit | not_better | 0.9353 | 0.9464 | $0.0006 | I'll change the rule so that the empty-bin promotion is based on the "awkwardness" of the residua... |
| 102 | edit | not_better | 0.9424 | 0.9464 | $0.0006 | Replace the empty-bin promotion with a "perfect-fit / small-residual reservation" rule: keep best... |
| 103 | edit | not_better | 0.9462 | 0.9464 | $0.0006 | I'll refine the empty-bin promotion so that instead of a linear ramp, it fires only for truly lar... |
| 104 | edit | not_better | 0.9455 | 0.9464 | $0.0006 | I'll broaden the empty-bin promotion window so that moderately large items (not just the very lar... |
| 105 | edit | not_better | 0.9444 | 0.9464 | $0.0007 | I'll make the empty-bin promotion depend on whether a good used-bin fit exists: keep best-fit as ... |
| 106 | edit | not_better | 0.9462 | 0.9464 | $0.0007 | I'll make the empty-bin promotion adaptive to the current bin state: reserve a fresh bin only whe... |
| 107 | edit | not_better | 0.9451 | 0.9464 | $0.0006 | I'll add a small "exact-fit first" preference to the primary term: a tiny bonus scaled by the neg... |
| 108 | edit | not_better | 0.9442 | 0.9464 | $0.0007 | Replace the heuristic combination with a cleaner two-regime rule: pure best-fit when a used bin c... |
| 109 | edit | not_better | 0.9462 | 0.9464 | $0.0007 | I'll replace the ad-hoc scoring with a learned-style linear combination of three normalized featu... |
| 110 | edit | not_better | 0.9462 | 0.9464 | $0.0006 | Replace the fixed linear empty-bin promotion with a size-relative best-fit rule: prefer the used ... |
| 111 | edit | not_better | 0.9460 | 0.9464 | $0.0006 | I'll replace the simple best-fit primary term with a scaled best-fit that emphasizes tight fits, ... |
| 112 | edit | not_better | 0.9437 | 0.9464 | $0.0008 | Replace the empty-bin promotion and absolute wasteful test with a relative wasteful-gap penalty (... |
| 113 | edit | not_better | 0.9446 | 0.9464 | $0.0006 | I'll replace the heuristic scoring with a size-relative waste criterion: prefer the used bin mini... |
| 114 | edit | not_better | 0.9440 | 0.9464 | $0.0006 | I'll replace the ad-hoc scoring with a principled best-fit variant: rank bins by leftover after p... |
| 115 | edit | not_better | 0.9444 | 0.9464 | $0.0006 | I'll replace the ad-hoc heuristics with a two-feature formulation: a strong best-fit primary term... |
| 116 | edit | improved | 0.9480 | 0.9480 | $0.0007 | I'll add a lightweight stateful "reserve the last empty bin" policy: keep the current best-fit + ... |
| 117 | edit | not_better | 0.5318 | 0.9480 | $0.0008 | I'll replace the fixed size threshold and heuristic bonuses with a residual-value criterion: pref... |
| 118 | edit | not_better | 0.9464 | 0.9480 | $0.0008 | I'll switch the primary criterion from pure best-fit to a "best fit that leaves a residual close ... |
| 119 | edit | not_better | 0.9303 | 0.9480 | $0.0008 | I'll add an adaptive scaling factor: track the running mean item size and, when the arriving item... |
| 120 | edit | not_better | 0.7954 | 0.9480 | $0.0006 | Replace the ad-hoc empty-bin threshold with a size-aware "harmony" fit that prefers the used bin ... |
| 121 | edit | not_better | 0.9457 | 0.9480 | $0.0007 | I'll simplify to a pure best-fit-dominant rule with a single stateful consolidation bonus that on... |
| 122 | edit | not_better | 0.7205 | 0.9480 | $0.0008 | I'll keep the best-fit primary and wasteful-gap terms, but replace the ad-hoc "half mean" consoli... |
| 123 | edit | not_better | 0.9442 | 0.9480 | $0.0006 | I'll add a stateful first-fit-decreasing-style "goodness" score based on the well-known bin-packi... |
| 124 | edit | not_better | 0.9460 | 0.9480 | $0.0007 | I'll keep the best-fit primary and wasteful-gap penalty, but replace the current empty-bin promot... |
| 125 | edit | not_better | 0.9442 | 0.9480 | $0.0007 | I'll add a stateful "residual-value" tie-breaker to best-fit: after the primary best-fit ordering... |
| 126 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the fragile wasteful-gap and consolidation heuristics with a cleaner stateful approa... |
| 127 | edit | not_better | 0.9444 | 0.9480 | $0.0006 | I'll replace the previous hand-tuned bonuses with a single well-principled improvement to best-fi... |
| 128 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the ad-hoc bonuses with a cleaner, better-principled rule: primary best-fit on resid... |
| 129 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the ad-hoc bonuses with a single well-grounded rule: primary best-fit on residual, p... |
| 130 | edit | not_better | 0.9453 | 0.9480 | $0.0008 | I'll replace the fixed 50/100 thresholds with ones derived from the running mean item size: promo... |
| 131 | edit | not_better | 0.9444 | 0.9480 | $0.0006 | I will replace the ad-hoc bonuses with a cleaner, better-grounded rule: pure best-fit on residual... |
| 132 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll keep best-fit on residual as the primary criterion, but replace the ad-hoc wasteful-gap and ... |
| 133 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the ad-hoc heuristics with a principled rule grounded in bin-packing theory: primary... |
| 134 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the heuristic stack with a cleaner rule grounded in bin-packing literature: primary ... |
| 135 | edit | not_better | 0.9446 | 0.9480 | $0.0008 | I'll keep the current heuristic stack but retune its key constants using insight from the recent ... |
| 136 | edit | not_better | 0.9457 | 0.9480 | $0.0008 | I'll make the key heuristic terms adaptive to the running mean instead of using fixed thresholds:... |
| 137 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | Replace the ad-hoc heuristic stack with a principled "best-fit plus empty-bin reluctance scaled b... |
| 138 | edit | not_better | 0.9446 | 0.9480 | $0.0007 | I'll revert to the original scoring structure (which scored best at 0.947985) but strengthen the ... |
| 139 | edit | not_better | 0.9408 | 0.9480 | $0.0008 | I'll keep the current best-scoring structure but make the consolidation nudge persistent and stro... |
| 140 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the fixed-threshold heuristic stack with a cleaner two-part rule: primary best-fit o... |
| 141 | edit | not_better | 0.9446 | 0.9480 | $0.0007 | I'll reframe the rule in terms of choosing the residual gap: primary best-fit, but add a strong b... |
| 142 | edit | not_better | 0.9444 | 0.9480 | $0.0008 | I'll add a "perfect-fit priority" plus a mild, size-aware empty-bin penalty: give the largest bon... |
| 143 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the ad-hoc heuristic stack with a principled "best-fit with residual-quality match" ... |
| 144 | edit | not_better | 0.9453 | 0.9480 | $0.0008 | I'll restore the best-known structure (which scored 0.947985) and make one targeted improvement: ... |
| 145 | edit | not_better | 0.9473 | 0.9480 | $0.0008 | I'll restore the best-known structure (score 0.947985) but make the empty-bin promotion threshold... |
| 146 | edit | not_better | 0.9453 | 0.9480 | $0.0008 | I'll restore the best-known structure and replace the fixed "wasteful = rem > item" absolute test... |
| 147 | edit | not_better | 0.9469 | 0.9480 | $0.0007 | I'll replace the heuristic stack with a principled score based on "post-placement goodness" of ea... |
| 148 | edit | not_better | 0.9464 | 0.9480 | $0.0009 | I'll restore the best-known structure (score 0.947985) and add a targeted "close-the-bin" bonus: ... |
| 149 | edit | not_better | 0.9382 | 0.9480 | $0.0010 | I'll keep the best-known structure but replace the fixed consolidation thresholds with a single p... |
| 150 | edit | not_better | 0.9444 | 0.9480 | $0.0007 | I'll replace the current heuristic stack with a cleaner best-fit rule augmented by one targeted t... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,6 +1,10 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best-fit primary, with item-size-scaled empty-bin promotion for large items
+and a stateful consolidation nudge for typical-size items."""
 import numpy as np
+
+# Per-stream running statistics (reset when a fresh stream starts).
+_state = {"n": 0, "sum": 0.0, "last_size": -1}
 
 
 def priority(item, bins):
@@ -10,5 +14,38 @@
     bins: numpy int64 array with the remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    # Update running statistics; detect a new stream by a capacity jump to 100
+    # combined with a small item after a large previous item is unreliable, so
+    # just keep a soft running mean that adapts across the stream.
+    _state["n"] += 1
+    _state["sum"] += item
+    mean_item = _state["sum"] / _state["n"]
+
+    rem = bins - item  # leftover capacity after placing the item
+    # Primary criterion: best fit (prefer smallest leftover).
+    score = -rem.astype(np.float64)
+
+    is_empty = bins == 100
+
+    # Absolute wasteful-gap test: a used bin that would leave a residual larger
+    # than the item itself is a poor fit.
+    wasteful = (rem > item) & (~is_empty)
+    score += wasteful.astype(np.float64) * (item + 1)
+
+    # Item-size-scaled empty-bin promotion: reserve a fresh bin mainly for
+    # large items, while letting smaller items consolidate into used bins.
+    scale = (item - 50.0) / 50.0  # <=0 for items up to 50, up to 1.0 at 100
+    if scale > 0:
+        bonus = scale * (item + 1) * is_empty.astype(np.float64)
+        score += bonus
+
+    # Consolidation nudge: for typical-size items, prefer a used bin whose
+    # residual stays useful (>= half the running mean item size) over opening a
+    # fresh bin, cutting needless bin openings without harming large items.
+    if scale <= 0:
+        half_mean = 0.5 * mean_item
+        useful_used = (rem >= half_mean) & (rem <= item) & (~is_empty)
+        score += 0.5 * (item + 1) * useful_used.astype(np.float64)
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (18 parts, 31 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 20 | `_state['n'] += 1` | -0.9480 | essential: the program fails or turns invalid without it |
| 24 | `rem = bins - item` | -0.9480 | essential: the program fails or turns invalid without it |
| 24 | `term + bins` | -0.9480 | essential: the program fails or turns invalid without it |
| 26 | `score = -rem.astype(np.float64)` | -0.9480 | essential: the program fails or turns invalid without it |
| 28 | `is_empty = bins == 100` | -0.9480 | essential: the program fails or turns invalid without it |
| 32 | `wasteful = (rem > item) & ~is_empty` | -0.9480 | essential: the program fails or turns invalid without it |
| 24 | `term - item` | -0.0078 | matters |
| 33 | `score += wasteful.astype(np.float64) * (item + 1)` | -0.0027 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 21: `_state['sum'] += item`
- line 22: `mean_item = _state['sum'] / _state['n']`
- line 37: `scale = (item - 50.0) / 50.0`
- line 38: `if scale > 0: ...`
- line 39: `bonus = scale * (item + 1) * is_empty.astype(np.float64)`
- line 40: `score += bonus`
- line 45: `if scale <= 0: ...`
- line 46: `half_mean = 0.5 * mean_item`
- line 47: `useful_used = (rem >= half_mean) & (rem <= item) & ~is_empty`
- line 48: `score += 0.5 * (item + 1) * useful_used.astype(np.float64)`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9480 | 0.9671 |
| minimal (5 parts removed) | 0.9462 | 0.9648 |

Minimal program:

```python
"""Best-fit primary, with item-size-scaled empty-bin promotion for large items
and a stateful consolidation nudge for typical-size items."""
import numpy as np
_state = {'n': 0, 'sum': 0.0, 'last_size': -1}

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    _state['n'] += 1
    rem = bins - item
    score = -rem.astype(np.float64)
    is_empty = bins == 100
    wasteful = (rem > item) & ~is_empty
    score += wasteful.astype(np.float64) * (item + 1)
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_b200 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 0
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_b200-s0   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `9f2bbd0772b0ec63759bdd119a5e2d9aa72eaa76`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_b200/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_b200/initial.py` `609927c5ea619a94`
- `problems/bp_sh_b200/problem.md` `190017a698e23cd8`
- `problems/bp_sh_b200/verify.py` `55fde4c12c8b08c5`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
