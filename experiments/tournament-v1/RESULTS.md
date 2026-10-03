# Tournament v1 (partial): five autoresearch frameworks at $1.10 per run

**Question.** At the same Anthropic spend, which complete autoresearch loop reaches the best scores,
and how fast?

**Answer: not settled by this run.** The API key ran out of credit 13.6 minutes into the grid.
17 of 60 runs used their full $1.10 budget; 43 were cut short. This is a partial study, not the
budget-matched comparison that PROTOCOL.md pre-registered.

- **Complete runs (17)** reached the reference value on every erdos_squares and circle_packing run
  that finished, so final scores tie. The 5 complete sum_difference runs ended at 0.9469 to 0.9471
  of the reference. Too few complete pairs exist for a comparison (1 to 3 per arm).
- **Common spend checkpoint (all 60 runs, disclosed post hoc).** Every run is valid up to the spend
  it had reached before its first API error. At $0.10 (circle_packing), $0.15 (erdos_squares) and
  $0.30 (sum_difference), the single-model loops were ahead of ShinkaEvolve in area under the
  score-versus-spend curve: lean +0.233 (bootstrap 95% CI [0.096, 0.386], 10 wins / 2 losses of
  12, Holm p = 0.007), independent sampling +0.209 ([0.104, 0.321], 11/1, Holm p = 0.006),
  lean_gate_patience +0.195 ([0.034, 0.375], 9/3, Holm p = 0.070). Triage was behind: −0.156
  ([−0.254, −0.046], 1/11, Holm p = 0.038).
- **The score at the checkpoint** did not differ significantly between any arm and ShinkaEvolve
  (all Holm p ≥ 0.44). The area differences say who got there first at a very low spend, which
  favours arms whose first call already writes a full program; triage spends its first dollars on
  an Opus idea call and six parallel implementations.
- **Two of the three problems are saturated for Claude Sonnet 5.5**: circle packing n = 26 and
  Erdős squares reach the reference within one to three calls. No score exceeded a reference.

## What we did

### Built

All new code is in `tournament/` plus tests; `autoresearch/run.py` got a small change (it takes
`argv` and an `--eval-program`) so ShinkaEvolve runs in-process with logged evaluations.

