# Research loop report: bp_sh_a5000

| | |
|---|---|
| problem | `bp_sh_a5000` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.1163 of a $0.20 hard cap, 150 calls, 371,222 tokens |
| wall time | search 2317 s, baselines 56 s, explain 129 s |
| stopped | max_iters (stopped_early) |
| evaluations | 151 (149 valid), 13 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9590 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9928 | 0.9893 |  |
| baseline `funsearch_or` | 0.9702 | 0.9711 | `problems/bp_sh_a5000/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9938 | 0.9937 | `problems/bp_sh_a5000/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9952 | 0.9950 | `problems/bp_sh_a5000/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9923 | 0.9890 | 2 parts removed |

Audit: public 0.9590 → 0.9928 (+0.0337), hidden 0.9634 → 0.9893 (+0.0259); public − hidden gap of the final program 0.0035.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9952). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Enhance best fit into "best fit with reserve": prefer bins with the smallest remaining capacity (... |
| 2 | edit | not_better | 0.9590 | 0.9590 | $0.0003 | Implement "best fit decreasing"-style lookahead by using a score that combines tightest fit with ... |
| 3 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Refine the fit rule from strict best-fit to a slightly capacity-aware variant: choose the bin wit... |
| 4 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Implement a classic full-bin heuristic: for each bin, compute the residual capacity after placing... |
| 5 | edit | not_better | 0.9321 | 0.9590 | $0.0004 | Replace pure best-fit with a learned-flavored residual-scoring rule: score bins by how close the ... |
| 6 | edit | not_better | 0.9558 | 0.9590 | $0.0004 | Replace greedy best-fit with a persistent first-fit-style search that maintains a single "open bi... |
| 7 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Implement a harmonic-based bin-choice rule: since item sizes are integers with mean about 40, sco... |
| 8 | edit | not_better | 0.9588 | 0.9590 | $0.0004 | Implement a hybrid that uses best-fit but, as soon as the item stream's history suggests it, swit... |
| 9 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I will replace pure best-fit with a "best-fit plus sum-of-two" residual-matching rule: score bins... |
| 10 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a bounded best-fit that occasionally prefers a bin leaving a residual ... |
| 11 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I will switch from pure best-fit to a "best-fit with a small reserve" rule based on the classic i... |
| 12 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace the static scoring with a two-parameter adaptive rule learned online: track the empirical... |
| 13 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace the pure best-fit rule with a "best-fit decreasing-aware" rule that prefers, among bins g... |
| 14 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Replace pure best-fit with a "best-fit plus a stranded-space penalty": still choose the tightest ... |
| 15 | edit | not_better | 0.9581 | 0.9590 | $0.0005 | Replace pure best-fit with a "best-fit with bounded gap reserve" rule that scores bins by post-pl... |
| 16 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I will replace pure best-fit with a hybrid rule: use best-fit normally, but when the arriving ite... |
| 17 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll switch from pure best-fit to a bounded "worst-fit among near-tight fits" hybrid: keep best-f... |
| 18 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Best-fit is already near-optimal for this item distribution, so the main remaining loss comes fro... |
| 19 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll try a principled departure from pure best-fit: score bins by a "space efficiency" measure th... |
| 20 | edit | not_better | 0.9524 | 0.9590 | $0.0006 | I'll replace pure best-fit with a two-sided residual-target rule: score bins by how close the pos... |
| 21 | edit | invalid | 0.0000 | 0.9590 | $0.0006 | I'll stop perturbing per-placement choices and instead implement the well-known "Harmonic/Sum-of-... |
| 22 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll return to pure best-fit (which the feedback shows is hard to beat) but add the theoretically... |
| 23 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a two-regime rule: for items large enough to matter, use best-fit norm... |
| 24 | edit | not_better | 0.9588 | 0.9590 | $0.0006 | I'll implement a "full-bin pairing" rule: for each arriving item, prefer placing it into a bin wh... |
| 25 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll replace best-fit with a "residual histogram" learning rule: keep best-fit as the core policy... |
| 26 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll keep best-fit but fix the residual target empirically: maintain a running histogram of item ... |
| 27 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll keep best-fit as the core but add a "good fit" preference derived from the classic First-Fit... |
| 28 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | The pure best-fit rule wastes opportunities to combine two smaller items into one bin. I'll switc... |
| 29 | edit | not_better | 0.9590 | 0.9590 | $0.0008 | Replace the pure best-fit rule with a "best fit with pairing awareness" rule that considers both ... |
| 30 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Pure best-fit is locally optimal, but the feedback shows any tweak that keeps its decisions uncha... |
| 31 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll replace best-fit with a classic "Best-Fit with an improvement" by using a rotating/randomize... |
| 32 | edit | invalid | 0.0000 | 0.9590 | $0.0009 | I'll implement a "lookahead-aware best fit" that tracks a running histogram of item sizes but sti... |
| 33 | edit | not_better | 0.9583 | 0.9590 | $0.0006 | I'll switch from strict best-fit to a "best-fit with small-item pairing" rule: keep the tight-fit... |
| 34 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Replace pure best-fit with a dual-criteria rule: prefer the bin whose post-placement residual is ... |
| 35 | edit | not_better | 0.9579 | 0.9590 | $0.0008 | Best-fit wastes capacity when a residual is too small to hold any future item, so I'll add a seco... |
| 36 | edit | not_better | 0.7759 | 0.9590 | $0.0006 | I'll replace pure best-fit with a threshold-based "residual minimization with fillability" rule: ... |
| 37 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Pure best-fit is a local rule that cannot exploit the distribution's known shape. I'll implement ... |
| 38 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace pure best-fit with a "best-fit-decreasing emulation" hybrid: track the running mean/... |
| 39 | edit | not_better | 0.9574 | 0.9590 | $0.0005 | Replace pure best-fit with "almost-best-fit": prefer tightest fits but, among bins whose resultin... |
| 40 | edit | not_better | 0.9537 | 0.9590 | $0.0006 | I'll switch from pure best-fit to a hybrid that mostly keeps best-fit (tightest residual) but bre... |
| 41 | edit | not_better | 0.9590 | 0.9590 | $0.0008 | I'll implement a proper "best fit with lookahead-by-histogram" rule based on the classic observat... |
| 42 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Best-fit is essentially optimal for this distribution, so the only reliable gain is to convert it... |
| 43 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a "smoothly averaged, capacity-aware" best-fit: prefer the tightest po... |
| 44 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll switch to a two-phase rule that emulates best-fit-decreasing by preferring bins whose post-p... |
| 45 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll implement the classic "Harmonic/K-per-bin aware" alternative to best fit: track a running hi... |
| 46 | edit | not_better | 0.3988 | 0.9590 | $0.0005 | Replace pure best-fit with a residual-aware rule that, when the best residual is small, sometimes... |
| 47 | edit | not_better | 0.9499 | 0.9590 | $0.0005 | Replace strict best-fit with a rule that avoids creating extremely small residuals: still prefer ... |
| 48 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Introduce a small learned "reserve" bias based on the observed distribution: keep best-fit as the... |
| 49 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll try a "reserve the emptiest bins" variant of best-fit that mimics best-fit-decreasing's tend... |
| 50 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll use a two-candidate rule inspired by "best-fit with lookahead-free fill": after computing th... |
| 51 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll switch to a variant that mimics "worst fit decreasing" style gap-balancing: instead of alway... |
| 52 | edit | not_better | 0.9590 | 0.9590 | $0.0007 | I'll replace pure best-fit with a hybrid rule that matches best-fit on most items but, when the t... |
| 53 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Try a "Sum of Squares"-style scoring borrowed from integer programming for bin packing: choose th... |
| 54 | edit | not_better | 0.8848 | 0.9590 | $0.0006 | I'll try a randomized/perturbed best-fit that occasionally (when the tightest residual is tiny an... |
| 55 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll replace pure best-fit with a learned online grouping rule: maintain bins for exact residual ... |
| 56 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Introduce a "reserve best-fit that avoids stranding large gaps" rule: among bins that keep the it... |
| 57 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Replace pure best-fit with a parity/pattern rule inspired by harmonic bin packing: score bins by ... |
| 58 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Use a distribution-aware variant of best fit: prefer placements that leave a residual matching th... |
| 59 | edit | improved | 0.9593 | 0.9593 | $0.0006 | I'll implement a "best-fit with residual-utility" rule: score each bin by the (negative) post-pla... |
| 60 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | Replace the 10-ladder residual snapping with a data-driven one: maintain online statistics of ite... |
| 61 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the coarse fixed-modulus ladder with a harmonic-style score based on the residual re... |
| 62 | edit | not_better | 0.9590 | 0.9593 | $0.0009 | Replace the coarse mod-10 snapping with a data-driven waste penalty: keep best-fit as the dominan... |
| 63 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll shift from "best-fit plus small tie-breaks" (which is near the noise floor) to a distributio... |
| 64 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | Replace the mod-10 alignment with a distribution-aware "residual utility" rule: compute post-plac... |
| 65 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll replace the near-noise-floor tie-break with a proper distribution-aware bin-choice rule: sco... |
| 66 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | Replace the near-noise-floor mod-10 tie-break with a scaled penalty: dominant term is best-fit, b... |
| 67 | edit | not_better | 0.3978 | 0.9593 | $0.0005 | Replace the near-noise floor best-fit tie-break with a proper conservation-style rule: use worst-... |
| 68 | edit | not_better | 0.9590 | 0.9593 | $0.0007 | I'll replace the noisy best-fit tie-break with a proper distribution-aware "residual utility" tha... |
| 69 | edit | not_better | 0.9590 | 0.9593 | $0.0006 | I'll replace the current near-flat best-fit tie-break with a proper Best-Fit-Decreasing-style rul... |
| 70 | edit | improved | 0.9702 | 0.9702 | $0.0007 | I'll replace best-fit with a two-part rule: strongly prefer size-0 perfect fits and otherwise pre... |
| 71 | edit | improved | 0.9800 | 0.9800 | $0.0007 | I'll replace the fixed harmonic targets with an online-learned target set: estimate the item dist... |
| 72 | edit | improved | 0.9815 | 0.9815 | $0.0008 | Add a "residual reachability" term: instead of only rewarding residuals that a *single* future it... |
| 73 | edit | not_better | 0.9544 | 0.9815 | $0.0009 | Replace the current histogram-only utility with a blended rule that combines the distribution-awa... |
| 74 | edit | not_better | 0.7467 | 0.9815 | $0.0011 | I will make the online histogram adapt faster and more stably early in the stream by using a disc... |
| 75 | edit | not_better | 0.9803 | 0.9815 | $0.0010 | Refine the residual-utility estimator: derive it from the empirical (unsmoothed) distribution via... |
| 76 | edit | improved | 0.9837 | 0.9837 | $0.0009 | I'll refine the three-item-sum weighting so it reflects the true probability of a later pair/trip... |
| 77 | edit | gate_rejected | 0.9856 | 0.9837 | $0.0010 | I'll augment the residual-utility ranking with a "future-fit feasibility" lookahead: keep a decay... |
| 78 | edit | not_better | 0.9705 | 0.9837 | $0.0009 | I'll replace the pure residual-utility scoring with a hybrid that adds an explicit best-fit tie-b... |
| 79 | edit | not_better | 0.9721 | 0.9837 | $0.0010 | I'll switch from scoring residuals to scoring the bin choice directly with a regret-based rule: e... |
| 80 | edit | improved | 0.9847 | 0.9847 | $0.0010 | I will add a second-pass refinement to the utility term: instead of a single residual value, comb... |
| 81 | edit | not_better | 0.7547 | 0.9847 | $0.0010 | I'll strengthen the exact-completion signal by computing, for each candidate residual, the probab... |
| 82 | edit | not_better | 0.7015 | 0.9847 | $0.0011 | I will replace the coarse rounded/binned residual utility with a proper distribution-aware scorin... |
| 83 | edit | not_better | 0.9774 | 0.9847 | $0.0011 | I'll add a lightweight "pair-completion" booster using the two most frequent observed item sizes:... |
| 84 | edit | improved | 0.9876 | 0.9876 | $0.0009 | I'll make the residual-utility computation distribution-aware in a cheap way: keep the online his... |
| 85 | edit | improved | 0.9881 | 0.9881 | $0.0009 | I will add a score-dependent "worst-fit tolerance" term that mildly penalizes choosing a bin whos... |
| 86 | edit | improved | 0.9883 | 0.9883 | $0.0008 | I'll replace the exponential/utility-scaling score with a calibrated log-utility that composes th... |
| 87 | edit | not_better | 0.9883 | 0.9883 | $0.0008 | I'll add a small "residual-complement" term that lightly prefers residuals which are reachable by... |
| 88 | edit | not_better | 0.8822 | 0.9883 | $0.0007 | I'll replace the hard-coded reachability and modal-size heuristics with a cleaner, distribution-a... |
| 89 | edit | not_better | 0.9567 | 0.9883 | $0.0008 | I'll tune the balance between exact-fit bonus and residual-utility by replacing the fixed 5.0 exa... |
| 90 | edit | not_better | 0.9883 | 0.9883 | $0.0008 | I will add a mild "least-loaded tie-break" penalty so that, when residuals are otherwise similar,... |
| 91 | edit | not_better | 0.9590 | 0.9883 | $0.0008 | I'll replace the fixed residual-utility lookup with a score that directly estimates the expected ... |
| 92 | edit | not_better | 0.9878 | 0.9883 | $0.0009 | Replace the binary reachability term with a probability-weighted "number of likely completing siz... |
| 93 | edit | improved | 0.9893 | 0.9893 | $0.0008 | I'll refine the exact-fit bonus to be adaptive: distinguish a residual that can be filled exactly... |
| 94 | edit | not_better | 0.9769 | 0.9893 | $0.0009 | I'll soften the aggressive log-utility with a small best-fit (smallest-residual) preference that ... |
| 95 | edit | not_better | 0.9864 | 0.9893 | $0.0009 | I'll add a “future-fit” penalty that slightly discounts bins whose residual, after placing the it... |
| 96 | edit | not_better | 0.9893 | 0.9893 | $0.0009 | I'll add a small "bin index tie-break" preference: among bins with equal score, prefer the one th... |
| 97 | edit | improved | 0.9898 | 0.9898 | $0.0011 | Extend the reachability marking from pairs to triples of the most probable item sizes, so residua... |
| 98 | edit | not_better | 0.9893 | 0.9898 | $0.0010 | I'll make the reachability term probability-weighted rather than binary, accumulating the actual ... |
| 99 | edit | not_better | 0.9898 | 0.9898 | $0.0009 | I'll replace the heuristic score with a principled "expected future waste" estimate: for each can... |
| 100 | edit | not_better | 0.9898 | 0.9898 | $0.0009 | I'll add an adaptive exact-fit bonus that additionally rewards bins where the residual equals the... |
| 101 | edit | not_better | 0.9499 | 0.9898 | $0.0008 | I'll replace the hand-tuned linear combination with a cleaner best-fit baseline modulated by a re... |
| 102 | edit | not_better | 0.9878 | 0.9898 | $0.0009 | I'll add an adaptive penalty that discourages creating residuals just below the most probable ite... |
| 103 | edit | not_better | 0.9767 | 0.9898 | $0.0009 | I'll tune the best-fit tendency by strengthening the linear closeness term (residual near zero fa... |
| 104 | edit | not_better | 0.9788 | 0.9898 | $0.0008 | The "avoid" penalty and the anchor-similarity terms appear to hurt (removing/weakening them dropp... |
| 105 | edit | not_better | 0.9590 | 0.9898 | $0.0009 | The `_UTIL` term is a coarse 0/1 indicator over a 101-entry histogram, which adds noise more than... |
| 106 | edit | improved | 0.9923 | 0.9923 | $0.0012 | I'll smooth the residual-probability lookup by convolving the per-integer value arrays with a sma... |
| 107 | edit | not_better | 0.9908 | 0.9923 | $0.0010 | Add a self-tuning multiplier on the reachability bonus based on whether the running utilization s... |
| 108 | edit | not_better | 0.9910 | 0.9923 | $0.0010 | I'll add a lightweight online best-fit tie-breaker derived from the observed item histogram: comp... |
| 109 | edit | not_better | 0.9910 | 0.9923 | $0.0010 | I'll replace the fixed exact-fit bonus constant with a stronger, smoothly-localized best-fit term... |
| 110 | edit | improved | 0.9928 | 0.9928 | $0.0010 | I'll replace the coarse 0/1 reachability indicator with a proper "can this residual be exactly fi... |
| 111 | edit | not_better | 0.9925 | 0.9928 | $0.0010 | Sharpen and strengthen the near-zero best-fit kernel (reduce its width and raise its weight) so b... |
| 112 | edit | not_better | 0.9745 | 0.9928 | $0.0010 | I'll strengthen the exact-fit preference with a small residual-tightening term that mildly favors... |
| 113 | edit | not_better | 0.9918 | 0.9928 | $0.0010 | I'll add a bounded "rare-residual" term: estimate from the observed histogram the probability tha... |
| 114 | edit | not_better | 0.9918 | 0.9928 | $0.0011 | I'll add an online "large-item reserve" term that discourages using a bin for a small item when t... |
| 115 | edit | not_better | 0.9800 | 0.9928 | $0.0010 | I'll replace the brittle multi-term heuristic with a single, well-grounded score derived from the... |
| 116 | edit | not_better | 0.9925 | 0.9928 | $0.0010 | I'll replace the crude modal-probability-scaled exact-fit bonus with an online estimate of the pr... |
| 117 | edit | not_better | 0.9908 | 0.9928 | $0.0010 | I'll add an online estimate of the chance that a leftover residual will be exactly filled by one ... |
| 118 | edit | not_better | 0.9925 | 0.9928 | $0.0010 | Increase the exact-fit bonus and near-zero kernel weight substantially so residual-zero bins are ... |
| 119 | edit | not_better | 0.9928 | 0.9928 | $0.0010 | I will replace the smoothed histogram-based value with a proper "future closability" score comput... |
| 120 | edit | not_better | 0.9871 | 0.9928 | $0.0010 | I'll add a mild residual-minimization tiebreak that, among bins that are not exact fits, prefers ... |
| 121 | edit | not_better | 0.9590 | 0.9928 | $0.0010 | Replace the noisy multi-term score with a value function dominated by classic best-fit (smaller l... |
| 122 | edit | not_better | 0.9928 | 0.9928 | $0.0011 | I'll add a "waste-avoidance" term: bins whose residual (after placing the item) is small but nonz... |
| 123 | edit | not_better | 0.9590 | 0.9928 | $0.0009 | I'll add a proper one-step lookahead value function: instead of only scoring residual closability... |
| 124 | edit | not_better | 0.9928 | 0.9928 | $0.0011 | The current rule is essentially best-fit; the main remaining loss vs. the lower bound comes from ... |
| 125 | edit | not_better | 0.9905 | 0.9928 | $0.0009 | I will replace the ad-hoc score with a Sum-of-Squares/Subset-Sum "closability" formulation: compu... |
| 126 | edit | not_better | 0.9910 | 0.9928 | $0.0011 | I'll add a light "aging" mechanism: track how many items have passed since each bin received its ... |
| 127 | edit | not_better | 0.9583 | 0.9928 | $0.0009 | I'll replace the ad-hoc closability terms with a proper expected-continuation lookahead: for each... |
| 128 | edit | not_better | 0.9588 | 0.9928 | $0.0011 | I'll replace the ad-hoc scoring with a principled expected-fit value: compute for each residual t... |
| 129 | edit | not_better | 0.9928 | 0.9928 | $0.0011 | I'll add an explicit "don't leave a residual that is smaller than the smallest likely future item... |
| 130 | edit | not_better | 0.9646 | 0.9928 | $0.0009 | I'll replace the fragile distribution-derived bonuses with a single, correctly-scaled expected-wa... |
| 131 | edit | not_better | 0.9900 | 0.9928 | $0.0011 | I'll add a distribution-adaptive "future-fit" term: estimate the most likely next item size(s) fr... |
| 132 | edit | not_better | 0.9928 | 0.9928 | $0.0010 | The current rule is close to plain best-fit, so the biggest remaining lever is tie-breaking among... |
| 133 | edit | not_better | 0.9590 | 0.9928 | $0.0009 | I'll make the score a true best-fit on the residual while adding a well-scaled probabilistic "wil... |
| 134 | edit | gate_rejected | 0.9928 | 0.9928 | $0.0010 | I'll add a proactive "reserve for the modal item" term: estimate the modal future item size from ... |
| 135 | edit | not_better | 0.9590 | 0.9928 | $0.0016 | I'll make the primary term strictly monotone decreasing in the residual (true best-fit ordering, ... |
| 136 | edit | not_better | 0.9915 | 0.9928 | $0.0013 | I'll introduce a lightweight per-stream online tie-breaker that tracks the empirical mean leftove... |
| 137 | edit | not_better | 0.9910 | 0.9928 | $0.0010 | I'll replace the fragile histogram-derived bonuses with a simpler, more robust best-fit score tha... |
| 138 | edit | not_better | 0.9905 | 0.9928 | $0.0011 | I will blend the current histogram-driven best-fit rule with a classic pure best-fit fallback by ... |
| 139 | edit | not_better | 0.9743 | 0.9928 | $0.0009 | Replace the combinatorial histogram bonuses with a lightweight learned per-residual "closure valu... |
| 140 | edit | not_better | 0.9590 | 0.9928 | $0.0006 | I'll strip the fragile histogram-derived bonuses down to a direct, monotone best-fit score (a smo... |
| 141 | edit | not_better | 0.9925 | 0.9928 | $0.0011 | The current rule can strand a bin when the leftover is smaller than the smallest item likely to a... |
| 142 | edit | not_better | 0.9590 | 0.9928 | $0.0008 | I'll replace the noisy histogram-driven bonus terms with a robust hybrid: a crisp best-fit orderi... |
| 143 | edit | not_better | 0.9913 | 0.9928 | $0.0010 | Increase the exact-fit bonus magnitude and widen its smooth near-zero reinforcement so that closi... |
| 144 | edit | not_better | 0.9918 | 0.9928 | $0.0011 | I'll add a term that computes, for each candidate leftover, the exact-closure probability against... |
| 145 | edit | not_better | 0.9908 | 0.9928 | $0.0010 | I'll add a gentle term based on the probability that a leftover residual can be exactly closed by... |
| 146 | edit | not_better | 0.9878 | 0.9928 | $0.0011 | I will add a lightweight adaptive term that promotes residuals which are "just below the next lik... |
| 147 | edit | not_better | 0.7548 | 0.9928 | $0.0011 | Add a small penalty for "dead" residuals: estimate the probability of seeing an item small enough... |
| 148 | edit | not_better | 0.9579 | 0.9928 | $0.0010 | I'll replace the modal-probability-scaled exact-fit and near-zero Gaussian bonuses with fixed, we... |
| 149 | edit | not_better | 0.9923 | 0.9928 | $0.0010 | I'll add a term that promotes bins whose leftover residual can likely be exactly closed by a sing... |
| 150 | edit | not_better | 0.9590 | 0.9928 | $0.0008 | I'll replace the fragile convolution/reach machinery with a cleaner, well-scaled hybrid: keep a c... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,95 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Distribution-adaptive best-fit with a learned residual-value estimate."""
 import numpy as np
 
 
+_COUNTS = np.ones(101, dtype=np.float64)
+_TOTAL = 101.0
+
+_UTIL = np.zeros(101, dtype=np.float64)
+_REACH = np.zeros(101, dtype=np.float64)
+_DIRTY = True
+
+
+def _smooth(arr, sigma=1.0):
+    """Small Gaussian smoothing over the integer residual axis."""
+    k = int(3 * sigma)
+    xs = np.arange(-k, k + 1, dtype=np.float64)
+    w = np.exp(-0.5 * (xs / sigma) ** 2)
+    w /= w.sum()
+    padded = np.concatenate([np.full(k, arr[0], dtype=np.float64), arr,
+                             np.full(k, arr[-1], dtype=np.float64)])
+    return np.convolve(padded, w, mode='valid')
+
+
+def _rebuild_util():
+    global _UTIL, _DIRTY, _REACH
+    probs = _COUNTS / _TOTAL
+
+    top = np.argsort(probs)[::-1][:14]
+    top = [int(t) for t in top if probs[t] > probs.mean()]
+
+    util = probs.copy()
+
+    # reach[s]: probability-like weight that residual s can be exactly closed
+    # by 1..3 future items drawn from the observed (top) support.
+    reach = np.zeros(101, dtype=np.float64)
+    reach[0] = 1.0
+    for s in top:
+        if 0 < s <= 100:
+            reach[s] = max(reach[s], probs[s])
+
+    for a in top:
+        if a <= 0 or a > 100:
+            continue
+        pa = probs[a]
+        for b in top:
+            s = a + b
+            if 0 < s <= 100:
+                w = pa * probs[b]
+                util[s] += w
+                reach[s] = max(reach[s], w)
+            for c in top:
+                t = a + b + c
+                if 0 < t <= 100:
+                    reach[t] = max(reach[t], pa * probs[b] * probs[c])
+
+    _UTIL = _smooth(util)
+    _REACH = _smooth(reach)
+    _DIRTY = False
+
+
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    global _COUNTS, _TOTAL, _DIRTY
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    residual = (bins - item).astype(np.float64)
+
+    if _DIRTY:
+        _rebuild_util()
+
+    ri = np.clip(np.round(residual).astype(np.int64), 0, 100)
+
+    # Value of a leftover: how easily it can be exactly closed later.
+    val = _UTIL[ri]
+    score = np.log(val + 1e-9)
+
+    score += 0.15 * _REACH[ri]
+
+    m = _COUNTS / _TOTAL
+    anchor = int(np.argmax(m[1:]) + 1)
+    modal_p = m[anchor]
+
+    # Sharp, strongly-weighted best-fit: residual exactly 0 is by far the most
+    # valuable, so bins that can be closed now are decisively preferred.
+    score += (residual == 0.0).astype(np.float64) * (6.0 + 3.0 * modal_p)
+
+    # Narrow Gaussian best-fit term centered at 0 so small leftovers are
+    # favored without the noisy anchor-shift.
+    score += (0.6 + 0.8 * modal_p) * np.exp(-0.5 * (residual / 3.0) ** 2)
+
+    _COUNTS[item] += 1.0
+    _TOTAL += 1.0
+    _DIRTY = True
+
+    return score
 # EVOLVE-BLOCK-END
```

