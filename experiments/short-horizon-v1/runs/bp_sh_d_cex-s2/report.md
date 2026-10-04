# Research loop report: bp_sh_d_cex

| | |
|---|---|
| problem | `bp_sh_d_cex` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0855 of a $0.20 hard cap, 150 calls, 287,161 tokens |
| wall time | search 1709 s, baselines 69 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (150 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9727 | 0.9634 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_d_cex/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_d_cex/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_d_cex/baselines/sum_of_squares.py` |

Audit: public 0.9727 → 0.9727 (+0.0000), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program 0.0093.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9276 | 0.9727 | $0.0011 | Replace pure best-fit with an adaptive rule that prefers bins whose residual after placement is c... |
| 2 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | The pure best-fit rule is score 0.9727. A promising refinement is a "best-fit with a threshold": ... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Add a "soft-waste" penalty only for very large residuals (tight-fit first, but among near-tight f... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Pure best-fit leaves a residual; using a small tie-break that prefers residuals around a “sweet s... |
| 5 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Add an adaptive twist on pure best-fit: compute a running mean item size and, among bins with nea... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with a "best-fit on residual, tie-break by preferring fuller bins via lower... |
| 7 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a bounded "best-fit with occasional worst-fit rescue": keep exact best... |
| 8 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace the pure best-fit with a fractional/linear-cost rule: choose the bin minimizing a co... |
| 9 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Pure best-fit wins on the long streams, so instead I keep best-fit's tight packing but add the cl... |
| 10 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Pure best-fit ties badly on the long streams because it fills bins to exactly zero residual, leav... |
| 11 | edit | not_better | 0.9688 | 0.9727 | $0.0005 | I'll try the classic "Best-Fit Decreasing"-like improvement adapted to online: instead of pure be... |
| 12 | edit | gate_rejected | 0.9742 | 0.9727 | $0.0008 | Replace pure best-fit with "dead-zone-aware best fit": primary key is still the post-placement re... |
| 13 | edit | not_better | 0.9701 | 0.9727 | $0.0005 | Keep exact best-fit as the primary key, but among bins whose post-placement residual is within 1 ... |
| 14 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace exact best-fit with a "harmonic/tiered best-fit" rule: instead of minimizing the raw resi... |
| 15 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Reinterpret the online problem with a proper "best fit decreasing-like" priority that also consid... |
| 16 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a size-class-aware secondary tie-break: keep exact best-fit as the primary key, but brea... |
| 17 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will replace pure best-fit with a "best-fit + small-item parking" rule: primary key remains the... |
| 18 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a proper "best-fit with lookahead via leftover usefulness": keep minimizing post-p... |
| 19 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with an adaptive rule that learns the item size distribution online an... |
| 20 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "best-fit + waiting-bin" rule based on the classic observation ... |
| 21 | edit | not_better | 0.9221 | 0.9727 | $0.0006 | I'll switch from best-fit to a "subharmonic" rule that targets a fixed fraction class: prefer to ... |
| 22 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll make the rule adaptive to the item size distribution: maintain an online estimate of the emp... |
| 23 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch to a randomized/tie-broken adaptive policy that occasionally uses worst-fit for very ... |
| 24 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a "best-fit decreasing with bin reuse" style heuristic that keeps best-fit as prim... |
| 25 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Pure best-fit wastes capacity on leftovers too small for any future item. I'll add a "harmonic"-s... |
| 26 | edit | not_better | 0.9713 | 0.9727 | $0.0005 | I'll implement a proper "almost-worst-fit"/harmonic-style variant: among bins where the item fits... |
| 27 | edit | not_better | 0.6787 | 0.9727 | $0.0005 | I will replace pure best-fit with a hybrid rule: for items that fill at least half the bin (item ... |
| 28 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | (no description) |
| 29 | edit | not_better | 0.9221 | 0.9727 | $0.0005 | Replace pure best-fit with a two-way hybrid: for large items (size &gt; 50) use best-fit, but for... |
| 30 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll use an adaptive score that keeps best-fit as the primary ranking but, when multiple bins yie... |
| 31 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure best-fit with a "best-fit among bins already opened, but only open a fresh ... |
| 32 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll upgrade best-fit with a *residual-value* tie-break using online statistics: primary score is... |
| 33 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try a proper "best fit with bounded residual" rule based on the classic result that almost-a... |
| 34 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best-fit is nearly optimal; I'll add a lightweight online harmonic-style override: track the runn... |
| 35 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will replace best-fit with a hybrid that beats its worst fragmentation case: choose the bin min... |
| 36 | edit | invalid | 0.0000 | 0.9727 | $0.0006 | I'll switch from pure best-fit to a hybrid that prefers tight fits but, among near-equal residual... |
| 37 | edit | not_better | 0.5985 | 0.9727 | $0.0009 | I'll abandon pure best-fit and implement the classic "Harmonic" style rule: classify each item in... |
| 38 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with a "best-fit + worst-fit hybrid": compute the ratio of residual-af... |
| 39 | edit | not_better | 0.7236 | 0.9727 | $0.0006 | I'll switch from best-fit to a "best-fit with a lookahead-free worst-fit guard for large items": ... |
| 40 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Keep best-fit as the primary rule but add a tiny secondary bonus that steers items into bins whos... |
| 41 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace best-fit with a rule that picks the bin leaving the smallest residual, but breaks ties am... |
| 42 | edit | not_better | 0.9727 | 0.9727 | $0.0018 | I'll replace pure best-fit with a rule that combines best-fit on small items with a minimum-bin-p... |
| 43 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a light-weight exact-fit rescue plus a "least-recently-touched" avoidance: score bins so... |
| 44 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Introduce a complementary-pairing refinement to best fit: track a running estimate of the item di... |
| 45 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace pure best-fit with a multi-class "Smart Harmonic" rule: partition items into size classes... |
| 46 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "best fit with limited open-bin window" rule: maintain a virtual notion of the m... |
| 47 | edit | not_better | 0.9143 | 0.9727 | $0.0007 | I'll implement a "Best Fit with complementary packing" (BFCP) rule: maintain a running mean of pa... |
| 48 | edit | not_better | 0.8929 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit with smallest residual, but among equally-good near... |
| 49 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Implement a perturbed best-fit rule: minimize the residual, but among residuals within a small to... |
| 50 | edit | not_better | 0.9408 | 0.9727 | $0.0005 | Replace pure best-fit with a "complementary best-fit" that adds a small bonus when the resulting ... |
| 51 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Keep best-fit as the dominant term (multiply by a large constant) and add a small, bounded bonus ... |
| 52 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try a simple "almost-worst-fit" rule: choose the bin with the smallest remaining capacity th... |
| 53 | edit | not_better | 0.9557 | 0.9727 | $0.0005 | Add the Johnson-style "best fit decreasing"-like trick that is actually available online: when th... |
| 54 | edit | not_better | 0.9705 | 0.9727 | $0.0005 | The perturbed/best-fit variants all converged to the same 0.9727 result, suggesting the tie-break... |
| 55 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | I'll try a seasonality/feedback rule: track the empirical distribution of item sizes seen so far ... |
| 56 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a rule that uses best-fit but, when it would create a small resid... |
| 57 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll try a "harmonic-style" hybrid: for small items (below a threshold) use best-fit into the ful... |
| 58 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace the pure best-fit with a bounded "best-fit with limited worst-fit fallback": rank pr... |
| 59 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best fit never leaves gaps large enough for the tie-breaks to matter on this distribution, and th... |
| 60 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace the pure best-fit rule with "best fit, but only among existing partially-filled bins; nev... |
| 61 | edit | not_better | 0.9640 | 0.9727 | $0.0005 | The pure best-fit is already optimal, so I'll try to squeeze out gains with a minimum-residual he... |
| 62 | edit | not_better | 0.8174 | 0.9727 | $0.0006 | Replace the pure best-fit score with a hybrid that combines tightness of fit with a "least feasib... |
| 63 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a bounded "residual-aware" best fit: keep the usual best-fit (smallest post-placement re... |
| 64 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add an online first-fit-descending-like prefill: keep a small buffer of the largest items se... |
| 65 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit with strict tie-breaking by smallest leftover" comb... |
| 66 | edit | gate_rejected | 0.9731 | 0.9727 | $0.0006 | I'll replace pure best-fit with a quantized best-fit: rank bins by how close the post-placement r... |
| 67 | edit | not_better | 0.9714 | 0.9727 | $0.0006 | I'll keep pure best-fit for the main placement decision but add a stateful "reserve the fullest n... |
| 68 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll make the scoring aware of a typical item size estimated online, and prefer the tightest fit ... |
| 69 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with "best-fit plus harmonic-style residual preference": use ordinary ... |
| 70 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll augment best-fit with an online-learned "mean item size" and add a small bonus for placing a... |
| 71 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll combine best-fit with a small, stateful "gap-consolidation" adjustment learned from the stre... |
| 72 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a linear-utility rule that scores each bin by a combination of tight f... |
| 73 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "fullest-bin-first" (worst-fit) rule capped: prefer to place into the bin with the lea... |
| 74 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the pure best-fit score with a "worst-fit among fitting bins, but only consider bins whos... |
| 75 | edit | not_better | 0.9714 | 0.9727 | $0.0005 | I will replace pure best-fit with a scored rule that prefers bins ending nearly full, but penaliz... |
| 76 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will try the classic "best-fit" improved by matching item sizes into open bins using a learned ... |
| 77 | edit | not_better | 0.5985 | 0.9727 | $0.0005 | Try an "almost-worst-fit" rule: among bins that fit, send the item to the bin with the largest re... |
| 78 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace best-fit with a variant that leaves a residual which can still fit a typical item: a... |
| 79 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will implement a two-parameter "best fit with mild spread" rule that adds a small fraction of t... |
| 80 | edit | not_better | 0.9724 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best-fit with a cutoff on residual stranding" approach infor... |
| 81 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Add a small stateful nudge: track an EMA of item sizes; among fitting bins give a tiny bonus to b... |
| 82 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "best-fit with harmonic/double-fit bias" learned from the stream: keep best-fit,... |
| 83 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a harmonic-weighted best-fit: score bins by how well the residual afte... |
| 84 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a randomized/priority-aware "best-fit decreasing-like" rule: keep best-fit but bre... |
| 85 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "best-fit plus score-compression" rule: keep the ordering by residua... |
| 86 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try a different family: score bins by a combination of best-fit residual and a stateful lear... |
| 87 | edit | not_better | 0.9705 | 0.9727 | $0.0004 | I'll abandon the best-fit tweaks and implement the classic "first fit" rule (place each item into... |
| 88 | edit | gate_rejected | 0.9731 | 0.9727 | $0.0006 | I'll switch from pure best-fit to a harmonic-family rule: score each bin by a decreasing function... |
| 89 | edit | not_better | 0.9725 | 0.9727 | $0.0011 | Try best-fit but, for each arriving item, restrict the candidate set to bins whose residual after... |
| 90 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace pure best-fit with an online learned "residual reuse" score: maintain a small histog... |
| 91 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a stateful "well-filled bin" tie-breaker: keep best-fit as the dominant term, but when t... |
| 92 | edit | not_better | 0.7663 | 0.9727 | $0.0006 | I'll implement the classic Harmonic bin-packing rule: score bins by the harmonic bucket value of ... |
| 93 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll keep best-fit as the dominant term but add a stateful tie-breaker that strongly favors drain... |
| 94 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a stateful "match residual to observed item sizes" bonus on top of best-fit: keep best-f... |
| 95 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Implement a score that is primarily best-fit but ranks exact-fit and near-exact-fit bins ahead us... |
| 96 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "best-fit with tunable residual-value function" that follows the cla... |
| 97 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a stateful "cut-off / match-make" rule: bins whose residual minus... |
| 98 | edit | not_better | 0.8566 | 0.9727 | $0.0005 | Add a stateful threshold rule: compute a small cutoff from the item size (seal fully, then prefer... |
| 99 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "best-fit plus small residual-gap bonus" that ties residual to ... |
| 100 | edit | not_better | 0.9727 | 0.9727 | $0.0018 | I'll replace the pure best-fit rule with a "residual binning" rule that maps each bin's post-plac... |
| 101 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with the "sum of squares" residual rule (score = -((bins - item)**2)),... |
| 102 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | The previous attempts all stayed near best-fit and never improved; I'll try a fundamentally diffe... |
| 103 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the residual-target approach with the classic "Sum of Squares" (SS) heuristic from t... |
| 104 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with the classic "Harmonic"-style approach that narrows the effective ... |
| 105 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | All previous attempts kept returning a score that ranks near-best-fit; the real limitation is tha... |
| 106 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the deterministic best-fit rule with a randomized best-fit that occasionally places ... |
| 107 | edit | not_better | 0.9280 | 0.9727 | $0.0005 | I'll implement the classic "BEST FIT with a lookahead-free capacity-leveling twist": instead of a... |
| 108 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try the classic "Almost Worst Fit" variant from online bin packing theory: among bins that l... |
| 109 | edit | not_better | 0.7126 | 0.9727 | $0.0005 | I'll implement the statistically strongest known online rule for this distribution family: Best F... |
| 110 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement the "Modified First Fit Decreasing" idea from online packing: reserve one bin as a... |
| 111 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Bin packing can be improved by ranking bins using the classic "suboptimal fit" bound: prefer bins... |
| 112 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will use a two-regime rule keyed to the item's size class: for "large" items (say ≥ 50) use bes... |
| 113 | edit | not_better | 0.9705 | 0.9727 | $0.0004 | I'll try "First Fit" instead of Best Fit: choosing the bin with the lowest index among those wher... |
| 114 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure greedy best-fit with a hybrid that uses best fit for large items (which ben... |
| 115 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "best fit with a fractional residual tie-break" that is more aggressive at conce... |
| 116 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "best fit with a look-ahead threshold" rule based on the item-size distribution: for i... |
| 117 | edit | not_better | 0.9672 | 0.9727 | $0.0006 | I'll implement the classic "harmonic" online bin packing algorithm: for each item, use a size-cla... |
| 118 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a small index-based tie-break that prefers earlier bins (lower index) among equally tigh... |
| 119 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a "sum-of-squares" / prominent left-gap rule from bin-packing literature: score bi... |
| 120 | edit | not_better | 0.8849 | 0.9727 | $0.0005 | I will implement a "worst-fit decreasing-like" adaptive rule: for each item, prefer the bin whose... |
| 121 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a "best fit with a packed-bin bonus": still prefer tight fits, ... |
| 122 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a multi-bin "eligible set" rule: place the item in the bin whose post-... |
| 123 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll combine best-fit with a pack-into-the-last-opened-bin preference: among bins that leave a sm... |
| 124 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a hybrid that applies best-fit but, for small items (below a threshold), prefers b... |
| 125 | edit | not_better | 0.7799 | 0.9727 | $0.0005 | Implement a harmonic/best-fit hybrid: for items ≥ 50 use tightest fit; for items &lt; 50 prefer b... |
| 126 | edit | not_better | 0.9727 | 0.9727 | $0.0009 | I'll replace pure best-fit with a harmonic-style rule from bin-packing theory: map each bin's pos... |
| 127 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace the pure best-fit rule with a "best-fit plus threshold-gap shaping" rule that introduces ... |
| 128 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Classic best-fit leaves lots of small residual slivers; I'll add a tie-breaking bonus that prefer... |
| 129 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace the pure best-fit rule with a best-fit rule that strictly prefers bins whose post-placeme... |
| 130 | edit | not_better | 0.8757 | 0.9727 | $0.0005 | Best-fit wastes bins on slivers; I'll switch to a two-level rule from online bin-packing theory: ... |
| 131 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "least-loaded bin that still leaves the item fitting tightly" approach tuned for the W... |
| 132 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a perturbed best-fit that adds a small tie-breaking bonus towar... |
| 133 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "best-fit within a capped worst-fit band" rule: using an online esti... |
| 134 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a harmonic-based rule that beats pure best-fit by bucketing post-placement residua... |
| 135 | edit | not_better | 0.9274 | 0.9727 | $0.0005 | Instead of prioritizing by post-placement residual (best-fit), use a rule that keeps an adaptive ... |
| 136 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add a bounded "close second" band to best-fit: use pure best-fit (smallest post-placement residua... |
| 137 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Use a "best-fit decreasing-like" rule adapted online: rank by post-placement residual but with a ... |
| 138 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "harmonic best-fit" that buckets post-placement residuals into geome... |
| 139 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Introduce a completion/open-bin signal: keep a counter of "closing" bins and prefer bins whose re... |
| 140 | edit | not_better | 0.9722 | 0.9727 | $0.0006 | I'll replace best-fit with a rule that uses the current item's size to decide between best-fit (f... |
| 141 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will replace pure best-fit with a slightly randomized/exact-fill-aware variant: keep best-fit a... |
| 142 | edit | not_better | 0.9663 | 0.9727 | $0.0005 | I'll shift from best-fit to a rule that prefers the bin that becomes "fullest but not closed too ... |
| 143 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Introduce a virtual-capacity bin reservation: among fitting bins, compute the residual after plac... |
| 144 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "best-fit with reserve-priority" rule that keeps some bins nearly em... |
| 145 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a "best-fit with lookahead-free gap filling" rule: use strict best-fit as backbone... |
| 146 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "fullest-fit but keep a small reserve" rule: among bins that fit, ch... |
| 147 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Use a two-candidate rule tuned to the Weibull item distribution: prefer an exact fill when availa... |
| 148 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll replace the deterministic best-fit with a "best-fit plus one-step future survival" rule: mai... |
| 149 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a light "two-choice" twist to best-fit: keep the tightest-fit bin as the primary anchor,... |
| 150 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit is hard to beat, but it ignores bin "openness". I'll switch to a classic online algorith... |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Skipped: priority has nothing to remove (a single return without a +/- chain).

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_d_cex --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 2
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_d_cex-s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_d_cex/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_d_cex/initial.py` `609927c5ea619a94`
- `problems/bp_sh_d_cex/problem.md` `190017a698e23cd8`
- `problems/bp_sh_d_cex/suite.json` `c10c239f751ffc5f`
- `problems/bp_sh_d_cex/verify.py` `12d8663a195dbe46`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
