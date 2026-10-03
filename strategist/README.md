# Strategist: learning when to change research strategy

An autoresearch loop has a handful of moves: tweak the current solution (**small edit**), rewrite a
large part of it (**rewrite**), combine it with another line of work (**crossover**), or start over
(**restart**). Most systems pick these with fixed probabilities. Strategist learns, during the run,
*when* each move pays for its cost, from two progress signals: how long the current line has stalled,
and whether that line holds the best solution.

The question that matters is whether the adaptation is real or lucky. So every result here comes with
two controls designed for that question: a timing-shuffled replay, and counterfactual forks at switch
points.

Standard library only (Python 3.10+). The bin-packing benchmark reuses the team's `falsify/` evaluator,
which needs a C++17 compiler on first use.

## How it decides

The search keeps a **leader line** (the line holding the best solution) and makes **excursions**
(restarts from scratch).

1. **Leave the leader** when the expected yield of staying on it falls below the progress per cost
   that past excursions delivered. Expected yield is P(improve) × typical gain ÷ cost for its best
   move, in the current stall context. This is the marginal value theorem from foraging theory: leave a
   patch when its marginal rate drops below the habitat's average rate.
2. **Abandon an excursion** once it has stalled as long as the leader had when it was left (equally
   exhausted), and resume the leader. The leader then faces test 1 again.
3. **Within a line**, choose edit, rewrite or crossover by Thompson sampling on the same yield,
   separately per context. Contexts are 6 log-spaced stall buckets × leader/excursion. Each context is
   shrunk towards the move's pooled statistics.
4. **Cost is part of the yield.** Moves are charged one evaluation plus a generation charge that grows
   with the move (edit 1.2, crossover 1.5, rewrite 2, restart 2), standing in for LLM diff, crossover,
   and full-rewrite prompts. A restart is judged by the progress per cost of *whole excursions*.
5. **Failed excursions lower the exploration estimate**, so the leader is given more patience, and
   the threshold grows on its own (in one run: stall 16, then 21, 32, 111, 368). The estimate is
   forgotten exponentially in cost, so early failures cannot lock out exploration.

Everything the controller believes is inspectable: `Adaptive.explain(state, run)` returns P(improve),
gain, cost and yield per move, plus the stay and explore rates behind each switch.

## Telling adaptation from luck

- **Timing-shuffled control.** For every seed, the adaptive run's exact multiset of moves is replayed
  in random order: same moves, same total cost, only the timing differs. If adaptive beats it, the gain
  comes from *when* it switched, not from which moves it used.
- **Counterfactual forks.** At each moment the controller leaves the leader, the full search state is
  copied. Forks either follow the controller or stay with small edits, each with an independent random
  stream. This asks whether the progress after a switch was caused by the switch.
- **Pre-registration.** `PROTOCOL.md` was written before the confirmatory run and discloses every
  design change made on development seeds 0-19. Confirmatory seeds 1000-1199 were run once.
- **Strong baselines.** The patience rule's threshold is tuned *after the fact on the confirmatory
  seeds*, which favours the baseline.

## Results

Full write-up: [`RESULTS.md`](RESULTS.md). Confirmatory run: 200 seeds per benchmark, budget 3,000 cost units, run once after freezing the design.
The full report is `experiments/strategist-v1/report.html` (open it in a browser); the numbers are in
`summary.json` and `forks.json` in the same folder.

Adaptive versus each arm. ▲ means adaptive is better and ▼ means worse, at Holm-adjusted p < 0.05;
"~" means no clear difference. Seed wins/ties/losses in brackets:

| adaptive versus | LABS (merit factor) | Heilbronn (min area) | NK (fitness) | bin packing |
|---|---|---|---|---|
| same moves, shuffled timing (H1) | ~ (98/11/91) | ▲ (130/0/70) | ▲ weak (116/0/84; mean CI crosses 0) | ~ (12/175/13) |
| static mix 0.6/0.3/0.1 (H2) | ▲ (150/4/46) | ~ (93/0/107) | ▲ (139/1/60) | ~ (11/164/25) |
| uniform random moves (H2) | ▲ (193/2/5) | ▲ (200/0/0) | ▲ (200/0/0) | ▲ (38/159/3) |
| small edits only (H2) | ▲ (152/10/38) | ▲ (120/0/80) | ▲ (158/0/42) | ~ (17/165/18) |
| best patience rule, tuned post hoc (H3) | ▼ (36/12/152; T=64) | ▲ (123/0/77; T=256) | ▼ (65/0/135; T=64) | ~ (18/166/16) |

Read honestly:

- **Adaptation beats fixed move mixes** almost everywhere (H2). Without any tuning it gets most of the
  way from a static mix to a good restart schedule.
