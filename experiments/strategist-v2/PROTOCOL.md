# Strategist v2 protocol

Written in stages. Stage 1 was committed before the development grid ran; stage 2 (the frozen design)
before the validation run; stage 3 before the confirmatory run. Each stage is a separate git commit
on branch `exp/strategist-v2`, so the order can be checked. Nothing in an earlier stage is edited
afterwards; later changes are listed under "Disclosed changes".

## Stage 1: question, design and selection rule (before any dev-grid result)

### Question

Strategist v1 (`strategist/RESULTS.md`) found that its adaptive controller beats fixed move mixes, but
that a patience rule tuned after the fact (T = 64) beats it on LABS and NK, that removing crossover or
the stall context helps on LABS and NK, and that many switches away from the leader are premature
(counterfactual forks). It also found a winner's curse: 20 dev seeds overstated LABS performance.

v1 proposed three fixes. This experiment asks:

1. Do the three fixes, together, make the controller better than v1 at equal cost?
2. Which fix does the work (each fix alone on top of v1, and v2 without each fix)?
3. Does the fixed controller now match or beat a patience rule whose T is tuned on dev seeds (not on the
   confirmatory seeds, as in v1)?
4. Does switch timing still matter (timing-shuffled control), and did premature switching drop
   (counterfactual forks)?
5. Do the conclusions survive a different cost table (uniform costs now; measured LLM costs later)?

### The three changes (`strategist/controller.py`, class `AdaptiveV2`)

`AdaptiveV2` with default options is move-for-move identical to v1's `Adaptive`
(`tests/test_strategist_v2.py`). v1's code paths are unchanged.

- (a) **Crossover must earn its place** (`xo_gate`). Crossover gets a sceptical prior on its success
  rate (wins/(pulls+1), which is 0 before any evidence; v1 gives every move the optimistic
  (wins+0.5)/(pulls+1)). In a context it joins the Thompson draw only when its posterior mean yield is
  at least that of the best other move there. While locked it is probed with probability `xo_probe`
  per within-line move. This is how it earns entry.
- (b) **Cap excursion length** (`excursion`). v1 abandons an excursion after it stalls as long as the
  leader had stalled when it was left. `cap`: the same, but at most `excursion_len` moves. `fixed`:
  always `excursion_len` moves, whatever the leader's patience.
- (c) **Stronger evidence before leaving an improving leader** (`leave_test`). v1 leaves when the best
  posterior-mean stay yield falls below the explore rate (`point`). `improving`: also require that the
  leader has gone `window` moves without improving (a recent-improvement test). `yield`: also require
  the leader's realised yield over its last `window` moves to be below the explore rate. `upper`: the
  upper `quantile` credible bound of the stay yield must be below the explore rate.

### Seed blocks

Not used for any v2 decision: 0-39 (v1 development), 1000-1199 (v1 confirmatory), 2000-2039 (v1 forks).
The code refuses them (`strategist/v2.py`, `check_seeds`).

| block | seeds | use |
|---|---|---|
| development | 40-239 (200 per benchmark) | the design grid and the patience T grid; selection |
| validation | 240-439 (200) | run once on the frozen design, to measure the winner's curse; no changes after |
| confirmatory | 3000-3199 (200) | run once after freezing; primary analysis |
| forks | 4000-4039 (40) | counterfactual forks for v1 and v2 |

A pilot on dev seeds 40-49 (12 configurations, `dev/pilot.py`) was run before this grid was fixed, to
check that each option changes behaviour. It informed the grid below (it showed that a probe rate is
needed for the gate to ever open, and that `upper` with q = 0.9 almost never restarts).

### Benchmarks, budget, costs

LABS n = 40, Heilbronn n = 12, NK N = 48 K = 6, exactly as in v1. Budget 3,000 cost units per run. The
primary cost table is v1's proxy (edit 1.2, crossover 1.5, rewrite 2.0, restart 2.0, resume 0). Every
arm sees the same instance and the same initial solution for a given seed. Bin packing is left out: it
sits at the best-fit ceiling (79-88% ties in v1) and has no fresh audit in this harness.

### Development grid (dev seeds 40-239, proxy costs)

Factorial over the three changes:

