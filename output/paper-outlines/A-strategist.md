# Paper A outline: Strategist

Status: outline, 3 October 2026. Evidence is from `strategist/RESULTS.md` (v1, on main) and
`experiments/strategist-v2/RESULTS.md` (v2, branch `exp/strategist-v2`). Related work is in
[context/related-work.md](../../context/related-work.md).

## Working title

*When to Leave: a Cost-Aware Marginal-Value Rule for Switching Search Strategy, and Controls that
Separate Timing from Luck*

## Thesis

Adaptive controllers for search strategy are usually compared on final score only. That cannot
show whether they gained from *when* they switched or from *which* moves they happened to use. We
propose a leave rule taken from the marginal value theorem that charges each move its cost. We
also propose two controls: timing-shuffled replay of the same moves, and counterfactual forks at
each switch point. In pre-registered runs over 200 seeds, timing matters on some landscapes
(Heilbronn, NK) and not on others (LABS). The forks found premature switching, and fixing it cut
premature switches on LABS from 48% to 21%. A tuned patience rule remains competitive, so we
report "no universal winner" (as Gupta et al. 2026 found for LLM harnesses), not a new champion.

## Contributions

1. **The controller:** leader line plus excursions, a cost-weighted marginal-value leave rule,
   Thompson sampling over edit, rewrite and crossover per stall context, and a crossover gate (v2).
2. **Two controls that separate timing from move mix:** timing-shuffled replay and counterfactual
   forks with a premature-switch share. None of AdaEvolve, PACEvolve, MetaMax or the Gupta et al.
   harnesses has them.
3. **A pre-registered evaluation with a documented winner's curse:** dev, validation and
   confirmatory seed blocks. The dev estimate fell from J = +0.236 to +0.132 on validation and
   was +0.209 on the confirmatory seeds.

## Evidence we have

**v1** (200 confirmatory seeds, 4 benchmarks, budget 3,000):
- Beats uniform random moves everywhere.
- Beats the static mix on LABS and NK.
- Timing matters on Heilbronn (130/0/70 against shuffled timing).
- A patience rule tuned after the fact wins on LABS and NK.

**v2** (dev / validation / confirmatory seeds 3000–3199):

| | LABS | Heilbronn | NK |
|---|---|---|---|
| v2 − v1 | +0.137 [0.043, 0.236] | ~ | +0.00577 [0.00236, 0.00915] |
| v2 − shuffled timing | ~ +0.082 | +0.00102 [0.00064, 0.00140] | +0.00746 [0.00397, 0.0109] |
| v2 − patience tuned on dev | −0.220 [−0.307, −0.132] | +0.00049 [0.00003, 0.00093] | ~ −0.00505 |
| premature share at switch points, v1 → v2 | 48% → 21% | 97% → 98% | 55% → 34% |

- Most of v2's gain comes from the crossover gate. The excursion cap and the recent-improvement
  test show no effect.
- Uniform-cost sensitivity: the LABS gain holds (+0.166).
- Runs give identical final scores on Linux (Modal) and macOS.

## What is missing (in priority order)

| # | Gap | Why reviewers will ask | Cost |
|---|---|---|---|
| 1 | **Baselines:** MetaMax (György & Kocsis 2011), Luby restarts, bet-and-run, an AdaEvolve-style controller (UCB over lines, spawn on stall), PACEvolve's backtrack-or-crossover rule, and adaptive operator selection (dynamic multi-armed bandit or adaptive pursuit) | They are the prior art. Without them the novelty claim reduces to "a new heuristic". | CPU only; each is a `Controller` subclass |
| 2 | **Real LLM moves on at least two problems:** diff, rewrite, two-parent merge and write-from-scratch prompts, charged by measured tokens (`strategist/costs.py` already accepts measured costs) | The motivation is LLM search, and the moves are proxies. This is the main weakness. | API spend; use circle packing or Heilbronn from `problems/`, a few seeds |
| 3 | **Anytime curves and a budget sweep**, not one 3,000-unit budget | Oved et al. 2026 show rankings flip with budget | CPU only |
| 4 | **Longer fork windows** (v1 used 300 units) and seed-clustered intervals throughout | Short windows understate restarts that pay off late | CPU only |
| 5 | **Why timing matters on Heilbronn and NK but not LABS:** relate it to landscape features (ruggedness, plateau length, how stalls are distributed) | Turns an observation into an explanation | Analysis of existing traces |

