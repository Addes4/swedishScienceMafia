# Autoresearch: the one-command loop, the integrity gate and triage

## One-command loop

```bash
python -m autoresearch.loop problems/bin_packing_online --budget 0.10 --provider hf
python -m autoresearch.loop problems/erdos_squares --mock          # no network, no cost
python -m autoresearch.loop --report runs/<dir>                    # rebuild the report of a saved run
```

`loop.py` wraps code that already exists and was tested in the overnight experiments. It does not
reimplement any of it:

| Stage | What runs | Default |
|---|---|---|
| search | `tournament.run.main` with one job (local, no Modal): the `lean` arm of `tournament/lean.py`, the hard dollar cap of `tournament/budget.py`, fatal handling of 401/402/403, the mock API | lean, gate on, 12 steps |
| score | `autoresearch/gate.py` on every candidate (public scores are used for selection; hidden scores go only to `evals.jsonl`) | |
| audit | `tournament.metrics.summarize`: initial and final incumbent on public and hidden instances; `OVERFIT?` if public rose and hidden fell | |
| compare | `problems/<name>/baselines/*.py`, each scored by the same gate; a missing folder is skipped | |
| explain | `explain_code.py`: two-sided ablation of the final program (below) | 40 evaluations |
| report | `report.md`, plus a 10-line summary in the terminal | |

