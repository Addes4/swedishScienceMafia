# Tournament v2: open models through the Hugging Face router (infrastructure and smoke only)

**Question.** Can the tournament run every arm on cheap open models, and what would a v2 grid
cost in money and time?

**Answer.** Yes; the route works for all five arms. The confirmatory v2 grid in PROTOCOL.md was
**not run**: tournament-v1's partial data already answered the main question (at a low budget,
single-call loops are as good as or better than the structured frameworks, and the problems
saturate quickly), and the remaining time went to the submission.

- **Route.** Every arm (ShinkaEvolve, triage, lean, lean_gate_patience, independent) ran live on
  the Hugging Face router under the same hard dollar cap, with prices read from the router.
  Six smoke runs cost $0.1408 of HF credit in total.
- **Cost per call** is about 25 times lower than Claude Sonnet 5.5 in v1: a DeepSeek-V4.1-Flash
  call cost $0.0019 on average (2,400 output tokens) against $0.048 for Sonnet.
- **Evaluation time, not the model, limits the wall clock.** A model call took 13 to 28 s (median
  per run), but one evaluation of a program written from scratch took up to 665 s, because the
  gate scores the 13 erdos_squares instances one after another, each up to its 60 s limit. At
  $0.15 per run (about 78 calls) a grid would be bounded by time, not money, unless instances are
  scored in parallel or the limits are lowered (both now available, below).
- **Hidden instances caught a weak program.** independent's best public program (0.960 of the
  reference on n = 5-15) scored 0.238 on the hidden n = 18-27, because it timed out on three of the
  four larger instances.

## What we did

### The Hugging Face route

| File | Role |
|---|---|
| `tournament/hf.py` | Budget guard on the openai SDK's chat completions (sync and async), prices from `/v1/models`, `HFClient` with `Claude.call`'s interface |
| `tournament/budget.py` | `register_prices` for models outside the Claude price table |
| `tournament/context.py`, `lean.py`, `arms.py` | `ctx.llm()` picks the client by provider; triage swaps its client; ShinkaEvolve uses its own OpenAI-compatible client (`local/<model>@https://router.huggingface.co/v1?api_key_env=HF_TOKEN`) |
| `tournament/run.py`, `grid.py`, `modal_app.py` | `"provider": "hf"` and `"hf_models"` in a grid; the Modal secret `ssm-hf` (HF_TOKEN) is attached for HF grids |
| `tournament/mockapi.py` | Also serves the router's OpenAI-compatible routes, for zero-cost tests |
| `autoresearch/gate.py` | Optional `GATE_WORKERS` (score instances in a shared process pool; results identical) and `GATE_TIMEOUT_S` (run-wide per-instance limit); defaults unchanged |
| `tests/test_tournament_hf.py` | 9 tests: prices from the listing, cap holds, reasoning-token accounting, 401/402/403 and "insufficient credits" fatal, 429 retried, unbounded requests refused |

