# Learning when to change research strategy: experiment and results

## Summary

We built a controller that decides, during a search, when to make small edits, rewrites, crossovers,
or restarts, based on progress and cost. We tested it against fixed strategies on four benchmarks, with
200 seeds each, at equal cost, under a protocol written before the main run.

- **It reliably beats fixed move mixes** (static mix, uniform random, small edits only) on LABS and NK.
  On Heilbronn it beats uniform and edits-only and ties the static mix.
- **Its switch timing provably matters only on Heilbronn.** There, the same moves replayed at random
  times lose 70 to 130. The effect is weak on NK and absent on LABS.
- **A simple hand-tuned rule beats it on LABS and NK.** "Restart after 64 stalled moves" is clearly
  better there; the controller wins only on Heilbronn. The untuned rule "restart after 256 stalled moves"
  is about as robust across benchmarks as the controller.
- **Many of its switches are premature.** In counterfactual forks, staying put gave a larger mean gain
  than following the controller on every benchmark over a short horizon.
- **Development seeds overstated performance.** The pre-registered confirmatory run caught this.

Verdict: a well-instrumented research system with real but partial success. The method for telling
adaptation from luck worked, and it is what exposed both the controller's weaknesses and our own
overfitting.

## The question

An autoresearch loop has a few kinds of moves:

| move | what it does | LLM analogue | cost (units) |
|---|---|---|---|
| small edit | local change to the current solution | a diff | 1.2 |
| rewrite | re-randomise a large part of the solution | regenerate the program | 2.0 |
| crossover | combine with the best of another line of work | merge two programs | 1.5 |
| restart | start a new line from scratch | write from the problem statement | 2.0 |

Each cost is one evaluation plus a generation charge that grows with the size of the move.

Most systems choose moves with fixed probabilities. We asked two things:

1. Does learning *when* to switch beat fixed strategies at equal cost?
2. If it does, is the gain caused by the timing of the switches, rather than by the mix of moves or by
   luck?

## The controller

The search keeps a **leader line** (the line holding the best solution) and makes **excursions**
(restarts from scratch). The controller sees two progress signals: how long the current line has
stalled (six log-spaced buckets), and whether it is on the leader or an excursion.

1. **Leave the leader** when the expected yield of staying falls below the progress per cost that past
   excursions delivered. Expected yield is P(improve) × typical gain ÷ cost of the best move in the
   current context. This is the marginal value theorem from foraging theory: leave a patch when its
   marginal rate drops below the habitat's average rate.
2. **Abandon an excursion** once it has stalled as long as the leader had when it was left, then resume
   the leader.
3. **Within a line**, choose edit, rewrite or crossover by Thompson sampling on the same yield, per
   context.
4. **Failed excursions lower the exploration estimate**, so the leader is given more patience. In one
   narrated run, the stall at which it left grew from 16 to 21, 32, 111 and 368. The estimate is
   forgotten exponentially in cost, so the controller retries later.

## Experimental design

**Benchmarks**

| benchmark | task | reported as |
|---|---|---|
| LABS, n = 40 | binary sequence with low autocorrelation | merit factor, higher is better |
| Heilbronn, n = 12 | place 12 points in the unit square | smallest triangle area, higher is better |
| NK landscape, N = 48, K = 6 | rugged synthetic landscape, new instance per seed | fitness, higher is better |
| bin packing | the team's `falsify/` heuristic space, 12 weights | excess bins over best-fit, lower is better |

**Budget.** 3,000 cost units per run. Rejected candidates are charged in full.

**Pairing.** For a given seed, every arm gets the same problem instance and the same starting solution.

**Arms**

| arm | description |
|---|---|
| `adaptive` | the controller above |
| `timing_shuffled` | the exact multiset of moves the paired adaptive run made, replayed in random order: same moves, same cost, different timing |
| `static_mix` | edit 0.6, rewrite 0.3, crossover 0.1 |
| `uniform` | all four moves equally often |
| `edits_only` | hill climbing |
| `patience_T`, T ∈ {16, 64, 256} | edit until the line stalls for T moves, then restart |
| `adaptive_blind` | ablation: the controller without the stall signal |
| `adaptive_no_crossover` | ablation: the controller without crossover |

