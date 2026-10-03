# Addendum for the experiment review PDF: "Discover, simplify, explain"

**For the agent maintaining `output/pdf/Swedish_Science_Mafia_Experiment_Review.pdf`:** this file adds missing and corrected details for **page 5, Experiment review / 04, "Discover, simplify, explain"**, plus one sentence on page 9. All numbers come from branch `simplify-explain` (commit `a0340a8`), built in the sibling worktree `../swedishScienceMafia-simplify`. They were re-checked against `experiments/simplify-v1/report.json` there.

## 1. Correction: "Reduced to exactly best-fit: 35" overstates the result

Simplification accepted any change that kept mean bins **at most** 0.002 above the original (a one-sided tolerance). A candidate that was worse than best-fit could therefore be "simplified" into best-fit, which is a repair, not an explanation. Re-checking all 43 candidates two-sidedly (|simplified − original| ≤ 0.002 mean bins on the 1,000-case simplification suite, seed 7000002):

| Measure | Result |
|---|---|
| Distinct candidates | 43 |
| Mean number of terms | 6.74 before → 1.05 after |
| Simplified rule equivalent to original (±0.002 bins) | **17** |
| … of which exactly best-fit | **14** |
| Simplification improved the candidate (by > 0.002 bins) | **26** |
| … of which exactly best-fit | **21** |
| Reduced to first-fit | 0 |

**Suggested replacement for the table row on page 5:** "Reduced to exactly best-fit: 35 (14 behaviourally equivalent; 21 were worse than best-fit and were improved by simplification)".

The largest improvements came from the Codex hypotheses:

| Candidate | Mean bins before | Mean bins after | Terms |
|---|---|---|---|
| reserve_half | 42.037 | 41.245 | 4 → 1 |
| reserve_quarter | 41.889 | 41.245 | 5 → 1 |
| avoid_tiny_gaps | 41.524 | 41.245 | 3 → 1 |
| avoid_subitem_gaps | 41.393 | 41.245 | 3 → 1 |
| random_replay-4 (local-v1) | 41.293 | 41.245 | 9 → 1 |

The deep-dive winner is **not** affected. `counterexample_replay-4` ties its simplified form on all 800 confirmation cases, so that simplification is equivalent in both directions.

**Suggested page-9 wording for claim 2:** "Complexity can hide a rediscovered baseline. The selected 11-term winner is exactly best-fit after reduction. Of 43 candidates, 14 are behaviourally equivalent to best-fit; another 21 were worse than best-fit and simplify toward it."

## 2. Missing: ablation of the original 11-term winner

This is the main "explain" evidence. Each term was removed in turn from `counterexample_replay-4` (normalized weights), evaluated on the 800-case confirmation suite (seed 7000003, all eight families), with a paired bootstrap 95% CI (10,000 resamples, seed 739).

| Removed term | Weight | Δ mean bins | 95% CI | Instances changed | Identical packings |
|---|---|---|---|---|---|
| gap/100 | −1 | +0.0037 | [0, +0.0088] | 3 | 92.7% |
| (gap/100)² | −0.031 | 0 | [0, 0] | 0 | 100% |
| 1/(gap+1) | +0.160 | 0 | [0, 0] | 0 | 100% |
| 0<gap<10 | +0.008 | 0 | [0, 0] | 0 | 100% |
| 0<gap<item | +0.061 | 0 | [0, 0] | 0 | 94.9% |
| gap≥item | +0.040 | 0 | [0, 0] | 0 | 100% |
| \|gap/100 − .25\| | −0.019 | 0 | [0, 0] | 0 | 100% |
| \|gap/100 − .5\| | +0.152 | 0 | [0, 0] | 0 | 100% |
| \|gap/100 − .75\| | +0.839 | +0.0037 | [0, +0.0088] | 3 | 96.6% |
| 0<gap<33 | +0.181 | 0 | [0, 0] | 0 | 99.8% |
| **0<gap<50** | **−0.631** | **+0.524** | **[+0.458, +0.591]** | **250** | **4.3%** |

**Suggested text:**
- Eight of the 11 terms change the bin count on none of the 800 instances when removed (an earlier version of this file said nine; the JSON shows eight).
- `gap/100` and `|gap/100 − .75|` each affect only 3 instances.
- The `0<gap<50` penalty is the only strongly load-bearing term. It works with `|gap/100 − .75|` and `−gap/100` to reproduce best-fit's ordering, so it encodes no new strategy.

## 3. Missing: the 8 simplified rules that are not best-fit

These were evaluated on the simplification suite only, not on the confirmation suite.

| Candidate | Terms | Simplified rule |
|---|---|---|
| counterexample_replay-2 | 11 → 1 | prefer leftover gaps far from 75 (best-fit below 75, worst-fit above) |
| random_replay-6 | 5 → 1 | same, far from 75 |
| random_replay-11 | 8 → 1 | same, far from 75 |
| counterexample_tail-11 | 9 → 1 | same, far from 75 |
| random_replay-5 | 5 → 1 | prefer leftover gaps far from 50 (best-fit below 50, worst-fit above) |
| random_replay-19 | 10 → 1 | same, far from 50 |
| counterexample_replay-1 | 3 → 2 | best-fit, but penalise leaving a non-zero gap under 33 (≈20 capacity units) |
| counterexample_replay-0 | 10 → 2 | 1/(gap+1), plus a small reward (0.02) for leaving a gap that could hold another copy of the item |

## 4. Other small facts the page could use

- Simplifying the winner took 12,000 packing executions (budget 150,000). The full run (selection, deep dive and map over 43 candidates) takes about 23 s on one CPU core.
- Tests: 8 pass (5 new in `tests/test_simplify.py` + 3 existing). One test caught a tie-breaking bug during development (the code kept a near-zero `|gap−.75|` term instead of the dominant `gap/100` term); it was fixed before the reported run.
- No witness instance exists for the winner: on the confirmation suite the simplified rule never uses a different number of bins from best-fit.

## 5. Sources and reproduction

- Full write-up: `../swedishScienceMafia-simplify/experiments/simplify-v1/EXPERIMENT.md`
- Raw results: `../swedishScienceMafia-simplify/experiments/simplify-v1/report.json` (`ablation_original`, `map.rows`)
- To reproduce the two-sided counts in Section 1, run this in the worktree:

```bash
python3 -c "
import json, statistics
from falsify.simplify import bins, is_best_fit, load_candidates, suite
r = json.load(open('experiments/simplify-v1/report.json'))
cases = suite(7000002, 1000)
c = {x['name']: x['weights'] for x in load_candidates(['experiments/local-v1/audit.json',
     'experiments/codex_candidates.json', 'experiments/codex_revision.json'])}
eq = [abs(statistics.mean(bins(x['weights'], cases)) - statistics.mean(bins(c[x['name']], cases))) <= .002
      for x in r['map']['rows']]
bf = [is_best_fit(x['weights']) for x in r['map']['rows']]
print('equivalent', sum(eq), 'of which best-fit', sum(e and b for e, b in zip(eq, bf)))
print('improved', len(eq) - sum(eq), 'of which best-fit', sum((not e) and b for e, b in zip(eq, bf)))
"
```

Expected output: `equivalent 17 of which best-fit 14` and `improved 26 of which best-fit 21`.
