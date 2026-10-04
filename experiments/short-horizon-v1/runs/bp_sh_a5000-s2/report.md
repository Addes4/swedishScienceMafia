# Research loop report: bp_sh_a5000

| | |
|---|---|
| problem | `bp_sh_a5000` |
| search | lean, 150 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.1391 of a $0.20 hard cap, 150 calls, 433,043 tokens |
| wall time | search 2460 s, baselines 81 s, explain 131 s |
| stopped | max_iters (stopped_early) |
| evaluations | 150 (147 valid), 10 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9590 | 0.9634 | |
| `best_program.py` (final incumbent) | 0.9952 | 0.9932 |  |
| baseline `funsearch_or` | 0.9702 | 0.9711 | `problems/bp_sh_a5000/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9938 | 0.9937 | `problems/bp_sh_a5000/baselines/funsearch_weibull.py` |
| baseline `sum_of_squares` | 0.9952 | 0.9950 | `problems/bp_sh_a5000/baselines/sum_of_squares.py` |
| minimal program (ablation) | 0.9952 | 0.9932 | 1 parts removed |

Audit: public 0.9590 → 0.9952 (+0.0362), hidden 0.9634 → 0.9932 (+0.0298); public − hidden gap of the final program 0.0020.

Against the baselines: the final program's public score is below the best baseline (`sum_of_squares`, 0.9952). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Add a small tie-breaking bonus so that among bins with equal fit, the one that is already occupie... |
| 2 | edit | not_better | 0.9590 | 0.9590 | $0.0003 | Replace greedy best-fit with a harmonic-like scoring that favors filling partly-used bins more ag... |
| 3 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll implement a "best fit decreasing"-style rule that reverses the priority in a bounded way: si... |
| 4 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll try a scored "best fit with lookahead-free residual shaping": among bins that fit, prefer th... |
| 5 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace pure best-fit with a variant of the "Sum of Squares" / bounding-based rule that acco... |
| 6 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | I'll replace pure best-fit with a "best-fit with a target-residual tie-break based on typical sma... |
| 7 | edit | not_better | 0.9544 | 0.9590 | $0.0005 | Replace pure best-fit with a "worst-fit among essentially-tied bins" rule: the real weakness of b... |
| 8 | edit | not_better | 0.9590 | 0.9590 | $0.0008 | Best-fit on individual items is weak for a Weibull(mean ~40) stream because it wastes space; a be... |
| 9 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll try a two-region strategy: keep pure best-fit for bins that become nearly full, but add a sm... |
| 10 | edit | not_better | 0.8300 | 0.9590 | $0.0007 | I'll implement the classic "Harmonic" bin-packing rule (a proven online algorithm that beats best... |
| 11 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Add a learned/statistical flavor: since best fit is already near-optimal here, I'll try the "Modi... |
| 12 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace pure best-fit with a two-parameter "residual-window" rule: since items have mean ~40... |
| 13 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll try an instance-adaptive mixing rule: track the running mean of past item sizes and, instead... |
| 14 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Replace pure best fit (which greedily closes bins at awkward residuals) with a "best fit plus lef... |
| 15 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Add a small "waste-avoidance" tie-breaker to best-fit: among bins with the same post-placement re... |
| 16 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll add a small margin-based perturbation to best-fit: score bins by post-placement residual as ... |
| 17 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll replace pure best-fit with a *combined* rule that briefly tries Best-Fit-Decreasing-like beh... |
| 18 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | The bin-choice rule I'll try is a duty-cycled mix: pure best-fit is near-optimal but occasionally... |
| 19 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | Replace pure best-fit (tightest post-placement residual) with a "best-fit plus small secondary ti... |
| 20 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a hybrid that reserves room for near-optimal packing: use best-fit nor... |
| 21 | edit | not_better | 0.9590 | 0.9590 | $0.0007 | I'll keep state across calls (an array of observed item sizes), and among the bins that fit, inst... |
| 22 | edit | not_better | 0.3978 | 0.9590 | $0.0004 | I'll try a classic "almost-worst-fit"/anti-best-fit variant: choose the bin that leaves the large... |
| 23 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a threshold rule that, for items large enough to matter, prefers filli... |
| 24 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | (no description) |
| 25 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll switch to a deterministic "best fit with a tiny residual-reuse guard": among bins whose post... |
| 26 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I'll try a randomized best-fit-and-worst-fit hybrid: with high probability do exact best fit (whi... |
| 27 | edit | not_better | 0.9590 | 0.9590 | $0.0007 | I'll use a small per-bin "closed-waste" memory: because best-fit ignores the future, I will keep ... |
| 28 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Add a deterministic tie-break on top of best fit: among bins that fit, prefer the one whose post-... |
| 29 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace pure best-fit with a "best-fit-with-lookahead" rule: among the bins that fit, prefer... |
| 30 | edit | not_better | 0.9590 | 0.9590 | $0.0004 | Replace pure best-fit with a hybrid that reverts to best-fit for most items but, when the item is... |
| 31 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | Replace pure best-fit with a modified best-fit that adds a small penalty proportional to the frac... |
| 32 | edit | invalid | 0.0000 | 0.9590 | $0.0006 | Add a lightweight per-stream statistical model: track the empirical distribution of recent item s... |
| 33 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I will replace pure best-fit with a bounded "best-fit with age-aware tie-break": keep best fit fo... |
| 34 | edit | not_better | 0.8299 | 0.9590 | $0.0006 | Replace pure best-fit with a two-level rule: keep best-fit as the primary criterion, but for item... |
| 35 | edit | not_better | 0.9481 | 0.9590 | $0.0005 | I'll implement a two-choice "best-fit-decreasing-like" adaptive rule: primary ranking stays best ... |
| 36 | edit | not_better | 0.9590 | 0.9590 | $0.0015 | Replace pure best-fit with a harmonic/rank-based rule: score each bin by a nonlinear function of ... |
| 37 | edit | not_better | 0.9556 | 0.9590 | $0.0008 | I'll use "best fit with unusable-residual penalty": primary best-fit ranking, but heavily penaliz... |
| 38 | edit | not_better | 0.9590 | 0.9590 | $0.0009 | I'll switch from pure best-fit to a two-level rule based on the classic "best-fit with a small-it... |
| 39 | edit | not_better | 0.9590 | 0.9590 | $0.0006 | I will implement "best fit with capacity-class bucketing": instead of maximizing fill exactly, pr... |
| 40 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I will replace the pure best-fit rule with a hybrid that keeps best-fit ranking but, when placing... |
| 41 | edit | not_better | 0.9590 | 0.9590 | $0.0005 | I'll replace pure best-fit with a two-choice adaptive rule: for each fit bin compute the post-pla... |
| 42 | edit | not_better | 0.9579 | 0.9590 | $0.0006 | I'll replace pure best-fit with a randomized "two-choice" rule: pick the best-fit candidate and a... |
| 43 | edit | improved | 0.9595 | 0.9595 | $0.0005 | Replace pure best-fit with a hybrid "best-fit-then-worst-fit for small items" rule: for items at ... |
| 44 | edit | improved | 0.9604 | 0.9604 | $0.0005 | I'll refine the small-item threshold and rule: keep best-fit for items above a threshold, and for... |
| 45 | edit | not_better | 0.9593 | 0.9604 | $0.0007 | I'll replace the ad-hoc small-item rule with a principled "residual value" function that scores a... |
| 46 | edit | not_better | 0.9604 | 0.9604 | $0.0005 | I'll replace the fixed residual threshold (15) in the small-item rule with a threshold derived fr... |
| 47 | edit | not_better | 0.9595 | 0.9604 | $0.0006 | Refine the small-item rule so that instead of a fixed "useful" threshold it rewards residuals tha... |
| 48 | edit | not_better | 0.9590 | 0.9604 | $0.0005 | I'll replace the small-item heuristic with a "fullest-fit among sufficiently-large residuals" rul... |
| 49 | edit | no_code | n/a | 0.9604 | $0.0005 | (no description) |
| 50 | edit | not_better | 0.9597 | 0.9604 | $0.0007 | For small items (≤20), after preferring perfect fits, restrict to bins whose residual stays ≥25 a... |
| 51 | edit | not_better | 0.9590 | 0.9604 | $0.0005 | I'll replace the small-item heuristic with a two-candidate approach based on the well-known "sum ... |
| 52 | edit | not_better | 0.9590 | 0.9604 | $0.0005 | Replace the small-item heuristic with a clean rule: strongly prefer a perfect fit, otherwise appl... |
| 53 | edit | not_better | 0.9595 | 0.9604 | $0.0005 | I'll change the small-item rule to a "residual near mean" ranking that first takes perfect fits, ... |
| 54 | edit | not_better | 0.9590 | 0.9604 | $0.0006 | I'll add a length-aware bucket-sum (energy) rule: for every item, compute the resulting residual ... |
| 55 | edit | improved | 0.9637 | 0.9637 | $0.0005 | I'll switch to a length-aware "modified best fit" that, for every item, first strongly prefers an... |
| 56 | edit | not_better | 0.9637 | 0.9637 | $0.0005 | Replace the ad-hoc small-item penalty with a principled "best fit but avoid leaving a residual to... |
| 57 | edit | not_better | 0.9609 | 0.9637 | $0.0005 | I will replace the current rule with one that, among bins that do not yield a perfect fit, prefer... |
| 58 | edit | improved | 0.9876 | 0.9876 | $0.0007 | I'll add a learned/statistical touch: track a running histogram of previously-seen items within e... |
| 59 | edit | improved | 0.9888 | 0.9888 | $0.0013 | Replace the simple ±2 neighborhood bonus with a richer usefulness estimate: exact-fit probability... |
| 60 | edit | improved | 0.9915 | 0.9915 | $0.0010 | I'll extend the gap-usefulness estimate from a pair-completion convolution to also account for tr... |
| 61 | edit | not_better | 0.9898 | 0.9915 | $0.0011 | I'll make the gap-usefulness combine exact single/pair/triple completion probabilities into a sin... |
| 62 | edit | not_better | 0.9822 | 0.9915 | $0.0011 | I will make the exact-fit preference the top term only when the residual is achievable, and repla... |
| 63 | edit | not_better | 0.9851 | 0.9915 | $0.0011 | I'll refine the gap-completability scoring so the exact-single, pair, and triple completion proba... |
| 64 | edit | not_better | 0.9878 | 0.9915 | $0.0008 | Replace the ad-hoc blend of exact/pair/triple/nearby/mean/tiny terms with a cleaner "best fit amo... |
| 65 | edit | not_better | 0.9883 | 0.9915 | $0.0010 | I'll replace the online-histogram usefulness terms with a tuned version that keeps the strong exa... |
| 66 | edit | improved | 0.9925 | 0.9925 | $0.0011 | I'll reduce variance/noise in the empirical estimates by using a recency-weighted histogram and a... |
| 67 | edit | gate_rejected | 0.9928 | 0.9925 | $0.0012 |  |
| 68 | edit | not_better | 0.9923 | 0.9925 | $0.0011 | I'll replace the fragile every-call full triple convolution with a cheaper, more stable pair-comp... |
| 69 | edit | not_better | 0.9920 | 0.9925 | $0.0011 | I'll add a light "residual equal to a common small item size" bias using the empirical histogram ... |
| 70 | edit | not_better | 0.9918 | 0.9925 | $0.0010 | I'll reduce the reliance on the noisy pair/triple convolution completability terms and instead ma... |
| 71 | edit | not_better | 0.9913 | 0.9925 | $0.0012 | I'll add a lightweight "residual matches a frequent recent item size" bonus computed directly fro... |
| 72 | edit | not_better | 0.9910 | 0.9925 | $0.0011 | The main inefficiency is leaving bins with residual in the 5–15 range that rarely get filled; I'l... |
| 73 | edit | not_better | 0.9501 | 0.9925 | $0.0010 | I'll simplify to a cleaner rule: strongly prefer exact fits, then rank by a reliable single-item ... |
| 74 | edit | not_better | 0.9900 | 0.9925 | $0.0010 | I'll make the priority rule a proper "best fit with a completability-aware residual value": inste... |
| 75 | edit | improved | 0.9935 | 0.9935 | $0.0012 | Bins with residual smaller than the smallest item seen so far (or smaller than 1) can never be fi... |
| 76 | edit | not_better | 0.9925 | 0.9935 | $0.0013 | Bins with small residuals 1..~10 are often stranded because the Weibull-like distribution rarely ... |
| 77 | edit | not_better | 0.9537 | 0.9935 | $0.0011 | I'll replace the ad-hoc exact/pair/triple weights with a single principled "completability" measu... |
| 78 | edit | not_better | 0.9935 | 0.9935 | $0.0015 | I'll add a targeted penalty/bonus term keyed on the empirically most common residual sizes that a... |
| 79 | edit | not_better | 0.9579 | 0.9935 | $0.0010 | The current rule ignores the classic best-fit heuristic's real strength: keeping bins as full as ... |
| 80 | edit | not_better | 0.9925 | 0.9935 | $0.0012 | I'll add an online learned residual-success table: track which residual sizes actually get exactl... |
| 81 | edit | not_better | 0.9930 | 0.9935 | $0.0012 | The triple-convolution and near-match terms add noise; I'll keep the strong exact/pair signals bu... |
| 82 | edit | not_better | 0.9524 | 0.9935 | $0.0011 | Replace the fixed prior/empirical histogram mixture and ad-hoc multi-convolution scoring with a c... |
| 83 | edit | not_better | 0.9546 | 0.9935 | $0.0008 | I'll switch the primary objective from the noisy multi-convolution "completability" scoring to th... |
| 84 | edit | not_better | 0.9930 | 0.9935 | $0.0013 | I will add a "future-fit awareness" term that estimates, from the current empirical item histogra... |
| 85 | edit | not_better | 0.9923 | 0.9935 | $0.0012 | I will tune the existing completion weights and decay using the fact that this rule already beats... |
| 86 | edit | not_better | 0.9588 | 0.9935 | $0.0011 | I'll replace the ad-hoc stranding/completion weights with a principled "expected future waste" sc... |
| 87 | edit | not_better | 0.9896 | 0.9935 | $0.0011 | The exact/pair/triple completion signals are valuable but the additive weights and the near-match... |
| 88 | edit | not_better | 0.9583 | 0.9935 | $0.0011 | I will replace the additive completion scoring with a cleaner two-stage rule: always take an exac... |
| 89 | edit | not_better | 0.9925 | 0.9935 | $0.0011 | Add a light "post-placement usefulness" tie-break based on the empirical distribution: estimate t... |
| 90 | edit | not_better | 0.9935 | 0.9935 | $0.0012 | I'll add an aggressive "anti-fragmentation" refinement: among bins that don't produce an exact fi... |
| 91 | edit | not_better | 0.9544 | 0.9935 | $0.0010 | I'll replace the noisy convolution-based completion signals with a principled "waste minimization... |
| 92 | edit | not_better | 0.9930 | 0.9935 | $0.0012 | Replace the heavily-prior-smoothed convolution signals with a sharper empirical exact/pair-comple... |
| 93 | edit | not_better | 0.9606 | 0.9935 | $0.0017 | I'll add a "prefer already-used bins" term: penalize selecting a completely empty bin (remaining ... |
| 94 | edit | not_better | 0.9871 | 0.9935 | $0.0012 | I'll add a tunable "concentration toward fuller bins" term and reduce reliance on the noisy high-... |
| 95 | edit | not_better | 0.9935 | 0.9935 | $0.0013 | I'll make the stranding penalty adaptive to the observed minimum item size using a soft, distribu... |
| 96 | edit | not_better | 0.9893 | 0.9935 | $0.0013 | I'll replace the brittle hard-threshold stranding penalty with a smooth, probabilistic "future-fi... |
| 97 | edit | not_better | 0.9644 | 0.9935 | $0.0010 | I'll replace the noisy high-order convolution completion signals (which are dominated by prior sm... |
| 98 | edit | not_better | 0.9562 | 0.9935 | $0.0011 | I'll replace the dominated noisy completion ranking with a strong best-fit core: rank primarily b... |
| 99 | edit | invalid | 0.0000 | 0.9935 | $0.0012 | Shift from exact-completion signals toward a distribution-aware "best fit with future-fillability... |
| 100 | edit | not_better | 0.9928 | 0.9935 | $0.0013 | I'll add an item-size-aware "future feasibility" correction that anticipates whether the current ... |
| 101 | edit | not_better | 0.9935 | 0.9935 | $0.0014 | I'll replace the hard per-stream minimum-item stranding penalty with a soft, distribution-based e... |
| 102 | edit | not_better | 0.9928 | 0.9935 | $0.0013 | I'll add a "residual alignment" bonus that rewards residuals which match a size that would make t... |
| 103 | edit | not_better | 0.9888 | 0.9935 | $0.0011 | I'll replace the pair/triple convolution completion bonuses—computed over the whole histogram wit... |
| 104 | edit | not_better | 0.9918 | 0.9935 | $0.0013 | I'll add a strong "least-loaded / tightest-fit" secondary signal by making the exact perfect-fit ... |
| 105 | edit | improved | 0.9945 | 0.9945 | $0.0012 | I'll replace the heavy prior-smoothed convolutions with a sharper, cheaply-computed "future filla... |
| 106 | edit | not_better | 0.9943 | 0.9945 | $0.0012 | I'll sharpen the exact-match signal by computing the single-item density as a weighted blend of t... |
| 107 | edit | not_better | 0.9717 | 0.9945 | $0.0010 | I'll make the perfect-fit preference the dominant rule (strongly prefer exact residuals and near-... |
| 108 | edit | not_better | 0.9925 | 0.9945 | $0.0012 | I'll blend the single-item exact-fit density with the raw empirical histogram at the exact residu... |
| 109 | edit | gate_rejected | 0.9947 | 0.9945 | $0.0011 | Add an exponential-recency half-life so the empirical distribution reflects recent items more tha... |
| 110 | edit | not_better | 0.9943 | 0.9945 | $0.0012 | I will make the stranding penalty adaptive by tracking a recency-weighted minimum item size (rath... |
| 111 | edit | improved | 0.9952 | 0.9952 | $0.0012 | I'll add a "pair-fit with the current item" bonus that rewards a bin whose residual can be exactl... |
| 112 | edit | not_better | 0.9947 | 0.9952 | $0.0013 | The change adds a term rewarding bins whose resulting residual equals a frequently observed item ... |
| 113 | edit | not_better | 0.9938 | 0.9952 | $0.0013 | I'll add a mild tie-break that prefers residuals at or just above the current smallest-seen item ... |
| 114 | edit | not_better | 0.9943 | 0.9952 | $0.0012 | I'll replace the crude "typical item size" bonus and the noisy current-item complement term with ... |
| 115 | edit | not_better | 0.9915 | 0.9952 | $0.0011 | Replace the static prior-based histogram smoothing and the various heuristic bonuses with a direc... |
| 116 | edit | not_better | 0.9938 | 0.9952 | $0.0012 | I will replace the sharp `cur_dens * exp(-\|residual-item\|/6)` term with a "pair with current it... |
| 117 | edit | not_better | 0.5258 | 0.9952 | $0.0013 | I'll add a strong exact-match term against the "canonical residual" that best pairs with the curr... |
| 118 | edit | not_better | 0.9945 | 0.9952 | $0.0013 | I'll add a term that rewards residuals which, together with the smallest observed item size, can ... |
| 119 | edit | not_better | 0.9915 | 0.9952 | $0.0010 | I'll replace the hard-to-tune heuristic bonuses with a single, well-normalized "expected completa... |
| 120 | edit | not_better | 0.9938 | 0.9952 | $0.0010 | I'll add a "stranding" penalty based on the probability that the resulting residual can never be ... |
| 121 | edit | not_better | 0.9933 | 0.9952 | $0.0012 | I'll replace the noisy self-convolution pair-completion term (which uses raw counts and is domina... |
| 122 | edit | not_better | 0.9940 | 0.9952 | $0.0011 | Replace the noisy combo of exact/pair/mean-size bonuses with a single well-normalized "future fil... |
| 123 | edit | not_better | 0.9923 | 0.9952 | $0.0011 | I'll simplify by removing the noisy mean-size exponential bonus and the pair-convolution term, an... |
| 124 | edit | not_better | 0.9935 | 0.9952 | $0.0012 | I will add a "perfect-fit completion" term that rewards a bin whose residual leaves room for the ... |
| 125 | edit | not_better | 0.9590 | 0.9952 | $0.0010 | I'll replace the ad-hoc exponential bonuses and raw-count pair convolution with a properly normal... |
| 126 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | Increase the strength of the "stranding penalty" for residuals below the smallest observed size b... |
| 127 | edit | not_better | 0.9590 | 0.9952 | $0.0011 | Strengthen the best-fit secondary criterion so that, absent an exact fit, the item goes to the bi... |
| 128 | edit | not_better | 0.9928 | 0.9952 | $0.0012 | Add a term that rewards placements which make the resulting residual exactly fillable by the *cur... |
| 129 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | I'll remove the harmful "mild bonus for residuals close to the typical item size" (which pulls it... |
| 130 | edit | not_better | 0.9490 | 0.9952 | $0.0011 | I'll replace the fixed Weibull prior with a nonparametric prior learned from typical bin-packing ... |
| 131 | edit | not_better | 0.9593 | 0.9952 | $0.0011 | I'll make the strong perfect-fit bonus and the best-fit tie-break interact correctly: currently t... |
| 132 | edit | not_better | 0.9925 | 0.9952 | $0.0012 | I'll add a normalized, histogram-based single-item exact-completion bonus for the residual (the p... |
| 133 | edit | not_better | 0.9938 | 0.9952 | $0.0011 | I'll add a "pair-completion with the current item" bonus that rewards the bin whose residual, aft... |
| 134 | edit | invalid | 0.0000 | 0.9952 | $0.0011 | I'll simplify by removing the weak, noisy "close to mean size" bonus (which can pull items into b... |
| 135 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | Reduce the dominance of the usefulness terms so that among non-perfect fits the rule leans more c... |
| 136 | edit | not_better | 0.9947 | 0.9952 | $0.0013 | Add a harmonic/close-sized pairing term: reward bins whose residual is approximately equal to (10... |
| 137 | edit | not_better | 0.9530 | 0.9952 | $0.0009 | Replace the unnormalized soft "pair completion" convolution term and other weak bonuses with a si... |
| 138 | edit | not_better | 0.9623 | 0.9952 | $0.0010 | I'll make the exact-fit/large-usefulness terms properly dominate only when clearly justified, and... |
| 139 | edit | not_better | 0.9544 | 0.9952 | $0.0010 | I'll reformulate the scoring around a single well-scaled, monotone-in-residual usefulness that st... |
| 140 | edit | not_better | 0.9556 | 0.9952 | $0.0010 | Reduce the noisy, over-scaled exact and pair probabilities to a much gentler term and make the do... |
| 141 | edit | not_better | 0.9947 | 0.9952 | $0.0012 | I'll remove the recency decay on the empirical histogram (it makes the distribution noisy and the... |
| 142 | edit | not_better | 0.9947 | 0.9952 | $0.0012 | I'll keep the exact-fit bonus and best-fit tie-break but fix the bug where the pair-completion co... |
| 143 | edit | not_better | 0.9898 | 0.9952 | $0.0011 | The empirical density smoothing currently "smears" probability across neighbours and clips at the... |
| 144 | edit | not_better | 0.9549 | 0.9952 | $0.0010 | Replace the noisy multi-term completion scoring with a stable, principled "best fit plus explicit... |
| 145 | edit | not_better | 0.9933 | 0.9952 | $0.0013 | Add a "double exact-fit ranking" refinement: within residuals that are completable, prefer the bi... |
| 146 | edit | not_better | 0.9933 | 0.9952 | $0.0012 | I'll tune the existing best-scoring rule by increasing the exact-fit binary bonus and strengtheni... |
| 147 | edit | not_better | 0.9935 | 0.9952 | $0.0012 | I'll tune the dominant useful-signal: strengthen the exact single-item and pair completion probab... |
| 148 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | I'll add a targeted bonus for bins whose residual is small enough to be filled by a single future... |
| 149 | edit | not_better | 0.9945 | 0.9952 | $0.0012 | I'll replace the sharply-heaped usefulness scale (5000/1000) with a normalized probability-of-com... |
| 150 | edit | not_better | 0.9943 | 0.9952 | $0.0012 | The current rule's completion bonus for residuals equal to a typical item size (mean-size Gaussia... |

## Change: `initial.py` → `best_program.py`

```diff
--- initial.py
+++ best_program.py
@@ -1,14 +1,105 @@
 # EVOLVE-BLOCK-START
