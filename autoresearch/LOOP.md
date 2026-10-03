# `autoresearch.loop`: design notes and build log

Built 3 October 2026, 23:39–23:55 BST, on branch `feat/one-command` (PR #4, on top of PR #3), from
a spec the user pasted (verbatim in the [appendix](#appendix-the-spec-as-pasted)). User-facing
documentation: [the root README's Quick start](../README.md#quick-start), [flags and outputs](README.md#one-command-loop),
[demo runs and the live demo plan](../runs/README.md).

## Question and answer

**Question.** Can the pieces that won this project's experiments run as one command that a judge
can understand, run, point at a new problem and reproduce?

**Answer: yes.** `python -m autoresearch.loop <problem folder>` searches, audits the final program
on hidden instances, scores the problem's baselines, explains the program by two-sided ablation and
writes `report.md`. It wraps existing code: `tournament/run.py`, `tournament/lean.py`,
`autoresearch/gate.py`, `tournament/metrics.py`; the new code is `loop.py` (340 lines) and
`explain_code.py` (355 lines, including its CLI and the report section).

- Mock run on Erdős squares: 3.9 s end to end, $0 ([runs/demo-erdos-mock](../runs/demo-erdos-mock/report.md)).
- Live run on online bin packing, 8 steps of DeepSeek-V4.1-Flash: $0.0038, 43 s of search. Nothing
  beat best fit (public 0.9616, hidden 0.9604); FunSearch's heuristics score 0.9925 / 0.9928
  (Weibull) and 0.9699 / 0.9702 (OR) on the same instances ([runs/demo-binpacking](../runs/demo-binpacking/report.md)).
- The ablation on FunSearch's Weibull heuristic keeps `(bins - max_bin_cap) ** 2 / item`, the
  sign flip and the differencing step, and drops the `bins ** 2 / item ** 2` and
  `bins ** 2 / item ** 3` terms (public 0.9925 → 0.9920, hidden 0.9928 → 0.9925; 7 parts, 14
  evaluations, 7 s).
- 182 tests pass (175 before, 7 new in `tests/test_loop.py`).

## Design

| Stage | Code | Default | Evidence for the default |
|---|---|---|---|
| propose + implement | `tournament.run.main` with one job, run locally (not Modal) | `lean`, 12 steps | [tournament-v1](../experiments/tournament-v1/RESULTS.md): lean and independent ahead of ShinkaEvolve and triage at a common early spend (partial, 17 of 60 runs) |
| score | `autoresearch/gate.py` | | [gate-redteam-v1](../experiments/gate-redteam-v1/RESULTS.md): 0 of 68 exploit attempts gained a material unearned score |
| keep | `tournament/lean.py` `Gate` | gate on | [gate-v3](../experiments/gate-v3/RESULTS.md) (counterexample gate beat score-only promotion); as prompt memory the same information mostly produced no-ops ([memory-ablation-v1](../experiments/memory-ablation-v1/RESULTS.md)) |
| audit | `tournament.metrics.summarize` | always | hidden instances caught 0.960 public → 0.238 hidden ([tournament-v2](../experiments/tournament-v2/RESULTS.md)) |
| compare | `problems/<name>/baselines/*.py` through `gate.evaluate` | when the folder exists | [bp-ceiling-v1](../experiments/bp-ceiling-v1/RESULTS.md): cheap baselines can match FunSearch |
| explain | `explain_code.py` | 40 evaluations, ±0.002 | [simplify-v1](../experiments/simplify-v1/EXPERIMENT.md) §4.2: one-sided simplification improved 26 of 43 candidates beyond the tolerance (repairs, not explanations), 21 of them into best fit |
| report | `loop.write_report` | `report.md` | |

Program simplification is standard in genetic programming: Javed, Gobet and Lane, "Simplification
of genetic programs: a literature survey", *Data Mining and Knowledge Discovery* 2022,
[doi:10.1007/s10618-022-00830-7](https://doi.org/10.1007/s10618-022-00830-7). Nothing here claims
the ablation is new; the two-sided check is there so the explanation describes the program found.

## Decisions and deviations from the spec

- **Evidence attribution corrected.** The spec credits the gate default partly to the tournament.
  In tournament-v1 the arm ahead of ShinkaEvolve was plain `lean` *without* the gate; lean with gate
  and patience was +0.195 (Holm p = 0.070). The README credits the gate to gate-v3. The default
  combination (lean + gate, no patience) was never itself a tournament arm.
- **Model id** `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra`, the pinned model and provider of
  tournament-v2's grids. On the HF router a model without `:provider` is refused, because prices
  are read per provider.
- **`--independent`** turns the gate off and refuses `--patience` (`tournament/lean.py` raises on
  either: an independent sample has no parent to regress from and no line to restart).
- **Mock budget** defaults to $0.10 of simulated spend; the mock prices calls like the real API so
  the cap binds. Reports print "$0 real" and the simulated figure separately. The test checks the
  run's `mock` flag rather than a spend of $0.
- **`--wall`** defaults to 3600 s (the spec gave no default). **`--out`** refuses an existing
  non-empty folder; an empty one is accepted.
- **The ablation scores with `gate.evaluate` unchanged**, so every variant also runs on the hidden
  instances. Their hidden scores are never used for a decision; only the minimal program's hidden
  score is reported. A public-only mode would halve the time but would change the red-teamed gate.
- **Greedy order.** Valid single removals by smallest |Δ| first, removals that break the program
  last. Every part is tried once, including parts with a large single effect: a dead store can
  become removable once another part is gone. Parts inside a removed statement are skipped.
- **Terms** are the operands of the left spine of a `+`/`-` chain, so a parenthesised right
  operand stays one term. A removed statement's leftover `pass` is tidied away.
- **Timeouts during the ablation**: max(5 s, 5 × the original's slowest instance), capped at the
  problem's own limit, so a variant that loops forever costs seconds, not minutes.
- **Stored outputs.** Baselines keep their gate results under `baselines/<name>/`; ablation
  variants are scored in a temporary folder and only `explain.json` is kept. No prompts or raw
  responses are stored anywhere.
- **Report** is markdown only (the spec allowed skipping HTML). The baseline column shows the
  baseline's file, where its credit is.
- **Interrupted runs.** After Ctrl-C the analysis is skipped and `--report DIR` finishes it.
  After a hard stop (budget or wall clock) `tournament/run.py` exits the process, so the same applies.
- **Git.** `runs/*` is ignored except `runs/demo-*/` and `runs/README.md`. The latest
  `consolidate-overnight` was merged, not rebased, so commit `0a98446`, recorded in the demo run's
  `job.json`, stays in the history.
- **Demo plan.** The live run kept best fit, which has nothing to ablate, so step 3 of the plan
  shows the ablation on FunSearch's heuristic instead (no cost).

## Work log: bugs and dead ends

| Problem | Fix |
|---|---|
| The terminal step printer first polled `events.jsonl` from a thread every 0.5 s; the last step printed after `tournament.run`'s `[done]` line | `loop.search` wraps `Context.event` for the duration of the run (restored afterwards), so each step prints as it is logged |
| The report listed the search time twice | Stage timings exclude `search_s`; search time comes from `summary.json` |
| Ablation timeout floor of 2 s was tight: the gate's limit includes interpreter start-up and imports, the measured time does not, and instances run in parallel | Floor raised to 5 s |
| `--report` on another machine: `job.json` stores an absolute problem path, so the diff would show the whole program as added | `problem_of()` falls back to `problems/<name>` in the current checkout (`0a98446`) |
| The baseline column cut the credit line off mid-sentence | Shows the baseline's file path |
| The README cited the GP simplification survey from memory | Checked on Crossref; DOI added |

## Limitations

- **One live seed of 8 steps.** It shows the loop working end to end, not what it can reach.
- **The explanation is a single evaluation per variant.** For a program with unseeded randomness
  (e.g. the starting programs of circle packing and Erdős discrepancy), Δ mixes the effect with
  noise and the ±0.002 tolerance can mislabel parts. There are no confidence intervals;
  `falsify/simplify.py` has them for the bin-packing evaluator. Noise in numerical simplification
  is studied by Kinzett, Zhang and Johnston (CEC 2010, doi:10.1109/CEC.2010.5586181).
- **The minimal program is greedy and order-dependent**: a local minimum, not the smallest
  program with the same score. With more parts than the evaluation limit, some parts are reported
  as not tested.
- **Only the problem's function is ablated**, not module-level helpers or constants.
- **The gate archive needs at least two public instances**; on a one-instance problem the default
  keep rule is plain improvement.
- **Baselines exist only for `bin_packing_online`.** Other problems report none.
- **Mock steps say nothing about search quality**: the mock perturbs one constant per step.

## Cost

| Item | Spend |
|---|---|
| Live demo run (HF router) | $0.0038: 8 calls, 8,158 input × $0.20/M + 3,617 output × $0.60/M, recomputed from `runs/demo-binpacking/usage.jsonl`; prices from `job.json` |
| Mock runs, tests, ablations | $0 |
| Citation check (Crossref; OpenAlex was over its free quota) | $0 |

Claude Code agent usage was not metered separately.

## Reproduce and verify

```bash
python -m pytest tests/test_loop.py -q                                   # 7 tests, ~14 s
python -m pytest tests -q                                                # 182 tests, ~80 s
python -m autoresearch.loop problems/erdos_squares --mock --out runs/my-mock
python -m autoresearch.loop problems/bin_packing_online --budget 0.15 --provider hf --max-iters 8 --gate-workers 8 --out runs/my-live
python -m autoresearch.loop --report runs/demo-binpacking                # rebuild a committed report, no LLM calls
python -m autoresearch.explain_code problems/bin_packing_online problems/bin_packing_online/baselines/funsearch_weibull.py
```

## Evidence index

| Path | Contents |
|---|---|
| `autoresearch/loop.py`, `autoresearch/explain_code.py` | The command and the ablation; module docstrings double as `--help` |
| `tests/test_loop.py`, `tests/conftest.py` | End-to-end mock runs, refusal checks, ablation on a hand-written program; the `slow` marker |
| `problems/bin_packing_online/baselines/` | FunSearch's OR and Weibull heuristics, verbatim, Apache-2.0 |
| `runs/demo-binpacking/`, `runs/demo-erdos-mock/` | The two committed runs: `report.md`, logs, `job.json` with source hashes |
| `runs/README.md` | What the runs show, and the 1:30 live demo plan |
| `experiments/OVERNIGHT-2026-10-03.md` | Timeline entry (23:39), spend ledger row, open-work row |

## Next steps

- Several seeds of a longer live run on Weibull 5k, e.g. 5 seeds × 30 steps (about $0.08 at the
  observed $0.0005 per step), to measure what the default loop reaches against the baselines.
- Repeated evaluations, or fixed seeds, for stochastic programs in the ablation, with intervals.
- Ablate module-level helpers the function calls.
- Add `baselines/` for the other problems (for example the best published constructions).
- Bring `--patience` (Strategist) or triage into the defaults only after a complete,
  budget-matched comparison inside the LLM loop.

## Appendix: the spec as pasted

Recorded verbatim, as the coordination log records the Devin task, with one edit: the Explain row
cited a second figure next to 21/43 that has no source in the repo, so it was removed. The source
for the repair finding is [simplify-v1](../experiments/simplify-v1/EXPERIMENT.md) §4.2: 26 of 43
candidates improved beyond the tolerance, 21 of them into best fit.

````markdown
# Spec: one command that runs the whole research loop

Audience: the Claude Code agents building this before the 10:30 code freeze (Sun 4 Oct).
Base branch: `consolidate-overnight` (PR #3). Work on a new branch `feat/one-command`, small commits.
Hard limit: about 4 hours of building. No new experiments. Default to wiring, not new research code.

## Why

The track brief (`context/Instructions/…pdf`) asks for "a system that can discover good algorithms",
"a reusable research system rather than … hard-coded to one benchmark", with install/run
instructions, a high-level design, and integrated benchmark examples. It judges ease of use
("understand, run, and apply to new problems … reproduce experiments") and research efficiency.
The event judging gives Demo 20/100 with a 1:30 **live** demo. Today the repo needs eight commands.

The pitch for the design: **every default in this command is whatever won one of our controlled
experiments**, and every option the experiments did not support is still available as a flag.

| Stage | Default | Evidence for the default |
|---|---|---|
| Propose + implement | `lean` loop (one call per step, edits the incumbent) | tournament-v1: lean/independent beat ShinkaEvolve and triage on early AUC (partial, 17/60) |
| Score | `autoresearch/gate.py` (separate process, static scan, strict recheck, hidden instances) | gate-redteam: 0/68 exploit attempts gained a material unearned score |
| Keep | improvement on public score + non-regression archive (`gate: true`) | Falsify gates; memory-ablation: archive as a **gate**, not prompt memory (prompt memory made the model timid) |
| Fresh audit | hidden-instance score of the final incumbent, never used for selection | caught 0.960 public → 0.238 hidden (tournament-v2 smoke); caught Codex 1/0 → 3/14 overfit |
| Explain | two-sided ablation of the winning program's statements | repair finding: one-sided simplification produced false "rediscovered best-fit" claims (21/43) |
| Compare | score the problem's baselines on the same public+hidden instances | bp-ceiling: cheap baselines can match FunSearch; any gain must be stated against them |

Not default (flags only): `--patience T` (Strategist restart rule), `--independent`, triage
(`autoresearch.triage`), prompt memory. Say in the README why they are off.

## The command

```
python -m autoresearch.loop problems/bin_packing_online --budget 0.10 --provider hf
python -m autoresearch.loop problems/erdos_squares --mock          # no network, no cost
python -m autoresearch.loop --report runs/<dir>                    # rebuild the report of a saved run
```

Flags (keep it short): `--budget USD` (hard cap, required unless `--mock`), `--provider hf|anthropic`
(default `hf`; Anthropic credit is exhausted), `--model` (default HF `deepseek-ai/DeepSeek-V4.1-Flash`
— use the exact id string from `experiments/tournament-v2/`), `--max-iters N` (default 12),
`--wall S`, `--seed`, `--out DIR` (default `runs/<problem>-<timestamp>`, refuse to overwrite),
`--no-gate`, `--patience T`, `--independent`, `--gate-workers N` (default `os.cpu_count()`),
`--explain-evals N` (default 40), `--mock`.

## Implementation: wrap what exists, do not rewrite it

New file `autoresearch/loop.py` (~200–300 lines) plus `autoresearch/explain_code.py` (~120 lines).

1. **Search** — build a job dict and call `tournament.run.main([...--job json...])` exactly as
   tournament-v2 did locally (`provider`, `hf_models`, `gate_workers`, `budget`, `wall_limit_s`,
   `mock`, arm `lean` with config `{"gate": true, "max_iters": N, "model": ..., "patience": T or null}`).
   This already gives: hard budget (`tournament/budget.py`), fatal 401/402/403 handling, mock API,
   `events.jsonl`, `evals.jsonl` (incl. hidden scores), `best_program.py`, `summary.json`.
   Do NOT go through `tournament/modal_app.py` (needs committed tree + Modal). Local only.
2. **Audit** — `tournament.metrics.summarize(run_dir)` already returns `initial_public`,
   `initial_hidden`, `final_public`, `final_hidden`. Report the public→hidden gap; flag
   `OVERFIT?` if `final_hidden < initial_hidden` while `final_public > initial_public`.
3. **Baselines** — new optional folder `problems/<name>/baselines/*.py`, each a normal candidate
   program. Score each with the same gate (`autoresearch.gate.evaluate`) and report public+hidden.
   For `bin_packing_online` copy `experiments/bp-ceiling-v1/programs/funsearch_weibull.py` and
   `funsearch_or.py` (credit FunSearch, Apache-2.0; best-fit is already `initial.py`).
   Missing folder → skip silently. This keeps the framework problem-agnostic.
4. **Explain (two-sided ablation)** — `explain_code.py`:
   - parse `best_program.py` with `ast`; find the function named `verify.FUNCTION`;
   - candidates = each statement in its body (recursively into if/for bodies) except the final
     `return`; also each operand of a top-level `+`/`-` chain in `return`/assignment expressions;
   - for each candidate, delete it (replace by `pass`, or drop the term), `ast.unparse`, score on
     **public** instances via the gate; record Δ score;
   - greedy minimal program: drop parts one by one, accept only if `|score - original| <= tol`
     (two-sided, default `tol = 0.002` of the normalised score); stop at `--explain-evals`;
   - score the minimal program on hidden too; report "parts that matter" (largest |Δ|), "parts
     that can go", and the minimal program. Never call a one-sided "better after removal" result
     an explanation: label it `REPAIRED (not an explanation)`.
   - If parsing fails or the function is a single expression, skip with a note.
5. **Report** — `report.md` (and `report.html` if trivial; markdown is enough) in the run dir:
   problem, model, spend, wall time; score table (initial / final / baselines × public / hidden);
   step log (iter, outcome, score, cost) from `events.jsonl`; diff `initial.py` → `best_program.py`;
   explanation section; reproduction command line; git commit and source hashes (already in `job.json`).
   Print a 10-line summary to the terminal at the end.

## Tests (pytest, all offline)

`tests/test_loop.py`:
- `--mock` end-to-end on `erdos_squares` (fast) writes `report.md`, `summary.json`, `best_program.py`,
  spends $0, and the report contains public and hidden columns;
- `--mock` on `bin_packing_online` with `--max-iters 2` scores baselines (skip if too slow; mark `slow`);
- `explain_code` on a hand-written priority with one dead statement and one essential one: the
  dead one is removed, the essential one is kept, and a "removal improves score" case is labelled
  `REPAIRED`;
- refuses to run live without `--budget`; refuses to overwrite `--out`.
Full suite must still pass (currently 175).

## README and docs

- Root README: new first section **Quick start** with the three commands above, then a 6-line
  "What one run does" list (the table above, compressed), then "Add a problem" (point to
  `problems/README.md`, mention optional `baselines/`).
- `autoresearch/README.md`: document `loop.py` flags and outputs.
- Keep claims narrow: no "beats best-fit", no "new" for simplification (GP literature: Javed et al.
  2022) — say "two-sided check so the explanation describes the program actually found".

## Demo assets (commit before 10:30)

1. One real run: `python -m autoresearch.loop problems/bin_packing_online --budget 0.15 --provider hf
   --max-iters 8 --gate-workers 8 --out runs/demo-binpacking` (≈ $0.02–0.10 of HF credit). Commit
   the run dir **except** any raw request/response files (check for `calls/`; keep `.gitignore` rules).
   Scan for `hf_`, `sk-` before committing.
2. One mock run on `erdos_squares` committed the same way (shows the second benchmark).
3. Live demo plan (1:30): start the bin-packing command live with `--max-iters 3` (first steps
   stream to the terminal), then open the committed `runs/demo-binpacking/report.md` to show the
   full result while it runs. If the network fails, run `--mock`.

## Out of scope tonight

Strategist integration beyond `--patience`, triage integration, prompt memory, Modal backend,
new problems, any paid run beyond the demo run, HTML dashboards.

## Acceptance checklist

- [ ] `python -m autoresearch.loop problems/erdos_squares --mock` finishes < 60 s and writes report.md
- [ ] live bin-packing demo run committed, spend recorded, no secrets
- [ ] `pytest -q` green
- [ ] README Quick start is the first thing a judge sees
- [ ] pushed and added to PR #3 (or a PR on top of it) before 10:30
````
