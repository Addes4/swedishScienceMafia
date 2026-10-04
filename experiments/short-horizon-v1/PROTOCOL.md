# short-horizon-v1: protocol (committed before any run)

Written at about 05:45 BST on 4 October 2026, before any LLM call of this study. The pre-run checks in
`sanity.json` (CPU only, no LLM) were run first; they are described below.

## Question

Do short selection instances, or short counterexample streams used as a gate, steer an LLM search loop
toward myopic online bin-packing rules that do worse on the long streams the rule is meant for?

## Background

- **The rank reversal itself is known.** Herrmann & Pallez (arXiv 2510.27353) and Burke, Hyde, Kendall &
  Woodward (CEC 2007, doi 10.1109/CEC.2007.4424789) show it, and our bp-ceiling-v1 length sweep measures
  it: FunSearch's Weibull heuristic is 20.5 pp worse than best fit at 80 items and 3.3 pp better at
  5,000. The literature check (`context/research-directions.md` §5 on branch `docs/research-directions`)
  found no study of how this changes what an LLM loop *selects*, and none of a bias from short
  counterexamples.
- **The replay evidence that motivates the gate arms** comes from overfit-gates-v1 (branch
  `exp/overfit-gates`). Replaying memory-ablation-v1's proposals, a strict counterexample veto, a random
  veto and a soft gate all blocked the best run. The archive veto behaved like a random veto of the same
  input lengths. 554 of its 635 archived inputs are 2 items long. That was a replay; this study is live.

## Arms

Every arm is the one-command loop (`python -m autoresearch.loop`) with its defaults: the lean loop, the
non-regression gate and the integrity gate. All arms share:
- the model, `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` on the Hugging Face router;
- 150 steps per run and a $0.20 cap per run;
- the same `problem.md`, which states that the rule will be used on long 5,000-item streams and that
  evaluation instances are shown in the feedback;
- the same initial program (best fit);
- the same hidden instances: 2 × 5,000 items, seeds 85900–85901, never used for selection.

Arms differ only in the public (selection) instances:

| Arm | Folder | Public instances | Items per evaluation |
|---|---|---|---|
| A (control) | `problems/bp_sh_a5000` | 2 × one 5,000-item stream (seeds 85500–85501) | 10,000 |
| B | `problems/bp_sh_b200` | 2 × 25 streams of 200 items (seeds 85600–85649) | 10,000 |
| C | `problems/bp_sh_c80` | 2 × 63/62 streams of 80 items (seeds 85700–85824) | 10,000 |
| D | `problems/bp_sh_d_cex` | A plus a check suite: the 519 unique counterexamples mined in memory-ablation-v1 (438 are 2 items long) | 10,000 + 1,197 |
| E | `problems/bp_sh_e_rand` | A plus a check suite of 519 random streams with the same lengths (seeds 86000–86518) | 10,000 + 1,197 |

**Suite score.** A suite's score is 1 − 1e-8 × (streams where the rule uses more bins than best fit). This
changes the mean score by at most 1.7e-6, which is less than 1% of one bin on a 5,000-item instance. So
the suite acts almost only through the loop's non-regression gate. Once any candidate regresses on the
suite, later candidates may not lose on more suite streams than their parent. Starting from best fit,
which loses on none, that is Falsify's strict veto.

**Fresh state per stream.** In multi-stream instances the trusted driver re-executes the candidate
module for every stream. Bins and module state therefore start fresh, as if each stream ran in its own
process. `sanity.json` confirms this: the gate's Sum-of-Squares score on arm B equals an independent
per-stream simulation exactly.

## Runs

- 4 seeds per arm (0–3), 20 runs in all.
- At most 4 runs at a time, interleaved by seed then arm, with `--gate-workers 1`, `--max-iters 150`,
  `--budget 0.20` and `--wall 5400`.
- **Spend:** at most 20 × $0.20 = $4.00 of Hugging Face credit, enforced per run by the loop's budget
  guard. On a billing error the study stops and is documented. No other provider is used.

## Primary endpoint

- **Fresh audit:** each run's final `best_program.py`, plus best fit, FunSearch's two heuristics and
  Sum-of-Squares, on 100 new 5,000-item instances (seeds 85000–85099). Programs run in the gate's sandbox
  (`autoresearch.sandbox.run_online`, single-stream driver of `problems/bin_packing_online`).
- **Metric:** excess over the L2 bound in percent, and its difference from best fit (pp) on the same
  instances. The per-run value is its mean over the 100 instances.
- **Primary contrasts:** B − A and C − A, the difference in arm means of the per-run Δ vs best fit.
  Each is reported with:
  - a 95% bootstrap interval resampling runs within each arm (10,000 resamples, seed 20261004);
  - an exact two-sided permutation p-value over the 70 splits of 8 runs;
  - Holm correction over the two contrasts.
- **Prediction, stated before the runs:** B − A > 0 and C − A > 0. Selecting on short instances ends
  nearer best fit, or worse than it, on 5,000-item streams.

## Secondary endpoints

- **D − E:** the counterexample suite against the length-matched random suite. A difference near 0
  would mean the length, not the counterexample content, drives the veto. D − A and E − A are also
  reported.
- **Myopia score of each final program:** the share of placements on the first 10 audit instances that
  open a new bin while an open bin has room.
- **Proxy fidelity:** Kendall's τ, per run, between each valid candidate's public score and its hidden
  (5,000-item) score, from `evals.jsonl`. Reported as the arm mean.
- **Long-horizon errors of selection,** per run:
  - rejections (not better, or gate-rejected) of candidates whose hidden score beat the incumbent's at
    that step;
  - promotions whose hidden score fell below the previous incumbent's.
- The loop's own report: hidden score of the final program, spend, steps.

## Threats to validity

- **Few runs:** 4 runs per arm. Most of the variance between runs comes from the model, which is not
  reproducible from the seed.
- **Different public seeds:** arm B and C public instances have different seeds from arm A. Every arm
  shares the generator and the hidden and fresh instances.
- **Generation as well as selection:** the feedback labels truthfully name the stream lengths, so the
  model may also propose differently. `problem.md` is identical in every arm, so the stated goal is the
  same.
- **Fixed suites:** the D and E suites are fixed, not mined live from the run. D's counterexamples were
  mined from Claude Haiku runs in memory-ablation-v1.
- **Module re-execution per stream** costs a little time. It is the same in every multi-stream arm and
  is far below the 60 s per-instance limit for the reference programs (`sanity.json`: 1.1–5.2 s per
  evaluation).

## Files

- `PROTOCOL.md`: this file.
- `make_problems.py`: generates the 5 problem folders and the suites.
- `cex_source_archive_inputs.json`: a copy of overfit-gates-v1's archive.
- `sanity.py`, `sanity.json`: pre-run checks.
- `run.sh`: launches the 20 runs.
- `runs/<arm>-s<seed>/`: the loop's output.
- `audit.py`: produces `audit.json`.
- `analyze.py`: produces `summary.json` and `tables.md`.
- `RESULTS.md`, `RUN_LOG.md`.