Models are pinned to one provider with the router's `model:provider` suffix, so price and
behaviour stay fixed. Prices on 3 October 2026 (`/v1/models`, recorded in each run's `job.json`):

| Model:provider | Input $/M | Output $/M | Used for |
|---|---|---|---|
| deepseek-ai/DeepSeek-V4.1-Flash:deepinfra | 0.20 | 0.60 | every single-model arm; triage middle tier |
| deepseek-ai/DeepSeek-V4-Pro:deepinfra | 1.30 | 2.60 | triage ideas and favourites |
| Qwen/Qwen3.5-9B:together | 0.17 | 0.25 | triage long shots |

deepinfra reported 0 reasoning tokens for Flash in every call; content was never empty. The guard
bills reported reasoning tokens as output either way. Errors 401, 402, 403 and any message about
insufficient credit or billing are fatal (no retry, later calls refused); 429 and 5xx are retried.
The Jev ranker was checked with one call ($0.000025) and used for triage.

### Work log

- Mock runs of lean, triage and ShinkaEvolve on the HF path, then a local live smoke (lean, $0.03
  cap, 900 s wall limit) and a Modal live smoke of all five arms (erdos_squares, seed 0, $0.03
  cap, 1,800 s wall limit, 2 cores).
- The coordinator's review of the smoke found that evaluation dominated wall time. In response we
  added parallel instance scoring and run-wide time limits that are also stated to the model
  (commit 764c093), and drafted a pre-launch amendment. Neither was used: the grid was cancelled.

## Results: smoke runs (erdos_squares, seed 0)

Scores are fractions of the reference (higher is better). "Completion": budget = the cap was used;
wall_limit = the clock ended the run first. Evaluation and call times are seconds.

| run | arm | completion | calls | $ spent | wall s | evals | eval s median | eval s max | call s median | start | final public | final hidden |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Modal | shinka | budget | 9 | 0.0270 | 675 | 8 | 1.9 | 12.3 | 26.8 | 0.8562 | 0.9485 | 0.9566 |
| Modal | triage | budget | 7 | 0.0239 | 1198 | 7 | 12.0 | 568.7 | 27.5 | 0.8562 | 0.9234 | 0.8993 |
| Modal | lean | budget | 17 | 0.0273 | 677 | 18 | 1.9 | 137.0 | 13.0 | 0.8562 | 0.9791 | 0.9712 |
| Modal | lean_gate_patience | budget | 12 | 0.0269 | 1169 | 13 | 24.2 | 344.3 | 17.8 | 0.8562 | 0.8960 | 0.8759 |
| Modal | independent | wall_limit | 6 | 0.0129 | 2183 | 7 | 255.0 | 665.2 | 27.4 | 0.8562 | 0.9600 | 0.2381 |
| local | lean | wall_limit | 12 | 0.0230 | 1277 | 13 | 1.1 | 508.3 | 15.6 | 0.8562 | 0.9267 | 0.9449 |

Triage made 3 Pro, 2 Flash and 2 Qwen calls; one Qwen call on together took 481 s
including a 504 retry. One run per arm says nothing about which arm is better. With Sonnet in v1,
lean reached the reference on erdos_squares in two calls; with Flash it reached 0.979 in 17.

## What it means and what it does not show

- The route and the cap work for every arm; a v2 grid could be launched with one command
  (PROTOCOL.md). It was not, so there is no v2 comparison.
- Open models give many more calls per dollar, but then program evaluation sets the pace:
  sequential instances with 60 s limits make some evaluations take 10 minutes. Parallel instance
  scoring (`gate_workers`) keeps scores identical and cuts wall time by up to the number of
  instances; lower limits (`timeout_overrides`) change the problem and must be told to the model
  and applied to every arm.
- Single smoke runs; seed 0 only; one problem.

## Cost

| Item | Amount |
|---|---|
| Hugging Face credit (recorded, at listed prices) | $0.1408 (Modal smoke $0.1178, local smoke $0.0230) |
| Jev | $0.00028 |
| Modal, smoke-v2 app (billing report, last hour possibly incomplete) | $0.22 |
| Modal, whole tournament (v1 and v2, app ssm-tournament, 3 Oct) | $7.47 |

## Reproduce

```bash
python -m pytest tests -q                 # includes the HF tests (mock only)
# create the HF secret once without printing the token, e.g. a script that passes HF_TOKEN=<file contents>
modal run tournament/modal_app.py --grid experiments/tournament-v2/grids/smoke.json      # $0.15 at most
python -m tournament.pull smoke-v2 --experiment tournament-v2
```

Any arm on open models in one job (reads HF_TOKEN or ~/.cache/huggingface/token):

```bash
python -m tournament.run --out /tmp/hf-lean --job '{"job_id": "x", "grid": "adhoc", "arm": "lean",
  "arm_config": {"type": "lean", "model": "deepseek-ai/DeepSeek-V4.1-Flash:deepinfra"},
  "problem": "erdos_squares", "seed": 0, "budget_usd": 0.05, "wall_limit_s": 1800, "mock": false,
  "provider": "hf", "hf_models": ["deepseek-ai/DeepSeek-V4.1-Flash:deepinfra"], "gate_workers": 8}'
```

## Evidence index

| Path | Contents |
|---|---|
| `PROTOCOL.md` | Drafted design of the v2 grid, marked not executed |
| `RESULTS.md` | This file |
| `summary.json` | Headline numbers, machine-readable |
| `smoke_summary.json` | The smoke table above, computed from the run folders |
| `grids/smoke.json`, `grids/full.json` | Smoke grid (run) and confirmatory grid (not run) |
| `launches/smoke-v2_*.json` | Launch record of the Modal smoke |
| `runs/smoke-v2/<arm>__erdos_squares__s0/`, `runs/local-smoke-v2/` | Per run: `job.json` (with prices), `usage.jsonl`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`, `best_program.py`, `artifacts.tar.gz` |

## Next steps

If the comparison is wanted later: launch `grids/full.json` with `"gate_workers": 8` and more cores
per container, after recording that change in PROTOCOL.md; it costs at most $9.00 of HF credit.

## Suggested README text

> Every tournament arm also runs on open models through the Hugging Face router
> (`"provider": "hf"` in a grid), under the same per-call dollar cap with prices read from the
> router. A DeepSeek-V4.1-Flash call costs about $0.002, so at small budgets the evaluator, not the
> model, sets the pace; `gate_workers` scores instances in parallel.
