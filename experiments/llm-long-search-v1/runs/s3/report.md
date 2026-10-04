# Research loop report: bin_packing_online

| | |
|---|---|
| problem | `bin_packing_online` |
| search | lean, 300 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.2100 of a $0.75 hard cap, 300 calls, 677,767 tokens |
| wall time | search 2221 s, baselines 44 s, explain 74 s |
| stopped | max_iters (stopped_early) |
| evaluations | 300 (296 valid), 16 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9922 | 0.9933 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online/baselines/funsearch_weibull.py` |
| minimal program (ablation) | 0.9922 | 0.9933 | 1 parts removed |

Audit: public 0.9616 → 0.9922 (+0.0306), hidden 0.9604 → 0.9933 (+0.0328); public − hidden gap of the final program -0.0010.

Against the baselines: the final program's public score is below the best baseline (`funsearch_weibull`, 0.9925). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace pure best-fit with a hybrid rule: apply best-fit only for small items, but for larger ite... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace pure best-fit with a rule that combines best-fit with a small preference for leaving "med... |
| 3 | edit | not_better | 0.9616 | 0.9616 | $0.0003 | Replace pure best-fit with a rule that strongly prefers exact/tight fits but also gives unused bi... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Implement a classic fixed-size bucketing policy: bins with remaining capacity ≤10, ≤20, ≤30, … (u... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a two-stage rule: among fitting bins, first prefer non-empty bins (rem... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use a two-part score that primarily maximizes utilization by best-fit, but adds a small tie-break... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with an online harmonic/geometric-bucketing rule: assign each arriving item... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Use a "best fit decreasing"-inspired online rule that also considers a small lookahead via a lear... |
| 9 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Implement a score that is a blend of best-fit and worst-fit: for each bin, score mainly by tighte... |
| 10 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Add an adaptive scheme that records recent item sizes and, after placing an item, mildly rewards ... |
| 11 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a two-parameter tuned rule that adds a small bonus proportional to how... |
| 12 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a score combining tightest fit and a bonus for leaving a residual capa... |
| 13 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll implement a "best fit with a reserve/slack parameter" rule inspired by the classic Best-Fit ... |
| 14 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a combined scoring rule that uses best-fit as the primary term but add... |
| 15 | edit | invalid | 0.0000 | 0.9616 | $0.0005 | Add a tiny secondary term that prefers leaving a residual capacity which has occurred often as an... |
| 16 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | The pure best-fit baseline is already strong, so instead of perturbing the primary criterion, I'l... |
| 17 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add a bounded, distribution-agnostic secondary tie-break that slightly favors leaving residu... |
| 18 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace best-fit with a classic "sum-of-squares" / harmonic-style rule: score each fitting bin by... |
| 19 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace the pure best-fit rule with a classic scoring approach ("Sum of Squares" / almost-worst-f... |
| 20 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will switch to the classic "Almost Worst Fit" (AWF) variant of best-fit by perturbing the best-... |
| 21 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the pure best-fit rule with a learned/adaptive scoring based on the classic "Harmonic" bi... |
| 22 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll keep best-fit as the core but add a small penalty when placing the item would leave the bin ... |
| 23 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a hybrid: compute the best-fit residual, and if placing the item ... |
| 24 | edit | not_better | 0.3961 | 0.9616 | $0.0006 | Replace the pure best-fit score with the "best-fit via potential reduction" rule: score each cand... |
| 25 | edit | not_better | 0.3961 | 0.9616 | $0.0006 | I'll switch the core rule from best-fit to a bounded "worst-fit" preference (place into the empti... |
| 26 | edit | not_better | 0.9616 | 0.9616 | $0.0015 | Replace pure best-fit with a harmonic-class bin-choice rule: partition capacity into harmonic int... |
| 27 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a rule that combines best-fit tightness with a small bonus for leaving... |
| 28 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Switch to a pure best-fit rule with a tiny deterministic tie-break that prefers leaving the small... |
| 29 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add an adaptive best-fit that, when the item can only fit in bins whose post-placement residual i... |
| 30 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit with smoothing" rule using the residual left in each bin: ... |
| 31 | edit | not_better | 0.8154 | 0.9616 | $0.0005 | I'll replace pure best-fit with a hybrid that uses best-fit but, among bins whose post-placement ... |
| 32 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a practical "best-fit decreasing-style" enhancement: combine best-fit ... |
| 33 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a rule that combines best-fit tightness with the classic online-p... |
| 34 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Pure best-fit is already near-optimal for this distribution, so the remaining losses come from a ... |
| 35 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit with post-placement residual classification" rule: compute... |
| 36 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Add a small priority bonus when the placement leaves the bin exactly full (residual 0), since a p... |
| 37 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a rule that prefers, among bins with the same tight residual, the bin ... |
| 38 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Pure best-fit is already near-optimal, so gains must come from handling the many unused/fresh bin... |
| 39 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a rule that first exhausts near-full bins by preferring placements lea... |
| 40 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best fit (tightest residual) with a two-regime rule: normally choose the tightest fi... |
| 41 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Pure best-fit is near-optimal here, so I'll shift from deterministic tightness to a randomized be... |
| 42 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Introduce a small "sum-of-residuals" (a.k.a. gap-greedy) tie-break: primary score is still tightn... |
| 43 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "sum-of-squares-of-fill" (Hochbaum-Shmoys-style) rule: score each ca... |
| 44 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a lookahead-aware rule based on the expected distribution: use be... |
| 45 | edit | not_better | 0.3961 | 0.9616 | $0.0004 | Introduce a "worst-fit-with-cap" strategy: choose the bin with the largest remaining capacity amo... |
| 46 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Introduce a hybrid rule that mirrors the strong online heuristics: use best-fit (tightest residua... |
| 47 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add lightweight stateful capacity tracking: maintain a per-instance adaptation that, when be... |
| 48 | edit | not_better | 0.9579 | 0.9616 | $0.0008 | Replace deterministic best-fit with a randomized best-fit that, on each call, picks uniformly amo... |
| 49 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit with a tunable cap on wasting residual": among bins that f... |
| 50 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace pure best-fit with a distribution-aware residual score: still prefer tight fits, but pena... |
| 51 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a distribution-aware rule: maintain an online histogram of observed it... |
| 52 | edit | not_better | 0.9614 | 0.9616 | $0.0011 | Replace pure best-fit with a "best-fit with reserved slack" rule: compute the tightest fit, but a... |
| 53 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll switch to a "best fit with a tiny reverse tiebreak toward fuller bins" — pure best fit alrea... |
| 54 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I will replace pure best-fit with a hybrid "best-fit-decreasing-emulation" rule: since items arri... |
| 55 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace pure best-fit with a "best-fit plus harmonic residual avoidance" rule that keeps b... |
| 56 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit with a small adaptive reserve" rule: keep tightest-fit as ... |
| 57 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll try a "Best-Fit with occasional worst-fit escape": keep best-fit as the primary rule, but ma... |
| 58 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from pure best-fit to a "best-fit with a reverse-order tiebreak on index": the key id... |
| 59 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the pure best-fit rule with a linear-programming-inspired "best-fit with adaptive small-i... |
| 60 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a two-key rule: keep tightest-fit as the primary key, but break ties b... |
| 61 | edit | not_better | 0.3961 | 0.9616 | $0.0005 | I'll switch from best-fit to worst-fit (prefer the emptiest bin the item fits in) — for a heavy-t... |
| 62 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Instead of always choosing the tightest fit, use a "best-fit-decreasing style" rule that prefers ... |
| 63 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will add a small "almost-full bin" penalty using a soft threshold: keep best-fit as the primary... |
| 64 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace pure best-fit with a "best-fit plus tuned residual bonus" rule: primary score still ... |
| 65 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace the pure per-call best-fit with a stateful "harmonic/geometric-mean-aware best fit":... |
| 66 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | The previous variants all kept a myopic one-item-at-a-time best fit; bin packing improves markedl... |
| 67 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch the ranking from best-fit to a "least-loaded feasible bin" rule scaled by a small fac... |
| 68 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add a small stateful "reserve" heuristic: keep best-fit as the primary key but subtract a ti... |
| 69 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace myopic best-fit with a stateful "sum-of-squares" style rule: track a running estimate of ... |
| 70 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | Replace the myopic best-fit with a stateful "harmonic fit" that tracks the running mean item size... |
| 71 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the greedy best-fit with a stateful "undirected best-fit with a dual-power score" th... |
| 72 | edit | not_better | 0.9616 | 0.9616 | $0.0012 | Implement a harmonic-style online packing rule (Refined Harmonic family): classify each item by s... |
| 73 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Implement a harmonic-style classification where items above 50 (which cannot be paired with anoth... |
| 74 | edit | not_better | 0.7087 | 0.9616 | $0.0005 | Implement First-Fit-Decreasing-like "worst-fit with cap": among bins where the item fits, prefer ... |
| 75 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Reintroduce a small stateful nudge on top of best-fit: prefer bins whose post-placement residual ... |
| 76 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a bounded "best-fit plus light bin-count-pressure" rule: keep tightest... |
| 77 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with the classic "best-fit with careful handling of large items" appr... |
| 78 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace myopic best-fit with a stateful "reserve small residuals" rule: primary key is tightest f... |
| 79 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a "best-fit that also avoids leaving unusably small residuals": keep t... |
| 80 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a stateful rule that, in addition to tightest fit, breaks ties t... |
| 81 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a stateful score that combines tightest-fit (to minimize waste) with a... |
| 82 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace myopic best-fit with a learned, offline-style rule based on the known item distribution: ... |
| 83 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a two-stage rule: among all feasible bins, choose the one minimiz... |
| 84 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use a "best-fit with occasionally opening a new bin" rule: normally place into the tightest-fitti... |
| 85 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace the myopic best-fit with a distribution-aware rule based on the known Weibull-like item d... |
| 86 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure myopic best-fit with "best-fit plus a best-fit-decreasing-style lookahead": prioriti... |
| 87 | edit | not_better | 0.9607 | 0.9616 | $0.0005 | Replace the pure best-fit (minimize residual) with a "best-fit-decreasing-aware" score: minimize ... |
| 88 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add a "sum-of-squares" (discrete harmonic-aware) tie-breaking on top of best fit: score each bin ... |
| 89 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | The pure best-fit rule is strong, but a known improvement for online bin packing is "best fit wit... |
| 90 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace the myopic best-fit with a modified best-fit that uses a fixed "almost-full preference" h... |
| 91 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Introduce a stateful "reserve a nearly-empty bin" idea: track recent item sizes and, when the arr... |
| 92 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a randomized/heuristic "best-fit with a perturbation that prefers star... |
| 93 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | Add a small tie-breaking bonus that prefers already-occupied bins over empty ones (so residual ti... |
| 94 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll use a stateful "best-fit with one-item lookahead refinement": maintain a moving estimate of ... |
| 95 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I will replace the myopic best-fit rule with a "best-fit plus residual-probability" variant: I ke... |
| 96 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | Replace pure best-fit with a size-bucketed "best fit among good fit classes" rule: items are plac... |
| 97 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the myopic best-fit with a "best-fit with a small reservation penalty": still primar... |
| 98 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace the myopic best-fit with a Harmonic-style threshold rule computed directly on residu... |
| 99 | edit | not_better | 0.3975 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit among bins that can be closed or filled well" rule: comput... |
| 100 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Replace the myopic best-fit with a stateful "reserve the best-fit bin for near-exact items" rule:... |
| 101 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Best-fit is strong, but the well-known improvement over best-fit in online bin packing is to avoi... |
| 102 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a weighted best-fit that combines the tightness of fit with the bin's ... |
| 103 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Use a tuned "best fit decreasing-like" rule: pure best-fit (maximize remaining fit tightness) is ... |
| 104 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | Instead of pure myopic best-fit, use a stateful rule that tracks a running estimate of the item-s... |
| 105 | edit | not_better | 0.9309 | 0.9616 | $0.0007 | Implement a stateful threshold-aware best-fit: keep a running histogram of observed item sizes to... |
| 106 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Best-fit is hard to beat myopically, so I'll add a light stateful improvement: track a running hi... |
| 107 | edit | not_better | 0.9449 | 0.9616 | $0.0005 | Replace the myopic best-fit score with a "best-fit except avoid tiny residuals" rule: primary pre... |
| 108 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Best-fit is already optimal among static myopic rules, so the gains must come from a smarter dyna... |
| 109 | edit | not_better | 0.9382 | 0.9616 | $0.0006 | Replace myopic best-fit with a stateful "shelf/level" rule: track the largest currently open bin ... |
| 110 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a randomized-tie best-fit: when multiple bins tie on tightest residual... |
| 111 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace the linear tightness score with a mildly convex scoring of the residual that still centra... |
| 112 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | Use a smooth convex reshaping of the residual that strongly rewards exact fits and otherwise mild... |
| 113 | edit | invalid | 0.0000 | 0.9616 | $0.0006 | Replace myopic best-fit with a stateful "sampling/matching" rule: keep a running histogram of obs... |
| 114 | edit | not_better | 0.3975 | 0.9616 | $0.0006 | Best-fit wastes bins because it always closes small residuals; I'll replace it with a stateful ru... |
| 115 | edit | not_better | 0.9614 | 0.9616 | $0.0006 | Replace pure best-fit with a hybrid rule that uses best-fit normally but, when the residual would... |
| 116 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Combine best-fit with an exact-fit-first rule that also prefers the bin whose residual after plac... |
| 117 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Introduce a two-phase policy: always place the item in a bin with an exact fit if one exists (res... |
| 118 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a "best-fit with a small preference for stale/emptier bins on near-tie... |
| 119 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use the classic "best fit decreasing"-style improvement for online packing: score bins by how the... |
| 120 | edit | not_better | 0.3971 | 0.9616 | $0.0005 | I'll replace best-fit with a "best-fit with a reservoir of larger-but-still-packable residuals": ... |
| 121 | edit | not_better | 0.6875 | 0.9616 | $0.0009 | I'll switch from myopic best-fit to a stateful rule inspired by Best-Fit with periodic "open one ... |
| 122 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Keep pure best-fit as the base score, but break ties (equal resulting residual) by preferring the... |
| 123 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | The base best-fit rule is hard to beat myopically, so add a global scale factor: keep best-fit bu... |
| 124 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Introduce a stateful "reserve" policy that deliberately leaves one bin with a large open residual... |
| 125 | edit | not_better | 0.5848 | 0.9616 | $0.0005 | I'll implement a stateful "harmonic-style" rule: maintain a running histogram of item sizes seen ... |
| 126 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Pure best-fit is the strongest known static rule here, so I will shift from changing the placemen... |
| 127 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Keep best-fit's primary ordering (minimize resulting residual) but add a small secondary bonus pr... |
| 128 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Best-fit is near-optimal myopically but wastes space when a bin's residual becomes smaller than a... |
| 129 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Best-fit leaves many bins with tiny unusable residuals; I'll switch to a two-stage rule: try to p... |
| 130 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Best-fit is already strong, so instead of tweaking placement, I will improve the tie-breaking amo... |
| 131 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll replace myopic best-fit with a "best fit among bins in a reserve-aware order": keep best-fit... |
| 132 | edit | invalid | 0.0000 | 0.9616 | $0.0005 | Replace the myopic best-fit with a stateful harmonic-style rule: keep best-fit as the primary key... |
| 133 | edit | not_better | 0.9593 | 0.9616 | $0.0007 | (no description) |
| 134 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with a harmonic-style rule: score each bin by best-fit residual but bi... |
| 135 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace pure best-fit with a dual-criterion rule: primarily minimize the resulting residual, but ... |
| 136 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I will replace pure best-fit with a "best-fit decreasing-style" variant using a tiny stateful bia... |
| 137 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from greedy best-fit to a stateful "energy/opportunity" rule that reserves a small, l... |
| 138 | edit | not_better | 0.8145 | 0.9616 | $0.0006 | I'll replace the myopic best-fit with a stateful "worst-fit gate" rule: keep best-fit as the prim... |
| 139 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace the myopic best-fit with a "best fit plus a small bonus for bins whose remaining capacity... |
| 140 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace myopic best-fit with a size-class-aware rule: keep exact best-fit residual as the primary... |
| 141 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the myopic best-fit with a "best fit plus one-step lookahead packing quality": for e... |
| 142 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace myopic best-fit with a size-threshold rule: reserve a small set of completely empty ... |
| 143 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace the myopic best-fit with a stateful "capacity-threshold" rule: the primary key minim... |
| 144 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll implement a proper stateful variant of best-fit decreasing: keep a bounded histogram of rece... |
| 145 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll change the rule from pure best-fit to a hybrid that keeps best-fit for large items but, for ... |
| 146 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Add a mild stateful "reserve" mechanism: track a running estimate of the average item size, and i... |
| 147 | edit | no_code | n/a | 0.9616 | $0.0005 | (no description) |
| 148 | edit | invalid | 0.0000 | 0.9616 | $0.0006 | Best fit ignores the future benefit of leaving a residual that a *later large item* can exactly f... |
| 149 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I will implement a "size-class reservation" harmonic-style rule: maintain a running histogram of ... |
| 150 | edit | not_better | 0.6435 | 0.9616 | $0.0004 | Replace the static best-fit with a size-ratio threshold: use best-fit normally, but for item size... |
| 151 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll replace pure best-fit with a stateful rule that uses a running histogram of item sizes to sc... |
| 152 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best-fit with a hybrid that switches between best-fit and worst-fit based on a runni... |
| 153 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Implement a "best fit with lookahead-safe residual classing" variant: maintain a running histogra... |
| 154 | edit | not_better | 0.9616 | 0.9616 | $0.0008 | I'll try best-fit-decreasing-like behavior online by preferring bins whose residual after placeme... |
| 155 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a bounded best-fit rule: among bins whose residual after placement is ... |
| 156 | edit | not_better | 0.9616 | 0.9616 | $0.0007 | I'll replace pure best-fit with a residual-class harmonic rule that treats an empty/new bin more ... |
| 157 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll introduce a stateful "reserve for large items" rule: maintain the observed item-size histogr... |
| 158 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace plain best-fit with a two-part rule: for each bin compute residuals, add a tiny stateful ... |
| 159 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace pure best-fit with an online "dual-fit" rule that recognizes the heavy small-item ta... |
| 160 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | Replace pure best fit with a "best fit plus subset-sum completion" rule: among bins whose post-pl... |
| 161 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll switch from best fit to "best fit decreasing-like" selection by exploiting the fact that bin... |
| 162 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace plain best-fit with a "worst-of-best-fit" hybrid driven by the running mean item size μ: ... |
| 163 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Use a "best-fit with score = residual minus a small term proportional to the reciprocal of the bi... |
| 164 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Switch the tie-break among best-fit bins to prefer the bin with the largest current residual (i.e... |
| 165 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace best-fit with a score that combines tight fit with an explicit preference for keeping at ... |
| 166 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace best-fit with a hybrid rule that uses best-fit for small items but, for larger items... |
| 167 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace best-fit with a randomized/perturbed "best fit with limited lookahead via harmonic-style ... |
| 168 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Use a two-parameter score: primary term is tight fit, but bias selection toward bins with small r... |
| 169 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace plain best-fit with a size-threshold hybrid: for items at or below the running mean size,... |
| 170 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace plain best-fit with a two-threshold "best-fit plus occasional worst-fit" rule: for items ... |
| 171 | edit | not_better | 0.9616 | 0.9616 | $0.0006 | I'll implement a proper adaptive self-tuning policy: track bins' remaining capacities implicitly ... |
| 172 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | Replace plain best-fit with a "gap-aware best-fit" that first strongly prefers bins whose residua... |
| 173 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with an "almost-full / perfect-fit aware" rule: strongly reward placements ... |
| 174 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll add a small stateful ingredient: maintain a running count of how many bins have been "opened... |
| 175 | edit | improved | 0.9621 | 0.9621 | $0.0005 | Replace best-fit with a stateful "reserve-aware" rule: keep a target for the number of near-empty... |
| 176 | edit | not_better | 0.9612 | 0.9621 | $0.0006 | I'll replace the fixed target residual with an adaptive one based on the observed item-size distr... |
| 177 | edit | not_better | 0.9609 | 0.9621 | $0.0005 | Replace the fixed residual target with a data-driven but stable rule: keep the strong perfect/nea... |
| 178 | edit | improved | 0.9652 | 0.9652 | $0.0005 | I'll strengthen the reward for near-perfect fills (not just exact zero) so bins that end up with ... |
| 179 | edit | not_better | 0.9616 | 0.9652 | $0.0005 | Instead of a fixed 20 residual target, make the fallback preference a decreasing function of resi... |
| 180 | edit | not_better | 0.9652 | 0.9652 | $0.0005 | Make the near-perfect-fill bonus threshold adaptive: reward residuals below a data-driven small c... |
| 181 | edit | not_better | 0.9647 | 0.9652 | $0.0006 | Replace the fixed residual target with a data-driven target equal to half the running mean item s... |
| 182 | edit | not_better | 0.9616 | 0.9652 | $0.0005 | Treat the problem as classic Best-Fit with a small twist: reward near-perfect fills more precisel... |
| 183 | edit | improved | 0.9656 | 0.9656 | $0.0006 | I'll add a lightweight "reserve for small items" rule: track a running estimate of the fraction o... |
| 184 | edit | not_better | 0.9656 | 0.9656 | $0.0007 | Add a "large-item reserve" rule: bins whose post-placement residual would be too large to fit the... |
| 185 | edit | not_better | 0.9600 | 0.9656 | $0.0007 | Replace the flat anti-sliver penalty with a data-driven threshold: track how often arriving items... |
| 186 | edit | improved | 0.9663 | 0.9663 | $0.0008 | Track the running minimum and distribution of small item sizes to set the anti-sliver threshold a... |
| 187 | edit | not_better | 0.9661 | 0.9663 | $0.0008 | I'll make the seal bonus and anti-sliver penalty responsive to the current bin state by preferrin... |
| 188 | edit | not_better | 0.9656 | 0.9663 | $0.0008 | I will add a data-driven "target fill" mechanism: track the running mean item size and prefer res... |
| 189 | edit | gate_rejected | 0.9663 | 0.9663 | $0.0007 | I'll make the anti-sliver penalty two-sided and stronger: also penalize leaving a residual that i... |
| 190 | edit | not_better | 0.9656 | 0.9663 | $0.0008 | I'll replace the absolute "target=20" leftover with a data-driven target based on the running mea... |
| 191 | edit | improved | 0.9666 | 0.9666 | $0.0006 | I'll replace the fixed anti-sliver penalty and seal bonus with a graded linear reward for residua... |
| 192 | edit | gate_rejected | 0.9666 | 0.9666 | $0.0006 | I will add adaptive aging/normalization: track the running mean, and instead of scoring by absolu... |
| 193 | edit | not_better | 0.9666 | 0.9666 | $0.0006 | Add a bounded "future usefulness" term that stochastically estimates the expected wasted capacity... |
| 194 | edit | not_better | 0.9542 | 0.9666 | $0.0008 | I'll switch from an absolute-distance target to a "best-fit with distributional weighting" rule: ... |
| 195 | edit | not_better | 0.9616 | 0.9666 | $0.0006 | I will shift the base rule closer to pure best-fit by giving the smallest residual the top score ... |
| 196 | edit | not_better | 0.9656 | 0.9666 | $0.0007 | I'll add a small per-size learned correction: track, for each item size bucket, the observed aver... |
| 197 | edit | not_better | 0.5310 | 0.9666 | $0.0007 | I'll replace the ad-hoc rule with a proper online-learned approximation of the expected long-run ... |
| 198 | edit | improved | 0.9771 | 0.9771 | $0.0007 | Replace the mean-distance scoring with a quantile-based "next-item" target: track the empirical d... |
| 199 | edit | not_better | 0.9616 | 0.9771 | $0.0008 | I'll replace the fragile per-array numpy.where seal bonus and ad-hoc penalties with a cleaner "be... |
| 200 | edit | not_better | 0.9616 | 0.9771 | $0.0008 | I'll make the base term a pure monotone best-fit (smaller residual scores higher), and instead of... |
| 201 | edit | not_better | 0.9616 | 0.9771 | $0.0008 | I'll replace the ad-hoc continuous penalties with a cleaner "best-fit with a tunable residual-sha... |
| 202 | edit | not_better | 0.9616 | 0.9771 | $0.0010 | I'll replace the crude small-quantile target with a distribution-informed "expected fill value" o... |
| 203 | edit | improved | 0.9824 | 0.9824 | $0.0008 | I'll tune the current rule's two hand-set constants so the useful-residual target sits a bit lowe... |
| 204 | edit | improved | 0.9851 | 0.9851 | $0.0008 | I'll widen the seal bonus to cover residuals up to 3 (rewarding tight near-exact fills slightly m... |
| 205 | edit | not_better | 0.9616 | 0.9851 | $0.0008 | I'll add a key counter and use it to make the small-item quantile target adapt (using an exponent... |
| 206 | edit | improved | 0.9858 | 0.9858 | $0.0009 | Add a running estimate of the fraction of bins currently open/vacated and use it only to slightly... |
| 207 | edit | improved | 0.9861 | 0.9861 | $0.0010 | I'll make the seal bonus depend on the running histogram of all past items: strongly reward resid... |
| 208 | edit | not_better | 0.9616 | 0.9861 | $0.0009 | Switch the base scoring to a monotone best-fit (smaller residual scores strictly higher), removin... |
| 209 | edit | not_better | 0.9861 | 0.9861 | $0.0010 | Add a random tie-breaking offset keyed on the bin's capacity so placements among equally-scored b... |
| 210 | edit | not_better | 0.9666 | 0.9861 | $0.0011 | Replace the per-call percentile/bincount recomputation with cheap exponentially-updated estimates... |
| 211 | edit | not_better | 0.9616 | 0.9861 | $0.0009 | Use a weighted best-fit-plus-reuse blend: keep the reuse/common-item bonuses and seal, but make t... |
| 212 | edit | not_better | 0.9831 | 0.9861 | $0.0011 | I'll add a "residual-fit" bonus that rewards placing the item so the leftover is close to (but no... |
| 213 | edit | not_better | 0.9853 | 0.9861 | $0.0010 | I'll replace the fixed "seal" threshold and the noisy rolling-window reuse histogram with an expo... |
| 214 | edit | not_better | 0.9831 | 0.9861 | $0.0011 | I will mix in a graduated best-fit tiebreak so that, among bins whose reuse/seal bonuses are equa... |
| 215 | edit | not_better | 0.9858 | 0.9861 | $0.0008 | I'll replace the noisy per-call percentile/mode estimation with a cheap, stable exponentially-upd... |
| 216 | edit | not_better | 0.9861 | 0.9861 | $0.0011 | Introduce a first-fit-like bonus that strongly prefers bins already containing items (non-empty, ... |
| 217 | edit | not_better | 0.9616 | 0.9861 | $0.0008 | Replace the noisy small-quantile target and sliver shaping with a classic "best-fit with a dead z... |
| 218 | edit | not_better | 0.9616 | 0.9861 | $0.0009 | The current reuse/seal shaping is noisy and the symmetric distance-to-target hurts; I'll switch t... |
| 219 | edit | not_better | 0.9616 | 0.9861 | $0.0008 | I'll add a tailored "harmonic/best-fit" hybrid: strongly prefer the smallest non-negative residua... |
| 220 | edit | not_better | 0.9853 | 0.9861 | $0.0011 | Add a Boltzman-style "acceptance" widening: keep the existing reuse target but make the base scor... |
| 221 | edit | not_better | 0.9616 | 0.9861 | $0.0008 | Replace the noisy per-call percentile/mode estimates and the strong symmetric distance-to-target ... |
| 222 | edit | not_better | 0.9616 | 0.9861 | $0.0008 | Introduce a "capacity-class" tiebreak: since residuals are what determine future fit, reward bins... |
| 223 | edit | not_better | 0.9853 | 0.9861 | $0.0009 | I'll keep the existing best-fit-with-reuse-target structure (which scored 0.986) but fix the nois... |
| 224 | edit | not_better | 0.9616 | 0.9861 | $0.0007 | Replace the fragile per-call percentile/mode target with a slowly-adapting best-fit rule: keep th... |
| 225 | edit | not_better | 0.9723 | 0.9861 | $0.0010 | I'll keep the strong near-exact seal and the reuse bonus, but replace the noisy per-call percenti... |
| 226 | edit | not_better | 0.9616 | 0.9861 | $0.0008 | I'll keep the strong near-exact seal and the reuse bonus, but remove the noisy per-call percentil... |
| 227 | edit | not_better | 0.9666 | 0.9861 | $0.0009 | I'll tune the reward/penalty balance: weaken the symmetric "distance to target" term (which is no... |
| 228 | edit | not_better | 0.9861 | 0.9861 | $0.0009 | I'll keep the proven structure (near-exact seal + reuse bonus) but replace the noisy per-call per... |
| 229 | edit | not_better | 0.9856 | 0.9861 | $0.0011 | Keep the proven structure but make the near-exact "seal" bonus asymmetric and smarter: instead of... |
| 230 | edit | not_better | 0.9861 | 0.9861 | $0.0010 | The near-exact "seal" logic currently fires for any residual <= 3 with an arbitrary 1000 offset, ... |
| 231 | edit | not_better | 0.9718 | 0.9861 | $0.0010 | I'll replace the noisy per-call percentile/mode target computation with a stable exponentially-up... |
| 232 | edit | not_better | 0.9851 | 0.9861 | $0.0010 | I'll strengthen the reuse/reusability logic by replacing the single "mode_small" nudge and the ro... |
| 233 | edit | not_better | 0.9614 | 0.9861 | $0.0007 | The current rule has a strong "seal" bonus for residual &lt;= 3 that can hijack good best-fit cho... |
| 234 | edit | not_better | 0.9614 | 0.9861 | $0.0008 | I'll replace the hard-coded target/sliver/reuse heuristics with a cleaner, more principled rule: ... |
| 235 | edit | not_better | 0.9792 | 0.9861 | $0.0010 | I'll sharpen the existing rule by replacing the noisy rolling 35th-percentile/mode target with a ... |
| 236 | edit | not_better | 0.9861 | 0.9861 | $0.0011 | The existing rule is already near-optimal, but its "seal" offset of 1000 makes the residual-shapi... |
| 237 | edit | not_better | 0.7568 | 0.9861 | $0.0011 | I'll fold the near-exact seal into the reuse-frequency term: give a large bonus when the residual... |
| 238 | edit | not_better | 0.9861 | 0.9861 | $0.0012 | I'll add a mild "almost-miss" penalty: for residuals within 1-2 below a commonly seen item size (... |
| 239 | edit | not_better | 0.9861 | 0.9861 | $0.0012 | I'll add a mild secondary "reuse potential" term that rewards residuals matching the *top few* mo... |
| 240 | edit | not_better | 0.9851 | 0.9861 | $0.0009 | I'll replace the noisy rolling-window percentile/mode target with a stable exponentially-decayed ... |
| 241 | edit | not_better | 0.9846 | 0.9861 | $0.0009 | I'll replace the noisy rolling-window percentile/mode-based target and reuse histogram with a sta... |
| 242 | edit | not_better | 0.9800 | 0.9861 | $0.0011 | I'll add a deterministic tie-break that, independent of the noisy target terms, prefers the bin w... |
| 243 | edit | not_better | 0.9809 | 0.9861 | $0.0010 | Add a clean, dominant "tight-fill" component: reward small residuals strongly and monotonically (... |
| 244 | edit | not_better | 0.9861 | 0.9861 | $0.0011 | The seal condition `residual <= 3` with a flat +1000 bonus means residual 1, 2, and 3 all beat re... |
| 245 | edit | not_better | 0.9861 | 0.9861 | $0.0011 | I'll add a small "small-item reserve" term that favors placing medium items so the leftover stays... |
| 246 | edit | not_better | 0.9593 | 0.9861 | $0.0011 | I'll replace the current target-seeking score with a calibrated "expected future waste" model: sc... |
| 247 | edit | improved | 0.9875 | 0.9875 | $0.0011 | I'll strengthen the seal so residual 0 always wins over residuals 1–3 (strict exact-fill priority... |
| 248 | edit | not_better | 0.9616 | 0.9875 | $0.0011 | Add a dominant near-exact-fill gradient: give every small residual (0..~15) a large, strictly dec... |
| 249 | edit | not_better | 0.9614 | 0.9875 | $0.0010 | Add a light "scale down the noisy target-seeking terms" adjustment: because the reuse/sliver term... |
| 250 | edit | not_better | 0.9616 | 0.9875 | $0.0010 | I'll make the priority an explicit, smooth best-fit-plus-reserve rule: a dominant monotone tight-... |
| 251 | edit | not_better | 0.9866 | 0.9875 | $0.0010 | I will add a "future-fit" reserve term: instead of only preferring residuals near a small target,... |
| 252 | edit | not_better | 0.9616 | 0.9875 | $0.0007 | I'll replace the noisy percentile-window reuse term with a smoother "expected future waste" estim... |
| 253 | edit | improved | 0.9880 | 0.9880 | $0.0010 | I'll reduce the noisy reuse bonus and add a smooth, always-on "expected future fit" term computed... |
| 254 | edit | not_better | 0.9766 | 0.9880 | $0.0012 | Replace the smoothed-histogram reuse term with one based on the most common item sizes: protect r... |
| 255 | edit | not_better | 0.9880 | 0.9880 | $0.0011 | I'll add a "complement" term: reward placing an item so the residual equals a value that together... |
| 256 | edit | not_better | 0.9878 | 0.9880 | $0.0011 | I'll add a complementary-fit term: track the full running histogram of item sizes, and give a bon... |
| 257 | edit | not_better | 0.9866 | 0.9880 | $0.0010 | The current code keeps a "small_hist" that is never used and the rolling-window percentile adds n... |
| 258 | edit | not_better | 0.9880 | 0.9880 | $0.0010 | I'll strengthen the exact-fill domination using a lexicographic-style large gap based on residual... |
| 259 | edit | not_better | 0.9718 | 0.9880 | $0.0010 | I'll make the seal term less aggressive (reduce its magnitude and range) and increase the sliver ... |
| 260 | edit | not_better | 0.9880 | 0.9880 | $0.0010 | I'll add a stronger two-tier sealing: an exact-fill dominance scaled by the current item, plus a ... |
| 261 | edit | not_better | 0.9616 | 0.9880 | $0.0008 | The current rule under-prioritizes simply filling large-residual bins to reduce the number of ope... |
| 262 | edit | not_better | 0.9616 | 0.9880 | $0.0008 | The current rule's "target" residual (the 35th percentile of recent items) makes it prefer leavin... |
| 263 | edit | not_better | 0.9616 | 0.9880 | $0.0008 | The current rule leaves a large "target" residual (35th percentile of recent items), which keeps ... |
| 264 | edit | not_better | 0.9614 | 0.9880 | $0.0008 | I'll switch from the noisy rolling-window percentile target to a proper "best-fit with lookahead-... |
| 265 | edit | not_better | 0.9616 | 0.9880 | $0.0009 | Replace the noisy recent-window percentile target and the awkward "target residual" preference wi... |
| 266 | edit | not_better | 0.9616 | 0.9880 | $0.0008 | I'll replace the noisy 35th-percentile "target residual" preference (which keeps many half-empty ... |
| 267 | edit | improved | 0.9883 | 0.9883 | $0.0011 | Increase the reusability bonus weight and base the reusability signal on the recent-window histog... |
| 268 | edit | not_better | 0.9875 | 0.9883 | $0.0012 | Add a light "complement pairing" bonus in the base gradient: instead of only rewarding residuals ... |
| 269 | edit | not_better | 0.9616 | 0.9883 | $0.0012 | I'll add a "near-exact seal" tier: give a strong (but below exact-fill) bonus to residuals small ... |
| 270 | edit | not_better | 0.9843 | 0.9883 | $0.0011 | Introduce a second, finer-grained "complement" bonus that rewards placing the item so the resulti... |
| 271 | edit | not_better | 0.9739 | 0.9883 | $0.0010 | The current rule's reusability bonus is computed from a scaled histogram fraction, which makes it... |
| 272 | edit | not_better | 0.9616 | 0.9883 | $0.0011 | Broaden the "seal" region so a bin is strongly preferred whenever the resulting residual is small... |
| 273 | edit | not_better | 0.9616 | 0.9883 | $0.0009 | I'll shift the residual-target preference to a genuinely best-fit-oriented gradient (strong prefe... |
| 274 | edit | not_better | 0.9875 | 0.9883 | $0.0011 | Replace the noisy "target residual" pull with a genuine best-fit gradient (strongly prefer the sm... |
| 275 | edit | improved | 0.9912 | 0.9912 | $0.0009 | Replace the per-bin "small-item target" residual pull with a two-sided complement objective: pref... |
| 276 | edit | gate_rejected | 0.9915 | 0.9912 | $0.0009 | I'll add a "pairing" bonus that rewards placements whose resulting residual complements common re... |
| 277 | edit | not_better | 0.9616 | 0.9912 | $0.0008 | Replace the hand-tuned additive target/anti-sliver terms with a cleaner two-term rule: an exact-f... |
| 278 | edit | not_better | 0.9616 | 0.9912 | $0.0008 | I'll reframe the reusability term as a convex "reward for filling a residual that matches a frequ... |
| 279 | edit | improved | 0.9915 | 0.9915 | $0.0010 | I'll refine the reusability bonus by using a sharper (narrower) kernel and adding a small extra p... |
| 280 | edit | not_better | 0.9905 | 0.9915 | $0.0011 | I will add a "complement-pairing" bonus that rewards a bin whose resulting residual is close to a... |
| 281 | edit | gate_rejected | 0.9917 | 0.9915 | $0.0011 | I'll add a lightweight "future-fit" term: for each candidate residual r, compute the fraction of ... |
| 282 | edit | not_better | 0.9915 | 0.9915 | $0.0011 | I will add a small "small-item complement" bonus: reward bins whose residual is close to a sum of... |
| 283 | edit | not_better | 0.9895 | 0.9915 | $0.0010 | I'll replace the fixed rolling-window histogram with a lifetime histogram of all seen items (whic... |
| 284 | edit | not_better | 0.9903 | 0.9915 | $0.0010 | I'll add a small "seal-soon" term that rewards residuals for which a single typical recent item w... |
| 285 | edit | not_better | 0.9915 | 0.9915 | $0.0010 | I'll add a pairwise "two-item seal" bonus by convolving the recent-item histogram with itself and... |
| 286 | edit | not_better | 0.9912 | 0.9915 | $0.0009 | Replace the 256-item rolling window with a large stable lifetime histogram (with mild exponential... |
| 287 | edit | not_better | 0.9910 | 0.9915 | $0.0010 | I'll add a "pair-seal" lookahead using the lifetime item distribution: compute the probability (v... |
| 288 | edit | not_better | 0.9910 | 0.9915 | $0.0010 | I will retune the two strong existing terms: increase the exponential decay of the base best-fit ... |
| 289 | edit | not_better | 0.9912 | 0.9915 | $0.0011 | I'll refine the seal term so that instead of a flat plateau over residuals 0-4, it monotonically ... |
| 290 | edit | improved | 0.9922 | 0.9922 | $0.0010 | I'll add a strong "exact-seal" tie-break that rewards placing an item so the bin's residual becom... |
| 291 | edit | not_better | 0.9907 | 0.9922 | $0.0010 | I'll make the reuse bonus use the smoothed histogram evaluated with a bilinear interpolation betw... |
| 292 | edit | not_better | 0.9922 | 0.9922 | $0.0012 | Add a narrow 3-bin neighborhood bonus on the stable full lifetime histogram (centered at residual... |
| 293 | edit | not_better | 0.9907 | 0.9922 | $0.0010 | I'll add a "one-item-ahead exact seal" term: reward a placement whose residual is exactly a very ... |
| 294 | edit | not_better | 0.9920 | 0.9922 | $0.0011 | I'll replace the noisy recent-window-driven reuse target with a well-estimated lifetime-histogram... |
| 295 | edit | not_better | 0.9910 | 0.9922 | $0.0011 | I'll add a "seal probability" term that estimates, using the lifetime item histogram, the chance ... |
| 296 | edit | not_better | 0.9895 | 0.9922 | $0.0010 | I will replace the noisy recent-window reuse target with a well-estimated lifetime-histogram-base... |
| 297 | edit | not_better | 0.9605 | 0.9922 | $0.0012 | I'll drop the noisy recent-window reuse machinery (keeping only lifetime statistics) and replace ... |
| 298 | edit | not_better | 0.9922 | 0.9922 | $0.0011 | I'll sharpen the near-seal behavior: make the small-residual reward use a steeper falloff (so res... |
| 299 | edit | not_better | 0.9908 | 0.9922 | $0.0011 | I'll lower the fixed best-fit gradient penalty on residual (so true best-fit is favored more, whi... |
| 300 | edit | not_better | 0.9616 | 0.9922 | $0.0010 | I'll replace the absolute-residual reuse/sliver terms with a concave "leftover quality" function:... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,76 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Distribution-aware best fit: prefer placements that either nearly seal the bin (residual
+close to 0) or leave a leftover matching a common upcoming item size (so the bin stays
+reusable). Uses a running estimate of item statistics to set these targets adaptively."""
 import numpy as np
+
+_state = {"n": 0, "sum": 0.0, "full_hist": np.zeros(101, dtype=np.float64),
+          "recent": np.zeros(256, dtype=np.int64), "ptr": 0, "filled": 0,
+          "recent_hist": np.zeros(101, dtype=np.float64)}
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
+    st = _state
+    st["n"] += 1
+    st["sum"] += item
+    st["full_hist"][item] += 1
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    # Rolling window of recent items for a responsive local distribution estimate.
+    r = st["recent"]
+    if st["filled"] < r.size:
+        r[st["filled"]] = item
+        st["filled"] += 1
+    else:
+        old = r[st["ptr"]]
+        st["recent_hist"][old] -= 1
+        r[st["ptr"]] = item
+        st["ptr"] = (st["ptr"] + 1) % r.size
+    st["recent_hist"][item] += 1
+
+    mean_all = st["sum"] / st["n"]
+
+    if st["filled"] >= 32:
+        window = r[:st["filled"]]
+        mean_recent = float(window.mean())
+        med_recent = float(np.median(window))
+    else:
+        mean_recent = mean_all
+        med_recent = mean_all
+
+    residual = bins - item
+
+    # Base best-fit gradient: gently prefer smaller usable leftovers.
+    score = -0.08 * residual
+
+    # Seal: strong monotone preference toward exact fill; residual 0 dominates.
+    score = score + 2.0 * np.clip(4.0 - residual, 0.0, None)
+    score = np.where(residual == 0, score + 100000.0, score)
+
+    # Reusability target: leftover close to a typical item size keeps the bin productive.
+    target = max(mean_recent, 1.0)
+    score = score - 0.6 * np.abs(residual - target)
+
+    # Anti-sliver: continuous penalty as residual falls below the usable target.
+    sliver = np.clip(target - residual, 0.0, None)
+    score = score - 0.5 * sliver
+
+    # Reusability bonus from recent-window histogram, smoothed for stability.
+    total_recent = float(max(st["filled"], 1))
+    frac = st["recent_hist"] / total_recent
+    kern = np.array([0.15, 0.7, 0.15])
+    smoothed = np.convolve(frac, kern, mode="same")
+    in_range = (residual >= 0) & (residual <= 100)
+    rr = np.where(in_range, residual, 0).astype(np.int64)
+    reuse = smoothed[rr] * in_range
+    score = score + 18.0 * reuse
+
+    # Sharp lifetime-histogram match: reward residuals that are themselves a very
+    # common item size in the full distribution seen so far.
+    full_total = float(max(st["n"], 1))
+    ffrac = st["full_hist"] / full_total
+    fpeak = ffrac[rr] * in_range
+    score = score + 6.0 * fpeak
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (52 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 14 | `st = _state` | -0.9922 | essential: the program fails or turns invalid without it |
| 15 | `st['n'] += 1` | -0.9922 | essential: the program fails or turns invalid without it |
| 20 | `r = st['recent']` | -0.9922 | essential: the program fails or turns invalid without it |
| 25 | `old = r[st['ptr']]` | -0.9922 | essential: the program fails or turns invalid without it |
| 31 | `mean_all = st['sum'] / st['n']` | -0.9922 | essential: the program fails or turns invalid without it |
| 33 | `if st['filled'] >= 32: ...` | -0.9922 | essential: the program fails or turns invalid without it |
| 34 | `window = r[:st['filled']]` | -0.9922 | essential: the program fails or turns invalid without it |
| 35 | `mean_recent = float(window.mean())` | -0.9922 | essential: the program fails or turns invalid without it |
| 38 | `mean_recent = mean_all` | -0.9922 | essential: the program fails or turns invalid without it |
| 41 | `residual = bins - item` | -0.9922 | essential: the program fails or turns invalid without it |
| 41 | `term + bins` | -0.9922 | essential: the program fails or turns invalid without it |
| 44 | `score = -0.08 * residual` | -0.9922 | essential: the program fails or turns invalid without it |
| 51 | `target = max(mean_recent, 1.0)` | -0.9922 | essential: the program fails or turns invalid without it |
| 55 | `sliver = np.clip(target - residual, 0.0, None)` | -0.9922 | essential: the program fails or turns invalid without it |
| 59 | `total_recent = float(max(st['filled'], 1))` | -0.9922 | essential: the program fails or turns invalid without it |
| 60 | `frac = st['recent_hist'] / total_recent` | -0.9922 | essential: the program fails or turns invalid without it |
| 61 | `kern = np.array([0.15, 0.7, 0.15])` | -0.9922 | essential: the program fails or turns invalid without it |
| 56 | `term + score` | -0.4543 | matters |
| 52 | `term + score` | -0.3638 | matters |
| 48 | `score = np.where(residual == 0, score + 100000.0, score)` | -0.3448 | matters |
| 41 | `term - item` | -0.0893 | matters |
| 56 | `score = score - 0.5 * sliver` | -0.0118 | matters |
| 56 | `term - 0.5 * sliver` | -0.0118 | matters |
| 52 | `score = score - 0.6 * np.abs(residual - target)` | -0.0115 | matters |
| 52 | `term - 0.6 * np.abs(residual - target)` | -0.0115 | matters |
| 47 | `term + score` | -0.0032 | matters |
| 28 | `st['ptr'] = (st['ptr'] + 1) % r.size` | -0.0030 | matters |
| 27 | `r[st['ptr']] = item` | -0.0027 | matters |
| 21 | `if st['filled'] < r.size: ...` | -0.0027 | matters |
| 23 | `st['filled'] += 1` | -0.0027 | matters |
| 22 | `r[st['filled']] = item` | -0.0022 | matters |
| 29 | `st['recent_hist'][item] += 1` | -0.0012 | no effect alone |
| 26 | `st['recent_hist'][old] -= 1` | -0.0010 | no effect alone |
| 16 | `st['sum'] += item` | -0.0007 | no effect alone |
| 17 | `st['full_hist'][item] += 1` | -0.0007 | no effect alone |
| 39 | `med_recent = mean_all` | +0.0000 | no effect alone |
| 47 | `score = score + 2.0 * np.clip(4.0 - residual, 0.0, None)` | +0.0000 | no effect alone |
| 47 | `term + 2.0 * np.clip(4.0 - residual, 0.0, None)` | +0.0000 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 36: `med_recent = float(np.median(window))`

Not tested (evaluation limit 40): 13 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9922 | 0.9933 |
| minimal (1 parts removed) | 0.9922 | 0.9933 |

Minimal program:

```python
"""Distribution-aware best fit: prefer placements that either nearly seal the bin (residual
close to 0) or leave a leftover matching a common upcoming item size (so the bin stays
reusable). Uses a running estimate of item statistics to set these targets adaptively."""
import numpy as np
_state = {'n': 0, 'sum': 0.0, 'full_hist': np.zeros(101, dtype=np.float64), 'recent': np.zeros(256, dtype=np.int64), 'ptr': 0, 'filled': 0, 'recent_hist': np.zeros(101, dtype=np.float64)}

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    st = _state
    st['n'] += 1
    st['sum'] += item
    st['full_hist'][item] += 1
    r = st['recent']
    if st['filled'] < r.size:
        r[st['filled']] = item
        st['filled'] += 1
    else:
        old = r[st['ptr']]
        st['recent_hist'][old] -= 1
        r[st['ptr']] = item
        st['ptr'] = (st['ptr'] + 1) % r.size
    st['recent_hist'][item] += 1
    mean_all = st['sum'] / st['n']
    if st['filled'] >= 32:
        window = r[:st['filled']]
        mean_recent = float(window.mean())
    else:
        mean_recent = mean_all
        med_recent = mean_all
    residual = bins - item
    score = -0.08 * residual
    score = score + 2.0 * np.clip(4.0 - residual, 0.0, None)
    score = np.where(residual == 0, score + 100000.0, score)
    target = max(mean_recent, 1.0)
    score = score - 0.6 * np.abs(residual - target)
    sliver = np.clip(target - residual, 0.0, None)
    score = score - 0.5 * sliver
    total_recent = float(max(st['filled'], 1))
    frac = st['recent_hist'] / total_recent
    kern = np.array([0.15, 0.7, 0.15])
    smoothed = np.convolve(frac, kern, mode='same')
    in_range = (residual >= 0) & (residual <= 100)
    rr = np.where(in_range, residual, 0).astype(np.int64)
    reuse = smoothed[rr] * in_range
    score = score + 18.0 * reuse
    full_total = float(max(st['n'], 1))
    ffrac = st['full_hist'] / full_total
    fpeak = ffrac[rr] * in_range
    score = score + 6.0 * fpeak
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online --budget 0.75 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --seed 3
python -m autoresearch.loop --report experiments/llm-long-search-v1/runs/s3   # rebuild this report
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
