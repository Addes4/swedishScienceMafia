# Tournament: complete autoresearch frameworks at equal dollar budgets

`tournament/` runs whole frameworks against each other on the same problems at the same dollar
budget per run. Each run gets its own Modal container, a hard per-call dollar cap and one shared
evaluation log. Four arms are built in:

| Arm | What it does |
|---|---|
| `shinka` | Stock ShinkaEvolve |
| `lean` | One model proposes and implements a change to the current best each call, and the best valid program is kept. In effect, greedy sequential best-of-N |
| `lean_gate_patience` | `lean`, plus a non-regression gate on archived failing instances and a patience restart rule ([patience.py](patience.py)) |
| `independent` | Every call writes a program from the problem statement and the initial program only, with no history and no parent selection; the best is kept |

Arms can use Claude through the Anthropic API, or open models through the Hugging Face router
(`"provider": "hf"` in a grid, with prices read from the router).

## Results so far

- **[Tournament v1](https://github.com/swedishScienceMafia/swedishScienceMafia/blob/archive/full-research-2026-10-04/experiments/tournament-v1/RESULTS.md)** (Claude, $1.10 per run) is a partial
  study. The API key ran out of credit 13.6 minutes in, so 17 of 60 runs used their full budget.
  - Circle packing and Erdős squares saturate within 1–3 Sonnet calls, so they cannot separate
    frameworks.
  - At a common early spend ($0.10 to $0.30), `lean` (+0.233 area under the score-versus-dollars
    curve, CI [0.096, 0.386]) and `independent` (+0.209) were ahead of ShinkaEvolve. `triage` was
    behind (−0.156).
  - Final scores did not differ.
- **[Tournament v2](../experiments/tournament-v2/RESULTS.md)** ran the full grid on open models (60 runs,
  $8.04). No framework differs significantly from ShinkaEvolve after Holm correction, and the winner
  depends on the problem. Hidden instances caught weak programs. A DeepSeek-V4.1-Flash call costs about
  $0.002, so evaluating programs, not the model, sets the pace.
- The `triage` arm used in both studies was removed from `main` with the triage loop; it is in tag
  `archive/full-research-2026-10-04`.

## Launch a grid on Modal

Prerequisites: `pip install -r requirements.txt` and `modal` authenticated. Live Claude grids
also need the Modal secret `ssm-llm-keys`, created from the git-ignored `.env` with
`modal secret create ssm-llm-keys --from-dotenv .env` (this prints key names only). From the
repository root:

```bash
modal run tournament/modal_app.py --grid experiments/tournament-v1/grids/mock.json --dry-run   # caps and job list
modal run tournament/modal_app.py --grid experiments/tournament-v1/grids/mock.json             # mock API: no cost
modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/full.json    # live
python -m tournament.pull full-v1     # Volume -> experiments/tournament-v1/runs/full-v1/
python -m tournament.report experiments/tournament-v1/runs/full-v1
```

Each job runs `python -m tournament.run --job ...` and writes to the Modal Volume `ssm-tournament`
under `/<grid>/<job_id>/`. Relaunching skips jobs that already have `summary.json`, and
`--only lean,erdos_squares` limits a launch. Live launches refuse uncommitted tracked changes and
stamp the commit on every job.

One job without Modal:

```bash
python -m tournament.run --arm lean --problem erdos_squares --seed 0 --budget 0.5 --mock --out /tmp/lean-check
```

Set `GATE_WORKERS` (or `gate_workers` in a grid) to score a program's instances in parallel. It is
off by default. Turn it on for weaker models, whose programs often run every instance up to its
time limit.

## Add an arm or a problem

A variant is a grid entry, for example `"lean_T8": {"type": "lean", "patience": 8}`. The options
are `DEFAULTS` in `lean.py` and the adapters in `arms.py`. A new framework is one function:

```python
@arm("my_loop")
def my_loop(ctx):                      # tournament.context.Context
    ev = ctx.evaluate(ctx.initial, "initial")
    while not ctx.out_of_time():
        ...                            # any Anthropic SDK call here is budgeted automatically
        ev = ctx.evaluate(code, tag)   # integrity gate + private evaluation log
```

It stops when a call raises `BudgetExhausted` (or its subclass `FatalAPIError`). A problem is a
folder under [problems/](../problems/README.md) named in a grid's `"problems"`.

## How costs are capped

- **Per call.** `guard.py` reserves the worst-case cost before sending, using
  `autoresearch/claude.py` PRICES or the HF router's prices. Actual usage then replaces the
  reservation. Rate limits are retried. Billing and authentication errors stop the run at once.
- **Per job.** `budget_usd` sets the cap. A watchdog ends a job that keeps running past its budget
  or its wall limit, and still writes its summary.
- **Per grid.** The launcher refuses a grid whose job budgets, worst-case Modal cost or recorded
  experiment spend would pass the caps in the grid file.
- **Collected per run:** `usage.jsonl`, `evals.jsonl`, `events.jsonl`, `summary.json`, `curve.csv`,
  `best_program.py`, `stdout.log.gz`, `artifacts.tar.gz`.

## Files

| File | Role |
|---|---|
| `modal_app.py`, `grid.py`, `pull.py` | Launch a grid on Modal, check its caps, pull results back |
| `run.py`, `context.py`, `arms.py`, `lean.py` | One job; what an arm receives; the arm adapters; the lean and independent loops. `autoresearch/loop.py` runs its search as one `run.py` job and wraps `Context.event` to print steps, so changes here affect it |
| `budget.py`, `guard.py`, `hf.py` | Dollar cap, routing every SDK call through it, the Hugging Face router client |
| `evallog.py`, `shinka_eval.py` | One logged integrity-gate evaluation per program |
| `metrics.py`, `report.py` | Curves, area under the curve, paired comparisons, the report |
| `mockapi.py` | A local fake of the Messages API, for zero-cost end-to-end runs |
