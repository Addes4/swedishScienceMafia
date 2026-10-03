# Tournament v2: the same frameworks on open models, at equal dollar budgets

**Status: NOT EXECUTED.** The confirmatory grid was cancelled before launch (see RESULTS.md); only
the smoke runs below were made. The design is kept as drafted.

Written and committed before the confirmatory grid (`grids/full.json`) is launched. Changes made
after launch are listed at the end.

## Why v2

tournament-v1 (Claude, $1.10 per run) was cut short when the Anthropic key ran out of credit, and
two of its three problems were saturated for Claude Sonnet 5.5 (see ../tournament-v1/RESULTS.md).
v2 asks the same question with open models through the Hugging Face router, which costs about a
twentieth per call, so each run can make many more calls at a small budget. A local smoke run on
erdos_squares reached 0.927 of the reference in 12 calls (Sonnet reached 1.0 in two), so the
problems are not saturated for this model.

## Question

At the same dollar spend, which complete autoresearch loop reaches the best scores, and how fast?

## Arms

All single-model arms use **deepseek-ai/DeepSeek-V4.1-Flash on the deepinfra provider** (pinned
with the router's `model:provider` suffix). Every call has max_tokens 32,000.

| Arm | What runs |
|---|---|
| `shinka` | Stock ShinkaEvolve 0.0.7 through `autoresearch/run.py`, its own OpenAI-compatible client (`local/<model>@https://router.huggingface.co/v1`) for proposals, meta and novelty calls; no embeddings |
| `triage` | `autoresearch/triage.py` unchanged except the client: ideas and the favourite tier on deepseek-ai/DeepSeek-V4-Pro (deepinfra), middle tier on DeepSeek-V4.1-Flash (deepinfra), long shots on Qwen/Qwen3.5-9B (together); Jev ranker (checked working with one call before launch); 6 ideas per round, 15% swaps, promotions |
| `lean` | One call per step proposes and implements one change to the current best program; best valid program kept; the last 8 attempts and outcomes in the prompt (greedy sequential best-of-N, the baseline Gupta et al. 2026 found no harness beat after Holm correction) |
| `lean_gate_patience` | `lean` + non-regression gate on archived failing instances + strategist `Patience` restart after T = 5 non-improving steps (fresh program from the problem statement) |
| `independent` | Every call writes a program from `problem.md` and the starting program only; best kept (independent sampling, Gideoni, Risi & Gal 2026) |

Claude-specific `effort` settings are ignored on the router (the HF client sends none).

## Prices (from the router's /v1/models, recorded in every run's job.json)

| Model:provider | Input $/M | Output $/M |
|---|---|---|
| deepseek-ai/DeepSeek-V4.1-Flash:deepinfra | 0.20 | 0.60 |
| deepseek-ai/DeepSeek-V4-Pro:deepinfra | 1.30 | 2.60 |
| Qwen/Qwen3.5-9B:together | 0.17 | 0.25 |

deepinfra reported 0 reasoning tokens for Flash in the smoke run; whatever a provider reports as
reasoning is billed as output (added if it is reported on top of completion_tokens).

## Problems

sum_difference (1 public instance), erdos_squares (9 public, 4 hidden: n = 18, 21, 23, 27),
circle_packing (n = 26, 1 public). Scores are normalized by the reference value (1.0 = reference,
higher is better); at least 1 − 1e-6 is a tie with the reference. Scores above a reference are
re-checked by the strict checker and listed with the reference value, margin and n x tolerance;
nothing is claimed without human review.

## Seeds and budget

Seeds 0-3 for every arm and problem (60 runs). **$0.15 hard cap per run**, the same for all.
The user's limit for HF spend in this study is $12: 60 x $0.15 = $9.00, plus the smoke runs
(at most $0.15 on Modal, $0.023 locally), leaves more than 10% headroom. The launcher refuses the
grid if recorded experiment spend plus job budgets exceed `experiment_cap_usd` = $12.

From the smoke run: a Flash call costs about $0.0019 and takes about 17 s; an erdos_squares step
including evaluation took about 106 s. $0.15 buys about 78 Flash calls. Wall-clock limit 6 hours
per run (circle packing programs may run 300 s each); a run that hits it is reported as
`stopped_early` and is not budget-matched.

Modal: one container per run, 2 cores and 4 GiB, all 60 in parallel. Worst case $48.74 (checked
by the launcher against `modal_cap_usd` = $60); the tournament's Modal total stays under $75.
Triage evaluates up to six programs at once on the same two cores, so CPU contention can make its
candidates slower than other arms' (disclosed, not corrected).

## Enforcement and measurement

As in v1 (../tournament-v1/PROTOCOL.md): every openai-SDK chat completion in a run's process goes
through `tournament/hf.py`'s guard (worst-case reservation, settle with reported usage, refuse when
the cap cannot pay). HTTP 401, 402, 403 and any error mentioning insufficient credit or billing are
fatal: no retry, every later call refused, run status `fatal_api_error`. 429 and 5xx are retried
for up to 10 minutes. Every evaluation is logged to `evals.jsonl` through the integrity gate; hidden
scores never reach a prompt or decision.

A run is **budget-matched** if it used its cap before any API error or the wall limit
(completion `budget`). Truncated runs are reported separately, never mixed with complete ones.

**Primary endpoint:** AUC gain over the full budget = (area under incumbent public score over
budget fraction [0, 1] minus the starting score) / (1 − starting score).

**Primary comparisons:** `triage`, `lean`, `lean_gate_patience`, `independent` each against
`shinka`, paired on (problem, seed), 12 units per comparison when all runs are complete: mean
difference with a bootstrap 95% CI, P(arm > shinka) with a bootstrap CI, sign-flip permutation p
with Holm adjustment across the four. If some runs are truncated, the complete pairs are analysed
and, as a secondary analysis, all runs at a common spend checkpoint (smallest valid spend per
problem, rounded down to $0.05), as in v1.

**Secondary:** final public score; final hidden score (erdos_squares); runs at the reference;
dollars and calls per improvement; `lean_gate_patience` − `lean`; `lean` − `independent`;
per-problem tables; record flags.

## Commands

```bash
modal run tournament/modal_app.py --grid experiments/tournament-v2/grids/full.json --dry-run
modal run --detach tournament/modal_app.py --grid experiments/tournament-v2/grids/full.json
python -m tournament.pull full-v2 --experiment tournament-v2
python -m tournament.report experiments/tournament-v2/runs/full-v2 --figure experiments/tournament-v2/curves.svg \
    --headline experiments/tournament-v2/summary.json
```

## Checks before the grid

- Mock runs of lean, triage and ShinkaEvolve on the HF path (local mock of the router).
- Jev key checked with one call ($0.000025).
- Local live smoke (lean, erdos_squares, $0.03 cap, 900 s wall limit): 12 Flash calls, $0.023,
  0.856 → 0.927 public, hidden 0.913 → 0.945; it hit the wall limit, not the cap.
- Modal live smoke of all five arms (`grids/smoke.json`, erdos_squares, $0.03 each): results in
  `runs/smoke-v2/` and RESULTS.md. Evaluation, not the model, set the wall time (up to 665 s per
  evaluation); a pre-launch amendment (parallel instance scoring, possibly lower time limits) was
  being prepared when the grid was cancelled.

## Changes after launch

(None yet.)
