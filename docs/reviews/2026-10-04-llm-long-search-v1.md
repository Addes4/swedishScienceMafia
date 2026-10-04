> Independent review written on 4 October 2026 by a reviewer subagent of session b1, at the user's request
> ("begin looking at the results from other agents"). The reviewer read the study on main at 468a352,
> recomputed numbers from its saved data, and modified no files. The review scripts were in a temporary
> scratchpad and are not kept. These are findings for the study's owners to check, not changes to the study.

# Review: experiments/llm-long-search-v1 (main at 468a352)

## Verdict: sound with issues

The primary endpoint holds. So do the pre-registered reading and every number in RESULTS.md that can be recomputed from the evidence files. The problems are all in the secondary claims about what the rules are:
- the description of s0 contradicts the run's own ablation;
- the "running histogram" is not what makes the rules work;
- the 5–6% agreement figure does not measure what the headline uses it for.

## Strongest finding

The three strong runs converged on the same two-line rule: **fill a bin exactly if possible; otherwise put the item where the leftover space is closest to 40.** The constant 40 comes from problem.md's "mean about 40". This rule is s0's own ablation "minimal program" (`runs/s0/report.md`, Explanation section), which RESULTS does not mention.

I re-ran it in-process on the 100 audit instances. On every instance I compared, my harness reproduced audit.json's bins exactly.
- **The two-line rule alone** reaches −3.19 pp against best-fit, 96.4% of FunSearch's gain.
- **s0 against the rule:** s0 is better by only 0.011 pp [−0.012, +0.034], or 0.22 bins per instance, which is not significant.
- **Same decisions:** given the same packing state, s0 and s1 pick the same bin 99.0% of the time. s0 and the two-line rule agree 98.8–99.1% of the time, and s0 and s3 94–95%.
- **It is not best-fit:** s0 never picks the tightest non-exact fit. On seed 30000:
  - 39% of steps have an exact fit;
  - in 18% no used bin fits;
  - in the other 43%, s0 never takes the tightest fitting bin;
  - in 22% of all steps it opens a new bin although a used bin fits.

## Issues

1. **High: the description of s0 contradicts its own ablation.**
   - *What RESULTS says:* "best-fit with three additions. Each one made the public score worse when removed by the two-sided ablation."
   - *What the ablation says:* `runs/s0/report.md` puts all of these under "Parts that can go":
     - the exact-fill bonus (`term + exact`);
     - the modal bonus (`term + complement`);
     - the `waste` term;
     - `_hist[item] += 1`;
     - the running-mean update.

     Without them the public score is 0.9915 (against 0.9925) and the hidden score 0.9928 (against 0.9933). The exact-fill and modal parts are called "essential" only in the crash rows (Δ = −0.9925), and RESULTS' own limitation note says those rows are uninformative.
   - *The exact-fill bonus does nothing:* without it, r = 0 scores 0 and every r > 0 scores below 0 whenever the modal size is above 3. Removing it gives identical bins on 25 of 25 audit instances.
   - *"Take the tightest fit" is wrong* for every non-trivial decision (see the numbers above).
   - *Fix:* describe the minimal program instead: exact fill, otherwise leave the gap closest to the mean item size (about 40). The running statistics and the modal bonus add about 0.2 bins per instance.

2. **Medium: "The best rules keep a running histogram of item sizes" overstates what the histogram does.**
   - *s1:*
     - `_hist` is written but never read, so it is dead code.
     - `_seen` decays by a factor of 0.999 per step but is only used as `_seen > 0`, so "recently-seen" in fact means "ever seen". The run's own ablation lists `_hist[item] += 1` and `_seen *= 0.999` as "can go".
     - Quoting s1's docstring presents the model's intent as the program's behaviour.
   - *s0:* the histogram is used only through its argmax, and its update can go.
   - *s3:*
     - The histogram updates show "no effect alone".
     - The two histogram score terms (lines 66 and 73) were among the 13 parts the ablation never tested because of its 40-evaluation limit. RESULTS does not mention this.
     - In my check on the 100 audit instances, removing s3's histogram terms costs +0.029 pp [0.004, 0.055], or 0.57 bins, about 1% of the gain. Removing s1's "seen size" term changes it by +0.004 pp [−0.018, 0.026].
   - *The event logs agree:*
     - Each strong run made its big jump when it adopted a target leftover near the mean: s0 at step 118, s1 at step 122 and s3 at step 275. All three reached a public score of about 0.99125, and s0 and s1 reached exactly 0.9912468.
     - s1's own change summary at step 122 says "score bins by how close their residual is to the observed mean item size (~40)".
     - The later histogram and modal steps added about 0.001 of public score, roughly 2 bins per public instance, and carried over to fresh instances weakly or not at all.
   - *Fix:* say "the rules leave a gap close to the mean item size; histogram refinements add at most about 1% of the gain". Also report that three of four runs converged on the same rule independently. That is a stronger and more interesting statement than "variations of the same idea".

