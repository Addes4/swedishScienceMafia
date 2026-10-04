# Tournament v2: five frameworks on open models through the Hugging Face router

**Question.** Can the tournament run every arm on cheap open models, and what would a v2 grid
cost in money and time?

**Answer.** Yes, the route works for all five arms. The full grid was run as `full-v2b`.

**Status note.** The grid was first cancelled at 23:05 on 3 October, and the text below the grid
section describes that state. Another session then re-opened it, with a pre-launch amendment at the
end of PROTOCOL.md. It ran as `full-v2b` from 00:23 BST on 4 October, and its results were committed
at 05:28. The coordinating session added the [full-v2b results](#results-full-grid-full-v2b) at
about 06:00 from `summary.json`.

Full-grid headline:
- **No framework differs significantly from ShinkaEvolve.** The grid had 60 runs (5 arms × 3
  problems × 4 seeds) at $0.15 each on DeepSeek-V4.1-Flash, and 47 used their full budget. After
  Holm correction, no arm's area under the score-versus-dollars curve or final public score differs
  from ShinkaEvolve's (all p ≥ 0.25). Triage's curve area is lower: −0.186 [−0.347, −0.041].
- **Results depend on the problem:**
  - on bin packing the single-model loops ended highest (mean final public score 0.983, against
    0.976 for ShinkaEvolve), and triage stayed at best-fit;
  - on Erdős squares ShinkaEvolve ended highest and held up on hidden instances (0.986);
  - on sum-difference only 9 of 20 runs finished their budget.
- **Hidden instances exposed programs that do not scale.** The two complete lean runs on Erdős
  squares averaged 0.994 public but 0.125 hidden (0 and 0.25). Of their evaluations, 34 of 46 and
  15 of 50 hit an instance time limit, so their programs scored 0 on the larger hidden instances.
  ShinkaEvolve's seed-0 run had no timeouts.
- **Cost:** $8.04 of HF credit, 19.6 million tokens and 5,284 evaluations. Every run stayed within its
  cap.

Smoke results (before the grid):

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

## Results: full grid (full-v2b)

Grid: [grids/full.json](grids/full.json) as amended (bin_packing_online replaced circle_packing; 4 gate
workers, 4 cores and a 4-hour wall limit per run). It covers 5 arms × sum_difference, erdos_squares
and bin_packing_online × seeds 0–3, with $0.15 of HF credit per run. The reference arm is ShinkaEvolve. All
numbers below come from [summary.json](summary.json); per-run data is in `runs/full-v2b/`.

**Completion.**
- 47 of 60 runs used their full budget.
- 13 were stopped before it, with no final status: 11 on sum_difference, where each evaluation is
  slow, and 2 lean runs on erdos_squares, where 37 of 46 and 30 of 45 evaluations hit an instance
  time limit.
- They are excluded from the full-budget table below. They count in the checkpoint comparison at
  $0.10, which covers bin packing and Erdős squares only.

### Runs that used their full budget

The public score is the mean over the visible instances, normalised to the reference (higher is
better); hidden instances are never used for selection. Sum-difference has no hidden instances.

| Problem | Arm | Complete runs | Final public, mean (min–max) | Final hidden | Calls per run |
|---|---|---|---|---|---|
| bin_packing_online | lean | 4 | 0.9831 (0.9640–0.9927) | 0.9818 | 189 |
| bin_packing_online | lean_gate_patience | 4 | 0.9825 (0.9642–0.9927) | 0.9822 | 222 |
| bin_packing_online | independent | 4 | 0.9797 (0.9654–0.9910) | 0.9795 | 276 |
| bin_packing_online | shinka | 4 | 0.9755 (0.9616–0.9920) | 0.9747 | 174 |
| bin_packing_online | triage | 4 | 0.9618 (0.9616–0.9619) | 0.9607 | 49 |
| erdos_squares | shinka | 4 | 0.9965 (0.9917–1.0000) | 0.9864 | 54 |
| erdos_squares | lean | 2 | 0.9940 (0.9881–1.0000) | 0.1250 | 48 |
| erdos_squares | lean_gate_patience | 4 | 0.9778 (0.9570–1.0000) | 0.5480 | 52 |
| erdos_squares | independent | 4 | 0.9717 (0.9582–0.9920) | 0.8331 | 76 |
| erdos_squares | triage | 4 | 0.9598 (0.9393–0.9984) | 0.6524 | 22 |
| sum_difference | triage | 4 | 0.9037 (0.8874–0.9350) | – | 38 |
| sum_difference | shinka | 4 | 0.8928 (0.8874–0.9090) | – | 84 |
| sum_difference | lean_gate_patience | 1 | 0.8886 | – | 85 |

For scale on bin packing: best-fit scores 0.9616 public and FunSearch's heuristic 0.9925.

### Each arm against ShinkaEvolve (paired by problem and seed, complete runs)

| Arm | Pairs | Δ area under curve [95% CI] | W/T/L | Holm p | Δ final public [95% CI] | W/T/L | Holm p |
|---|---|---|---|---|---|---|---|
| lean | 6 | −0.004 [−0.182, +0.183] | 3/0/3 | 1.0 | +0.0054 [+0.0000, +0.0116] | 5/0/1 | 0.52 |
| lean_gate_patience | 9 | +0.012 [−0.228, +0.238] | 5/0/4 | 1.0 | −0.0051 [−0.0183, +0.0083] | 4/1/4 | 0.56 |
| independent | 8 | −0.113 [−0.335, +0.114] | 2/0/6 | 1.0 | −0.0103 [−0.0241, +0.0049] | 3/0/5 | 0.56 |
| triage | 12 | −0.186 [−0.347, −0.041] | 5/2/5 | 0.25 | −0.0132 [−0.0281, +0.0029] | 2/2/8 | 0.52 |

At the $0.10 checkpoint (all runs, bin packing and Erdős squares), triage's curve area is again lower
(−0.307 [−0.495, −0.120], Holm p = 0.25), and the other arms do not differ from ShinkaEvolve.
Two Erdős-squares scores were flagged above the reference, by 4.5e-12 and 1.3e-11. Both margins are
below n × tolerance (8e-9 and 1.5e-8), so they are not record claims.

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

- **The full grid** (full-v2b) agrees with tournament-v1 and the literature. With a cheap open model
  and $0.15 per run, no framework is reliably better than ShinkaEvolve or the simple loops. Which
  framework does best depends on the problem, and triage gets started slowest.
- **Hidden instances matter most on Erdős squares,** where many LLM-written programs are too slow
  on the larger hidden instances. A public score near 1.0 can sit next to a hidden score near 0.1.
- **Limits:** 4 seeds per cell, one budget, and 13 runs stopped before using their budget, mostly on
  sum-difference. The runs were not budget-matched on that problem.
- Open models give many more calls per dollar, but then program evaluation sets the pace:
  sequential instances with 60 s limits make some evaluations take 10 minutes. Parallel instance
  scoring (`gate_workers`) keeps scores identical and cuts wall time by up to the number of
  instances; lower limits (`timeout_overrides`) change the problem and must be told to the model
  and applied to every arm.
- Single smoke runs; seed 0 only; one problem.

## Cost

| Item | Amount |
|---|---|
| Hugging Face credit, full-v2b grid (recorded, at listed prices) | $8.04 (19.6 million tokens, 5,284 evaluations) |
| Hugging Face credit, smoke runs | $0.1408 (Modal smoke $0.1178, local smoke $0.0230) |
| Jev | $0.00028 |
| Modal, smoke-v2 app (billing report, last hour possibly incomplete) | $0.22 |
| Modal, whole tournament (v1 and v2, app ssm-tournament, 3 Oct) | $7.47 |

## Reproduce

```bash
/Users/adriansohrabi/.venvs/ssm/bin/python -m pytest tests -q                 # includes the HF tests (mock only)
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
| `PROTOCOL.md` | Design of the v2 grid with the pre-launch amendment under which full-v2b ran |
| `PROTOCOL-before-amendment.md`, `grids/full-v2-unamended.json` | The protocol and grid before the amendment (renamed from `PROTOCOL 2.md` and `grids/full 2.json`) |
| `runs/full-v2b/` | The 60 runs of the full grid |
| `runs/full-v2/` | Two stopped launches of the unamended grid (spend only; see the amendment) |
| `RESULTS.md` | This file |
| `summary.json` | Headline numbers, machine-readable |
| `smoke_summary.json` | The smoke table above, computed from the run folders |
| `grids/smoke.json`, `grids/full.json` | Smoke grid and the amended full grid (run as full-v2b) |
| `launches/smoke-v2_*.json` | Launch record of the Modal smoke |
| `runs/smoke-v2/<arm>__erdos_squares__s0/`, `runs/local-smoke-v2/` | Per run: `job.json` (with prices), `usage.jsonl`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`, `best_program.py`, `artifacts.tar.gz` |

## Next steps

- Rerun sum-difference with longer wall limits or faster evaluation, so that runs finish their
  budget.
- Add more seeds per cell before claiming any difference between frameworks.

## Suggested README text

> Every tournament arm also runs on open models through the Hugging Face router
> (`"provider": "hf"` in a grid), under the same per-call dollar cap with prices read from the
> router. A DeepSeek-V4.1-Flash call costs about $0.002, so at small budgets the evaluator, not the
> model, sets the pace; `gate_workers` scores instances in parallel.