- **Timing matters on Heilbronn** (H1): the same moves at random times lose 70-130. The evidence is
  weak on NK, and absent on LABS, where the controller's gains come from its move mix rather than its
  timing.
- **A hand-tuned patience rule wins on LABS and NK** (H3 fails there), but no single patience value
  wins everywhere. T=64 is best on LABS and NK yet loses to adaptive on Heilbronn (mean area 0.0081 vs
  0.0105). T=256 is about as robust as adaptive: its worst gap to the best arm is 10.1%, against 10.9%.
- **Ablations beat the full controller on LABS and NK.** Without crossover: +0.20 merit factor on LABS
  and +0.007 fitness on NK. Without the stall context: +0.14 and +0.005. Exploring a useless move costs
  real budget on those problems; on Heilbronn the full controller is ahead of both.
- **Counterfactual forks** (about 237 switch points per benchmark, 20 + 20 forks each, 300 cost units):
  following the controller found a new best slightly more often than staying on LABS (54% vs 50%), but
  the improvements were smaller. Mean gain was lower with switching on all three benchmarks (LABS
  0.416 vs 0.457; NK 0.037 vs 0.047; Heilbronn 0.0010 vs 0.0022). Many switches are premature,
  especially on Heilbronn, where the leader was still improving. The fork intervals treat moments from
  the same seed as independent, so they are somewhat too narrow.
- **Development seeds overstated LABS performance.** Seeds 0-19 gave 4.29 against 3.92 on never-used
  seeds 20-39 and 3.96 on the confirmatory seeds. Picking among about 15 variants on 20 seeds produced a
  winner's curse, which the pre-registered confirmatory run exposed. Use more dev seeds next time.

The most promising next step, to be tested as a new named experiment on new seeds: drop crossover
unless it has earned its place, cap the length of an excursion, and require stronger evidence before
leaving a leader that is still improving.

## Run it

```sh
python3 -m unittest discover -s tests                     # includes tests/test_strategist.py
python3 -m strategist.demo --benchmark labs --seed 1000   # one run, narrated switch by switch
python3 -m strategist.experiment --seeds 1000:1200 --out experiments/my-run    # about 10 min, 6 workers
python3 -m strategist.forks --seeds 2000:2040 --out experiments/my-run
python3 -m strategist.demo --benchmark labs --seed 1000 --trace experiments/my-run/demo.json
python3 -m strategist.report --dir experiments/my-run
```

Use `--costs uniform` on `strategist.experiment` to charge every move the same.

## Add a problem

Subclass `Problem` in `problems.py`. Scores are minimised; moves must return new objects.

```python
class MyProblem(Problem):
    name, higher_is_better = 'mine', False
    def random(self, rng): ...                 # restart
    def score(self, x): ...                    # lower is better
    def edit(self, x, rng): ...                # small local change
    def rewrite(self, x, rng): ...             # large change that keeps part of x
    def crossover(self, x, y, rng): ...        # combine with another line's best

BENCHMARKS['mine'] = lambda seed: MyProblem()
```

An LLM-backed problem implements the same five methods with prompts (diff, full rewrite, two-parent
merge, write from scratch), and passes measured token costs in place of the cost table.

## Files

| file | contents |
|---|---|
| `controller.py` | `Adaptive` and the baseline policies (`Fixed`, `Patience`, `Replay`/`shuffled`) |
| `search.py` | `Run`: leader line, excursions, archive, cost accounting, forking |
| `problems.py` | LABS, Heilbronn, NK, and the bin-packing adapter for `falsify/` |
| `experiment.py` | seed-paired equal-cost comparison, parallel |
| `forks.py` | counterfactual forks at switch points |
| `stats.py` | paired bootstrap, exact sign test, Holm correction |
| `demo.py`, `report.py` | narrated run; standalone HTML report |
| `PROTOCOL.md` | pre-registration and disclosed development changes |

## Limitations

- The moves here are stochastic local operators standing in for LLM edit types, and costs are a proxy
  model. No LLM was called in these experiments.
- One budget (3,000 cost units) and one problem size per benchmark.
- Bin packing sits at a ceiling: best-fit is very hard to beat in this 12-weight space (see the team's
  `falsify/` results), so nearly every arm ties. Its scores are on the 24-case training suite, with no
  fresh audit, so negative excess bins do not mean an algorithm better than best-fit.
- Evidence per context is capped by the decay (about 100 recent moves), so the controller never becomes
  certain that a stalled line is dead. It leaves only once excursions demonstrably pay more.
- Early in a run the optimistic prior causes a few one-move excursions. Late in a run, a very patient
  leader means a single excursion can take a large share of the remaining budget.
