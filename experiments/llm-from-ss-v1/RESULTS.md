# llm-from-ss-v1: can 300 loop steps starting from Sum-of-Squares beat it?

**Question.** When the one-command loop (`python -m autoresearch.loop`) starts from Sum-of-Squares (SS), the best
horizon-free policy found on FunSearch's Weibull benchmark, can a few hundred steps of a cheap open model find a
policy that uses fewer bins than SS on unseen instances?

**Answer.** Yes, by the pre-registered test, in all 4 runs; one run by a useful margin.

- **The best run found something new.** Run s3 beat SS by **2.31 bins per instance [−2.58, −2.04]** on 100 unseen
  5,000-item instances (92 wins, 6 ties, 2 losses).
  - It is **8.37 bins above the exact optimum**, against 10.68 for SS and 13.52 for FunSearch's evolved heuristic.
  - It found a gap-weighted SS that penalises nearly full bins.
  - A post-hoc check shows that the weighting (100/g)^0.8 alone accounts for the whole gain (−2.29 against SS).
- **The other three runs made the same small change.** Runs s0, s1 and s2 each beat SS by **0.48 bins per instance
  [−0.74, −0.22]**. All three replaced SS's tie-break (tighter fit) with the opposite one (larger leftover gap).
- **No run used the horizon.** None of the final programs uses the number of items. The known-horizon policy FWSS
  (session b1's fill-weighted SS with a best-fit finish, a disclosed reference) is at **1.83 bins above the
  optimum** on the same instances. This confirms b1's numbers on new instances, and it remains far ahead.
- **Cost.** $1.10 of Hugging Face credit for all 4 runs, under a $2.50 cap. Hugging Face only; no other provider.
- **Novelty.** Level-weighted SS is a known family: Csirik et al. 2006 §8.1, Theorem 8.1 keeps SS's guarantees for
  any weight function of the level.
  - Their examples weight *emptier* bins more, and they report "no clear winner" among variants.
  - s3's weight goes the opposite way: it penalises nearly full bins. FWSS's weight goes the same way as s3's,
    and b1 found it by hand.
  - So the loop found a member of a known family, in a direction the family's authors did not report, and it
    beats SS on FunSearch's benchmark.

The protocol was committed at `1c6bc88` (05:41:14 BST, 4 October 2026), before any LLM call. Runs: 05:41–08:43 BST.
Audit: 08:44–08:48 BST.

## Results

### Fresh audit: 100 unseen 5,000-item instances (seeds 84000–84099)

- Bins are per instance. "Bins above OPT" uses the exact optimum from the arc-flow integer program, proved on all 100
  instances.
- Contrasts are mean bin differences with a 95% paired bootstrap interval (seed 84, 10,000 resamples) and
  wins/ties/losses.
- Source: `audit.json`, via `report.py` → `tables.md`.

| Program | Bins above OPT | Excess over L1 | vs SS | vs FunSearch | vs FWSS | Same decisions as SS | Uses horizon |
|---|---|---|---|---|---|---|---|
| Best fit | 78.95 | 3.980% | +68.27 [+67.62, +68.93] 0/0/100 | +65.43 | +77.12 | 1.7% | no |
| FunSearch Weibull heuristic | 13.52 | 0.682% | +2.84 [+2.36, +3.36] 8/9/83 | 0 | +11.69 | 2.5% | no |
| Sum-of-Squares (starting program) | 10.68 | 0.538% | 0 | −2.84 [−3.36, −2.36] 83/9/8 | +8.85 | 100% | no |
| FWSS (known horizon; disclosed reference) | **1.83** | 0.092% | −8.85 [−9.19, −8.51] 100/0/0 | −11.69 | 0 | 7.9% | yes |
| run s0 | 10.20 | 0.514% | **−0.48 [−0.74, −0.22]** 51/28/21 | −3.32 [−3.88, −2.80] 84/12/4 | +8.37 | 16.3% | no |
| run s1 | 10.20 | 0.514% | **−0.48 [−0.74, −0.22]** 51/28/21 | −3.32 [−3.88, −2.80] 84/12/4 | +8.37 | 16.3% | no |
| run s2 | 10.20 | 0.514% | **−0.48 [−0.74, −0.22]** 51/28/21 | −3.32 [−3.88, −2.80] 84/12/4 | +8.37 | 16.3% | no |
| run s3 | **8.37** | 0.422% | **−2.31 [−2.58, −2.04]** 92/6/2 | −5.15 [−5.69, −4.62] 99/0/1 | +6.54 [+6.21, +6.88] 0/0/100 | 7.2% | no |

**Pre-registered decision.** A run *beats SS* if its interval lies entirely below 0. All 4 runs do.

**Columns.**
- *Same decisions as SS* is the share of identical bin choices on the first 10 audit instances.
- *Uses horizon*: any difference between a program's decisions on the first 4,000 items of a 4,000-item instance and
  of the 5,000-item instance with the same seed (5 seeds).
  - FWSS differs on 20–32 of 4,000 decisions, as expected.
  - Every run and every other reference differs on 0.

### The runs

Source: `runs/*/summary.json`, `usage.jsonl`, `loop.json`.

| Run | Stop | Steps | Evaluations (valid) | Improvements | Public, 2 instances | Hidden, 2 instances | Spend | LLM seconds |
|---|---|---|---|---|---|---|---|---|
| s0 | wall limit | 293 | 294 (290) | 2 | 0.9942 → 0.9952 | 0.9950 → 0.9947 | $0.2703 | 3,418 |
| s1 | 300 steps | 300 | 301 (294) | 3 | 0.9942 → 0.9952 | 0.9950 → 0.9947 | $0.2687 | 3,355 |
| s2 | wall limit | 264 | 265 (251) | 2 | 0.9942 → 0.9952 | 0.9950 → 0.9947 | $0.2509 | 3,095 |
| s3 | wall limit | 286 | 287 (285) | 6 | 0.9942 → 0.9965 | 0.9950 → 0.9957 | $0.3095 | 4,482 |

- **Total spend.** $1.0994, recomputed from `usage.jsonl`. No failed or refused calls.
- **False OVERFIT? flags.** The loop flagged s0–s2 `OVERFIT?` because their hidden score fell slightly on its
  2 hidden instances. On 100 fresh instances all three beat SS. Two hidden instances are too few to judge a change
  of half a bin per instance. The flag is a prompt to audit, not a verdict, and here the audit overturned it.

### What the programs do

- **s0, s1 and s2: tie-break flip.** All three made the same change, independently: among placements with equal SS
  cost, prefer the one that leaves the *larger* gap. The starting program, like Csirik et al.'s canonical SS,
  prefers the higher level, that is the tighter fit. Csirik et al. note that SS's guarantees hold for any tie rule.
  - The flip changes 84% of decisions, because one different choice changes every later state.
  - It saves 0.48 bins per instance.
- **s3: weighted potential.** s3 minimises Σ_g (100/g)^0.8 · N(g)², where N(g) counts open bins with gap g. It adds
  an exact-fit override, a small bonus term, and the tighter-fit tie-break.
  - **Code–docstring mismatch.** The bonus term is documented as rewarding leftover gaps that match common gap
    sizes. The code subtracts it, so it actually penalises them.
- **Mechanism check (post hoc, `mechanism.py`, `mechanism.json`).** Weighted SS with only the (100/g)^p weight, on
  the same 100 instances:
  - p = 0 reproduces SS exactly on 100 of 100 instances (control).
  - p = 0.8 gives −2.29 bins per instance against SS, within 0.02 of s3.
  - The weighting is therefore the whole effect; the override and the bonus term contribute nothing measurable.
- **The loop's explanation step** (`runs/*/explain.json`) is not informative here. Most parts are "essential" only
  because removing them breaks the program's own bookkeeping of bins. For s3 it marks the exact-fit lines as
  "no effect alone" (Δ = −0.00075 on the 2 public instances), which agrees with the mechanism check.
- **Running time.** The programs take about 0.65 s per instance in the sandbox, the same as SS. FunSearch's
  heuristic takes 1.46 s.

### Timeouts and machine load (at the coordinator's request)

- **Load.** The machine was heavily loaded by other sessions' work during the runs. At 06:57 `uptime` gave load
  averages 69.85 / 65.76 / 67.88 on 10 cores; the coordinator puts it at about 64 from about 06:30. Since SS-based
  candidates keep state and are slower than stateless ones, a timeout could hide an improvement, so failures were
  split by cause (`timeouts.py` → `timeouts.json`).
- **Timeouts.** 1 of 1,147 candidate evaluations timed out: s2 step 124, at 120 s, on both public instances.
  - It was re-evaluated after the runs through the same gate and 30 s per-instance limit (load about 7–10).
  - Instance 1 took 28.4 s and scored 0.9607; instance 2 timed out again at 30.0 s.
  - The incumbent's score on instance 1 was about 0.996, so this candidate would not have been accepted.
- **Code errors.** The other 26 failed evaluations are code errors with a traceback: s0 4, s1 7, s2 13, s3 2.
- **Steps lost to load.** Three runs stopped at the 5,400 s wall limit before 300 steps (293, 264 and 286 steps).
  - LLM time alone was 3,095–4,482 s per run, against about 2,066 s of total wall time per run in
    llm-long-search-v1.
  - So these runs had 1–12% fewer steps than planned. The effective budget is reported as run.

## What was done

- **05:38.** Worktree `../ssm-llm-from-ss`, branch `exp/llm-from-ss`, from `main` at `02ba33e`. New problem folder
  `problems/bin_packing_online_ss`:
  - `problem.md`, `verify.py` and `evaluate.py` are unchanged copies of `problems/bin_packing_online`.
  - `initial.py` is SS as a stateful `priority` function, with the same logic as llm-long-search-v1's reference.
  - Baselines: best fit, FunSearch Weibull and SS.
- **Pre-run checks** (`check_initial.py`, `check_initial.json`).
  - `initial.py` in the gate's sandbox gives the same bins as online-frontier-v1's SS on 5 instances.
  - The gate's score of `initial.py` equals SS computed directly on the public and hidden instances. Each instance
    runs in a fresh process, so state does not leak between instances.
  - The arc-flow smoke test proved OPT = L1 on a spare seed.
- **05:41:14.** Protocol, scripts and checks committed (`1c6bc88`). Runs launched with at most 3 at a time; s3
  started at 07:12 when a slot freed.
- **06:57.** The coordinator's validity note about load. Load recorded; the timeout analysis was planned and nothing
  rerun.
- **08:43.** All runs finished. Fresh audit with 3 workers (08:44–08:48), then `report.py`.
- **Post hoc.**
  - `timeouts.py`, at the coordinator's request. Its first version had two bugs, fixed before its results were
    used:
    - it looked for candidate folders that the loop had already packed into `artifacts.tar.gz`;
    - it misclassified tracebacks as "other".
  - `mechanism.py`.
- **Deviations from the protocol.** The wall limit cut three runs short (above). Two analyses were added post hoc
  (above). Nothing else.

## Limitations

- **Few runs, one model.** Four runs and one model (DeepSeek-V4.1-Flash). Three of the four runs converged on the
  same small change, so the large gain rests on one run (s3). The study shows that such a gain is reachable in
  about 300 steps for about $0.30, not how often it is reached.
- **Selection on two instances.** Selection used 2 public instances. That was enough to promote real gains here,
  but the loop's own 2-instance hidden check gave false OVERFIT? flags.
- **Recall.** The model may know level-weighted SS from the literature. s3's docstring does not cite it, and its
  weighting direction differs from Csirik et al.'s published examples.
- **One distribution.** Only Weibull 5k, FunSearch's setting. The OR-Library instances, other lengths and other
  distributions were not audited for these programs.
- **The horizon was available.** The model was told each instance has 5,000 items, but no run used that. FWSS shows
  the horizon is worth about 6.5 more bins per instance.
- **Exponent not tuned.** s3's exponent 0.8 was chosen by the model on 2 instances; a tuned exponent might do better.

## Cost

- **Hugging Face:** $1.0994 for 1,143 calls, under the $2.50 cap.
- **CPU:** local only, about 4 minutes for the audit and about 2 minutes for the timeout re-evaluation and the
  mechanism check.
- No Anthropic, OpenAI or Modal spend.

## Reproduce

From the repository root, with the repository's venv and an HF token at `~/.cache/huggingface/token`:

```bash
python experiments/llm-from-ss-v1/check_initial.py                 # pre-run check (no API calls)
PY=python experiments/llm-from-ss-v1/run.sh                         # the 4 runs (HF spend; at most $2.40)
python experiments/llm-from-ss-v1/audit.py --workers 3              # fresh audit, optimum, agreement, horizon -> audit.json
python experiments/llm-from-ss-v1/report.py                         # tables.md, summary.json
python experiments/llm-from-ss-v1/timeouts.py                       # timeouts vs code errors -> timeouts.json
python experiments/llm-from-ss-v1/mechanism.py                      # weighting-only check -> mechanism.json
```

Model outputs are not reproducible from the seed. The audit, report, timeout and mechanism steps are deterministic
given the saved run folders.

## Evidence index

| File | What it holds |
|---|---|
| `PROTOCOL.md` | Design, committed before any run (`1c6bc88`) |
| `RUN_LOG.md` | Times, load readings, events |
| `check_initial.py`, `check_initial.json` | Pre-run equivalence checks |
| `run.sh`, `run_sh.log`, `runs/s*.log` | Launch script and logs |
| `runs/s0`–`s3/` | The loop's outputs: `best_program.py`, `report.md`, `evals.jsonl`, `events.jsonl`, `usage.jsonl`, `explain.json`, `artifacts.tar.gz` (every candidate) |
| `audit.py`, `audit.json`, `audit.log` | Fresh audit on 100 instances, exact optimum, agreement, horizon check |
| `report.py`, `tables.md`, `summary.json` | Tables generated from `audit.json` and the run folders |
| `timeouts.py`, `timeouts.json` | Timeouts vs code errors; re-evaluation of the timed-out candidate |
| `mechanism.py`, `mechanism.json` | Weighting-only ablation of s3 |
| `references/` | `arcflow.py` and `ss_hist.py` (verbatim from online-frontier-v1's `frontier.py`, SHA-256 `3b74ed18…`, full copy included); `priority_fss.py` (FWSS from commit `47258dc` of `exp/online-beyond-ss`, SHA-256 `ad087d0a…`) |

## Next steps

1. **Tune the weighted family.** Tune s3's weighted-SS family (the exponent p, with both tie-breaks) on separate
   instances, to see how far horizon-free weighting can go. Then test it on OR1–OR4 and other lengths.
2. **Give the model the horizon.** Run the loop from s3's program with a prompt that states the horizon is usable,
   to see whether it finds a best-fit finish like FWSS's (worth about 6.5 bins).
3. **Count successes.** Run more seeds, or a second model, to estimate how often the weighting is found.
4. **Test the tie-break on its own.** The tie-break flip is cheap and orthogonal to the weighting; check whether it
   adds to s3's weighting.
