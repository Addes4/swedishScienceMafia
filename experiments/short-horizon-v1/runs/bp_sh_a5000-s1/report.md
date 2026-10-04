# Research loop report: bp_sh_a5000

| | |
|---|---|
| problem | `bp_sh_a5000` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.1081 of a $0.20 hard cap, 150 calls, 362,523 tokens |
| wall time | search 2219 s, baselines 169 s, explain 72 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (150 valid), 2 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9590 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9707 | 0.9709 |  |
| baseline `funsearch_or` | 0.9702 | 0.9711 | `problems/bp_sh_a5000/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9938 | 0.9937 | `problems/bp_sh_a5000/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9952 | 0.9950 | `problems/bp_sh_a5000/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9693 | 0.9712 | 4 parts removed |

Audit: public 0.9590 → 0.9707 (+0.0117), hidden 0.9634 → 0.9709 (+0.0075); public − hidden gap of the final program -0.0002.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9952). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Add a small penalty for choosing an unused bin (remaining capacity 100) so the item prefers alrea... |
| 2 | edit | not_better | 0.6068 | 0.9590 | $0.0004 | I'll replace plain best-fit with a size-class-aware rule that uses a small amount of learned stat... |
| 3 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll use a "best fit with reserved slack" rule: score bins by preferring the tightest fit among a... |
| 4 | edit | not_better | 0.9558 | 0.9590 | $0.0004 | Replace plain best-fit with a hybrid that applies the classic Best-Fit-Decreasing intuition onlin... |
| 5 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Add a learning component that tracks the empirical mean item size seen so far and uses it to comp... |
| 6 | edit | not_better | 0.9294 | 0.9590 | $0.0004 | Replace plain best-fit with a "worst-fit among good fits with reserved slack" strategy: normally ... |
| 7 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll add a small tie-breaking preference for the tightest fit but with a tiny penalty that biases... |
| 8 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll implement a modified best-fit that strongly avoids opening new bins: among used bins it pick... |
| 9 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Add a stable-key perturbation to best-fit: among bins, prefer the tightest post-placement residua... |
| 10 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll replace plain best-fit with a learned best-fit that keeps a running histogram of item sizes ... |
| 11 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace plain best-fit with a shifted best-fit that reserves a small amount of slack: among ... |
| 12 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Replace plain best-fit with a score that balances tightest-fit against leaving a reusable gap, us... |
| 13 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace plain best-fit with a "reserved slack" hybrid: use best-fit among used bins normally... |
| 14 | edit | not_better | 0.9590 | 0.9590 | $0.0007 | I'll implement an adaptive best-fit-with-reservation: normally best-fit, but among near-ties in r... |
| 15 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll switch from pure best-fit to a hybrid "reserve large items" rule: prefer a fresh/empty bin o... |
| 16 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace pure best-fit with a "best fit plus last-bin tie-break" that, among bins leaving the... |
| 17 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a hook-based rule: among fitting bins, prefer the fullest used bin (sm... |
| 18 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace plain best-fit with a rule that also discourages leaving tiny unusable residuals: score b... |
| 19 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Replace best-fit with a harmonic-style rule that scores bins by how well the item fills the resid... |
| 20 | edit | not_better | 0.8848 | 0.9590 | $0.0005 | Switch to a "worst-fit with a cap" rule: among bins whose residual after placement stays above a ... |
| 21 | edit | not_better | 0.8663 | 0.9590 | $0.0005 | I'll add a "consolidation" phase just before opening a fresh bin: when no used bin fits the item ... |
| 22 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace the deterministic best-fit rule with a randomized choice among a small set of near-b... |
| 23 | edit | not_better | 0.8253 | 0.9590 | $0.0006 | I'll switch to a smarter online rule: use best-fit normally, but when the arriving item is large ... |
| 24 | edit | not_better | 0.9045 | 0.9590 | $0.0005 | I'll replace the deterministic best-fit with a two-regime rule: compute a running mean item size ... |
| 25 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace plain best-fit with a rule that mixes the classic best-fit score with a small bonus ... |
| 26 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Use best-fit (minimize residual after placement) but break ties — and near-ties within a small ma... |
| 27 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I will use a two-parameter classic online heuristic: score bins by a signed power of the post-pla... |
| 28 | edit | not_better | 0.9590 | 0.9590 | $0.0007 | Leveraging the strong baseline of best-fit, I'll add a "reserve the last gap" improvement: when p... |
| 29 | edit | not_better | 0.9331 | 0.9590 | $0.0006 | Replace pure best-fit with best-fit that additionally avoids leaving tiny unusable residuals: amo... |
| 30 | edit | not_better | 0.9590 | 0.9590 | $0.0007 | Best fit wastes the largest bins early; I will instead try a "modified best-fit with lookahead to... |
| 31 | edit | improved | 0.9693 | 0.9693 | $0.0006 | I'll replace pure best-fit with a "best-fit but avoid leaving a residual that is too small to be ... |
| 32 | edit | not_better | 0.9693 | 0.9693 | $0.0007 | I'll make the residual threshold adaptive to the current item's size: only reject a tight best-fi... |
| 33 | edit | not_better | 0.9693 | 0.9693 | $0.0007 | I'll combine the residual-guard best-fit with a biased tie-breaking that, among bins whose post-p... |
| 34 | edit | not_better | 0.9572 | 0.9693 | $0.0007 | I'll replace the fragile single-guard logic with a smoothed "fit-quality" ranking: score each bin... |
| 35 | edit | not_better | 0.9508 | 0.9693 | $0.0007 | I'll replace the guard heuristic with a smooth, state-free scoring that mirrors best fit but shif... |
| 36 | edit | not_better | 0.9592 | 0.9693 | $0.0009 | Replace the residual-guard logic with a "complement-matching" best-fit: track a short window of r... |
| 37 | edit | not_better | 0.9693 | 0.9693 | $0.0007 | I'll replace best-fit with a "worst-fit-like greedy" that tries to keep bins near-full by adding ... |
| 38 | edit | not_better | 0.9693 | 0.9693 | $0.0007 | I will try a "best-fit with a full-bin/reopen avoidance" tweak: among bins whose post-placement r... |
| 39 | edit | not_better | 0.9590 | 0.9693 | $0.0005 | I'll replace the heuristic guard with a stateless "best fit with fresh-bin deferral" rule: always... |
| 40 | edit | not_better | 0.9590 | 0.9693 | $0.0007 | I'll replace the fragile residual-guard branch with a robust interval-based best-fit: track a run... |
| 41 | edit | not_better | 0.9590 | 0.9693 | $0.0006 | I'll replace the current guard heuristic with a "best fit by item-size-bucket" strategy that keep... |
| 42 | edit | not_better | 0.9590 | 0.9693 | $0.0007 | I'll replace the heuristic with a clean, well-known strong rule: "best fit decreasing-style" is u... |
| 43 | edit | not_better | 0.9590 | 0.9693 | $0.0007 | I'll switch to a score that ranks bins by their post-placement residual but with a squared emphas... |
| 44 | edit | not_better | 0.9590 | 0.9693 | $0.0005 | I will replace the current guard heuristic with a straightforward "best fit + exact residual matc... |
| 45 | edit | not_better | 0.9590 | 0.9693 | $0.0005 | I will replace the heuristic guard with a "best fit on full residual, else best fit" rule using a... |
| 46 | edit | not_better | 0.9590 | 0.9693 | $0.0007 | I will replace the hard guard with a smooth convex score that strongly prefers the tightest fit b... |
| 47 | edit | improved | 0.9707 | 0.9707 | $0.0008 | I'll add a fast-path that detects an exact residual match with a common small item size (tracked ... |
| 48 | edit | not_better | 0.9634 | 0.9707 | $0.0009 | I'll broaden the exact-residual fast path to accept an exact match with the current item size as ... |
| 49 | edit | not_better | 0.9707 | 0.9707 | $0.0009 | I'll add a "least-satisfiable" guard: when the best-fit residual is small but nonzero, check whet... |
| 50 | edit | not_better | 0.9700 | 0.9707 | $0.0010 | I'll add a "combine" fast path: when the current item is small and there exists a used bin whose ... |
| 51 | edit | not_better | 0.9546 | 0.9707 | $0.0009 | I'll replace the mode-based exact-residual fast path with a "pair-matching" rule: track the recen... |
| 52 | edit | not_better | 0.9707 | 0.9707 | $0.0015 | I'll make the guard branch reuse the exact-residual fast path: when the plain best fit would leav... |
| 53 | edit | not_better | 0.9700 | 0.9707 | $0.0010 | Replace the crude integer-halving mode tracker with a continuously-decaying exponentially-weighte... |
| 54 | edit | not_better | 0.9684 | 0.9707 | $0.0008 | I'll tune the exponential decay rates and guard threshold: use faster decay (0.01) for the small-... |
| 55 | edit | not_better | 0.9592 | 0.9707 | $0.0008 | I'll bias selection toward bins whose residual after placement is itself at least as large as a t... |
| 56 | edit | not_better | 0.9590 | 0.9707 | $0.0008 | Replace the hard-threshold guard and mode fast-path with a single smooth scoring rule: pure best-... |
| 57 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the mode-based exact-residual fast path with a harmonic-style score that rewards bin... |
| 58 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll remove the disruptive guard branch and mode fast path entirely, replacing them with a single... |
| 59 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the hand-tuned heuristic with the classic "best fit plus sum-of-squares-aware balanc... |
| 60 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | Replace the brittle mode fast path and guard with a proper Best-Fit-Decreasing-style rule augment... |
| 61 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the ad-hoc mode/guard heuristics with the classic Best-Fit rule that also keeps the ... |
| 62 | edit | not_better | 0.9679 | 0.9707 | $0.0009 | I'll generalize the exact-match fast path: instead of matching only the single most-common small ... |
| 63 | edit | not_better | 0.9223 | 0.9707 | $0.0010 | The lower bound is 100/mean ≈ 2.5 items per bin, so waste of ~2-3 capacity units per bin is the d... |
| 64 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the ad-hoc heuristics with a principled "best fit with a lookahead-aware residual bo... |
| 65 | edit | not_better | 0.9593 | 0.9707 | $0.0007 | I'll replace the brittle mode fast path with a proper "harmonic/best-fit hybrid": score each bin ... |
| 66 | edit | not_better | 0.9560 | 0.9707 | $0.0009 | I'll add a "residual-fill" bonus to the existing best-fit-plus-guard rule: keep the exact-match f... |
| 67 | edit | not_better | 0.9351 | 0.9707 | $0.0007 | I'll replace the brittle mode/guard heuristic with a cleaner two-stage rule: pure best-fit (score... |
| 68 | edit | not_better | 0.9590 | 0.9707 | $0.0008 | I'll replace the brittle mode/guard heuristics with a principled "Best Fit with a small-residual ... |
| 69 | edit | not_better | 0.9665 | 0.9707 | $0.0009 | I'll add a "sweet-spot" preference to the exact-match fast path: instead of only matching a bin w... |
| 70 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the brittle mode-based fast path with a tuned multi-residual scoring rule: keep pure... |
| 71 | edit | not_better | 0.9590 | 0.9707 | $0.0005 | I'll replace the heuristic with pure Best-Fit (score = -residual), since the repeated failures of... |
| 72 | edit | not_better | 0.9590 | 0.9707 | $0.0008 | Replace the hard mode fast-path and brittle guard with pure best-fit plus a small additive bonus ... |
| 73 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the brittle mode/guard heuristics with an online "harmonic-style" scoring that combi... |
| 74 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | Use a principled "full-bin packing" fast path: before falling back to best fit, check whether any... |
| 75 | edit | not_better | 0.9700 | 0.9707 | $0.0016 | Keep the winning exact-residual-match fast path, but replace the coarse "halve every 500 items" m... |
| 76 | edit | not_better | 0.9590 | 0.9707 | $0.0009 | I will combine the current exact-residual-match fast path with a Best-Fit that breaks ties toward... |
| 77 | edit | not_better | 0.9691 | 0.9707 | $0.0009 | I'll refine the fast path's target residual to consider a small set of the most frequent recent s... |
| 78 | edit | not_better | 0.9586 | 0.9707 | $0.0009 | I'll generalize the fast path from a single mode to the set of most-frequent recent small item si... |
| 79 | edit | not_better | 0.9351 | 0.9707 | $0.0008 | Replace the ad-hoc mode/guard heuristics with a principled "best fit with exact-fit priority plus... |
| 80 | edit | not_better | 0.9688 | 0.9707 | $0.0008 | I'll replace the ad-hoc mode/guard logic with a clean, well-known strong online rule: Best-Fit, b... |
| 81 | edit | not_better | 0.9551 | 0.9707 | $0.0008 | I will replace the fragile mode/small-item heuristics with a principled best-fit rule that uses a... |
| 82 | edit | not_better | 0.9590 | 0.9707 | $0.0008 | I'll keep the exact-residual-match fast path but make the match target only be accepted when it i... |
| 83 | edit | not_better | 0.9702 | 0.9707 | $0.0011 | Keep the winning single-target exact-residual fast path and pure best-fit fallback unchanged, but... |
| 84 | edit | not_better | 0.9688 | 0.9707 | $0.0008 | I'll tune the fast-path to target the mode of *all* recent items (not capped at 40) with per-item... |
| 85 | edit | not_better | 0.8783 | 0.9707 | $0.0006 | I'll replace the fragile mode/exact-match heuristics with a robust ranking that combines best-fit... |
| 86 | edit | not_better | 0.9632 | 0.9707 | $0.0010 | I'll add a complementary "worst-fit among small-residual bins" avoidance: instead of only forcing... |
| 87 | edit | invalid | 0.0000 | 0.9707 | $0.0009 | I will replace the risky "force exact mode match" fast path with a robust two-pronged rule: alway... |
| 88 | edit | not_better | 0.9644 | 0.9707 | $0.0006 | I'll replace the heuristic-heavy rule with a principled scoring function that prefers exact fits ... |
| 89 | edit | not_better | 0.9588 | 0.9707 | $0.0008 | I'll keep the strong best-fit base but add a safe, well-gated exact-fill fast path (residual 0) p... |
| 90 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the current stateful mode-based fast path with a clean, stateless best-fit that adds... |
| 91 | edit | not_better | 0.9590 | 0.9707 | $0.0009 | Replace the risky forced exact-residual fast path with a soft bounded bonus added to best-fit, so... |
| 92 | edit | not_better | 0.9590 | 0.9707 | $0.0008 | I'll keep the strong best-fit base but replace the aggressive forced exact-match fast path with a... |
| 93 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the fragile forced exact-mode-match fast path (which often jumps to a suboptimal bin... |
| 94 | edit | not_better | 0.9590 | 0.9707 | $0.0005 | I'll replace the stateful mode-based forced exact-match fast path with a clean, stateless rule: p... |
| 95 | edit | not_better | 0.9707 | 0.9707 | $0.0009 | I'll keep the current strong exact-match fast path but gate it so it only fires when the match is... |
| 96 | edit | not_better | 0.9693 | 0.9707 | $0.0009 | I'll replace the fragile single-mode forced fast path with a bounded soft bonus for residuals mat... |
| 97 | edit | not_better | 0.9693 | 0.9707 | $0.0009 | I'll make the exact-residual fast path prefer the best-fit bin when the mode-match residual is no... |
| 98 | edit | not_better | 0.9595 | 0.9707 | $0.0006 | I'll replace the fragile stateful forced-match fast path with a clean, stateless "best fit with a... |
| 99 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the fragile forced exact-mode-match fast path with an adaptive "fractional best-fit"... |
| 100 | edit | not_better | 0.9634 | 0.9707 | $0.0009 | I'll replace the fragile forced-mode fast path with a distribution-aware best-fit that prefers re... |
| 101 | edit | not_better | 0.9604 | 0.9707 | $0.0009 | I'll replace the single-mode hard forced jump with a soft, frequency-weighted bonus for residuals... |
| 102 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the fragile forced exact-mode-match fast path with pure best-fit (rank by decreasing... |
| 103 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll revert to the current best-performing structure but replace the fragile single-mode forced f... |
| 104 | edit | not_better | 0.9632 | 0.9707 | $0.0007 | I'll keep the proven best-fit base with its dead-gap guard, but make the fast-path match use the ... |
| 105 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the noisy cumulative-mode exact-match fast path with a robust two-part rule: keep be... |
| 106 | edit | not_better | 0.9632 | 0.9707 | $0.0008 | I'll make the exact-match fast path target the single most-recent small item size (a cleaner pred... |
| 107 | edit | not_better | 0.9705 | 0.9707 | $0.0007 | The mode-match fast path uses a global all-time counter that is too noisy; I'll replace it with a... |
| 108 | edit | not_better | 0.9693 | 0.9707 | $0.0006 | I'll replace the fragile forced-mode fast path with a standard best-fit-decreasing-like rule but ... |
| 109 | edit | not_better | 0.9700 | 0.9707 | $0.0007 | I'll replace the noisy cumulative-mode fast path with a proper nearest-fit rule: score bins by ho... |
| 110 | edit | not_better | 0.9351 | 0.9707 | $0.0008 | I'll replace the fragile forced exact-mode fast path with a cleaner, well-known strong rule: rank... |
| 111 | edit | not_better | 0.9686 | 0.9707 | $0.0010 | Replace the single-mode exact-residual fast path with a lookup that accepts a small set of target... |
| 112 | edit | not_better | 0.9590 | 0.9707 | $0.0008 | I'll replace the hard exact-mode fast path and the dead-gap guard with a single soft scoring rule... |
| 113 | edit | not_better | 0.9549 | 0.9707 | $0.0007 | I'll replace the all-time noisy mode counter with the standard, well-proven "best fit with a smal... |
| 114 | edit | not_better | 0.8120 | 0.9707 | $0.0008 | I will replace the exact-residual fast path with a "best fit with gap-avoidance using a percentil... |
| 115 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I will replace the fragile mode-match heuristic with a classic best-fit rule plus a tie-breaker t... |
| 116 | edit | not_better | 0.9576 | 0.9707 | $0.0008 | I'll keep the strong exact-residual fast path but make its target a small window (mode and a coup... |
| 117 | edit | not_better | 0.9565 | 0.9707 | $0.0008 | I will keep the strong exact-residual match but change the fallback from pure best-fit to a "best... |
| 118 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the exact single-mode match with a softer "hole-filling" bonus: score bins by best-f... |
| 119 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll switch the primary rule to a well-tested "best fit with a residual-reuse lookahead": instead... |
| 120 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the brittle exact-mode fast path with a tried-and-true approach: strict best-fit (sm... |
| 121 | edit | not_better | 0.9581 | 0.9707 | $0.0014 | I'll keep the winning exact-residual fast path but simplify the fallback to a clean best-fit (no ... |
| 122 | edit | not_better | 0.9592 | 0.9707 | $0.0008 | I'll add a second fast path: when an item is large (most of a bin), prefer a bin whose remaining ... |
| 123 | edit | not_better | 0.9590 | 0.9707 | $0.0005 | I will drop the brittle "exact-residual mode" fast path and the dead-gap guard, replacing them wi... |
| 124 | edit | not_better | 0.9579 | 0.9707 | $0.0007 | I will keep the strong exact-residual fast path but broaden its target from the single recent mod... |
| 125 | edit | not_better | 0.9700 | 0.9707 | $0.0009 | The current fast path uses the single most frequent small item, which is brittle; I'll keep the s... |
| 126 | edit | not_better | 0.9679 | 0.9707 | $0.0011 | The current rule's fallback ignores bin index order and uses `-residual`, which among equal resid... |
| 127 | edit | not_better | 0.8952 | 0.9707 | $0.0008 | The current fast path only matches the single most frequent recent small item, which is brittle; ... |
| 128 | edit | not_better | 0.7773 | 0.9707 | $0.0008 | I'll replace the fragile mode-based fast path with a robust "prefer exact residual matches agains... |
| 129 | edit | not_better | 0.9590 | 0.9707 | $0.0005 | I'll replace the brittle mode/guard fast paths with a well-tested, robust rule: best-fit (smalles... |
| 130 | edit | not_better | 0.8964 | 0.9707 | $0.0007 | I'll replace the brittle mode/guard logic with a robust "match any recent observed small-item siz... |
| 131 | edit | not_better | 0.9707 | 0.9707 | $0.0009 | I'll make the mode-based fast path more robust by tracking not just the single most frequent smal... |
| 132 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the brittle single-mode exact-residual fast path with a score that is the usual best... |
| 133 | edit | not_better | 0.9560 | 0.9707 | $0.0008 | The current rule's fallback is pure best-fit, which is already strong, but its exact-residual fas... |
| 134 | edit | not_better | 0.9592 | 0.9707 | $0.0008 | I'll strengthen the fallback by breaking best-fit ties (equal residuals) toward the bin with the ... |
| 135 | edit | not_better | 0.8948 | 0.9707 | $0.0008 | I'll redirect the brittle fast path: track the most recent item sizes in a bounded window and, wh... |
| 136 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll simplify to a robust best-fit that breaks ties among equal residuals toward the bin with lar... |
| 137 | edit | not_better | 0.9579 | 0.9707 | $0.0007 | The exact-residual fast path currently only fires for a single stale mode; I'll make it more robu... |
| 138 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the fragile mode-based fast path with a weighted "hole suitability" score: prefer th... |
| 139 | edit | not_better | 0.8992 | 0.9707 | $0.0008 | I will make the small-item fast path adaptive and less brittle: instead of a single decaying mode... |
| 140 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | The previous attempts to add clever residual/hole heuristics all hurt. I'll simplify to pure best... |
| 141 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | All the clever residual/mode heuristics hurt, so I'll simplify to a clean best-fit rule but add t... |
| 142 | edit | not_better | 0.9590 | 0.9707 | $0.0006 | I'll replace the brittle exact-residual fast path with a best-fit-plus tie-break that prefers, am... |
| 143 | edit | not_better | 0.9574 | 0.9707 | $0.0008 | Recent attempts show that the residual/mode fast path is the only thing lifting the score above p... |
| 144 | edit | not_better | 0.9688 | 0.9707 | $0.0010 | Keep the proven structure (exact-residual fast path + best-fit guard) but broaden the fast path f... |
| 145 | edit | not_better | 0.9351 | 0.9707 | $0.0009 | I'll make the exact-residual fast path fire only when the match is genuinely likely: track a rece... |
| 146 | edit | not_better | 0.8937 | 0.9707 | $0.0009 | I'll make the exact-residual fast path more reliable by preferring, among all bins whose post-pla... |
| 147 | edit | not_better | 0.9705 | 0.9707 | $0.0009 | I'll fix an inconsistency that is likely costing accuracy: the fast path compares `residual == m`... |
| 148 | edit | not_better | 0.9590 | 0.9707 | $0.0005 | I will replace the mode-based exact-match fast path with a principled variant of best fit that sc... |
| 149 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the fragile mode-based exact-residual fast path with a cleaner, more robust mechanis... |
| 150 | edit | not_better | 0.9590 | 0.9707 | $0.0007 | I'll replace the fragile mode-based exact-match fast path with a continuous, distribution-aware b... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,74 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Best fit with an exact-residual-match fast path driven by the recent small-item mode."""
 import numpy as np
 
 
+class _State:
+    def __init__(self):
+        self.small = 10.0   # running estimate of a "small" item size
+        self.n = 0
+        self.counts = {}    # recent counts of small item sizes (for mode)
+
+    def update(self, item):
+        self.n += 1
+        s = float(min(item, 40))
+        self.small = 0.98 * self.small + 0.02 * s
+        if self.small < 3.0:
+            self.small = 3.0
+        # track mode of small item sizes seen recently (bounded memory)
+        if item <= 40:
+            self.counts[item] = self.counts.get(item, 0) + 1
+            if self.n % 500 == 0:
+                # decay counts to keep it "recent"
+                for k in list(self.counts.keys()):
+                    self.counts[k] = self.counts[k] // 2
+                    if self.counts[k] == 0:
+                        del self.counts[k]
+
+    def mode_small(self):
+        best_k, best_v = 0, 0
+        for k, v in self.counts.items():
+            if v > best_v:
+                best_v, best_k = v, k
+        return best_k
+
+
+_state = _State()
+
+
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority per bin: prefer an exact residual match, else best fit with a guard."""
+    _state.update(item)
+    bins = np.asarray(bins)
+    residual = bins - item  # post-placement residual per bin
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    # Fast path: an existing used bin whose residual exactly matches a common small item.
+    m = _state.mode_small()
+    if m > 0:
+        match = np.where((residual == m) & (bins < 100))[0]
+        if match.size > 0:
+            score = np.full(bins.shape, -1e9, dtype=np.float64)
+            score[match[0]] = 1.0
+            return score
+
+    residual = bins - item
+    thresh = 0.6 * _state.small  # residual below this is hard to reuse
+
+    order = np.argsort(residual, kind="stable")
+    best = order[0]
+    best_res = residual[best]
+
+    if best_res <= 0 or best_res >= thresh:
+        score = -residual.astype(np.float64)
+        return score
+
+    usable = np.where((residual >= thresh) & (bins < 100))[0]
+    if usable.size > 0:
+        j = usable[np.argmin(residual[usable])]
+        score = np.full(bins.shape, -1e9, dtype=np.float64)
+        score[j] = 1.0
+        return score
+
+    return -residual.astype(np.float64)
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (28 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 43 | `residual = bins - item` | -0.9707 | essential: the program fails or turns invalid without it |
| 46 | `m = _state.mode_small()` | -0.9707 | essential: the program fails or turns invalid without it |
| 55 | `thresh = 0.6 * _state.small` | -0.9707 | essential: the program fails or turns invalid without it |
| 57 | `order = np.argsort(residual, kind='stable')` | -0.9707 | essential: the program fails or turns invalid without it |
| 58 | `best = order[0]` | -0.9707 | essential: the program fails or turns invalid without it |
| 59 | `best_res = residual[best]` | -0.9707 | essential: the program fails or turns invalid without it |
| 62 | `score = -residual.astype(np.float64)` | -0.9707 | essential: the program fails or turns invalid without it |
| 65 | `usable = np.where((residual >= thresh) & (bins < 100))[0]` | -0.9707 | essential: the program fails or turns invalid without it |
| 67 | `j = usable[np.argmin(residual[usable])]` | -0.9707 | essential: the program fails or turns invalid without it |
| 68 | `score = np.full(bins.shape, -1000000000.0, dtype=np.float64)` | -0.9707 | essential: the program fails or turns invalid without it |
| 61 | `if best_res <= 0 or best_res >= thresh: ...` | -0.0336 | matters |
| 63 | `return score` | -0.0336 | matters |
| 41 | `_state.update(item)` | -0.0161 | matters |
| 66 | `if usable.size > 0: ...` | -0.0115 | matters |
| 70 | `return score` | -0.0115 | matters |
| 69 | `score[j] = 1.0` | -0.0110 | matters |
| 43 | `term - item` | -0.0014 | no effect alone |
| 43 | `term + bins` | -0.0014 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 42: `bins = np.asarray(bins)`
- line 47: `if m > 0: ...`
- line 48: `match = np.where((residual == m) & (bins < 100))[0]`
- line 49: `if match.size > 0: ...`
- line 50: `score = np.full(bins.shape, -1000000000.0, dtype=np.float64)`
- line 51: `score[match[0]] = 1.0`
- line 52: `return score`
- line 54: `residual = bins - item`
- line 54: `term + bins`
- line 54: `term - item`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9707 | 0.9709 |
| minimal (4 parts removed) | 0.9693 | 0.9712 |

Minimal program:

```python
"""Best fit with an exact-residual-match fast path driven by the recent small-item mode."""
import numpy as np

