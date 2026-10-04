# Research loop report: bp_sh_e_rand

| | |
|---|---|
| problem | `bp_sh_e_rand` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0844 of a $0.20 hard cap, 150 calls, 285,606 tokens |
| wall time | search 1399 s, baselines 73 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (150 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9727 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9727 | 0.9634 |  |
| baseline `funsearch_or` | 0.9802 | 0.9711 | `problems/bp_sh_e_rand/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9958 | 0.9937 | `problems/bp_sh_e_rand/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9968 | 0.9950 | `problems/bp_sh_e_rand/baselines/sum_of_squares.py` |

Audit: public 0.9727 → 0.9727 (+0.0000), hidden 0.9634 → 0.9634 (+0.0000); public − hidden gap of the final program 0.0093.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9968). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll switch from pure best-fit to a "best fit with prefer-residual-that-leaves-small-or-exact-fit... |
| 2 | edit | not_better | 0.9663 | 0.9727 | $0.0003 | I'll switch from pure best-fit to a hybrid rule that prefers an exact fit (residual 0) first, the... |
| 3 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a two-phase rule that uses a small amount of state: keep the classic b... |
| 4 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll replace pure best-fit with a best-fit rule that adds a tiny deterministic tie-break preferri... |
| 5 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll replace pure best-fit with a "best-fit plus exact-fit preference" using a strong but not abs... |
| 6 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a rule that combines best-fit tightness with a bounded "worst-fit... |
| 7 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Introduce a small amount of stateful, size-class-aware behavior: track the running mean item size... |
| 8 | edit | not_better | 0.5985 | 0.9727 | $0.0004 | I'll replace best-fit with a "least-loaded bin" (worst-fit) style rule that spreads items evenly,... |
| 9 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll use a stateful learned-cost rule: each arriving item is scored by a small "matching" heurist... |
| 10 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch to a "best-fit with a size-aware finish bonus" rule that keeps best-fit tightness but... |
| 11 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll try a principled departure from pure best-fit: use "best fit decreasing"-style behavior by m... |
| 12 | edit | not_better | 0.9719 | 0.9727 | $0.0005 | I'll implement a refinement of best-fit using an online "harmonic"-style classification: for item... |
| 13 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll implement "best-fit with exact-fill priority and a consolidation tie-break": score = -(resid... |
| 14 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll maintain a small pool of "open" bins and use a stateful rule that reserves partially-filled ... |
| 15 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll switch from best-fit to a "best-fit with a learned common-residual target": track the most f... |
| 16 | edit | not_better | 0.9582 | 0.9727 | $0.0007 | Best-fit is already near-optimal for this distribution; the remaining gap is caused by small item... |
| 17 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Try a "best-fit with a small-item protection" rule: when the arriving item is small (say ≤ 12), a... |
| 18 | edit | invalid | 0.0000 | 0.9727 | $0.0006 | I'll implement a "harmonic-style size-class with best-fit" rule: for large items (size > 50) they... |
| 19 | edit | gate_rejected | 0.9733 | 0.9727 | $0.0006 | I will implement a hybrid "best-fit with a minimum-fill guard": normally choose the tightest-fitt... |
| 20 | edit | not_better | 0.9649 | 0.9727 | $0.0006 | Best-fit is being hurt by wasting tiny slivers. I'll add a stateful "residual threshold" guard: w... |
| 21 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the plain best-fit with a "best-fit plus tiny-sliver tie-break": among bins within 1 capa... |
| 22 | edit | not_better | 0.9582 | 0.9727 | $0.0008 | Implement a minimal dead-zone guard: keep strict best-fit except when the tightest fit would leav... |
| 23 | edit | not_better | 0.9727 | 0.9727 | $0.0011 | Try a "complement matching" rule: track the multiset of currently-open residuals online, and for ... |
| 24 | edit | not_better | 0.9449 | 0.9727 | $0.0006 | I'll replace best-fit with a "worst-fit among near-best fits" tie-break restricted to large resid... |
| 25 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace plain best-fit with a capacity-class-aware scoring: rank bins primarily by the residual-a... |
| 26 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "best-fit with complementary-pairing bonus" rule: keep best-fit as the primary criteri... |
| 27 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a minimal "exact-fill preference": normally use strict best-fit, but give a strong bonus... |
| 28 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a stateful "best-fit with exact-fit priority, but only for large items" rule: strict bes... |
| 29 | edit | gate_rejected | 0.9781 | 0.9727 | $0.0006 | I'll try to actually reduce bins used by exploiting the fact that bins with remaining capacity 10... |
| 30 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "best-fit with a complementary-fill lookahead" that is stateful: kee... |
| 31 | edit | not_better | 0.9682 | 0.9727 | $0.0007 | I'll add a stateful rule that suppresses the classic best-fit "dead sliver" waste: maintain a his... |
| 32 | edit | not_better | 0.9714 | 0.9727 | $0.0007 | The prior dead-sliver rule failed because it applied too broadly; I'll make it stateful and narro... |
| 33 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit plus a capacity-class/rounding tie-break" rule: prima... |
| 34 | edit | not_better | 0.9682 | 0.9727 | $0.0007 | I'll implement a stateful "best-fit with a slack-threshold guard": normally strict best-fit, but ... |
| 35 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The prior dead-sliver rules all failed because "prefer any other fit" ignores that best-fit's res... |
| 36 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch from pure best-fit to a variant of the "best fit decreasing"-style supremacy of exact... |
| 37 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch the backbone from pure best-fit to the classic "Subharmonic" bin-packing score (fs = ... |
| 38 | edit | not_better | 0.9679 | 0.9727 | $0.0008 | Replace pure best-fit with a two-candidate rule: still take the tightest fit, but among bins, if ... |
| 39 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the pure best-fit backbone with a "Worst-Fit-Decreasing-aware" hybrid: normally use ... |
| 40 | edit | not_better | 0.5985 | 0.9727 | $0.0005 | Switch the backbone from pure best-fit to the classic "Sum of Squares" style rule: score each bin... |
| 41 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with the classic "Almost Worst Fit" style tie-break known to help bin ... |
| 42 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will keep best-fit as the backbone but add a small secondary bonus (below one integer unit so i... |
| 43 | edit | not_better | 0.7814 | 0.9727 | $0.0007 | I'll try the classic "best fit with lookahead-free fairness/randomization": my recent attempts al... |
| 44 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace best-fit with a score that prefers the bin whose residual after placement is closest... |
| 45 | edit | not_better | 0.9727 | 0.9727 | $0.0013 | I'll add a "best-fit with dead-sliver rescue" that is stateful: when best-fit would leave a resid... |
| 46 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch from greedy best-fit to a pooling/dual-threshold scheme: for small items (size ≤ runn... |
| 47 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | The evaluator feedback shows that every local tie-break tweak around best-fit is already at the s... |
| 48 | edit | not_better | 0.8737 | 0.9727 | $0.0005 | Replace pure best-fit (minimize residual) with a convex lost-opportunity penalty on the residual:... |
| 49 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to the classic "best fit with a smallest-remaining-bin restructure": for each arrivin... |
| 50 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch the tie-break from "leave residual matching a common item size" to a score that prefe... |
| 51 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a proper Harmonic-style packing rule: classify items by size into intervals (1/2, ... |
| 52 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the residual-based best-fit score with a score that implements the "Best-Fit Decreasing w... |
| 53 | edit | not_better | 0.9607 | 0.9727 | $0.0006 | Replace the deterministic best-fit score with a randomized one: pick the top-k fullest bins that ... |
| 54 | edit | not_better | 0.9363 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit plus residual binning" rule that reserves near-full b... |
| 55 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit with largest-residual slack" rule: among the bins whe... |
| 56 | edit | not_better | 0.9708 | 0.9727 | $0.0006 | I will replace pure best-fit with a size-class harmonic rule: items are classified by size into i... |
| 57 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "worst-fit among near-full bins for large items, best-fit for s... |
| 58 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The pure best-fit rule is already strong, but it never uses the small-item waste-avoidance idea o... |
| 59 | edit | gate_rejected | 0.9960 | 0.9727 | $0.0005 | I'll replace best-fit with a "least-loaded-that-still-fits-why": specifically, implement the clas... |
| 60 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement the classic "Best Fit" but with a small tweak: when an item exactly fills a bin's ... |
| 61 | edit | gate_rejected | 0.9784 | 0.9727 | $0.0007 | I'll replace pure best-fit with a "harmonically bucketed best-fit" that reserves mostly-empty bin... |
| 62 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll normalize scores so that exact fits are strongly preferred and near-exact fits are ranked ab... |
| 63 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a light "leave room for a future exact pair" safeguard: keep pure best-fit ordering, but... |
| 64 | edit | not_better | 0.9663 | 0.9727 | $0.0004 | I'll replace pure best-fit with a rule that specifically targets exact and near-exact fits using ... |
| 65 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "best-fit with exact-fit priority plus worst-fit rescue" rule: for each item, fi... |
| 66 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a running-size-histogram-aware "pair-score" that favors placing an item so the remaining... |
| 67 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add a small age/index-based tiebreaker that encodes a "bounded best-fit" preference: among b... |
| 68 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "best-fit with look-ahead-free bucket reservation" targeted at ... |
| 69 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Add a dominant bonus for placements that yield an exact fit (residual 0) and a smaller bonus when... |
| 70 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll implement a "score-based residual matching" rule that up-weights placing the item so the res... |
| 71 | edit | not_better | 0.9727 | 0.9727 | $0.0005 |  |
| 72 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The current rule is pure best-fit, which strands many medium residuals. I'll add a smarter rule t... |
| 73 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace the baseline with a learned "best-fit plus residual-value matching" rule: keep best-... |
| 74 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Replace pure best-fit with a hybrid that uses best-fit normally but, when an item is small and se... |
| 75 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "least-load / most-loaded" hybrid known to help bin packing: use best-fit but, a... |
| 76 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement the classic "Best Fit Decreasing"-style improvement adapted online: keep best-fit ... |
| 77 | edit | not_better | 0.9675 | 0.9727 | $0.0006 | Replace pure best-fit with a hybrid that occasionally uses worst-fit for the tightest residuals: ... |
| 78 | edit | not_better | 0.9719 | 0.9727 | $0.0005 | For items larger than 50 (which cannot be paired with anything else), route them to the emptiest ... |
| 79 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a hybrid of best-fit for large items and a "residual matching / anti-fragmentation... |
| 80 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best-fit with residual histogram" rule that directly scores ea... |
| 81 | edit | not_better | 0.5985 | 0.9727 | $0.0005 | I'll keep best-fit as the primary rule but add a strong secondary key that favors placing the ite... |
| 82 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace plain best-fit with a score that, among fitting bins, treats near-perfect fits equally (a... |
| 83 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a "conversion" improvement on top of best-fit: since the item distribution is Weibull wi... |
| 84 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a two-mode rule: for items ≤ 50 use best-fit (tightest residual), but ... |
| 85 | edit | not_better | 0.9701 | 0.9727 | $0.0005 | Keep best-fit but treat residuals within a small epsilon as tied, and among those ties prefer the... |
| 86 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Bin packing with a skewed item distribution benefits from "best fit" but effectively equally-good... |
| 87 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "fractional best-fit plus exact-residual reservation" rule: score bi... |
| 88 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to "best-fit with a small residual-threshold quirk": when the best... |
| 89 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a "harmonic/smooth best-fit" that still ranks by tightest residual but replaces hard tie... |
| 90 | edit | not_better | 0.9604 | 0.9727 | $0.0006 | Replace pure best-fit with a two-phase strategy: prefer placing the item as the exact complement ... |
| 91 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a hybrid: for large items (size > 50), best-fit often creates awkward residuals; i... |
| 92 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best-fit leaves tiny unusable residual slivers (e.g. capacity 1–4) that can never be filled; I'll... |
| 93 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Introduce a scale-adaptive perturbation: instead of hard best-fit, add a small sub-unit bonus pro... |
| 94 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with an online "best-fit with residual-class reserving" rule inspired ... |
| 95 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | The pure best-fit rule is already near-optimal for this distribution; the main remaining loss com... |
| 96 | edit | not_better | 0.9663 | 0.9727 | $0.0006 | Replace pure best-fit with a small randomized "best-fit versus first-fit" hybrid: use best-fit bu... |
| 97 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a dual-criterion rule: primary preference for the smallest residual, b... |
| 98 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | Best fit wastes capacity when it leaves residuals smaller than the smallest item we've seen. I'll... |
| 99 | edit | not_better | 0.9727 | 0.9727 | $0.0007 | I'll try a genuinely different rule: two-category "harmony" scoring. For each bin compute post-pl... |
| 100 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll try a different deterministic rule that changes tie-breaking among equal residuals: score ea... |
| 101 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "best-fit with unusable-sliver avoidance" rule where the primary key is the post... |
| 102 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best-fit is already near-optimal on realistic streams; the clearest remaining weakness is that ti... |
| 103 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll implement a "smart best-fit / worst-fit hybrid": primary score prefers the smallest usable p... |
| 104 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Introduce a "best fit decreasing"-style aging/statistics rule: track the running mean and standar... |
| 105 | edit | not_better | 0.9682 | 0.9727 | $0.0006 | Best-fit wastes capacity by leaving tiny unusable residuals; I'll change the primary score to a v... |
| 106 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a rule that scores bins by the post-placement residual but adds a... |
| 107 | edit | not_better | 0.9507 | 0.9727 | $0.0005 | I'll try a size-aware "best fit" that also avoids leaving residuals that are too small to be refi... |
| 108 | edit | not_better | 0.9507 | 0.9727 | $0.0006 | I'll replace the pure best-fit rule with a "best fit with sliver avoidance" that ranks first by h... |
| 109 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I will replace pure best-fit with a lookahead-free "best fit with unusable-sliver demotion" that ... |
| 110 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch from pure best-fit to a rule that uses the bin index as a proxy for bin age and prefe... |
| 111 | edit | not_better | 0.9688 | 0.9727 | $0.0004 | I'll replace pure best-fit with a "best fit with size-class matching": strong penalty for leaving... |
| 112 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Replace pure best-fit with a harmonic/percentage-based best-fit that prefers the bin minimizing t... |
| 113 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a hybrid that keeps best-fit ranking but applies a small penalty ... |
| 114 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "best fit decreasing"-style aging rule: keep the tight-fit rank... |
| 115 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "moving-average fit" rule that scores each bin by how close its... |
| 116 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "least-loaded that still fits" style rule that also demotes bin... |
| 117 | edit | gate_rejected | 0.9742 | 0.9727 | $0.0005 | Best fit has sat at 0.9727 for many tweaks, so I'll try a genuinely different online heuristic: i... |
| 118 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Best-fit residual chasing may strand unusable small leftovers; I'll cap the residual penalty so t... |
| 119 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Best-fit is near-optimal but ties on "smallest residual" often pick the wrong fuller bin; I'll sh... |
| 120 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll switch to a "fullest bin that fits" rule (score by pre-placement remaining capacity, i.e. pr... |
| 121 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace the pure best-fit residual with a blend: score primarily by post-placement residual (best... |
| 122 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | I'll try a proper Best-Fit-Decreasing-like rule that uses the running mean item size as a "target... |
| 123 | edit | not_better | 0.8050 | 0.9727 | $0.0006 | I'll implement a "residual reusability" rule: compute each bin's post-placement residual, and sco... |
| 124 | edit | not_better | 0.8479 | 0.9727 | $0.0006 | Introduce a proper Almost-Worst-Fit / harmonic-style rule that is generally stronger than best-fi... |
| 125 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Best fit's tie-breaking on exactly-equal residuals is arbitrary; I'll add a small tie-break term ... |
| 126 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll combine best-fit with a light "reserve" rule: prefer the smallest post-placement residual, b... |
| 127 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace best-fit with a two-component rule: score by post-placement residual closeness to ze... |
| 128 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll implement a "best-fit with residual-tolerance tie-break" that stays exact for the primary be... |
| 129 | edit | not_better | 0.9727 | 0.9727 | $0.0008 | I will try a size-class/quantile harmonic approach: track arriving item sizes online, bucket each... |
| 130 | edit | not_better | 0.5985 | 0.9727 | $0.0007 | Replace best-fit with a Harmonic-style rule: assign each item to a size class based on a set of f... |
| 131 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll add a lightweight "closing" penalty to best-fit: prefer the fullest bin (smallest post-place... |
| 132 | edit | not_better | 0.9590 | 0.9727 | $0.0007 | Replace best-fit with a bounded harmonic-style rule that partitions items by size class and, for ... |
| 133 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a full-bin-first rule: among bins that fit, strongly prefer bins alrea... |
| 134 | edit | not_better | 0.9232 | 0.9727 | $0.0008 | (no description) |
| 135 | edit | not_better | 0.9280 | 0.9727 | $0.0005 | I'll change the objective from pure best-fit to a "best-fit with bounded-waste" rule: when pickin... |
| 136 | edit | not_better | 0.9727 | 0.9727 | $0.0004 | Introduce a lightweight online "sum-of-squares" load-balancing bias: keep best-fit as the primary... |
| 137 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll switch to a score that blends best-fit with a "leave a usable remainder" objective: strongly... |
| 138 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Use a "best-fit with a reserved-slot" rule: among the bins that fit, prefer the tightest fit as u... |
| 139 | edit | not_better | 0.9705 | 0.9727 | $0.0006 | I'll replace pure best-fit (which packs tightly but can waste small residuals) with a rule that p... |
| 140 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll add an online learned item-size threshold: track the running mean/variance of observed items... |
| 141 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | I'll replace pure best-fit with a "least-loaded among tight fits" hybrid: score primarily by best... |
| 142 | edit | not_better | 0.9727 | 0.9727 | $0.0005 | Replace pure best-fit with a "best-fit plus a small future-aware penalty": prefer the tightest fi... |
| 143 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a "best-fit to the fullest bin" variant: among all fitting bins, ... |
| 144 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace plain best-fit with a rule that tracks past item sizes online and, among bins whose tight... |
| 145 | edit | not_better | 0.9698 | 0.9727 | $0.0005 | I'll replace pure best-fit with a size-class / harmonic-style online rule: track item sizes seen ... |
| 146 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I will replace the rule with a "best-fit plus bounded-budget consolidation" heuristic that is kno... |
| 147 | edit | not_better | 0.9716 | 0.9727 | $0.0006 | I'll replace pure best-fit with a learned "best-fit among bins with a small residual, else avoid ... |
| 148 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | Replace pure best-fit with a "best-fit, but never leave a medium residual in a nearly-empty bin" ... |
| 149 | edit | not_better | 0.9727 | 0.9727 | $0.0006 | I'll replace pure best-fit with a harmonic-style rule: since item sizes range 1..100 and best-fit... |
| 150 | edit | not_better | 0.9243 | 0.9727 | $0.0006 | Replace pure best-fit with a rule that keeps the tightest fit but, among all bins that fit, choos... |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Skipped: priority has nothing to remove (a single return without a +/- chain).

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_e_rand --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 2
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_e_rand-s2   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 42 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_e_rand/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_e_rand/initial.py` `609927c5ea619a94`
- `problems/bp_sh_e_rand/problem.md` `190017a698e23cd8`
- `problems/bp_sh_e_rand/suite.json` `7e369a6aa9869ab4`
- `problems/bp_sh_e_rand/verify.py` `0f28aa90e2f40f70`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
