> Independent review written on 4 October 2026 by a reviewer subagent of session b1, at the user's request
> ("begin looking at the results from other agents"). The reviewer read the study on main at 468a352,
> recomputed numbers from its saved data, and modified no files. The review scripts were in a temporary
> scratchpad and are not kept. These are findings for the study's owners to check, not changes to the study.

# Review: experiments/overfit-gates-v1 (main @ 468a352)

## Verdict: sound, with issues

The data and the code agree. I re-ran `analyze.py` on copies of the saved files (OGV1_DATA set to the scratchpad), and it produced a byte-identical `summary.json` and `tables.md`. I also wrote my own version of all seven gates, the as-run gaps and the archive statistics. It matches every count in the gate table:

- promotions, false acceptances (FA), false rejections (FR) and "truly better" counts;
- the material-threshold counts and the tie split;
- extra items packed and the final means;
- the per-run finals and the contrasts.

Positive control 2 holds as an assertion. **No headline number in RESULTS.md fails to recompute.**

The problems are in labels and interpretation:
- one wrong attribution;
- an inflated "1–2 orders of magnitude";
- a run-weighted mean presented as a per-promotion mean;
- veto inference that rests on 2–3 runs.

## Strongest finding

The strict archive veto works as a test of input length. Whether an input was a counterexample hardly matters, and I checked the mechanism from the saved inputs:
- 554 of the 635 archived inputs are 2 items long, and all 554 fit in one bin.
- 473 of the 554 size-matched random 2-item inputs (85%) also fit in one bin.
- So both G4 (archive veto) and G5 (random veto) mainly test "never open a new bin when one fits". FunSearch-style long-horizon heuristics break that rule on purpose.
- Both vetoes blocked the two largest real gains: prose-s9 (+40.6) and none-s6 (+15.7).

## Issues

1. **Wrong attribution of the tournament-v2 collapse (medium).**
   - RESULTS says: "The 0.960 → 0.238 collapse in tournament-v2 came from much smaller public sets."
   - tournament-v2's RESULTS.md (lines 43–45) says the program "timed out on three of the four larger instances": public n = 5–15, hidden n = 18–27.
   - That is a runtime and size shift. It is not evidence about selection overfitting.
   - Fix: delete the sentence, or restate it as a size or timeout shift that this study does not address.

2. **The "1–2 orders of magnitude" mostly comes from how σ was chosen (medium).**
   - σ follows the protocol: the pooled per-instance SD over the run's distinct proposals, about 11–12. That is almost exactly the SD of best-fit bin counts across the 40 instances (12.4).
   - The cause is degenerate programs. 56% of distinct proposals are more than 20 bins/instance worse than best fit. The largest group (180 members, 161 code texts) averages −2,932 bins/instance (one item per bin). For such a program the advantage is best fit minus a constant, so its SD is just instance difficulty, which cancels in paired selection.
   - With a relevant σ, the bound at K = 30 drops a lot:

     | σ used | n = 1 | n = 5 | n = 10 |
     |---|---|---|---|
     | Proposals within 20 bins of best fit (σ = 1.52) | 3.97 | 1.78 | 1.26 |
     | Paired-difference median from the post hoc table (σ = 0.87) | 2.27 | 1.01 | 0.72 |
     | Observed gap | 0.53 | 0.19 | 0.10 |

   - So the bound overstates by about 4–10×, not 60–100×. The remaining gap is expected, because the bound assumes K independent candidates with equal means.
   - The comparison follows the protocol, and the post hoc bullet hints at this, but the headline does not.
   - Fix: keep the pre-registered row, add the competitive-σ row, and reword the headline.

3. **The as-run gap is a mean of run means, labelled as a mean over promotions, and its framing hides that small promotions were noise (medium).**
   - 0.61 [0.02, 1.49] is the mean of 7 per-run means. The mean over the 17 promotions is 0.38: cluster bootstrap [0.07, 1.05], median 0.30.
   - This also explains why the calls 0–9 / 10–29 split (0.18, 0.41) sits below the "overall" 0.61.
   - The CI's lower bound above 0 depends on one promotion: executable-s6 at call 16, gap 3.09. Without that run the mean of run means is 0.20. A bootstrap over 7 clusters will also undercover.
   - Big promotions kept almost all their gain; small ones lost all of it:
     - the 11 promotions with fixed advantage above 1.2 went from 8.25 to 8.00;
     - the 6 with fixed advantage of 1.2 or less went from 0.60 to −0.01.
   - "Selection overfitting was small" is true in absolute bins but not for marginal promotions.
   - Fix: report both weightings, and add the split by promotion size.
   - experiments/README.md repeats the 0.61.

4. **The veto contrasts rest on 2–3 runs, and the bootstrap p-values are mechanical (low–medium).**
   - G4 − G0 is non-zero in 3 of 30 runs (−40.62, −15.79, −3.21), G5 − G0 in 2, and G6 − G0 in 4.
   - p = 0.045 for G4 is essentially the probability that a resample misses all 3 non-zero runs: (27/30)^30 ≈ 0.042. An exact sign test on the non-zero runs gives p = 0.25.
   - The conclusions survive, since Holm makes nothing significant. But the bold "Strict veto gates threw away the largest real gains" should state "in 2 runs, open-loop replay, Holm p = 0.27". The README "cut 2.28 to 0.29" should carry the same caveat.
   - "Behaved like a random veto" is an absence of difference in an underpowered sample. Its real support is the mechanism (see Strongest finding), so lead with that.

