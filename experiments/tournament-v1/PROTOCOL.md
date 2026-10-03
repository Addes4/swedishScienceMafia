# Tournament v1: complete frameworks at equal dollar budgets

**Status: DRAFT.** Written before any confirmatory run. The arm list depends on three
experiments still running (idea-table, memory-ablation, strategist-v2). The final arm configs,
budget per run and the commit they run from will be frozen in the section "Frozen
configuration" before the grid is launched. Any change after that is disclosed below it.

## Question

At the same Anthropic spend, which complete autoresearch loop reaches the best scores, and
how fast? Each arm is a whole framework: its own prompts, models, selection and stopping,
measured by the same meter.

## Arms (draft)

| Arm | What runs | Models |
|---|---|---|
| `shinka` | Stock ShinkaEvolve 0.0.7 through `autoresearch/run.py` (diff, full and cross patches, islands, meta and novelty LLMs, no embeddings). Its own `--max-cost` is set to the cap as well. | one model for every role |
| `triage` | `autoresearch/triage.py` unchanged: Opus proposes 6 ideas per round, a ranker splits them into thirds, Opus / Sonnet / Haiku implement them, promotions. Ranker: `random` now; `jev` or `claude` if the idea-table experiment supports it. | Opus 5.5, Sonnet 5.5, Haiku 4.5 |
| `lean` | `tournament/lean.py`: one call per step proposes and implements one change to the current best program; the best valid program is kept; the prompt lists the last 8 attempts and their outcomes. | Sonnet 5.5, effort high |
| `lean_gate_patience` | `lean` plus (a) the non-regression gate: a candidate may not score below its parent on any public instance in an archive of instances where earlier valid candidates scored below their parents; (b) the strategist `Patience` rule: after T = 5 consecutive non-improving steps, restart from a fresh program written from the problem statement (the best program found is always kept). | Sonnet 5.5, effort high |

Open choices to settle at freeze time:

- `shinka` model. ShinkaEvolve's launcher defaults to Opus 5.5. The draft uses Sonnet 5.5 so
  that `shinka`, `lean` and `lean_gate_patience` differ in loop design, not model. Triage
  keeps its tiered models because model routing is what it is.
- Triage ranker (idea-table result), lean history length (memory-ablation result), restart
  rule and T (strategist-v2 result; T = 5 was set by hand for runs of 15-40 calls, not tuned).
- Every arm uses max_tokens 32,000 per call.

## Problems

- `problems/erdos_squares`: 9 public instances (n = 5-8, 11-15), 4 hidden (n = 18, 21, 23, 27).
- `problems/circle_packing`: n = 26, one public instance, no hidden instances. The starting
  program places some circles at random, so its score varies from run to run (0.34-0.38 in
  the mock grid); programs that use randomness are scored once, the same way for every arm.
- `problems/bin_packing_online` if it is ready and its tests pass on branch `exp/bp-ceiling`
  at freeze time (added by merging that branch; no tournament code change).

The non-regression gate only acts on problems with more than one public instance; on
circle packing `lean_gate_patience` differs from `lean` only by the restart rule.

## Seeds and budget

Seeds 0, 1, 2 (replicates; the models are not seedable, seeds drive triage's swaps and
random ranker and the order of nothing else). Budget per run: equal for every arm and problem.

- With three problems: 4 arms x 3 problems x 3 seeds = 36 runs x $2.00 = $72 (cap $75).
- With two problems: 4 x 2 x 3 = 24 runs x $3.00 = $72.

The per-run budget is fixed at freeze time from the smoke run's measured cost per call (see
"Checks done before the grid"). Wall-clock limit 3 hours per run as a safety net only; a run
that hits it is reported as such and keeps its incumbent.

## How the budget is enforced (same for every arm)

All arms run in one process each, in their own Modal container (2 CPU cores, 4 GiB). Every
Anthropic SDK message call in the process goes through `tournament/guard.py`:

1. Before sending, reserve the worst case: input upper bound (UTF-8 bytes of system + messages
   + 2,000) x input price + max_tokens x output price, at `autoresearch/claude.py` PRICES.
2. If it does not fit in cap - spent - reservations in flight, lower max_tokens to what fits.
   Below 2,048 tokens, wait for calls in flight; if none are in flight, the budget is
   exhausted and the call is refused (never sent).
3. After the call, charge the usage the API reported. HTTP error statuses are charged 0;
   other failures (timeouts, broken streams) are charged their full reservation.
4. Every call, refusal and failure is written to `usage.jsonl`.

Server-side refusal fallbacks are stripped from every request (triage's client asks for
them): with a fallback the serving model and price are unknown, so the worst case could not
be bounded. A refusal is then an ordinary recorded outcome. Code paths the guard does not
cover (streaming create, batches, beta create) raise instead of sending.

Lowering max_tokens near the end of a budget applies to every arm in the same way and lets
each arm spend close to its full cap. The Jev ranker, if used, is billed outside Anthropic;
its cost is added to the same cap.

## Measurement (same for every arm)

All evaluations go through `autoresearch.gate.evaluate` via `tournament/evallog.py`, which
appends one record per evaluation to a private `evals.jsonl` (public per-instance scores,
validity, hidden-instance scores). Arms never read this log; hidden scores never reach a
prompt or a decision.

- Incumbent: the program the arm would submit. `lean` arms log it explicitly; for `shinka`
  and `triage` it is the best valid program by public score so far, which is how both choose.
- Curve: incumbent public score against cumulative dollars at the time each evaluation
  finished (`curve.csv` per run, `all_curves.csv` per grid).

**Primary endpoint:** AUC gain = (area under incumbent score over budget fraction [0, 1]
minus the starting score) / (1 - starting score). It rewards both how far and how early an
arm improves; 0 means no improvement, 1 means matching the best known result from the start.

**Primary comparisons:** each of `triage`, `lean`, `lean_gate_patience` against `shinka`,
paired on (problem, seed); mean difference with a seed-level bootstrap 95% interval
(10,000 resamples) over the matched units, Holm-adjusted across the three comparisons.
With 9 (or 6) units the intervals will be wide; a null is reported as a null.

**Secondary:** final public score at the cap; final hidden score of the incumbent
(erdos_squares only); hidden score of the best public program seen; dollars and tokens per
improvement; number of calls and valid evaluations; wall time; `lean_gate_patience` minus
`lean` (does the add-on help?); per-problem breakdowns; any program flagged as exceeding a
best known value (re-checked by the strict checker, reviewed by hand before any claim).

## Provenance

Each run folder holds `job.json` (job, arm config, git commit, package versions, SHA-256 of
`tournament/`, `autoresearch/`, `strategist/controller.py` and the problem folder),
`usage.jsonl`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`,
`best_program.py`, `stdout.log.gz` and `artifacts.tar.gz` (every program and the arm's own
logs: ShinkaEvolve's database, triage's log and notebook). Grid launches are recorded in
`launches/`.

## Commands

```bash
modal run tournament/modal_app.py --grid experiments/tournament-v1/grids/full.json --dry-run   # caps and job list
modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/full.json    # launch
python -m tournament.pull full-v1                                                              # results + report
```

The launcher refuses a grid whose job budgets sum above `anthropic_cap_usd` or whose
worst-case Modal cost (jobs x (wall limit + 25 min) x container price) exceeds `modal_cap_usd`.

## Checks done before the grid

See the end of this file once filled in: mock grid on Modal, live smoke run.

## Frozen configuration

(Filled in at go-ahead: commit, final arm configs, budget per run, problems.)

## Changes after freezing

(None yet.)