| Flag | Meaning |
|---|---|
| `--budget USD` | hard cap on LLM spend; required unless `--mock` (mock runs default to $0.10 of simulated spend) |
| `--provider hf\|anthropic` | `hf` (default): Hugging Face router, token from `HF_TOKEN` or `~/.cache/huggingface/token`; `anthropic`: `ANTHROPIC_API_KEY` |
| `--model` | default `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` (tournament-v2's pinned model and provider) or `claude-sonnet-5-5` |
| `--max-iters N` | LLM steps (default 12) |
| `--wall S` | wall-clock limit of the search in seconds (default 3600) |
| `--seed` | recorded with the run; seeds the mock API |
| `--out DIR` | default `runs/<problem>-<timestamp>`; an existing non-empty folder is never overwritten |
| `--no-gate` | keep any public improvement, without the non-regression archive |
| `--patience T` | restart from a fresh program after T non-improving steps (Strategist's Patience rule) |
| `--independent` | independent sampling: every call starts from the problem and `initial.py`, no history, no gate |
| `--gate-workers N` | instances scored in parallel (default: all cores) |
| `--explain-evals N` | evaluations for the ablation (default 40; 0 skips it) |
| `--mock` | local mock API: no network, no cost |

Outputs in the run folder: `job.json` (config, git commit, SHA-256 of every source file, model
prices), `usage.jsonl` (every LLM call and its cost), `events.jsonl` (every step: operation, outcome,
score, the model's own one-line description of its change), `evals.jsonl` (every evaluation with
hidden scores), `summary.json`, `curve.csv`, `best_program.py`, `artifacts.tar.gz` (every candidate
and its gate results), `loop.json` (the command and stage timings), `baselines.json` and
`baselines/<name>/` (gate results), `explain.json` and `report.md`. No prompts or raw responses are
stored. If a run is stopped from outside (a budget or wall-clock hard stop, Ctrl-C),
`--report DIR` finishes the baselines and the explanation without any LLM call.

### Explanation by two-sided ablation (`explain_code.py`)

The parts of the final program are the statements in the body of the problem's function
(`verify.FUNCTION`), searched into if/for/while/with/try bodies and nested functions, except each
function's final `return`, plus each operand of a top-level `+`/`-` chain in a return or assignment.
Each part is removed on its own and the variant is scored by the gate on the public instances. Then
parts are removed greedily, smallest single effect first, and a removal is kept only if the public
score stays within ±0.002 of the original **on both sides**. A removal that raises the score is a
repair of the program, not an explanation of it, and is labelled `REPAIRED (not an explanation)`.
The minimal program is also scored on the hidden instances. Variants that run more than five times
longer than the original count as failures. Only the function is ablated, not module-level helpers.

```bash
python -m autoresearch.explain_code problems/bin_packing_online problems/bin_packing_online/baselines/funsearch_weibull.py
```

On FunSearch's Weibull heuristic this keeps `(bins - max_bin_cap) ** 2 / item`, the sign flip and
the differencing step, and drops the `bins ** 2 / item ** 2` and `bins ** 2 / item ** 3` terms
(public 0.9925 → 0.9920, hidden 0.9928 → 0.9925).
Simplifying evolved programs is standard in genetic programming (survey: Javed, Gobet and Lane
2022, [doi:10.1007/s10618-022-00830-7](https://doi.org/10.1007/s10618-022-00830-7)); the two-sided
check is there so the explanation describes the program actually found.

Design decisions, deviations from the spec, bugs fixed, limitations and the spec itself:
[LOOP.md](LOOP.md).

## Triage: System 1 decides where to look, System 2 does the work

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

## What we found: the idea table

The comparison above was not run as planned, because credit ran out. Instead,
[experiments/idea-table-v1](../experiments/idea-table-v1/RESULTS.md) answered the ranking question
offline.
- **Method:** every idea was implemented by every model, and each program was scored by the
  integrity gate. `python -m autoresearch.ideatable` builds the table, with spend hard-capped and
  resumable steps.
- **Replaying policies:** `python -m autoresearch.policy_eval <folder>` replays any ranker or
  routing policy against the saved table, with bootstrap intervals. A new ranker is scored at
  zero implementation cost with `--extra-rankings`.

On Erdős squares, using the 62 ideas complete for all three models:
- **The model decided success, not the idea.** Opus improved the program on 62/62 ideas, Sonnet
  on 60/62, Haiku on 10/62.
- **Ranker AUC for predicting success:** Codex 0.600, Claude Opus 0.564, Claude Haiku 0.516,
  Jev 0.484, random 0.499. Codex and Opus mainly predicted which ideas Haiku could implement.
- **No ranker made triage beat random tiers.** Sonnet on every idea gave the best result per
  dollar: 60 improvements for $4.00.

So do not claim that triage's thirds split or Jev add value on this problem. A rerun needs a
starting program or problem where strong models do not always succeed. The
[tournament](../tournament/README.md) compares triage with other complete frameworks.

## Red-team of the integrity gate

[experiments/gate-redteam-v1](../experiments/gate-redteam-v1/RESULTS.md) ran 28 hand-crafted
exploits and 40 live attempts by Sonnet and Haiku through the real `gate.evaluate` path. None
obtained a materially unearned score.
- **Where the protection comes from:** the separate process and JSON boundary, which strips lying
  objects, monkeypatching and import tricks; stripped credentials; and the record-triggered
  1e-12 strict re-check, which catches overlaps hidden inside the tolerance.
- **The weak layer:** the static text scan is defence in depth only, and can be bypassed.

The gate isolates an honest loop; it is not a security sandbox. The gate also has an online mode
for problems like [bin_packing_online](../problems/bin_packing_online/), where the candidate is
called once per arriving item. It can score instances in parallel with `GATE_WORKERS`.

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
| `loop.py` | the one-command loop: search, audit, baselines, explanation, report |
| `explain_code.py` | two-sided ablation of a program's statements and sum terms |
| `LOOP.md` | design notes and build log of `loop.py` and `explain_code.py` |
| `triage.py` | the triage loop and CLI |
| `rankers.py` | Jev, Claude and random rankers |
| `claude.py` | idea proposal and implementation calls, prompts, cost accounting |
| `analyze.py` | run summaries, comparison table, cost curve, research notebook |
| `gate.py`, `sandbox.py` | integrity gate: scoring in a separate process, exploit checks |
| `run.py`, `shinka_compat.py` | stock ShinkaEvolve baseline on the same problems |
| `check.py` | score any program on a problem without an LLM |
| `env.py` | loads `.env` |
| `spend.py` | hard spend cap: refuses any call whose worst-case cost could pass the cap; stops on billing errors |
| `ideatable.py`, `policy_eval.py` | the counterfactual idea table, and offline replay of rankers and triage policies |
| `evalcode.py`, `modal_eval.py` | score one program with the gate, locally or in its own Modal container |
| `mock_claude.py` | a deterministic stand-in for the Claude client, for tests and dry runs |

Problems live in `../problems/` (see its README for the contract).