-"""Baseline: best fit. Put the item in the bin it fits most tightly."""
+"""Empirical-residual best fit with completion-aware future-fillability.
+
+Strongly prefer exact perfect fits. Otherwise score a placement by how
+likely its resulting residual can be consumed by future items, using a
+smoothed online estimate of the item-size distribution:
+  - probability a single future item exactly equals the residual,
+  - probability a pair of future items sums to the residual,
+plus a mild best-fit tie-break and a softened stranding penalty.
+"""
 import numpy as np
+
+# Parametric prior: Weibull-ish shape with mean ~40, over sizes 1..100.
+_sizes = np.arange(101, dtype=np.float64)
+_shape = 2.0
+_scale = 45.0
+_w_prior = (_sizes[1:] / _scale) ** (_shape - 1.0) * np.exp(-(_sizes[1:] / _scale) ** _shape)
+_w_prior = _w_prior / _w_prior.sum()
+_prior = np.zeros(101, dtype=np.float64)
+_prior[1:] = _w_prior
+_prior_scale = 30.0  # weight of prior relative to observed counts
+
+# Empirical distribution over item sizes 1..100, updated online.
+_hist = 1.0 + _prior_scale * _prior
+_seen = 0.0
+
+_min_item = 100.0  # smallest item size observed so far in this stream
+
+_DECAY = 0.999  # mild recency weighting to adapt within a stream
+
+# Precomputed smoothing kernel (over residual distance).
+_kdist = np.arange(-2, 3, dtype=np.float64)
+_ksmooth = np.exp(-0.5 * (_kdist / 1.0) ** 2)
+_ksmooth /= _ksmooth.sum()
 
 
 def priority(item, bins):
