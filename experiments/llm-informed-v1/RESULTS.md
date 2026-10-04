# llm-informed-v1: telling the LLM what its function can know did not help

**Question.** Online bin packing has two pieces of information that make the difference between
FunSearch-level rules and near-optimal ones (online-beyond-ss-v1): the full state of the open bins,
and the number of items. If the problem statement spells out that the function has both, does a cheap
LLM loop find rules that beat FunSearch's heuristic, reach Sum-of-Squares (SS), or reach FWSS?

**Answer. No, on all three counts. The informed runs were, if anything, worse than the uninformed ones.**
- **Q1 (beat FunSearch): 0 of 4 runs.** Every interval for (run − FunSearch) lies above zero. The best
  informed run is 1.063% excess over L2 on 100 fresh instances, against FunSearch's 0.703%.
- **Q2 (reach SS): 0 of 4.** SS is at 0.534%.
- **Q3 (reach FWSS): 0 of 4.** FWSS is at 0.096%.
- **Q4 (informed vs uninformed, descriptive, 4 runs each).**

  | Arm | Mean of 4 | Best |
  |---|---|---|
  | Informed | 1.361% | 1.063% |
  | Uninformed (llm-long-search-v1, same model, settings and audit instances) | 1.109% | 0.810% |

  The exact permutation p-value over runs is 0.46, so there is no evidence of a difference either way.
- **What the information changed (code reading, `classification.md`).**
  - 3 of the 4 informed programs tried to use the item count, against none of the uninformed ones. But 2
    of the 3 used it wrongly: one re-initialised its state on most calls, and one read `len(bins)` at
    every call.
  - No program tracked the open bins, although the prompt said how. An SS- or FWSS-style rule needs
    exactly that state.
- **Post-hoc finding (not pre-registered): the informed runs overfit more.**
  - The gap between a run's fresh excess and its excess on the 2 public instances it selected on
    averaged +0.23 pp (informed) against +0.05 pp (uninformed).
  - All four informed gaps (0.10–0.35) exceed all four uninformed ones (0.02–0.08). The exact
    permutation p-value is 0.029.
  - Run s2's public score (0.9927) beat FunSearch's (0.9925), but on fresh instances it lost to FunSearch
    on 89 of 100.
  - The informed programs are about twice as long (96–137 lines vs 40–76) and stack many tuned terms.
- **Cost:** $1.07 of Hugging Face credit, 1,136 calls, 0 errors (recomputed from `usage.jsonl`). The
  user approved about $1; the hard cap was $1.40.

**What this means for online-beyond-ss-v1.** The gap between LLM-found rules and FWSS is not only an
interface problem. Even when told the information exists, this model at this budget did not build the
state that the classical algorithm needs. This is one model, one prompt and 300 steps per run. It does
not show that LLM loops cannot find SS. It does show that telling the model what is available is not
enough.

## What we did

- **Pre-registration.** `PROTOCOL.md`, committed in e2e4b81 at 05:43:37 BST on 4 October 2026, before
  any run.
- **Problem.** `problems/bin_packing_online_informed` is `problems/bin_packing_online`, with an identical
  `verify.py`, instances, scoring, starting program and time limit. Only one paragraph is added to
  `problem.md`, "What your function can know":
  - the item count is `len(bins)` on the first call;
  - the function can track every open bin by recording its own choices;
  - it knows past sizes and how many items remain;
  - each instance runs in a fresh process.

  No algorithm is named. SS and FWSS sit in the folder's `baselines/`; the loop scores them for its
  report but never shows them to the model.
- **Runs.** `run.sh` launched 4 runs (seeds 0–3) of `python -m autoresearch.loop` in parallel:
  - DeepSeek-V4.1-Flash through the Hugging Face router;
  - the lean loop with the non-regression and integrity gates;
  - 300 steps, `--gate-workers 2`, `--wall 5400`, `--budget 0.35`.

  These match llm-long-search-v1 except for the budget cap; it spent $0.19–0.21 per run and never
  approached its $0.75 cap.
- **Fresh audit.** `audit.py` scored, in one run, the 4 informed and 4 uninformed final programs, best
  fit, FunSearch's Weibull heuristic, SS and FWSS.
  - Instances: the same 100 fresh 5,000-item instances as llm-long-search-v1 (seeds 30000–30099).
  - Sandbox: the gate's, a fresh process per instance.
- **Positive control (passed).** Best fit, FunSearch and the 4 uninformed programs reproduce
  llm-long-search-v1's `audit.json` exactly: identical bins on every instance.
- **Code reading.** `classification.md` applies the rules fixed in the protocol.

### Work log
Full times are in `RUN_LOG.md`.
- **05:43.** Launched.
- **During the runs.** The machine was shared, with load averages of 15–58 from other sessions' work.
- **Wall-clock stop.** Run s0 was slower and stopped at 236 steps at the pre-registered 5,400 s wall
  limit. The other three completed 300 steps.
- **07:17.** All runs finished and the audit started.
- **Coordination during the run.** Session 2d claimed the TSP construction lane. Session 43, cleaning up
  the repo, deleted the already-merged remote copy of `exp/online-beyond-ss` after this session checked
  it was merged.

