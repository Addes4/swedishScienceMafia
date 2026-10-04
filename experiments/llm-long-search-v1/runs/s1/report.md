# Research loop report: bin_packing_online

| | |
|---|---|
| problem | `bin_packing_online` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2010 of a $0.75 hard cap, 300 calls, 677,983 tokens |
| wall time | search 1981 s, baselines 45 s, explain 43 s |
| stopped | max_iters (stopped_early) |
| evaluations | 301 (294 valid), 4 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9925 | 0.9918 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online/baselines/funsearch_weibull.py` |
| minimal program (ablation) | 0.9925 | 0.9918 | 4 parts removed |

Audit: public 0.9616 → 0.9925 (+0.0308), hidden 0.9604 → 0.9918 (+0.0314); public − hidden gap of the final program 0.0007.

Against the baselines: the final program's public score is below the best baseline (`funsearch_weibull`, 0.9925). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9233 | 0.9616 | $0.0004 | Add a small "almost-full bin" bias plus periodic smart measures. I'll switch to a hybrid of best-... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace pure best fit with a score that mixes best-fit tightness with a small bias toward bins wh... |
| 3 | edit | invalid | 0.0000 | 0.9616 | $0.0005 | Replace pure best-fit with a restarted harmonic-style ranking: for the current item size, prefer ... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll combine best-fit with a residual-aware rule: for each candidate bin, compute the residual af... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace pure best-fit with a "best-fit with harmonic-class grouping" rule: prefer the tighte... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | (no description) |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | The best available online bin-packing heuristic for this distribution should beat pure best-fit b... |
| 8 | edit | not_better | 0.9614 | 0.9616 | $0.0005 | Replace pure best-fit with best-fit plus a history-learned "perfect residual" bonus: keep an onli... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace pure best-fit with a "best-fit + smart-worst-fit-tie-break" strategy: score primaril... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a score that adds a small residual-quality bonus based on whether the ... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace pure best-fit with a "best-fit + tighter sliver avoidance" rule: primary score is ti... |
| 12 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from best-fit to a "best-fit with amortized item-size-aware residual penalty": instea... |
| 13 | edit | not_better | 0.9614 | 0.9616 | $0.0005 | I'll replace pure best-fit with a two-phase rule that leverages the bin array's fixed ordering to... |
| 14 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Pure best-fit ignores that an item nearly filling a bin is often better used later; I'll try a ra... |
| 15 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Try a tuned parametric score that blends best-fit tightness with a residual preference near a mid... |
| 16 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a size-class-aware "harmonic" score inspired by the observation that best-fit leav... |
| 17 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a probabilistic variant that breaks near-ties by randomly preferr... |
| 18 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a policy that first tries to complete an existing bin whose current fi... |
| 19 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a size-class "complement pairing" rule: among all bins the item f... |
| 20 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a hybrid that adds an online-learned blend: the item goes to the bin m... |
| 21 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the pure best-fit with a score that prefers the bin leaving a residual that is a "go... |
| 22 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I will replace pure best-fit with a "Best Fit with lookahead-free waste penalty" variant that use... |
| 23 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a score that exploits the item-size distribution: keep tightest-fit as... |
| 24 | edit | not_better | 0.9499 | 0.9616 | $0.0006 | I'll switch the primary criterion from smallest residual to a "future-utility" score: exact fills... |
| 25 | edit | not_better | 0.9614 | 0.9616 | $0.0006 | I'll switch from best-fit to a scaled/quantized first-fit-like policy that reserves space more ev... |
| 26 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a size-class-aware best fit that boosts bins whose residual after placing the item... |
| 27 | edit | not_better | 0.8992 | 0.9616 | $0.0006 | I'll replace pure best-fit with a harmonic-style rule: bins are bucketed by their remaining capac... |
| 28 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Implement the classic "best fit with a small bias toward leaving larger residuals reusable" by ad... |
| 29 | edit | not_better | 0.9402 | 0.9616 | $0.0005 | The classic improvement over pure best fit for Weibull-ish sizes is "best fit decreasing ordering... |
| 30 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll try a small refinement of pure best fit that specifically exploits the heavy-tailed (Weibull... |
| 31 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I will switch the ranking from pure best-fit to a smoothed "residual utility" score: primary is t... |
| 32 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a "best fit plus a bonus for bins that become exactly full or lea... |
| 33 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a "compatibility-aware best fit" that prefers tight fits but brea... |
| 34 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a rule based on the classic Sum-of-Squares / "utility" idea: score eac... |
| 35 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll implement the classic "harmonic/maximum-utilization" idea but tuned for heavy-tailed sizes: ... |
| 36 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a score that combines tight fitting with a value-function based o... |
| 37 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Recent attempts show local tweaks to best-fit do not help. I'll implement the classic "Sum of Squ... |
| 38 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a rule that also considers the global packing state: track a runn... |
| 39 | edit | invalid | 0.0000 | 0.9616 | $0.0005 | Replace best-fit with a two-regime rule: track a coarse histogram of past item sizes, and when th... |
| 40 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from best-fit to a "minimum waste plus double-bin/perfect-fill rescue" rule: among fe... |
| 41 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll test a fundamentally different rule: instead of pure best-fit, use a "dual feasible function... |
| 42 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add a tiny index-based tiebreaker to best-fit so that among bins with equal post-placement residu... |
| 43 | edit | not_better | 0.9501 | 0.9616 | $0.0005 | I'll add a "reserve the last bin" adaptation of Harmonic-style packing: track the number of bins ... |
| 44 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace pure best-fit with an "almost worst fit / best fit hybrid": strongly prefer placing an it... |
| 45 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Best-fit is near-optimal for this distribution, but a known improvement is to occasionally prefer... |
| 46 | edit | invalid | 0.0000 | 0.9616 | $0.0008 | I'll replace the static best-fit with an online learned model: maintain a probability histogram o... |
| 47 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Best-fit leaves many bins with small unusable residuals. I'll add a fallback: when the item fits ... |
| 48 | edit | not_better | 0.9614 | 0.9616 | $0.0004 | Implement "best fit decreasing-style pairing" online: prefer exact fits first, then among residua... |
| 49 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a rule that prefers exact fits, but among non-exact placements prefers... |
| 50 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch the tie-breaking and score shape: keep best-fit as the primary criterion but, among b... |
| 51 | edit | improved | 0.9621 | 0.9621 | $0.0005 | Replace pure best-fit with a score that still favors tight fits but adds a strong bonus for exact... |
| 52 | edit | not_better | 0.9621 | 0.9621 | $0.0006 | Add a stateful "exact-fit reservation" rule: track how many bins currently hold each residual (th... |
| 53 | edit | not_better | 0.9621 | 0.9621 | $0.0007 | Add lightweight state tracking a histogram of seen item sizes, and add a small bonus when the lef... |
| 54 | edit | not_better | 0.5269 | 0.9621 | $0.0008 | Replace the heuristic scoring with an online learned predictor: maintain a histogram of item size... |
| 55 | edit | not_better | 0.9549 | 0.9621 | $0.0007 | Replace the ad-hoc penalty with a proper expected-waste value function: maintain a stateful histo... |
| 56 | edit | not_better | 0.9616 | 0.9621 | $0.0005 | Keep the exact-fit bonus and best-fit ordering, but replace the arbitrary "tiny residual" penalty... |
| 57 | edit | improved | 0.9623 | 0.9623 | $0.0006 | Add a lookahead-aware "leftover usability" term using a stateful histogram of seen item sizes: re... |
| 58 | edit | not_better | 0.9619 | 0.9623 | $0.0006 | Replace the concave mean-peaked bonus with a sharper "reusability" term: estimate the empirical i... |
| 59 | edit | not_better | 0.9614 | 0.9623 | $0.0007 | Replace the concave mean-peaked residual bonus with a smooth target-residual preference: instead ... |
| 60 | edit | not_better | 0.9623 | 0.9623 | $0.0007 | I will replace the ad-hoc residual shaping with a best-fit rule augmented by a strong exact-fit p... |
| 61 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | Simplify and regularize: use a dominant best-fit term plus a strong exact-fit bonus, and replace ... |
| 62 | edit | not_better | 0.9623 | 0.9623 | $0.0007 | Add a scale-aware exact-fit-adjacent lookahead: instead of a fixed bonus/penalty pattern, compute... |
| 63 | edit | not_better | 0.9612 | 0.9623 | $0.0007 | Add a small stateful "energy" term that biases toward bins whose resulting residual matches the m... |
| 64 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace the fixed 1000 exact-fit bonus and ad-hoc residual penalties with a principled two-part r... |
| 65 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace the heuristic residual shaping with a dynamic-programming-style estimate: for each candid... |
| 66 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the noisy histogram-based residual shaping with a clean, well-known online rule: Bes... |
| 67 | edit | not_better | 0.9619 | 0.9623 | $0.0006 | I'll add a stateful "pairing" term that prefers placing an item into a bin whose current residual... |
| 68 | edit | not_better | 0.9609 | 0.9623 | $0.0006 | Replace the noisy bonus/penalty shaping with a pure best-fit core (dominant), plus a strong exact... |
| 69 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | Add a size-aware pairing term that favors placing an item into a bin where the pre-placement load... |
| 70 | edit | not_better | 0.9619 | 0.9623 | $0.0007 | I'll add a second-order "future pair" term: after tentatively placing the item, estimate whether ... |
| 71 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I will simplify to a pure best-fit rule with only a strong exact-fit bonus, removing all residual... |
| 72 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I will replace the ad-hoc geometric residual shaping with a principled "future-fit probability" m... |
| 73 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | Add a stateful "damage-minimizing" tie-breaker: keep the dominant best-fit with strong exact-fit ... |
| 74 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the fixed geometric shaping with an adaptive "residual reuse probability" model: kee... |
| 75 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I will replace the pure best-fit-with-exact-fit-bonus core by an online learned "residual desirab... |
| 76 | edit | not_better | 0.9619 | 0.9623 | $0.0007 | I'll use a distribution-aware expected-waste model: instead of ad-hoc residual shaping, compute f... |
| 77 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace the ad-hoc residual shaping with a principled harmonic/expectation score: keep best-fit d... |
| 78 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the ad-hoc residual shaping with a simple, well-established heuristic: best-fit with... |
| 79 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll adopt a hybrid of best-fit and worst-fit: keep best-fit dominant with an exact-fit bonus, bu... |
| 80 | edit | not_better | 0.9619 | 0.9623 | $0.0007 | I'll add a stateful "sum-of-squares" (energy) tie-breaker: keep best-fit dominant with the exact-... |
| 81 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll replace the reshaping with pure best-fit (tightest residual, strong exact-fit preference) as... |
| 82 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I will replace the heuristic "small residual" penalty with a learned, distribution-aware expected... |
| 83 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll switch from scoring by residual to a worst-fit-style rank that maximizes remaining space onl... |
| 84 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll make the exact-fit bonus dominant at a level that clearly outweighs any residual difference,... |
| 85 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace the direct-residual scoring with a "best fit decreasing with future-fit awareness" rule: ... |
| 86 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the ad-hoc residual shaping with a cleaner "best-fit + usable-gap bonus" that is les... |
| 87 | edit | invalid | 0.0000 | 0.9623 | $0.0006 | I'll keep exact-fit preference but make the ranking purely lexicographic by residual (best-fit) a... |
| 88 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll use a sum-of-two-criteria approach: keep best-fit dominant, add a modest exact-fit bonus, an... |
| 89 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the ad-hoc shaping with a strict lexicographic best-fit: the only additional term is... |
| 90 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the heuristic scoring with a proper "best fit decreasing"-style rule augmented by a ... |
| 91 | edit | not_better | 0.5228 | 0.9623 | $0.0007 | I'll replace the heuristic scoring with a proper distribution-aware "best fit with one-step looka... |
| 92 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll make the scoring a pure best-fit rule with a dominant exact-fit bonus and remove the residua... |
| 93 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | The current scoring already dominates with best-fit plus exact-fit bonus; the risk is the small-r... |
| 94 | edit | not_better | 0.9614 | 0.9623 | $0.0006 | I'll add a "sum-of-item-sizes" tie-break so that among bins with the same residual, the one whose... |
| 95 | edit | not_better | 0.9612 | 0.9623 | $0.0006 | I will replace the smooth bonus with a dominant best-fit ordering plus a sharper, distribution-aw... |
| 96 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | Replace the heuristic shaping with a strict best-fit rule plus a dominant exact-fit bonus and a m... |
| 97 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll strengthen the reuse term: instead of a small linear bonus capped at the running mean item s... |
| 98 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I'll replace the weak reuse/pairing heuristics with a proper distribution-aware "best fit with on... |
| 99 | edit | not_better | 0.9595 | 0.9623 | $0.0005 | I'll keep the proven best-fit with exact-fit bonus and add a "perfect pair" lookahead: reward bin... |
| 100 | edit | not_better | 0.9616 | 0.9623 | $0.0008 | I'll replace the weak shaping with a proper distribution-aware one-step lookahead: for each bin c... |
| 101 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll replace the heuristic shaping with best-fit plus a strong exact-fit bonus, and add a targete... |
| 102 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I will replace the heuristic scoring with a strict best-fit rule (maximize used capacity, i.e. mi... |
| 103 | edit | not_better | 0.9616 | 0.9623 | $0.0009 | Replace the heuristic with a distribution-based one-step lookahead that estimates, for each candi... |
| 104 | edit | not_better | 0.9614 | 0.9623 | $0.0021 | Keep the proven "best fit + exact-fit bonus + leave-at-least-one-item residual" structure, but ad... |
| 105 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll simplify to a pure best-fit with a dominant exact-fit bonus and remove the noise-adding shap... |
| 106 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll add a moderate bonus for placing an item into a bin whose residual after placement matches a... |
| 107 | edit | not_better | 0.9621 | 0.9623 | $0.0006 | I'll implement a score that rewards the bin whose resulting residual is exactly a size that appea... |
| 108 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | Replace the weak residual shaping with a symmetry-aware best fit: still dominate with exact-fit b... |
| 109 | edit | not_better | 0.9614 | 0.9623 | $0.0006 | I'll replace the pure best-fit rule with an empirical one-step "expected waste" model: estimate t... |
| 110 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll keep the proven exact-fit and best-fit core but replace the residual shaping with a lookahea... |
| 111 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll add a strong bonus for the resulting residual being exactly an item size that has recently a... |
| 112 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll switch from pure best-fit to a harmonic-style rule that minimizes the expected number of bin... |
| 113 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I will add a small "almost-fit" penalty/bonus asymmetry tuned to the empirical distribution: rewa... |
| 114 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll replace the ad-hoc residual shaping with a principled "best fit decreasing"-style score, but... |
| 115 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | I'll use a "least-loaded residual that still fits nicely" hybrid: keep exact-fit dominance and be... |
| 116 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | Replace the ad-hoc residual shaping with a direct "best fit decreasing"-style scoring that is gro... |
| 117 | edit | not_better | 0.9616 | 0.9623 | $0.0005 | I'll replace the hand-tuned residual shaping with a learned-style scoring based directly on best-... |
| 118 | edit | not_better | 0.9616 | 0.9623 | $0.0006 | Strip everything down to strict pure best-fit with exact-fit dominance (exact fill = 0 residual s... |
| 119 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll implement a principled expected-waste rule: score each bin by the expected number of future ... |
| 120 | edit | not_better | 0.9616 | 0.9623 | $0.0007 | I'll reverse the residual-shaping intuition by adding a small penalty for residuals that are too ... |
| 121 | edit | not_better | 0.5224 | 0.9623 | $0.0006 | I'll switch from best-fit to a "worst-fit among fitting, with exact-fit dominance" strategy: sinc... |
| 122 | edit | improved | 0.9912 | 0.9912 | $0.0006 | I'll keep exact-fit dominance but replace pure best-fit with a scoring that targets a fixed "good... |
| 123 | edit | not_better | 0.7531 | 0.9912 | $0.0006 | I'll refine the residual-target objective so exact fits stay dominant, but instead of targeting t... |
| 124 | edit | improved | 0.9925 | 0.9925 | $0.0007 | I'll replace the single fixed target residual with a small set of target residuals derived from t... |
| 125 | edit | not_better | 0.9903 | 0.9925 | $0.0007 | I'll make exact-fill dominance absolute (a very large constant) and replace the distance-to-neare... |
| 126 | edit | not_better | 0.9861 | 0.9925 | $0.0007 | I'll replace the min-distance-to-nearest-seen-size objective with a probabilistic "match" score: ... |
| 127 | edit | not_better | 0.9925 | 0.9925 | $0.0007 | I'll cap the fallback term so it only acts as a mild tie-breaker, and add a small bonus for resid... |
| 128 | edit | not_better | 0.9848 | 0.9925 | $0.0007 | The current min-distance-to-nearest-seen-size lookup is noisy because "near" a seen size is not t... |
| 129 | edit | not_better | 0.9853 | 0.9925 | $0.0007 | Replace the min-distance-to-nearest-seen-size objective with a recency-weighted histogram lookup:... |
| 130 | edit | not_better | 0.9682 | 0.9925 | $0.0007 | The current score uses min-distance to any seen size in a noisy way; I'll instead score each bin ... |
| 131 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | I'll simplify to a robust "best fit" rule (smallest residual wins, exact fills first) since the e... |
| 132 | edit | not_better | 0.9640 | 0.9925 | $0.0009 | I'll keep the winning min-distance-to-nearest-seen-size term but weight the distance by the frequ... |
| 133 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | Add a "perfect-completion" term that scores a bin higher when the residual it would leave can be ... |
| 134 | edit | not_better | 0.9654 | 0.9925 | $0.0007 | The current min-distance lookup treats a residual of 1 as having distance 0 from many seen sizes ... |
| 135 | edit | not_better | 0.9619 | 0.9925 | $0.0007 | The min-distance-to-nearest-seen-size lookup is fragile and noisy; I'll replace it with a proper ... |
| 136 | edit | not_better | 0.9875 | 0.9925 | $0.0008 | I'll refine the current winning min-distance objective so that matched residuals whose seen-size ... |
| 137 | edit | not_better | 0.9626 | 0.9925 | $0.0007 | I will replace the fragile min-distance-to-nearest-seen-size lookup with a distributional "expect... |
| 138 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I'll keep the exact same winning min-distance-to-nearest-seen-size objective, but replace the arb... |
| 139 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | I'll keep the winning min-distance-to-nearest-seen-size term, but make the exact-fill dominance m... |
| 140 | edit | not_better | 0.9547 | 0.9925 | $0.0007 | I'll replace the arbitrary -0.05*\|res-mean\| fallback with a small monotone best-fit tie-breaker... |
| 141 | edit | not_better | 0.9822 | 0.9925 | $0.0008 | I'll replace the fragile O(101×K) min-distance lookup with an O(1)-per-bin vectorized "expected f... |
| 142 | edit | not_better | 0.9824 | 0.9925 | $0.0007 | The current min-distance lookup is expensive and noisy; I'll simplify to a robust scoring rule: s... |
| 143 | edit | not_better | 0.9925 | 0.9925 | $0.0007 | I'll keep the winning min-distance-to-nearest-seen-size objective but replace the recency-weighte... |
| 144 | edit | not_better | 0.9742 | 0.9925 | $0.0008 | I'll replace the noisy per-bin min-distance-to-seen-size lookup with a smooth, stable "residual q... |
| 145 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll simplify and stabilize the scoring: replace the fragile recency-weighted min-distance-to-nea... |
| 146 | edit | not_better | 0.9893 | 0.9925 | $0.0007 | Replace the fragile recency-weighted "seen" set with a value-function heuristic: since items have... |
| 147 | edit | not_better | 0.9910 | 0.9925 | $0.0008 | Blend the winning min-distance-to-nearest-seen-size objective with the full running histogram's p... |
| 148 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | Add a penalty for residuals larger than the maximum observed item size (since such residuals cann... |
| 149 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | Replace the noisy per-item recency "seen" set (last-hundreds of items) with a stable, adaptive su... |
| 150 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | Replace the noisy recency-weighted "nearest seen size" lookup with a stable, stationary-distribut... |
| 151 | edit | not_better | 0.9637 | 0.9925 | $0.0008 | Replace the fragile recency-based "nearest seen size" surrogate with a stable, distribution-aware... |
| 152 | edit | not_better | 0.9807 | 0.9925 | $0.0007 | I'll replace the noisy min-distance-to-nearest-recently-seen-size lookup with a direct "best-fit"... |
| 153 | edit | not_better | 0.9751 | 0.9925 | $0.0008 | Add a small monotone tie-breaker that prefers the smallest positive residual (classic best-fit) o... |
| 154 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | Add a small "best-fit"-style monotone tie-breaker that prefers the smallest positive residual, bu... |
| 155 | edit | not_better | 0.9900 | 0.9925 | $0.0007 | I'll replace the noisy recency-decay "seen" set with a stable stationary-distribution surrogate: ... |
| 156 | edit | not_better | 0.9905 | 0.9925 | $0.0007 | I'll replace the fragile "nearest recently-seen size" surrogate (which uses a decaying noisy set)... |
| 157 | edit | not_better | 0.9910 | 0.9925 | $0.0008 | I will replace the fragile recency-decay lookup with a smoothed stationary-distribution surrogate... |
| 158 | edit | not_better | 0.9614 | 0.9925 | $0.0007 | Replace the noisy recency-decay "nearest seen size" with a distribution-aware surrogate that uses... |
| 159 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | Keep the proven nearest-seen-size scoring but make the recency set symmetric and more stable: use... |
| 160 | edit | not_better | 0.9908 | 0.9925 | $0.0008 | Reduce the recency decay to 0.998 so the "recently-seen size" set adapts faster and better reflec... |
| 161 | edit | not_better | 0.9621 | 0.9925 | $0.0008 | I'll soften the exact-fill bonus from a binary 1000-point spike into a smooth, monotone function ... |
| 162 | edit | not_better | 0.9754 | 0.9925 | $0.0007 | Replace the decaying presence array (which accumulates noise) with a stable running histogram pro... |
| 163 | edit | not_better | 0.9612 | 0.9925 | $0.0008 | Replace the noisy recency-decay distance-to-nearest-seen-size lookup with a stable stationary-dis... |
| 164 | edit | not_better | 0.9925 | 0.9925 | $0.0007 | Replace the noisy recency-decay nearest-seen-size lookup with a principled "future-fillability" s... |
| 165 | edit | not_better | 0.9682 | 0.9925 | $0.0008 | I'll replace the recency-weighted "nearest seen size" heuristic with a score based on the running... |
| 166 | edit | not_better | 0.9903 | 0.9925 | $0.0007 | I'll keep the proven exact-fill dominance but replace the noisy recency-decay distance lookup wit... |
| 167 | edit | not_better | 0.9915 | 0.9925 | $0.0008 | Add a standard Best-Fit tie-break: among residuals with the same reusable-residual score, prefer ... |
| 168 | edit | not_better | 0.9718 | 0.9925 | $0.0007 | Avoid the O(len(bins)*101) distance-matrix computation each call (which wastes time and adds nois... |
| 169 | edit | not_better | 0.9737 | 0.9925 | $0.0007 | I'll keep the exact-fill dominance but make the reusable-residual signal much sharper and cheaper... |
| 170 | edit | not_better | 0.9915 | 0.9925 | $0.0007 | I will keep the proven exact-fill dominance and the reusable-residual nearest-seen-size term, but... |
| 171 | edit | not_better | 0.9915 | 0.9925 | $0.0008 | The recency-decay presence array with 0.999 multiplier never forgets fast enough and its "nearest... |
| 172 | edit | not_better | 0.9903 | 0.9925 | $0.0008 | I'll keep the proven exact-fill dominance and the reusable-residual nearest-seen-size term, but I... |
| 173 | edit | not_better | 0.9922 | 0.9925 | $0.0008 | I'll replace the expensive O(101·bins) distance-matrix recomputation with a cached vector and, mo... |
| 174 | edit | not_better | 0.9861 | 0.9925 | $0.0007 | Replace the noisy distance-to-nearest-recently-seen-size signal with a stationary probability-wei... |
| 175 | edit | not_better | 0.9925 | 0.9925 | $0.0007 | I'll keep the proven exact-fill dominance and the reusable-residual nearest-seen-size term, but I... |
| 176 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | I'll make the reusable-residual signal secondary to true best-fit: strongly prefer exact fills, t... |
| 177 | edit | not_better | 0.9614 | 0.9925 | $0.0006 | Replace the noisy recency-decay "reusable residual" signal with a best-fit-plus-perfect-pack tie-... |
| 178 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | I'll keep the proven exact-fill dominance and reusable-residual nearest-seen-size term, but repla... |
| 179 | edit | not_better | 0.9903 | 0.9925 | $0.0008 | I'll keep the exact-fill dominance and nearest-common-residual structure but replace the crude "n... |
| 180 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | The prior best used a recency-decay `_seen` array; I'll replace the fragile "nearest recently-see... |
| 181 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | I'll add a periodic "shuffle-to-front" style tie-break that prefers bins whose residual equals a ... |
| 182 | edit | not_better | 0.9912 | 0.9925 | $0.0008 | I will keep the current best structure (exact-fill dominance plus distance-to-nearest-recently-se... |
| 183 | edit | not_better | 0.9925 | 0.9925 | $0.0009 | I'll add a "generalized fill" signal: for each candidate residual r, compute the probability that... |
| 184 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | I'll replace the fragile recency-decay "_seen" array with a stable long-run histogram of every it... |
| 185 | edit | not_better | 0.9616 | 0.9925 | $0.0009 | Replace the nearest-seen-size term with a histogram-weighted exact-fill probability (sum over see... |
| 186 | edit | not_better | 0.9614 | 0.9925 | $0.0006 | I'll keep the proven exact-fill dominance, but replace the brittle "nearest recently-seen size" m... |
| 187 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | I'll keep the proven exact-fill dominance and the successful "nearest recently-seen size" residua... |
| 188 | edit | not_better | 0.9614 | 0.9925 | $0.0007 | The current residual-matching uses a nearest-seen-size distance that is dominated by the running ... |
| 189 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the score with a classic Best-Fit (smallest residual), but add a small bonus that prefers... |
| 190 | edit | not_better | 0.9920 | 0.9925 | $0.0009 | Add a generalized-fill bonus computed from the histogram: for each residual r, reward it by the p... |
| 191 | edit | not_better | 0.9915 | 0.9925 | $0.0008 | I'll keep the proven exact-fill dominance and the "nearest recently-seen size" residual-matching,... |
| 192 | edit | invalid | 0.0000 | 0.9925 | $0.0008 | The current "nearest seen size" distance term is coarse (integer distances 0,1,2...), giving weak... |
| 193 | edit | not_better | 0.9885 | 0.9925 | $0.0008 | Replace the brittle integer "nearest seen size" metric with a smoothly-weighted reusability score... |
| 194 | edit | not_better | 0.9898 | 0.9925 | $0.0009 | I'll replace the coarse integer "nearest seen size" distance with a smoothly-weighted reusability... |
| 195 | edit | not_better | 0.9903 | 0.9925 | $0.0008 | Replace the brittle nearest-seen-size distance (which saturates once many sizes are seen) with a ... |
| 196 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll replace the coarse integer nearest-seen-size distance with a proper Best-Fit-plus-reuse hybr... |
| 197 | edit | not_better | 0.9900 | 0.9925 | $0.0008 | I'll replace the coarse integer “nearest seen size” term with a smoother reusability score: for e... |
| 198 | edit | not_better | 0.9863 | 0.9925 | $0.0008 | Keep the exact-fill dominance and nearest-seen-size matching, but add a tie-break term that break... |
| 199 | edit | not_better | 0.9715 | 0.9925 | $0.0008 | I'll replace the coarse "nearest seen size" integer-distance term with a smooth, histogram-weight... |
| 200 | edit | not_better | 0.9661 | 0.9925 | $0.0008 | The current nearest-seen-size metric saturates into many ties; I'll keep exact-fill dominance but... |
| 201 | edit | not_better | 0.9903 | 0.9925 | $0.0007 | I'll replace the brittle nearest-seen-size distance with a scaled, smoothly-decaying reuse bonus ... |
| 202 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | Simplify to a classic Best-Fit rule (prefer the smallest non-negative residual), which is the str... |
| 203 | edit | not_better | 0.9619 | 0.9925 | $0.0006 | The nearest-seen-size term saturates and creates many ties, so I'll replace the whole scoring rul... |
| 204 | edit | not_better | 0.9912 | 0.9925 | $0.0008 | I'll keep the existing nearest-seen-size distance term (which works) but strengthen it by replaci... |
| 205 | edit | not_better | 0.9730 | 0.9925 | $0.0008 | I'll keep exact-fill dominance but replace the brittle "nearest-seen-size" term with a lighter, r... |
| 206 | edit | not_better | 0.9915 | 0.9925 | $0.0008 | I'll keep the proven nearest-seen-size distance term but replace the coarse integer distance with... |
| 207 | edit | not_better | 0.9616 | 0.9925 | $0.0008 | The current rule ignores the known strength of Best-Fit; I'll make Best-Fit (smallest non-negativ... |
| 208 | edit | not_better | 0.9912 | 0.9925 | $0.0006 | I'll replace the brittle nearest-seen-size distance with a quantity known to correlate with good ... |
| 209 | edit | not_better | 0.9905 | 0.9925 | $0.0008 | I'll add a recency-weighted histogram "reuse" bonus computed from the actual distribution rather ... |
| 210 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | The nearest-seen-size distance term is essentially binary at distances of 0,1,2 and saturates int... |
| 211 | edit | invalid | 0.0000 | 0.9925 | $0.0009 | Replace the nearest-seen-size distance (which saturates into ties) with a continuous "expected re... |
| 212 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | The current nearest-seen-size distance saturates into ties; I'll soften it by using a fractional ... |
| 213 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | The nearest-seen-size tie saturation is the core weakness; I'll replace it with a classic Best-Fi... |
| 214 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | I'll make the reuse guidance distribution-aware instead of based on the noisy nearest-seen-size: ... |
| 215 | edit | not_better | 0.9761 | 0.9925 | $0.0008 | Point the reuse bonus at the actual capacity-100 target instead of the nearest observed size: com... |
| 216 | edit | not_better | 0.9579 | 0.9925 | $0.0007 | (no description) |
| 217 | edit | not_better | 0.9917 | 0.9925 | $0.0009 | I'll add an "aging"/best-fit tie-break refinement: when residuals tie under the current scoring, ... |
| 218 | edit | not_better | 0.9642 | 0.9925 | $0.0008 | Replace the saturating nearest-seen-size distance with a two-step lookahead: score each residual ... |
| 219 | edit | not_better | 0.9898 | 0.9925 | $0.0008 | I'll keep the exact-fill bonus and the reuse logic, but replace the uninformative saturating dist... |
| 220 | edit | not_better | 0.9666 | 0.9925 | $0.0007 | I'll replace the saturating nearest-seen-size distance (which collapses into ties) with a recency... |
| 221 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | Replace the noisy nearest-seen-size reuse signal with a Sum-of-Squares-style objective: score eac... |
| 222 | edit | not_better | 0.9614 | 0.9925 | $0.0008 | The current scoring saturates because the distance-to-nearest-seen-size collapses many residuals ... |
| 223 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | I will replace the saturating nearest-seen-size distance with a deterministic best-fit tie-break ... |
| 224 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | Replace the reuse/nearest-seen scoring with a simple Best-Fit rule (choose the bin with the small... |
| 225 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | I will replace the saturating nearest-seen-size distance (which collapses residuals into harmful ... |
| 226 | edit | not_better | 0.7688 | 0.9925 | $0.0006 | Replace the saturating nearest-seen-size distance with a direct "power-of-two residual penalty" o... |
| 227 | edit | not_better | 0.9915 | 0.9925 | $0.0007 | I'll keep the exact-fill bonus and mean-residual fallback, but replace the saturating discrete ne... |
| 228 | edit | not_better | 0.9839 | 0.9925 | $0.0008 | I'll refine the reuse signal by scaling it: instead of the raw nearest-seen-size distance (which ... |
| 229 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | Replace the discrete nearest-seen-size reuse signal with a smooth two-sided reuse score: keep the... |
| 230 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the current recomputed-per-call nearest-seen table with a fixed, cheap "flip-to-comp... |
| 231 | edit | not_better | 0.9751 | 0.9925 | $0.0007 | Keep the dominant exact-fill bonus and the recency-weighted nearest-seen-size reuse signal, but b... |
| 232 | edit | not_better | 0.9905 | 0.9925 | $0.0007 | I'll replace the costly per-call distance table with a cheap, closed-form "expected future fill" ... |
| 233 | edit | not_better | 0.7976 | 0.9925 | $0.0007 | I'll keep the exact-fill bonus and reuse signal but replace the brittle discrete nearest-seen-siz... |
| 234 | edit | not_better | 0.9912 | 0.9925 | $0.0006 | Replace the brittle nearest-seen-size table with a direct best-fit-style objective: strongly rewa... |
| 235 | edit | not_better | 0.9910 | 0.9925 | $0.0006 | The recency-weighted nearest-seen-size signal is noisy and saturating; replace it with a clean be... |
| 236 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the noisy nearest-seen-size reuse signal with a "worst-fit for small residuals" rule... |
| 237 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy recency-weighted nearest-seen-size reuse table with a clean, well-known objecti... |
| 238 | edit | not_better | 0.9922 | 0.9925 | $0.0007 | Reintroduce the recency-weighted "reusable residual" signal, but make the exact-fill bonus domina... |
| 239 | edit | not_better | 0.9905 | 0.9925 | $0.0008 | Keep the current recency-weighted nearest-seen-size reuse signal but add a modest bonus for resid... |
| 240 | edit | not_better | 0.9917 | 0.9925 | $0.0009 | Add a "sum-of-two-items" reuse signal: build a recency-weighted histogram of pairwise item-size s... |
| 241 | edit | not_better | 0.9922 | 0.9925 | $0.0007 | I'll replace the noisy per-item recency nearest-seen-distance signal with a smoother, more robust... |
| 242 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | The current nearest-seen-size table is brittle and the exact-fill bonus can't distinguish among b... |
| 243 | edit | not_better | 0.9903 | 0.9925 | $0.0006 | The recency-weighted nearest-seen-size table is noisy and its per-call O(101×\|seen\|) recomputat... |
| 244 | edit | not_better | 0.9910 | 0.9925 | $0.0008 | The current nearest-seen-size table is recomputed with an O(101×\|seen\|) distance matrix every c... |
| 245 | edit | not_better | 0.9912 | 0.9925 | $0.0007 | Introduce a tunable family of "reuse payoff" signals summarized by a single scalar blend: keep ex... |
| 246 | edit | not_better | 0.9711 | 0.9925 | $0.0008 | Introduce a learned-lookahead: maintain a recency-decayed histogram of observed item sizes and re... |
| 247 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the noisy nearest-seen-size reuse signal and mean fallback with a clean classic Best-Fit-... |
| 248 | edit | not_better | 0.9602 | 0.9925 | $0.0009 | Replace the brittle nearest-seen-size table and weak mean term with a single, sharper reuse signa... |
| 249 | edit | not_better | 0.9910 | 0.9925 | $0.0009 | I'll replace the brittle nearest-seen-size lookup with a "residual-value" table that rewards the ... |
| 250 | edit | not_better | 0.9905 | 0.9925 | $0.0007 | The strong exact-fill bonus (worth 1000) dominates everything, so the tie-breaking among non-exac... |
| 251 | edit | not_better | 0.9735 | 0.9925 | $0.0007 | I'll simplify to a well-tested classic: exact-fill first, then prefer the smallest residual that ... |
| 252 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Simplify to a fast, robust rule that avoids the noisy per-call distance table: keep a dominant ex... |
| 253 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the costly/noisy nearest-seen-distance table with a cheap best-fit rule: keep the dominan... |
| 254 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I will keep the dominant exact-fill rule but replace the noisy nearest-seen-distance table with a... |
| 255 | edit | not_better | 0.9670 | 0.9925 | $0.0007 | I'll replace the noisy nearest-seen-size table with an exact-fill-first rule that then prefers le... |
| 256 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I will keep the strong exact-fill rule but replace the brittle nearest-seen-size table with a cle... |
| 257 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | The current rule's near-best performance suggests keeping the strong exact-fill bonus and the nea... |
| 258 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | The current nearest-seen-size table only checks if a residual matches a *single* recent item size... |
| 259 | edit | not_better | 0.9890 | 0.9925 | $0.0008 | Replace the nearest-seen-distance table (which is brittle and essentially binary) with a frequenc... |
| 260 | edit | not_better | 0.9920 | 0.9925 | $0.0008 | The nearest-seen-distance table is noisy and stale; I'll replace it with a smoother reuse signal ... |
| 261 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | Replace the brittle nearest-seen-size distance table with a smooth "reuse" signal based on the cu... |
| 262 | edit | not_better | 0.9649 | 0.9925 | $0.0008 | I'll keep the dominant exact-fill bonus but replace the brittle nearest-seen-distance signal with... |
| 263 | edit | not_better | 0.9649 | 0.9925 | $0.0008 | The nearest-seen-size signal is essentially binary and noisy; I'll replace it with a smoother reu... |
| 264 | edit | invalid | 0.0000 | 0.9925 | $0.0008 | I'll keep the dominant exact-fill bonus and the nearest-recently-seen-size reuse signal (which is... |
| 265 | edit | not_better | 0.9558 | 0.9925 | $0.0007 | Keep the dominant exact-fill bonus and the nearest-recently-seen-size reuse signal, but replace t... |
| 266 | edit | not_better | 0.9870 | 0.9925 | $0.0008 | I'll keep the winning structure (dominant exact-fill bonus plus nearest-recently-seen-size reuse ... |
| 267 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | I'll keep the exact-fill bonus but replace the brittle "nearest recent seen size" signal with a b... |
| 268 | edit | not_better | 0.9883 | 0.9925 | $0.0007 | I will keep the exact-fill bonus and the nearest-recently-seen-size reuse signal, but make the re... |
| 269 | edit | not_better | 0.9905 | 0.9925 | $0.0008 | I'll keep the winning structure (exact-fill bonus plus reuse signal), but make the reuse signal a... |
| 270 | edit | not_better | 0.9922 | 0.9925 | $0.0008 | I'll keep the exact-fill bonus and the nearest-recently-seen-size reuse signal (the winning struc... |
| 271 | edit | not_better | 0.9908 | 0.9925 | $0.0007 | Keep the exact-fill bonus and nearest-recently-seen-size reuse signal, but weight the reuse prefe... |
| 272 | edit | not_better | 0.9751 | 0.9925 | $0.0008 | Keep the exact-fill bonus and the nearest-recently-seen-size reuse signal, but add a tiny best-fi... |
| 273 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I'll make the reuse signal symmetric by treating residual r and its complement 100-r as equivalen... |
| 274 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | I'll keep the winning exact-fill bonus plus nearest-recently-seen-size reuse signal, but make the... |
| 275 | edit | not_better | 0.9910 | 0.9925 | $0.0007 | I'll change the reuse table to track only the distribution of item sizes via a smoothed, exponent... |
| 276 | edit | not_better | 0.9579 | 0.9925 | $0.0007 | Keep the exact-fill bonus and nearest-recently-seen-size reuse signal, but change the fallback ti... |
| 277 | edit | not_better | 0.9920 | 0.9925 | $0.0007 | I'll tune the magnitude of the exact-fill bonus and the fallback mean-preference coefficient: mak... |
| 278 | edit | not_better | 0.9240 | 0.9925 | $0.0008 | Restrict the reuse table to seen item sizes above a threshold (e.g. ≥40), so that the "nearest-se... |
| 279 | edit | not_better | 0.9912 | 0.9925 | $0.0008 | Replace the brittle "distance to nearest seen size" reuse table with an expected-fill-value objec... |
| 280 | edit | not_better | 0.9910 | 0.9925 | $0.0007 | I'll replace the "distance to nearest seen size" reuse signal with a two-part objective: a strong... |
| 281 | edit | not_better | 0.9863 | 0.9925 | $0.0007 | Replace the brittle "nearest recently-seen size" reuse signal with a distribution-aware "usabilit... |
| 282 | edit | not_better | 0.9708 | 0.9925 | $0.0007 | I'll replace the noisy nearest-seen-size reuse signal with a smooth "fill probability" derived fr... |
| 283 | edit | not_better | 0.9910 | 0.9925 | $0.0010 | Replace the brittle Boolean nearest-seen-size distance with a frequency-weighted reuse signal: fo... |
| 284 | edit | not_better | 0.5688 | 0.9925 | $0.0008 | The fallback tiebreaker should reward residuals that match common item sizes while also mildly pr... |
| 285 | edit | not_better | 0.9616 | 0.9925 | $0.0007 | I'll add a stronger, more stable exact-fill mechanism: precompute a smoothed histogram of item si... |
| 286 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | Replace the reuse-table scoring with a simpler, more robust best-fit-plus-exact-fill rule: strong... |
| 287 | edit | not_better | 0.9696 | 0.9925 | $0.0007 | Replace the fragile nearest-seen-size reuse signal with a principled distribution-aware expected-... |
| 288 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | Keep the strong exact-fill bonus, but simplify the fallback to pure best-fit (smallest residual) ... |
| 289 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll strengthen the exact-fill mechanism by adding a capped bonus for residuals that are common r... |
| 290 | edit | not_better | 0.5224 | 0.9925 | $0.0005 | Replace the noisy nearest-seen-size objective with the classic robustness-oriented rule: strong e... |
| 291 | edit | not_better | 0.9614 | 0.9925 | $0.0007 | Replace the noisy nearest-seen-size table with a hybrid: a strong exact-fill bonus, and for non-e... |
| 292 | edit | not_better | 0.9614 | 0.9925 | $0.0007 | Replace the O(101×seen) nearest-seen lookups and best-fit fallback with a cleaner "expected immed... |
| 293 | edit | not_better | 0.9637 | 0.9925 | $0.0007 | I'll add a strong, capped "reusable residual" bonus: keep the exact-fill preference, and addition... |
| 294 | edit | not_better | 0.9740 | 0.9925 | $0.0007 | I'll replace the noisy nearest-seen-distance term with a cleaner objective: keep the strong exact... |
| 295 | edit | not_better | 0.9917 | 0.9925 | $0.0007 | Keep the current exact-fill and nearest-seen-size reuse logic, but replace the linear nearest-dis... |
| 296 | edit | not_better | 0.9917 | 0.9925 | $0.0008 | I will make the nearest-seen-size lookup much sharper by replacing the linear distance penalty wi... |
| 297 | edit | not_better | 0.9616 | 0.9925 | $0.0006 | I'll replace the noisy "nearest recently-seen size" lookup (which is fragile and empirically near... |
| 298 | edit | not_better | 0.9925 | 0.9925 | $0.0008 | Add a penalty for leaving very small residuals (which essentially waste capacity since items have... |
| 299 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | Replace the fragile "nearest seen size" reuse table with the classic and robust Best-Fit rule (mi... |
| 300 | edit | not_better | 0.9616 | 0.9925 | $0.0005 | Replace the fragile nearest-seen-size objective with a "best fit + exact-fill" rule that directly... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,60 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with a "reusable residual" objective.
+
+Exact fills are strongly preferred. Otherwise, prefer leaving a residual that
+matches a recently-seen item size (so the next few arrivals can fill it exactly),
+falling back toward a mild preference for residuals near the running mean.
+"""
 import numpy as np
+
+_hist = np.zeros(101, dtype=np.float64)
+_count = 0.0
+_sum = 0.0
+# Cached array of item sizes seen recently (weighted by recency via decay)
+_seen = np.zeros(101, dtype=np.float64)
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
+    global _hist, _count, _sum, _seen
+    _hist[item] += 1.0
+    _count += 1.0
+    _sum += item
+    # Recency-weighted presence: decay all, then boost this item.
+    _seen *= 0.999
+    _seen[item] += 1.0
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    residual = bins - item  # >= 0 for all bins shown
+    res = residual.astype(np.float64)
+
+    if _count > 0:
+        mean_item = _sum / _count
+    else:
+        mean_item = 40.0
+
+    # Distance to the closest recently-seen item size (0 if residual is an observed size).
+    # Build distance-to-nearest-seen-size for each possible residual value 0..100.
+    seen_present = _seen > 0.0
+    # positions of seen sizes
+    # distance from any residual r to nearest seen size
+    # compute via cumulative approach
+    idx = np.nonzero(seen_present)[0]
+    if idx.size > 0:
+        # For each residual value 0..100, min distance to a seen size.
+        vals = np.arange(101, dtype=np.float64)
+        d = np.abs(vals[:, None] - idx[None, :].astype(np.float64))
+        nearest = d.min(axis=1)  # shape (101,)
+    else:
+        nearest = np.abs(np.arange(101, dtype=np.float64) - mean_item)
+
+    # Score: closer to a reusable residual is better; exact fills dominant.
+    score = -nearest[residual.astype(np.int64)]
+
+    # Mild preference for residuals near the running mean as a fallback.
+    score += -0.05 * np.abs(res - mean_item)
+
+    # Strongly prefer exact fills.
+    score += np.where(residual == 0, 1000.0, 0.0)
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (23 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 19 | `global _hist, _count, _sum, _seen` | -0.9925 | essential: the program fails or turns invalid without it |
| 27 | `residual = bins - item` | -0.9925 | essential: the program fails or turns invalid without it |
| 27 | `term + bins` | -0.9925 | essential: the program fails or turns invalid without it |
| 28 | `res = residual.astype(np.float64)` | -0.9925 | essential: the program fails or turns invalid without it |
| 30 | `if _count > 0: ...` | -0.9925 | essential: the program fails or turns invalid without it |
| 31 | `mean_item = _sum / _count` | -0.9925 | essential: the program fails or turns invalid without it |
| 37 | `seen_present = _seen > 0.0` | -0.9925 | essential: the program fails or turns invalid without it |
| 41 | `idx = np.nonzero(seen_present)[0]` | -0.9925 | essential: the program fails or turns invalid without it |
| 42 | `if idx.size > 0: ...` | -0.9925 | essential: the program fails or turns invalid without it |
| 44 | `vals = np.arange(101, dtype=np.float64)` | -0.9925 | essential: the program fails or turns invalid without it |
| 45 | `d = np.abs(vals[:, None] - idx[None, :].astype(np.float64))` | -0.9925 | essential: the program fails or turns invalid without it |
| 46 | `nearest = d.min(axis=1)` | -0.9925 | essential: the program fails or turns invalid without it |
| 51 | `score = -nearest[residual.astype(np.int64)]` | -0.9925 | essential: the program fails or turns invalid without it |
| 57 | `score += np.where(residual == 0, 1000.0, 0.0)` | -0.2836 | matters |
| 27 | `term - item` | -0.0857 | matters |
| 54 | `score += -0.05 * np.abs(res - mean_item)` | -0.0360 | matters |
| 22 | `_sum += item` | -0.0346 | matters |
| 21 | `_count += 1.0` | -0.0015 | no effect alone |
| 25 | `_seen[item] += 1.0` | -0.0012 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 20: `_hist[item] += 1.0`
- line 24: `_seen *= 0.999`
- line 33: `mean_item = 40.0`
- line 48: `nearest = np.abs(np.arange(101, dtype=np.float64) - mean_item)`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9925 | 0.9918 |
| minimal (4 parts removed) | 0.9925 | 0.9918 |

Minimal program:

```python
"""Best fit with a "reusable residual" objective.

Exact fills are strongly preferred. Otherwise, prefer leaving a residual that
matches a recently-seen item size (so the next few arrivals can fill it exactly),
falling back toward a mild preference for residuals near the running mean.
"""
import numpy as np
_hist = np.zeros(101, dtype=np.float64)
_count = 0.0
_sum = 0.0
_seen = np.zeros(101, dtype=np.float64)

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _hist, _count, _sum, _seen
    _count += 1.0
    _sum += item
    _seen[item] += 1.0
    residual = bins - item
    res = residual.astype(np.float64)
    if _count > 0:
        mean_item = _sum / _count
    else:
        pass
    seen_present = _seen > 0.0
    idx = np.nonzero(seen_present)[0]
    if idx.size > 0:
        vals = np.arange(101, dtype=np.float64)
        d = np.abs(vals[:, None] - idx[None, :].astype(np.float64))
        nearest = d.min(axis=1)
    else:
        pass
    score = -nearest[residual.astype(np.int64)]
    score += -0.05 * np.abs(res - mean_item)
    score += np.where(residual == 0, 1000.0, 0.0)
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online --budget 0.75 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 1
python -m autoresearch.loop --report experiments/llm-long-search-v1/runs/s1   # rebuild this report
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
