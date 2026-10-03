# Discover → Simplify → Explain: experiment write-up (simplify-v1)

Branch: `simplify-explain` · Code: `falsify/simplify.py` · Tests: `tests/test_simplify.py` · Protocol: `experiments/SIMPLIFY_PROTOCOL.md` · Raw results: `experiments/simplify-v1/report.json`, `report.md`

## 1. Question

After an automated search discovers a "winning" heuristic, can we (a) reduce it to a short, human-readable rule without losing measured quality, (b) show experimentally which of its components matter, and (c) state what it actually does in one sentence?

The idea is a post-discovery stage for an algorithm-discovery loop. It turns an opaque weight vector into a rule with supporting ablations, and it stays tightly scoped: a fixed packing-execution budget and fixed simplification moves, no open-ended refactoring.

## 2. Setting (inherited from the discovery experiments)

- **Problem:** online bin packing with capacity 100. Each instance has 80 integer items in 1–100, placed in arrival order with no lookahead.
- **Heuristic space:** a fixed C++ packer (`falsify/packing.cpp`) places each item in the feasible open bin with the highest linear score `Σ wⱼ·fⱼ(gap, item)`, where `gap` is the space left after placing the item. Ties go to the earliest bin, and a new bin is opened only if nothing fits. There are 12 features:

  | idx | feature | idx | feature |
  |---|---|---|---|
  | 0 | gap/100 | 6 | gap ≥ item |
  | 1 | (gap/100)² | 7 | \|gap/100 − .25\| |
  | 2 | 1/(gap+1) | 8 | \|gap/100 − .5\| |
  | 3 | gap == 0 | 9 | \|gap/100 − .75\| |
  | 4 | 0 < gap < 10 | 10 | 0 < gap < 33 |
  | 5 | 0 < gap < item | 11 | 0 < gap < 50 |

- **Reference:** best-fit is `w = [-1, 0, …, 0]`.
- **Instance families:** five training families (uniform, small, large, bimodal, complementary) and three shifted families (near_thirds, near_halves, bands).
- **Candidates simplified:** 43 distinct weight vectors, deduplicated after scale normalization:
  - the final incumbents of all 60 `experiments/local-v1` runs (3 arms × 20 seeds of stochastic evolution starting from best-fit), which leave 29 distinct vectors after deduplication;
  - 14 Codex-proposed vectors from `codex_candidates.json` and `codex_revision.json`.

## 3. Method

All of it is in `falsify/simplify.py`, and it only imports from `falsify/core.py`. Nothing in the discovery code or its outputs was modified.

1. **Fresh, separate data.** Three new suites, each with its own seed and none sharing a seed with search or with the local-v1 audit (seed 982451653 is not reused):
   - *selection*: 500 instances, training families, seed 7000001. Used only to pick which candidate to study in depth.
   - *simplification*: 1000 instances, training families, seed 7000002. Used for every simplification decision.
   - *confirmation*: 800 instances, all 8 families, seed 7000003. Generated only after simplification finished, and used for the final comparisons, ablations and witness search.
2. **Winner selection:** lowest mean bins on the selection suite. Ties go to the candidate with more non-zero terms, which is the hardest case for simplification.
3. **Normalization:** weights are divided by max |w|. The packer takes an argmax, so positive rescaling never changes a packing (this is unit-tested).
4. **Simplification** (`simplify`), accepted while mean bins on the simplification suite are ≤ the original's mean + tol, with tol = 0.002 bins per instance:
   1. *Single-term shortcut:* try each existing term alone, keeping its sign. If any meets the tolerance, take the best; ties go to the term with the larger original weight.
   2. *Greedy backward elimination:* repeatedly drop the term whose removal costs least. Ties go to dropping the smaller-magnitude term.
   3. *Rounding:* round each surviving weight to one of the nearest {1, 2, 5}×10ᵏ values, if that stays within tolerance.
   4. *Budget:* every packing execution is counted, with a hard cap of 150,000 per simplification.
5. **Ablation** (`ablate`), on the confirmation suite: zero one term at a time and report the mean bin change with a paired bootstrap 95% CI (10,000 resamples, seed 739), the number of instances whose bin count changed, and the share of packings that stay identical.
6. **Explanation** (`explain`): a template-based English sentence. It recognises that single monotone terms (`-gap/100`, `-(gap/100)²`, `+1/(gap+1)`) are exactly best-fit, and that their opposites are exactly worst-fit.
7. **Witness** (`witness`): look for a confirmation instance where the simplified rule and best-fit use different numbers of bins, then shrink it by greedy item deletion into a small, readable example.
8. **Simplification map:** run the same simplification on all 43 candidates and record term counts before and after, which terms survive, and the resulting rules.

## 4. Results

### 4.1 Deep dive on the winner

