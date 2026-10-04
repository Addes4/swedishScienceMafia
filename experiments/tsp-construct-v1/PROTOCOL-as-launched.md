# tsp-construct-v1: protocol for the confirmatory run

Drafted on 4 October 2026 at 06:10 BST and revised at 06:30 BST, after the literature search
(`literature.md`) and before any heuristic was run on a test set. The only test-set computation
before this point was the LKH reference, which is a positive control on the optimum. The final
text's SHA-256 and the time are recorded in `RUN_LOG.md` before the first confirmatory command.
Nothing can be committed without the user's approval, so the hash stands in for a commit timestamp.

**Why the draft was revised.** The draft's H1 asked whether farthest insertion beats every published
LLM step-by-step result. The literature search then found three things:
- Newer methods (TIDE 4.76% at n = 50, SimpleEvol, HiFo-Prompt at n = 200) beat farthest insertion
  by running rollouts and 2-opt inside `select_next_node`.
- RouteRepair (arXiv 2609.11452) already places farthest insertion next to its own LLM constructor.
- No paper normalises for compute.

The question was therefore re-centred on the interface and compute. The draft's H1 is kept, as H3,
and restricted to the comparisons that remain open.

## Question

LLM-based automatic heuristic design (AHD) papers benchmark a "step-by-step construction" task for the
TSP. This lineage includes AEL, ReEvo, EoH, MCTS-AHD, CALM, MoH, HiFo-Prompt, Clade-AHD, PathWise,
TIDE and SimpleEvol. The LLM writes `select_next_node(current_node, destination_node,
unvisited_nodes, distance_matrix)`, and the tour is built by appending its answers. The only manual
baseline these papers report on random instances is nearest neighbour.

The function receives the whole instance at every call, so it can plan a complete tour and emit it
one node at a time. Recent best methods already do part of this: rollouts, MST look-ahead, or 2-opt
inside each call.

1. What is the benchmark's ceiling inside its own interface, and how much compute does reaching it
   cost?
2. Measured on the same instances and the same machine, are the released LLM-designed heuristics
   Pareto-dominated in time and tour length by classical constructions from 1958–1977 emitted
   through the interface?
3. Does farthest insertion (1977), with no local search, already beat the MCTS-AHD-lineage results
   that report only nearest neighbour as a baseline?

## Test sets

| Set | Source | Instances | n |
|---|---|---|---|
| `mctsahd_test50/100/200` | MCTS-AHD's released `test{50,100,200}_dataset.npy`, used by MCTS-AHD, CALM, Clade-AHD, RedAHD and TIDE (n = 50). They regenerate exactly from `np.random.seed(1234)` in their `gen_inst.py` (`make_data.py`; SHA-256 checked). | 1,000 each | 50, 100, 200 |
| `fresh50/100/200` | Ours: instance with seed s is `np.random.default_rng(s).random((n, 2))`. Seeds 200000–200999 (n = 50), 201000–201999 (n = 100), 202000–202199 (n = 200). | 1,000 / 1,000 / 200 | 50, 100, 200 |

Development used only MCTS-AHD's `val{50,100,200}` sets (64 instances each). No method has a
parameter fitted to any set; the classical methods have no parameters.

**Reference.** LKH through elkai 2.0.1 (RUNS = 3, MAX_TRIALS = n, SEED = 1). Coordinates are scaled by
1e7 as EUC_2D, and the returned tour is measured in float coordinates.

**Positive control on the reference.** MCTS-AHD publishes optimum means of 5.675 / 7.768 / 10.659.
- Our values: 5.675483 and 7.768032 at n = 50 and 100, both within 0.001.
- At n = 200 we get 10.708149, which is +0.049 (+0.46%).
  - On 8 test200 instances, heavier LKH (RUNS = 10, MAX_TRIALS = 2000) gave identical tours.
  - PathWise (arXiv 2601.20539) reports 10.709 as the LKH-3 mean on its own n = 200 instances.
- Check in the run: heavy LKH (RUNS = 10, MAX_TRIALS = 10000, MCTS-AHD's setting) on the first 20
  test200 instances. If any tour is shorter than ours by more than 1e-6, every n = 200 result uses
  the heavy values where available, and the discrepancy is reported as unresolved.
- Published n = 200 gaps that use 10.659 are also re-expressed against our reference:
  (1 + g) · 10.659 / 10.708 − 1.

## Methods

**B. Released LLM-designed heuristics, re-run.** Each runs through `eval_interface.py`, whose loop is
copied verbatim from MCTS-AHD's `eval.py` (identical to ReEvo's).