- crossover: `off` (v1), `gate02` (gate, probe 0.02), `gate10` (gate, probe 0.10), `none` (crossover
  removed: v1's ablation, a reference level only)
- excursion: `inherit` (v1), `cap16`, `cap64`, `fixed16`, `fixed64`
- leave test: `point` (v1), `improving16`, `improving64`, `yield64`, `upper90`

That is 99 configurations besides v1 itself (`off/inherit/point` is identical to v1 and not re-run),
plus `adaptive_v1`, `static_mix`, `edits_only` and `patience_T` for T in {8, 16, 32, 64, 128, 256, 512,
1024}. All on the same 200 dev seeds per benchmark.

### Selection rule (fixed before the grid ran)

- For configuration c and benchmark b, D_b(c) = mean over seeds of the paired difference
  (c minus adaptive_v1, oriented so positive is better) divided by the standard deviation of
  adaptive_v1's final scores on b. J(c) = mean of D_b(c) over the three benchmarks.
- **adaptive_v2** = the configuration with the highest J among the 32 that switch all three changes on
  (crossover `gate02` or `gate10`; excursion `cap16`, `cap64`, `fixed16` or `fixed64`; leave test
  `improving16`, `improving64`, `yield64` or `upper90`). Reference levels (`none`, partial
  configurations) are reported but cannot be chosen.
- The ablation arms use v2's chosen level of each change: `only_X` is v1 plus change X alone;
  `without_X` is v2 with change X set back to v1's behaviour.
- **patience_dev**: for each benchmark, the T in the grid with the best mean on dev seeds. This is
  per-benchmark tuning, which favours the baseline over a single cross-benchmark design. We also
  record the single T with the best J (`patience_joint`) for information.
- `python -m strategist.v2 dev` computes this and writes `dev/selection.json`; `freeze` copies it to
  `frozen.json`, which is committed before validation.

### Validation (seeds 240-439, once)

The frozen design and every confirmatory arm are run once on the validation block. We report the dev
and validation J and per-benchmark differences side by side as the estimate of the winner's curse.
No design change is allowed after validation, whatever it shows. Only a bug fix would be allowed, and
it would be disclosed.

### Confirmatory run (seeds 3000-3199, once, proxy costs)

    python -m strategist.v2 confirm --modal

**Primary endpoint:** best score at the end of the 3,000-unit budget, per benchmark.

**Primary comparisons** (per benchmark; Holm correction over these six; paired over 200 seeds;
positive favours adaptive_v2):

| comparison | hypothesis |
|---|---|
| adaptive_v2 vs adaptive_v1 | H1: the fixes help (one-sided interest, two-sided test) |
| adaptive_v2 vs timing_shuffled | H2: timing matters (same multiset of v2's moves in random order) |
| adaptive_v2 vs patience_dev | H3: v2 vs the patience rule tuned on dev seeds (two-sided) |
| adaptive_v2 vs patience_256 | H3: v2 vs the untuned patience rule (two-sided) |
| adaptive_v2 vs static_mix | H4: adaptation beats a fixed mix (0.6 edit, 0.3 rewrite, 0.1 crossover) |
| adaptive_v2 vs edits_only | H4: adaptation beats hill climbing |

**Statistics:** as v1 (`strategist/stats.py`): per-seed paired differences, mean with 95% bootstrap
interval (10,000 resamples), win/tie/loss counts, exact two-sided sign test, Holm correction over the
six primary comparisons within each benchmark. "Better"/"worse" means Holm-adjusted sign-test
p < 0.05; where the bootstrap interval of the mean crosses 0 despite that, we say so.

**Secondary** (no multiplicity correction; reported as exploratory): each change alone vs v1
(`only_X`), v2 vs v2 without each change (`without_X`), v2 with crossover removed instead of gated,
v1 with crossover removed, v1 vs the baselines on new seeds (replication of v1's findings), anytime
performance (mean best-so-far over 30 checkpoints), per-context move usage, the robustness table
(gap to the best non-ablation arm per benchmark), and dev vs validation vs confirmatory estimates.

### Cost sensitivity (secondary)

The cost table is a parameter (`strategist/costs.py`). The frozen v2 controller is re-run on the
confirmatory seeds under uniform costs (every move 1, resume 0). The patience baseline's T is re-tuned
on the dev seeds under the same table first, by the same rule. A placeholder for measured LLM costs is
in `costs/measured_llm.json`; once its relative costs are filled in, one command repeats the whole
sensitivity run:

    python -m strategist.v2 confirm --costs measured --modal

Measured tables are rescaled so an edit costs 1.2, as in the proxy table, so the budget buys about the
same number of edits and only the ratios change.

### Counterfactual forks (secondary, seeds 4000-4039)

As in v1 (`strategist/forks.py`), now for both adaptive_v1 and adaptive_v2 on the same seeds: at each
moment the controller leaves the leader, the full state is copied; 20 forks follow the controller and 20
stay with small edits, each with an independent random stream, for 300 cost units. Up to 6 moments per
seed, evenly spaced among those with at least 300 units left. Outcomes per controller: leaves per run,
P(new best) and mean gain for switch and stay forks, and the **premature share**: the fraction of switch
moments where staying gave a larger mean gain than switching. "Premature switching dropped" means
v2's premature share is lower than v1's with a seed-clustered 95% bootstrap interval excluding 0. All
fork intervals are now also given with seeds as clusters (v1's treated moments as independent).

### Provenance

Each phase writes its config (arguments, cost table, seeds, sha256 of every `strategist/*.py`, Python
version) and gzip-compressed raw records. Jobs run on Modal (app `ssm-strategist-v2`, Linux,
Python 3.12) or locally with at most 2 processes.

## Disclosed changes

(none yet)