3. **Medium: 5–6% decision agreement is weak evidence for "not copies".**
   - *The measure saturates:* free-running bin-index agreement is about 1% even for best-fit and FunSearch's OR heuristic, so it only detects exact behavioural clones. RESULTS says so under the table, but the headline bullet still uses the number as evidence.
   - *Agreement given the same state* (same leftover size chosen, 2 instances):
     - the runs agree with FunSearch on 71–72% of decisions under FunSearch's packing, and 82–83% under s0's;
     - best-fit agrees on 45% and 57%.

     At the decision level, the runs behave much more like FunSearch than best-fit does.
   - *The conclusion still stands on code inspection:* no run contains FunSearch's formula, which is (bins−max)²/item + bins²/item² + bins²/item³, then a sign flip, then a first difference.
   - *Fix:* rest "not copies" on code inspection and report the same-state agreement. "The rules are new" also sits badly with RESULTS' later "the ideas are not new to the field". Say "not copies of FunSearch's heuristic".

4. **Medium: the explanation-step limitation is accurate but incomplete, and the write-up does not apply it.**
   - *What is accurate:* deleting a variable definition raises a NameError, and the row is then marked "essential" with Δ = −(the program's score).
   - *What is missing or inaccurate:*
     - (a) Δ is −0.9925 only for s0 and s1; it is −0.9922 for s3 and −0.9809 for s2.
     - (b) The rows that carry information are the term rows and the "can go" list. The section "What the best rule does" relies on the crash rows instead (issue 1).
     - (c) "Can go" is a joint test at ±0.002 on 2 public instances, which is about ±4 bins per instance. That is twice the 2.1-bin gap between s0 and FunSearch, so the tool cannot resolve parts at the scale of the headline comparison.
     - (d) In s3, 13 parts were never tested.
   - *Fix:* state (a)–(d). In the loop, mark a part whose removal raises a NameError as a "dependency" rather than "essential", or remove definitions together with their uses.

5. **Low–medium: how "97%" is framed.**
   - *Rounding:* the arithmetic is right for s0 (96.8%), but s1 and s3 are at 96.1% and 96.2%, so "the best three got about 97%" rounds up. Say "96–97%".
   - *Share of gain flatters:* measuring from best-fit makes the runs look close. In excess over L2, s0 has 15% more than FunSearch (0.810% against 0.703%) and s1 and s3 have 18% more; Sum-of-Squares has 24% less.
   - *Calibration:* a stateless two-line rule reaches 96.4%, so "97% of FunSearch's gain" does not imply a sophisticated rule.
   - *Undisclosed hint:* problem.md tells the model "Weibull-shaped, mean about 40", the one constant the effective rule needs. s0's minimal program uses 40 verbatim (the initial value of `_mean`). This information gap should be disclosed next to the FunSearch comparison. I did not check FunSearch's prompt.

6. **Low: the post-hoc Sum-of-Squares reference.**
   - *What I verified:*
     - the reference's internal bin record matches the harness at every step (0 mismatches on 2 instances);
     - it reproduces audit_extra.json's bins;
     - its gate scores of 0.9942 public and 0.9950 hidden reproduce. Those scores are not recorded in any evidence file.
   - *Disclosure is good* in the body, the table and audit_extra.json. What remains:
     - The first sentence of the Answer and the suggested README text present Sum-of-Squares without saying it was post-hoc.
     - RESULTS does not say whether the decision to add it came before or after the runs' audit was seen.
     - The motivating probe (`docs/literature/probes/sos_probe.*`) was committed only at 05:35 (c0b759b), after this study (02:14). When RESULTS was committed, "an exploratory probe elsewhere" had no pointer in the repository.
   - *Fix:* add "post-hoc" in those two places, link the probe, and say when the decision was made.

7. **Low: the audit start delay.**
   - *Disclosure is adequate,* and the result is unaffected: the audit is deterministic and was reproduced exactly.
   - *The timing is only accurate to the minute:*
     - s3's search ended at 01:54:40, and its baselines and explanation step ran until about 01:56:38 (from the report's timings).
     - So "started at 01:56, after all four runs had finished" holds only to within a minute.
     - audit.json records no start time.
   - *Why overlap would not matter:* it could only act through the sandbox's 120 s timeout, and all 700 audit runs are valid.
   - *Fix:* record start and end timestamps in audit.json.