class _State:

    def __init__(self):
        self.small = 10.0
        self.n = 0
        self.counts = {}

    def update(self, item):
        self.n += 1
        s = float(min(item, 40))
        self.small = 0.98 * self.small + 0.02 * s
        if self.small < 3.0:
            self.small = 3.0
        if item <= 40:
            self.counts[item] = self.counts.get(item, 0) + 1
            if self.n % 500 == 0:
                for k in list(self.counts.keys()):
                    self.counts[k] = self.counts[k] // 2
                    if self.counts[k] == 0:
                        del self.counts[k]

    def mode_small(self):
        best_k, best_v = (0, 0)
        for k, v in self.counts.items():
            if v > best_v:
                best_v, best_k = (v, k)
        return best_k
_state = _State()

def priority(item, bins):
    """Return a priority per bin: prefer an exact residual match, else best fit with a guard."""
    _state.update(item)
    residual = bins - item
    m = _state.mode_small()
    thresh = 0.6 * _state.small
    order = np.argsort(residual, kind='stable')
    best = order[0]
    best_res = residual[best]
    if best_res <= 0 or best_res >= thresh:
        score = -residual.astype(np.float64)
        return score
    usable = np.where((residual >= thresh) & (bins < 100))[0]
    if usable.size > 0:
        j = usable[np.argmin(residual[usable])]
        score = np.full(bins.shape, -1000000000.0, dtype=np.float64)
        score[j] = 1.0
        return score
    return -residual.astype(np.float64)
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_a5000 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 1
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_a5000-s1   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c5b977554525335eb384e9d226a9b80e95f909c2`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_a5000/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_a5000/initial.py` `609927c5ea619a94`
- `problems/bp_sh_a5000/problem.md` `190017a698e23cd8`
- `problems/bp_sh_a5000/verify.py` `0c52b77a6e5ec18a`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
