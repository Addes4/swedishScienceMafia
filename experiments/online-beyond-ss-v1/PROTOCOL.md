# online-beyond-ss-v1: protocol for the confirmatory run

Written on 4 October 2026 before `run.py` was run on any test set. Its SHA-256 and the time are
recorded in `RUN_LOG.md` before the first confirmatory command. Nothing can be committed without the
user's approval, so the hash stands in for a commit timestamp.

## Question

Can a simple online policy that keeps state get much closer to the offline optimum than FunSearch's
evolved heuristic and the other published LLM-designed heuristics, on their own benchmarks?

## The policy (frozen in `config.json`)

**FWSS, fill-weighted Sum-of-Squares with a best-fit finish.** N(g) is the number of open bins with
remaining capacity g, 0 < g < C.

1. **Main phase.** Item s goes to the open bin with gap g ≥ s, or to a new bin, that minimises the
   increase of Σ_g w(g)·N(g)².
   - The weight is w(g) = F(g)^(-β), with β = 1.5.
   - F(g) = (1 + #{seen items ≤ g}) / (1 + #seen) is the empirical CDF of the item sizes seen so far,
     the current item included.
   - So bins whose gap few items can fill are expensive to keep.
   - Ties go to the smaller remaining gap.
2. **Finish.** Once (items left, the current one included) × (mean size seen so far) ≤ c × (total open
   gap), with c = 1.5, the policy uses best fit for the rest of the sequence.
3. **Information used:**
   - its own past placements;
   - the sizes of past items;
   - the item count T. In FunSearch's evaluator this is `len(bins)` on an instance's first call,
     because every bin starts unused.

   It uses no future items, no distribution given in advance and no capacity-specific constant.

   Because the finish uses T, FWSS is a **known-horizon** policy, in the same class as PD-exp-T
   (Gupta–Radovanović) and Banerjee–Freund. SS and FunSearch's heuristics do not use T. That is
   why every table reports FWSS-no-finish next to it: the same weights with no switch, which is
   horizon-free.
   `priority_fss.py` is the same policy as a stateful FunSearch `priority(item, bins)`, and
   `check_priority.py` shows it gives identical bin counts.

**How the parameters were chosen.**
- Tuning used training-style draws only: `verify.items_for` seeds 90000–90199, the EoH generator with
  seeds 777000+ at C = 100 and 500, and uniform {20..100} sizes at C = 150 with seeds 888000+.
- See `RUN_LOG.md` and `tuning_grid.py`/`tuning_grid.json`.
- The rule was: the lowest geometric-mean ratio to the best of SS, FS-W, FS-OR and best fit across
  the 9 training-style sets. (β = 1.5, α = 0, c = 1.5 beat the best of those on 9 of 9.)

**Disclosure.** Before freezing, three earlier configurations were scored on FunSearch's 5 released
Weibull 5k instances (see RUN_LOG.md): SS, weighted SS with weight g^-1, and the latter with a best
fit over the last 40 items. FWSS itself has not been scored there. The released set is therefore
reported, but flagged as seen.

## Test sets (none used for any choice)

| Set | Source | Instances | Items | C |
|---|---|---|---|---|
| fs_released_w5k | FunSearch's released Weibull 5k test data (`experiments/bp-ceiling-v1/funsearch_weibull5k_test.json.gz`) | 5 | 5,000 | 100 |
| fresh_w1k / w5k / w10k / w100k | `verify.items_for`, seeds 98000–98199 / 98200–98399 / 98400–98449 / 98450–98459 | 200 / 200 / 50 / 10 | 1k / 5k / 10k / 100k | 100 |
| eoh_{1k,2k,5k,10k,100k}_c{100,500} | EoH's test pickles (github.com/FeiLiu36/EoH, examples/bp_online/testingdata, commit 5d3319e), loaded without code execution; each item list is run at both capacities, as EoH's runEval does | 5, 5, 5, 5, 1 | 1k–100k | 100 and 500 |
| or1–or4 | OR-Library binpack1–4 (Falkenauer u120–u1000; FunSearch's OR1–OR4) | 20 each | 120–1,000 | 150 |

## Policies compared

- **Ours:** FWSS.
- **Ablations:**
  - FWSS-no-finish (c = 0);
  - SS+finish (β = 0, the same switch).
- **Classic:**
  - SS (Csirik et al. 2006);
  - best fit.
- **LLM-designed heuristics, verbatim:**
  - FunSearch's Weibull and OR heuristics (FS-W, FS-OR), run in FunSearch's evaluator through
    online-frontier-v1's compact evaluator (`frontier_snapshot.py`, SHA-256 3b74ed18…);
  - EoH's heuristic from its repository ("EoH (this code)") and the EoH paper's heuristic, both in the
    published full evaluator, for n ≤ 10,000 only, because that evaluator is O(n²).
- **Hand-tuned:** Herrmann & Pallez's ab-WorstFit (a = 1, b = 21).

## Endpoints

- **Primary.** Mean bins above L1 = ⌈Σ sizes / C⌉ per instance, and % excess over L1 (FunSearch's and
  EoH's metric, Σ bins / Σ L1 − 1).
- **Primary contrasts:** FWSS − FS-W on the Weibull sets, FWSS − FS-OR on OR1–OR4, and FWSS − SS
  everywhere.
  - Each is reported as the mean difference in bins per instance, with a 95% paired bootstrap interval
    (10,000 resamples, seed 20261004) and wins/ties/losses.
  - A two-sided sign test is run on fresh_w1k, fresh_w5k, fresh_w10k and OR1–OR4, the sets with ≥ 20
    instances.
- **OPT.**
  - The exact optimum by arc flow (HiGHS, 300 s per instance), where it is proved.
  - On OR1–OR4 it must equal OR-Library's listed optimum.
  - Report bins above OPT.
- **Secondary:**
  - the ablations;
  - EoH's heuristics on EoH's own data;
  - which published number each set corresponds to: FunSearch Table 1, the EoH README table, and
    other papers per the literature check.

## Expectations stated in advance (from tuning)

1. FWSS beats FS-W and SS on every Weibull set at C = 100. Tuning gave about 2 bins above L1 at 5k,
   against about 10.6 for SS and 13–14 for FS-W.
2. FWSS beats FS-OR on OR2–OR4. OR1 (120 items) is uncertain: in tuning it beat FS-OR at 120 items
   (4.79% vs 5.47%), but that margin is small.
3. At C = 500, FWSS beats SS and best fit. The margins are small in bins.

## What will not be claimed

- Nothing about FunSearch's or EoH's search procedures. Their interfaces were stateless, and FWSS keeps
  state.
- No claim beyond these distributions and capacities.
- Whether FWSS counts as "new" depends on the literature check in `RESULTS.md`. Weighted SS objectives
  are a known family: Csirik et al. 2006, §8.1, Theorem 8.1.

## Cost

CPU only, no API calls, at most 2 processes on the shared machine.

## Amendment 1, written before any of these sets was run: the MoH/HMACE leaderboard settings

**Why.** The literature check (`literature.md`) found that the largest same-protocol leaderboard for
LLM-designed online bin-packing heuristics is in MoH (Shi et al., ICLR 2026, arXiv 2505.20881,
Table 2), reused and extended by HMACE (arXiv 2605.07214, Table 2).
- It has 11 methods: FunSearch, EoH, ReEvo, HSEvo, MCTS-AHD, MoH, EoH*, CORAL* and HMACE*, plus best
  fit and first fit.
- It covers 15 settings: capacity 100, 200, 300, 400 and 500 × 1k, 5k and 10k items.
- Each setting has 100 Weibull instances, measured as excess over L1.

Their instances are not released; the MoH repository holds TSP code only.

**Sets.** For each of the 15 settings, 100 instances from EoH's generator:
- sizes = round(clip(45 · Weibull(shape 3), 1, 100)), with sizes not scaled with capacity, as in EoH
  and in MoH's best-fit numbers;
- `numpy.random.default_rng(600000 + 1000·i + k)` for setting i = 0..14 and instance k = 0..99.

These seeds were never used. Capacities 200–400 were never seen in tuning.

**Policies.** FWSS, FWSS-no-finish, SS+finish, SS, best fit, FS-W and FS-OR, as in the main protocol.
EoH's heuristics are left out because the full evaluator is O(n²).

**Comparison.**
- Best fit is the calibration row: our best fit should match MoH's within sampling error. If it differs
  from theirs by more than 0.1 percentage points in some setting, the generator is judged different
  there, and that setting is reported but not counted.
- Primary: in how many of the 15 settings FWSS's excess is below the best published number among the
  11 methods (MoH Table 2 plus HMACE Table 2).
- These are different draws from the same distribution, so this is a distribution-level comparison,
  not a same-instance one. The 100-instance mean has a standard error, which is reported.
- Expectation from tuning: FWSS beats all of them at capacity 100 and 500. Capacities 200–400 are
  untested.