- **Winner:** `counterexample_replay-4` (local-v1), with mean 41.172 bins on the selection suite and **11 non-zero terms**:

  `-1·gap/100 −0.031·(gap/100)² +0.160·1/(gap+1) +0.008·[0<gap<10] +0.061·[0<gap<item] +0.040·[gap≥item] −0.019·|x−.25| +0.152·|x−.5| +0.839·|x−.75| +0.181·[0<gap<33] −0.631·[0<gap<50]`

- **Simplified rule:** `-1·gap/100`, which is **exactly best-fit (11 → 1 term)**. The single-term shortcut found it directly. Simplification used 12,000 packing executions, well under the 150,000 budget.
- **Plain-language rule:** "Put each item in the feasible bin that leaves the smallest gap."

**Confirmation suite** (800 fresh instances, all 8 families):

| comparison | mean bins A | mean bins B | A − B | 95% CI | wins/ties/losses | identical packings |
|---|---|---|---|---|---|---|
| simplified vs original | 40.285 | 40.285 | 0 | [0, 0] | 0/800/0 | 99.875% |
| simplified vs best-fit | 40.285 | 40.285 | 0 | [0, 0] | 0/800/0 | 100% |
| original vs best-fit | 40.285 | 40.285 | 0 | [0, 0] | 0/800/0 | 99.875% |

The winner and best-fit have zero excess bins in every family, including the three shifted ones. The 11-term vector differs from best-fit in only one of 800 packings, and that difference doesn't change the bin count.

**Ablation of the original 11-term winner** (confirmation suite):

| removed term | weight | Δ mean bins | 95% CI | instances changed | identical packings |
|---|---|---|---|---|---|
| gap/100 | −1 | +0.0037 | [0, +0.0088] | 3 | 92.7% |
| (gap/100)² | −0.031 | 0 | [0, 0] | 0 | 100% |
| 1/(gap+1) | +0.160 | 0 | [0, 0] | 0 | 100% |
| 0<gap<10 | +0.008 | 0 | [0, 0] | 0 | 100% |
| 0<gap<item | +0.061 | 0 | [0, 0] | 0 | 94.9% |
| gap≥item | +0.040 | 0 | [0, 0] | 0 | 100% |
| \|x−.25\| | −0.019 | 0 | [0, 0] | 0 | 100% |
| \|x−.5\| | +0.152 | 0 | [0, 0] | 0 | 100% |
| \|x−.75\| | +0.839 | +0.0037 | [0, +0.0088] | 3 | 96.6% |
| 0<gap<33 | +0.181 | 0 | [0, 0] | 0 | 99.8% |
| **0<gap<50** | **−0.631** | **+0.524** | **[+0.458, +0.591]** | **250** | **4.3%** |

How to read this table:
- **Eight of the 11 terms do nothing.** Removing any one of them changes the bin count on 0 of 800 instances.
- **Only `0<gap<50` really matters.** It is not a new idea, though. Under the `0<gap<50` penalty, `|x−.75|` plus `−gap/100` rebuilds best-fit's ordering: the sum decreases as the gap grows. Removing the penalty breaks that ordering and costs about half a bin per instance.

**Ablation of the simplified rule:** removing `gap/100` leaves an all-zero score, which is first-fit. That costs +0.326 bins per instance (CI [+0.293, +0.363]) and changes 254 of 800 instances. So the one remaining term is clearly necessary.

**Witness:** none exists. On the confirmation suite, the simplified rule never uses a different number of bins from best-fit, because it *is* best-fit.

### 4.2 Simplification map over all 43 candidates

- The average term count drops from **6.74 to 1.05**. 41 candidates end with one term and 2 end with two.
- **35 of 43** simplify to a rule that is exactly best-fit (`-gap/100`, `-(gap/100)²` or `+1/(gap+1)`). None simplify to first-fit.
- Surviving terms across the 43 simplified rules: `gap/100` 20, `1/(gap+1)` 15, `|x−.75|` 4, `|x−.5|` 2, `(gap/100)²` 2, `gap≥item` 1, `0<gap<33` 1.
- The 8 rules that are not exactly best-fit:
  - six local-v1 runs become a single "prefer leftover gaps far from c" term, meaning best-fit below gap size c and worst-fit above it. That is c = 75 for `counterexample_replay-2`, `random_replay-6`, `random_replay-11` and `counterexample_tail-11`, and c = 50 for `random_replay-5` and `random_replay-19`;
  - `counterexample_replay-1` becomes "best-fit, but penalise leaving a non-zero gap under 33, worth about 20 units of capacity";
  - `counterexample_replay-0` becomes `1/(gap+1)` plus a small reward for leaving a gap that could hold another copy of the item.
- Codex candidates: all 14 simplify to best-fit.

