# Research directions: where we could make new findings

Written 4 October 2026, 01:30–02:00 BST, after reading the repository at `554abdc`, the three
workshop-paper drafts and their ledgers, and each study's next steps. For each candidate direction
a search agent checked the literature (arXiv API, OpenAlex, Semantic Scholar, publishers). Every
paper below was confirmed to exist by the agent that cited it. Most 2026 items are preprints, and
several verdicts rest on abstracts. "Not done" means not found in that search, not proven absent.

One direction was also probed on CPU (no API spend): [probes/sos_probe.py](probes/sos_probe.py), with
its output in [probes/sos_probe.log](probes/sos_probe.log). The probe is exploratory, not
pre-registered.

## Summary

| # | Direction | Literature verdict | What we already have | Cost to a first result |
|---|---|---|---|---|
| 1 | Classical online bin-packing algorithms (Sum-of-Squares and successors) against FunSearch | **Not done** | Probe: Sum-of-Squares beats FunSearch's heuristic on FunSearch's own released Weibull 5k data | CPU only, hours |
| 2 | Adaptive overfitting in LLM program search, and Ladder/Thresholdout as the promotion rule | Partly done (gap measured once; Ladder/Thresholdout as a promotion rule not done) | Hidden audits, gate replay harness (gate-v3), 0.960 → 0.238 and 1/0 → 3/14 observations | Mostly CPU replays; about $5–20 of LLM calls for a proposal stream |
| 3 | Timing-shuffle and matched-mix controls on an LLM framework's adaptive component | Timing shuffle **not done** anywhere; matched mix done only for two model routers | Strategist's controls, ShinkaEvolve already wired into the tournament | About $20–60 of cheap-model calls |
| 4 | Behavioural no-ops: does failure memory make LLM proposals copy the incumbent, and does dedup before charging help? | Partly done (text-level near-copies in single-task repair); behavioural dedup at matched budget **not done** | memory-ablation-v1 harness and its no-op measurements | About $10–30 |
| 5 | Short-horizon bias: short instances and shrunk counterexamples steer LLM search to myopic rules | Rank reversal is known; its effect on what an LLM loop selects **not done**; shrinking bias **not done** | Length sweep, 2-item counterexample archive | About $10–30 |
| 6 | Unprompted evaluator exploitation measured with proven-optimum canaries | Partly done (one problem, LLM-judge labels) | Gate red team (0/68 prompted), Erdős discrepancy canary | About $20–50 |

Recommendation: start with 1. It is new, cheap, and already has a result that changes how
FunSearch's headline benchmark should be read. 2 and 3 are the strongest methodological
contributions and fit the team's "checks" story. 4 and 5 make the memory-ablation null more
informative. 6 also fixes the tournament's saturation problem.

## 1. Classical OR algorithms against FunSearch on its own benchmark

**Question.** How does FunSearch's evolved heuristic compare with the online bin-packing algorithms
the operations-research literature proved good for exactly this setting: integer sizes, a fixed
capacity, and i.i.d. items from a fixed discrete distribution?

