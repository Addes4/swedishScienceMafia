# Strategist protocol (written before the confirmatory run)

## Question

Does a controller that *learns when to change research strategy* (small edit, rewrite, crossover,
restart) find better solutions at equal cost than fixed strategies? And is any gain caused by the
*timing* of its switches, rather than by the mix of moves it happens to use, or by luck?

## Fixed design

- Benchmarks (all minimised internally, reported in natural units):
  - `labs`: low-autocorrelation binary sequences, n = 40, reported as merit factor (higher is better).
  - `heilbronn`: 12 points in the unit square, smallest triangle area (higher is better).
  - `nk`: NK landscape, N = 48, K = 6, a new random instance per seed (higher is better).
  - `binpacking`: the team's `falsify/` heuristic space (12 bin-scoring weights), mean excess bins over
    best-fit on a seed-specific 24-instance training suite (lower is better).
- Budget: 3,000 cost units per run. Costs: edit 1.2, crossover 1.5, rewrite 2.0, restart 2.0, resume 0.
  Each candidate costs one evaluation plus a generation charge that grows with the move (an LLM proxy).
  The initial solution is charged as a restart. Rejected candidates are charged in full.
- Pairing: for a given seed, every arm sees the same instance and the same initial solution.
- Arms:
  - `adaptive`: the controller in `strategist/controller.py`, hyperparameters frozen below.
  - `timing_shuffled`: replays the *exact multiset* of moves the paired `adaptive` run made, in a random
    order. Same moves, same total cost, random timing. This is the main control for adaptation vs. luck.
  - `adaptive_blind`: the controller without the stall context (it still knows leader vs. excursion).
  - `adaptive_no_crossover`: the controller restricted to edit/rewrite within lines.
  - `edits_only`; `uniform` (four moves uniformly); `static_mix` (edit 0.6, rewrite 0.3, crossover 0.1).
  - `patience_T` for T in {16, 64, 256}: edit until the line stalls T moves, then restart.
- Frozen controller hyperparameters: discount 0.99, prior strength 4, excursion memory 500 cost units,
  prior pseudo-cost 100. Stall buckets 0 / 1-3 / 4-15 / 16-63 / 64-255 / 256+.

## Development phase (already done; disclosed)

Seeds 0-19 (budget 3,000) on `labs`, `heilbronn`, `nk`, and seeds 0-5 on `binpacking`, were used to
design the controller. Changes made after looking at dev results, in order:

1. A flat contextual bandit over all four moves, credited in overall progress with delayed credit for
   restarts, restarted far too often. Replaced by a two-level design.
2. Crediting moves by the working line's own progress let excursions' easy gains leak into the leader's
   contexts. Fixed by pooling prior statistics only within leader or excursion contexts, and measuring
   gains as log-ratios.
3. The leave decision became a marginal-value test (leave the leader when its expected yield falls
   below the overall yield of past excursions). Trailing lines were first never abandoned, then judged by
   leader yields (restart cascades), then abandoned by their climbing rate (excursions too short).
   Final rule: an excursion is abandoned when it has stalled as long as the leader had when it was left,
   and the search resumes the leader line.
4. Excursion statistics are forgotten exponentially in cost (memory 500) so early failures cannot lock
   out exploration for the rest of the run.
5. Crossover on an excursion never borrows from the leader line, so excursions stay independent.
6. Tried and rejected: a UCB rule instead of Thompson sampling; prior strength 1 and 16; discount 0.995,
   0.998 and 0.9995; memory 200 and 1,500; prior pseudo-cost 300.

The dev-phase numbers are not reported as evidence.

## Confirmatory run

Seeds 1000-1199 (200 per benchmark), run once with the frozen design:

    python3 -m strategist.experiment --seeds 1000:1200 --out experiments/strategist-v1

Primary outcome: best score at the end of the budget. Per benchmark, five primary paired comparisons,
`adaptive` minus each of `timing_shuffled`, `static_mix`, `uniform`, `edits_only` and `patience_best`.
`patience_best` is the patience value with the best mean *on the confirmatory seeds themselves*, chosen
after the fact. This deliberately favours the baseline.

- H1 (timing matters): adaptive beats timing_shuffled.
- H2 (adaptation beats fixed mixes): adaptive beats static_mix, uniform and edits_only.
- H3 (no tuning needed): adaptive is not worse than patience_best. This is two-sided; we report the
  difference whichever way it goes.

Statistics: per-seed paired differences oriented so that positive favours `adaptive`; mean, 95%
bootstrap interval (10,000 resamples), win/tie/loss counts, exact two-sided sign test, Holm correction
over the five primary comparisons within each benchmark. All arms and benchmarks are reported,
including losses and ties.

Secondary (not part of the confirmatory claim): anytime performance (mean best-so-far over 30 cost
checkpoints); the two ablations; per-context move usage; counterfactual forks (below); a re-run with
uniform move costs as a robustness check.

## Counterfactual forks at switch points

Seeds 2000-2039 on `labs`, `heilbronn` and `nk`. Each time `adaptive` leaves the leader line (a
restart), the full search state just before that decision is copied. From the copy we run 20 forks that
continue with the controller, and 20 that stay on the line with small edits only, for 300 cost units each.
Every fork gets an independent random stream. Outcome: the probability of a new overall best within the
window, and the mean improvement. This tests whether the moves that followed a switch caused the
progress, rather than the run being lucky.

Any design change after viewing confirmatory results requires a new named experiment and new seeds.
