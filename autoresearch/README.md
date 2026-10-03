# Triage: System 1 decides where to look, System 2 does the work

Every idea gets tested — "stupid" experiments included — but the budget follows promise.
A fast decision model (Jev, by TypeSafe AI) ranks every idea in milliseconds before any code
is written; favourites are implemented by the strongest Claude model, long shots by the cheapest.

```
Claude Opus proposes K ideas  ->  Jev ranks each one  ->  sort, split into thirds
   favourites -> claude-opus-5-5      middle -> claude-sonnet-5-5      long shots -> claude-haiku-4-5
   (15% of assignments swapped at random)
every idea is implemented and scored by the integrity gate  ->  log.jsonl, notebook.md
a cheap model's improvement is "promoted": Opus refines it
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then put your TYPESAFE_API_KEY (Jev) and ANTHROPIC_API_KEY in .env
```

`.env` is git-ignored. Jev is called through the official `typesafe-sdk`
(`POST https://api.typesafe.ai/v1/systemone`).

## Run

```bash
python -m autoresearch.triage problems/erdos_squares --rounds 10 --budget 10     # Jev triage
python -m autoresearch.analyze results/triage_*/log.jsonl                         # compare runs
```

Each run writes `results/triage_<problem>_<ranker>_<time>/`:
`log.jsonl` (every proposal, ranking, implementation and cost), `notebook.md` (readable research
log), `summary.json`, `best_program.py`, and every program with its gate results under `programs/`.

## The experiment (same problem, same dollar budget, 3 seeds each)

| Run | Command flags | What it answers |
|---|---|---|
| Jev triage | `--ranker jev` | the system |
| Random triage | `--ranker random` | same model mix, random assignment: does the *ranking* matter? |
| Claude ranker | `--ranker claude` | System 2 ranker: is Jev's speed and price worth any accuracy loss? |
| All Opus | `--uniform claude-opus-5-5` | the expensive way: how much does triage save? |
| All Haiku | `--uniform claude-haiku-4-5` | the cheap way: what does triage buy over it? |

Use `--seed 0/1/2` and the same `--budget` for every run. What `analyze` reports:

- **best score vs dollars** (`--curve curve.csv` for plotting): the headline.
- **AUC**: chance that an idea which improved was ranked above one that did not (0.5 = no better than random).
- **success rate by planned tier**: favourites should beat long shots if the ranking means anything.
- **swaps**: a long shot that succeeds on Opus means the ranker undervalued it; a favourite that fails on
  Haiku separates "bad idea" from "weak implementer". Swaps also keep the measurement honest.
- **Brier score** of Jev's P(improve): calibration.
- **promotions**: how often a cheap model's find is pushed further by Opus.

## What each ranker is asked (one Jev call per idea)

| Question | Type | Used for |
|---|---|---|
| How promising is the idea for beating the current best? | Choice: favourite / middle / long_shot | tier |
| Will implementing it beat the current best program? | Noul (probability) | tie-breaks, calibration |
| Is it essentially an idea that already failed? | Noul | penalty (dead-end filter) |
| What kind of change is it? | Choice | research log |

The state Jev sees: the problem statement, the current best program and score, the last 20 ideas
with outcomes, and the idea. Independent studies found Jev's probabilities can tie when used as a
sort key, which is why the tier comes from a Choice question and P(improve) only breaks ties.

## Files

| File | Role |
|---|---|
| `triage.py` | the loop and CLI |
| `rankers.py` | Jev, Claude and random rankers |
| `claude.py` | idea proposal and implementation calls, prompts, cost accounting |
| `analyze.py` | run summaries, comparison table, cost curve, research notebook |
| `gate.py`, `sandbox.py` | integrity gate: scoring in a separate process, exploit checks |
| `run.py`, `shinka_compat.py` | stock ShinkaEvolve baseline on the same problems |
| `check.py` | score any program on a problem without an LLM |
| `env.py` | loads `.env` |

Problems live in `../problems/` (see its README for the contract).
