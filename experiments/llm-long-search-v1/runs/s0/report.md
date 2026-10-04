# Research loop report: bin_packing_online

| | |
|---|---|
| problem | `bin_packing_online` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.1939 of a $0.75 hard cap, 300 calls, 656,858 tokens |
| wall time | search 2066 s, baselines 42 s, explain 58 s |
| stopped | max_iters (stopped_early) |
| evaluations | 301 (295 valid), 4 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9925 | 0.9933 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online/baselines/funsearch_weibull.py` |
| minimal program (ablation) | 0.9915 | 0.9928 | 8 parts removed |

Audit: public 0.9616 → 0.9925 (+0.0308), hidden 0.9604 → 0.9933 (+0.0328); public − hidden gap of the final program -0.0008.

Against the baselines: the final program's public score is below the best baseline (`funsearch_weibull`, 0.9925). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0010 | Replace pure best-fit with a scoring that still favors the tightest fit but adds a small bonus fo... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace the myopic best-fit rule with a hybrid that adds a tunable bonus to bins whose post-place... |
| 3 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Add a small tie-breaking bonus that prefers placing the item into an already-nonempty bin whose r... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a "tie-break toward filling emptier bins less" approach: keep best-fit... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace the myopic best-fit score with a "sum-of-squares" residual cost that favors bins that wil... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use a "worst-fit among fit bins, but only if remainder is small" hybrid is unlikely to help; inst... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | Replace the myopic best-fit with a "least-fragmentation" rule that anticipates the item-size dist... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace the myopic best-fit rule with a "reserve the last slot" policy based on a first-fit-decre... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a rule that favors the smallest post-placement remainder but adds an a... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace the myopic best-fit with a score that uses an exponential penalty on the post-placem... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a classic harmonic-style bucketing rule: bins are ranked primarily by ... |
| 12 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "worst-fit with reservation" rule: among bins that fit, prefer the b... |
| 13 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Implement a learned-style hybrid: keep best-fit as the default, but add a small deterministic tie... |
| 14 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Implement the classic "best fit decreasing with lookahead-free harmonic bucketing" as an adaptive... |
| 15 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | Replace the myopic best-fit with a tuned "best fit with a small tie-break" that exactly matches b... |
| 16 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Statistical BMTP-style approach: replace the myopic best-fit scalar ranking with a score derived ... |
| 17 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace the myopic best-fit with a lookahead that uses past-item statistics: maintain an online h... |
| 18 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Implement a two-dimensional best-fit rule that is a genuinely different packing policy: prefer bi... |
| 19 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Introduce a randomized tie-break using a hash of the bin index among bins with equal best-fit res... |
| 20 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a scaled-metric variant that first searches for an exact fit and other... |
| 21 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Introduce a score that ranks bins by best-fit primary term, but with a small perturbation based o... |
| 22 | edit | not_better | 0.9614 | 0.9616 | $0.0006 | Replace the myopic best-fit with a two-bin lookahead: store recent item sizes and score each cand... |
| 23 | edit | not_better | 0.3961 | 0.9616 | $0.0004 | I'll switch to a "least-loaded bin" (worst-fit) rule instead of best-fit, but restricted to bins ... |
| 24 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add a harmonic/adaptive blend: keep best-fit as the primary rule, but multiply the score by a sma... |
| 25 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Use a two-parameter "suboptimal-fit" rule: score bins primarily by best-fit residual, but add a s... |
| 26 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a two-choice power-of-two-choices rule that is both fast and rob... |
| 27 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a blend of best-fit and a "minimum post-placement leftover" rule: add ... |
| 28 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a classic "harmonic/adaptive" approach that is known to beat bes... |
| 29 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Switch the primary rule from plain best-fit (tightest residual) to a "best-fit-decreasing-aware" ... |
| 30 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I will replace the myopic best-fit tie-breaking with an online-learned "item-size histogram" that... |
| 31 | edit | invalid | 0.0000 | 0.9616 | $0.0007 | Replace the myopic best-fit rule with an "adaptive fit" that uses a running estimate of the item-... |
| 32 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Switch to "best fit with a capacity-class floor": keep best-fit as the primary key, but break tie... |
| 33 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace myopic best-fit with a "most-full bin that still leaves room for the expected next items"... |
| 34 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the purely myopic rule with "best fit + least-load balancing": keep best-fit (smalle... |
| 35 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace the purely myopic best-fit with a "best-fit plus slice/remainder-class" rule that ... |
| 36 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Switch from myopic best-fit to a "best-fit with remainder-value" rule: score bins primarily by ti... |
| 37 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will add a simple learned-parameter tweak: use best-fit but with an asymmetric penalty that, wh... |
| 38 | edit | not_better | 0.9616 | 0.9616 | $0.0011 | (no description) |
| 39 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll implement a distribution-aware "best fit" variant that, instead of preferring the tightest f... |
| 40 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a harmonic/score-based ranking known to beat Best Fit on average... |
| 41 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | Replace myopic best-fit with a blended score that combines tightest fit (smallest residual gap) w... |
| 42 | edit | invalid | 0.0000 | 0.9616 | $0.0007 | Replace myopic Best Fit with two-phase ranking inspired by "best fit decreasing" emulation: keep ... |
| 43 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I will switch to a simple, fast "best fit" variant that adds a tiny tie-breaking bonus based on b... |
| 44 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace the myopic best-fit rule with a "best-fit with a small full-bin consolidation bias": scor... |
| 45 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure Best Fit with a bounded "Best Fit with score-based bin ranking" that also considers ... |
| 46 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace plain Best Fit with a "Best Fit with sub-1 remainder refinement": primary key is the resi... |
| 47 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic Best-Fit addition term with a score inspired by the "Sum of Squares" / matchin... |
| 48 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a two-level score: primary is the tightest fit (smallest residual), bu... |
| 49 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace the pure best-fit with a hybrid: keep best-fit as the main rule but, when the item would ... |
| 50 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | The repeated failures of small additive biases suggest the search needs a genuinely stronger onli... |
| 51 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace the myopic best-fit rule with a "Best Fit with a learned-scale wasted-space penalt... |
| 52 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace myopic best-fit with a score that combines tightest fit with a bonus for placing the item... |
| 53 | edit | not_better | 0.9609 | 0.9616 | $0.0006 | I'll try a fundamentally different and much stronger online rule from the literature: "Averaging"... |
| 54 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Introduce a "sum-of-squares wasted-space" score with an added bias toward keeping post-placement ... |
| 55 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Best-fit ignores smaller items that could later fill gaps. I will add a lightweight online "reser... |
| 56 | edit | invalid | 0.0000 | 0.9616 | $0.0006 | I'll replace best-fit with a "harmonic fit" score: score each bin by the probability that the res... |
| 57 | edit | invalid | 0.0000 | 0.9616 | $0.0006 | I'll switch from a purely myopic rule to a historical-statistics rule: score each bin by the prob... |
| 58 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "harmonic-plus-mean-fit" rule from online bin packing literature: sc... |
| 59 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "post-placement remainder maximization for robustness" rule: in... |
| 60 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | Switch from "best fit" to a bounded "modified best fit with a worst-fit fallback": use best-fit (... |
| 61 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | The pure best-fit rule leaves many bins with small remainders that can never be filled; I'll add ... |
| 62 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll switch the ranking to a fractional/"harmonic-like" measure that prefers bins by a normalized... |
| 63 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace the myopic best-fit rule with a "best fit decreasing-aware" rule that, among bins gi... |
| 64 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Switch from myopic best-fit to a randomized "best-fit with tie-breaking toward exact-fit and away... |
| 65 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "best fit + validity guard": score bins primarily by tightest f... |
| 66 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from myopic best-fit to a two-candidate rule inspired by "best fit with a large-item ... |
| 67 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace myopic best-fit with a "reserve-largest-gaps" rule: score bins by tightest fit, but multi... |
| 68 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace the myopic best-fit rule with "best fit decreasing"-style behavior adapted online: score ... |
| 69 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the myopic best-fit with a scaled "best fit" that ranks bins by the amount of capaci... |
| 70 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace best-fit with a "sum-of-squares / congruent-fit" rule that prefers the bin whose rem... |
| 71 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a lookahead-flavored "best fit but treat a resulting remainder b... |
| 72 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | (no description) |
| 73 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace myopic best-fit with a "best fit plus occasional new-bin seeding for small items": k... |
| 74 | edit | not_better | 0.9465 | 0.9616 | $0.0007 | Replace myopic best-fit with a "rank by post-placement remainder matched to the empirical item-si... |
| 75 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a hybrid: keep best-fit as the default, but when the item is larg... |
| 76 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a variant that reserves one "open" bin for large items: keep bes... |
| 77 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace best-fit with a scoring rule that combines best-fit tightness with a bonus favoring bins ... |
| 78 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a score that combines best-fit tightness with a dynamic penalty based on whether t... |
| 79 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | The pure best-fit rule ignores the huge mass of empty bins, causing premature opening of new bins... |
| 80 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add a small amount of state: track how many items have been packed and a running sum, then u... |
| 81 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the pure best-fit rule with a "best fit with capacity-class smoothing": score bins b... |
| 82 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace myopic best-fit with a rule that scores bins by a "waste potential" estimate: prefer the ... |
| 83 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Best-fit is a strong greedy but provably leaves many near-full bins with small unusable gaps. I'l... |
| 84 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a "worst-fit among non-empty bins, but strongly prefer closing p... |
| 85 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace myopic best-fit with a "best-fit with sum-aware tie-breaking": among bins where the ... |
| 86 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add light state: cap how many bins can reach nonzero score by preferring best-fit while subtracti... |
| 87 | edit | not_better | 0.9616 | 0.9616 | $0.0013 | Replace the pure best-fit with a sum-aware "fillable residual" rule: among bins where the item fi... |
| 88 | edit | not_better | 0.8853 | 0.9616 | $0.0009 | Replace the reactive best-fit rule with an online-learning hedge: maintain a static scoring funct... |
| 89 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Add a simple online "open-bin count" signal: score each bin by best-fit tightness but add a small... |
| 90 | edit | not_better | 0.8269 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit decreasing-aware residual matching" rule: after computing ... |
| 91 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | (no description) |
| 92 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add an online "sum-aware" rule: keep a running estimate of the distribution's item-size CDF from ... |
| 93 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add an online-learned threshold: bin scores default to tightest-fit, but bins whose post-placemen... |
| 94 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Try a least-loaded ("worst fit") tie-break blended with best-fit: primary score is tightness (bes... |
| 95 | edit | not_better | 0.9609 | 0.9616 | $0.0005 | I'll replace the deterministic best-fit with a randomized-greedy scheme that occasionally chooses... |
| 96 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | The current best-fit is essentially optimal for this distribution, so I'll add a "learned" adapti... |
| 97 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Best-fit leaves many bins with tiny unusable remainders. I'll add a "residual feasibility" score:... |
| 98 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace pure best-fit with a "residual smoothing" rule: among bins that fit, prefer tightest... |
| 99 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace best-fit with a hybrid that blends best-fit tightness with a mild "open-bin" preference: ... |
| 100 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a harmony-style "residual matching" rule: score each fitting bin prima... |
| 101 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll switch from pure best-fit to a "best-fit decreasing aware" hybrid that uses the running hist... |
| 102 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a score that uses best-fit as primary but adds a tiny learned-len... |
| 103 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Switch the ordering to worst-fit on the least-loaded bins: since items are large (mean ~40, capac... |
| 104 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a hybrid that combines best-fit tightness with a low-pass "future... |
| 105 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Add an exact-fit bonus: keep best-fit tightness as the primary term, but add a large constant bon... |
| 106 | edit | invalid | 0.0000 | 0.9616 | $0.0005 | Replace pure best-fit with a "spread-fit" rule that combines best-fit tightness with a penalty ta... |
| 107 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace best-fit's linear tightness with a squared tightness term so the rule more strongly prefe... |
| 108 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a "first-fit decreasing-like" rule using the learned average item size... |
| 109 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use a harmonics-based score instead of exact best-fit: score each bin by Harmonic(item/bins_capac... |
| 110 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Pure best-fit wastes capacity by ignoring that many items are large (mean ~40), so it packs bins ... |
| 111 | edit | not_better | 0.5814 | 0.9616 | $0.0005 | Replace pure best-fit with a "reserve-a-seed" rule: track the running mean of past items, and amo... |
| 112 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit plus near-perfect-fill bonus": keep best-fit tightness as ... |
| 113 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll replace best-fit with a "reserve-for-larger-items" tie-break: among bins that yield the tigh... |
| 114 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Introduce a two-candidate hybrid: normally use best fit, but when the arriving item is large rela... |
| 115 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a "least-loaded fitting bin" (first-fit) strategy for small ite... |
| 116 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "best-fit plus bounded waste penalty" rule: for each bin, penal... |
| 117 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "best-fit with capacity-fraction lottery" inspired by the Harmo... |
| 118 | edit | improved | 0.9912 | 0.9912 | $0.0006 | Implement a "best fit decreasing-like" idea online: prefer best-fit, but when the item is small r... |
| 119 | edit | not_better | 0.9912 | 0.9912 | $0.0007 | Add a heuristic learned from bin-packing theory: prefer bins whose post-placement residual is clo... |
| 120 | edit | not_better | 0.9579 | 0.9912 | $0.0007 | Refine the sliver penalty: only penalize residuals below a fraction (0.5) of the running mean (tr... |
| 121 | edit | not_better | 0.9556 | 0.9912 | $0.0006 | I'll tune the sliver penalty thresholds: only penalize very small residuals (below 0.35 of the ru... |
| 122 | edit | not_better | 0.9510 | 0.9912 | $0.0006 | Replace the hard sliver penalty with a smooth "waste" objective: score each bin by the estimated ... |
| 123 | edit | not_better | 0.9616 | 0.9912 | $0.0007 | I'll replace the fragile sliver-penalty heuristic with a "best-fit that also avoids near-full-bin... |
| 124 | edit | not_better | 0.9609 | 0.9912 | $0.0006 | Refine the sliver penalty to be milder and tuned, while keeping pure best-fit dominant: penalize ... |
| 125 | edit | invalid | 0.0000 | 0.9912 | $0.0007 | Replace the heuristic scoring with a proper "best fit with a waste-aware residual target": prefer... |
| 126 | edit | not_better | 0.9614 | 0.9912 | $0.0006 | The current best-fit rule is strong, so I'll make the sliver penalty less aggressive but add a sm... |
| 127 | edit | not_better | 0.9616 | 0.9912 | $0.0006 | Replace the fragile sliver penalty with a dominance-based scoring inspired by the pairing/dual-bi... |
| 128 | edit | not_better | 0.9616 | 0.9912 | $0.0005 | Pure best-fit is already near-optimal here; the sliver penalty/distortion hurt. I'll revert to pu... |
| 129 | edit | not_better | 0.9616 | 0.9912 | $0.0005 | I'll keep pure best-fit (smallest post-placement residual wins) as the dominant rule — which scor... |
| 130 | edit | not_better | 0.9616 | 0.9912 | $0.0005 | Keep pure best-fit (smallest residual) as the dominant rule, but replace the large sliver penalty... |
| 131 | edit | not_better | 0.9616 | 0.9912 | $0.0006 | Keep best-fit dominant but replace the ad-hoc sliver penalty with a principled "expected waste" s... |
| 132 | edit | not_better | 0.9616 | 0.9912 | $0.0006 | Keep the strong best-fit rule (tightness dominant), but replace the ad-hoc sliver penalty with a ... |
| 133 | edit | not_better | 0.9616 | 0.9912 | $0.0005 | I'll revert to pure best-fit (smallest post-placement residual wins), which is the strongest rule... |
| 134 | edit | not_better | 0.9616 | 0.9912 | $0.0007 | I'll replace pure best-fit with a "best-fit plus reject-if-it-would-be-better-wasted" rule: keep ... |
| 135 | edit | not_better | 0.9616 | 0.9912 | $0.0006 | Keep pure best-fit (smallest post-placement residual wins) as the dominant rule, but add a small ... |
| 136 | edit | not_better | 0.9616 | 0.9912 | $0.0007 | Keep pure best-fit (smallest post-placement residual) as the dominant rule, but make the sliver p... |
| 137 | edit | not_better | 0.9616 | 0.9912 | $0.0005 | The current rule already does essentially pure best-fit with a sliver penalty; the strongest know... |
| 138 | edit | not_better | 0.9616 | 0.9912 | $0.0005 | Replace the ad-hoc sliver penalty (which hurt performance) with a clean pure best-fit that also b... |
| 139 | edit | improved | 0.9915 | 0.9915 | $0.0008 | Keep best-fit dominant with the sliver penalty and exact-fill bonus, but scale the sliver penalty... |
| 140 | edit | not_better | 0.9652 | 0.9915 | $0.0008 | The current code's histogram/complement bonus uses frequencies over all 5000 items seen so far, b... |
| 141 | edit | not_better | 0.9616 | 0.9915 | $0.0008 | The current rule is essentially best-fit with a sliver penalty and complement bonus, but the sliv... |
| 142 | edit | not_better | 0.9652 | 0.9915 | $0.0008 | I'll keep the proven best-fit-dominant structure but retune the two soft terms so they act only a... |
| 143 | edit | not_better | 0.9616 | 0.9915 | $0.0006 | Replace the ad-hoc penalties with a clean best-fit that only uses the running histogram as a mild... |
| 144 | edit | not_better | 0.9607 | 0.9915 | $0.0007 | The exact-fill bonus of 5.0 currently can override best-fit by preferring a residual-0 bin over a... |
| 145 | edit | not_better | 0.9616 | 0.9915 | $0.0008 | I'll keep the proven best-fit-dominant structure (tightness primary, with the existing sliver/exa... |
| 146 | edit | not_better | 0.9915 | 0.9915 | $0.0008 | I'll keep the proven best-fit-dominant structure but retune the soft terms: restore the strong sl... |
| 147 | edit | improved | 0.9922 | 0.9922 | $0.0008 | I'll add a "waste-aware" adjustment: after choosing the best residual, penalize residuals that ar... |
| 148 | edit | not_better | 0.9922 | 0.9922 | $0.0008 | I'll replace the fixed running-mean sliver penalty with a data-driven one based on the observed d... |
| 149 | edit | not_better | 0.9920 | 0.9922 | $0.0008 | I'll strengthen the data-driven term: instead of a static complement bonus, compute the empirical... |
| 150 | edit | not_better | 0.9920 | 0.9922 | $0.0009 | Add a mild "fuller bin" preference by tracking each bin's original index and rewarding bins whose... |
| 151 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | I'll replace the ad-hoc sliver penalty and waste term with a single principled "reusability" scor... |
| 152 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | I will keep the proven best-fit-dominant structure but replace the ad-hoc sliver/waste terms with... |
| 153 | edit | not_better | 0.9917 | 0.9922 | $0.0008 | Replace the single-scalar running mean with a small quantile estimate: since the item distributio... |
| 154 | edit | not_better | 0.9920 | 0.9922 | $0.0009 | Replace the mean-based sliver threshold with a running median (25th-50th percentile proxy) comput... |
| 155 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | The best-fit rule with a tiny tie-break is clearly optimal for this distribution; instead of ad-h... |
| 156 | edit | not_better | 0.9538 | 0.9922 | $0.0008 | I'll replace the mean-based sliver penalty with a smaller threshold (scaled by 0.5*mean) so the p... |
| 157 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | I'll shift from a heuristic penalty to a cleaner "best-fit with a smart complement" rule: keep ti... |
| 158 | edit | not_better | 0.9666 | 0.9922 | $0.0007 | Remove the histogram-based complement term (which consistently hurt: every attempt using it score... |
| 159 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll simplify the rule to pure best-fit-dominant scoring: tightness (smallest residual) as the ma... |
| 160 | edit | not_better | 0.9628 | 0.9922 | $0.0007 | The pure best-fit score (0.9616) vs. the current best (0.9922) shows the gain comes from NOT dist... |
| 161 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll revert the extras that consistently hurt and instead strengthen the one detail that plausibl... |
| 162 | edit | not_better | 0.9922 | 0.9922 | $0.0009 | Increase the exact-fill bonus from 5.0 to a larger value (e.g. 20.0) so that placing an item into... |
| 163 | edit | not_better | 0.9912 | 0.9922 | $0.0007 | I'll add a second-tier exact-fill logic: when the arriving item exactly fills a bin only if that ... |
| 164 | edit | not_better | 0.9920 | 0.9922 | $0.0006 | I'll add a bulk "matching residual" bonus that rewards a placement leaving a residual equal to th... |
| 165 | edit | not_better | 0.9912 | 0.9922 | $0.0006 | I'll keep the strong best-fit structure but add a small bonus for placing the item into a used bi... |
| 166 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll replace the current best-fit-with-extras rule with a "best fit decreasing"-style rule that a... |
| 167 | edit | not_better | 0.9917 | 0.9922 | $0.0009 | I'll strengthen the exact-fill term by rewarding not just residual == 0 but also residuals that e... |
| 168 | edit | not_better | 0.9912 | 0.9922 | $0.0007 | Remove the repeatedly-harmful data-driven histogram/complement/waste terms and keep a clean best-... |
| 169 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | I'll replace the data-driven extras with a clean best-fit rule plus a "perfect-pairing" bonus: st... |
| 170 | edit | not_better | 0.9912 | 0.9922 | $0.0006 | Replace the fragile hand-tuned multi-term rule with a clean best-fit plus a mild sliver penalty (... |
| 171 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | I'll replace the hand-tuned multi-term rule with a principled "least-waste" scoring: dominant ter... |
| 172 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | I'll replace the hand-tuned multi-term rule with a clean best-fit (tightest residual) primary sco... |
| 173 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll replace the hand-tuned multi-term heuristic with a principled "decreasing best-fit"-style ru... |
| 174 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll replace the multi-term heuristic with a pure best-fit rule (tightest residual, with exact fi... |
| 175 | edit | not_better | 0.9922 | 0.9922 | $0.0009 | I'll keep the strong best-fit/current heuristic structure but recalibrate the exact-fill and sliv... |
| 176 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | Replace the fragile multi-term heuristic with a robust best-fit-plus-complement rule: keep tightn... |
| 177 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll implement a "best fit decreasing"-style rule based on the well-known fact that pairing items... |
| 178 | edit | not_better | 0.9917 | 0.9922 | $0.0007 | I'll keep the current heuristic's tightness/sliver structure but replace the noisy histogram-base... |
| 179 | edit | not_better | 0.9880 | 0.9922 | $0.0006 | Recalibrate the tie-break weights: the histogram-based complement term is noisy while the sliver/... |
| 180 | edit | not_better | 0.9922 | 0.9922 | $0.0009 | Add a deterministic "perfect-pairing" tie-break: keep best-fit tightness as the dominant term, bu... |
| 181 | edit | not_better | 0.9616 | 0.9922 | $0.0008 | The current tie-break weights are on a scale (e.g. ×5) that can override the tightness term and r... |
| 182 | edit | not_better | 0.9616 | 0.9922 | $0.0007 | Replace the noisy histogram-based complement term with a deterministic, data-driven match bonus u... |
| 183 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll simplify to a pure best-fit rule (prefer the smallest residual, with an exact-fill tie-break... |
| 184 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll keep best-fit tightness as the dominant decision but add a cheap, robust tie-break that brea... |
| 185 | edit | not_better | 0.9900 | 0.9922 | $0.0008 | I'll replace the noisy histogram complement term with a smarter data-driven rule: a "match-freque... |
| 186 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | Introduce a "waste-avoidance by residual value" tie-break: after best-fit tightness, add a term t... |
| 187 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll test a score-scale change that keeps best-fit tightness strictly dominant but scales the tig... |
| 188 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | Replace the noisy/hard-coded auxiliary terms with a single scale factor: use best-fit tightness m... |
| 189 | edit | not_better | 0.9616 | 0.9922 | $0.0008 | I'll keep the current best-fit-plus-histogram structure but replace the hard-coded sliver/mean th... |
| 190 | edit | not_better | 0.9616 | 0.9922 | $0.0005 | I'll revert to the pure best-fit rule (prefer smallest residual), which was the empirically best-... |
| 191 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll replace the noisy auxiliary terms with a single, empirically-motivated "best-fit-decreasing-... |
| 192 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | Keep best-fit tightness strictly dominant but add a small tie-break that rewards residuals matchi... |
| 193 | edit | not_better | 0.9616 | 0.9922 | $0.0008 | I'll keep the current structure but replace the noisy histogram-complement term with a cleaner da... |
| 194 | edit | not_better | 0.9616 | 0.9922 | $0.0006 | I'll replace the noisy auxiliary terms with a single, strictly-dominant best-fit rule (prefer sma... |
| 195 | edit | not_better | 0.9900 | 0.9922 | $0.0008 | I'll revert to the exact structure of the original best-scoring program (0.992238) rather than th... |
| 196 | edit | not_better | 0.9912 | 0.9922 | $0.0007 | The current program's histogram "complement" term and waste/sliver penalties appear noisy. I'll r... |
| 197 | edit | improved | 0.9925 | 0.9925 | $0.0010 | Replace the noisy "reward any seen residual size" histogram-complement term with a data-driven bo... |
| 198 | edit | not_better | 0.9616 | 0.9925 | $0.0011 | I'll replace the modal-only complement term and the redundant sliver/waste penalties with a singl... |
| 199 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I'll make the exact-fill bonus much stronger and make the sliver penalty sharper so the rule aggr... |
| 200 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | I'll replace the noisy "modal size" complement bonus with a data-driven "reusable residual value"... |
| 201 | edit | not_better | 0.9605 | 0.9925 | $0.0008 | I'll replace the modal-complement term with a bonus for residuals that are exactly fillable by an... |
| 202 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | I'll keep the current best structure but replace the noisy histogram-based modal complement with ... |
| 203 | edit | not_better | 0.9912 | 0.9925 | $0.0006 | I'll drop the noisy data-dependent histogram/complement and waste terms and use a purely geometri... |
| 204 | edit | not_better | 0.9910 | 0.9925 | $0.0008 | The exact-fill bonus is the key driver, so I'll strengthen it substantially (reward residual 0 he... |
| 205 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | The key signal in online bin packing is not "tight residual" alone but "residual that a typical f... |
| 206 | edit | not_better | 0.9602 | 0.9925 | $0.0006 | Replace the weak, noisy histogram/modal/waste terms with a single "sum-of-two-items" reusable-res... |
| 207 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | The recurring best-performing pattern is best-fit (minimize residual) plus a strong exact-fill bo... |
| 208 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | I'll keep the proven best-fit + exact-fill core but replace the noisy histogram/modal term with a... |
| 209 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy absolute penalty/exact/waste terms with a scale-relative best-fit core: score =... |
| 210 | edit | not_better | 0.9547 | 0.9925 | $0.0008 | I'll replace the noisy histogram/modal complement term with a parametric, stable "expected future... |
| 211 | edit | not_better | 0.9925 | 0.9925 | $0.0007 | The current exact-fill bonus of 5.0 is too small relative to the best-fit tightness slope of 1.0,... |
| 212 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | The current best uses pure best-fit plus bonuses, but best-fit is not the optimal online rule: a ... |
| 213 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I will replace the noisy histogram/modal and waste terms with a stable "sum-of-two-fillability" b... |
| 214 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy data-dependent terms with a clean best-fit + exact-fill bonus, and add a strong... |
| 215 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the proven best-fit tightness plus exact-fill bonus core, but replace the noisy histogr... |
| 216 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll shift from the noisy per-bin heuristics to a more principled best-fit-with-sum-of-two rule: ... |
| 217 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | I'll strengthen the previous best rule by keeping its best-fit tightness and exact-fill bonus but... |
| 218 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the noisy histogram modal complement with a stable, distribution-free term: keep bes... |
| 219 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll simplify to a clean, principled best-fit rule with a strong exact-fill bonus and a mild pena... |
| 220 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | I'll add a "least-loaded fit" second-order tie-break: among tight fits, prefer the bin whose resi... |
| 221 | edit | not_better | 0.9637 | 0.9925 | $0.0006 | The best submissions all lose to the plain histogram-modal version, so the data-driven terms are ... |
| 222 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | I'll strengthen the exact-fill and modal-complement terms in the proven best rule: keep best-fit ... |
| 223 | edit | not_better | 0.9925 | 0.9925 | $0.0009 | I will add a small randomized tie-break that, among bins with equal residual, prefers the one who... |
| 224 | edit | not_better | 0.9856 | 0.9925 | $0.0008 | I'll make the sliver penalty depend on item size so that placing an item that leaves a residual s... |
| 225 | edit | not_better | 0.9925 | 0.9925 | $0.0007 | I'll keep the proven best-fit + exact-fill + modal-complement core, but make the exact-fill bonus... |
| 226 | edit | not_better | 0.9908 | 0.9925 | $0.0008 | I'll replace the single-modal complement bonus with a smoothed, multi-size complement bonus: rewa... |
| 227 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I'll refine the running-mean estimate to be more robust and shift the sliver penalty to start sli... |
| 228 | edit | gate_rejected | 0.9925 | 0.9925 | $0.0008 | Keep the proven best-fit + exact-fill + single modal-complement core unchanged, but add a small s... |
| 229 | edit | not_better | 0.9922 | 0.9925 | $0.0008 | I will keep the proven best-fit + exact-fill + modal-complement core but replace the hard single-... |
| 230 | edit | not_better | 0.9925 | 0.9925 | $0.0009 | I will add a mild "next-item fit" bonus that rewards a bin whose residual after placement is clos... |
| 231 | edit | not_better | 0.9640 | 0.9925 | $0.0008 | Keep the proven core but lower the sliver threshold from the running mean to a fixed small value ... |
| 232 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I'll tune the penalization/tie-break coefficients based on the proven best-fit core: reduce the s... |
| 233 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the best-fit core but remove the constant-and-tie-break-heavy sliver/waste penalties (w... |
| 234 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I'll keep the proven best-fit core and add a bounded, decaying modal-complement bonus computed fr... |
| 235 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the hand-tuned penalty/bonus heuristic with a pure best-fit rule (score = -residual)... |
| 236 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the pure best-fit rule (score = -residual, which is provably strong for this problem) b... |
| 237 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I will replace the perturbing hand-tuned bonuses with pure best-fit (score = -residual) and break... |
| 238 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the noisy heuristic with pure best-fit (score = -residual, the strongest simple rule... |
| 239 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the strong best-fit core but replace the noisy mean/histogram penalties with a single d... |
| 240 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I will replace the heuristic with pure best-fit (score = -residual) and add only a tiny, bounded ... |
| 241 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the noisy mean/heuristic scoring with a clean, tunable two-term rule: a strong best-... |
| 242 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | The pure best-fit always leaves the smallest residual, but a small bounded "reusability" bonus re... |
| 243 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I will make the rule near-pure best-fit by sharply reducing the magnitude of the sliver/waste pen... |
| 244 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the proven best-fit core (score = -residual) and add only a tiny, bounded tie-break tha... |
| 245 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the heuristic with a simpler, stronger rule: strict best-fit (score = -residual) plu... |
| 246 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Use a fixed reference mean (40) instead of the drifting running mean, and make the sliver penalty... |
| 247 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the best-fit core but make the sliver penalty purely data-driven and bounded using a fi... |
| 248 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the heuristic entirely with a clean, parameter-light rule that behaves like best-fit... |
| 249 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the heuristic with a clean combination of best-fit plus a "worst-fit among near-ties" cor... |
| 250 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Recent small perturbations all scored 0.961642 while the original composite heuristic scored 0.99... |
| 251 | edit | not_better | 0.9922 | 0.9925 | $0.0008 | I'll revert to the original strong composite heuristic (which scored 0.992488) but replace its dr... |
| 252 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | Revert to the original composite heuristic (score 0.992488) and refine it by replacing the crude ... |
| 253 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the composite heuristic's ad-hoc bonuses with a single principled term: strong best-... |
| 254 | edit | not_better | 0.9861 | 0.9925 | $0.0009 | I'll keep the proven composite structure but tune it: strengthen the exact-fill bonus and the sli... |
| 255 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I'll replace the ad-hoc penalty/bonus mix with a principled "residual usefulness" score: keep bes... |
| 256 | edit | not_better | 0.9903 | 0.9925 | $0.0009 | I'll add a "perfect complement" bonus to the existing heuristic: strongly reward bins where the r... |
| 257 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Replace the drifting running mean and noisy single-mode histogram bonus with a fixed reference me... |
| 258 | edit | not_better | 0.9600 | 0.9925 | $0.0007 | Keep the proven pure best-fit core (score = -residual) but restrict the heuristic extras to only ... |
| 259 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | I'll strip the heuristic down to pure best-fit (score = -residual) without any penalties or bonus... |
| 260 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Replace the heuristic with a "residual viability class" score: bins whose residual is exactly 0 g... |
| 261 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | I'll keep the proven best-fit core (score = -residual) but add a stronger, more targeted exact-fi... |
| 262 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy running-mean/histogram heuristics with a "match the dominant residual classes" ... |
| 263 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the ad-hoc penalties with a principled "waste-fraction" best-fit score: rank by resi... |
| 264 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the noisy running-mean/histogram heuristics with a purely fixed, parameter-free best... |
| 265 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I'll keep the proven best-fit core (score = -residual) unchanged and only add a non-disruptive ti... |
| 266 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Keep the proven best-fit ordering (maximize -residual) but add a small, monotone bonus that only ... |
| 267 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the ad-hoc heuristics with a principled "score = -(residual waste)" best-fit: keep t... |
| 268 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Previous composite perturbations hurt, and plain best-fit is strong, but the genuine bin-choice l... |
| 269 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy running-mean/histogram heuristics with a clean, principled score that keeps bes... |
| 270 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy running-mean/histogram heuristics with a "best-fit plus reserve-capacity" rule:... |
| 271 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | After many perturbed variants all scored 0.9616 while the original composite scored 0.9925, the e... |
| 272 | edit | not_better | 0.9915 | 0.9925 | $0.0008 | All previous perturbations collapsed to ~0.9616, which is suspiciously identical: that is the sco... |
| 273 | edit | not_better | 0.9880 | 0.9925 | $0.0008 | I'll keep the proven composite structure (tightness + exact bonus + sliver penalty) but remove th... |
| 274 | edit | not_better | 0.9678 | 0.9925 | $0.0008 | I'll keep the proven composite structure and add a monotone, data-driven term that penalizes resi... |
| 275 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | I'll tune the exact-fill bonus upward and make it scale with item size, since exact fills are the... |
| 276 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Reduce the exact-fill bonus to 0.5 (a value strictly less than 1) so it acts only as a tie-breake... |
| 277 | edit | not_better | 0.9925 | 0.9925 | $0.0009 | Keep the proven composite (best-fit tightness + sliver penalty + exact bonus + modal complement) ... |
| 278 | edit | not_better | 0.9903 | 0.9925 | $0.0008 | Replace the noisy global-histogram modal-complement term with a smooth data-driven "residual reus... |
| 279 | edit | not_better | 0.9915 | 0.9925 | $0.0008 | I'll replace the noisy modal-histogram complement term with a smoothed reuse-value lookup over th... |
| 280 | edit | not_better | 0.9920 | 0.9925 | $0.0009 | Replace the modal-histogram complement term with a "recency/consolidation" term that mildly boost... |
| 281 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the noisy running-mean/sliver heuristics with a cleaner best-fit plus a data-driven ... |
| 282 | edit | not_better | 0.9915 | 0.9925 | $0.0007 | Replace the heuristic modal-complement with a proper data-driven "best fit decreasing"-style reus... |
| 283 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | Introduce a self-scaling "residual reusability" term computed from the empirical histogram of pas... |
| 284 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I will replace the noisy hand-tuned heuristic blend with a cleaner, self-scaling score: best-fit ... |
| 285 | edit | not_better | 0.9616 | 0.9925 | $0.0010 | Consolidate the two overlapping dead-zone penalties (sliver ×2.0 and waste ×1.0) into a single cl... |
| 286 | edit | not_better | 0.9917 | 0.9925 | $0.0009 | I will replace the noisy modal-histogram complement term with a coherent "sum-of-two-items" reuse... |
| 287 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the hand-tuned dead-zone/complement blend with a pure best-fit score plus only a small, b... |
| 288 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll keep pure best-fit as the dominant term but replace the noisy histogram/running-mean terms w... |
| 289 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the noisy histogram/running-mean penalties with a clean "sum-of-two best-fit" rule: ... |
| 290 | edit | not_better | 0.9915 | 0.9925 | $0.0009 | Keep the strong hand-tuned blend that scored 0.992488 as the core, but replace the single "modal"... |
| 291 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I will keep the proven best-fit-with-penalties core but replace the arbitrary modal-complement an... |
| 292 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll keep pure best-fit as the dominant term, but replace the noisy histogram/running-mean terms ... |
| 293 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll keep the proven best-fit core but replace the fragile histogram/mean penalties with a robust... |
| 294 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | Keep the proven best-fit core but replace the fragile modal-histogram/running-mean penalties with... |
| 295 | edit | not_better | 0.9917 | 0.9925 | $0.0009 | Keep the proven best-fit-with-blend core (which scored 0.992488) exactly as is, but replace the s... |
| 296 | edit | not_better | 0.9922 | 0.9925 | $0.0008 | I'll keep the proven best-fit core but replace the noisy single-modal complement and fragile runn... |
| 297 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I'll keep the proven best-fit core intact but tune the constant weights more conservatively: rais... |
| 298 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I'll keep the proven best-fit-with-blend core but replace the single-modal complement match with ... |
| 299 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll keep the proven best-fit core intact and instead try a well-established online bin-packing i... |
| 300 | edit | not_better | 0.9920 | 0.9925 | $0.0009 | I'll keep the exact same best-fit core and constants, but make the complement bonus far more usef... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,6 +1,13 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with a residual-usability tie-break based on a running mean and a
+histogram of seen item sizes (to nudge residuals toward frequently reusable sizes)."""
 import numpy as np
+
+_mean = 40.0
+_count = 0
+# Histogram of seen item sizes (1..100), used to reward residuals that match
+# a common leftover size.
+_hist = np.zeros(101, dtype=np.float64)
 
 
 def priority(item, bins):
@@ -10,5 +17,45 @@
     bins: numpy int64 array with the remaining capacity of every bin the item fits in,
           including unused bins (remaining capacity 100), in bin order.
     """
-    return -(bins - item)
+    global _mean, _count, _hist
+
+    # Update running mean and histogram of past items (before scoring this one).
+    _mean = (_mean * _count + item) / (_count + 1)
+    _count += 1
+    _hist[item] += 1.0
+
+    residual = bins - item  # remaining capacity after placing the item here
+
+    # Best-fit tightness: prefer smaller residual.
+    tightness = -residual.astype(np.float64)
+
+    # Penalize residuals that are positive but smaller than a typical item:
+    # such slivers are effectively wasted capacity.
+    m = _mean
+    sliver = (residual > 0) & (residual < m)
+    penalty = np.where(sliver, (m - residual) * 2.0, 0.0)
+
+    # Small bonus for very tight fits (residual 0) to strongly prefer exact fills.
+    exact = (residual == 0).astype(np.float64) * 5.0
+
+    # Data-driven complement bonus: reward residuals that equal the most
+    # frequently seen item size so far, since such a leftover is the size most
+    # likely to be reusable by a future item.
+    r = residual
+    valid = r >= 1
+    if _count > 0:
+        modal = int(np.argmax(_hist[1:])) + 1
+        match = (valid & (r == modal)).astype(np.float64)
+    else:
+        match = np.zeros_like(r, dtype=np.float64)
+    complement = match * 3.0
+
+    # Waste-aware term: a residual that is just below the mean item size will
+    # likely never be reused and is effectively lost capacity, so add a mild
+    # extra penalty scaled by how close it is to the mean (larger residual =
+    # more recoverable, smaller residual = more dead).
+    near_full = (residual > 0) & (residual < m)
+    waste = np.where(near_full, (1.0 - residual / m) * 1.0, 0.0)
+
+    return tightness - penalty + exact + complement - waste
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (28 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 20 | `global _mean, _count, _hist` | -0.9925 | essential: the program fails or turns invalid without it |
| 27 | `residual = bins - item` | -0.9925 | essential: the program fails or turns invalid without it |
| 27 | `term + bins` | -0.9925 | essential: the program fails or turns invalid without it |
| 30 | `tightness = -residual.astype(np.float64)` | -0.9925 | essential: the program fails or turns invalid without it |
| 34 | `m = _mean` | -0.9925 | essential: the program fails or turns invalid without it |
| 35 | `sliver = (residual > 0) & (residual < m)` | -0.9925 | essential: the program fails or turns invalid without it |
| 36 | `penalty = np.where(sliver, (m - residual) * 2.0, 0.0)` | -0.9925 | essential: the program fails or turns invalid without it |
| 39 | `exact = (residual == 0).astype(np.float64) * 5.0` | -0.9925 | essential: the program fails or turns invalid without it |
| 44 | `r = residual` | -0.9925 | essential: the program fails or turns invalid without it |
| 45 | `valid = r >= 1` | -0.9925 | essential: the program fails or turns invalid without it |
| 46 | `if _count > 0: ...` | -0.9925 | essential: the program fails or turns invalid without it |
| 47 | `modal = int(np.argmax(_hist[1:])) + 1` | -0.9925 | essential: the program fails or turns invalid without it |
| 48 | `match = (valid & (r == modal)).astype(np.float64)` | -0.9925 | essential: the program fails or turns invalid without it |
| 51 | `complement = match * 3.0` | -0.9925 | essential: the program fails or turns invalid without it |
| 57 | `near_full = (residual > 0) & (residual < m)` | -0.9925 | essential: the program fails or turns invalid without it |
| 58 | `waste = np.where(near_full, (1.0 - residual / m) * 1.0, 0.0)` | -0.9925 | essential: the program fails or turns invalid without it |
| 27 | `term - item` | -0.0865 | matters |
| 60 | `term + tightness` | -0.0829 | matters |
| 60 | `term - penalty` | -0.0308 | matters |
| 24 | `_count += 1` | -0.0077 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 23: `_mean = (_mean * _count + item) / (_count + 1)`
- line 25: `_hist[item] += 1.0`
- line 47: `term + int(np.argmax(_hist[1:]))`
- line 47: `term + 1`
- line 50: `match = np.zeros_like(r, dtype=np.float64)`
- line 60: `term + exact`
- line 60: `term + complement`
- line 60: `term - waste`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9925 | 0.9933 |
| minimal (8 parts removed) | 0.9915 | 0.9928 |

Minimal program:

```python
"""Best fit with a residual-usability tie-break based on a running mean and a
histogram of seen item sizes (to nudge residuals toward frequently reusable sizes)."""
import numpy as np
_mean = 40.0
_count = 0
_hist = np.zeros(101, dtype=np.float64)

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    global _mean, _count, _hist
    _count += 1
    residual = bins - item
    tightness = -residual.astype(np.float64)
    m = _mean
    sliver = (residual > 0) & (residual < m)
    penalty = np.where(sliver, (m - residual) * 2.0, 0.0)
    exact = (residual == 0).astype(np.float64) * 5.0
    r = residual
    valid = r >= 1
    if _count > 0:
        modal = 0
        match = (valid & (r == modal)).astype(np.float64)
    else:
        pass
    complement = match * 3.0
    near_full = (residual > 0) & (residual < m)
    waste = np.where(near_full, (1.0 - residual / m) * 1.0, 0.0)
    return tightness - penalty
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online --budget 0.75 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 0
python -m autoresearch.loop --report experiments/llm-long-search-v1/runs/s0   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `adb7fe98e2b1a4de003a9248cda56b4f0f74b6e5`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bin_packing_online/evaluate.py` `0ac9a4a253a299d2`
- `problems/bin_packing_online/initial.py` `609927c5ea619a94`
- `problems/bin_packing_online/problem.md` `aa1aa4a2d6d00d6a`
- `problems/bin_packing_online/verify.py` `b3ea67a1c6f94885`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