-    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).
+    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
+    global _hist, _seen, _min_item
 
-    item: integer size of the arriving item, 1..100.
-    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
-          including unused bins (remaining capacity 100), in bin order.
-    """
-    return -(bins - item)
+    residual = bins - item
+
+    # Strongly prefer an exact perfect fit.
+    perfect = residual == 0
+
+    # Current estimate of the item-size distribution over 1..100.
+    h = _hist / _hist.sum()
+
+    r_idx = np.clip(residual, 0, 100).astype(np.int64)
+
+    # Smoothed density at the residual (robustness to small sampling gaps).
+    dens = np.zeros(101, dtype=np.float64)
+    for k, w in enumerate(_ksmooth):
+        shift = k - 2
+        src = np.clip(np.arange(101) + shift, 0, 100)
+        dens += w * h[src]
+
+    # Probability a single future item exactly equals this residual.
+    exact = dens[r_idx]
+
+    # Pair-completion probability via self-convolution of the empirical hist.
+    conv2 = np.convolve(_hist[1:], _hist[1:])  # conv2[k] for sum k+2
+    total2 = _hist.sum() * _hist.sum()
+    pair = np.zeros(101, dtype=np.float64)
+    k = min(101, conv2.size)
+    pair[2:2 + k] = conv2[:101 - 2] / total2
+
+    # Complementary fit: residual that pairs with the *current* item size to
+    # leave a small reusable leftover, or that the current item can help fill
+    # toward a common bin total. Reward residuals that equal a typical item.
+    mean_size = float(np.dot(np.arange(101), h))
+
+    # Combined usefulness: exact single > exact pair.
+    usefulness = (
+        5000.0 * exact
+        + 1000.0 * pair[r_idx]
+    )
+
+    # Mild bonus for residuals close to the typical item size.
+    usefulness += 40.0 * np.exp(-np.abs(residual - mean_size) / 10.0)
+
+    # Sharp complement bonus: residual likely to be filled exactly by a single
+    # future item of the current item's size class (encourages pairing like items).
+    cur_dens = float(dens[item]) if 0 <= item <= 100 else 0.0
+    usefulness += 300.0 * cur_dens * np.exp(-np.abs(residual - item) / 6.0)
+
+    # Mild best-fit tie-break: prefer smaller residuals.
+    score = usefulness - residual.astype(np.float64) * 0.02
+
+    # Penalize residuals that can never be filled again (below smallest seen).
+    min_obs = max(1.0, _min_item)
+    unusable = (residual > 0) & (residual < min_obs)
+    deficit = np.clip(min_obs - residual, 0.0, None)
+    score -= unusable * (20.0 + 8.0 * deficit)
+
+    # Update histogram for future items, with mild decay for recency.
+    _hist *= _DECAY
+    _hist[item] += 1.0
+    _seen += 1.0
+    if item < _min_item:
+        _min_item = float(item)
+
+    return score + perfect * 1e9
 # EVOLVE-BLOCK-END
+
```

## Explanation

Two-sided ablation of `priority` (41 parts, 40 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 39 | `global _hist, _seen, _min_item` | -0.9952 | essential: the program fails or turns invalid without it |
| 41 | `residual = bins - item` | -0.9952 | essential: the program fails or turns invalid without it |
| 41 | `term + bins` | -0.9952 | essential: the program fails or turns invalid without it |
| 44 | `perfect = residual == 0` | -0.9952 | essential: the program fails or turns invalid without it |
| 47 | `h = _hist / _hist.sum()` | -0.9952 | essential: the program fails or turns invalid without it |
| 49 | `r_idx = np.clip(residual, 0, 100).astype(np.int64)` | -0.9952 | essential: the program fails or turns invalid without it |
| 52 | `dens = np.zeros(101, dtype=np.float64)` | -0.9952 | essential: the program fails or turns invalid without it |
| 54 | `shift = k - 2` | -0.9952 | essential: the program fails or turns invalid without it |
| 55 | `src = np.clip(np.arange(101) + shift, 0, 100)` | -0.9952 | essential: the program fails or turns invalid without it |
| 59 | `exact = dens[r_idx]` | -0.9952 | essential: the program fails or turns invalid without it |
| 62 | `conv2 = np.convolve(_hist[1:], _hist[1:])` | -0.9952 | essential: the program fails or turns invalid without it |
| 63 | `total2 = _hist.sum() * _hist.sum()` | -0.9952 | essential: the program fails or turns invalid without it |
| 64 | `pair = np.zeros(101, dtype=np.float64)` | -0.9952 | essential: the program fails or turns invalid without it |
| 65 | `k = min(101, conv2.size)` | -0.9952 | essential: the program fails or turns invalid without it |
| 71 | `mean_size = float(np.dot(np.arange(101), h))` | -0.9952 | essential: the program fails or turns invalid without it |
| 74 | `usefulness = 5000.0 * exact + 1000.0 * pair[r_idx]` | -0.9952 | essential: the program fails or turns invalid without it |
| 84 | `cur_dens = float(dens[item]) if 0 <= item <= 100 else 0.0` | -0.9952 | essential: the program fails or turns invalid without it |
| 88 | `score = usefulness - residual.astype(np.float64) * 0.02` | -0.9952 | essential: the program fails or turns invalid without it |
| 91 | `min_obs = max(1.0, _min_item)` | -0.9952 | essential: the program fails or turns invalid without it |
| 92 | `unusable = (residual > 0) & (residual < min_obs)` | -0.9952 | essential: the program fails or turns invalid without it |
| 93 | `deficit = np.clip(min_obs - residual, 0.0, None)` | -0.9952 | essential: the program fails or turns invalid without it |
| 100 | `if item < _min_item: ...` | -0.4567 | matters |
| 101 | `_min_item = float(item)` | -0.4567 | matters |
| 41 | `term - item` | -0.0891 | matters |
| 88 | `term + usefulness` | -0.0422 | matters |
| 53 | `for k, w in enumerate(_ksmooth): ...` | -0.0147 | matters |
| 56 | `dens += w * h[src]` | -0.0147 | matters |
| 75 | `term + 5000.0 * exact` | -0.0111 | matters |
| 54 | `term - 2` | -0.0050 | matters |
| 66 | `pair[2:2 + k] = conv2[:101 - 2] / total2` | -0.0035 | matters |
| 76 | `term + 1000.0 * pair[r_idx]` | -0.0035 | matters |
| 54 | `term + k` | -0.0020 | no effect alone |
| 88 | `term - residual.astype(np.float64) * 0.02` | -0.0007 | no effect alone |
| 98 | `_hist[item] += 1.0` | -0.0007 | no effect alone |
| 85 | `usefulness += 300.0 * cur_dens * np.exp(-np.abs(residual - item) / 6.0)` | -0.0007 | no effect alone |
| 80 | `usefulness += 40.0 * np.exp(-np.abs(residual - mean_size) / 10.0)` | -0.0007 | no effect alone |
| 97 | `_hist *= _DECAY` | -0.0005 | no effect alone |
| 94 | `score -= unusable * (20.0 + 8.0 * deficit)` | -0.0002 | no effect alone |

**Parts that can go** (removed together without moving the public score beyond the tolerance):

- line 99: `_seen += 1.0`

Not tested (evaluation limit 40): 2 parts.

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.9952 | 0.9932 |
| minimal (1 parts removed) | 0.9952 | 0.9932 |

Minimal program:

```python
"""Empirical-residual best fit with completion-aware future-fillability.

