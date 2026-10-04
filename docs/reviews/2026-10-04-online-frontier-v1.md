> Independent review written on 4 October 2026 by a reviewer subagent of session b1, at the user's request
> ("begin looking at the results from other agents"). The reviewer read the study on main at 468a352,
> recomputed numbers from its saved data, and modified no files. The review scripts were in a temporary
> scratchpad and are not kept. These are findings for the study's owners to check, not changes to the study.

# Review: experiments/online-frontier-v1 (main @ 468a352)

## Verdict: sound, with issues

- **Numbers:** every number I checked recomputes exactly from `results.jsonl`.
- **Code:** I found no bug that changes a conclusion.
- **Theory:** the PD-exp implementation and its parameters match the paper.
- **Sibling study:** on all 85 shared instances, both studies give identical bin counts.
- **What needs fixing:** the interpretation and the protocol bookkeeping. Wording overreaches about FunSearch's "interface", one failed pre-registered check is not called a deviation, an n = 5 bootstrap interval is in the headline, and there are several small documentation errors.

## Strongest finding

On W5k-fresh (100 fresh 5k instances, seeds 81000–81099, not used anywhere else in the repo):
- SS − FS-W = **−2.65 bins [−3.07, −2.24], 84/11/5, sign p = 1.4e-19**. My recomputation matches exactly, including the seeded bootstrap.
- An independent re-implementation reproduces the bin counts:
  - brute-force SS gives 2022 and 1993;
  - FunSearch's full, non-compact evaluator gives FS-W 2019 and 2002 on test_0 and test_1.
- The sibling study, with different seeds, shows the same gap: SS 10.5 against FS-W 13.8 bins above OPT on 200 fresh 5k instances.
- OPT = L1 holds on 129 of 130 Weibull instances. The exception, seed81045, has OPT = L2 = L1 + 1, so OPT = max(L1, L2) on all 130.
- All 210 MILPs have `proved: true` and dual bound = incumbent.

## Recomputation (task 2)

From `results.jsonl` (210 rows, no duplicates, every bin count ≥ OPT), these all match RESULTS.md, tables.md and summary.json **with no mismatches**:
- bins above OPT, for 8 sets × 8 policies;
- OPT − L1 by set;
- excess over L1 in percent (ratio of sums);
- all 32 contrast means and bootstrap CIs (seed 20261004, 10,000 resamples);
- W/T/L counts and sign-test p-values;
- Holm-adjusted p-values (P1 1.4e-19; P2–P4 6.3e-30);
- the longest OPT solve (42.67 s, reported as "43 s"), total OPT time (1,074.5 s, reported as "1,075") and total time (1,312.8 s, reported as "1,313").

## Issues

1. **Medium: the "interface ceiling" claim overreaches, and "no memory" is a convention, not a constraint.**
   - **Where:** RESULTS.md:17–18 and 82–88 ("the ceiling it was measured against is the interface's ceiling, not the problem's"), and Limitations :188 ("state that FunSearch's evaluator did not offer").
   - **Evidence:**
     - Only one stateless restriction of SS was tested (SS-view). FS-W reaches 13.5 inside that same view, so the interface's ceiling was never measured.
     - The sibling's `online-beyond-ss-v1/check_priority.py` runs a *stateful* `priority(item, bins)` through FunSearch's full evaluator and gets identical bin counts. FunSearch's evaluator therefore permits state; only the evolved-function template is stateless.
   - **Fix:** say "a natural stateless restriction of SS (SS-view) is no better than BF; the view hides N(g) for g < item size, which SS needs". Drop the "interface's ceiling" sentence, and note that state is possible through FunSearch's evaluator.

