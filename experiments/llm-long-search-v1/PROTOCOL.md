# llm-long-search-v1: protocol (written before the first run)

Written at 01:20 BST on 4 October 2026, before any run of this study.

## Question

With a few hundred calls to an inexpensive open model, does the one-command loop
(`python -m autoresearch.loop`) beat best-fit on online bin packing with 5,000 Weibull items? How close
does it get to FunSearch's published heuristic?

Background: [bp-ceiling-v1](../bp-ceiling-v1/RESULTS.md) showed that on these instances a 21-weight
linear rule tuned on CPU reaches −3.28 pp of excess over the L2 bound relative to best-fit, and
FunSearch's heuristic −3.33 pp. The LLM searches so far were tiny: 8 steps in the
[demo run](../../runs/demo-binpacking/report.md) and 30 calls per run in
[memory-ablation-v1](../memory-ablation-v1/RESULTS.md). This study is the first with hundreds of steps.

## Design

- **Problem:** `problems/bin_packing_online`, unchanged. The model sees `problem.md` only; FunSearch is
  not mentioned. Selection uses the problem's 2 public instances; the loop also reports its 2 hidden
  instances.
- **System:** `autoresearch.loop` with its defaults: the lean loop, the non-regression gate on, and
  the integrity gate.
- **Model:** `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` through the Hugging Face router.
- **Runs:** 4 independent runs, seeds 0–3, each `--max-iters 300 --budget 0.75 --wall 5400 --gate-workers 2`.
  They run in parallel on the local machine.
- **Spend cap:** $3 of Hugging Face credit in total, enforced per run by the loop. No Anthropic calls.

## Primary endpoint: fresh audit

After every run has finished, each final `best_program.py` is evaluated on **100 new instances**.
- **Instances:** `verify.items_for(seed, 5000)` for seeds 30000–30099, which no earlier study or run
  has used.
- **Sandbox:** the same integrity-gate sandbox as the loop (`autoresearch.sandbox.run_online`: a
  separate process, one item at a time, no look-ahead).
- **Metric:** excess over the L2 lower bound, in percent, and its difference from best-fit in
  percentage points (pp). Negative is better.
- **Statistics:** a paired bootstrap over instances (10,000 resamples, seed 739) gives a 95% interval
  for each run.
- **References on the same 100 instances:** best-fit (`initial.py`), and FunSearch's Weibull and
  OR heuristics (`problems/bin_packing_online/baselines/`).

Pre-stated reading:
- a run **beats best-fit** if its interval against best-fit lies entirely below 0;
- it **reaches FunSearch's level** if its interval against FunSearch's heuristic includes 0 or lies
  below 0.

All four runs are reported; none is selected after the fact. The −3.28 pp CPU-tuned rule was measured
on bp-ceiling-v1's own audit instances, from a different generator namespace. It is cited for context
and is not re-measured here.

## Secondary measures

- The loop's own report for each run: spend, steps, accepted improvements, public and hidden scores,
  and the explanation of the final program.
- **Similarity to FunSearch's heuristic:** the fraction of placement decisions identical to FunSearch's
  on the first 10 audit instances. FunSearch's heuristic has been public since 2023, so the model may
  recall it. A near-copy would qualify any "reaches FunSearch" result.
- Wall time split into LLM time and evaluation time.

## Threats to validity

- **Overfitting:** selection uses only 2 public instances. The fresh audit measures exactly this.
- **Scope:** one model, one problem, one budget; 4 runs say little about variance across runs.
- **Recall:** the model may reproduce published heuristics (see the similarity measure).
- **Non-determinism:** model outputs are not reproducible from the seed. The seed fixes only the
  harness's randomness.

## Files

- `PROTOCOL.md`: this file.
- `run.sh`: launches the 4 runs.
- `audit.py`: the fresh audit.
- `runs/s0`–`runs/s3`: the loop's outputs.
- `audit.json`: the audit results.
- `RESULTS.md`: the write-up.
