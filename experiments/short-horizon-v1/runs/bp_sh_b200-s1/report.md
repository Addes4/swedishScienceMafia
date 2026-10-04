# Research loop report: bp_sh_b200

| | |
|---|---|
| problem | `bp_sh_b200` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0900 of a $0.20 hard cap, 150 calls, 309,427 tokens |
| wall time | search 1667 s, baselines 105 s, explain 104 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (151 valid), 3 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9444 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9502 | 0.9678 |  |
| baseline `funsearch_or` | 0.9552 | 0.9711 | `problems/bp_sh_b200/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.8723 | 0.9937 | `problems/bp_sh_b200/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9200 | 0.9950 | `problems/bp_sh_b200/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9496 | 0.9671 | 6 parts removed |

Audit: public 0.9444 → 0.9502 (+0.0059), hidden 0.9634 → 0.9678 (+0.0044); public − hidden gap of the final program -0.0176.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9552). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Replace pure best-fit with a tie-broken rule that ranks bins by best fit but adds a small penalty... |
| 2 | edit | not_better | 0.9444 | 0.9444 | $0.0003 | Use a best-fit rule but add a small bonus for bins that would be left with a large residual (to k... |
| 3 | edit | not_better | 0.9444 | 0.9444 | $0.0003 | Replace pure best-fit with a hybrid that mostly uses best fit but, when the tightest residual wou... |
| 4 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Move beyond static best-fit by maintaining exact-fit and near-exact-fit bookkeeping via module st... |
| 5 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | The static best-fit rule is near-optimal for online packing, but a known improvement is to add a ... |
| 6 | edit | not_better | 0.9426 | 0.9444 | $0.0005 | Replace static best fit (which lets small items finish off many bins and leaves no large-residual... |
| 7 | edit | not_better | 0.9353 | 0.9444 | $0.0004 | Replace pure best fit with a harmonic-style classifier: use best fit for large items, first fit f... |
| 8 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | Use a two-dimensional best-fit rule that breaks ties by preferring the bin that leaves room for a... |
| 9 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Introduce a small "fit-quality" bonus that rewards bins whose residual after placement equals 0 (... |
| 10 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | The best-fit score is currently a linear function of residual, so any monotone bonus is irrelevan... |
| 11 | edit | not_better | 0.9019 | 0.9444 | $0.0005 | Replace the pure best-fit score with a rule that treats bins which exactly fit the item as most p... |
| 12 | edit | not_better | 0.9435 | 0.9444 | $0.0006 | Replace static best fit with a "best fit plus gap-aware consolidation" rule: use best fit normall... |
| 13 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Replace pure best fit with a "best fit decreasing-like" scheme that tracks the running average it... |
| 14 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll switch from pure best fit to a "least-loaded bin that still fits" rule when the item is larg... |
| 15 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll keep best-fit for most items but add a targeted exception: when an item exactly equals a bin... |
| 16 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best fit with a "best fit plus size-class batching" rule: track a small set of ... |
| 17 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a rule adapted to the Weibull item distribution: best-fit is optimal f... |
| 18 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll replace pure best-fit with a "worst-fit for large-residual bins, best-fit otherwise" hybrid:... |
| 19 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Pure best fit tends to shatter nearly-empty large bins with small items; I'll use best fit for it... |
| 20 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Keep best fit as the primary rule, but for small items add a mild penalty proportional to the res... |
| 21 | edit | not_better | 0.9444 | 0.9444 | $0.0009 | I'll change the rule to best-fit but only among bins whose residual is below a threshold (item + ... |
| 22 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement a "best fit with a reserve" rule: score bins by how tightly they fit (like best fi... |
| 23 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch to a "best fit decreasing-like" rule adapted online: score each bin by the residual-m... |
| 24 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Pure best fit ignores the item-size distribution. Since item sizes are Weibull-shaped with mean ~... |
| 25 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll switch the objective from raw residual to an explicit waste-minimizing rule that also keeps ... |
| 26 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace best-fit with a "best-fit + residual-proximity to typical item size" rule: since items ar... |
| 27 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | Implement a scale-invariant "residual modulo mean" style best-fit variant: prefer the bin that mi... |
| 28 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | All previous tweaks to best-fit keep landing at ~0.9444, so I'll try a structurally different onl... |
| 29 | edit | not_better | 0.8328 | 0.9444 | $0.0005 | Replace best-fit with a hybrid that uses best-fit for large items (which benefit from tight packi... |
| 30 | edit | not_better | 0.6162 | 0.9444 | $0.0006 | I'll implement a proper harmonic-style online bin packing rule: map each item to a size class bas... |
| 31 | edit | not_better | 0.9444 | 0.9444 | $0.0006 | I'll try a "best fit with aging/reuse pressure" rule: pure best-fit can strand bins with tiny res... |
| 32 | edit | improved | 0.9469 | 0.9469 | $0.0006 | Best-fit keeps landing at ~0.9444; the real failure mode is stranding bins with tiny unusable res... |
| 33 | edit | not_better | 0.9347 | 0.9469 | $0.0006 | Replace the fixed dead-zone threshold of 25 with the actual observed minimum item size seen so fa... |
| 34 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the fixed dead-zone penalty with a score based on the "waste" a residual implies: pe... |
| 35 | edit | not_better | 0.9323 | 0.9469 | $0.0006 | I will make the dead-zone penalty distinguish residuals that are truly useless (below the smalles... |
| 36 | edit | not_better | 0.9469 | 0.9469 | $0.0005 | I'll exploit a structural weakness of best-fit: instead of always picking the tightest fit, add a... |
| 37 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the hard dead-zone threshold with a smooth, distribution-aware penalty: use the runn... |
| 38 | edit | not_better | 0.4112 | 0.9469 | $0.0009 | I'll replace the fixed dead-zone penalty with a distribution-aware "expected reuse" score: track ... |
| 39 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll add a stronger, size-aware tie-break that prefers the least-loaded bin among equally-tight f... |
| 40 | edit | not_better | 0.9288 | 0.9469 | $0.0006 | Rather than hand-tuning the dead-zone threshold, I'll replace the fixed penalty with a substantia... |
| 41 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll add a lookahead-free "future fit" tie-break based on the item-size distribution: score each ... |
| 42 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll replace the hand-tuned dead-zone penalty with the classic best-fit rule (pure tightest-fit) ... |
| 43 | edit | not_better | 0.9327 | 0.9469 | $0.0005 | I'll replace the fixed 25-threshold dead-zone penalty with a narrower one: only residuals in (0, ... |
| 44 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll shift from a penalty formulation to the classic "best fit" rule stated differently: prefer t... |
| 45 | edit | not_better | 0.9413 | 0.9469 | $0.0005 | I'll keep the tight best-fit core but replace the fixed dead-zone with a distribution-adaptive pe... |
| 46 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll keep the strong best-fit core but change the dead-zone penalty from a uniform shave into a s... |
| 47 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll switch from a fixed dead-zone penalty to the classic "best fit with a small worst-fit safegu... |
| 48 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | The previous attempts show that adding penalties to plain best-fit consistently hurts; I'll test ... |
| 49 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | Replace pure best-fit with a "best-fit with small-item advocacy" rule: after choosing the tightes... |
| 50 | edit | not_better | 0.9451 | 0.9469 | $0.0005 | I'll reformulate the rule as a proper Best-Fit with a *dynamic* dead-zone derived from the curren... |
| 51 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll stop perturbing the ordering with penalties entirely and instead implement pure best-fit wit... |
| 52 | edit | not_better | 0.9448 | 0.9469 | $0.0005 | Most attempts show that any penalty on plain best-fit hurts, so I'll try a genuinely different cl... |
| 53 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll implement the distribution-aware "leave enough room for the next-typical item" rule: rank ma... |
| 54 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll add a deterministic improvement over plain best-fit by using Fill-Forward style lookahead: a... |
| 55 | edit | not_better | 0.9459 | 0.9469 | $0.0007 | I'll make the dead-zone threshold depend on the current item (large items stranded with small res... |
| 56 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the heuristic scoring with the classic "Best Fit Decreasing"-style rule implemented ... |
| 57 | edit | not_better | 0.9397 | 0.9469 | $0.0006 | I'll replace the arbitrary fixed dead-zone penalty with the classic harmonic-style rule: score bi... |
| 58 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the hand-tuned dead-zone penalty with a principled score that mimics the classic "Ha... |
| 59 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll implement a proper online "Subset-Sum / Fill-Forward"-style rule: rank primarily by smallest... |
| 60 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll try a hybrid that keeps pure best-fit as the dominant term but adds a small, statistically-g... |
| 61 | edit | not_better | 0.9406 | 0.9469 | $0.0006 | Increase the dead-zone penalty strength and make it item-size aware: penalize residuals that are ... |
| 62 | edit | not_better | 0.9444 | 0.9469 | $0.0007 | I will replace the dead-zone penalty with a "Fill-Forward aware" hybrid: keep a strong best-fit p... |
| 63 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | Keep best-fit as the dominant term but add a tiny bonus for leaving a residual that is large (a r... |
| 64 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll add an online learned "fit score" using an exponentially-weighted estimate of the recent ite... |
| 65 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll switch from a residual-based best-fit to the classic "Subset Sum" fill heuristic: score each... |
| 66 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | Replace the broad dead-zone penalty with a pure best-fit primary term plus a small bounded bonus ... |
| 67 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | Replace the hard dead-zone penalty with a smooth, item-size-aware "reusability" term: keep pure b... |
| 68 | edit | not_better | 0.9444 | 0.9469 | $0.0007 | I'll replace the current hard dead-zone penalty (which is too coarse) with a data-driven online f... |
| 69 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | Replace the fixed dead-zone penalty with a strong "Fullest-Bin" approximation: use a large multip... |
| 70 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | Replace the single fixed dead-zone with a two-sided, item-aware exponential grid: score bins by a... |
| 71 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | The dead-zone penalty is too crude: instead of a flat penalty for residuals under 25, I'll estima... |
| 72 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll move from a fixed dead-zone to a strictly-best-fit rule but with the tie-break favoring the ... |
| 73 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll abandon ad-hoc residual shaping and instead use a classic "best fit decreasing"-style tie-br... |
| 74 | edit | not_better | 0.3990 | 0.9469 | $0.0005 | I'll switch the primary rule from best-fit to a "largest residual that still fits" (worst-fit) pr... |
| 75 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the crude fixed dead-zone with a smooth, distribution-aware penalty derived from the... |
| 76 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll keep strict best-fit as the primary rule but replace the coarse fixed dead-zone with a "smal... |
| 77 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the arbitrary flat dead-zone with an online-learned item-size distribution (histogra... |
| 78 | edit | not_better | 0.9426 | 0.9469 | $0.0006 | I'll replace the flat dead-zone with a scaled penalty proportional to how much reusable capacity ... |
| 79 | edit | not_better | 0.9347 | 0.9469 | $0.0005 | I'll combine strict best-fit with the dead-zone penalty but calibrate the dead-zone width to the ... |
| 80 | edit | not_better | 0.9413 | 0.9469 | $0.0006 | I'll replace the flat dead-zone penalty with a smooth, distribution-aware score that estimates th... |
| 81 | edit | not_better | 0.9290 | 0.9469 | $0.0006 | Replace the crude fixed dead-zone with an online-tracked minimum item size: strict best-fit remai... |
| 82 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll strengthen the best-fit primary signal by removing the dependence on bin order artifacts: in... |
| 83 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the fixed dead-zone penalty with a smooth, calibrated penalty based on the residual ... |
| 84 | edit | not_better | 0.9424 | 0.9469 | $0.0006 | Most recent attempts confirm that tampering with pure best-fit ordering hurts. The remaining leve... |
| 85 | edit | not_better | 0.9364 | 0.9469 | $0.0005 | I'll exploit bimodality: most items are large (mean ~40, Weibull-shaped), so a residual in a mid ... |
| 86 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll keep pure best-fit as the primary rule but add a tie-aware secondary signal that favors, amo... |
| 87 | edit | not_better | 0.9469 | 0.9469 | $0.0005 | Add a "fill the fullest bin" tiebreaker by scaling the primary best-fit term with a tiny coeffici... |
| 88 | edit | not_better | 0.9444 | 0.9469 | $0.0007 | I'll replace the crude score with a smooth, piecewise-linear convex "loss" function of the residu... |
| 89 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll add an online-tracked histogram of item sizes to estimate, for each candidate residual, the ... |
| 90 | edit | not_better | 0.9364 | 0.9469 | $0.0006 | I'll augment pure best-fit with a learned online estimate of the current minimum item size seen, ... |
| 91 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll keep the exact best-fit primary ordering but change the dead-zone penalty into a *tie-break-... |
| 92 | edit | not_better | 0.9469 | 0.9469 | $0.0005 | I'll try a fundamentally different angle: instead of tweaking the residual penalty, I'll use a ha... |
| 93 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the fixed penalty with a "best-fit with a lookahead-free residual-value" score: scor... |
| 94 | edit | not_better | 0.9206 | 0.9469 | $0.0007 | I will replace the residual-only ranking with a size-class last-fit policy: maintain the empirica... |
| 95 | edit | not_better | 0.9431 | 0.9469 | $0.0006 | I'll use a *quantized* best-fit: round the residual to a coarse grid (multiples of 5) so bins wit... |
| 96 | edit | not_better | 0.9444 | 0.9469 | $0.0010 | The dead-zone penalty score is asymmetric and fixed; I'll replace it with a smooth, well-motivate... |
| 97 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll add a strong bonus when the item exactly fills a bin (residual == 0) so that perfect fits ar... |
| 98 | edit | not_better | 0.9173 | 0.9469 | $0.0007 | I will replace the fixed dead-zone penalty with an online-adaptive penalty based on the largest r... |
| 99 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll keep exact best-fit ordering but add a tie-break that, among bins whose resulting residual i... |
| 100 | edit | not_better | 0.9386 | 0.9469 | $0.0008 | Replace the wide dead-zone penalty (residual < 25, penalty 30) with a narrower and gentler one (r... |
| 101 | edit | not_better | 0.8777 | 0.9469 | $0.0005 | I'll steepen and narrow the dead-zone penalty to a single strong "avoid leaving a tiny sliver" ru... |
| 102 | edit | not_better | 0.9290 | 0.9469 | $0.0005 | I'll replace the raw residual ranking with a "best-fit with calibrated dead zone" that uses a smo... |
| 103 | edit | not_better | 0.9444 | 0.9469 | $0.0009 | I'll switch from a hand-tuned dead-zone penalty to a principled "expected wasted space" score: fo... |
| 104 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I will replace the fixed dead-zone penalty with a small, principled best-fit-plus template that a... |
| 105 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll change the rule to a pure best-fit minus a single, tiny bias toward leaving the largest poss... |
| 106 | edit | not_better | 0.9347 | 0.9469 | $0.0006 | I'll add a lightweight online estimate of the item-size distribution and, rather than penalize re... |
| 107 | edit | not_better | 0.9444 | 0.9469 | $0.0008 | I'll implement a "best-fit decreasing-aware" rule that uses an online running estimate of the ite... |
| 108 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | Replace the ad-hoc dead-zone penalty with a "best-fit with a preference for residuals slightly la... |
| 109 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the fixed-threshold dead-zone penalty with a large penalty applied only to residuals... |
| 110 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll switch to a two-tier best-fit that breaks near-ties among residuals by their "fillability" u... |
| 111 | edit | not_better | 0.9444 | 0.9469 | $0.0007 | I'll replace the ad-hoc dead-zone penalty with a best-fit base plus a modest bonus for leaving re... |
| 112 | edit | not_better | 0.9444 | 0.9469 | $0.0008 | I'll replace the binary dead-zone penalty with a smooth, monotonically-decaying penalty on small ... |
| 113 | edit | not_better | 0.9391 | 0.9469 | $0.0005 | I will lower the dead-zone threshold/penalty so only very small residuals (below ~16) are penaliz... |
| 114 | edit | not_better | 0.9444 | 0.9469 | $0.0005 | I'll combine pure best-fit with a much softer dead-zone penalty tuned to the distribution: penali... |
| 115 | edit | not_better | 0.9444 | 0.9469 | $0.0007 | Replace the fixed dead-zone penalty with an online-updated item-size histogram that estimates the... |
| 116 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll replace the ad-hoc dead-zone rule with the "Sum of Squares" / residual-matching idea: instea... |
| 117 | edit | not_better | 0.9444 | 0.9469 | $0.0008 | I'll switch from pure best-fit to a "smooth worst-fit near capacity" hybrid: keep best-fit as the... |
| 118 | edit | not_better | 0.9444 | 0.9469 | $0.0008 | I'll replace the crude dead-zone bonus with a principled "sum-of-squares" style penalty derived f... |
| 119 | edit | not_better | 0.9444 | 0.9469 | $0.0006 | I'll implement a "best-fit with a friendliness bonus for residuals that exactly match a currently... |
| 120 | edit | improved | 0.9496 | 0.9496 | $0.0006 | I'll add a mild deterministic guard against placing an item into an unused (empty, capacity 100) ... |
| 121 | edit | not_better | 0.9451 | 0.9496 | $0.0006 | I'll add a small "saturation bonus" that prefers used bins with tiny residual capacities (which a... |
| 122 | edit | not_better | 0.9444 | 0.9496 | $0.0005 | I'll shift from a fixed threshold dead-zone to a smooth, distribution-aware penalty: score primar... |
| 123 | edit | not_better | 0.9444 | 0.9496 | $0.0006 | I'll strengthen best-fit by rewarding exact and near-exact fits with a smooth nonlinear tightness... |
| 124 | edit | not_better | 0.9466 | 0.9496 | $0.0006 | I'll add a small deterministic tie-breaker that prefers used bins (fewer than 100 remaining) over... |
| 125 | edit | improved | 0.9502 | 0.9502 | $0.0007 | I'll add a distribution-aware "fill-quality" term on top of best-fit: estimate the online item-si... |
| 126 | edit | not_better | 0.9502 | 0.9502 | $0.0008 | I'll replace the histogram-based "exactly fillable" bonus with a stronger, more targeted one: rew... |
| 127 | edit | not_better | 0.9347 | 0.9502 | $0.0008 | I'll replace the hard-coded dead-zone and fixed bonus weights with a principled "expected future ... |
| 128 | edit | not_better | 0.9502 | 0.9502 | $0.0008 | I'll add a targeted "residual unusability" penalty using the online histogram: penalize placing t... |
| 129 | edit | not_better | 0.9397 | 0.9502 | $0.0008 | I'll replace the dead-zone penalty with an adaptive one based on the online distribution: penaliz... |
| 130 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll replace the fixed text dead-zone/threshold bonuses with a single clean best-fit-worst-fit hy... |
| 131 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll replace the hardcoded rules with a cleaner, well-scaled best-fit rule: rank primarily by sma... |
| 132 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll replace the hand-tuned hybrid with a principled "waste" rule: score each bin by simulating t... |
| 133 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll strip away the fixed dead-zone penalty, empty-bin bonus, and over-weighted histogram term, r... |
| 134 | edit | not_better | 0.9444 | 0.9502 | $0.0006 | The current rule is essentially Best-Fit, which scores ~0.95. I will switch to a Best-Fit with ti... |
| 135 | edit | not_better | 0.9426 | 0.9502 | $0.0008 | I'll replace the ad-hoc dead-zone and bonus terms with a principled "reclaimable residual" score:... |
| 136 | edit | not_better | 0.9444 | 0.9502 | $0.0006 | I'll replace the current ad-hoc hybrid with a cleaner rule: primary tight best-fit, plus a modera... |
| 137 | edit | not_better | 0.9444 | 0.9502 | $0.0006 | I'll replace the ad-hoc heuristic with the classic "Best Fit Decreasing"-style rule expressed onl... |
| 138 | edit | not_better | 0.9353 | 0.9502 | $0.0009 | I'll make the dead-zone penalty threshold adaptive to the smallest item size seen so far (tracked... |
| 139 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I will add the classic "Worst-Fit within threshold" idea as a principled improvement: keep tight ... |
| 140 | edit | not_better | 0.9444 | 0.9502 | $0.0006 | I'll simplify to a clean tight best-fit (minimize residual) plus a small penalty for using a comp... |
| 141 | edit | not_better | 0.9442 | 0.9502 | $0.0007 | Replace the strict best-fit rule with a "best-fit plus special handling for matching residuals": ... |
| 142 | edit | not_better | 0.9444 | 0.9502 | $0.0006 | The current dead-zone penalty (residuals 1..24) and fixed bonuses are hurting near-best-fit packi... |
| 143 | edit | not_better | 0.9351 | 0.9502 | $0.0008 | I'll replace the ad-hoc fixed dead-zone penalty with a principled score that combines tight best-... |
| 144 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | Replace the entire ad-hoc scoring (dead-zone penalty, empty-bin bonus, histogram bonus) with a cl... |
| 145 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll replace the ad-hoc bonuses with a principled "residual matching" rule: primary term is still... |
| 146 | edit | not_better | 0.9489 | 0.9502 | $0.0008 | The recent attempts all regressed, so I'll revert to the original best-performing rule and make o... |
| 147 | edit | not_better | 0.9500 | 0.9502 | $0.0007 | I'll make the residual-match bonus sharper: replace the smooth histogram probability with a stron... |
| 148 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll replace the ad-hoc bonuses with a principled score based on the classic "Best-Fit with a sli... |
| 149 | edit | not_better | 0.9444 | 0.9502 | $0.0007 | I'll replace the whole scoring rule with a cleaner, more classic online heuristic: Best-Fit with ... |
| 150 | edit | not_better | 0.9277 | 0.9502 | $0.0006 | I'll simplify to a pure tight best-fit with only a mild dead-zone penalty and a small empty-bin p... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,56 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best-fit packing enhanced with an online item-size histogram that rewards
+leaving residuals which are likely to be exactly fillable by a future item."""
 import numpy as np
+
+# Module-level state: a coarse histogram of item sizes (1..100).
+_HIST = np.zeros(101, dtype=np.float64)
+_COUNT = 0
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Rank bins; the item goes to the highest (first on ties).
 
     item: integer size of the arriving item, 1..100.
     bins: numpy int64 array with the remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    global _HIST, _COUNT
+
+    residual = bins - item  # remaining capacity after placing the item here
+
+    # ---- Primary: tight best-fit (residual near 0 is best). ----
+    score = -residual.astype(np.float64)
+
+    # ---- Dead-zone penalty: residuals in (0, 25) are likely stranded. ----
+    dead = (residual > 0) & (residual < 25)
+    score -= np.where(dead, 30.0, 0.0)
+
+    # ---- Mild bonus for unused bins. ----
+    empty = bins == 100
+    score += np.where(empty, 5.0, 0.0)
+
+    # ---- Distribution-aware friendliness bonus ----
+    # Estimated probability that a residual equals some common item size, i.e.
+    # that a future item could exactly fill the leftover.  Scale by the mean
+    # item size so it never dominates best-fit.
+    if _COUNT > 20:
+        total = _HIST.sum()
+        if total > 0:
+            # probability mass of each residual as a future item size
+            probs = np.zeros(residual.shape, dtype=np.float64)
+            valid = residual >= 1
+            idx = np.where(valid, residual, 0).astype(np.int64)
+            idx = np.clip(idx, 0, 100)
+            probs = _HIST[idx] / total
+            probs = np.where(valid & (residual <= 100), probs, 0.0)
+            # weight chosen to be a gentle nudge vs. best-fit's unit steps
+            score += probs * 3.0
+
+    # ---- Record this item into the histogram ----
+    if 1 <= item <= 100:
+        _HIST[item] += 1.0
+        _COUNT += 1
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (22 parts, 36 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 20 | `residual = bins - item` | -0.9502 | essential: the program fails or turns invalid without it |
| 20 | `term + bins` | -0.9502 | essential: the program fails or turns invalid without it |
| 23 | `score = -residual.astype(np.float64)` | -0.9502 | essential: the program fails or turns invalid without it |
| 26 | `dead = (residual > 0) & (residual < 25)` | -0.9502 | essential: the program fails or turns invalid without it |
| 30 | `empty = bins == 100` | -0.9502 | essential: the program fails or turns invalid without it |
| 20 | `term - item` | -0.0294 | matters |
| 27 | `score -= np.where(dead, 30.0, 0.0)` | -0.0059 | matters |
| 31 | `score += np.where(empty, 5.0, 0.0)` | -0.0032 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 18: `global _HIST, _COUNT`
- line 37: `if _COUNT > 20: ...`
- line 38: `total = _HIST.sum()`
- line 39: `if total > 0: ...`
- line 41: `probs = np.zeros(residual.shape, dtype=np.float64)`
- line 42: `valid = residual >= 1`
- line 43: `idx = np.where(valid, residual, 0).astype(np.int64)`
- line 44: `idx = np.clip(idx, 0, 100)`
- line 45: `probs = _HIST[idx] / total`
- line 46: `probs = np.where(valid & (residual <= 100), probs, 0.0)`
- line 48: `score += probs * 3.0`
- line 51: `if 1 <= item <= 100: ...`
- line 52: `_HIST[item] += 1.0`
- line 53: `_COUNT += 1`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9502 | 0.9678 |
| minimal (6 parts removed) | 0.9496 | 0.9671 |

Minimal program:

```python
"""Best-fit packing enhanced with an online item-size histogram that rewards
leaving residuals which are likely to be exactly fillable by a future item."""
import numpy as np
_HIST = np.zeros(101, dtype=np.float64)
_COUNT = 0

def priority(item, bins):
    """Rank bins; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    residual = bins - item
    score = -residual.astype(np.float64)
    dead = (residual > 0) & (residual < 25)
    score -= np.where(dead, 30.0, 0.0)
    empty = bins == 100
    score += np.where(empty, 5.0, 0.0)
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_b200 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 1
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_b200-s1   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_b200/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_b200/initial.py` `609927c5ea619a94`
- `problems/bp_sh_b200/problem.md` `190017a698e23cd8`
- `problems/bp_sh_b200/verify.py` `55fde4c12c8b08c5`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