2. **Medium-low: a failed pre-registered check is not reported as a deviation.**
   - **Where:** PROTOCOL.md:73 says "OPT must equal OR-Library's listed optimum on all 80". The result was 76/80. It was resolved by an unplanned script (`verify_opt.py`, not in the protocol's file list), yet RESULTS.md:170 says "Deviations from the protocol: none".
   - **The resolution itself is correct:**
     - I re-validated the 4 packings in `or_improved_packings.json`: same item multiset, every bin ≤ 150, bins = L1.
     - OR-Library's binpackinfo page confirms that u120_08, u120_19, u250_07, u250_12 and u250_13 are not proven optima.
   - **Impact:** none on the contrasts, because OPT cancels in paired differences. Bins above OPT on OR1 and OR2 are 0.10 per instance higher than they would be with the listed values.
   - **Fix:** list it as a deviation with its resolution. Optionally add that the MILP proves u250_13 = 103 (dual bound 103 > L2 = 102).

3. **Medium-low: an n = 5 bootstrap interval is in the headline.**
   - **Where:** RESULTS.md:16 ("−4.0 [−7.2, −0.4] on FunSearch's own 5 released test instances").
   - **Evidence:**
     - A percentile bootstrap under-covers at n = 5. The per-instance differences are [+3, −9, −5, −3, −6]: the t-interval is [−9.55, +1.55], Wilcoxon p = 0.19 and sign test p = 0.38.
     - The probe also saw this set before the protocol (disclosed).
     - The "All 32 intervals exclude 0" count includes 8 intervals from n = 5 sets.
   - **Fix:** present the released-set result descriptively (mean −4.0, 4 of 5 wins). Say the interval is unreliable at n = 5, or give the t-interval.

4. **Low: "All 32 intervals exclude 0" mixes pre-registered and supplementary contrasts.**
   - PROTOCOL.md:82–83 defines P1/P2 on the Weibull sets and P3/P4 on OR, but line 87 says "4 contrasts × 8 sets", so the protocol is ambiguous.
   - Half the 32 are cross-domain contrasts that are trivially significant (for example SS − FS-OR on W100k is −1178.6).
   - **Fix:** report 16/16 for the pre-registered contrasts and label the rest as supplementary.

5. **Low: asymptotic language goes beyond the data.**
   - RESULTS.md:75–76 says "both keep their waste bounded … so both reach the asymptotic optimum's growth rate". The data are three lengths with only 5 instances at 100k. FS-W rises from 13.5 to 14.4. SS's guarantee on bounded-waste distributions is O(log n), not O(1).
   - :96–98 states "too short for SS's asymptotic behaviour" as a conclusion, but it is an untested hypothesis. SS grows 2.35× from 120 to 1,000 items, while ln n grows 1.44×.
   - **Fix:** write "consistent with bounded waste from 5k to 100k" (the sibling adds 1k), and label the OR explanation as a hypothesis.

6. **Low: the comparison with FunSearch's paper is garbled.**
   - RESULTS.md:52–53 says "reports 3.98%, 0.68%, 0.32% and 0.03% for best fit and its heuristic at 5k, 10k and 100k". It quotes best fit at 5k only.
   - So "our best-fit numbers reproduce these" is not shown at 10k and 100k.
   - FS-W on fresh instances is 0.330% against the published 0.32%, and 0.036% against 0.03%. That is "consistent with", not "reproduce".
   - On the positive side, the OR excesses (FS-OR 5.30 / 4.19 / 3.11 / 2.47%) equal FunSearch's published OR numbers as quoted in the sibling's RESULTS.
   - **Fix:** quote best fit's published values at all three lengths and soften "reproduce".

7. **Low: one bound is mislabelled.**
   - RUN_LOG.md:10 compares open-ended PD-exp (about 250 bins) with "their bound √(4BT) ≈ 1,414". That bound is Theorem 2's, for the known horizon, which is PD-exp-T. Open-ended PD-exp falls under Theorem 3: √(8BT) = 2,000 at B = 100, T = 5,000. The conclusion is unaffected.
   - **Otherwise the implementation is verified against the arXiv PDF of 1211.2687:**
     - The Algorithm 1 Lagrangian Σ_{h=1..B} N(h) + (κ/ε_t) Σ_{h=1..B−1} e^{−ε_t N(h)} matches.
     - Theorem 2 (ε = √(B/T), κ = 1) and Theorem 3 (ε_t = √(B/(2(t+1))), κ = 1) match.
     - The paper's Figure 3 text says PD-exp has O(√t) regret on BW, where SS has O(log t). This matches `pd_sanity.json`.

8. **Low: documentation errors.**
   - RESULTS.md:221 says the OR data hashes are "in RUN_LOG.md". They are not there. Current SHA-256: binpack1 `891fe4b3…`, binpack2 `86fd8c3d…`, binpack3 `24ef075e…`, binpack4 `a87d04d0…`.
   - RESULTS.md:203 gives "about 10 CPU-minutes for the checks and the probe", but the OR solves in `checks.json` alone sum to 1,475 s (24.6 min). The Reproduce section says "~20 min".
   - PROTOCOL.md:130–131 says `results.json`; the actual file is `results.jsonl`.
   - RESULTS.md:80–81 calls online-beyond-ss "not yet confirmed", but :240–248 says its confirmatory study finished.
   - RESULTS.md:137 says the probe ran "before 01:34", but `sos_probe.log`'s mtime in the original worktree is 01:45:58.
   - The docstring at frontier.py:131–132 says PROTOCOL.md explains why the compact evaluator "cannot change a choice". The protocol gives no argument. I checked the argument analytically for:
     - FS-W, including its `max(bins)` and `score[1:] -= score[:-1]` terms (positions past top+2 all score 0, the same as position top+2);
     - FS-OR, ab-WF;
     - SS-view, which `checks.py` did not test.
     The compact evaluator is exact for all of them.
   - Commit 23e9e4d on `exp/online-frontier` edits RESULTS.md (the literature path and next step 2) and is not merged into main.

9. **Low (a sibling-study bug): OPT for u250_12.**
   - `online-beyond-ss-v1/results.json` uses OPT = 106 for OR2/u250_12. That is OR-Library's listed value; the sibling's own arc-flow solve did not prove it (incumbent 129, dual bound 105). This study proves 105 with a verified packing.
   - So the sibling's OR2 bins-above-OPT are 0.05 per instance too low for every policy (SS 10.20 against 10.25; FS-OR 4.15 against 4.20). Its RESULTS also says "3 corrected OR instances"; there are 4.
   - All other shared values (SS, FS-W, FS-OR, BF, ab-WF bins, and L1) match exactly on the 85 shared instances (5 released + 80 OR).
   - The sibling's next-step numbers quoted here (FWSS 1.6–2.1, SS 9.6–10.9, FS-W 13.4–14.0) match its `results.json`.

10. **Low: the pre-registration has no git timestamp.**
    - PROTOCOL.md was first committed together with the results (a586104, 05:35 BST). The hash in RUN_LOG is self-recorded. This is disclosed: there was no commit approval.
    - The committed PROTOCOL.md hashes to the logged value `d1cd8aa6…`.
    - File mtimes in the original worktree (`../ssm-online-frontier`) support the stated order: PROTOCOL 01:49:02 → frontier.py 01:50:39 → checks.json 02:17:23 → results 02:30:15.
    - `report.py` was last modified at 02:19:32, about 24 s after the first results printed. It implements the protocol exactly, so the risk is low.

## Claims checked and supported

- **Distribution class** ("bounded waste"):
  - The LP waste is 5.6e-17 for both distributions.
  - All 200 (Weibull) and 162 (OR) margin LPs return status 0 at the cap t = 1.
  - Axis-wise ±t feasibility is enough to show p is interior, because the cone is convex.
  - `weibull_pmf` matches `verify.items_for` exactly.
  - The empirical OPT = L1 at 100k items agrees.
  - The citation of Courcoubetis–Weber via Csirik et al. is correct. Gupta & Radovanović confirm that SS is O(log T) on bounded-waste distributions and can be made O(1).
- **Prior work:** the OR-Library statement is confirmed from binpackinfo, including the u-class description (uniform 20–100, C = 150).
- **PD-exp numerics:** the float decisions agree with 50-digit decimal arithmetic at all 5,000 steps on test_0 (2268 bins). The maximum level count reaches 360, which is why naive full-sum re-implementations drift by 1–2 bins.
- **Other code:**
  - SS's incremental Δ is exact (r ≠ g always).
  - The ab-WF vectorisation is equivalent to the transcription.
  - The arc-flow model with ordered arcs and loss arcs is the standard formulation.

## What I could not check

- I did not re-run any MILP or the distribution LPs; I relied on the recorded status and dual bounds.
- Independent policy re-implementations ran on 2 released instances only. Nothing on the 10k, 100k or OR sets was re-run.
- I could not view the plots in Gupta & Radovanović's Figure 3, only the text.
- I did not read Csirik et al. 2006 directly, so the naming "SS′" is unverified.
- Unverified: the Mathematics 9(13):1540 citation, Herrmann & Pallez's (1, 21) parameters and "tuned for 5,000 items", and FunSearch's published best-fit values at 10k and 100k.
