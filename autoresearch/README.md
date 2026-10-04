# Autoresearch: the one-command loop and the integrity gate

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
| `--patience T` | restart from a fresh program after T non-improving steps (a simple patience rule; the adaptive Strategist controller was dropped) |
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

## Files

| File | Role |
|---|---|
| `loop.py` | the one-command loop: search, audit, baselines, explanation, report |
| `explain_code.py` | two-sided ablation of a program's statements and sum terms |
| `LOOP.md` | design notes and build log of `loop.py` and `explain_code.py` |
| `gate.py`, `sandbox.py` | integrity gate: scoring in a separate process, exploit checks |
| `claude.py` | Anthropic client, prompts and cost accounting used by the search arms |
| `run.py`, `shinka_compat.py` | stock ShinkaEvolve, the external baseline in the tournament |
| `check.py` | score any program on a problem without an LLM |
| `env.py` | loads `.env` |

The search arms and the spend cap live in [../tournament/](../tournament/README.md). Problems live in
`../problems/` (see its README for the contract).

Idea triage (a cheap model ranking ideas for an expensive one), its rankers and the idea table were
removed from `main` after the [idea table](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/idea-table-v1)
showed ranking ideas did not beat random tiers. The code is in tag `archive/full-research-2026-10-04`.
