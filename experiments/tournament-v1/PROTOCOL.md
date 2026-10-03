# Tournament v1: complete frameworks at equal dollar budgets

Written and committed before the confirmatory grid (`grids/full.json`) was launched. The
earlier draft of this file (commit ce8adf7) had four arms and two or three problems; the
changes made before freezing are listed under "Changes before freezing". Changes after
launch, if any, are listed at the end.

## Question

At the same Anthropic spend, which complete autoresearch loop reaches the best scores, and
how fast? Each arm is a whole framework (its prompts, models, selection and stopping),
measured by the same meter.

## Arms

| Arm | What runs | Models |
|---|---|---|
| `shinka` | Stock ShinkaEvolve 0.0.7 through `autoresearch/run.py`: diff, full and cross patches, islands, meta and novelty LLMs, no embeddings. Its own `--max-cost` is also set to the cap. | Sonnet 5.5 (effort high) for every role |
| `triage` | `autoresearch/triage.py` unchanged: Opus proposes 6 ideas per round, the Jev ranker splits them into thirds, Opus / Sonnet / Haiku implement them (15% of assignments swapped), an Opus refinement promotes a cheaper model's improvement. | Opus 5.5, Sonnet 5.5, Haiku 4.5; Jev (TypeSafe) |
| `lean` | `tournament/lean.py`: each call proposes and implements one change to the current best program; the best valid program is kept; the prompt lists the last 8 attempts and their outcomes. This is greedy sequential best-of-N, which Gupta et al. (2026, arXiv 2607.18235) report no harness among 30 beat significantly after Holm correction. | Sonnet 5.5, effort high |
| `lean_gate_patience` | `lean` plus (a) a non-regression gate: a candidate is not accepted if it scores below its parent on any public instance in an archive of instances where earlier valid candidates scored below their parents; (b) the strategist `Patience` rule: after T = 5 consecutive non-improving steps, restart from a fresh program written from the problem statement (the best program is always kept). | Sonnet 5.5, effort high |
| `independent` | Every call writes a program from `problem.md` and the starting program only: no history, no parent selection; the best valid program is kept. Independent sampling as in Gideoni, Risi & Gal (2026, arXiv 2602.16805), who report it matching or beating ShinkaEvolve on these problems at about $20 per problem. | Sonnet 5.5, effort high |

Every call has max_tokens 32,000. `shinka`, `lean`, `lean_gate_patience` and `independent`
use the same model so they differ in loop design only; triage keeps its tiered models
because model routing is what it tests. T = 5 was set by hand for runs of 15-25 calls; it was
not tuned. The gate only acts on problems with more than one public instance (erdos_squares);
elsewhere `lean_gate_patience` differs from `lean` only by the restart rule.

## Problems

| Problem | Public | Hidden | Start (normalized) | Note |
|---|---|---|---|---|
| `sum_difference` | 1 set | none | 0.887 | reference = 1.2715 + 0.01 size bonus (asymptotic bound); most headroom |
| `erdos_squares` | n = 5-8, 11-15 | n = 18, 21, 23, 27 | 0.856 | reference = k + c/k (best known); the smoke run reached it in 2 calls |
| `circle_packing` | n = 26 | none | 0.34-0.38 | reference = 2.6359830849 (AlphaEvolve); start varies because the seed program is random |

`bin_packing_online` is not in this grid. If budget remains, it may be run afterwards as a
separately reported second wave.

Scores are normalized by the reference (1.0 = the reference value; higher is better). A final
score of at least 1 - 1e-6 is reported as a tie with the reference, not a win. A program that
scores above a reference is re-checked by the gate's strict checker (1e-12); it is listed with
the reference value, the margin and n x the checker tolerance (1e-9; 0 for the exact
sum-difference checker), and a margin below n x tolerance is not a claim. Nothing is claimed
as a record without a human review.

## Seeds and budget

Seeds 0, 1, 2, 3 for every arm and problem. The models are not seedable; seeds drive triage's
swaps, and otherwise the runs are replicates. Budget per run: **$1.10 hard cap**, the same for
every arm and problem.

Choice (from the smoke run, below): one run at a $1 cap made 20 Sonnet calls for $0.962. At
about $1 per run, 5 arms x 3 problems x 5 seeds would cost $75 plus $1.66 already spent on the
smoke run and live check, which does not fit; 4 seeds fit. 60 runs x $1.10 = $66.00, plus
$0.96 (smoke) and at most $0.70 (live check) = at most $67.66, leaving about 10% of the $75
cap unused. The launcher refuses the grid if the job budgets sum above `anthropic_cap_usd`
($73.30 = $75 minus the smoke run and the live check).