## Section plan

1. **Introduction.** Strategy choice in LLM evolution (diff vs rewrite vs merge vs restart).
   Current controllers are judged on final score alone. Our question: is adaptation real, or
   is it timing luck? Contributions.
2. **Related work.**
   - Adaptive operator selection: Thierens 2005, Da Costa et al. 2008, Fialho et al. 2008/2010.
   - Restarts: Luby et al. 1993, MetaMax 2011, bet-and-run 2017.
   - Foraging and the marginal value theorem: Charnov 1976; Davidson & El Hady 2019 and
     Kilpatrick et al. 2021 on leaving under noisy estimates.
   - LLM-era controllers: AdaEvolve, PACEvolve, Gupta et al. 2026, Relay Don't Route.
   - Evaluation pitfalls: Oved et al. 2026, Cawley & Talbot 2010.
3. **Method.**
   - Leader line and excursions.
   - The leave rule: the leader's expected yield against the progress per cost that excursions
     delivered, credited only for overtaking the best.
   - When to abandon an excursion.
   - Thompson sampling per stall context; move costs.
   - The v2 changes.
   - `Adaptive.explain` for inspecting each decision.
4. **Controls.** Timing-shuffled replay (same moves, same total cost). Counterfactual forks and
   the premature-switch share. Seed blocks and pre-registration.
5. **Setup.** Benchmarks (LABS n = 40, Heilbronn n = 12, NK N = 48 K = 6; plus the LLM problems from
   gap 2), budgets, cost tables, statistics (paired bootstrap, sign test, Holm correction,
   seed-clustered intervals).
6. **Results.**
   - 6.1 Against fixed move mixes and the new baselines (gap 1).
   - 6.2 Timing against shuffled timing.
   - 6.3 Against patience and restart schedules.
   - 6.4 Forks diagnose premature switching, and the v2 fix.
   - 6.5 Ablations: the crossover gate does most of the work.
   - 6.6 Cost sensitivity.
   - 6.7 LLM moves (gap 2).
7. **Discussion.** There is no universal winner. The controls are the transferable contribution,
   and any adaptive controller can be audited with them. When does timing matter (gap 5)?
8. **Limitations.** Proxy moves (unless gap 2 is done), one problem size per benchmark, small
   effect sizes, patience still wins on LABS.

**Figures:**
1. A narrated switch timeline (from `strategist.demo`).
2. Primary comparisons with intervals (`comparisons.png`).
3. Premature-switch share, v1 vs v2.
4. Anytime curves (gap 3).
5. Ablation bars.

## Likely reviewer objections

- **"Proxy moves are not LLM search."** Gap 2 answers this; until then, frame the paper as a
  study of controllers on classic black-box benchmarks.
- **"AdaEvolve already does this."** Its mechanism has no move costs and never abandons an
  island, and no paper we found separates timing from move mix. Gap 1 must show the comparison.
- **"The patience rule wins, so why use yours?"** It needs no tuning. Its worst-case gap to the
  best arm across benchmarks is 5.0%, against 5.3% for patience tuned per benchmark. That margin
  is small, so present it as robustness, not superiority.

## Venues (check current deadlines; none were verified)

- GECCO or PPSN: the evolutionary-computation community, where the restart and
  operator-selection prior art lives.
- EvoStar / EvoApplications.
- A workshop on agents or automated algorithm discovery at NeurIPS or ICLR.
- TMLR, which takes submissions at any time.

## Before writing

- Run gaps 1 and 2 first; they decide whether the paper is a methods paper or an
  evaluation-methodology note.
- Search the literature again for 2026 work on strategy controllers and timing controls.