5. **The Thresholdout critique is specific to these parameters (low–medium).**
   - The implementation matches Dwork et al.: γ ~ Lap(2σ), η ~ Lap(4σ), ξ ~ Lap(σ), budget.
   - For a no-op, an overflow needs η < −(T + γ). The expected tie-promotion rate is about ½ · ½ · e^(−T/4σ):
     - about 9% at T = 2, σ = 0.5, which predicts about 40 tie false acceptances against the observed 38;
     - under 0.2% at σ = 0.1.
   - So "would remain at other σ" overstates the point; the effect shrinks exponentially with T/σ.
   - Other problems:
     - It overflowed on 323 of 879 queries, up to 27–28 of 30 in a single run, largely burned on degenerate programs.
     - A budget of 30 is about the number of queries per run, so it can hardly bind by design.
     - The counts come from one random draw. Re-drawing in the protocol's text order gives 49 promotions, 34 FA and 31 ties, against the reported 63/45/38. Seed offsets give 58–65 promotions and 44–47 FA, with finals of 2.24–2.28.
   - Fix: report a spread over seeds, and present the tie problem as a property of T/σ ≈ 4 combined with "promote iff answer < 0" (a margin would remove it).

6. **The no-op share is overgeneralised (low).** "No-ops are 65–82% of proposals" is true only for the prose (0.649) and executable (0.815) arms. The none arm has 0.134, and all 879 valid proposals together about 0.53.

7. **Two omissions in the per-run narrative (low).**
   - G6 also lost none-s6's gain: it ended at −0.67, worse than best fit. The text says only G4 and G5 blocked it.
   - The sign test lost executable-s6's whole 1.71. "Kept almost all of score-only's gain" holds only in aggregate, and the aggregate is driven by prose-s9 and none-s6.

8. **Small implementation choices are undisclosed (low).** None changes a conclusion.
   - Offline best-of-K puts best fit in as a candidate (row 0). "K = 1" is therefore best-of-2, which explains the non-zero K = 1 gaps. At K ≥ 20 it makes no difference: with and without best fit both give about 0.50 at n = 1 and 0.15 at n = 5.
   - The random-veto seeds are `run_index*1000 + k`, where the protocol says `k`.
   - Thresholdout redraws γ before drawing the answer noise, where the protocol text has the reverse order.
   - FA and FR are given as shares of promotions or of truly-better proposals, where the protocol says "among valid proposals". The counts are given, so readers can recompute.
   - Offline cells have no Monte Carlo error bars. The K = 1 values of 0.01–0.03 are within noise.

9. **The dedup check is complete but thin, and the run log misexplains it (low).**
   - Only 19 groups have two or more distinct code texts, and all 19 were checked: 19 of 19 agree on bins and hashes, and the representatives' bins equal their pool bins (recomputed).
   - So 38 rows is the full design. RUN_LOG's "38 rather than 36 or 40, because the runs read different done sets" is wrong.
   - The 19 groups hold 612 code texts (one holds 161), so only 19 of about 593 non-representative texts were checked. The grouping key (identical hashes on 25,000 items) is strong evidence, but "Deduplication was exact" should read "19 of 19 sampled pairs agreed".

10. **Process (low, disclosed).**
    - The freeze is self-attested. PROTOCOL.md's SHA-256 matches the hash in RUN_LOG and in summary.json, but RUN_LOG and all results were committed together at 05:35 (8e9b62e), so nothing outside the log shows the 01:48 time.
    - The worker cap was breached: up to 5 processes ran while load was above 6. This is disclosed, and harmless to the scores.
    - Successful retries are not logged (`errors` is None after a retry), so "0 timeouts" cannot be checked from the files. 0 final failures is verified.

## Protocol adherence

- **Frozen before scoring:** the hash matches. The time is only self-reported (issue 10).
- **Positive control 1:** passed. `control.json` shows 6 programs, 3 of them promoted, with identical bins and packing hashes, and the protocol asked for at least 5 including at least 2 promoted. RUN_LOG times it before the pool run, and the pool log's starting load (21.6) matches.
- **Dedup:** done as specified, and covers every qualifying group (issue 9).
- **Deviations:** the incident, the mid-p change and the post hoc items are disclosed. Issue 8 lists the undisclosed ones.

## Statistics

- The FA, FR and material definitions are applied the same way in every gate (my independent code reproduces every count). They are relative to each gate's own incumbent, which RESULTS discloses.
- Resampling is at the right unit: 30 runs for the gates, and the 7 promoting runs for the as-run gap.
- Holm adjustments recompute.
- The weak points are the few clusters and zero-inflated contrasts (issues 3 and 4) and the choice of σ for the bound (issue 2).

## Literature

- **Ladder:** the parameter-free variant exists (arXiv 1502.04585, confirmed from the abstract). The rule −mean Δ > sd(Δ)/√n matches it as I know it.
- **Thresholdout:** the implementation matches Dwork et al.'s algorithm. I checked this from memory and did not fetch the paper.
- **Gallego 2608.08722:** "16/53 (30%) of in-distribution wins fail to transfer to held-out configurations" is confirmed. The claim appears only in docs/literature/research-directions.md, not in this study. Its phrase "no mitigation" is arguable, because the paper gives design guidance such as "gates must measure held-out performance". It is not clearly wrong, so I did not flag it.

## What I could not check

- When the protocol was actually frozen, beyond the self-reported log.
- Whether the duplicate rows dropped after the incident were identical; they were not kept.
- Pool retries and timeouts, which were not logged.
- Positive control 1 and the pool bins themselves: the review rules forbade re-scoring programs. I only re-derived best fit on 2 pool instances (both match) and confirmed the instance namespaces are distinct.
- The memory study's audit numbers: I checked them against its RESULTS.md, not its raw data.

My scripts are `recheck.py`, `recheck_lib.py` and `recheck_lib2.py`; output is in `recheck.out`, and the `analyze.py` re-run output is in `ogv1data/`. All are in the scratchpad.