**Controls for luck**

1. *Timing-shuffled replay* (above). If adaptive beats it, the gain comes from *when* it switched.
2. *Counterfactual forks.* On seeds 2000-2039, the full search state is copied every time the controller
   leaves the leader. From each copy, 20 forks follow the controller and 20 stay with small edits, each
   with an independent random stream, for 300 cost units.
3. *Pre-registration.* `PROTOCOL.md` was written before the confirmatory run and discloses every design
   change made on development seeds 0-19. Confirmatory seeds 1000-1199 were run once.
4. *A favoured baseline.* `patience_best` is the patience value with the best mean *on the confirmatory
   seeds themselves*, chosen after the fact.

**Statistics.** Per-seed paired differences, a 95% bootstrap interval (10,000 resamples), and an exact
sign test, with Holm correction over the five primary comparisons per benchmark.

## Results

### Mean final score, 200 seeds per arm

| arm | LABS ↑ | Heilbronn ↑ | NK ↑ | bin packing ↓ |
|---|---|---|---|---|
| **adaptive** | **3.959** | **0.01050** | **0.7336** | **−0.0408** |
| timing_shuffled | 3.963 | 0.00924 | 0.7304 | −0.0410 |
| static_mix | 3.533 | 0.01085 | 0.7184 | −0.0440 |
| uniform | 3.034 | 0.00430 | 0.6511 | −0.0333 |
| edits_only | 3.491 | 0.00989 | 0.7123 | −0.0410 |
| patience_16 | 4.170 | 0.00504 | 0.7242 | −0.0371 |
| patience_64 | **4.446** | 0.00814 | **0.7446** | −0.0402 |
| patience_256 | 4.239 | 0.00975 | 0.7417 | −0.0406 |
| adaptive_blind | 4.103 | 0.00982 | 0.7381 | −0.0400 |
| adaptive_no_crossover | 4.162 | 0.01027 | 0.7406 | −0.0429 |

### The pre-registered comparisons

Adaptive versus each arm. **Better** or **worse** means Holm-adjusted p < 0.05; ~ means no clear
difference. Brackets give seed wins/ties/losses for adaptive.

