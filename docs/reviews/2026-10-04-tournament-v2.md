> Independent review written on 4 October 2026 by a reviewer subagent of session b1, at the user's request
> ("begin looking at the results from other agents"). The reviewer read the study on main at 468a352,
> recomputed numbers from its saved data, and modified no files. The review scripts were in a temporary
> scratchpad and are not kept. These are findings for the study's owners to check, not changes to the study.

# Review: experiments/tournament-v2 (ssm-review @ 468a352)

## Verdict: sound with issues

Every number recomputes exactly from the raw logs, and the headline null holds up: after Holm, no arm differs from ShinkaEvolve. The problems are in completeness reporting and interpretation:

- RESULTS does not disclose the cancellation that cut the grid short.
- Which runs are missing depends on the arm.
- Per-problem orderings are presented as findings.
- RESULTS says the results agree with v1, but they do not.

## Design (from PROTOCOL.md + amendment, grids/full.json)

- **Grid:** 5 arms (shinka, triage, lean, lean_gate_patience, independent) × 3 problems (sum_difference, erdos_squares, bin_packing_online; bin packing replaced circle packing before launch) × seeds 0–3 = 60 runs.
- **Models and budget:** DeepSeek-V4.1-Flash (deepinfra) for the single-model arms. Triage uses V4-Pro, Flash and Qwen3.5-9B. The cap is $0.15 of HF credit per run.
- **Run settings:** 4 cores per run, gate_workers 4, a 4-hour wall limit, and an experiment cap of $12.
- **Primary endpoint:** AUC gain over the full budget.
- **Primary comparisons:** each of the 4 arms against shinka, paired on (problem, seed). The plan reports a bootstrap CI, P(arm > shinka) and a sign-flip p with Holm correction across 4 tests.
- **Truncation rule:** if runs are truncated, analyse complete pairs and add a secondary all-run analysis at a common checkpoint (smallest valid spend, rounded down to $0.05).
- **Pre-registration integrity:** PROTOCOL.md, grids/full.json and tournament/*.py (apart from its README) are unchanged since launch commit 66f0628 (launch_dirty false). The amendment (7612274) predates the launch.

## Completeness

- 60 planned, 60 launched.
- 47 runs completed with `budget` status (cap reached).
- 13 runs are `incomplete` (no run_end): independent sum ×4, lean sum ×4, lean_gate_patience sum ×3, lean erdos ×2.
- No API errors (0 failed calls, at most 3 retries per run) and no wall_limit runs.
- RESULTS gets the counts (47/13) right but the cause wrong (see issue 1).

## Recomputation

- **Per-run summaries:** I rebuilt all 60 `summary.json` files from usage/evals/events.jsonl with `metrics.summarize` (it only reads files). Comparing 11 fields gave 0 mismatches.
- **Headline file:** I re-ran `report.analyse` and `report.headline` in memory on the recomputed runs. The result reproduces `summary.json` exactly, with 0 mismatches.
- **RESULTS tables:** every value in the full-grid tables matches at the printed precision. That covers the per-cell means, min and max, hidden scores and calls; Δ AUC, Δ final, W/T/L and Holm p; the $0.10 checkpoint for triage; the record-flag margins; and $8.04, 19.6 M tokens and 5,284 evals.
- **Smoke totals:** the recorded total is $0.1181. RESULTS shows $0.1178 plus Jev $0.00028 listed separately, so the two reconcile.
- **Mismatches:** none.

## Strongest finding

**The null holds under every re-cut I tried.** No arm differs from ShinkaEvolve after Holm on AUC gain or final public score:

| Analysis | Result |
|---|---|
| Full-budget complete pairs | all Holm p ≥ 0.25 |
| $0.10 checkpoint | all Holm p ≥ 0.25 |
| All 60 runs with sum_difference added at a $0.02 checkpoint | lean −0.088, independent −0.100, lgp +0.022, triage −0.200 [−0.360, −0.057]; all Holm p ≥ 0.25 |
| bin/erdos at $0.05 plus sum at $0.02 | all Holm p ≥ 0.25 |
| Leave-one-problem-out | no arm significant |

**Triage trails in every analysis but is never significant.** Its gap ranges from −0.19 to −0.31 AUC gain and comes from bin packing and Erdős (−0.30 each). On sum_difference triage is ahead (+0.05).

**Secondary, verified at program level:** the final programs of lean s2/s3 on Erdős squares score 0.99–1.0 public but 0.0/0.25 hidden. The hidden zeros coincide exactly with instance timeouts (4 and 3) on n = 18–27.

## Issues

1. **High: an undisclosed early cancellation, with the truncation blamed on the wrong cause.**
   - *Evidence:*
     - In `launches/full-v2b_20261004_024341.json`, 47 results have returncode 0. The other 13 read "RemoteError: Function call was cancelled by user or a failure."
     - All 13 incomplete runs stop between 01:41:20 and 01:43:30 UTC (02:41–02:43 BST), about 2 h 18 min after the 23:23 UTC start. That is well inside the pre-registered 4 h limit (14,400 s) and the Modal timeout (16,200 s). Their wall_s ranges from 3,224 to 8,348 s.
     - At each run's observed spend rate, 9 of the 13 would have reached the cap in 7,400–10,500 s, inside 4 h: lean erdos ×2, lean sum ×4, lgp sum ×3. Only the 4 independent sum_difference runs (projected 15,700–22,500 s) would have hit the wall limit.
     - RESULTS says these runs were stopped "where each evaluation is slow". Its status note says the grid "ran from 00:23 BST … committed at 05:28". PROTOCOL says "Changes after launch: (None yet.)". The coordinator log has no entry for the cancellation.
   - *Fix:*
     - Record the cancellation (time, cause, who) as a post-launch deviation and correct the completion text.
     - Relaunch `full-v2b`. `run_job` skips jobs that have `summary.json` on the Volume, so only the 13 cancelled jobs should rerun, for at most $1.95 of HF credit.

2. **High/medium: which runs are missing depends on the arm, so the four primary tests are not comparable.**
   - *Evidence:*
     - All 13 truncated runs belong to the three sequential Flash arms. shinka and triage, which evaluate in parallel, completed 24 of 24.
     - The cause is not slower evaluation for those arms. sum_difference evaluations take about 110 s (median) for every arm, shinka included. What differs is how many evaluations each arm buys per dollar and how many it runs in parallel.
     - So the pairs come from different problem mixes: lean has 4 bin + 2 erdos, independent 4 + 4, lgp 4 + 4 + 1, and triage 4 + 4 + 4.
     - Dropping lean erdos s0 flatters lean. That run was at 0.861 after spending 88% of its budget, the worst lean Erdős run; lean's Erdős cell (0.994) uses only s2 and s3.
   - *Fix:*
     - Show each comparison's problem composition next to it.
     - Promote the all-run checkpoint analysis, with sum_difference included (for example at $0.02), to co-primary, or rerun the missing jobs.

3. **Medium: "agrees with tournament-v1" is not accurate.**
   - *Evidence:*
     - At its checkpoint, v1 found lean +0.233 [0.096, 0.386] (Holm p 0.007), independent +0.209 (Holm p 0.006) and triage −0.156 (Holm p 0.038).
     - At the $0.10 checkpoint, v2 finds lean −0.136 [−0.384, 0.081], independent −0.151 [−0.352, 0.053], lgp +0.011 and triage −0.307. At the full budget, lean is −0.004 and independent −0.113.
     - The sign reverses for lean and independent. The two studies agree only that triage trails and that final scores do not differ. Model, budget and problems all differ between them.
   - *Fix:* say that v2 did not replicate v1's early-spend lead of lean and independent over ShinkaEvolve.

4. **Medium: per-problem findings are within noise.**
   - *Evidence:*
     - The headline says "Results depend on the problem", with "single-model loops ended highest" on bin packing (0.983 against 0.976) and "ShinkaEvolve ended highest" on Erdős.
     - With 4 seeds, the smallest possible sign-flip p per cell is 0.125, and no arm × problem interaction was tested.
     - The per-seed differences are noisy: lgp on bin packing has AUC diffs of −0.72, +0.21, +0.56 and +0.41, and the ranges overlap (shinka 0.9616–0.9920, lean 0.9640–0.9927).
     - The 0.983 figure is lean alone; independent is 0.980. The Erdős claim beats lean's 2 complete runs by 0.0025.
   - *Fix:* label these as descriptive, or test the interaction.

5. **Medium: the null has low power and should be framed as inconclusive.**
   - *Evidence:*
     - The standard deviation of the paired AUC-gain differences is 0.24–0.39. With n = 12 and Holm α ≈ 0.0125, the minimum detectable difference is about 0.23–0.37 AUC gain. The actual n is 6–9, so it is larger still.
     - For triage, the bootstrap CI excludes 0 (−0.347, −0.041) while the sign-flip p is 0.0625 (Holm 0.25). Printing that CI under "no framework differs" invites a misreading.
     - lean's Δ-final CI lower bound is +0.00005, printed as "+0.0000".
   - *Fix:* state the minimum detectable difference and note that the bootstrap CI and the permutation test disagree at n ≤ 12.

6. **Medium: triage mixes the framework with its model mix and with how much budget it used.**
   - *Evidence:*
     - 78% of triage's spend ($1.24 of $1.58) went to V4-Pro. 27% of its calls went to Qwen3.5-9B.
     - Complete triage runs used 90.5% of the cap on average (minimum 82.9%), against 96–99% for the other arms. The reason is the roughly $0.083 worst-case reservation for a 32k-token Pro call.
     - Only about half of triage's evaluations were valid (Erdős 10/19, bin packing 25.5/42).
     - Spend is assigned when an evaluation finishes. Triage pays for an idea call and six implementations before any evaluation finishes, which pushes its curve to the right.
   - *Fix:* attribute the result to "triage as configured" and report its budget use and valid-evaluation rate.

7. **Low/medium: some runs may have been restarted without disclosure.**
   - *Evidence:*
     - 7 runs started 14–86 minutes after the other 53: triage erdos s1, independent erdos s0, lean erdos s1, lgp sum s1, independent bin s3, lgp sum s3 and independent sum s1.
     - This happened even though max_containers = 100 and retries = 0.
     - If these were preemption reschedules, `run.py` deletes the run folder before starting (`shutil.rmtree(out)`). The first attempts' spend and logs would then be lost, and the $8.04 total would undercount.
     - independent sum s1 had only 53 minutes before the cancellation and spent $0.021. That run alone pushes the sum_difference checkpoint to $0.00, which drops the problem from the checkpoint analysis.
   - *Fix:* check the Modal logs and the HF billing page, and record what happened.

8. **Low: the cost reporting is incomplete.**
   - *Evidence:*
     - Amendment item 4 promises the HF spend of the stopped full-v2 launches in RESULTS. It is missing; $0.4384 was recorded.
     - The Modal cost of full-v2b is not reported. The $7.47 row covers 3 October only. At list prices, about 64.5 container-hours × $0.221 per hour comes to roughly $14.
   - *Fix:* add both rows.

9. **Low: some pre-registered secondaries are computed but not reported.**
   - *Evidence:*
     - The final-hidden paired test is in `summary.json` but not in RESULTS. For triage it gives −0.174 [−0.422, −0.016], 1/0/7, raw p 0.016, Holm 0.0625, the closest result to significance in the study. It also pools bin packing with Erdős, while the protocol names Erdős only.
     - The lgp − lean (+0.147, p 0.25) and lean − independent contrasts are missing, as are $/improvement and the number of runs at the reference.
   - *Fix:* add a short table of secondary results.

10. **Low: hidden collapse is not always a timeout.**
    - *Evidence:* triage erdos s1 scores 0.9984 public and 0.0 on all four hidden instances, with 0 timeouts. Its program uses exact dynamic programming for n ≤ 15 (the largest public n) and a fallback that fails above that.
    - *Fix:* describe both ways a program can fail to scale: running out of time, and code paths tied to the public instance sizes.

11. **Low: wording.**
    - experiments/README calls the runs "stopped early", which clashes with the protocol's `stopped_early` class.
    - The protocol says "all 60 in parallel", but 7 runs started late.
    - "ShinkaEvolve's seed-0 run had no timeouts" picks one seed; seed 2 had one.

On saturation, the problems are not saturated for Flash. Erdős reaches ≥ 0.999 in only 5 of 20 runs (at $0.009–$0.101), and bin packing and sum_difference never do. v1's saturation threat does not apply here. Bin-packing AUC gain is bimodal, though (shinka scores 0.75, 0.48, 0.001 and 0), so one lucky early jump dominates a cell.

## What I could not check

- **The cancellation:** who or what cancelled the Modal calls at 01:43 UTC. The 13 runs have no stdout logs or Modal logs.
- **The late starts:** whether the 7 late starts were preemption restarts.
- **Billing:** actual spend on the HF billing page and the Modal bill.
- **Timing determinism:** whether instance timing varies across containers. Only 9 programs were evaluated twice, and all 9 gave identical results.
- **Program integrity:** I only spot-checked best programs (lean s2/s3, triage s1).
- **Not inspected:** I did not inspect curves.svg or the full-v2 partial runs beyond their spend.
- **Re-runs:** nothing was re-run.