| Name | Source (pinned commit in file header) | Mechanism |
|---|---|---|
| `mctsahd_gpt4omini_best` | MCTS-AHD `gpt.py`, "the leading heuristic" | nearest-neighbour rollout per candidate, weighted 0.7/0.3 |
| `hifo_best` | HiFo-Prompt `examples/tsp_construct/evaluation/heuristic.py` | 8 identical NN rollouts per candidate, plus regions |
| `reevo_best` | ReEvo test notebook | scoring rule |
| `ael_best` | ReEvo test notebook (AEL's) | scoring rule |
| `refineevo_released` | RefineEvo `gpt.py` (fetched; not the paper's Opus heuristic) | scoring rule, uses `random` |
| `clade_released` | Clade-AHD `gpt.py` (fetched) | scoring rule |

**C. Classical, outside the interface** (`tspalgs.py`, numba). Nearest neighbour; nearest, random,
cheapest and farthest insertion; greedy edge; Clarke–Wright savings. Each is run alone, with 2-opt,
and with 2-opt and Or-opt. Reported for context, with no hypothesis.

**D. Classical, inside the interface.** Each is a `select_next_node`, numpy only unless stated, and
runs through the same loop.
- `nearest_neighbour`: the papers' baseline.
- `fi_emit`: builds farthest insertion over all nodes from `distance_matrix` (Rosenkrantz, Stearns
  and Lewis 1977) and returns the node after `current_node`. Its output depends only on its four
  arguments.
- `greedy_ls_emit`: greedy edge, then 2-opt (Croes 1958) and Or-opt (Or 1976) to a joint local
  optimum, emitted the same way. A cache keyed on the matrix bytes holds the plan within an instance;
  it changes speed, not answers.
- `lkh_emit` (exploratory ceiling): the LKH tour emitted the same way. It needs the compiled elkai
  package.
- `fi_replan`, `nn_rollout` (exploratory): replanned and rollout variants.

**Instances per heuristic.** The slow released heuristics are run on a fixed prefix of each set,
chosen now so that each run takes about 1 CPU-hour or less:

| Heuristic | test50 | test100 | test200 | fresh50 | fresh100 | fresh200 |
|---|---|---|---|---|---|---|
| `mctsahd_gpt4omini_best` | 1000 | 1000 | first 200 | first 200 | first 200 | first 50 |
| `hifo_best` | 1000 | first 200 | first 50 | first 200 | first 100 | first 25 |
| all other heuristics | all | all | all | all | all | all |

## Metrics

- **Gap** = mean tour length / mean LKH length − 1 (ratio of means), as in MCTS-AHD's Table 1, over
  the instances a heuristic was run on. The mean per-instance gap is also reported.
- **Paired difference** between two heuristics on their common instances: the mean per-instance
  length difference, with a 95% percentile bootstrap CI (10,000 resamples, numpy seed 0) and
  wins/ties/losses.
- **Time.** Median wall seconds per instance, recorded inside each worker process. The machine is
  shared and heavily loaded (load average about 60 on 10 cores), so absolute times are inflated.
  Speed comparisons are reported as ratios within a set, and as orders of magnitude.

## Pre-registered hypotheses and decision rules

**H1 (the interface allows a new best at low cost).** On `mctsahd_test{50,100,200}`, `greedy_ls_emit`'s
gap is below the best published pure step-by-step result at each n in `literature.md` §1a:
- n = 50: 4.76% (TIDE);
- n = 100: 6.47% (SimpleEvol), reported together with TIDE's 7.15%;
- n = 200: 8.877% (HiFo-Prompt), and also after the 10.659 → 10.708 re-expression where a paper
  used MCTS-AHD's reference.

RefineEvo's Claude Opus objectives, which give an inferred ≈3.3% at n = 100 and ≈4.7% at n = 200, are
reported as a secondary comparison and flagged as inferred.

**H2 (Pareto dominance over the released heuristics).** For each re-run released heuristic h and each
n, on `mctsahd_test`, some interface method c in {`nearest_neighbour`, `fi_emit`,
`greedy_ls_emit`} satisfies both of these:
- paired length difference c − h with a 95% CI entirely below 0;
- median time per instance of c ≤ that of h.

A tie with nearest neighbour counts as a failure of H2 for that h, because a strict improvement is
required.

**H3 (missing baseline in the MCTS-AHD lineage).** `fi_emit`'s gap on `mctsahd_test{50,100,200}` is
below:
- every LLM row of MCTS-AHD Table 1;
- CALM Table 2;
- Clade-AHD Table I;
- MoH Table 1;
- PathWise Table 1.

The rows are listed in `literature.md`. It is reported separately for each n and each paper. Its
paired difference with `mctsahd_gpt4omini_best`, `reevo_best` and `ael_best` has a 95% CI below 0.

**H4 (robustness).** On `fresh50/100/200`, the signs of the H2 and H3 paired comparisons are the same
as on `mctsahd_test`.

Exploratory, not tested: `lkh_emit`, `fi_replan` and `nn_rollout`; every classical construction in C;
behavioural notes on the released heuristics. One example: on the validation set,
`clade_released` gave exactly nearest neighbour's mean length.

## What would change the conclusion

- **A published pure step-by-step gap below `greedy_ls_emit`'s:** H1 fails for that n, and the claim
  becomes a cost comparison only.
- **The heavy-LKH check finding shorter tours at n = 200:** our n = 200 gaps would be overstated, and
  the 10.659 discrepancy would be ours, not MCTS-AHD's.

## Out of scope

- Other LLM-AHD frameworks for the TSP (GLS, ACO, POMO/LEHD); the TSP-GLS variant is already compared
  with KGLS and LKH in its papers.
- Other problems (KP, CVRP, PFSP).
- Unreleased heuristics (TIDE, SimpleEvol, RefineEvo-Opus): only their published numbers are used.
- No LLM calls are made, and there is no spend.
