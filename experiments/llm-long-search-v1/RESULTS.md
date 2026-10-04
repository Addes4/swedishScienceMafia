# llm-long-search-v1: a few hundred cheap LLM steps on FunSearch's bin-packing benchmark

**Question.** With 300 calls to an inexpensive open model, does the one-command loop
(`python -m autoresearch.loop`) beat best-fit on online bin packing with 5,000 Weibull items, and how
close does it get to FunSearch's published heuristic?

**Answer.** All four runs beat best-fit on 100 unseen instances. The best three got about 97% of the
way to FunSearch's level, but not all the way, and the classic Sum-of-Squares rule (2006, no LLM)
beats all of them.
- **Every run beat best-fit** on 100 fresh instances. The best run (s0) used 0.81% excess bins over the
  L2 bound, against 4.01% for best-fit: −3.20 pp [−3.25, −3.15], or 63.5 fewer bins per instance.
  The others reached −3.18, −3.18 and −2.05 pp.
- **No run reached FunSearch's level** by the pre-registered test. FunSearch's heuristic reached
  −3.31 pp (−65.6 bins); the best run was 0.11 pp [0.07, 0.15] behind, about 2 bins per instance. That is
  96.8% of FunSearch's gain over best-fit. Against FunSearch per instance, s0 won 26, tied 7 and
  lost 67.
- **The rules are new, not copies.** Only 5–6% of placement decisions match FunSearch's heuristic.
  The best rules keep a running histogram of item sizes and leave gaps that typical items can fill.
- **A classical rule does better than all of them.** Sum-of-Squares, a disclosed post-hoc reference
  with no LLM and no tuning, reached −3.48 pp (−69.0 bins) and beat FunSearch on 86 of 100
  instances: −0.17 pp [−0.20, −0.14].
- **Cost:** $0.80 of Hugging Face credit for all four runs (about $0.20 each) and about 35 minutes of
  wall time per run, run in parallel.

## What we did

- **Protocol.** [PROTOCOL.md](PROTOCOL.md) was committed at 01:17 BST on 4 October (adb7fe9), before
  any run.
- **Runs.** `run.sh` launched four runs of `autoresearch.loop` on `problems/bin_packing_online`, using
  the loop's defaults: the lean loop, the non-regression gate and the integrity gate.
  - Model: `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` through the Hugging Face router.
  - Settings: seeds 0–3, 300 steps each, a $0.75 cap per run, 2 gate workers.
  - Selection: the problem's 2 public instances; the loop also reports its 2 hidden ones.
- **Fresh audit.** `audit.py` ran after all runs had finished. Each final program, plus best-fit and
  both FunSearch heuristics, was scored on 100 new 5,000-item instances (seeds 30000–30099) in the
  integrity gate's sandbox, one item at a time. Intervals are paired bootstraps over instances
  (10,000 resamples, seed 739).
- **Disclosed addition.** `audit_extra.py` scored Sum-of-Squares ([references/sum_of_squares.py](references/sum_of_squares.py))
  on the same 100 instances. It was added after the protocol because an exploratory probe elsewhere
  in the project found that it beats FunSearch on these instances. It does not change the primary
  endpoint. Through the gate it scores 0.9942 public and 0.9950 hidden.

### Work log and deviations

- **01:17.** Launched. The coordinating Claude session restarted while the runs were in progress;
  the runs were unaffected.
- **01:50–01:56.** The runs finished. The helper that was to start the audit automatically waited for
  "no loop process running", but its own command line contained that text, so it never fired. The
  audit was started by hand at 01:56, after all four runs had finished. This made no difference to
  the result.
- **02:12–02:15.** The audit and the Sum-of-Squares reference finished.
- **Explanation-step limitation.** The loop's two-sided explanation marks some lines "essential" only
  because deleting a variable definition crashes the program (Δ = −0.9925). The informative rows are
  the terms with small Δ; see below.

## Results

### Fresh audit: 100 unseen Weibull instances of 5,000 items

