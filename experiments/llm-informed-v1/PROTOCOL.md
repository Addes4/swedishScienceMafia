# llm-informed-v1: does an LLM loop find SS- or FWSS-like rules when told what it may know?

Written on 4 October 2026 before any run of this study. It is committed before the first run; that
commit is the timestamp.

## Question

[llm-long-search-v1](../llm-long-search-v1/RESULTS.md) ran the one-command loop for 300 steps of
DeepSeek-V4.1-Flash on `problems/bin_packing_online`. That problem statement already allows state.
- **What it found:** rules that beat best fit but stopped short of FunSearch's heuristic (best run 0.81%
  over L2 on 100 fresh instances).
- **What it missed:** it found neither Sum-of-Squares (SS, 0.53%) nor FWSS (online-beyond-ss-v1,
  about 0.11%).

FWSS's gains come from two pieces of information that FunSearch-style heuristics never use: the full
state of every open bin, and the number of items. So the question is:

**If the problem statement only spells out what the function can know, without naming any algorithm,
does the same loop with the same budget find rules that beat FunSearch's heuristic, reach SS, or reach
FWSS?**

## Design

- **Problem:** `problems/bin_packing_online_informed`. It is identical to `problems/bin_packing_online`
  (verify.py, instances, scoring, initial best-fit program, time limit), with one addition at the end of
  `problem.md`: the paragraph "What your function can know".
  - **What the paragraph states:**
    - `len(bins)` on an instance's first call is the number of items;
    - the function can track every open bin by recording its own choices;
    - it knows past sizes and how many items remain;
    - each instance runs in a fresh process.
  - **What it leaves out:** no algorithm, objective, weighting or end-game rule is named.
  - **Baselines:** SS and FWSS are added to the folder's `baselines/`, which the loop scores for the
    report but never shows the model.
- **System, model and settings:** exactly those of llm-long-search-v1.
  - `python -m autoresearch.loop` with defaults: the lean loop, the non-regression gate and the
    integrity gate.
  - Model: `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` through the Hugging Face router.
  - 300 steps per run, `--gate-workers 2`, `--wall 5400`.
- **Runs:** 4 independent runs, seeds 0–3, in parallel.
- **Spend cap:** `--budget 0.35` per run, so at most $1.40 in total (approved by the user: about $1).
  llm-long-search-v1 spent $0.19–0.21 per run.
- **Comparator arm:** llm-long-search-v1's 4 runs (uninformed prompt, same model, same settings). They
  were not run at the same time, and the loop code may have changed since (commit adb7fe9 → this
  commit). This is a disclosed limitation.

## Primary endpoint: fresh audit

- **Instances:** the same 100 fresh instances as llm-long-search-v1, `verify.items_for(seed, 5000)` for
  seeds 30000–30099. No run of either study selected on them.
- **Sandbox:** the integrity gate's sandbox (`autoresearch.sandbox.run_online`), a fresh process per
  instance.
- **Programs audited, all in the same run of `audit.py`:**
  - the 4 informed final programs;
  - the 4 uninformed final programs from llm-long-search-v1;
  - best fit, FunSearch's Weibull heuristic, SS and FWSS.
- **Metric:** excess over the L2 bound (%), as in llm-long-search-v1.
- **Statistics:** paired bootstrap intervals over instances (10,000 resamples, seed 739) for each run
  against FunSearch, SS and FWSS.
- **Positive control:** the re-audited uninformed runs and the references must reproduce
  llm-long-search-v1's `audit.json` exactly (same bins per instance).

**Pre-registered questions (each answered per run, then as a count of 4):**
1. **Q1.** Does the run beat FunSearch's heuristic? Its interval for (run − FS-W) must lie below 0.
2. **Q2.** Does it reach SS? Its interval for (run − SS) must lie at or below 0, meaning it is not worse
   than SS.
3. **Q3.** Does it reach FWSS? Its interval for (run − FWSS) must include or lie below 0.
4. **Q4 (informed vs uninformed).** Compare the best of 4 and the mean of 4 fresh-audit excess. With 4
   runs per arm this is descriptive. We also report the exact permutation p-value for the difference in
   means over runs (70 permutations).

## Secondary: what the programs do

Each final program is classified by reading its code, with these rules fixed now:
- (a) **uses the item count:** it reads `len(bins)` on the first call, or an equivalent, and the number
  of remaining items changes its decisions;
- (b) **tracks every open bin:** it keeps the remaining capacity of open bins the item does not fit in;
- (c) **SS-like objective:** it scores placements by a convex penalty on the number of open bins per gap
  (or per gap class);
- (d) **end-game rule:** its decision rule changes as the end of the sequence approaches.

Also reported:
- **decision agreement** with SS and with FWSS on the first 10 audit instances: the share of identical
  bin choices, computed as llm-long-search-v1 computes agreement with FunSearch;
- the loop's own report (`report.md`), with its hidden-instance audit, baselines and two-sided
  explanation.

## Expectations stated in advance

- Uninformed runs reached 96.8% of FunSearch's gain over best fit. With the information spelled out, we
  expect some runs to track open bins and use the item count.
- We expect at least one run to beat FunSearch (Q1) and fewer to reach SS (Q2). Reaching FWSS (Q3) is
  unlikely within 300 cheap steps.
- These are guesses. They are written down so the outcome can be judged against them.

## What will not be claimed

- Nothing about other models, budgets or prompts.
- With 4 runs per arm, informed vs uninformed is descriptive.
- A run that reaches FWSS's level would show that the information is sufficient for this model at this
  budget. It would not show that the model "knows" SS.

## Files

- `PROTOCOL.md`: this file.
- `run.sh`: launches the 4 runs.
- `audit.py`: writes `audit.json`.
- `RESULTS.md`: the write-up, with `summary.json` and `classification.md` (the code reading).
- `runs/s0..s3/`: everything the loop writes.
