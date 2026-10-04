# Research loop report: bp_sh_c80

| | |
|---|---|
| problem | `bp_sh_c80` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0850 of a $0.20 hard cap, 150 calls, 285,455 tokens |
| wall time | search 1456 s, baselines 36 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (149 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9349 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9349 | 0.9634 |  |
| baseline `funsearch_or` | 0.9390 | 0.9711 | `problems/bp_sh_c80/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.7852 | 0.9937 | `problems/bp_sh_c80/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.8821 | 0.9950 | `problems/bp_sh_c80/baselines/sum_of_squares.py` |

Audit: public 0.9349 → 0.9349 (+0.0000), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program -0.0285.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9390). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a small tie-breaking bonus that favors leaving a residual close to the distribution mean (~40... |
| 2 | edit | not_better | 0.9272 | 0.9349 | $0.0005 | I'll implement a "best fit with future-aware residual preference" rule: among near-tight fits, pr... |
| 3 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a small tie-breaking bonus that favors bins which, after placement, still retain a residual a... |
| 4 | edit | not_better | 0.9264 | 0.9349 | $0.0005 | I'll implement a proper "Best Fit Decreasing"-flavored rule with an online twist: score bins by t... |
| 5 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Use a proper Best-Fit rule based on the item size and, crucially, exploit bin index order: among ... |
| 6 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace plain best-fit with a "best fit + reserve-aware" rule: score the tightest fit highest, bu... |
| 7 | edit | not_better | 0.4064 | 0.9349 | $0.0005 | Switch to Worst-Fit: prefer the bin with the most remaining capacity (emptiest bin that fits), wh... |
| 8 | edit | not_better | 0.8858 | 0.9349 | $0.0004 | I'll test Worst-Fit but bounded: among bins that fit, prefer the one whose post-placement residua... |
| 9 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the pure best-fit with a "best fit + sub-40 residual preferred over near-zero residu... |
| 10 | edit | gate_rejected | 0.9349 | 0.9349 | $0.0007 | I'll add online state (a running histogram of observed item sizes) and score each bin by the expe... |
| 11 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best fit with an online "modified best fit" that keeps a running estimate of the typ... |
| 12 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Keep best-fit but add online state tracking a running histogram of item sizes and evenly spread s... |
| 13 | edit | not_better | 0.8255 | 0.9349 | $0.0005 | Replace pure best-fit with a "best fit but leave a slightly larger residual when the tightest fit... |
| 14 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will implement an online Learned Best-Fit that tracks the item-size histogram and, instead of a... |
| 15 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Use a classic harmonic-style rule: since the distribution is Weibull with mean ~40, best-fit crea... |
| 16 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace the pure best-fit with a randomized family: use online state to occasionally (with the ar... |
| 17 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | I'll replace pure best fit with an online variant that tracks the empirical item-size histogram a... |
| 18 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best fit with a constant-factor-aware "almost best fit" that accepts a slightly larg... |
| 19 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Implement an online "Harmonic-like best fit": discretize items into size classes based on item si... |
| 20 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll replace best-fit with a "Best-Fit with gap-based class matching": track empirically which re... |
| 21 | edit | not_better | 0.9349 | 0.9349 | $0.0009 | Try a learned "residual-matching" rule: track an online histogram of item sizes, and among bins w... |
| 22 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will add a small stateful "reservation" tie-break: pure best-fit (tightest residual) tends to b... |
| 23 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | Replace myopic best-fit with a stateful online rule that tracks a decoded item-size histogram and... |
| 24 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | I'll switch from myopic best-fit to a randomized-restart style rule using the observed universal ... |
| 25 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace myopic best-fit with a "Best-Fit with least-loaded-full-bin threshold" variant: sinc... |
| 26 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace plain best-fit with a "worst-fit among near-best" rule that breaks ties toward larger pos... |
| 27 | edit | not_better | 0.8812 | 0.9349 | $0.0005 | Implement the classic "Almost Worst Fit / Best Fit hybrid" trick from online bin packing: keep be... |
| 28 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the pure best-fit rule with the classic online bin-packing heuristic "Best Fit Decre... |
| 29 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement the classic "Best Fit with a full-bin-prevention twist" that is known to help onli... |
| 30 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Use a "best fit with occasional worst-fit for large items" rule: plain best-fit is strong here, b... |
| 31 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace myopic best-fit with a stateful "Best-Fit with dynamic exact-fill reward" that uses ... |
| 32 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll add a small stateful "reserve large empty bins for large items" heuristic: keep best-fit as ... |
| 33 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a score-and-repair style rule based on the classic "Harmonic" online bin-packing i... |
| 34 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Plain best fit is already near-optimal, so I'll add a small stateful "harmonic-fit" nudge: keep b... |
| 35 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Implement the classic "Worst-Fit with a bounded threshold" idea differently: use a stateful rule ... |
| 36 | edit | not_better | 0.9129 | 0.9349 | $0.0006 | I'll implement the classic "Best Fit Decreasing"-style improvement for online setting: an "Almost... |
| 37 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace plain best-fit with a rule that prefers bins whose post-placement residual is close to a ... |
| 38 | edit | not_better | 0.9349 | 0.9349 | $0.0011 | Add a strong penalty against placing items smaller than the distribution mean (~40) into a comple... |
| 39 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a stateful "open a new bin only when necessary" rule: track the best-fit residual; if the ite... |
| 40 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Swap plain best-fit for a stateful "best-fit with residual-reuse for nearly-full bins": keep best... |
| 41 | edit | not_better | 0.8600 | 0.9349 | $0.0006 | I'll switch to a size-class-aware "best fit" variant: maintain an online histogram of item sizes ... |
| 42 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace plain best-fit with a stateful "best-fit plus least-loaded tiebreak among near-equal... |
| 43 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a score-function rule that targets residuals near a value that maximizes future pa... |
| 44 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the stateless best-fit with "best fit with reservation": since the distribution is W... |
| 45 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace best-fit with a "fuller-bin-first" rule that prefers non-empty bins with the smalles... |
| 46 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll combine best-fit with a "residual complement" bonus: estimate the distribution's item-size h... |
| 47 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a refined "best-fit decreasing-aware" rule that adds a stateful o... |
| 48 | edit | not_better | 0.8206 | 0.9349 | $0.0005 | I'll replace pure best-fit with a harmonic/dominant-item-aware rule: best-fit is optimal-ish for ... |
| 49 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a stateful "best-fit with remaining-capacity-aware unloading" rule: track an onlin... |
| 50 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a stateful "smart reserved best-fit" rule: keep an online estimate of ... |
| 51 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll replace stateless best-fit with a small-lookahead heuristic: when an item would leave a bin ... |
| 52 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch from best-fit to a "best-fit with a tunable gap-acceptance bias": among bins whose po... |
| 53 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | The problem evaluates 80-item streams (so at most ~80 bins exist, all shown in the array), meanin... |
| 54 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I will add a stateful "gap-filling reservation" rule: keep an online histogram of item sizes to e... |
| 55 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit with a small-lookahead rule that buffers the single current item: when a ne... |
| 56 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch from pure best-fit to a "best-fit over the residual but with an exact-fit bonus": bin... |
| 57 | edit | not_better | 0.9313 | 0.9349 | $0.0006 | Replace pure best-fit with a "tuned best-fit that reserves small gaps": among fitting bins, use b... |
| 58 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will replace pure best-fit with a stateful "extensible best-fit": keep a running histogram of i... |
| 59 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Pure best-fit fails when several equal-size items could have been grouped: I will use a "best-fit... |
| 60 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch from pure best-fit to a "modified best-fit / first-fit hybrid": use best-fit (tightes... |
| 61 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll replace pure best-fit with an online-learned "harmonic/quantized bin class" rule: classify b... |
| 62 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll keep pure best-fit (which is already strong) but add a key improvement for ties: when multip... |
| 63 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | The current tie-breaking is inert; instead I'll make best-fit "sticky" by maximizing the resultin... |
| 64 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll add a mild "worst-fit bonus" only among bins whose residual after placement is small but non... |
| 65 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a harmonic-style reservation rule: track the most common (modal) ... |
| 66 | edit | not_better | 0.8623 | 0.9349 | $0.0011 | I'll replace pure best-fit with an online-learned "matching residual" rule: keep a histogram of i... |
| 67 | edit | invalid | 0.0000 | 0.9349 | $0.0006 | I will switch to a "residual-quality weighted best-fit" that scores each bin by combining tightne... |
| 68 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is already near-optimal per placement; the biggest remaining gain is reducing the number... |
| 69 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is already strong; I'll add a light second-fit avoidance by preferring, among the tighte... |
| 70 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | I'll make best-fit smarter by penalizing residuals that fall into a "dead zone" (too small to be ... |
| 71 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a "reserve-aware" rule that still strongly prefers tight fits but... |
| 72 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is already near-optimal, but ties are common and currently broken toward the FIRST bin. ... |
| 73 | edit | not_better | 0.9017 | 0.9349 | $0.0009 | Replace best-fit with "almost-worst-fit / second-best-fit": among fitting bins, prefer the bin le... |
| 74 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch to a Best-Fit-Decreasing-like online rule that reserves exact-fit bins: keep a small ... |
| 75 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is near-optimal, so I'll add a stateful "harmonic" tweak: track the running mean item si... |
| 76 | edit | not_better | 0.8255 | 0.9349 | $0.0005 | I'll test a stateful cutoff rule that prevents best-fit from creating unusably tiny residuals: tr... |
| 77 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a hybrid that keeps best-fit's strong core but adds a conservative "perfect-fit re... |
| 78 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a "best-fit among non-empty bins, but leave some slack": compute ... |
| 79 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | The pure best-fit rule ignores a well-known online improvement: when an item exactly fills a bin ... |
| 80 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a "best-fit plus pair-anticipation" rule: track recent item sizes... |
| 81 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "modified best-fit with residual-value damping": score bins by -(res... |
| 82 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit with a two-metric rule: primary best-fit, but break near-ties by preferring... |
| 83 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll try a "power of two choices" style twist on best-fit: keep best-fit as the primary rule but,... |
| 84 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a residual-bin score based on the known harmonic/Modified-Best-Fit ide... |
| 85 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a proper sample-based "best fit with a learned value function": maintain an empiri... |
| 86 | edit | not_better | 0.8228 | 0.9349 | $0.0005 | Replace pure best-fit with a residual-class rule: score exact fits highest, then prefer bins whos... |
| 87 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace best-fit with a "best-fit plus smallest-residual-tie-to-largest-bin" rule that also sligh... |
| 88 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a score that adds a small, size-aware tie-breaker to best-fit: bins whose post-pla... |
| 89 | edit | not_better | 0.9241 | 0.9349 | $0.0009 | Replace pure best-fit with a size-weighted variant of Best-Fit-Decreasing-like scoring that works... |
| 90 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Reproduce the strong online bin-packing heuristic "Sum of Squares" (Csirik et al.) exactly: prefe... |
| 91 | edit | not_better | 0.9114 | 0.9349 | $0.0005 | I'll implement a proper offline-lookahead-free improvement: use the well-known "Best Fit with Att... |
| 92 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch to a randomized/rotational tie-breaking over near-best bins that also mildly rewards ... |
| 93 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the pure best-fit rule with a "best-fit + good-residual" rule that prefers a bin who... |
| 94 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Implement a "residual-quality" best-fit: rank primarily by tightest fit, but apply a strong bonus... |
| 95 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Implement a two-phase rule: primary key is best-fit (tightest residual), but when multiple candid... |
| 96 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | Try a best-fit variant where, among bins that leave a residual within 1 unit of the tightest fit,... |
| 97 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Instead of pure best-fit on the residual, use "best-fit by resulting residual, but among the bins... |
| 98 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a "best-fit with a small look-ahead-free bump": rank bins by tigh... |
| 99 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a rank that prefers placing the item so the residual hits the "sweet s... |
| 100 | edit | not_better | 0.9345 | 0.9349 | $0.0006 | I'll implement a proper "best-fit + first-fit residual reuse" rule by scoring each bin as a two-l... |
| 101 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Adopt a "best-fit decreasing-style" scoring that also considers future fit by preferring bins whe... |
| 102 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a fixed small tie-break term that prefers bins whose remaining capacity is closest to a multi... |
| 103 | edit | not_better | 0.4064 | 0.9349 | $0.0004 | I'll switch from best-fit to a worst-fit-style rule on the residual: rank bins so that the bin le... |
| 104 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit with a classic "best-fit with gap matching" rule: score each bin by preferr... |
| 105 | edit | not_better | 0.9349 | 0.9349 | $0.0009 | I'll replace pure best-fit with a rank that additionally penalizes bins whose resulting residual ... |
| 106 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Use a hybrid: apply best-fit, but when several bins are within 1 unit of the tightest fit, break ... |
| 107 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a bounded best-fit with online learning of a "waste threshold": prefer the tightes... |
| 108 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Implement a "best-fit with reservoir" rule: normally place with best fit, but occasionally (when ... |
| 109 | edit | invalid | 0.0000 | 0.9349 | $0.0006 | I'll add a small online-learned tie-break that, among bins nearly tied for best fit, prefers the ... |
| 110 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with "best-fit decreasing-like" grouping: score each bin primarily by ... |
| 111 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the pure best-fit rank with a controlled "almost-worst-fit" rule: use best fit (smal... |
| 112 | edit | not_better | 0.9349 | 0.9349 | $0.0010 | Switch to a size-aware hybrid: for large items (≥ capacity/2) use best fit (tightest residual) to... |
| 113 | edit | not_better | 0.9302 | 0.9349 | $0.0005 | I'll try a two-regime rule that is known to work well on Weibull(mean 40) item streams: for small... |
| 114 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the pure best-fit rule with a load-aware best-fit that occasionally reserves one nea... |
| 115 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll implement a bounded online-learned tie-break among near-best-fit candidates: keep pure best-... |
| 116 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | I'll replace pure best-fit with an adaptive "harmonic" bin-choice rule: best-fit is known to be w... |
| 117 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with the well-known "Sum of Squares" (SS) bin-packing rule: score each... |
| 118 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | Most attempts only tweaked pure best-fit and stalled at 0.9349. I'll switch the primary rule to "... |
| 119 | edit | not_better | 0.8228 | 0.9349 | $0.0005 | I'll switch from first-fit (score = -bins) to the classical "Harmonic"-inspired / best-fit hybrid... |
| 120 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch to the classic Best-Fit-Decreasing-style rule that is strong on Weibull streams but a... |
| 121 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace the ad-hoc heuristics with a principled online rule: score each bin by the "waste" i... |
| 122 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement the classic "Sum of Squares" (SS) online rule from the literature but in its resid... |
| 123 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll test whether aggressive first-fit/consolidation (smaller remaining capacity ranked higher) a... |
| 124 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement the classic Harmonic-K style rule: items are classified into size intervals and ma... |
| 125 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | I'll implement the "Better Fit" heuristic (Cai et al.): score bins by the product of the item's r... |
| 126 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | All prior attempts use only the current item's fit. I'll add a stateful "reserve the emptiest bin... |
| 127 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll add state: track the histogram of past item sizes, then score bins by a combination of (a) b... |
| 128 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the simple best-fit rule with a hybrid of best-fit and worst-fit driven by the fract... |
| 129 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a stateful "residual histogram matching" rule: track the residual capacities of bins after ea... |
| 130 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll try a stateful "reserve the emptiest bins for large items" adaptive rule: track the running ... |
| 131 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll stop tuning the ranking rule (all variants plateaued) and instead make the rule a true best-... |
| 132 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch from pure best-fit to a stateful "reuse before open" rule that strongly prefers the t... |
| 133 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a two-parameter Bernstein-optimal-style linear combination: score... |
| 134 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch from pure best-fit to a "best-fit with reserve" hybrid that reserves empty bins: scor... |
| 135 | edit | not_better | 0.4064 | 0.9349 | $0.0004 | I'll stop the plateaued heuristic tweaks and implement the classic "almost-worst-fit / harmonic" ... |
| 136 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll change the rule to favor tightest-fit but with a significant bonus to earlier bin indices (a... |
| 137 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace best-fit with a stateful "best-fit with aging/close" rule: among bins that fit, prefer th... |
| 138 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a score based on the classic "sum of squares" (SS) heuristic insi... |
| 139 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Add a "reserve" term based on the count of empty bins: reward placing items into already-used bin... |
| 140 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a harmonic-style class-based rule: assign each bin a "level" base... |
| 141 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll add a small "full-bin consolidation" bonus to best-fit: when the item would leave the bin's ... |
| 142 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Replace pure best-fit tightness with a stateful rule that tracks the empirical average item size ... |
| 143 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace the pure best-fit rule with a stateful "fractional/level-based" rule derived from the Sum... |
| 144 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Implement a proper "Harmonic/level" style rule: precompute thresholds after each call so that ite... |
| 145 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I will switch from pure best-fit to a hybrid rule that tracks a running estimate of the item-size... |
| 146 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I will replace pure best-fit with a lookahead-free "best fit decreasing emulation" style rule tha... |
| 147 | edit | not_better | 0.9257 | 0.9349 | $0.0007 | Implement the classic Harmonic bin-packing rule (known to have a better worst-case ratio than bes... |
| 148 | edit | not_better | 0.8976 | 0.9349 | $0.0007 | Replace best-fit with a stateful rule based on the "Best Fit with lookahead-free sampling" idea f... |
| 149 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch from best-fit to a rule based on the "Modified Best Fit Decreasing" insight: prefer e... |
| 150 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | The current best-fit score of 0.9349 is likely near-optimal for a greedy rule, so I'll switch to ... |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Skipped: priority has nothing to remove (a single return without a +/- chain).

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_c80 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 3
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_c80-s3   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_c80/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_c80/initial.py` `609927c5ea619a94`
- `problems/bp_sh_c80/problem.md` `190017a698e23cd8`
- `problems/bp_sh_c80/verify.py` `dc0d05d86db9dbf0`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
