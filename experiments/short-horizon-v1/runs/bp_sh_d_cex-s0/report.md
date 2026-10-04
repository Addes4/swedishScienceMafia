# Research loop report: bp_sh_d_cex

| | |
|---|---|
| problem | `bp_sh_d_cex` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0938 of a $0.20 hard cap, 150 calls, 313,398 tokens |
| wall time | search 1944 s, baselines 180 s, explain 115 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (148 valid), 1 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9728 | 0.9634 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_d_cex/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_d_cex/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_d_cex/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9727 | 0.9634 | 7 parts removed |

Audit: public 0.9727 → 0.9728 (+0.0002), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program 0.0094.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0003 | Replace pure best-fit with a size-aware best-fit variant: score bins by leftover capacity after p... |
| 2 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with a dual-threshold rule: use best-fit normally, but when the arriving it... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Use a "best fit decreasing-like" tie-break: primary score is tightest fit (smallest leftover), bu... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Use a size-aware score that balances best-fit tightness with a learned estimate of item-size dist... |
| 5 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "worst-fit toward the complement" using the known mean item size (~4... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Switch from pure best-fit to a score that strongly prefers exact fills (leftover 0) and otherwise... |
| 7 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Add state to track the running item-size distribution and, for larger items, prefer bins whose le... |
| 8 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Introduce a stateful "sum-of-small-items" trick: for items that are small relative to the typical... |
| 9 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Best-fit alone ignores that a bin with tiny leftover after placement is often useless, while leav... |
| 10 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure best-fit rule with a harmonic/mixed rule: prefer to place an item into a bi... |
| 11 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a dual-criterion score inspired by the "sum of squares" / least-loaded... |
| 12 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the raw best-fit with a "fill-the-gap" harmonic rule: track a smoothed estimate of t... |
| 13 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Use a stateful "reserve" best-fit variant: place the item in the feasible bin with the smallest r... |
| 14 | edit | not_better | 0.9609 | 0.9727 | $0.0005 | Replace the best-fit-with-tiebreak score with a two-component rule inspired by the "Best Fit Decr... |
| 15 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from the raw best-fit tie-break to a strict best-fit on the *resulting free space*, b... |
| 16 | edit | not_better | 0.9550 | 0.9727 | $0.0006 | I will replace pure static best-fit with an online "subharmonic gap" rule inspired by harmonic bi... |
| 17 | edit | not_better | 0.3333 | 0.9727 | $0.0008 | Pure best-fit is already near-optimal; the main remaining gain is to break ties among equal resul... |
| 18 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll keep strict best-fit as the primary criterion but replace the complicated/buggy tie-breaking... |
| 19 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will replace pure best-fit with a two-level rule that first prefers feasible bins whose remaini... |
| 20 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll use a stateful "best fit with lookahead-free sub-bin accounting": keep strict best-fit as th... |
| 21 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a "smart best fit" that ranks bins by post-placement leftover, but adds a small pe... |
| 22 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll add a stateful twist to strict best-fit: track a running histogram of recent item sizes and,... |
| 23 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will try a "best fit decreasing-like" rule that adds a tiny stateful nudge: keep strict best-fi... |
| 24 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | I'll implement a stateful rule that switches to a "worst-fit-like" secondary preference: keep str... |
| 25 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit is unchanged on the two long streams but the score is capped by its inability to improve... |
| 26 | edit | not_better | 0.5985 | 0.9727 | $0.0005 | I'll switch the primary rule from best-fit to a "worst-fit with a cap" variant: prefer placing th... |
| 27 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a hybrid rule that keeps best-fit for large items (where tight pa... |
| 28 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "best-fit plus a small random tie-break entropy that favors bal... |
| 29 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | I'll keep strict best-fit (maximize item - bins remaining, i.e., minimize leftover) as the primar... |
| 30 | edit | invalid | 0.0000 | 0.9727 | $0.0005 | Replace best-fit with a "best-fit with a reject threshold" hybrid: rank bins by a stateful score ... |
| 31 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace pure best-fit with a criterion that minimizes the increase in sum of squared leftover cap... |
| 32 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll keep strict best-fit as the primary key but add a stateful histogram of recent item sizes an... |
| 33 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Recent attempts all failed because they tweak best-fit by tiny amounts that don't change the long... |
| 34 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "shelf-aware best fit": for each bin, prefer a fit that leaves ... |
| 35 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit wastes space; I'll switch to a "First-Fit with best-fit tie-break on the fondest bin" th... |
| 36 | edit | not_better | 0.9727 | 0.9727 | $0.0010 | Best-fit on Weibull item sizes suffers fragmentation from tiny leftovers; I'll implement a proper... |
| 37 | edit | not_better | 0.8679 | 0.9727 | $0.0007 | I'll stop micro-tweaking best-fit and instead implement a proper interval-based (Harmonic/Modifie... |
| 38 | edit | not_better | 0.7563 | 0.9727 | $0.0006 | I'll implement a proper two-parameter online heuristic: a Harmonic-style size-classification wher... |
| 39 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Keep strict best-fit as the primary criterion, but when the tightest fit leaves a small leftover,... |
| 40 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll augment best-fit with a "goodness of leftover" adjustment: among bins whose resulting leftov... |
| 41 | edit | not_better | 0.5985 | 0.9727 | $0.0005 | All prior attempts failed because any rule that still places the item into the tightest-fitting b... |
| 42 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace the pure best-fit with a "best-fit among bins whose leftover is usable, otherwise best-fi... |
| 43 | edit | not_better | 0.9666 | 0.9727 | $0.0005 | Prior attempts all reduced to best-fit because ties/near-ties occur rarely on long streams. I'll ... |
| 44 | edit | not_better | 0.9722 | 0.9727 | $0.0006 | Prior attempts never beat plain best-fit because tie-breaking windows almost never trigger. I'll ... |
| 45 | edit | not_better | 0.9445 | 0.9727 | $0.0005 | Best-fit leaves unusable small slivers; I'll switch to a score that prefers the smallest remainin... |
| 46 | edit | not_better | 0.9718 | 0.9727 | $0.0007 | Replace pure best-fit with a "best-fit-with-lookahead-via-statistics" rule: keep choosing the tig... |
| 47 | edit | not_better | 0.9682 | 0.9727 | $0.0007 | Best-fit is near-optimal but leaves small unusable slivers; I'll switch to a genuinely different ... |
| 48 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the pure best-fit with a bounded "best-fit + perfect-fill priority" rule: keep best-fit a... |
| 49 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | The "bins" array only contains bins the item fits in, so my rule sees a truncated view; a key kno... |
| 50 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with the classic "Harmonic"-style rule: precompute fixed capacity classes (... |
| 51 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "dual-threshold residual matching" rule: keep best-fit as the primar... |
| 52 | edit | not_better | 0.9713 | 0.9727 | $0.0006 | Introduce a Bounded-Best-Fit rule: keep best-fit as the primary criterion but implement the class... |
| 53 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | Introduce a size-class (fractional-harmonic) rule that reserves large bins for large items: compu... |
| 54 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best-fit is already near-optimal, but its weakness is leaving many tiny unusable slivers. I'll ad... |
| 55 | edit | improved | 0.9728 | 0.9728 | $0.0005 | Introduce a "best-fit with exact-fill and sliver-avoidance tie-break": rank primarily by tightest... |
| 56 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll broaden the sliver definition by tracking a running estimate of the expected item-size distr... |
| 57 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll replace the fixed min-item sliver threshold with a dynamically estimated 5th-percentile of o... |
| 58 | edit | not_better | 0.5985 | 0.9728 | $0.0005 | I'll switch the primary criterion from a pure best-fit (tightest residual) to a "least-loaded bin... |
| 59 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll implement a proper "sum-of-squares"/harmonic-aware best-fit: keep best-fit as the dominant c... |
| 60 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll combine best-fit with a small "good-fit" tolerance window (like Bounded-Best-Fit) but let th... |
| 61 | edit | not_better | 0.9721 | 0.9728 | $0.0007 | I'll replace the fixed min-item sliver threshold with a dynamically tracked count of bins in each... |
| 62 | edit | invalid | 0.0000 | 0.9728 | $0.0009 | I'll try a "best-fit with tie-break that prefers residuals which are sums of common item sizes" b... |
| 63 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll add a light "residual-class awareness" term: track a running histogram of item sizes and, am... |
| 64 | edit | not_better | 0.9727 | 0.9728 | $0.0007 |  |
| 65 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I will replace the fixed min-item sliver penalty with an adaptive "avoid creating hard-to-fill re... |
| 66 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the integer-residual "sliver" penalty with a smarter scoring that strongly prefers c... |
| 67 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll switch from best-fit to a "best-fit with worst-fit fallback for low-fill bins": the known st... |
| 68 | edit | not_better | 0.9728 | 0.9728 | $0.0007 | I'll switch the core rule to a "largest-residual-that-still-fits-with-a-sane-slack" strategy is r... |
| 69 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll add a "pair-completion" bias: track a running histogram of item sizes and, among near-tied b... |
| 70 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll replace the fragile min-item histogram tweak with a proven "almost-worst-fit for large items... |
| 71 | edit | not_better | 0.9727 | 0.9728 | $0.0009 | I'll replace the hand-tuned best-fit variant with a principled dynamic program over an item-size ... |
| 72 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the fixed sliver penalty with a size-class best-fit that treats the residual as a "w... |
| 73 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I'll make the sliver penalty graded and adaptive: instead of a binary "residual < min_item" penal... |
| 74 | edit | not_better | 0.9727 | 0.9728 | $0.0009 | I'll add a "leave-room-for-pairs" bias based on a running item-size histogram: keep best-fit domi... |
| 75 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the hand-tuned residual tweaks with a principled two-level rule: compute best-fit as... |
| 76 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll weaken the sliver penalty to only apply when the residual is strictly less than the item jus... |
| 77 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll replace the best-fit primary with a "best-fit with full-bin exploitation" rule: since unused... |
| 78 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the ad-hoc sliver penalty with the classic well-performing variant of best-fit that ... |
| 79 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the purely best-fit rule with a score that is dominated by best-fit but uses an expo... |
| 80 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | Replace the sliver-penalty tie-break with a rule that is best-fit dominant but adds a bonus propo... |
| 81 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the binary sliver penalty with a smooth penalty that uses the actual item-size distributi... |
| 82 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Keep best-fit dominant but replace the sliver penalty with a smooth "fillability" score: maintain... |
| 83 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll test a fundamentally different and stronger rule known to beat best-fit: score bins so that ... |
| 84 | edit | not_better | 0.9727 | 0.9728 | $0.0013 | Replace the rule with a smoothing that penalizes leftover residuals that are too small to be fill... |
| 85 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the ad-hoc sliver logic with the well-known "worst-fit decreasing-like" alternative that ... |
| 86 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I'll replace the ad-hoc best-fit/sliver rule with a smoothed "expected future waste" score based ... |
| 87 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | The previous attempts all added tiny tie-break perturbations to best-fit that were too small to m... |
| 88 | edit | gate_rejected | 0.9822 | 0.9728 | $0.0006 | I'll switch from best-fit to a "best-fit with lookahead-aware threshold" that implements the clas... |
| 89 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the ad-hoc sliver rule with the classic 1D online strategy of best-fit combined with... |
| 90 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Add a mild "second-best-fit" style rebalancing: when the strict best-fit residual is very small b... |
| 91 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the broken sliver penalty (which uses the running minimum — always 1, making it never tri... |
| 92 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the ad-hoc sliver/mean heuristics with the classic online rule that is provably strong fo... |
| 93 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Add a *harmonically-scaled* best-fit variant that scores bins by the residual after placement div... |
| 94 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I'll implement a smooth "least harmful residual" rule: prefer tightest fit but apply a penalty pr... |
| 95 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Adopt pure best-fit (smallest residual after placing) with no heuristics: the history shows every... |
| 96 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace pure best-fit with a "least-load" (worst-fit-like) tie-break only among the bins tha... |
| 97 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll implement a "residual compatibility" rule: score each bin by how well its post-placement res... |
| 98 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll use a two-parameter "harmonics" rule known to be strong for Weibull-like sizes: prefer the t... |
| 99 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll switch to a distribution-aware scoring that uses the known item distribution shape: instead ... |
| 100 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | Add a stateful residual-utility cache: track, across the stream, the empirical frequency of item ... |
| 101 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll implement a "critical item size" penalty based on the actual minimum item seen, but instead ... |
| 102 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the heuristic scoring with a classic, well-proven online rule for Weibull-ish sizes:... |
| 103 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Make the rule pure best-fit without the persistent min_item-driven sliver penalty (which shrinks ... |
| 104 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the pure best-fit rule with a "best-fit with bounded-flooding exact-fit preference":... |
| 105 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll switch to a stateless pure best-fit rule with only a strong exact-fill preference, since all... |
| 106 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Add a stateful item-size histogram and score each bin by the estimated probability that its post-... |
| 107 | edit | not_better | 0.9727 | 0.9728 | $0.0008 | I'll replace the pure scoring with a "intelligent Best-Fit with Hall-condition awareness": instea... |
| 108 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll implement a "power-of-two-choices"-style rule that, among bins with the smallest residual af... |
| 109 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Switch from local best-fit to a genuinely different online rule: a "capacity-class / harmonic" ap... |
| 110 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Replace the score with a "best-fit plus predicted refill value" rule: keep tightest-fit primary, ... |
| 111 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | Every secondary tweak so far has only tied or hurt, so I will make the rule exact best-fit (small... |
| 112 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the local best-fit rule with a size-class (harmonic-style) assignment: it keeps a st... |
| 113 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll switch to a genuinely different rule: "Objective Best-Fit" scored by minimizing wasted space... |
| 114 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll add a stateful histogram of past item sizes and, instead of the coarse sliver penalty, score... |
| 115 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the sliver penalty (based only on the running minimum item) with a stateful empirica... |
| 116 | edit | not_better | 0.9705 | 0.9728 | $0.0006 | I'll replace the simple best-fit-plus-sliver-penalty with a "worst-fit among fitting bins that av... |
| 117 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Introduce a stateful exponential-decay estimate of the item-size distribution and, while keeping ... |
| 118 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Replace the pure-geometric scoring with a "minimum-waste best-fit" that penalizes the expected fu... |
| 119 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the best-fit-plus-flat-penalty scheme with a "best-fit, but rank ties and near-ties ... |
| 120 | edit | not_better | 0.9682 | 0.9728 | $0.0006 | I'll replace the residual-only score with a "fullness-aware best fit": keep best-fit dominant (sm... |
| 121 | edit | invalid | 0.0000 | 0.9728 | $0.0006 | I'll use a two-part score that keeps best-fit dominant but resolves near-ties by preferring the r... |
| 122 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll keep best-fit as the dominant term but refine the sliver penalty: instead of using a single ... |
| 123 | edit | gate_rejected | 0.9730 | 0.9728 | $0.0006 | I'll switch from pure best-fit to a "best-fit with matching residual preference": keep best-fit d... |
| 124 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the flat sliver penalty with a probabilistic expected-waste estimate: keep best-fit ... |
| 125 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll switch the primary term from best-fit to a "best-fit with a soft threshold" that prefers the... |
| 126 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the simple sliver penalty with a score that targets the residual most likely to be e... |
| 127 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the flat sliver penalty with a smarter residual-value score: keep best-fit dominant,... |
| 128 | edit | not_better | 0.9727 | 0.9728 | $0.0005 | I'll switch to a "sum-of-squares residual" (SSF) style score: instead of best-fit, prefer the bin... |
| 129 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace best-fit with a score that prefers the bin whose residual after placement is closest... |
| 130 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll make the tie-break prefer placing the item into the bin whose residual, after placement, mat... |
| 131 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the fixed running-minimum sliver threshold with a stateful expected-waste estimate: ... |
| 132 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the flat sliver penalty with a continuous, distribution-aware expected-waste term: k... |
| 133 | edit | not_better | 0.9718 | 0.9728 | $0.0006 | I'll replace the simplistic best-fit+sliver rule with a classic "modified best-fit" that adds a h... |
| 134 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | Replace the fixed sliver threshold and ad-hoc bonus with a principled "harmony" score: for each b... |
| 135 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll change the sliver threshold from the running minimum item to a fixed low value (like 1) so t... |
| 136 | edit | not_better | 0.9728 | 0.9728 | $0.0006 | I'll add a "largest-first among usable residuals" tie-break: keep best-fit dominant, but when two... |
| 137 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | Keep best-fit dominant, but replace the running-minimum sliver threshold with a running-maximum-b... |
| 138 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the best-fit-plus-penalty rule with a residual-value scoring based on the empirical ... |
| 139 | edit | not_better | 0.9682 | 0.9728 | $0.0009 | Make the sliver penalty dominate best-fit instead of merely breaking ties: strongly penalize resi... |
| 140 | edit | not_better | 0.9727 | 0.9728 | $0.0006 | I'll replace the ad-hoc sliver term with a two-stage rule: keep best-fit dominant, but among bins... |
| 141 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace best-fit with a "dot-product" style score based on how well the post-placement resid... |
| 142 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll switch from pure best-fit (which is myopic and tends to shred capacity into unusable slivers... |
| 143 | edit | not_better | 0.9537 | 0.9728 | $0.0006 | I'll replace the myopic best-fit with a scale-invariant "expected future fill" score: for each po... |
| 144 | edit | gate_rejected | 0.9741 | 0.9728 | $0.0006 | Replace the min-item sliver penalty (which only knows the smallest item seen so far) with an adap... |
| 145 | edit | not_better | 0.9725 | 0.9728 | $0.0006 | Instance 3 (short streams) is very sensitive, and the current min-item sliver penalty also stops ... |
| 146 | edit | not_better | 0.9682 | 0.9728 | $0.0006 | I'll keep best-fit dominant but replace the tiny fixed sliver penalty with a scaled, distribution... |
| 147 | edit | not_better | 0.9715 | 0.9728 | $0.0006 | I'll keep best-fit dominant but add a scaled penalty term for residuals that are too small to be ... |
| 148 | edit | not_better | 0.9727 | 0.9728 | $0.0007 | I'll replace the hard min-item sliver penalty with a smooth, continuous "waste" penalty that favo... |
| 149 | edit | not_better | 0.9727 | 0.9728 | $0.0009 | Keep best-fit strictly dominant by making all secondary terms have magnitude < 1 (residuals are i... |
| 150 | edit | not_better | 0.5985 | 0.9728 | $0.0005 | I'll switch the bin-choice from best-fit to a "least-loaded-bin that still fits" (worst-fit / rou... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,6 +1,8 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best-fit with residual-aware tie-break to avoid tiny unusable slivers."""
 import numpy as np
+
+_state = {"min_item": 100}
 
 
 def priority(item, bins):
@@ -10,5 +12,22 @@
     bins: numpy int64 array with the remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    global _state
+    if item < _state["min_item"]:
+        _state["min_item"] = item
+
+    residual = bins - item  # remaining capacity after placing the item
+
+    # Best-fit primary: tighter fit (smaller residual) is better.
+    primary = -residual.astype(np.float64)
+
+    # Sliver penalty: residuals in [1, min_item-1) can never be reused.
+    # Also give a slight bonus to exact fills (residual 0).
+    sliver_thresh = _state["min_item"]
+    sliver = (residual > 0) & (residual < sliver_thresh)
+    penalty = np.where(sliver, 1.0, 0.0)
+    bonus = np.where(residual == 0, 0.5, 0.0)
+
+    # Scale primary so the small secondary terms only matter near ties.
+    return primary - penalty + bonus
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (14 parts, 27 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 19 | `residual = bins - item` | -0.9728 | essential: the program fails or turns invalid without it |
| 19 | `term + bins` | -0.9728 | essential: the program fails or turns invalid without it |
| 22 | `primary = -residual.astype(np.float64)` | -0.9728 | essential: the program fails or turns invalid without it |
| 26 | `sliver_thresh = _state['min_item']` | -0.9728 | essential: the program fails or turns invalid without it |
| 27 | `sliver = (residual > 0) & (residual < sliver_thresh)` | -0.9728 | essential: the program fails or turns invalid without it |
| 32 | `term + primary` | -0.0043 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 15: `global _state`
- line 16: `if item < _state['min_item']: ...`
- line 17: `_state['min_item'] = item`
- line 19: `term - item`
- line 28: `penalty = np.where(sliver, 1.0, 0.0)`
- line 29: `bonus = np.where(residual == 0, 0.5, 0.0)`
- line 32: `term - penalty`
- line 32: `term + bonus`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9728 | 0.9634 |
| minimal (7 parts removed) | 0.9727 | 0.9634 |

Minimal program:

```python
"""Best-fit with residual-aware tie-break to avoid tiny unusable slivers."""
import numpy as np
_state = {'min_item': 100}

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    residual = bins
    primary = -residual.astype(np.float64)
    sliver_thresh = _state['min_item']
    sliver = (residual > 0) & (residual < sliver_thresh)
    return primary
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_d_cex --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 0
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_d_cex-s0   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `9f2bbd0772b0ec63759bdd119a5e2d9aa72eaa76`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_d_cex/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_d_cex/initial.py` `609927c5ea619a94`
- `problems/bp_sh_d_cex/problem.md` `190017a698e23cd8`
- `problems/bp_sh_d_cex/suite.json` `c10c239f751ffc5f`
- `problems/bp_sh_d_cex/verify.py` `12d8663a195dbe46`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