Strongly prefer exact perfect fits. Otherwise score a placement by how
likely its resulting residual can be consumed by future items, using a
smoothed online estimate of the item-size distribution:
  - probability a single future item exactly equals the residual,
  - probability a pair of future items sums to the residual,
plus a mild best-fit tie-break and a softened stranding penalty.
"""
import numpy as np
_sizes = np.arange(101, dtype=np.float64)
_shape = 2.0
_scale = 45.0
_w_prior = (_sizes[1:] / _scale) ** (_shape - 1.0) * np.exp(-(_sizes[1:] / _scale) ** _shape)
_w_prior = _w_prior / _w_prior.sum()
_prior = np.zeros(101, dtype=np.float64)
_prior[1:] = _w_prior
_prior_scale = 30.0
_hist = 1.0 + _prior_scale * _prior
_seen = 0.0
_min_item = 100.0
_DECAY = 0.999
_kdist = np.arange(-2, 3, dtype=np.float64)
_ksmooth = np.exp(-0.5 * (_kdist / 1.0) ** 2)
_ksmooth /= _ksmooth.sum()

def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties)."""
    global _hist, _seen, _min_item
    residual = bins - item
    perfect = residual == 0
    h = _hist / _hist.sum()
    r_idx = np.clip(residual, 0, 100).astype(np.int64)
    dens = np.zeros(101, dtype=np.float64)
    for k, w in enumerate(_ksmooth):
        shift = k - 2
        src = np.clip(np.arange(101) + shift, 0, 100)
        dens += w * h[src]
    exact = dens[r_idx]
    conv2 = np.convolve(_hist[1:], _hist[1:])
    total2 = _hist.sum() * _hist.sum()
    pair = np.zeros(101, dtype=np.float64)
    k = min(101, conv2.size)
    pair[2:2 + k] = conv2[:101 - 2] / total2
    mean_size = float(np.dot(np.arange(101), h))
    usefulness = 5000.0 * exact + 1000.0 * pair[r_idx]
    usefulness += 40.0 * np.exp(-np.abs(residual - mean_size) / 10.0)
    cur_dens = float(dens[item]) if 0 <= item <= 100 else 0.0
    usefulness += 300.0 * cur_dens * np.exp(-np.abs(residual - item) / 6.0)
    score = usefulness - residual.astype(np.float64) * 0.02
    min_obs = max(1.0, _min_item)
    unusable = (residual > 0) & (residual < min_obs)
    deficit = np.clip(min_obs - residual, 0.0, None)
    score -= unusable * (20.0 + 8.0 * deficit)
    _hist *= _DECAY
    _hist[item] += 1.0
    if item < _min_item:
        _min_item = float(item)
    return score + perfect * 1000000000.0
```

## Reproduce

```bash
python -m autoresearch.loop problems/bp_sh_a5000 --budget 0.2 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 150 --seed 2
python -m autoresearch.loop --report experiments/short-horizon-v1/runs/bp_sh_a5000-s2   # rebuild this report
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