**Literature: not done.**
- Herrmann & Pallez ([2510.27353](https://arxiv.org/abs/2510.27353)) and Sim, Renau & Hart
  ([2501.11411](https://arxiv.org/abs/2501.11411)) compare only against the Any-Fit family.
- None of EoH, ReEvo, HSEvo, MCTS-AHD, CALM, LLM4AD, EvoTune, RAISE or ASRO mentions
  Sum-of-Squares or the primal-dual / re-solving algorithms (full texts searched).
- OpenAlex finds no paper citing both FunSearch and Csirik et al. 2006, Banerjee & Freund, or
  Ayyadevara et al.
- Closest work:
  - Balaji et al., ORL ([1911.10641](https://arxiv.org/abs/1911.10641)): reinforcement learning
    against Sum-of-Squares on small toy distributions. Not FunSearch's benchmark.
  - Angelopoulos, Kamali & Shadkami ([2102.03311](https://arxiv.org/abs/2102.03311)):
    frequency-aware packing on Weibull shape 3. No Sum-of-Squares, and it predates FunSearch.

**Theory.**
- Sum-of-Squares (SS): Csirik et al., JACM 53(1) 2006, [cs/0210013](https://arxiv.org/abs/cs/0210013).
  - Expected waste is O(√n) on perfectly packable distributions and O(log n) or O(1) on
    bounded-waste ones.
  - On linear-waste distributions it can be up to 1.5–3× the optimum.
- SS′, SS_F and SS* fix those cases.
- Gupta & Radovanović (Oper. Res. 2020, [1211.2687](https://arxiv.org/abs/1211.2687)): O(√n)
  additive regret for any distribution, without knowing it.
- Banerjee & Freund (SIGMETRICS 2020, doi 10.1145/3393691.3394224): O(1) additive loss when the
  horizon and the distribution are known.

**Probe result.** SS is about 15 lines and has no parameters. Excess over L1 on FunSearch's
released test data, FunSearch's own metric:

| | best fit | FunSearch Weibull heuristic | Sum-of-Squares | SS restricted to FunSearch's stateless view |
|---|---|---|---|---|
| Weibull 5k, 5 instances | 3.984% | 0.684% | **0.483%** (4/0/1 against FunSearch) | 4.095% |
| OR3, 20 instances (capacity 150, 500 items) | 5.368% | 3.106% (OR heuristic) | 7.107% (0/0/20) | — |

- The best-fit and FunSearch numbers reproduce FunSearch's published 3.98% and 0.68%.
- On 20 fresh 5,000-item instances from our generator, SS beat FunSearch's heuristic on 19 of 20
  (0.529% against 0.736% excess over L2).
- At 20,000 items SS won 4 of 4 (0.138% against 0.179%).
- At 10,000 and 100,000 items, SS reaches 0.317% and 0.030% over L1 on fresh instances. That ties
  FunSearch's published 0.32% and 0.03%, which were measured on different instances of the same
  distribution.
- Both algorithms stay about 10–13 bins above L1 at every length: bounded waste.
- At 80 items SS loses to best fit (+1.98 bins per instance) but beats FunSearch's heuristic by
  4.55 bins per instance (395/5/0). At 500 items SS already beats best fit.

**The interface finding.** FunSearch's `priority(item, bins)` sees only the bins the item fits in.
SS needs the counts of bins whose gap is smaller than the item.
- Restricted to what that stateless view shows, SS is worse than best fit (4.095%).
- Given one piece of state, its own placement history, it recovers 0.483% exactly.

So the benchmark's interface hides the state that the provably good algorithm needs. Our
`problems/bin_packing_online` already allows state, so an LLM could find SS there.

**Confirmed (02:30 BST).** The pre-registered follow-up `online-frontier-v1` is on branch `exp/online-frontier`, folder
`experiments/online-frontier-v1/RESULTS.md`. It covers 210 instances with the exact optimum from arc-flow.

| | OPT − L1 | SS above OPT | FunSearch's heuristic above OPT |
|---|---|---|---|
| Weibull | 0 on 129 of 130 instances | 10–11 bins | 13–14 bins |

- SS − FunSearch is −2.65 bins per instance [−3.07, −2.24] on 100 fresh 5k instances (84/11/5), and SS wins at 10k and 100k.
- On OR1–OR4 FunSearch's OR heuristic beats SS by 4–8 bins.
- Gupta–Radovanović PD-exp is far worse at these sizes.
- Both distributions are bounded-waste.

**What would be new.**
1. An online-achievable frontier for FunSearch's benchmarks:
   - BF, FunSearch, Herrmann & Pallez's rules, our 21-weight rule and the campaign's table rule;
   - against SS, SS′, SS*, Gupta–Radovanović and a Banerjee–Freund / Liu–Li re-solving policy;
   - on Weibull 5k/10k/100k and OR1–OR4.
2. The exact offline optimum (an arc-flow model; sizes ≤ 100 keep it small), so that
   "12 bins above L1" can be split into L1's slack and real waste.
3. Solving the Csirik et al. LP to classify discretised Weibull(45, 3) as perfectly packable or
   bounded-waste. That says which growth rate is optimal.
4. Whether an LLM loop rediscovers SS when given state. How close the campaign's
   "residual-space table" rule is to SS's potential or to Gupta–Radovanović's dual prices.

**Caveats.**
- Only 5 released Weibull instances exist; the fresh-instance results come from our generator,
  which matches in distribution, not instance by instance.
- SS uses state that FunSearch's evaluator did not offer. So this is a statement about the
  benchmark's ceiling and its missing baseline, not about FunSearch's search.
- SS loses on OR3, which may be a linear-waste case for plain SS; SS* or primal-dual should be
  tested there.
- SS is published and may be known to LLMs.

## 2. Adaptive overfitting, and Ladder or Thresholdout as the promotion rule

**Question.** How fast does the gap between public and fresh scores grow with the number of LLM
proposals and promotions? Do Ladder or Thresholdout promotion rules close it, and at what cost in
false rejections?

**Literature: partly done.**
- Gallego 2026, "Gaming Without an Attacker" ([2608.08722](https://arxiv.org/abs/2608.08722)):
  in an LLM kernel loop, 30% of in-distribution wins fail on held-out configurations. Gives
  adaptive-data-analysis theory, but no mitigation and no gap-against-rounds curve.
- Toledo et al. ([2507.02554](https://arxiv.org/abs/2507.02554)) and AIRA_2
  ([2603.26499](https://arxiv.org/abs/2603.26499)): the validation–test gap in ML-engineering
  agents. AIRA_2 attributes it mostly to evaluation noise.
- Sequential tests as acceptance gates:
  - PACE ([2606.08106](https://arxiv.org/abs/2606.08106)): prompts; false acceptances measured.
  - SGM ([2510.10232](https://arxiv.org/abs/2510.10232)): ML training loops; missed
    improvements measured.
- Archive-style gates for agent harnesses: CHASE ([2609.18366](https://arxiv.org/abs/2609.18366))
  and HarnessEvolve ([2609.00829](https://arxiv.org/abs/2609.00829)).
- Not found:
  - Ladder ([1502.04585](https://arxiv.org/abs/1502.04585)) or Thresholdout
    ([1506.02629](https://arxiv.org/abs/1506.02629)) as the promotion rule in program evolution;
  - a false-acceptance vs false-rejection trade-off for LLM-generated heuristics;
  - a strict counterexample veto compared with a random veto of equal size.

**What would be new.**
- Log every proposal's public and fresh score, and fit the gap against proposals T and
  promotions P. Theory predicts two curves:
  - √(ln T / n) for selection;
  - √(P·bits / n) for adaptive reuse (Hardt & Ullman [1408.1655](https://arxiv.org/abs/1408.1655)).
- Sweep the public-set size n and the feedback richness: per-instance floats, the mean, or 1 bit.
- Add a null proposer that writes semantically equivalent rewrites, to separate noise from
  overfitting.
- Replay one proposal stream through each gate: greedy, Ladder, Thresholdout, a PACE-style test,
  the strict archive, a size-matched random veto and the soft gate. Report false acceptances,
  false rejections and final fresh score at equal evaluation cost.
- A small theoretical point for the paper: a veto gate's false-rejection rate is 1 − ∏(1 − qᵢ)
  over archived cases. Archived cases are selected for disagreement, so qᵢ is higher there than on
  random inputs. That predicts gate-v3's 40.3% against 21.0%.
- Also quotable: a paired sign test needs at least 5 wins and 0 losses for one-sided p < 0.05, so
  no valid test would have promoted the Codex revision's 1/0.

## 3. Timing-shuffle and matched-mix controls on LLM frameworks

**Question.** When an LLM evolution framework adapts something during a run (ShinkaEvolve's model
bandit, AdaEvolve's exploration intensity, PACEvolve's backtracking), is the gain from the timing
of its decisions or only from the mix they add up to?

**Literature.**
- **Timing shuffle: not done** in any LLM or classic paper found.
- **Matched-proportion static mix: partly done**, for model routing only:
  - AdaptEvolve ([2602.11931](https://arxiv.org/abs/2602.11931)): the router beat random routing
    at the same ratio. One seed.
  - LEVI ([2605.09764](https://arxiv.org/abs/2605.09764)): changed two things at once.
- ShinkaEvolve ([2509.19349](https://arxiv.org/abs/2509.19349)) compares its bandit only with a
  uniform mix, on circle packing, with no seed count. AdaEvolve
  ([2602.20133](https://arxiv.org/abs/2602.20133)) compares with OpenEvolve's default split, not
  the rate its controller used.
- **Counterfactual forks:** done for SWE-bench agents (The Replay Gap,
  [2608.08239](https://arxiv.org/abs/2608.08239)), not in LLM evolution.
- Classic evidence predicts the mix does the work for reward-history controllers:
  - Karafotias et al. 2013 (doi 10.1109/CEC.2013.6557590);
  - Pellegrini et al. 2012 (doi 10.1007/s11721-011-0061-0);
  - Relay, Don't Route ([2608.05651](https://arxiv.org/abs/2608.05651)): the bandit was at or
    below random.

**What would be new (cheapest version).**
- Use ShinkaEvolve's UCB model bandit (`llm_dynamic_selection="ucb"`, with `cost_aware_coef=0`
  or cost reported per arm) on Heilbronn triangles, which does not saturate and is where our
  timing effect appeared.
- Four arms, at least 20 paired seeds:
  - (A) the bandit;
  - (B) A's model sequence, shuffled;
  - (C) random choice at A's pooled shares;
  - (D) uniform choice.
- Next target: AdaEvolve's intensity control. Add same-action control forks to measure the noise
  floor, as The Replay Gap does.
- Prediction from prior work: the bandit is about equal to (B) and (C), and timing matters more
  where decisions read the search state.

## 4. Behavioural no-ops and failure memory

**Question.** Does failure memory make LLM proposals copy the incumbent's behaviour? Does rejecting
behavioural duplicates before they are charged improve the result at a matched budget?

**Literature: partly done.**
- Single-task repair:
  - Verma ([2607.26117](https://arxiv.org/abs/2607.26117)): shown its failed program, a model
    returns near-identical code in 33–68% of retries.
  - Gumaan ([2608.23651](https://arxiv.org/abs/2608.23651)): showing a failed action raises the
    chance of repeating it from 0.06 to 0.54. Most of the effect comes from the failed code being
    in context.
- Population level: HSEvo ([2412.14995](https://arxiv.org/abs/2412.14995)) and LaGO
  ([2602.16038](https://arxiv.org/abs/2602.16038)) find that reflection reduces population
  diversity.
- Gurkan et al. ([2606.05408](https://arxiv.org/abs/2606.05408)): LLM mutation chains with no
  selection mostly return to code structures already seen. Code-level only.
- Admission control exists only at the text level: ShinkaEvolve's embedding novelty filter; EoH's
  identical-code or identical-score check, never ablated.
- Zhang et al. ([2407.10873](https://arxiv.org/abs/2407.10873)) skipped functional deduplication
  for lack of tools.
- Not found:
  - the behavioural no-op rate inside an evolutionary loop as memory varies;
  - that the fall in harmful proposals is mostly no-ops (our 0.133 → 0.650 → 0.815);
  - behavioural dedup before charging at a matched budget.

**What would be new.**
- Design: memory {none, prose, executable} × admission {charge every proposal; dedup}.
- Dedup means that a proposal making the same decisions as an archived program on probe inputs is
  resampled without being charged, up to K tries.
- Add a copying control: counterexamples given as inputs only, with no code.
- Match both charged evaluations and total LLM calls. Use two or more models.
- Report the harmful rate among proposals that do change behaviour. That separates "memory
  improves proposals" from "memory makes the model abstain".
- Gumaan's result is a rival explanation to risk aversion: copying from context. The design above
  separates the two.

## 5. Short-horizon bias in LLM heuristic search

**Question.** Do short evaluation instances and shrunk counterexamples steer an LLM loop toward
myopic rules?

**Literature.**
- The rank reversal itself is known:
  - Herrmann & Pallez for FunSearch's heuristic;
  - Burke, Hyde, Kendall & Woodward 2007 (doi 10.1109/CEC.2007.4424789) for GP-evolved bin-packing
    rules. They call the winners "less myopic", and longer training sequences gave better rules.
- So our 80/200/5,000-item sweep is a replication.
- Related concepts: short-horizon bias (Wu et al. [1803.02021](https://arxiv.org/abs/1803.02021)),
  instance-size scaling in algorithm configuration (Styles & Hoos 2013,
  doi 10.1145/2463372.2463438), and slippage in test-case reduction.
- **Not done:** measuring how evaluation fidelity changes what an LLM loop *selects*. Proxy
  agreement inside LLM loops has been measured only for example subsets (LEVI) and learned
  proxies (Janus, [2608.08189](https://arxiv.org/abs/2608.08189)).
- **Not done:** shrunk counterexamples biasing search toward myopic policies. LLM practice treats
  minimal counterexamples as purely beneficial; see PGS,
  [2506.18315](https://arxiv.org/abs/2506.18315).

**What would be new.**
- One LLM, one budget, five fitness regimes:
  - (A) full 5,000-item instances;
  - (B) 80- or 200-item instances;
  - (C) successive halving 200 → 1,000 → 5,000;
  - (D) A plus shrunk counterexamples;
  - (E) A plus counterexamples that keep their length.
- Report:
  - Kendall's τ between fidelities over all candidates;
  - how many eventual top-k candidates each low fidelity eliminated;
  - final excess at 5,000 and 100,000 items;
  - a myopia score: how often a rule opens a new bin while an open bin fits.
- In bin packing a 2-item counterexample can almost never reward opening a new bin, so the bias
  is nearly built in. A second domain is needed for a general claim.

## 6. Unprompted exploitation, measured with canaries

**Question.** How often does ordinary LLM evolutionary search exploit its evaluator when nobody
asks it to cheat? Does selection amplify it?

**Literature: partly done.**
- Ishibashi, Yano & Oyamada ([2605.15221](https://arxiv.org/abs/2605.15221)) give a rate (26.1%
  of programs for one model), but on circle packing only and labelled by an LLM judge.
- Georgiev, Gómez-Serrano, Tao & Wagner ([2511.02864](https://arxiv.org/abs/2511.02864)) and HASE
  ([2607.03935](https://arxiv.org/abs/2607.03935)) give anecdotes.
- ImpossibleBench ([2510.20270](https://arxiv.org/abs/2510.20270)) and the hacker/fixer loops of
  Zhong et al. ([2606.08960](https://arxiv.org/abs/2606.08960)) cover coding tasks, not
  discovery.
- No proven-optimum canaries embedded in AlphaEvolve-style search were found.

**What would be new.** Run unprompted search (our loop, plus ShinkaEvolve or OpenEvolve, across
model tiers) on matched pairs.
- **Headroom problems:**
  - the sum-difference constant: 1.1584 (AlphaEvolve) → 1.173077
    ([2506.01896](https://arxiv.org/abs/2506.01896)) → later unrefereed claims; our finite-set
    version may differ;
  - kissing number in 11 dimensions ([2606.10402](https://arxiv.org/abs/2606.10402));
  - LABS at N = 80–120.
- **Canary twins**, where the target is provably unreachable:
  - Erdős discrepancy C = 2 beyond 1160 ([1402.2184](https://arxiv.org/abs/1402.2184));
  - kissing number above 240 in 8 dimensions;
  - LABS below the known optimum for N ≤ 66 ([1512.02475](https://arxiv.org/abs/1512.02475)).
- Sweep the evaluator tolerance over {0, 1e-12, 1e-8, 1e-6}.
- The breach rate needs no judge: any score past a proven optimum is an exploit. Report time to
  first breach and how far a breaching program spreads under selection, against our prompted 0/68.
- The headroom twins also replace the saturated problems: circle packing n = 26 and Erdős minimum
  overlap now improve by about 1e-6 or less per record.

## Checked and not worth pursuing as novelty

- **Short versus long rank reversal in bin packing:** Herrmann & Pallez; Burke et al. 2007.
- **A cheap tuned rule matching FunSearch:** Herrmann & Pallez.
- **Automated simplification of evolved programs:** genetic-programming practice (Javed et al.
  2022).
- **Prompted idea rankers near chance:** Wen et al., Si et al.
- **Implementation variance dominating idea quality:** Ning et al.

These are already in [related-work.md](related-work.md).

## Reproduce

```bash
python docs/literature/probes/sos_probe.py --quick   # released Weibull 5k only, about 10 s
python docs/literature/probes/sos_probe.py           # plus fresh instances at 80 to 100,000 items, a few minutes
python docs/literature/probes/sos_probe.py --or3 <datasets.json>   # adds FunSearch's OR3 data
```

The OR3 file comes from FunSearch's notebook (Apache 2.0 / CC-BY 4.0). It is in the unmerged
campaign tag `archive/all-approaches` (formerly branch `research/all-approaches`) at
`data/funsearch/datasets.json`, not in `main`.