Modal: 60 containers in parallel, 4 CPU cores and 6 GiB each, wall-clock limit 2.5 hours per
run (a safety net; a run that hits it keeps its incumbent and is reported). Worst case
$41.51 (60 x 2.92 h x $0.237 per hour), under the $74 Modal cap the launcher enforces.

## How the budget is enforced (same for every arm)

Every Anthropic SDK message call in a run's process goes through `tournament/guard.py`:

1. Before sending, reserve the worst case: input upper bound (UTF-8 bytes of system + messages
   + 2,000) x input price + max_tokens x output price, at `autoresearch/claude.py` PRICES.
2. If it does not fit in cap - spent - reservations in flight: wait for calls in flight to
   settle; with nothing in flight, lower max_tokens to what fits; below 2,048 tokens the budget
   is exhausted and the call is refused (never sent).
3. After the call, charge the usage the API reported. HTTP error statuses are charged 0; other
   failures (timeouts, broken streams) are charged their full reservation.
4. Requests that fail at the start with 429 / 5xx / 529 are retried with backoff for up to 10
   minutes (not billed). Every call, refusal, retry and failure is written to `usage.jsonl`.

Server-side refusal fallbacks are stripped (triage's client asks for them), because the serving
model and price would be unknown. Paths the guard does not cover raise instead of sending. The
Jev ranker is billed by TypeSafe; its cost is added to the same cap.

## Measurement (same for every arm)

All evaluations go through `autoresearch.gate.evaluate` via `tournament/evallog.py`, which
writes a private `evals.jsonl` (public per-instance scores, validity, hidden-instance scores,
record flags). Arms never read it; hidden scores never reach a prompt or a decision.

- Incumbent: the program the arm would submit. Lean-family arms log it; for `shinka` and
  `triage` it is the best valid program by public score so far, which is how both choose.
- Curve: incumbent public score against cumulative dollars when each evaluation finished.

**Primary endpoint:** AUC gain = (area under incumbent score over budget fraction [0, 1]
minus the starting score) / (1 - starting score). It rewards how far and how early an arm
improves; 0 = no improvement, 1 = at the reference from the start.

**Primary comparisons:** each of `triage`, `lean`, `lean_gate_patience` and `independent`
against `shinka`, paired on (problem, seed): mean difference with a bootstrap 95% interval
(10,000 resamples of the 12 matched units) and P(arm > shinka) (ties count one half) with a
bootstrap 95% interval; Holm adjustment across the four comparisons for any p-value quoted.
With 12 units the intervals will be wide; a null is reported as a null.

**Secondary:** final public score at the cap; final hidden score (erdos_squares only); hidden
score of the best public program seen; runs that tie with the reference; dollars and tokens per
improvement; calls; valid evaluations; wall time; `lean_gate_patience` minus `lean`;
`lean` minus `independent` (does conditioning on history help?); per-problem breakdowns;
record flags.

## Provenance

Each run folder holds `job.json` (job, arm config, git commit, package versions, SHA-256 of
`tournament/`, `autoresearch/`, `strategist/controller.py` and the problem folder),
`usage.jsonl`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`, `best_program.py`,
`stdout.log.gz` and `artifacts.tar.gz` (every program and the arm's own logs). The launch
record goes to `launches/`.

## Checks done before the grid

- **Mock grid on Modal** (`grids/mock.json`, results in `runs/mock-v1/`): 4 arms x 2 problems x
  2 seeds against the local mock API with $0.50 virtual caps. All 16 containers finished,
  every run stayed within its cap, no errors.
- **Live smoke run** (`grids/smoke.json`, `runs/smoke-v1/`): `lean` on erdos_squares, $1 cap:
  20 calls, $0.962, 140,478 tokens, 678 s; public score 0.856 -> 1.000 (reached in the second
  call), hidden 0.913 -> 1.000.
- **Live check** (`grids/check.json`, `runs/check-v1/`): `shinka` ($0.25) and `triage` with Jev
  ($0.45) on erdos_squares, to exercise the two client paths the smoke run did not. Not part
  of the comparison.

## Changes before freezing (from the draft)

- Added the `independent` arm and named `lean` as greedy best-of-N (literature review,
  `context/related-work.md` on branch docs/related-work).
- Problems: sum_difference and erdos_squares first, circle_packing third; bin_packing_online
  dropped from this grid.
- Triage ranker set to Jev. `shinka` uses Sonnet 5.5 rather than its launcher's default Opus.
- Seeds 4 and $1.10 per run (from the smoke run), instead of 3 x $2.
- Added P(A > B) with bootstrap intervals, record ties, and record flags with reference,
  margin and n x tolerance.
- The guard waits for in-flight calls before shortening max_tokens (so parallel arms are not
  truncated early) and retries rate-limited requests.

## Changes after launch

(None yet.)
