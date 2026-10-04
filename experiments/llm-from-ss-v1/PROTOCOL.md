# llm-from-ss-v1: protocol (written and committed before any run)

Written at 05:40 BST on 4 October 2026, before any LLM call of this study. This file is committed on
branch `exp/llm-from-ss` before `run.sh` is started; that commit is the pre-registration timestamp.

## Question

Can 300 steps of the one-command loop (`python -m autoresearch.loop`) find a policy that uses fewer bins than
Sum-of-Squares on unseen instances, when the loop starts from Sum-of-Squares?

Background:
- [online-frontier-v1](../online-frontier-v1/RESULTS.md) (branch `exp/online-frontier`) measured bins above the
  exact optimum on FunSearch's Weibull benchmark (5,000 items):
  - Sum-of-Squares (SS; Csirik et al., JACM 2006): 10–11 bins;
  - FunSearch's evolved heuristic: 13–14 bins.
  SS is the best policy found there that does not use the number of items.
- [llm-long-search-v1](../llm-long-search-v1/RESULTS.md) (in `main`) ran the same loop from best fit for 300
  steps. It reached about 97% of FunSearch's gain over best fit, and SS beat all four runs.
- Session b1's online-beyond-ss-v1 (branch `exp/online-beyond-ss`) reports a fill-weighted SS with a best-fit
  finish (FWSS) at 1.6–2.1 bins above the optimum. FWSS uses the number of items T.

**Secondary question.** Does the loop find a horizon-aware rule such as FWSS's finish? The problem statement
tells the model that each instance has 5,000 items, and `bins` has one entry per item on the first call, so
the horizon is available to the model. That is the same information FWSS uses.

## What the model sees

Problem folder `problems/bin_packing_online_ss`:
- `problem.md`: identical to `problems/bin_packing_online/problem.md`. FunSearch, SS, FWSS and the optimum are
  not mentioned.
- `verify.py`, `evaluate.py`: unchanged copies; the same public instances (seeds 101, 102) and hidden instances
  (901, 902).
- `initial.py`: SS as a stateful `priority(item, bins)`. Its logic is identical to
  `experiments/llm-long-search-v1/references/sum_of_squares.py`; only the docstrings differ. The docstring
  names it "the Sum-of-Squares rule" and describes it neutrally (SHA-256 `15a169ab…`).
- `baselines/`: best fit, FunSearch's Weibull heuristic, and SS. The loop scores these on the same instances;
  the model does not see them.

## Pre-run checks (done before this protocol was committed)

- `check_initial.py` → `check_initial.json`: through the gate's sandbox, `initial.py` gives the same bin counts
  as online-frontier-v1's gap-histogram SS on 5 instances (seeds 84900–84904), 5 of 5 equal.
- The gate's own evaluation of `initial.py` gives public 0.994228 and hidden 0.994996. These equal SS computed
  directly on those instances, so state does not leak between instances: each instance runs in a fresh process.
- `references/arcflow.py` (the arc-flow optimum, extracted verbatim from online-frontier-v1's `frontier.py`)
  proved OPT = L1 = 1963 on seed 84999 in a smoke test. That seed is not in the audit set.

## Runs

- **Settings.** 4 independent runs, seeds 0–3:
  `python -m autoresearch.loop problems/bin_packing_online_ss --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 300 --budget 0.60 --wall 5400 --gate-workers 1 --seed S`
- **System defaults.** The lean loop, the non-regression gate and the integrity gate.
- **Differences from llm-long-search-v1:**
  - The starting program is SS instead of best fit.
  - `--budget` is 0.60 instead of 0.75. Those runs cost about $0.20 each, so the cap is not expected to bind.
  - `--gate-workers` is 1 instead of 2, and at most 3 runs at a time. The machine is shared and CPU is capped at
    3 concurrent processes. This changes wall time only.
- **Spend cap.** $2.50 of Hugging Face credit in total (4 × $0.60), enforced per run by the loop's budget guard.
  No other provider. A billing error stops the study, and it is documented.

## Primary endpoint: fresh audit

- **Instances.** After every run has finished, each run's final `best_program.py` is scored on 100 new
  5,000-item instances: `verify.items_for` seeds 84000–84099. No earlier study uses them; 84000–84999 is
  reserved for this study.
- **Sandbox.** The gate's sandbox (`autoresearch.sandbox.run_online`): a separate process per instance, one item
  at a time.
- **Contrast.** Bins minus SS bins per instance. A 95% paired bootstrap interval over instances (10,000
  resamples, seed 84), with wins/ties/losses.
- **Decision rule.** A run **beats SS** if its interval lies entirely below 0. All 4 runs are reported; none is
  selected after the fact.

## Secondary measures

- **Bins above the exact optimum** on the same 100 instances (arc-flow, `references/arcflow.py`). Reported for
  every program: the 4 runs, SS, best fit, FunSearch's Weibull heuristic, and FWSS (`references/priority_fss.py`,
  copied from commit `47258dc` of `exp/online-beyond-ss`, SHA-256 `ad087d0a…`). FWSS is a disclosed reference:
  it is not searched and not tuned here.
- **Each run against FunSearch's heuristic and against FWSS:** paired intervals as above.
- **Decision agreement** with SS and with FunSearch's heuristic: the share of identical bin choices on the first
  10 audit instances.
- **Horizon use.** For each final program, the decisions on the first 4,000 items of a 4,000-item instance are
  compared with the decisions on those same first 4,000 items of the 5,000-item instance (same seed; the items
  are a prefix). Any difference means the program uses the number of items. Checked on 5 audit seeds
  (84000–84004). The code is also read for uses of `len(bins)` or the constant 5000.
- **From the loop's own report:** steps, accepted improvements, public and hidden scores, the explanation of
  the final program, spend, and wall time.

## Threats to validity

- **Selection.** Selection uses only 2 public instances. The fresh audit measures this.
- **Sample size.** 4 runs is too few to estimate how often a run succeeds.
- **Recall.** The model may recall SS-based or horizon-based rules from the literature.
- **Reproducibility.** Model outputs are not reproducible from the seed.
- **Ceiling.** SS sits about 10 bins above the optimum, so the possible gain without the horizon may be small.
  The 2 public instances may be too noisy to detect a gain of 1–3 bins per instance: SS minus FunSearch varies
  by several bins per instance.

## Files

- `PROTOCOL.md`: this file.
- `RUN_LOG.md`: times and events.
- `run.sh`: launches the runs.
- `audit.py`: the fresh audit, optimum, agreement and horizon checks; writes `audit.json`.
- `report.py`: builds `tables.md` and `summary.json` from `audit.json` and the run folders.
- `RESULTS.md`: the write-up.
- `references/`: `arcflow.py`, `ss_hist.py`, `frontier.py` (full copy, SHA-256 `3b74ed18…`), `priority_fss.py`.
- `check_initial.py`, `check_initial.json`: the pre-run check.
- `runs/s0`–`runs/s3`: the loop's outputs.
