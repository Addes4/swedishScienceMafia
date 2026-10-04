# Research loop report: bp_sh_c80

| | |
|---|---|
| problem | `bp_sh_c80` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0909 of a $0.20 hard cap, 150 calls, 311,191 tokens |
| wall time | search 1606 s, baselines 54 s, explain 174 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (149 valid), 1 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9349 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9351 | 0.9625 | **OVERFIT?** public rose, hidden fell |
| baseline `funsearch_or` | 0.9390 | 0.9711 | `problems/bp_sh_c80/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.7852 | 0.9937 | `problems/bp_sh_c80/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.8821 | 0.9950 | `problems/bp_sh_c80/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9349 | 0.9634 | 8 parts removed |

Audit: public 0.9349 → 0.9351 (+0.0002), hidden 0.9634 → 0.9625 (-0.0009); public − hidden gap of the final program -0.0274. **OVERFIT?** The public score rose while the hidden score fell: treat the gain as unconfirmed.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9390). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9349 | 0.9349 | $0.0003 | Introduce a size-aware threshold: for small items prefer the fullest/largest bins (worst fit) to ... |
| 2 | edit | not_better | 0.9166 | 0.9349 | $0.0004 | Replace pure best-fit with a hybrid rule that blends best-fit with a "residual-fit" preference tu... |
| 3 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace pure best-fit with a rule that uses the first-fit-descending-style idea adapted online: p... |
| 4 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Replace pure best-fit with a hybrid: keep best-fit for large items, but for small items (size &lt... |
| 5 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | I will add a light "first-fit" tie-break: score bins primarily by best-fit (tightest remaining ca... |
| 6 | edit | not_better | 0.9274 | 0.9349 | $0.0004 | I will replace pure best-fit with a rule that scores each bin by how close its remaining capacity... |
| 7 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Implement a "score = -bins, but with a small bonus for the fullest bin that leaves a residual mat... |
| 8 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is already near-optimal for the dominant small/medium items, but its weakness is leaving... |
| 9 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I will switch from best-fit to a score that combines best-fit with a lookahead-free "residual reu... |
| 10 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a size-aware hybrid: use exact best-fit (tightest residual) for items that are at ... |
| 11 | edit | not_better | 0.8419 | 0.9349 | $0.0006 | I will replace pure best-fit with a hybrid rule that uses exact best-fit for medium/large items b... |
| 12 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll introduce an online "subset-sum awareness" trick: keep state of the largest residual seen re... |
| 13 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll keep best-fit as the core (it is strong) but add a tie-break that, among bins that fit, pref... |
| 14 | edit | not_better | 0.7203 | 0.9349 | $0.0006 | (no description) |
| 15 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "best-fit with tie-break toward avoiding hard-to-fill residuals" rul... |
| 16 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch to a variant of best-fit that uses the known item distribution (Weibull, mean ~40): i... |
| 17 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a "best-fit over recent item sizes" scheme: keep a small state of... |
| 18 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll keep best-fit as the primary rule but replace its raw residual cost with a monotone, distrib... |
| 19 | edit | not_better | 0.9153 | 0.9349 | $0.0005 | I will add a light stateful improvement to best-fit: track a running estimate of the current item... |
| 20 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a stateful "harmonic/adaptive" rule: alternate exploration among ... |
| 21 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a two-phase strategy: track the fraction of a stream consumed via... |
| 22 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll try a small, robust tweak to best-fit: prefer the tightest fit, but among bins whose post-pl... |
| 23 | edit | invalid | 0.0000 | 0.9349 | $0.0006 | I'll switch from pure best-fit to a "best-fit with resampling tie-break": choose the tightest-fit... |
| 24 | edit | not_better | 0.8871 | 0.9349 | $0.0005 | I'll switch from pure best-fit to a “lowest-index-fill/almost-worst-fit hybrid” that avoids the m... |
| 25 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace best-fit with a "best-fit decreasing-aware" tie-break: among bins whose post-placeme... |
| 26 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | I'll replace the purely myopic best-fit residual with a rule that targets a preferred post-placem... |
| 27 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a two-stage rule: prefer a bin that leaves a small "perfect-fit-l... |
| 28 | edit | not_better | 0.9349 | 0.9349 | $0.0007 | Switch from pure best-fit to a stateful "harmonic-like" rule: track the count of bins opened impl... |
| 29 | edit | not_better | 0.7007 | 0.9349 | $0.0005 | Replace pure best-fit with a "best-fit with a tail-reservation tie-break": use integer-exact best... |
| 30 | edit | not_better | 0.8547 | 0.9349 | $0.0006 | Replace myopic best-fit with a "Hoffmann/dominant-bin" style rule: compute each bin's post-placem... |
| 31 | edit | not_better | 0.8423 | 0.9349 | $0.0008 | I'll switch from the purely myopic best-fit to a "best-fit with look-ahead residual matching": ro... |
| 32 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit was already strong, and the failures came from adding thresholds/reservations. The one c... |
| 33 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the rule with a randomized-threshold "best-fit with probabilistic tie-breaking": com... |
| 34 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace pure best-fit with a class-aware hybrid: best-fit normally, but when an item is smal... |
| 35 | edit | not_better | 0.8297 | 0.9349 | $0.0005 | I'll replace the myopic best-fit with "best-fit decreasing-like" using a small stateful upper-qua... |
| 36 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace the myopic best-fit with a "least-loaded-fit" variant that prefers the bin where the... |
| 37 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace the myopic best-fit with a "best-fit plus selective first-fit fallback": use best-fi... |
| 38 | edit | not_better | 0.8421 | 0.9349 | $0.0008 | Implement a proper class-based packing heuristic (like the Harmonic/Modified Harmonic family): pa... |
| 39 | edit | not_better | 0.9238 | 0.9349 | $0.0006 | I will try "best fit with an aging/round-robin penalty that protects a small number of never-used... |
| 40 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a stateful "best-fit with a small number of size-class-specific reserved bins" usi... |
| 41 | edit | not_better | 0.9336 | 0.9349 | $0.0005 | I'll replace pure best-fit with a bounded "best-fit + occasional worst-fit" rule that uses a dete... |
| 42 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | Best-fit is already near-optimal for this IID Weibull stream. I'll refine it slightly by breaking... |
| 43 | edit | not_better | 0.9343 | 0.9349 | $0.0006 | I'll implement a best-fit rule that, among bins whose resulting residual is within a tiny window ... |
| 44 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a stateful "best-fit with occasional deliberate suboptimal placement to consolidat... |
| 45 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a compact lookup-table rule learned for the Weibull(≈40) item distribution: derive... |
| 46 | edit | not_better | 0.7129 | 0.9349 | $0.0008 | I'll add a stateful "dual-bin" tweak to best-fit: when the arriving item is small and its best-fi... |
| 47 | edit | not_better | 0.8812 | 0.9349 | $0.0006 | Best-fit wastes bins on slivers; I'll switch to a stateful "closed-bin-aware best-fit" that track... |
| 48 | edit | not_better | 0.9323 | 0.9349 | $0.0006 | I'll keep best-fit as the primary rule but break ties and near-ties using a stateful harmonic tar... |
| 49 | edit | not_better | 0.8228 | 0.9349 | $0.0006 | Replace plain best-fit with a two-stage rule: compute each bin's resulting residual, and among bi... |
| 50 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll try a known-strong online heuristic that often beats best-fit: "Best Fit with a cap" is hard... |
| 51 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace plain best-fit with a randomized-restart style approach using a deterministic pseudo... |
| 52 | edit | not_better | 0.9349 | 0.9349 | $0.0017 | I'll perturb best-fit with a small value-function bonus: among bins, prefer the one whose resulti... |
| 53 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Use a stateful harmonic-style rule: keep an online estimate of the item-size distribution and, in... |
| 54 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll switch from pure best-fit to a stateful "best-fit with a small-item consolidation penalty": ... |
| 55 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Best-fit wastes capacity when it drops items into very full bins leaving tiny slivers. I will rep... |
| 56 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | In online bin packing, a well-known improvement over best-fit is to avoid leaving tiny slivers th... |
| 57 | edit | not_better | 0.4685 | 0.9349 | $0.0007 | I'll switch to a stateful "Best Fit Decreasing-like" threshold rule: use best-fit normally but wh... |
| 58 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace tie-break-heavy best-fit variants with a stateful rule that scores bins using the "best f... |
| 59 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | Best-fit is near-optimal but ties on residual waste. I'll implement the classic "Best Fit Decreas... |
| 60 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit usually wins but wastes capacity when it leaves unusable slivers; I'll add a small, risk... |
| 61 | edit | not_better | 0.9349 | 0.9349 | $0.0008 | Replace pure best-fit with a harmonic-style rule: classify the item by its size into a bucket, an... |
| 62 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll implement a proper online bin-packing improvement: a stateful variant of Best-Fit that occas... |
| 63 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch from raw best-fit to a "best-fit with a tie-break that avoids tiny unusable slivers" ... |
| 64 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "Best-Fit with sub-1% sliver avoidance plus fresh-bin preference onl... |
| 65 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a "best-fit among bins that won't strand a sliver" rule: compute the r... |
| 66 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll replace best-fit with a "Worst-Fit Decreasing"-style aging scheme: keep the classic best-fit... |
| 67 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a hybrid: maintain Best-Fit as the primary rule but when the best... |
| 68 | edit | not_better | 0.9137 | 0.9349 | $0.0006 | Replace pure best-fit with a "capped best-fit" rule that targets each item to a bin whose residua... |
| 69 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll replace pure best-fit with a size-class harmonic-style rule: classify each item into a bucke... |
| 70 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll try a "best-fit with a small lookahead-free perturbation": keep best-fit as the primary scor... |
| 71 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is already very strong for this distribution; the main gains come from the first-fit beh... |
| 72 | edit | not_better | 0.7534 | 0.9349 | $0.0005 | Shift from pure best-fit to a two-pass mix per item: keep best-fit (tightest residual) as primary... |
| 73 | edit | not_better | 0.7050 | 0.9349 | $0.0006 | I'll switch from pure best-fit to a rule that exploits a stronger understanding of this specific ... |
| 74 | edit | not_better | 0.7534 | 0.9349 | $0.0005 | I'll replace pure best-fit with a rule that caps the tightness: prefer bins whose post-placement ... |
| 75 | edit | not_better | 0.9102 | 0.9349 | $0.0007 | I'll replace pure best-fit with a rule based on the classic "Harmonic" bin-packing idea adapted o... |
| 76 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Replace pure best-fit with a best-fit + "reserved pairing" hybrid: prefer placing an item into an... |
| 77 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Since pure best-fit already dominates, the only lever left is which fresh/unused bin gets opened ... |
| 78 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit currently loses because its tie-break on unused bins (all residual 100) always opens the... |
| 79 | edit | not_better | 0.9349 | 0.9349 | $0.0006 | I'll switch to a size-class / harmonic-style rule: map each item to a class threshold, prefer bin... |
| 80 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll add a learned size-class policy: precompute from the Weibull(size≈40) shape, but instead of ... |
| 81 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement a "sum-of-squares / greedy pairing" rule: when the item and the bin's current cont... |
| 82 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit leaves tiny slivers when an item lands in a bin whose residual is just below the item si... |
| 83 | edit | not_better | 0.9349 | 0.9349 | $0.0004 | I'll implement a scale-invariant "best fit decreasing"-style rule that, after placing the item, s... |
| 84 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | Best-fit is already near-optimal on this distribution; the remaining loss comes from how ties amo... |
| 85 | edit | not_better | 0.9349 | 0.9349 | $0.0005 | I'll implement the classic "best fit with a lookahead-style dual-bin pairing" idea: keep exact be... |
| 86 | edit | improved | 0.9351 | 0.9351 | $0.0007 | I'll implement the classic "Almost Worst Fit / Best Fit with reserved space" style rule based on ... |
| 87 | edit | not_better | 0.9349 | 0.9351 | $0.0011 | I'll replace the mean-band heuristic with a proper size-class (harmonic-style) rule: partition it... |
| 88 | edit | not_better | 0.9351 | 0.9351 | $0.0007 | I'll implement a refined best-fit rule: primary score is tightness (smallest residual), but bins ... |
| 89 | edit | not_better | 0.8333 | 0.9351 | $0.0010 | I'll replace the heuristic band-based scoring with a learned "residual value" model: keep state o... |
| 90 | edit | not_better | 0.9349 | 0.9351 | $0.0008 | I'll keep the tightest-fit base but replace the ad-hoc band bonuses with a principled "residual q... |
| 91 | edit | not_better | 0.9351 | 0.9351 | $0.0008 | I'll add a small learned "residual value" table: estimate the empirical item-size CDF from past i... |
| 92 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace best-fit's tightness ordering with a size-class aware rule: keep tightest-fit as the... |
| 93 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Replace the ad-hoc band/sliver bonuses with a robust "best fit decreasing-like" rule that also in... |
| 94 | edit | not_better | 0.9347 | 0.9351 | $0.0007 | The current rule's main loss likely comes from a hard penalty structure that misfires; I'll simpl... |
| 95 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll reframe the rule as a "dual bin packing"-style score: since items have mean ~40 and capacity... |
| 96 | edit | not_better | 0.9351 | 0.9351 | $0.0008 | I'll add a mild "second-best-fit" bias: when a bin's post-placement residual is close to the item... |
| 97 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll switch from posting a per-bin score to a "best-fit with matching-residual look-ahead": score... |
| 98 | edit | not_better | 0.9349 | 0.9351 | $0.0008 |  |
| 99 | edit | not_better | 0.9349 | 0.9351 | $0.0009 | Simplify the scoring to a cleaner best-fit with a strong single reusability rule: prefer the tigh... |
| 100 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the ad-hoc band/sliver bonuses with a clean best-fit in which the only deviation fro... |
| 101 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Reinterpret the task: with a Weibull(mean 40) distribution, many items are small, so optimal pack... |
| 102 | edit | not_better | 0.9349 | 0.9351 | $0.0004 | I'll test the classic "best fit decreasing-like" but with a small tie-breaking twist: score purel... |
| 103 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | The pure best-fit variant scored worse, so I'll return to the strong reusable-residual bonus but ... |
| 104 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Replace the soft band/sliver bonuses with a single decisive rule: strongly prefer placing the ite... |
| 105 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll keep the good tightest-fit base but replace the weak band bonuses with a sharper, better-tar... |
| 106 | edit | not_better | 0.4481 | 0.9351 | $0.0006 | I'll switch the primary rule to "worst fit that still leaves a reusable residual": among bins a t... |
| 107 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the noisy soft bonuses with a cleaner formulation: keep the tightest-fit base (small... |
| 108 | edit | not_better | 0.9351 | 0.9351 | $0.0007 | I'll add a state-tracked "completion" bonus that rewards leaving a residual exactly equal to the ... |
| 109 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | The current rule's learned band bonuses are too weak and fuzzy; I'll replace them with a sharper,... |
| 110 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll simplify and strengthen the rule: keep strict tightest-fit as the base but increase the pena... |
| 111 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the fuzzy band bonuses with a targeted "perfect complement" bonus derived from the e... |
| 112 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the fuzzy band bonuses with a principled rule based on the Weibull-like distribution... |
| 113 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Recent attempts to add distribution-driven bonuses all tie or lose to plain best-fit, so I'll ins... |
| 114 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | All prior variants either tied or lost to plain best-fit, so I'll try the opposite direction used... |
| 115 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Recent variants show plain best-fit dominates; I'll switch to a distribution-aware best-fit that ... |
| 116 | edit | not_better | 0.9351 | 0.9351 | $0.0005 | I'll keep strict best-fit (dominant tightest residual) but add a strong exact-completion bonus fo... |
| 117 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | Replace the heuristic bonuses with the classic, well-proven "best fit decreasing" emulation via a... |
| 118 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Replace the noisy empirical-band heuristics with a principled score: strict best-fit (dominant ti... |
| 119 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll use the well-known "best fit with sum-of-squares" scoring used in harmonic/class-based bin p... |
| 120 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I will change the tie-breaking to use a "best-fit-decreasing-like" residual-class score: keep tig... |
| 121 | edit | not_better | 0.9340 | 0.9351 | $0.0007 | Make the exact-fit bonus dominant and deterministic by preferring residuals that equal common sma... |
| 122 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the fuzzy band heuristics with a principled "best fit" base plus a deterministic bon... |
| 123 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the noisy empirical band with a theoretically grounded "best fit" that explicitly mi... |
| 124 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the fuzzy empirical-band heuristic with a closer-to-optimal "sum of squares" score: ... |
| 125 | edit | not_better | 0.8536 | 0.9351 | $0.0011 | Replace the fuzzy empirical-band heuristic with a deterministic harmonic-class score (like Harmon... |
| 126 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll switch from the fuzzy empirical-band heuristic to a strong best-fit-decreasing-style rule: d... |
| 127 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I will replace the fuzzy empirical-band heuristics with a principled "best fit with a sum-of-squa... |
| 128 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Replace the fuzzy empirical-band heuristics with a single principled best-fit score whose sole se... |
| 129 | edit | not_better | 0.9351 | 0.9351 | $0.0008 | Add a "perfect-pack" bonus that, for the current item, checks whether the bin's residual after pl... |
| 130 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll replace the fuzzy band heuristic with a principled "least waste into reusable bins" rule emp... |
| 131 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I will keep the strong tightest-fit base (which dominates) but make the secondary tie-break rewar... |
| 132 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | Simplify to a near-pure best-fit: dominant tightest-fit score with a very small, robust tie-break... |
| 133 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the heuristic band terms with a "fill-the-gap" rule: dominant tightest-fit, but a la... |
| 134 | edit | not_better | 0.9351 | 0.9351 | $0.0007 | The fuzzy band heuristics add noise; I'll replace them with a clean "best fit with reusable-resid... |
| 135 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I will replace the heuristic scoring with a classic Best-Fit rule strengthened by a two-bin "comp... |
| 136 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll switch from a heuristic blend to a principled "least future waste" rule: place the item in t... |
| 137 | edit | invalid | 0.0000 | 0.9351 | $0.0006 | The current rule is essentially Best-Fit with noisy tie-breakers, and recent attempts show these ... |
| 138 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Remove all fuzzy band bonuses (which only add noise) and use pure Best-Fit: place the item in the... |
| 139 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the noisy single-item band heuristics with a "best-fit-decreasing-style" rule that a... |
| 140 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | This task is essentially online bin packing from a fixed distribution, where a classic "Best-Fit"... |
| 141 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll replace the noisy single-item heuristics with a Best-Fit rule augmented by a strong "exact c... |
| 142 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | I'll switch to a lower-variance strategy: pure Best-Fit on the residual (tightest remaining capac... |
| 143 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Replace the noisy, history-dependent band bonuses with a pure Best-Fit rule: rank bins by smalles... |
| 144 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | The all-heuristic boilerplate is scoring below plain best-fit. I'll replace it with a clean, low-... |
| 145 | edit | not_better | 0.9349 | 0.9351 | $0.0006 | I'll implement a Best-Fit rule augmented with a "residual complement" bonus: after placement, rew... |
| 146 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Replace the noisy history-based band bonuses with a pure Best-Fit rule: rank by smallest residual... |
| 147 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the heuristic scoring with the classic "Worst-Fit Decreasing-style" intuition revers... |
| 148 | edit | not_better | 0.9349 | 0.9351 | $0.0007 | I'll replace the rule with pure Best-Fit under a signed-linear score that gives a decisive bonus ... |
| 149 | edit | not_better | 0.9349 | 0.9351 | $0.0005 | Replace the noisy best-fit variants with a classic best-fit that also accepts items into bins whe... |
| 150 | edit | not_better | 0.4064 | 0.9351 | $0.0005 | I'll implement the classic "Sum of Squares" (SS) heuristic, a theoretically-grounded rule that pr... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,56 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit biased so that the residual left behind is likely reusable."""
 import numpy as np
+
+_state = {"sizes": []}
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    sizes = _state["sizes"]
+    sizes.append(int(item))
+    if len(sizes) > 2000:
+        del sizes[:1000]
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    # Estimate the typical item size band from observed history.
+    if len(sizes) >= 20:
+        arr = np.array(sizes, dtype=np.float64)
+        mu = arr.mean()
+        sd = arr.std()
+    else:
+        mu = 40.0
+        sd = 20.0
+
+    tmp = int(mu)
+    if tmp < 1:
+        tmp = 1
+    if tmp > 100:
+        tmp = 100
+    band = tmp
+    # Tolerance around the typical size: residual in [band - tol, band + tol]
+    tol = int(0.25 * band) + 1
+
+    resid = bins - item  # remaining capacity after placing (>= 0 for shown bins)
+
+    # Base: prefer tightest fit (smallest residual).
+    score = -(resid.astype(np.float64))
+
+    # Bonus if residual is a "useful" leftover: big enough to hold a typical item
+    # but not so big we waste it by fragmenting (i.e., close to a typical size).
+    useful = (resid >= 0) & (resid <= 100)
+    near_band = useful & (np.abs(resid - band) <= tol)
+    score += np.where(near_band, 6.0, 0.0)
+
+    # Smaller bonus if residual is at least one typical item (reusable later).
+    reusable = useful & (resid >= band - tol) & (resid <= 100)
+    score += np.where(reusable, 1.0, 0.0)
+
+    # Mild penalty for leaving slivers too small for anything meaningful.
+    sliver = useful & (resid > 0) & (resid < max(1, band - tol))
+    score -= np.where(sliver, 1.0, 0.0)
+
+    # Strong preference not to open a fresh bin when a valid partial fill exists.
+    empty = bins == 100
+    score -= np.where(empty, 0.5, 0.0)
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (32 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 9 | `sizes = _state['sizes']` | -0.9351 | essential: the program fails or turns invalid without it |
| 15 | `if len(sizes) >= 20: ...` | -0.9351 | essential: the program fails or turns invalid without it |
| 16 | `arr = np.array(sizes, dtype=np.float64)` | -0.9351 | essential: the program fails or turns invalid without it |
| 17 | `mu = arr.mean()` | -0.9351 | essential: the program fails or turns invalid without it |
| 20 | `mu = 40.0` | -0.9351 | essential: the program fails or turns invalid without it |
| 23 | `tmp = int(mu)` | -0.9351 | essential: the program fails or turns invalid without it |
| 28 | `band = tmp` | -0.9351 | essential: the program fails or turns invalid without it |
| 30 | `tol = int(0.25 * band) + 1` | -0.9351 | essential: the program fails or turns invalid without it |
| 32 | `resid = bins - item` | -0.9351 | essential: the program fails or turns invalid without it |
| 32 | `term + bins` | -0.9351 | essential: the program fails or turns invalid without it |
| 35 | `score = -resid.astype(np.float64)` | -0.9351 | essential: the program fails or turns invalid without it |
| 39 | `useful = (resid >= 0) & (resid <= 100)` | -0.9351 | essential: the program fails or turns invalid without it |
| 40 | `near_band = useful & (np.abs(resid - band) <= tol)` | -0.9351 | essential: the program fails or turns invalid without it |
| 44 | `reusable = useful & (resid >= band - tol) & (resid <= 100)` | -0.9351 | essential: the program fails or turns invalid without it |
| 48 | `sliver = useful & (resid > 0) & (resid < max(1, band - tol))` | -0.9351 | essential: the program fails or turns invalid without it |
| 52 | `empty = bins == 100` | -0.9351 | essential: the program fails or turns invalid without it |
| 32 | `term - item` | -0.0006 | no effect alone |
| 10 | `sizes.append(int(item))` | -0.0002 | no effect alone |
| 30 | `term + int(0.25 * band)` | -0.0002 | no effect alone |
| 30 | `term + 1` | -0.0002 | no effect alone |
| 53 | `score -= np.where(empty, 0.5, 0.0)` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 11: `if len(sizes) > 2000: ...`
- line 12: `del sizes[:1000]`
- line 18: `sd = arr.std()`
- line 21: `sd = 20.0`
- line 24: `if tmp < 1: ...`
- line 25: `tmp = 1`
- line 26: `if tmp > 100: ...`
- line 27: `tmp = 100`
- line 41: `score += np.where(near_band, 6.0, 0.0)`
- line 45: `score += np.where(reusable, 1.0, 0.0)`
- line 49: `score -= np.where(sliver, 1.0, 0.0)`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9351 | 0.9625 |
| minimal (8 parts removed) | 0.9349 | 0.9634 |

Minimal program:

```python
"""Best fit biased so that the residual left behind is likely reusable."""
import numpy as np
_state = {'sizes': []}

def priority(item, bins):
    sizes = _state['sizes']
    sizes.append(int(item))
    if len(sizes) >= 20:
        arr = np.array(sizes, dtype=np.float64)
        mu = arr.mean()
    else:
        mu = 40.0
    tmp = int(mu)
    band = tmp
    tol = int(0.25 * band) + 1
    resid = bins - item
    score = -resid.astype(np.float64)
    useful = (resid >= 0) & (resid <= 100)
    near_band = useful & (np.abs(resid - band) <= tol)
    reusable = useful & (resid >= band - tol) & (resid <= 100)
    sliver = useful & (resid > 0) & (resid < max(1, band - tol))
    empty = bins == 100
    score -= np.where(empty, 0.5, 0.0)
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_c80 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 0
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_c80-s0   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `9f2bbd0772b0ec63759bdd119a5e2d9aa72eaa76`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_c80/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_c80/initial.py` `609927c5ea619a94`
- `problems/bp_sh_c80/problem.md` `190017a698e23cd8`
- `problems/bp_sh_c80/verify.py` `dc0d05d86db9dbf0`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