Excess is over the L2 lower bound, in percent; Δ is in percentage points, and lower is better.
Brackets are 95% intervals. "vs FunSearch" counts instances where the program used fewer, equal or
more bins than FunSearch's heuristic.

| Program | Excess | Δ vs best-fit | Bins vs best-fit | Δ vs FunSearch | vs FunSearch (W/T/L) | Same decisions as FunSearch |
|---|---|---|---|---|---|---|
| Best-fit (starting program) | 4.010% | – | – | +3.31 | 0/0/100 | 1.0% |
| FunSearch, OR heuristic | 3.048% | −0.96 [−1.00, −0.92] | −19.1 | +2.34 | 0/0/100 | 1.1% |
| FunSearch, Weibull heuristic | 0.703% | −3.31 [−3.36, −3.26] | −65.6 | – | – | 100% |
| **run s0** | **0.810%** | **−3.20 [−3.25, −3.15]** | **−63.5** | +0.11 [+0.07, +0.15] | 26/7/67 | 6.4% |
| run s3 | 0.830% | −3.18 [−3.24, −3.13] | −63.1 | +0.13 [+0.08, +0.17] | 24/7/69 | 5.2% |
| run s1 | 0.833% | −3.18 [−3.23, −3.13] | −63.1 | +0.13 [+0.09, +0.17] | 23/6/71 | 6.4% |
| run s2 | 1.965% | −2.05 [−2.11, −1.97] | −40.6 | +1.26 [+1.20, +1.33] | 0/0/100 | 1.3% |
| Sum-of-Squares (added after the protocol) | 0.534% | −3.48 [−3.52, −3.43] | −69.0 | −0.17 [−0.20, −0.14] | 86/9/5 | – |

Pre-stated reading:
- **Beats best-fit:** 4 of 4 runs.
- **Reaches FunSearch's level:** 0 of 4. Every interval against FunSearch lies above zero.

"Same decisions" is the share of identical bin indices on the first 10 instances. It falls quickly
once two packings diverge, so it only flags near-copies: none of the runs is one.

### The runs

The visible and hidden scores are the loop's own, on 2 instances each (L2 bound / bins, higher is
better). Best-fit scores 0.9616 visible and 0.9604 hidden; FunSearch 0.9925 and 0.9928.

| Run | Spent | Steps | Accepted improvements (at step) | Invalid / gate-rejected | Visible | Hidden | LLM time | Search wall time |
|---|---|---|---|---|---|---|---|---|
| s0 | $0.194 | 300 | 4 (118, 139, 147, 197) | 6 / 1 | 0.9925 | 0.9933 | 24.5 min | 34.5 min |
| s1 | $0.201 | 300 | 4 (51, 57, 122, 124) | 7 / 0 | 0.9925 | 0.9918 | 22.8 min | 33.1 min |
| s2 | $0.193 | 300 | 7 (26, 40, 93, 121, 279, 283, 300) | 13 / 8 | 0.9809 | 0.9776 | 21.2 min | 30.5 min |
| s3 | $0.210 | 300 | 16 (first at 175, last at 290) | 4 / 4 | 0.9922 | 0.9933 | 26.0 min | 37.1 min |

None of the three strong runs made its main gain before step 118. This study's
earlier 8-step demo and the 30-call runs in memory-ablation-v1 would have stopped before that point.

### What the best rule does

s0's final program (61 lines, [runs/s0/best_program.py](runs/s0/best_program.py)) is best-fit with
three additions. Each one made the public score worse when removed by the two-sided ablation:
- a penalty for leaving a "sliver" gap smaller than the running mean item size, since such a gap is
  unlikely to be reused;
- a bonus for an exact fill;
- a bonus for leaving a gap equal to the most common item size seen so far.

In one sentence: *take the tightest fit, but avoid leaving a gap too small for a typical item, and
prefer gaps that the most common item can fill.* s1 and s3 found variations of the same idea of
reusable gaps; s1's docstring says "prefer leaving a residual that matches a recently-seen item size".
Each run's `report.md` has the full ablation table.

## What it means and what it does not show