| adaptive versus | LABS | Heilbronn | NK | bin packing |
|---|---|---|---|---|
| H1: shuffled timing | ~ (98/11/91) | **better** (130/0/70, p = 1e-4) | **better**, weak (116/0/84, p = 0.028; the mean's interval crosses 0) | ~ (12/175/13) |
| H2: static mix | **better** (150/4/46) | ~ (93/0/107) | **better** (139/1/60) | ~ (11/164/25) |
| H2: uniform | **better** (193/2/5) | **better** (200/0/0) | **better** (200/0/0) | **better** (38/159/3) |
| H2: edits only | **better** (152/10/38) | **better** (120/0/80) | **better** (158/0/42) | ~ (17/165/18) |
| H3: best patience rule | **worse** (36/12/152, T = 64) | **better** (123/0/77, T = 256) | **worse** (65/0/135, T = 64) | ~ (18/166/16) |

### Counterfactual forks

About 237 switch points per benchmark, each with 20 + 20 forks run for 300 cost units:

| benchmark | P(new best): follow / stay | difference, 95% CI | mean gain: follow / stay | difference, 95% CI |
|---|---|---|---|---|
| LABS | 54.4% / 50.4% | +0.3 to +7.9 points | 0.416 / 0.457 | −0.072 to −0.010 |
| Heilbronn | 82.1% / 99.8% | −21.3 to −14.2 points | 0.00100 / 0.00217 | −0.00128 to −0.00106 |
| NK | 62.4% / 66.9% | −7.5 to −1.6 points | 0.0366 / 0.0465 | −0.0116 to −0.0083 |

Over this 300-unit window, switching gave a *lower mean gain on all three benchmarks*. On LABS it found
some improvement slightly more often, but smaller ones. The intervals resample switch moments, and up to
six moments come from the same seed, so they are narrower than truly independent intervals would be.

### Robustness across benchmarks

| arm | LABS | Heilbronn | NK | worst case |
|---|---|---|---|---|
| adaptive | −10.9% | −3.2% | −1.5% | 10.9% |
| patience_256 | −4.6% | −10.1% | −0.4% | 10.1% |
| patience_64 | 0% | −25.0% | 0% | 25.0% |
| static_mix | −20.5% | 0% | −3.5% | 20.5% |

Each cell is the gap to the best arm on that benchmark, excluding ablations.

## What the results mean

- **Adapting is much better than a fixed mix of moves.** Without tuning, the controller discovers that
  restarts pay on rugged problems and that the leader should be refined when it keeps improving.
- **"When" matters on Heilbronn, but not on LABS.** On LABS the controller's advantage over fixed mixes
  comes entirely from *which* moves it ends up using. Shuffling their order costs nothing. On Heilbronn
  the timing is worth more than the whole gap to edits-only (0.00126 vs 0.00061 in mean area).
- **The controller leaves too early.** Forks show that at many of its switch points the leader was still
  productive, especially on Heilbronn (99.8% of stay-forks improved). Over a short horizon, switching
  lowered the mean gain everywhere. A positive full-run timing result (Heilbronn) can coexist with this,
  because the forks answer a shorter-horizon question. Long excursions late in a run,
  caused by "equal patience" after a very patient leader, also waste budget.
- **Exploring a weak move costs real budget.** The controller spends about 30% of moves on crossover.
  Removing crossover improves LABS by +0.20 merit factor and NK by +0.007 fitness. Removing the stall
  signal also helps on LABS and NK, but hurts on Heilbronn.
- **Bin packing is at a ceiling.** Best-fit is very hard to beat in this 12-weight space (matching the
  team's `falsify/` findings), so 79-88% of seed comparisons tie. The negative excess-bin numbers are
  scores on the seed-specific 24-case *training* suite used for selection. There is no fresh audit here,
  so they do not show a better-than-best-fit algorithm and do not contradict `falsify/`'s held-out
  results.

## Threats to validity

- **Proxy moves and costs.** The moves are stochastic local operators standing in for LLM edit types,
  and costs come from a proxy table. No LLM was called.
- **Winner's curse during development.** Seeds 0-19 gave a mean merit factor of 4.29 on LABS. Never-used
  seeds 20-39 give 3.92, and the confirmatory mean is 3.96. Choosing among about 15 variants on 20 seeds
  inflated the dev estimate. The code was verified to reproduce both numbers exactly, so this is not a
  code change. Re-running 90 logged confirmatory runs with the final code gave identical results.
- **Narrow scope.** One budget and one problem size per benchmark. Holm correction covers the five
  primary comparisons per benchmark, not the ablations or forks.
- **Short fork window.** The forks measure a 300-unit window. A switch can pay off later than that, so
  they understate the value of restarts on problems like LABS. Their intervals also treat switch moments
  from the same seed as independent.
- **Bin packing has no fresh audit.** Its scores come from the training suite (see above).

## Next steps

To be run as a new named experiment on new seeds:

1. Make crossover earn its place: start without it, or require evidence before using it.
2. Cap the length of an excursion, rather than inheriting the leader's patience.
3. Require stronger evidence before leaving a leader that is still improving.
4. Replace the proxy moves with LLM-generated diffs, rewrites and merges, charged by measured tokens.

## Reproduce

```sh
python3 -m unittest discover -s tests
python3 -m strategist.experiment --seeds 1000:1200 --out experiments/strategist-v1    # about 13 min, 6 workers
python3 -m strategist.forks --seeds 2000:2040 --out experiments/strategist-v1
python3 -m strategist.demo --benchmark labs --seed 1000 --trace experiments/strategist-v1/demo.json
python3 -m strategist.report --dir experiments/strategist-v1                         # writes report.html
```

Raw data: `experiments/strategist-v1/runs.jsonl` (every run), `summary.json` and `forks.json`.
