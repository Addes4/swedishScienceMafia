# online-frontier-v1: FunSearch's heuristics against the exact optimum and classical online algorithms

**Question.** On FunSearch's online bin-packing benchmarks, how far is each heuristic from the offline
optimum? How does FunSearch's evolved heuristic compare with classical online algorithms that have
guarantees for i.i.d. item sizes?

**Answer.**
- On FunSearch's Weibull benchmark the offline optimum equals the L1 bound on 129 of 130 instances.
  FunSearch's reported excess over L1 is therefore all online waste.
- FunSearch's Weibull heuristic wastes 13–14 bins per instance at every length from 5,000 to
  100,000 items.
- Sum-of-Squares (SS; Csirik et al., JACM 2006) wastes 10–11. It has no parameters, is about 15
  lines, and uses fewer bins than FunSearch's heuristic on every Weibull set:
  - −2.65 bins per instance [−3.07, −2.24] on 100 fresh 5,000-item instances (84 wins, 11 ties,
    5 losses);
  - on FunSearch's own 5 released test instances, mean −4.0 with 4 wins in 5. That is consistent,
    but too few instances for an interval: the t-interval is [−9.55, +1.55] and the sign test
    p = 0.38. These instances were also seen in the exploratory probe before the protocol.
- A natural stateless restriction of SS, which sees only the bins the current item fits in (as
  FunSearch's `priority(item, bins)` template does), is no better than best fit: 81 bins against
  79. That view hides N(g) for gaps smaller than the item, which SS needs. FunSearch's evaluator
  does let a function keep state between calls; only its template is stateless.
- On the OR-Library instances (OR1–OR4) FunSearch's OR heuristic is the best policy tested. SS is
  4–8 bins per instance worse than it, though better than FunSearch's Weibull heuristic there.
- The Gupta–Radovanović primal-dual algorithm, which has an O(√(BT)) guarantee for every
  distribution, is far worse than both at these sizes.

The study was run on 4 October 2026, 02:19–02:30 BST, on CPU only. It costs $0 in API calls. The
protocol was written before the run (`PROTOCOL.md`, SHA-256 in `RUN_LOG.md`).

## Headline numbers

Mean bins above the exact optimum per instance. Lower is better. Bold marks the best policy tested
on each set.

| Set | Instances | Items | OPT − L1 | Best fit | FunSearch Weibull | FunSearch OR | ab-WorstFit (1, 21) | Sum-of-Squares | SS in FunSearch's view | PD-exp | PD-exp-T |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W5k-released | 5 | 5,000 | 0.00 | 79.20 | 13.60 | 60.20 | 13.60 | **9.60** | 81.40 | 253.60 | 188.20 |
| W5k-fresh | 100 | 5,000 | 0.01 | 79.15 | 13.53 | 60.53 | 13.56 | **10.88** | 81.10 | 252.99 | 188.77 |
| W10k-fresh | 20 | 10,000 | 0.00 | 155.30 | 13.10 | 118.90 | 21.15 | **10.05** | 157.75 | 359.80 | 265.15 |
| W100k-fresh | 5 | 100,000 | 0.00 | 1506.40 | 14.40 | 1189.40 | 153.80 | **10.80** | 1515.60 | 1137.00 | 810.60 |
| OR1 | 20 | 120 | 0.00 | 2.85 | 14.35 | **2.60** | 7.65 | 6.70 | 2.80 | 10.15 | 11.40 |
| OR2 | 20 | 250 | 0.05 | 6.10 | 20.10 | **4.20** | 11.80 | 10.25 | 6.15 | 27.60 | 25.75 |
| OR3 | 20 | 500 | 0.00 | 10.80 | 25.70 | **6.25** | 17.15 | 14.30 | 10.75 | 61.00 | 50.95 |
| OR4 | 20 | 1,000 | 0.00 | 19.80 | 32.60 | **9.90** | 25.65 | 15.75 | 19.70 | 115.80 | 91.15 |

The same results in FunSearch's metric (excess over L1, %):

| Set | Best fit | FunSearch Weibull | Sum-of-Squares |
|---|---|---|---|
| W5k-released | 3.984 | 0.684 | **0.483** |
| W5k-fresh | 3.990 | 0.682 | **0.549** |
| W10k-fresh | 3.910 | 0.330 | **0.253** |
| W100k-fresh | 3.795 | 0.036 | **0.027** |

- **5k, FunSearch's released data:** our best fit (3.984%) and FunSearch heuristic (0.684%)
  reproduce FunSearch's published 3.98% and 0.68% exactly.
- **10k and 100k:** FunSearch reports 0.32% and 0.03% for its heuristic, and best fit 3.90% at 10k
  (its SI A.3). On fresh instances from our generator we get 0.330% and 0.036%, and best fit
  3.910% and 3.795%. That is consistent with the published values, not a reproduction: the
  instances differ.
- **OR1–OR4:** our FS-OR excesses (5.30, 4.19, 3.11, 2.47%) equal FunSearch's published OR numbers.

Primary contrasts, in bins per instance, with 95% paired bootstrap intervals over instances:

| Set | SS − FS-W | PD-exp − FS-W | SS − FS-OR | PD-exp − FS-OR |
|---|---|---|---|---|
| W5k-released | −4.00 [−7.20, −0.40], 4/0/1 | +240.0 | −50.6 | +193.4 |
| W5k-fresh | **−2.65 [−3.07, −2.24], 84/11/5** | +239.5 | −49.7 | +192.5 |
| W10k-fresh | −3.05 [−4.10, −1.95], 17/1/2 | +346.7 | −108.9 | +240.9 |
| W100k-fresh | −3.60 [−4.80, −2.20], 5/0/0 | +1122.6 | −1178.6 | −52.4 |
| OR1 | −7.65 | −4.20 | +4.10 [+3.60, +4.65], 0/0/20 | +7.55 |
| OR2 | −9.85 | +7.50 | +6.05 [+5.50, +6.65], 0/0/20 | +23.40 |
| OR3 | −11.40 | +35.30 | +8.05 [+7.45, +8.60], 0/0/20 | +54.75 |
| OR4 | −16.85 | +83.20 | +5.85 [+5.05, +6.65], 0/0/20 | +105.90 |

- **Pre-registered contrasts:** P1 and P2 on the four Weibull sets, P3 and P4 on the four OR sets.
  All 16 intervals exclude 0. The other 16 cells (cross-domain contrasts) are supplementary.
- **The two 5-instance sets:** their percentile-bootstrap intervals under-cover at n = 5, so they
  are descriptive only.
- Full intervals and sign tests are in [tables.md](tables.md).
- On W5k-fresh the Holm-adjusted sign test gives p = 1.4e-19 for SS − FS-W and p ≤ 6.3e-30 for
  the other three contrasts.

## What this means

1. **FunSearch's Weibull heuristic is close to optimal, and a 2006 algorithm is closer.** From 5k
   to 100k items, both have roughly constant waste above the optimum. That is consistent with
   bounded waste, though three lengths, with only 5 instances at 100k, cannot establish an
   asymptotic rate. SS's guarantee on bounded-waste distributions is O(log n). SS's waste is about
   20–30% lower: 10.9 against 13.5 bins at 5k; 10.8 against 14.4 at 100k.
   - The distribution is bounded-waste (below), so an online policy could in principle stay within
     O(1) bins of the optimum.
   - SS gets about 10 bins. A separate session reports a known-horizon, distribution-learning
     policy at 1.6–2.1 bins in its confirmatory study (online-beyond-ss-v1; see Next steps).
2. **SS needs state that FunSearch's template does not present.** FunSearch's `priority`
   function template sees only the bins the current item fits in, and is written as a pure
   function. Its evaluator does allow module-level state; a sibling study ran a stateful
   `priority` through FunSearch's full evaluator and got identical bin counts.
   - SS restricted to that view (SS-view) loses all its advantage: 81.1 bins above the optimum,
     best fit 79.2.
   - The same rule with its own placement history reaches 10.9.
   - We tested only this one stateless restriction, so we did not measure the best that a stateless
     function can do. FS-W itself reaches 13.5 within that view.
   - Our `problems/bin_packing_online` states explicitly that the function may keep state.
3. **The comparison set matters.** FunSearch, Herrmann & Pallez and Sim et al. compare evolved
   heuristics with Any-Fit rules only.
   - Best fit is 79 bins above the optimum on Weibull 5k, which makes a 65-bin gain look large.
   - Against SS, FunSearch's Weibull heuristic is 2.6–4 bins per instance behind.
4. **No single classical rule dominates.** On OR1–OR4, FunSearch's OR heuristic beats SS by 4–8
   bins per instance, and best fit is within 0.25 bins of it on OR1.
   - The OR generator (uniform 20–100, capacity 150) is also bounded-waste by our LP, so SS's loss
     there is not the linear-waste failure the theory warns about.
   - SS's waste over the optimum grows from 6.7 to 15.8 bins between 120 and 1,000 items. A
     hypothesis, untested here: these instances are too short for SS's asymptotic behaviour.
5. **Guarantees are not performance at these sizes.** PD-exp's guarantee holds for every
   distribution: √(8BT) for the open-ended version (their Theorem 3), which is 2,000 bins at
   B = 100, T = 5,000. That allows the 250 bins it wastes at 5,000 items and 1,137 at 100,000. An
   implementation check on the paper's own Figure 3 distributions reproduces its qualitative
   behaviour (below), so this is the algorithm, not a bug.
6. **Herrmann & Pallez's tuned rule does not scale with length.** ab-WorstFit (1, 21), tuned for
   5,000 items, ties FunSearch's heuristic at 5k (13.56 against 13.53). It falls behind at 10k
   (21.2 against 13.1) and at 100k (153.8 against 14.4). This is a secondary observation, not a
   pre-registered contrast.

## Distribution class

| Distribution | Minimum LP waste per item | Interior of the perfect-packing cone? | Class |
|---|---|---|---|
| Weibull(45, 3), truncated to integers, clipped to 1..100, C = 100 (FunSearch's) | 5.6e-17 (zero) | yes: every ±t margin reached its cap of 1, in units where the smallest probability is 1 | bounded waste |
| Uniform{20..100}, C = 150 (OR-Library u-class) | 5.6e-17 (zero) | yes | bounded waste |

- For bounded-waste distributions the optimal offline waste is O(1).
- SS's expected waste is at most O(log n), and the SS′ variant's is O(1) (Csirik et al. 2006).
- The flat 10–11 bins of SS from 5k to 100k items fit that.

Sources: `distribution_class.json`, `distribution_class_or.json`.

## What was done

**Instances.**
- FunSearch's 5 released Weibull 5k test instances, from `experiments/bp-ceiling-v1`.
- OR-Library `binpack1`–`binpack4`, 80 instances, stored in `data/`.
- 125 fresh Weibull instances from `verify.items_for`, seeds 81000–83004, never used before.

**Policies.**
- Best fit; FunSearch's two heuristics, verbatim, in FunSearch's evaluator; ab-WorstFit (1, 21).
- SS; SS restricted to FunSearch's view.
- PD-exp, open-ended and known-horizon settings, with the paper's parameters and no tuning.

**Optimum.** Exact, from the arc-flow integer program solved with HiGHS; all 210 solves proved
optimal; at most 43 s.

**Work log** (times in BST; details in `RUN_LOG.md`).
- **Before about 01:46, exploratory probe** (`sos_probe.py`, `sos_probe.log`). SS against best fit and
  FunSearch on the released data and fresh instances from other seed ranges. It found SS ahead on
  Weibull and behind on OR3. The probe is disclosed in the protocol, and its instances are not
  reused.
- **Literature check.**
  - An agent found no paper comparing SS, primal-dual or re-solving policies with FunSearch
    (`docs/literature/research-directions.md` on branch `docs/research-directions`).
  - FunSearch's follow-ups (Herrmann & Pallez, arXiv 2510.27353; Sim et al., arXiv 2501.11411)
    compare with Any-Fit rules only.
- **01:48, protocol.** Written and hashed. Its stated time was then corrected from 01:50 to 01:48
  and it was rehashed, before any confirmatory code ran.
- **Pre-run checks** (`checks.py`, `checks.json`).
  - The compact FunSearch evaluator, which passes open bins plus two unused ones, equals the full
    evaluator on all 75 policy × instance cases. W100k is only feasible with it.
  - The vectorised ab-WorstFit equals the team's transcription.
  - Arc-flow OPT equals OR-Library's listed value on 76 of 80 instances.
- **The 4 OR-Library mismatches.** On u120_08, u120_19, u250_07 and u250_12, arc-flow found one
  bin fewer than listed.
  - `verify_opt.py` extracted explicit packings that meet L1 (`or_improved_packings.json`).
  - This is known, not a new result. OR-Library's information page says the listed values for these
    instances (and u250_13) are not proven optima, and later work reports the corrected optima
    (e.g. Mathematics 9(13):1540, doi 10.3390/math9131540, which gives 49 for u120_19). Our four packings
    meet the L1 bound, so they are optimal whatever the listings say.
  - We use our OPT.
- **PD-exp's large excess.** We checked it against the paper's own Figure 3 distributions
  (`pd_sanity.py`, `pd_sanity.json`).
  - On the linear-waste distribution, SS's excess grows linearly (37 → 132 → 532 bins at
    T = 1k, 4k, 16k).
  - PD-exp's grows like √T (22 → 45 → 92) and beats SS.
  - On the bounded-waste distribution, SS stays flat (5, 2, 2) and PD-exp grows like √T.
  - This matches the paper, so the implementation is kept as specified.
- **02:19–02:30, confirmatory run** (`run.py`, 2 processes). 210 instances, 1,313 CPU-seconds, of
  which 1,075 were the optimum solves.
- **Deviations from the protocol.**
  - The pre-registered check "OPT must equal OR-Library's listed optimum on all 80" came out 76/80.
    It was resolved by an unplanned script, `verify_opt.py`: explicit packings meeting L1 for the 4
    mismatched instances. This affects bins above OPT on OR1 and OR2 by 0.10 per instance; paired
    contrasts are unchanged.
  - `PROTOCOL.md` names the results file `results.json`; it is `results.jsonl`.
  - The protocol's "4 contrasts × 8 sets" conflicts with its own definition of P1–P4 by domain.
    The 16 domain-matched contrasts are treated as primary.
- **Machine load.** Load averages reached 55 during the checks because of another session's
  `llm-long-search-v1` audit (2 × 8 workers). This affects wall times only, not results; every
  policy is deterministic.

**Pre-stated expectations against outcomes.**

| Expectation | Outcome |
|---|---|
| SS beats FS-W on W5k-fresh | yes |
| SS loses to FS-OR on OR3 | yes |
| PD-exp may lose to SS on Weibull and beat it on OR | it loses on both |

## Limitations

- **One generator for fresh instances.** Our Weibull generator matches FunSearch's released data
  in distribution, not instance by instance (see `verify.py`). On the 5 released instances the
  results agree in direction and size: SS 9.6, FS-W 13.6.
- **Policies, not search methods.** SS uses state that FunSearch's evaluator did not offer. Nothing
  here says FunSearch's search could not find SS given that state.
- **Tie rule.** SS's tie rule (prefer the smaller resulting gap) is our choice; other tie rules
  were not tested.
- **Classical variants not tested.** SS′ (O(1) waste on bounded-waste distributions), SS*, and
  re-solving policies with a known distribution or horizon were not run.
- **Small sets.** W100k has only 5 instances, and W5k-released has 5. Their sign tests cannot
  reach p < 0.05; the intervals are reported instead.
- **Released data seen before the protocol.** The exploratory probe saw the 5 released instances
  before the protocol was written. The confirmatory result rests on the 100 fresh instances.
- **OR instances.** The OR sets are the classic Falkenauer u-instances only. Their item order is as
  published.

## Cost

$0 of API calls. About 22 CPU-minutes for the confirmatory run, plus about 25 for the checks and
the probe, all on the local machine. No Modal.

## Reproduce

From this folder, with the repository's venv (Python 3.12, numpy, scipy ≥ 1.9):

```bash
python checks.py             # pre-run checks -> checks.json (~20 min under heavy load; mostly OR optima)
python run.py --workers 2    # all policies and OPT on 210 instances -> results.jsonl (~12 min)
python report.py             # tables.md and summary.json
python verify_opt.py         # explicit packings for the 4 OR-Library instances listed one bin too high
python pd_sanity.py          # PD-exp implementation check on Gupta & Radovanović's Figure 3 distributions
python -c "import json, frontier as F; json.dump(F.distribution_class(F.weibull_pmf(), 100), open('distribution_class.json','w'), indent=1)"
python sos_probe.py          # the earlier exploratory probe (needs --or3 <datasets.json> for OR3)
```

`data/binpack1.txt`–`binpack4.txt` come from OR-Library
(people.brunel.ac.uk/~mastjjb/jeb/orlib/files/). Their SHA-256 hashes are in `RUN_LOG.md`.

## Evidence index

| File | What it holds |
|---|---|
| `PROTOCOL.md` | Design, written before the run |
| `RUN_LOG.md` | Protocol hash, times, checks, decisions |
| `results.jsonl` | One row per instance: L1, L2, OPT (with solver status), bins and seconds per policy |
| `tables.md`, `summary.json` | All tables and contrasts, generated by `report.py` |
| `checks.json` | Evaluator equivalence and OR optimum checks |
| `or_improved_packings.json` | Explicit optimal packings for the 4 mismatched OR-Library instances |
| `distribution_class.json`, `distribution_class_or.json` | Waste class LPs |
| `pd_sanity.json` | PD-exp implementation check |
| `frontier.py`, `run.py`, `report.py`, `checks.py`, `verify_opt.py`, `pd_sanity.py` | Code |
| `sos_probe.py`, `sos_probe.log` | Exploratory probe that preceded the protocol |

## Next steps

1. **Close the gap from 10 to about 2 bins with a confirmed policy.** Session b1's confirmatory
   study (`exp/online-beyond-ss`, `experiments/online-beyond-ss-v1/RESULTS.md`) finished. Its own
   numbers, not re-checked here:
   - FWSS, a size-weighted SS with a best-fit finish that needs the item count, is 1.6–2.1 bins
     above OPT on Weibull from 1k to 100k items. Its SS gets 9.6–10.9 and FS-W 13.4–14.0.
   - b1's SS on the released set matches ours (9.6).
   - Without the horizon, the same weights do worse than plain SS. So plain SS remains the best
     horizon-free policy found.
   - On OR3 and OR4, FWSS beats FS-OR.
2. **Ask whether an LLM loop finds SS when the interface allows state.** Partly answered by
   llm-long-search-v1 (merged in PR #5): 4 × 300 DeepSeek steps for $0.80.
   - The best rules kept a running histogram of item sizes and reached 96.8% of FunSearch's gain
     over best fit.
   - SS beat all four runs, and FunSearch too (−0.17 pp [−0.20, −0.14]).
   - Follow-up `llm-from-ss-v1` (branch `exp/llm-from-ss`, started 05:40 BST on 4 Oct, HF cap
     $2.50) asks the next question: starting from SS, can the loop find a better policy?
3. **Explain why ab-WorstFit (1, 21) degrades with length** while FunSearch's heuristic does not.
   Tune ab per length to see whether a two-threshold rule can stay at O(1) waste.
4. **Test SS′ and SS*** for the theoretical O(1) constant. Test SS variants on the short OR
   instances, where FS-OR still wins.
5. **Write up.** A short note: "FunSearch's bin-packing benchmark: optimum, classical baselines,
   and interface". It updates the bin-packing headroom paper draft, whose headroom framing should
   now be measured against the optimum, not best fit.

## Corrections after independent review (4 October 2026)

An independent reviewer (a subagent of session b1, at the user's request) recomputed every number
from `results.jsonl` and found no mismatch and no code bug that changes a conclusion. It
re-implemented SS and FunSearch's full evaluator on 2 released instances and got the same bin
counts. Its report is `docs/reviews/2026-10-04-online-frontier-v1.md`, on branch
`fix/obss-u250-12` when this was written.

Corrections made, each checked here against the data or the source:

1. **The interface claim.** The overreaching "interface's ceiling" claim is replaced. Only one
   stateless restriction was tested, and FunSearch's evaluator permits state (§ What this means,
   2).
2. **A failed pre-registered check** (OR optima, 76/80) is now listed as a deviation, together
   with two smaller ones.
3. **The 5-instance released set** is reported descriptively, with the t-interval and sign test.
4. **The contrast count.** "32/32" is replaced by 16/16 pre-registered contrasts; the other 16 are
   labelled supplementary.
5. **Asymptotic language** is softened, and the OR explanation is labelled a hypothesis.
6. **The comparison with FunSearch's published numbers** is restated per length: the 5k and OR
   values are exact reproductions; 10k and 100k are consistent.
7. **PD-exp's bound** is now Theorem 3's √(8BT) = 2,000 for the open-ended version (checked in the
   paper). `RUN_LOG.md`'s √(4BT) applied to PD-exp-T.
8. **Documentation errors.**
   - The OR data SHA-256 hashes are now in `RUN_LOG.md`.
   - Checks plus probe took about 25 CPU-minutes, not 10. The OR optima alone took 1,475 s.
   - The probe ran before about 01:46, not "before 01:34".
   - `frontier.py`'s compact-evaluator docstring now points to the argument here: positions past
     top + 2 all score as position top + 2 does. The reviewer checked this analytically for FS-W,
     FS-OR, ab-WF and SS-view.
   - The sibling study is no longer described as unconfirmed.
9. **u250_13.** The MILP also proves OR-Library's listed 103 optimal (dual bound 103 > L2 = 102),
   although OR-Library lists it as unproven.