## Results

### Fresh audit: 100 unseen Weibull instances of 5,000 items

Excess over the L2 bound, in percent; lower is better. Brackets are 95% paired bootstrap intervals
(10,000 resamples, seed 739). "Public" is the excess implied by the loop's own score on the 2 instances
it selected on.

| Program | Steps | Spent | Public | Fresh | Δ vs FunSearch, pp | W/T/L vs FunSearch |
|---|---|---|---|---|---|---|
| FWSS (online-beyond-ss-v1) | – | – | – | **0.096** | −0.607 | – |
| Sum-of-Squares | – | – | – | 0.534 | −0.169 | – |
| FunSearch, Weibull heuristic | – | – | – | 0.703 | – | – |
| informed s0 | 236 | $0.254 | 0.959 | 1.063 | +0.359 [+0.306, +0.417] | 2/4/94 |
| informed s2 | 300 | $0.294 | 0.732 | 1.083 | +0.380 [+0.322, +0.437] | 7/4/89 |
| informed s3 | 300 | $0.260 | 1.161 | 1.330 | +0.627 [+0.584, +0.670] | 0/0/100 |
| informed s1 | 300 | $0.265 | 1.666 | 1.969 | +1.266 [+1.148, +1.393] | 0/0/100 |
| uninformed s0 | 300 | $0.194 | 0.757 | 0.810 | +0.107 [+0.066, +0.149] | 26/7/67 |
| uninformed s3 | 300 | $0.210 | 0.782 | 0.830 | +0.127 [+0.084, +0.169] | 24/7/69 |
| uninformed s1 | 300 | $0.201 | 0.757 | 0.833 | +0.130 [+0.088, +0.170] | 23/6/71 |
| uninformed s2 | 300 | $0.193 | 1.943 | 1.965 | +1.262 [+1.199, +1.325] | 0/0/100 |
| best fit | – | – | – | 4.010 | +3.307 | 0/0/100 |

### Pre-registered expectations against the outcome

1. **"Some runs will track open bins and use the item count."** Partly. 3 of 4 tried to use the item
   count (one correctly); none tracked open bins.
2. **"At least one run beats FunSearch."** Wrong: none did.
3. **"Fewer reach SS; reaching FWSS is unlikely."** None reached either.

## Limitations

- **One model, one prompt wording, 300 steps.** A stronger model, a longer search, or a prompt that
  names candidate algorithms could behave differently. The last of these would test recall rather than
  discovery.
- **The comparator arm was not run at the same time.** It ran 4.5 hours earlier, with the loop code at
  adb7fe9. Loop changes between then and e2e4b81 are possible confounds. The positive control shows that
  the audit is identical, not that the search is.
- **Small samples.** Four runs per arm makes Q4 descriptive. The overfitting comparison was not
  pre-registered; its p = 0.029 should be read as exploratory.
- **Budget cap differs.** The cap was $0.35 here and $0.75 there. Neither arm came near its cap
  ($0.25–0.29 here, $0.19–0.21 there), so the cap did not bind.
- **One run stopped early.** s0 hit the wall limit at 236 steps, on a loaded machine.
- **The code reading is one session's reading,** though the rules were fixed in advance.

## Reproduce

```bash
# from the repository root, with the shared venv and a Hugging Face token (~$1.10)
PY=python bash experiments/llm-informed-v1/run.sh
python experiments/llm-informed-v1/audit.py --workers 6      # fresh audit -> audit.json (~10 min)
```

## Evidence index

| File | What it holds |
|---|---|
| `PROTOCOL.md` | Design, questions and expectations (commit e2e4b81, before any run) |
| `RUN_LOG.md` | Times, the wall-clock stop, coordination events |
| `run.sh` | The launch command |
| `runs/s0..s3/` | Everything the loop wrote: `events.jsonl`, `evals.jsonl`, `usage.jsonl` (every call and its cost), `best_program.py`, `report.md`, `explain.json`, `baselines.json`, `summary.json`, `artifacts.tar.gz` |
| `audit.py` → `audit.json` | Per-instance bins of all 12 programs on 100 fresh instances, summary statistics, the positive control |
| `runs_table.json` | Public, hidden and fresh excess, spend and steps per run, both arms |
| `summary.json` | Answers to Q1–Q4, the post-hoc overfitting test, spend |
| `classification.md` | The code reading of all 8 final programs |
| `../../problems/bin_packing_online_informed/` | The problem folder the model saw (`problem.md`) and its baselines |

## Next steps

- **Name the algorithms.** A prompt that cites SS (recall rather than discovery) would show whether the
  model can implement it at all with this interface.
- **A stronger model.** The same informed prompt with a frontier model, at a matched dollar or call
  budget.
- **Hand the model the state.** Give it a gap histogram directly, for example through a different
  function signature. Tracking state was the step no run took.
- **Select on more public instances.** The informed runs' overfitting suggests that selecting on 2
  public instances is too few once programs carry many tuned terms.