**Important caveat, found while writing this up: the tolerance only works in one direction.** A step is accepted when the new rule is *no worse* than the original + tol, not when it is *as good*. So a candidate that is worse than best-fit can be "simplified" into a *better* rule. That is a repair, not an explanation of that candidate. Re-checking every row two-sidedly (|simplified − original| ≤ 0.002 bins on the simplification suite):

| | count |
|---|---|
| truly equivalent simplifications | **17 / 43** |
| of which reduce to best-fit | 14 |
| simplification *improved* the candidate by more than tol | **26 / 43** |
| of which reduce to best-fit | 21 |

The improved cases include every badly performing Codex candidate. For example, `reserve_half` goes from 42.037 to 41.245 bins and `reserve_quarter` from 41.889 to 41.245, along with most local-v1 runs that had drifted slightly worse than best-fit (e.g. `random_replay-4`, 41.293 → 41.245).

The deep-dive result in 4.1 is not affected. There the original and simplified rules tie on every confirmation instance, so the simplification is equivalent in both directions.

## 5. Conclusions

1. **The pipeline works.** It automatically cut an 11-term evolved heuristic to the one term that explains its behaviour, backed that with per-term ablations and confidence intervals, and stated the result in one sentence, all within 12k packing executions.
2. **The evolved "winner" is best-fit.** Eight of its 11 terms are measurably irrelevant, and two more affect only 3 of 800 instances. The one load-bearing term interacts with the gap terms so that, together, they reproduce best-fit's choices.
3. **The search found no improvement over best-fit.** All local-v1 runs started at best-fit, and none beat it on fresh data. The earlier local-v1 result (counterexample replay −0.0047 excess bins vs random replay) is therefore about *staying close to best-fit*, not about discovering better rules.
4. **Most evolved vectors are best-fit with noise or slightly worse.** 14 are exactly equivalent to best-fit after simplification. 21 more were slightly or clearly worse than best-fit and get pulled back to it by simplification.
5. **This feature set may not be able to express anything better than best-fit on these families.** A real "discover → simplify → explain" demo needs a setting where the discovered rule actually beats the baseline.

## 6. Limitations

- **One-sided tolerance** (Section 4.2). For explaining a heuristic, simplification should require two-sided equivalence (|Δ| ≤ tol); the one-sided form answers "what simplest rule is at least as good?" The fix is a one-line change in `simplify`, and the map needs re-running afterwards.
- "Equivalent" means equivalent on finite suites (500–1000 instances of 80 items), not a proof. The bootstrap CIs resample instances and treat the suite as fixed.
- The winner tie-break deliberately favours complexity, so the deep-dive candidate is the hardest simplification case, not necessarily the most interesting heuristic.
- The simplification moves are greedy and limited to deletion and rounding. They never add new terms or combine features, so a shorter equivalent rule using different features would be missed.
- The map's non-best-fit rules (e.g. "far from 75") were checked only on the simplification suite, not the confirmation suite.
- The explanation text comes from templates: it is faithful to the formula but mechanical.
- Single-threaded CPU, deterministic seeds. The whole run (selection, deep dive, map) takes about 23 seconds.

## 7. Tests

When this was written on the `simplify-explain` branch, `python3 -m unittest discover tests` ran 8 tests, all passing:

| test | checks |
|---|---|
| `test_vestigial_terms_collapse_to_best_fit` | best-fit plus near-zero noise terms simplifies to exactly best-fit (1 term) |
| `test_normalize_preserves_packing` | scale normalization leaves bins and assignments unchanged |
| `test_gap_term_is_load_bearing_for_best_fit` | removing best-fit's only term changes packings |
| `test_budget_is_respected` | simplification never exceeds its packing-execution cap |
| `test_explanations` | rule text for best-fit, first-fit and a gap-penalty rule |
| 3 existing tests in `tests/test_core.py` | packer matches an independent best-fit implementation, mutated heuristics give valid packings, invalid input is rejected |

While building this, a test caught a tie-breaking bug. Elimination dropped the dominant `gap/100` term and kept a near-zero `|x−.75|` term that happens to give the same bin count. It is fixed: ties now drop the smaller term.

## 8. Reproduce

```bash
python3 -m unittest discover tests
python3 -m falsify.simplify                 # writes experiments/simplify-v1/report.{json,md}
python3 -m falsify.simplify --weights -1 0 0 0 0 0 0 0 0 0 -0.14 0 --out experiments/simplify-manual   # one vector
```

This uses `falsify/core.py`, `falsify/packing.cpp` and `experiments/local-v1/audit.json` from the discovery work, all included in this repository.

## 9. Next steps

1. Make the tolerance two-sided for the explanation mode, and re-run the map.
2. Run discovery on families designed to defeat best-fit, or give the features more information (e.g. the gaps of other open bins, or recent item sizes), so there is a real winner to simplify.
3. Add a "replace" move to simplification (swap a term for a simpler correlated one) and confirm the map's non-best-fit rules on the confirmation suite.