- **The loop found strong, readable rules cheaply and automatically.** Starting from best-fit and
  given only `problem.md`, three of four runs reached about 97% of FunSearch's gain for about $0.20
  each. This is the first study in the project where an LLM loop gets close to a published result on
  unseen data.
- **It did not beat FunSearch, and FunSearch is not the frontier here.** Sum-of-Squares (Csirik et
  al., 2006) beats FunSearch on these instances, and simple tuned rules match it: a 21-weight linear
  rule in [bp-ceiling-v1](../bp-ceiling-v1/RESULTS.md), and two-threshold rules in Herrmann & Pallez
  2025. A claim of "LLM discovers better algorithms" would need to beat Sum-of-Squares.
- **The ideas are not new to the field.** Leaving reusable gaps and avoiding unusable slivers are
  known bin-packing ideas. The model may be recombining what it knows.
- **We cannot say which part of the loop mattered.** There was no ablation: the same budget with
  independent sampling, or without the gate, might do as well. The literature and our tournament
  suggest simple loops are hard to beat.
- **Scope:** one problem, one distribution, one model, one budget and four runs. Model sampling is not
  reproducible from the seed.

## Cost

| Item | Amount |
|---|---|
| Hugging Face router (DeepSeek-V4.1-Flash on deepinfra) | $0.7977 for 1,200 calls, summed from the runs' `usage.jsonl` |
| Anthropic | $0 |
| Modal | $0 (everything ran locally) |
| Wall time | about 35 minutes per run, 4 in parallel; the audit took 15 minutes and Sum-of-Squares 3 minutes |

## Reproduce

From the repository root, with Python 3.12, `pip install -r requirements.txt` and a Hugging Face
token in `HF_TOKEN` or `~/.cache/huggingface/token`:

```bash
PY=python ./experiments/llm-long-search-v1/run.sh             # 4 runs, at most $3 (about $0.80 spent here)
python experiments/llm-long-search-v1/audit.py                # fresh audit, about 15 min, no API calls
python experiments/llm-long-search-v1/audit_extra.py          # Sum-of-Squares on the same instances
python -m autoresearch.loop --report experiments/llm-long-search-v1/runs/s0   # rebuild a run's report
```

New runs write to `runs/`, which already exists here: move or rename the old folders first.

## Evidence index

| File | Contents |
|---|---|
| `PROTOCOL.md` | Pre-registered design and reading rules (committed before the runs) |
| `run.sh` | Launches the 4 runs |
| `audit.py`, `audit.json` | Fresh audit on 100 instances: per-instance bins, excess and summary with intervals |
| `audit_extra.py`, `audit_extra.json`, `references/sum_of_squares.py` | Disclosed post-hoc Sum-of-Squares reference |
| `summary.json` | Headline numbers, per program and per run |
| `runs/s0`–`s3/` | Each run's `report.md`, `best_program.py`, `events.jsonl` (every step with the model's change description), `evals.jsonl`, `usage.jsonl` (every call), `explain.json`, `baselines.json`, `job.json`, `loop.json`, `summary.json`, `curve.csv` and `artifacts.tar.gz` (every candidate program) |
| `runs/s0.log`–`s3.log` | The terminal output of each run |

## Next steps

1. **Ablation at the same budget:** the same setup with `--independent` and with `--no-gate`, to see
   which part of the loop matters.
2. **Aim at the real frontier:** start the loop from Sum-of-Squares, or from s0's rule with Sum-of-Squares
   as a baseline, and ask whether the loop can beat Sum-of-Squares on fresh instances.
3. **Generalisation:** other item distributions and lengths (500, 10k, 100k), and OR-Library.

## Suggested README text

> **Can the loop reach a published result?** In `experiments/llm-long-search-v1`,
> four 300-step runs of `python -m autoresearch.loop` cost about $0.20 each on an open model. All four beat
> best-fit on 100 unseen 5,000-item Weibull instances. The best got 97% of the way to FunSearch's heuristic
> (−3.20 vs −3.31 pp of excess over the L2 bound) with a different, readable rule, but stayed measurably short of
> it. The classic Sum-of-Squares rule beats both (−3.48 pp).