## Explanation

Two-sided ablation of `priority` (16 parts, 32 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 63 | `global _COUNTS, _TOTAL, _DIRTY` | -0.9928 | essential: the program fails or turns invalid without it |
| 65 | `residual = (bins - item).astype(np.float64)` | -0.9928 | essential: the program fails or turns invalid without it |
| 70 | `ri = np.clip(np.round(residual).astype(np.int64), 0, 100)` | -0.9928 | essential: the program fails or turns invalid without it |
| 73 | `val = _UTIL[ri]` | -0.9928 | essential: the program fails or turns invalid without it |
| 74 | `score = np.log(val + 1e-09)` | -0.9928 | essential: the program fails or turns invalid without it |
| 78 | `m = _COUNTS / _TOTAL` | -0.9928 | essential: the program fails or turns invalid without it |
| 79 | `anchor = int(np.argmax(m[1:]) + 1)` | -0.9928 | essential: the program fails or turns invalid without it |
| 80 | `modal_p = m[anchor]` | -0.9928 | essential: the program fails or turns invalid without it |
| 92 | `_DIRTY = True` | -0.3105 | matters |
| 84 | `score += (residual == 0.0).astype(np.float64) * (6.0 + 3.0 * modal_p)` | -0.2824 | matters |
| 91 | `_TOTAL += 1.0` | -0.1575 | matters |
| 67 | `if _DIRTY: ...` | -0.0340 | matters |
| 68 | `_rebuild_util()` | -0.0340 | matters |
| 90 | `_COUNTS[item] += 1.0` | -0.0333 | matters |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 76: `score += 0.15 * _REACH[ri]`
- line 88: `score += (0.6 + 0.8 * modal_p) * np.exp(-0.5 * (residual / 3.0) ** 2)`

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9928 | 0.9893 |
| minimal (2 parts removed) | 0.9923 | 0.9890 |

Minimal program:

```python
"""Distribution-adaptive best-fit with a learned residual-value estimate."""
import numpy as np
_COUNTS = np.ones(101, dtype=np.float64)
_TOTAL = 101.0
_UTIL = np.zeros(101, dtype=np.float64)
_REACH = np.zeros(101, dtype=np.float64)
_DIRTY = True

def _smooth(arr, sigma=1.0):
    """Small Gaussian smoothing over the integer residual axis."""
    k = int(3 * sigma)
    xs = np.arange(-k, k + 1, dtype=np.float64)
    w = np.exp(-0.5 * (xs / sigma) ** 2)
    w /= w.sum()
    padded = np.concatenate([np.full(k, arr[0], dtype=np.float64), arr, np.full(k, arr[-1], dtype=np.float64)])
    return np.convolve(padded, w, mode='valid')

def _rebuild_util():
    global _UTIL, _DIRTY, _REACH
    probs = _COUNTS / _TOTAL
    top = np.argsort(probs)[::-1][:14]
    top = [int(t) for t in top if probs[t] > probs.mean()]
    util = probs.copy()
    reach = np.zeros(101, dtype=np.float64)
    reach[0] = 1.0
    for s in top:
        if 0 < s <= 100:
            reach[s] = max(reach[s], probs[s])
    for a in top:
        if a <= 0 or a > 100:
            continue
        pa = probs[a]
        for b in top:
            s = a + b
            if 0 < s <= 100:
                w = pa * probs[b]
                util[s] += w
                reach[s] = max(reach[s], w)
            for c in top:
                t = a + b + c
                if 0 < t <= 100:
                    reach[t] = max(reach[t], pa * probs[b] * probs[c])
    _UTIL = _smooth(util)
    _REACH = _smooth(reach)
    _DIRTY = False

def priority(item, bins):
    global _COUNTS, _TOTAL, _DIRTY
    residual = (bins - item).astype(np.float64)
    if _DIRTY:
        _rebuild_util()
    ri = np.clip(np.round(residual).astype(np.int64), 0, 100)
    val = _UTIL[ri]
    score = np.log(val + 1e-09)
    m = _COUNTS / _TOTAL
    anchor = int(np.argmax(m[1:]) + 1)
    modal_p = m[anchor]
    score += (residual == 0.0).astype(np.float64) * (6.0 + 3.0 * modal_p)
    _COUNTS[item] += 1.0
    _TOTAL += 1.0
    _DIRTY = True
    return score
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_a5000 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 3
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_a5000-s3   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `c2537038d96342c397401cc97bd51bbba505762d`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bp_sh_a5000/evaluate.py` `0ac9a4a253a299d2`
- `problems/bp_sh_a5000/initial.py` `609927c5ea619a94`
- `problems/bp_sh_a5000/problem.md` `190017a698e23cd8`
- `problems/bp_sh_a5000/verify.py` `0c52b77a6e5ec18a`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