| File | Role |
|---|---|
| `tournament/budget.py` | Hard dollar cap: reserve each call's worst case before sending, settle with reported usage, log every call to `usage.jsonl`; `FatalAPIError` |
| `tournament/guard.py` | Routes every Anthropic SDK message call in the process through the budget (covers ShinkaEvolve's own clients); strips refusal fallbacks; retries 429/5xx; billing and authentication errors are fatal; blocks unbudgeted paths |
| `tournament/mockapi.py` | Local fake of the Messages API (JSON and streaming) with priced usage and injectable failures, for zero-cost end-to-end runs |
| `tournament/evallog.py`, `shinka_eval.py` | One logged integrity-gate evaluation per program (`evals.jsonl`), with hidden scores and record flags (reference, margin, n x tolerance) |
| `tournament/context.py` | What an arm gets: problem, output folder, budget, config, `evaluate()`, `incumbent()` |
| `tournament/lean.py` | `lean`, `lean_gate_patience` (non-regression gate + strategist `Patience` restarts) and `independent` loops |
| `tournament/arms.py` | Arm registry; adapters for stock ShinkaEvolve and triage |
| `tournament/run.py` | One job (arm, problem, seed, cap): provenance, mock or live API, watchdog, summary, artifact archive |
| `tournament/metrics.py` | Per-run metrics: incumbent curve against dollars, AUC gain, completion class, valid spend, `score_at` / `auc_to` a checkpoint |
| `tournament/report.py` | Grid report: complete-run tables, checkpoint analysis, paired comparisons (bootstrap CIs, P(A > B), sign-flip p, Holm), SVG curves |
| `tournament/grid.py` | Grid files, job lists, Anthropic / Modal / experiment-wide cap checks |
| `tournament/modal_app.py`, `pull.py` | Modal app `ssm-tournament` (one container per job, Volume, secret) and result download and compaction |
| `tests/test_tournament_budget.py`, `tests/test_tournament.py` | 28 tests: cap never exceeded, parallel callers, retries, fatal billing/auth errors, blocked paths, gate logic, metrics, grid caps, statistics, mock end-to-end runs of every arm |

### Setup

5 arms (shinka, triage with the Jev ranker, lean, lean_gate_patience, independent) x 3 problems
(sum_difference, erdos_squares, circle_packing) x 4 seeds, $1.10 hard cap per run, one Modal
container per run (4 cores, 6 GiB), all 60 in parallel, launched from commit 6f4ec27. Arms,
endpoints and statistics are in PROTOCOL.md (frozen before launch).

How many calls $1.10 bought in the complete runs: lean 28 to 36 Sonnet calls; lean_gate_patience
23 to 25; ShinkaEvolve 24 to 30 calls producing 12 to 19 evaluated programs; triage 1 or 2 rounds
(6 to 14 calls, 3 to 8 of them Opus). Independent sampling had no complete run; its erdos_squares
runs made 17 to 19 calls before the cutoff.

### Work log

- Mock grid on Modal (16 runs, both problems, every arm, virtual dollars): all finished within cap.
- Live smoke run (lean, erdos_squares, $1 cap): 20 calls, $0.962, reached the reference in call 2.
- Live check of ShinkaEvolve and triage+Jev ($0.67): both client paths work under the guard.
- Bugs found and fixed before the grid: shrinking max_tokens whenever in-flight reservations
  crowded the cap truncated parallel arms early (now they wait); no retry on rate limits (added).
- **The cutoff.** 13.6 minutes after launch every request started failing with HTTP 400 "Your
  credit balance is too low". The guard treated that as an ordinary error: lean-family runs stopped
  after six consecutive failures; ShinkaEvolve retried, sending 12,378 failed requests until the
  coordinator stopped the app. Fixed afterwards (commit 65ffdcb): a credit-balance 400, a 401 or a
  403, returned at once or inside a stream, is never retried, costs nothing, and stops every later
  call in the process; runs end with status `fatal_api_error`. Tests cover all three paths.
- **Deviation from PROTOCOL.md.** The pre-registered endpoint (AUC gain over the full $1.10) cannot
  be computed for 43 runs. The checkpoint analysis above was chosen after the cutoff; its rule
  (smallest valid spend per problem, rounded down to $0.05) uses no score information.

## Results

### Complete runs (budget used before any error), full budget

Scores are fractions of the reference value (higher is better; at least 1 − 1e-6 is a tie).

| problem | arm | runs | final public (mean) | min | max | AUC gain | final hidden | $ spent | calls |
|---|---|---|---|---|---|---|---|---|---|
| circle_packing | triage | 2 | 1.0000 | 1.0000 | 1.0000 | 0.7689 | – | 1.0568 | 14.0 |
| erdos_squares | lean | 3 | 1.0000 | 1.0000 | 1.0000 | 0.9426 | 1.0000 | 1.0729 | 31.3 |
| erdos_squares | lean_gate_patience | 2 | 1.0000 | 1.0000 | 1.0000 | 0.9192 | 1.0000 | 1.0890 | 24.0 |
| erdos_squares | shinka | 4 | 1.0000 | 1.0000 | 1.0000 | 0.9329 | 1.0000 | 1.0638 | 27.0 |
| erdos_squares | triage | 1 | 1.0000 | 1.0000 | 1.0000 | 0.9057 | 0.9920 | 1.0800 | 7.0 |
| sum_difference | shinka | 1 | 0.9469 | 0.9469 | 0.9469 | 0.5018 | – | 1.0768 | 25.0 |
| sum_difference | triage | 4 | 0.9470 | 0.9469 | 0.9471 | 0.4661 | – | 1.0685 | 10.8 |

### Common spend checkpoint (all 60 runs)

Gain = (score at the checkpoint − start) / (1 − start); AUC gain = the same for the mean score over
spend [0, checkpoint]. Higher is better.

| problem ($ checkpoint) | arm | score (mean) | min | max | gain | AUC gain | runs at reference |
|---|---|---|---|---|---|---|---|
| circle_packing ($0.10) | independent | 0.9998 | 0.9994 | 1.0000 | 0.9997 | 0.5829 | 3 / 4 |
| | lean | 0.9692 | 0.9361 | 0.9994 | 0.9533 | 0.7070 | 0 / 4 |
| | lean_gate_patience | 0.9820 | 0.9288 | 1.0000 | 0.9703 | 0.7314 | 2 / 4 |
| | shinka | 0.8410 | 0.3661 | 1.0000 | 0.7493 | 0.1379 | 2 / 4 |
| | triage | 0.5227 | 0.3432 | 0.9685 | 0.2374 | 0.0803 | 0 / 4 |
| erdos_squares ($0.15) | independent | 0.9980 | 0.9921 | 1.0000 | 0.9863 | 0.6532 | 3 / 4 |
| | lean | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6019 | 4 / 4 |
| | lean_gate_patience | 0.9980 | 0.9921 | 1.0000 | 0.9863 | 0.4573 | 3 / 4 |
| | shinka | 0.9941 | 0.9921 | 1.0000 | 0.9588 | 0.5243 | 1 / 4 |
| | triage | 0.9917 | 0.9762 | 1.0000 | 0.9423 | 0.2494 | 2 / 4 |
| sum_difference ($0.30) | independent | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.4868 | 0 / 4 |
| | lean | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.4862 | 0 / 4 |
| | lean_gate_patience | 0.9470 | 0.9469 | 0.9470 | 0.5290 | 0.4911 | 0 / 4 |
| | shinka | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.4336 | 0 / 4 |
| | triage | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.2988 | 0 / 4 |

Paired against ShinkaEvolve at the checkpoint, 12 units (3 problems x 4 seeds); sign-flip
permutation p, Holm-adjusted across the four arms:

| metric | arm | mean difference | bootstrap 95% CI | P(arm > shinka) [95% CI] | wins / ties / losses | p (Holm) |
|---|---|---|---|---|---|---|
| AUC gain | independent | 0.2091 | [0.1037, 0.3212] | 0.92 [0.75, 1.00] | 11 / 0 / 1 | 0.006 |
| AUC gain | lean | 0.2331 | [0.0963, 0.3864] | 0.83 [0.58, 1.00] | 10 / 0 / 2 | 0.007 |
| AUC gain | lean_gate_patience | 0.1947 | [0.0339, 0.3746] | 0.75 [0.50, 1.00] | 9 / 0 / 3 | 0.070 |
| AUC gain | triage | −0.1558 | [−0.2543, −0.0456] | 0.08 [0.00, 0.25] | 1 / 0 / 11 | 0.038 |
| gain | independent | 0.0926 | [0.0005, 0.2594] | 0.58 [0.38, 0.79] | 4 / 6 / 2 | 0.438 |
| gain | lean | 0.0817 | [−0.0219, 0.2588] | 0.54 [0.33, 0.75] | 4 / 5 / 3 | 1.000 |
| gain | lean_gate_patience | 0.0830 | [−0.0195, 0.2590] | 0.71 [0.54, 0.88] | 6 / 5 / 1 | 1.000 |
| gain | triage | −0.1761 | [−0.4990, 0.1436] | 0.33 [0.12, 0.54] | 2 / 4 / 6 | 0.633 |

Secondary contrasts at the checkpoint (12 units): lean_gate_patience − lean, AUC gain −0.0385
[−0.1146, 0.0156], 6/0/6; lean − independent, AUC gain 0.0240 [−0.0454, 0.1076], 6/0/6. No
difference in either.

Hidden scores (erdos_squares, n = 18, 21, 23, 27): every complete run's final program scored 1.0000 (to four decimals)
on the hidden instances except triage seed 2 (0.9920). Record flags: none.

The figure `curves.svg` shows each run's best public score against dollars, drawn only as far as
the run is valid, with the mean over runs up to each problem's checkpoint (vertical line).

## What it means and what it does not show

- It does not answer the pre-registered question: the full-budget comparison needs the 43 runs
  re-run (below).
- At $0.10 to $0.30 per problem, one Sonnet call that writes a whole program is already
  competitive: independent sampling and lean got further per dollar early than ShinkaEvolve and
  triage. This matches the literature's finding that greedy best-of-N and independent sampling are
  strong baselines (Gupta et al. 2026; Gideoni, Risi & Gal 2026), but it is a measurement of the
  first few calls, not of search.
- circle_packing (n = 26) and erdos_squares are saturated for this model: independent sampling
  reaches the reference in one or two calls. A comparison of search frameworks needs problems with
  headroom. sum_difference has headroom but every arm stopped at the same value (0.9469), which
  suggests a shared construction the model knows.
- Threats: the checkpoint rule was chosen after the cutoff; checkpoints differ by problem; at low
  spend the order of an arm's first calls dominates; four seeds; models are not seedable.

## Cost

| Item | Amount |
|---|---|
| Anthropic, full-v1 (recorded) | $40.23 (usage-priced $37.87, plus $2.35 reserved for calls that failed inside a stream, probably not billed; Jev $0.011) |
| Anthropic, smoke and live check | $0.96 + $0.67 |
| Tokens (full-v1) | 4,997,553 |
| Evaluations (full-v1) | 733 programs, each on every public and hidden instance |
| Modal, app ssm-tournament (billing report, 3 Oct) | $7.25 |
| Wall time | complete runs 8.7 to 15.3 minutes (524 to 917 s); grid stopped by hand after the cutoff |

## Re-running the 43 truncated runs

One command, fresh runs with the same arms, seeds and cap (`grids/rerun.json` lists the 43 jobs):

```bash
modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/rerun.json --experiment-cap 90
python -m tournament.pull full-v1-rerun
python -m tournament.report experiments/tournament-v1/runs/full-v1 experiments/tournament-v1/runs/full-v1-rerun \
    --out experiments/tournament-v1/runs/full-v1-merged
```

Cost: at most 43 x $1.10 = $47.30 of Anthropic spend (complete runs used $1.03 to $1.09 each) and
at most $29.75 of Modal (expected about $5). With the $41.86 already recorded the experiment total
would be $89.16, above the $75 cap, so the launcher refuses without `--experiment-cap` set above
that. It needs a funded key in the Modal secret `ssm-llm-keys`.

## HOW-TO

### Launch a grid on Modal

Prerequisites: `pip install -r requirements.txt`, `modal` authenticated, and for live grids the
Modal secret `ssm-llm-keys` created from the git-ignored `.env` (`modal secret create ssm-llm-keys
--from-dotenv .env`; it prints key names only). From the repository root:

```bash
modal run tournament/modal_app.py --grid experiments/tournament-v1/grids/mock.json --dry-run   # caps and job list
modal run tournament/modal_app.py --grid experiments/tournament-v1/grids/mock.json             # mock API: no cost
modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/full.json    # live
python -m tournament.pull full-v1     # Volume -> experiments/tournament-v1/runs/full-v1/, then the report
```

Each job runs in its own container (`python -m tournament.run --job ...`), writes to the Modal Volume
`ssm-tournament` under `/<grid>/<job_id>/`, and returns its summary. Relaunching skips jobs that
already have `summary.json`; `--only lean,erdos_squares` limits a launch. Live launches refuse
uncommitted tracked changes and stamp the commit on every job. One job without Modal:

```bash
python -m tournament.run --arm lean --problem erdos_squares --seed 0 --budget 0.5 --mock --out /tmp/lean-check
```

### Add an arm

A variant is a grid entry, e.g. `"lean_T8": {"type": "lean", "patience": 8}` (options: `DEFAULTS` in
`tournament/lean.py`, the adapters in `tournament/arms.py`). A new framework is one function:

```python
@arm("my_loop")
def my_loop(ctx):                      # tournament.context.Context
    ev = ctx.evaluate(ctx.initial, "initial")
    while not ctx.out_of_time():
        ...                            # any Anthropic SDK call here is budgeted automatically
        ev = ctx.evaluate(code, tag)   # integrity gate + private evaluation log
```

It stops when a call raises `BudgetExhausted` (or its subclass `FatalAPIError`). Frameworks with
their own evaluation runner call `tournament.evallog.evaluate_logged` (ShinkaEvolve runs
`tournament/shinka_eval.py`).

### Add a problem

Add a folder under `problems/` following `problems/README.md`, then name it in a grid's
`"problems"`. `bin_packing_online` (merged from exp/bp-ceiling) was added this way; a mock run on
it completes.

### How costs are capped and collected

- Per call: the guard reserves the worst case (input bytes + 2,000 as an input-token bound, plus
  max_tokens, at `autoresearch/claude.py` PRICES) before sending; waits for in-flight calls if it
  does not fit; shortens the last call; refuses below 2,048 output tokens. Usage replaces the
  reservation; HTTP errors cost 0; timeouts and broken streams are charged their reservation;
  rate limits are retried; billing and authentication errors stop the run.
- Per job: `budget_usd`; a watchdog ends a job that keeps running after exhaustion or past its wall
  limit and still writes its summary.
- Per grid: the launcher refuses if job budgets exceed `anthropic_cap_usd`, the worst-case Modal
  cost exceeds `modal_cap_usd`, or recorded experiment spend plus the grid exceeds
  `experiment_cap_usd` (pull every live grid before launching the next).
- Collected per run: `usage.jsonl`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`,
  `best_program.py`, `stdout.log.gz`, `artifacts.tar.gz`.

## Reproduce

```bash
/Users/adriansohrabi/.venvs/ssm/bin/python -m pytest tests -q
/Users/adriansohrabi/.venvs/ssm/bin/python -m tournament.report experiments/tournament-v1/runs/full-v1 \
    --figure experiments/tournament-v1/curves.svg --headline experiments/tournament-v1/summary.json
```

## Evidence index

| Path | Contents |
|---|---|
| `PROTOCOL.md` | Pre-registered design (frozen at commit 6f4ec27), checks before the grid |
| `RESULTS.md` | This file |
| `summary.json` | Headline numbers (machine-readable) from `tournament.report --headline` |
| `curves.svg` | Best public score vs dollars per run and problem, valid part only |
| `grids/mock.json`, `smoke.json`, `check.json`, `full.json`, `rerun.json` | Grid definitions |
| `launches/*.json` | Per-launch records: grid, caps, one result line per job |
| `runs/mock-v1/` | 16 mock runs on Modal (infrastructure check) with report |
| `runs/smoke-v1/`, `runs/check-v1/` | Live smoke run and live check of shinka and triage |
| `runs/full-v1/` | 60 runs: per run `job.json`, `usage.jsonl(.gz)`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`, `best_program.py`, `artifacts.tar.gz`; `report.md`, `report.html`, `results.json`, `all_curves.csv` |

## Next steps

- Re-run the 43 truncated runs (above) for the pre-registered full-budget comparison, or
- run the same grid on a cheaper open model with problems that have headroom
  (tournament-v2, Hugging Face router).

## Suggested README text

> **Tournament.** `tournament/` runs complete autoresearch frameworks (ShinkaEvolve, triage, a
> lean loop, lean with a non-regression gate and restarts, independent sampling) against each
> other at equal dollar budgets, one Modal container per run, with a hard per-call dollar cap and
> one shared evaluator log. In a partial first run (the API key ran out of credit after 13.6
> minutes; 17 of 60 runs complete), single-call loops got further per dollar than ShinkaEvolve at
> $0.10 to $0.30, and two of the three problems were saturated for Claude Sonnet 5.5.
