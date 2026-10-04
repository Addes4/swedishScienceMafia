# Research loop report: bp_sh_b200

| | |
|---|---|
| problem | `bp_sh_b200` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0868 of a $0.20 hard cap, 150 calls, 297,977 tokens |
| wall time | search 1326 s, baselines 40 s, explain 33 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (149 valid), 4 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9444 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9478 | 0.9641 |  |
| baseline `funsearch_or` | 0.9552 | 0.9711 | `problems/bp_sh_b200/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.8723 | 0.9937 | `problems/bp_sh_b200/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9200 | 0.9950 | `problems/bp_sh_b200/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9478 | 0.9641 | 1 parts removed |

Audit: public 0.9444 → 0.9478 (+0.0034), hidden 0.9634 → 0.9641 (+0.0007); public − hidden gap of the final program -0.0163.

Against the baselines: the final program's public score is below the best baseline (`funsearch_or`, 0.9552). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9444 | 0.9444 | $0.0003 | Replace pure best-fit with a "best-fit among sufficiently-full bins" rule: prefer the tightest fi... |
| 2 | edit | not_better | 0.9444 | 0.9444 | $0.0003 | Replace pure best-fit with a balance-aware rule that is the well-known "best fit decreasing"-styl... |
| 3 | edit | not_better | 0.9444 | 0.9444 | $0.0007 | Add a small residual-usefulness bonus to best fit: score by tightness but add a mild reward for l... |
| 4 | edit | not_better | 0.6039 | 0.9444 | $0.0004 | Replace pure best-fit with a hybrid rule: use best-fit when a fairly tight fit exists, otherwise ... |
| 5 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | Replace pure best-fit with a bounded "waste" rule: score bins by how well the residual after inse... |
| 6 | edit | not_better | 0.7056 | 0.9444 | $0.0004 | I'll implement a follow-up-aware rule based on the "sum of squares" (Worst-Fit-with-residual) heu... |
| 7 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll implement a "best fit with a stay-small tie-break" rule based on the classic observation tha... |
| 8 | edit | not_better | 0.9444 | 0.9444 | $0.0005 | I'll replace pure best-fit with a mathematically-grounded rule: score bins by the "waste" if the ... |
| 9 | edit | not_better | 0.9444 | 0.9444 | $0.0004 | I'll try a tie-broken best-fit that uses bin index awareness by adding a tiny, deterministic term... |
| 10 | edit | improved | 0.9446 | 0.9446 | $0.0005 | Replace pure best-fit with a randomized variant of Best-Fit that occasionally (with small probabi... |
| 11 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | Replace the crude occasional least-full diversion with a softer, more principled diversification:... |
| 12 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | Replace the periodic least-full diversion with an adaptive best-fit variant: pure best-fit normal... |
| 13 | edit | not_better | 0.9446 | 0.9446 | $0.0005 | I will add a lightweight "reserve large bins" tweak: keep best-fit, but when an item cannot exact... |
| 14 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the crude periodic least-full diversion with a principled "best fit plus bounded har... |
| 15 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I will replace the periodic least-full diversion with a deterministic "best fit with exact/subset... |
| 16 | edit | not_better | 0.9442 | 0.9446 | $0.0005 | I'll implement a proper "best fit decreasing"-style approach adapted to online packing: among bin... |
| 17 | edit | not_better | 0.9446 | 0.9446 | $0.0005 | I'll replace pure best-fit with a "sum-of-squares" best fit: rather than minimizing the post-plac... |
| 18 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I will switch the bin-choice rule from best-fit (minimize post-placement residual) to worst-fit o... |
| 19 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the crude periodic least-full diversion with a two-tier best-fit that uses a seconda... |
| 20 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the periodic least-full diversion with a bounded "almost-best-fit" tie-break: among ... |
| 21 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the crude periodic least-full diversion with a deterministic two-criterion rule: pri... |
| 22 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the rule with a Gaussian-fit / "residual value" score: score each bin by how well it... |
| 23 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll switch to a "best fit with future-aware residual rejection": keep strict best-fit as the pri... |
| 24 | edit | not_better | 0.9444 | 0.9446 | $0.0007 | I'll replace the fixed periodic least-full diversion with an adaptive "reservation" rule: maintai... |
| 25 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the crude periodic diversion with a "fuller-bin-consolidation" selection: use strict... |
| 26 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I will replace the periodic least-full diversion with an adaptive "aging/leveling" score: strict ... |
| 27 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the rule with an "adaptive best-fit plus a persistent lab-state bonus": keep strict ... |
| 28 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I will use a proper "best fit decreasing-like" trick adapted online: pure best-fit, but among bin... |
| 29 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Add a small deterministic tie-break that prefers bins with more items already packed (a count pro... |
| 30 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Replace the deterministic periodic least-full diversion with the classic online "harmonic/next-fi... |
| 31 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the periodic least-full diversion with a deterministic "harmonic-like" score: strict... |
| 32 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | Replace the ad-hoc periodic diversion with a deterministic, state-free tie-break: strict best-fit... |
| 33 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc periodic diversion with strict best-fit plus a tiny state-free tie-break ... |
| 34 | edit | not_better | 0.5080 | 0.9446 | $0.0005 | I'll replace best-fit with a "best-fit with residual-gap awareness" rule: instead of minimizing r... |
| 35 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I will replace the periodic least-full diversion with a "best-fit plus residual-waste penalty" ru... |
| 36 | edit | not_better | 0.9433 | 0.9446 | $0.0005 | The periodic least-full diversion currently uses a fixed 50-step period; I will replace it with a... |
| 37 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I will replace the ad-hoc periodic least-full diversion with a state-free "best-fit plus fullness... |
| 38 | edit | not_better | 0.9439 | 0.9446 | $0.0006 | I'll replace the priority rule with a "best-fit that only fills a bin if the resulting residual i... |
| 39 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the periodic least-full diversion with a stateful "match the most common recent item... |
| 40 | edit | not_better | 0.9346 | 0.9446 | $0.0005 | I'll replace the periodic deterministic diversion with a rare, state-free diversion triggered by ... |
| 41 | edit | not_better | 0.9444 | 0.9446 | $0.0007 | I'll tune the existing diversification: change the diversion period and make the diversion reward... |
| 42 | edit | not_better | 0.9424 | 0.9446 | $0.0005 | I will replace the fragile periodic diversion with a tuned deterministic alternation that shifts ... |
| 43 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the ad-hoc periodic diversion with a principled "best-fit that respects a residual-u... |
| 44 | edit | not_better | 0.9226 | 0.9446 | $0.0004 | I will replace the periodic diversion with a state-free rule that inverts to worst-fit (most-free... |
| 45 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I will replace the periodic diversification with a classic, well-established online heuristic: Be... |
| 46 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | Replace the periodic worst-fit diversion with a proper harmonic-based best-fit that switches beha... |
| 47 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll combine best-fit with a "best-fit-decreasing-style" sub-bin rule: rank by tightest residual ... |
| 48 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll switch from the periodic worst-fit diversion to the well-known "Almost Worst-Fit / Best-Fit ... |
| 49 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc periodic diversion with a principled hybrid: scale the best-fit residual ... |
| 50 | edit | not_better | 0.9437 | 0.9446 | $0.0005 | I will replace the arbitrary periodic worst-fit diversion with a deterministic, item-size-aware "... |
| 51 | edit | not_better | 0.8857 | 0.9446 | $0.0006 | I'll replace the ad-hoc periodic diversion with the well-known "Best-Fit with a sub-threshold wor... |
| 52 | edit | not_better | 0.9426 | 0.9446 | $0.0005 | I will keep the proven best-fit-plus-periodic-diversion structure but tune the diversion paramete... |
| 53 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the periodic worst-fit diversion with a deterministic "reserve-fit" tie-breaker: kee... |
| 54 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll replace the periodic worst-fit diversion with a smoother, state-driven "aging" rule: give a ... |
| 55 | edit | not_better | 0.9444 | 0.9446 | $0.0006 | I'll keep pure best-fit as the base but add a small, sharply-thresholded bonus only when the resu... |
| 56 | edit | not_better | 0.9444 | 0.9446 | $0.0005 | I'll replace the ad-hoc periodic diversion with a principled Best-Fit-Decreasing-style rule: pref... |
| 57 | edit | not_better | 0.8699 | 0.9446 | $0.0006 | I'll replace the periodic worst-fit diversion with a "best fit plus least-full-eligible tie-break... |
| 58 | edit | not_better | 0.9437 | 0.9446 | $0.0005 | I'll replace the arbitrary periodic single-bin diversion with a periodic Gaussian (normal) pertur... |
| 59 | edit | improved | 0.9453 | 0.9453 | $0.0005 | I will replace the ad-hoc periodic diversion with a hybrid that keeps pure best-fit but, on a rar... |
| 60 | edit | not_better | 0.9282 | 0.9453 | $0.0006 | I will make the periodic diversion self-tuning: instead of a fixed period and fixed modulo target... |
| 61 | edit | not_better | 0.9430 | 0.9453 | $0.0005 | I'll replace the fixed-period modulo diversion with a self-tuning periodic diversion that occurs ... |
| 62 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the single fixed modulo target with a "match complement" rule: on a periodic trigger... |
| 63 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll keep the periodic modulo-consolidation diversion but blend it softly with best-fit (only whe... |
| 64 | edit | not_better | 0.9442 | 0.9453 | $0.0006 |  |
| 65 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll replace the periodic modulo diversion with a stateless "best-fit, but prefer to leave a larg... |
| 66 | edit | not_better | 0.9285 | 0.9453 | $0.0005 | I'll switch from best-fit to a "least-loaded-bin-that-still-fits-with-a-small-residual" hybrid: r... |
| 67 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | Replace the weak periodic modulo diversion with a well-known stronger online heuristic: keep best... |
| 68 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll replace the periodic heuristic entirely with a clean scale-free scoring rule: rank bins by b... |
| 69 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | The current periodic diversion is too rare and uses a fixed target; I'll replace it with a determ... |
| 70 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the periodic modulo diversion with a proper always-on "best-fit with sliver-avoidanc... |
| 71 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll switch from best-fit to a "harmonic/score-based" packing that exploits the known item-size d... |
| 72 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | Replace the rare periodic modulo diversion with an always-on, bounded consolidation tie-break: ra... |
| 73 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll replace the periodic modulo diversion with an always-on scoring rule that combines best-fit ... |
| 74 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll replace the weak periodic modulo-consolidation with an always-on "best-fit plus residual usa... |
| 75 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the fragile, heuristic scoring with a principled approach: use best-fit as the prima... |
| 76 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll switch from best-fit to worst-fit-within-window: among bins whose residual is not much large... |
| 77 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the heuristics with a standardized best-fit variant used in bin-packing literature: ... |
| 78 | edit | not_better | 0.9444 | 0.9453 | $0.0009 | I'll replace best-fit with a "best-fit by matching to a canonical residual" rule: since items are... |
| 79 | edit | not_better | 0.9444 | 0.9453 | $0.0019 | Instead of ad-hoc residual preferences, I'll use a principled "best-fit with least-waste" rule: r... |
| 80 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I will replace the ad-hoc heuristic with a principled best-fit variant that distinguishes among n... |
| 81 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the ineffective periodic modulo heuristic with a principled online bin-packing rule ... |
| 82 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | Replace best-fit with a "tighten to fill" rule: rank bins so that placing the item either closes ... |
| 83 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | The best-fit baseline is solid; I'll add a small deterministic sub-1 tie-break that prefers bins ... |
| 84 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the rare periodic diversion with an always-on blend: keep best-fit as the dominant t... |
| 85 | edit | not_better | 0.9426 | 0.9453 | $0.0007 | I'll switch from best-fit to a "worst-fit among nearly-full bins" hybrid: rank primarily by best ... |
| 86 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll abandon the ineffective residual-modulo heuristics and switch to a "best-fit with capacity-f... |
| 87 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the ad-hoc periodic diversion with the classic online bin-packing heuristic that gen... |
| 88 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | Replace best-fit with a portfolio-free "least-loaded bin that still fits tightly": rank bins by p... |
| 89 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Replace the heuristic with a scaled "best fit plus gentle worst-fit tie-break" that avoids always... |
| 90 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the heuristic with a proper harmonic-style ranking: prefer bins where placing the it... |
| 91 | edit | not_better | 0.9404 | 0.9453 | $0.0007 | I'll implement a "best-fit with bounded worst-fit tie-break": find the minimum post-placement res... |
| 92 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the ineffective periodic modulo diversion with a proven better rule: Best-Fit with a... |
| 93 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the heuristic with a tuned online "subset-sum aware" secondary term: keep best-fit a... |
| 94 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the periodic modulo diversion with pure best-fit, but add an exact-fit bonus and a s... |
| 95 | edit | invalid | 0.0000 | 0.9453 | $0.0006 | I'll replace the periodic diversion with a consistently strong online rule: rank by best-fit, but... |
| 96 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Replace the intermittent modulo diversion with a steady, well-known strong online bin-packing rul... |
| 97 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the periodic modulo diversion with a stateful "residual histogram matching" rule: ke... |
| 98 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Replace the ineffective periodic modulo diversion with a fully deterministic version of best-fit ... |
| 99 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the rule with classic "Best Fit" (smallest post-placement residual) combined with a ... |
| 100 | edit | not_better | 0.9448 | 0.9453 | $0.0008 | Make the modulo-consolidation diversion trigger based on the arriving item being large (size >= 6... |
| 101 | edit | invalid | 0.0000 | 0.9453 | $0.0006 | I'll replace the heuristic with a stateful "match-pair" rule that keeps best-fit as the base rank... |
| 102 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll make the modulo-consolidation diversion more aggressive by applying it continuously to bins ... |
| 103 | edit | not_better | 0.9442 | 0.9453 | $0.0008 | Replace the modulo diversion with a safe online item-size histogram: keep best-fit as the dominan... |
| 104 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Pure best-fit is a strong baseline, but ties among bins with equal residual are decided by bin in... |
| 105 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll add a stateful tie-break that, when several bins give the same post-placement residual (the ... |
| 106 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll switch to a stateful best-fit variant that tracks the empirical item mean and, among bins wi... |
| 107 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | Replace the fragile modulo-periodic diversion with a robust stateful "best fit with large-gap pre... |
| 108 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | Refine tie-breaking: keep best-fit as the dominant term but add a small epsilon that, among bins ... |
| 109 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the fragile periodic modulo-diversion with a robust "residual-matching" rule: track ... |
| 110 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll implement a proper O(1) perceptron-style online learning rule: maintain a running estimate o... |
| 111 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | I'll replace the fragile periodic modulo-diversion with a robust, always-on secondary term: compu... |
| 112 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | The periodic modulo diversion hurt more than it helped; I'll replace it with a pure best-fit plus... |
| 113 | edit | not_better | 0.9444 | 0.9453 | $0.0007 | (no description) |
| 114 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace best-fit with a stateful "best fit plus lookahead-safe residual matching": keep best... |
| 115 | edit | not_better | 0.9393 | 0.9453 | $0.0006 | I'll make the diversion less fragile: instead of a fixed modulo period, divert a small determinis... |
| 116 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace best-fit with a distribution-aware "fit-plus-waste" scoring that mirrors the classic... |
| 117 | edit | not_better | 0.9413 | 0.9453 | $0.0005 | I'll replace the fragile periodic modulo diversion with a deterministic "worst-fit for large item... |
| 118 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the fragile periodic modulo diversion with a smooth always-on formulation that blend... |
| 119 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the fragile periodic modulo diversion with a robust always-on hybrid that keeps best... |
| 120 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Replace the fragile scoring with pure best-fit implemented as a stable, correct ranking: use lexi... |
| 121 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | I'll switch from pure best-fit to a "best fit plus avoid-new-bin" rule: keep best-fit as the domi... |
| 122 | edit | not_better | 0.9426 | 0.9453 | $0.0005 | I'll use a randomized "best-fit with small probability of worst-fit among fitting bins" rule: pur... |
| 123 | edit | not_better | 0.9444 | 0.9453 | $0.0008 | I'll replace the fragile periodic modulo diversion with an always-on smooth blend that keeps best... |
| 124 | edit | not_better | 0.9453 | 0.9453 | $0.0006 | I'll switch to a tuned "best fit" variant that only diverts to the modulo-40 consolidation bin le... |
| 125 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | Replace the arbitrary periodic modulo diversion with the "smooth-fit" heuristic of Csirik et al.:... |
| 126 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll keep best-fit as the dominant rule but replace the noisy periodic diversion with a robust al... |
| 127 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Replace the fragile periodic modulo diversion with a robust "harmonic fit" tie-breaker that keeps... |
| 128 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the noisy periodic modulo diversion with a principled always-on tie-breaker: keep be... |
| 129 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the noisy periodic modulo diversion with a principled "post-placement residual leavi... |
| 130 | edit | not_better | 0.9444 | 0.9453 | $0.0005 | Use pure best-fit but break ties toward the bin whose residual after placement is largest (i.e., ... |
| 131 | edit | not_better | 0.9444 | 0.9453 | $0.0006 | I'll replace the noisy periodic modulo diversion with a deterministic, always-on consolidation ru... |
| 132 | edit | improved | 0.9471 | 0.9471 | $0.0005 | I'll keep best-fit dominant but strengthen the periodic consolidation diversion by using it more ... |
| 133 | edit | not_better | 0.9444 | 0.9471 | $0.0005 | The current periodic diversion is noisy; instead I'll make the heuristic depend smoothly on the i... |
| 134 | edit | not_better | 0.9469 | 0.9471 | $0.0005 | I'll make the consolidation diversion adaptive and stronger: instead of a fixed every-4th-step mo... |
| 135 | edit | not_better | 0.9444 | 0.9471 | $0.0006 |  |
| 136 | edit | improved | 0.9478 | 0.9478 | $0.0005 | I'll replace the noisy fixed-period modulo diversion with an adaptive scheme that triggers divers... |
| 137 | edit | not_better | 0.9458 | 0.9478 | $0.0005 | I'll make diversion much more selective and tie it to the actual number of bins while ranking div... |
| 138 | edit | not_better | 0.9446 | 0.9478 | $0.0005 | I'll replace the noisy periodic diversion with a smooth, always-on hybrid score that blends best-... |
| 139 | edit | not_better | 0.9444 | 0.9478 | $0.0005 | I'll replace the modulo-of-mean diversion with a "worst-fit-improving" consolidation: on diversio... |
| 140 | edit | not_better | 0.9417 | 0.9478 | $0.0006 | I'll replace the noisy modulo-mean diversion with a principled hybrid: mostly pure best-fit, but ... |
| 141 | edit | not_better | 0.9442 | 0.9478 | $0.0006 | Replace the fixed period-3 modulo diversion with a diversion that triggers only when the current ... |
| 142 | edit | not_better | 0.7469 | 0.9478 | $0.0006 | I'll replace the heuristic modulo-mean diversion with a stronger, more principled rule: keep best... |
| 143 | edit | not_better | 0.9290 | 0.9478 | $0.0006 | I'll replace the diversion criterion with a smooth, always-on best-fit variant that adds a bonus ... |
| 144 | edit | not_better | 0.8913 | 0.9478 | $0.0006 | I'll make diversion deterministic and targeted: always use best-fit, but when the arriving item i... |
| 145 | edit | not_better | 0.9444 | 0.9478 | $0.0006 | I'll keep best-fit as the default but make the diversion depend on the current best-fit residual ... |
| 146 | edit | not_better | 0.9444 | 0.9478 | $0.0006 | Use a deterministic "sliver-aware best fit": default to best fit, but when best-fit would leave a... |
| 147 | edit | not_better | 0.9173 | 0.9478 | $0.0006 | Replace the noisy fixed-period modulo-mean diversion with a self-tuning threshold: track the runn... |
| 148 | edit | not_better | 0.9426 | 0.9478 | $0.0006 | Replace the modulo-mean diversion with a proper "floor best-fit" rule: among bins that can hold t... |
| 149 | edit | not_better | 0.9478 | 0.9478 | $0.0006 | I'll keep the same modulo-consolidation diversion structure but trigger it based on the item size... |
| 150 | edit | not_better | 0.9444 | 0.9478 | $0.0005 | I'll replace the best-fit base with a harmonic-style "smooth best fit" score that combines best-f... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,34 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with adaptive modulo-consolidation diversion.
+
+Pure best fit leaves many small slivers for this distribution. On some steps we
+divert to the bin whose residual after placement is closest to a multiple of
+the mean item size (~40), which consolidates leftovers into fuller slots.
+Best-fit stays dominant otherwise. Diversion fires only for smaller items
+(where slivers form) and uses a fractional-phase period so consolidation is
+spread evenly rather than in bursts.
+"""
 import numpy as np
+
+_state = {"n": 0}
+_MEAN = 40.0
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin; highest score wins (first on ties)."""
+    n = _state["n"]
+    _state["n"] = n + 1
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    # Base: best-fit priority (tighter residual -> higher score).
+    better_fit = -(bins - item)
+
+    # Divert mainly when small items are arriving (these create slivers),
+    # using a fractional phase to spread consolidation evenly.
+    if item < 60 and (n % 3 == 0):
+        resid = bins - item  # remaining after placing (>= 0)
+        m = np.round(resid / _MEAN)
+        dist = np.abs(resid - m * _MEAN)
+        return -dist * 100.0 + better_fit
+
+    return better_fit
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (14 parts, 28 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 19 | `n = _state['n']` | -0.9478 | essential: the program fails or turns invalid without it |
| 23 | `better_fit = -(bins - item)` | -0.9478 | essential: the program fails or turns invalid without it |
| 28 | `resid = bins - item` | -0.9478 | essential: the program fails or turns invalid without it |
| 29 | `m = np.round(resid / _MEAN)` | -0.9478 | essential: the program fails or turns invalid without it |
| 30 | `dist = np.abs(resid - m * _MEAN)` | -0.9478 | essential: the program fails or turns invalid without it |
| 28 | `term - item` | -0.0116 | matters |
| 20 | `_state['n'] = n + 1` | -0.0049 | matters |
| 20 | `term + 1` | -0.0049 | matters |
| 20 | `term + n` | -0.0034 | matters |
| 27 | `if item < 60 and n % 3 == 0: ...` | -0.0034 | matters |
| 28 | `term + bins` | -0.0034 | matters |
| 31 | `return -dist * 100.0 + better_fit` | -0.0034 | matters |
| 31 | `term + -dist * 100.0` | -0.0034 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 31: `term + better_fit`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9478 | 0.9641 |
| minimal (1 parts removed) | 0.9478 | 0.9641 |

Minimal program:

```python
"""Best fit with adaptive modulo-consolidation diversion.

Pure best fit leaves many small slivers for this distribution. On some steps we
divert to the bin whose residual after placement is closest to a multiple of
the mean item size (~40), which consolidates leftovers into fuller slots.
Best-fit stays dominant otherwise. Diversion fires only for smaller items
(where slivers form) and uses a fractional-phase period so consolidation is
spread evenly rather than in bursts.
"""
import numpy as np
_state = {'n': 0}
_MEAN = 40.0

def priority(item, bins):
    """Return a priority for every bin; highest score wins (first on ties)."""
    n = _state['n']
    _state['n'] = n + 1
    better_fit = -(bins - item)
    if item < 60 and n % 3 == 0:
        resid = bins - item
        m = np.round(resid / _MEAN)
        dist = np.abs(resid - m * _MEAN)
        return -dist * 100.0
    return better_fit
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_b200 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 3
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_b200-s3   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_b200/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_b200/initial.py` `609927c5ea619a94`
- `problems/bp_sh_b200/problem.md` `190017a698e23cd8`
- `problems/bp_sh_b200/verify.py` `55fde4c12c8b08c5`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
