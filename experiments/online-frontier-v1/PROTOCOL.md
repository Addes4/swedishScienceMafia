# online-frontier-v1: protocol (written before the confirmatory run)

Written at 01:48 BST on 4 October 2026, after an exploratory probe and before any run of the code
below. The protocol cannot be committed yet (no commit approval), so its SHA-256 and the time are
recorded in `RUN_LOG.md` before the first run.

## Question

On FunSearch's online bin-packing benchmarks, how far is each heuristic from the offline optimum?
How does FunSearch's evolved heuristic compare with classical online algorithms that come with
guarantees for i.i.d. item sizes?

Background:
- FunSearch (Romera-Paredes et al., Nature 2024) reports results only against hand-written
  Any-Fit rules. So do the studies that re-examine it: Herrmann & Pallez (arXiv 2510.27353) and
  Sim, Renau & Hart (arXiv 2501.11411).
- Our literature check (`context/research-directions.md`, branch `docs/research-directions`)
  found no paper that runs Sum-of-Squares or the Gupta–Radovanović primal-dual algorithm on these
  benchmarks.

## Disclosure: what was seen before this protocol

An exploratory probe (`sos_probe.py`, output in `sos_probe.log`) ran Sum-of-Squares (SS), best fit
and FunSearch's heuristics. Data:
- FunSearch's released Weibull 5k and OR3 data;
- fresh instances from seeds 50000–50399, 51000–51099, 52000–52019, 53000–53003, 60000–60009,
  61000–61004 and 62000–62001.

What it showed:
- On Weibull 5k, SS beat FunSearch's Weibull heuristic: 0.483% vs 0.684% over L1 on the released
  data; 19 of 20 fresh instances.
- SS lost to best fit and to FunSearch's OR heuristic on OR3.

Nothing else in this protocol was run before it was written. The confirmatory instances below are
new and none of the probe's instances are reused.

## Instances

| Set | Source | Instances | Items | Capacity |
|---|---|---|---|---|
| W5k-released | FunSearch's released Weibull 5k test data (`experiments/bp-ceiling-v1/funsearch_weibull5k_test.json.gz`) | 5 | 5,000 | 100 |
| OR1–OR4 | OR-Library `binpack1`–`binpack4` (Falkenauer's u120, u250, u500, u1000), downloaded from people.brunel.ac.uk/~mastjjb/jeb/orlib/; the probe confirmed OR3 is item-for-item FunSearch's OR3 | 20 each | 120, 250, 500, 1,000 | 150 |
| W5k-fresh | `verify.items_for(seed, 5000)`, seeds 81000–81099 | 100 | 5,000 | 100 |
| W10k-fresh | seeds 82000–82019 | 20 | 10,000 | 100 |
| W100k-fresh | seeds 83000–83004 | 5 | 100,000 | 100 |

## Policies

All policies are online: each item is placed before the next one is seen.

| Policy | Definition | State it uses |
|---|---|---|
| BF | Best fit | Open-bin gaps |
| FS-W, FS-OR | FunSearch's Weibull and OR heuristics, verbatim, in FunSearch's evaluator (the `priority` function sees only bins the item fits in, including unused ones, in bin order; ties go to the first bin) | That view only |
| ab-WF | Herrmann & Pallez's ab-WorstFit with their published a = 1, b = 21 (`falsify/funsearch_heuristics.py`) | Open-bin gaps |
| SS | Sum-of-Squares (Csirik et al., JACM 2006): minimise Σ_{0<g<C} N(g)², where N(g) is the number of open bins with gap g; ties go to the smaller resulting gap | Full gap histogram |
| SS-view | SS restricted to FunSearch's stateless view: N(g) counted only over the bins shown | That view only |
| PD-exp | Gupta & Radovanović (Oper. Res. 2020, arXiv 1211.2687), Algorithm 1: greedily minimise Σ_{h=1..C} N(h) + (κ/ε_t) Σ_{h=1..C−1} exp(−ε_t N(h)) over fill levels h | Full histogram |
| PD-exp-T | PD-exp with the known-horizon setting of their Theorem 2 | Full histogram plus the item count T |

PD-exp uses the open-ended setting of their Theorem 3: ε_t = √(C / (2(t+1))), κ = 1. PD-exp-T
uses ε = √(C/T), κ = 1. Ties go to the smaller resulting gap. No parameter is tuned.

FunSearch's two heuristics are run with a compact evaluator that passes the open bins and two
unused bins instead of all n bins. Before use it must reproduce the full evaluator's bin counts
exactly on all W5k-released and OR3 instances. If it does not, the full evaluator is used and
W100k-fresh is dropped for FS-W and FS-OR.

## Reference values

- **OPT:** the exact offline optimum, from the arc-flow integer program (Valério de Carvalho
  1999) solved with HiGHS through `scipy.optimize.milp`.
  - Check: OPT must equal OR-Library's listed optimum on all 80 OR instances.
  - If a solve does not prove optimality within 600 s, the best bound and incumbent are recorded
    and the instance is reported separately.
- **L1** = ⌈Σ sizes / C⌉ (FunSearch's metric); **L2** is Martello–Toth.

## Endpoints

**Primary.** For each instance set and policy, mean bins above OPT per instance. For each set,
these paired contrasts:
- (P1) SS − FS-W and (P2) PD-exp − FS-W on the Weibull sets;
- (P3) SS − FS-OR and (P4) PD-exp − FS-OR on OR1–OR4.

Each contrast is reported as a mean difference in bins per instance, with a 95% paired bootstrap
interval over instances (10,000 resamples, seed 20261004) and wins/ties/losses. With 4
contrasts × 8 sets, intervals are reported unadjusted, together with the count of contrasts whose
interval excludes 0. A Holm-adjusted sign test is added for the four contrasts on W5k-fresh.

**Secondary.**
- Excess over L1 in percent, for comparison with FunSearch's Table 1.
- How waste above OPT grows from 5k to 100k items.
- SS-view against SS: the cost of FunSearch's stateless interface.
- ab-WF.
- Wall time per policy.

**Distribution class.** Weibull(45, 3), truncated to integers and clipped to 1..100 as in
`verify.items_for`. Using the arc-flow linear program on its exact probabilities:
- **Waste rate:** linear waste if the minimum expected waste per item is above 0.
- **Interior:** otherwise, whether p lies in the interior of the cone of perfect packings. This
  separates bounded waste from √n waste (Courcoubetis–Weber, as stated by Csirik et al.). It is
  tested with LPs that move p by ±t along each size.

## Pre-stated expectations (from the probe and from theory)

- SS beats FS-W on W5k-fresh. This expectation comes from the probe.
- SS loses to FS-OR on OR3.
- PD-exp has an O(√n) guarantee for every distribution, so it may lose to SS on bounded-waste
  Weibull and beat it on OR.

None of these is a hypothesis we have tested before, except the first two.

## What will not be claimed

- Nothing about FunSearch's search procedure. Its evaluator did not offer SS's state, and this
  study compares policies, not search methods.
- No claim on instance families other than those listed.
- No claim that an LLM could not find these policies.

## Cost

CPU only, on the local machine, and no API calls. At most two processes, because timed runs from
another study share the machine.

## Files

- `PROTOCOL.md`: this file.
- `RUN_LOG.md`: hash, times, decisions, incidents.
- `frontier.py`: policies, evaluators, arc-flow solver, distribution LP.
- `run.py`: produces `results.json`.
- `report.py`: produces `tables.md` from `results.json`.
- `RESULTS.md`: the write-up.
- `sos_probe.py`, `sos_probe.log`: the earlier exploratory probe.