8. **Low: wording of the cost.**
   - *What recomputes:* $0.7977 matches the sum of `usage.jsonl` exactly.
   - *What it is:* `cost_usd` is token counts times the configured list price ($0.20 / $0.60 per million tokens; my recomputation from token counts matches within $0.00001). It is not a Hugging Face invoice.
   - *Fix:* say "estimated at list price" instead of "of Hugging Face credit", or check against HF billing.

9. **Low: small inaccuracies.**
   - *Protocol timestamp:* PROTOCOL.md says "Written at 01:20 BST", but it was committed at 01:17:37 (adb7fe9), and the runs started at 01:17:39.75 (`job.json` `started_at`). RESULTS' "01:17" is right; add an erratum.
   - *Missing outcomes:* the run table omits one `no_code` outcome each for s2 and s3. Outcomes only sum to 300 with them.
   - *Evaluation time not reported:* the protocol asks for wall time split into LLM and evaluation time. Evaluation time is about 9.2–11.0 min per run from `evals.jsonl`.
   - *Demo attribution:* "this study's earlier 8-step demo": the demo is not part of this study.
   - *Sum-of-Squares duration:* "3 minutes" equals its summed sandbox seconds (179 s). With 8 workers the wall time would be well under a minute. I cannot verify this.

## Verified with no issue

- **Spend per run:** $0.193883, $0.201041, $0.192763 and $0.209964; $0.797651 in total.
- **Steps and calls:** 300 contiguous steps per run, 300 calls each, 0 failed calls. No gaps in the event streams suggest the coordinator restart interrupted anything.
- **Run counts:** improvement counts and the steps they happened at; invalid and gate-rejected counts (6/1, 7/0, 13/8, 4/4).
- **Times:**
  - LLM time, the sum of usage seconds: 24.45, 22.81, 21.18 and 25.96 min.
  - Search wall time, from `loop.json` `search_s`.
- **Loop scores:** visible and hidden scores.
- **Audit-derived numbers:** excess, Δ, bootstrap intervals (seed 739), bins, wins/ties/losses, decision agreement and 96.8%.
- **Sum-of-Squares numbers:** −3.48 pp, −69.0 bins, 86/9/5, −0.17 pp [−0.20, −0.14].
- **Run configuration matches the protocol:** lean loop, gate on, seeds 0–3, $0.75, 300 steps, 5400 s, 2 gate workers, commit adb7fe9.
- **"No main gain before step 118":** correct (118, 122, and 198–290 for s3).

## What I could not check

- Actual Hugging Face billing.
- The failure of the audit-start helper and the coordinator restart: there are no logs of either.
- When the decision to add Sum-of-Squares was made, relative to seeing the audit.
- Whether FunSearch's prompt stated the distribution's mean.
- Reproducibility of the model's sampling, since no API calls were allowed.
- Sample size of my own checks:
  - same-state agreement and the tightest-fit breakdown use 1–3 instances;
  - the simplified-rule comparisons use 25–100 instances;
  - all ran in-process, not in the sandbox. In-process bins matched audit.json exactly on every instance compared.

Scripts (in the scratchpad, read-only with respect to the repository): `sim.py`, `tf2.py`, `tight.py`, `variants2.py`, `full100.py`, `sos_check.py`.
