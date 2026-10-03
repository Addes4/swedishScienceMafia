# Research paper outlines

Written on 3 October 2026, after the team asked whether the hackathon work could become a research
paper. Short answer: yes, but as one focused paper at a time, not as a write-up of the whole
repository. Four loosely connected parts make a project, not a paper.

| Outline | Question | Evidence ready | Must add before writing | Venues (deadlines not verified) |
|---|---|---|---|---|
| [A: Strategist](A-strategist.md) | Does an adaptive strategy controller gain from *when* it switches, or from luck? | v1 and v2, pre-registered, 200 seeds, 3–4 benchmarks, forks | Prior-art baselines (MetaMax, Luby, AdaEvolve-style, PACEvolve-style); real LLM moves charged by tokens | GECCO, PPSN, EvoStar; agents or algorithm-discovery workshops; TMLR |
| [B: Checking claims](B-checking-claims.md) | Which claims of an autoresearch loop survive a control, and what does checking cost? | Gates v2–v4, Simplify, gate red team, memory ablation, idea table, partial tournament, bp-ceiling | Budget-matched tournament on unsaturated problems; gates rerun in the Weibull regime; token-matched memory | NeurIPS or ICLR workshop on AI for science, agents or evaluation; TMLR |

**Recommendation: write A first.** Its evidence is the most complete and its gaps are cheap
(baselines run on CPU). B depends on a tournament rerun with API credit.

## A third candidate (not outlined)

bp-ceiling-v1 could be a short paper on its own, in the line of Herrmann & Pallez and Sim et al.:

- On 80-item instances nothing online beats best-fit robustly.
- On 5,000-item Weibull instances a 21-weight linear rule with a "new bin" option matches
  FunSearch's evolved code (−3.278 vs −3.329 pp of the L2 bound).
- So instance length and that single decision, not code, were what earlier searches lacked.
- It includes a positive control that reproduces FunSearch's published numbers exactly.

A natural venue is EvoApplications, where Sim et al. appeared. It would need OR-Library and
Falkenauer instances and the Sum-of-Squares feature to be complete.

## How these were produced

Each outline lists its evidence sources, the gaps in priority order, a section plan, likely
reviewer objections and venues. Numbers come from each experiment's RESULTS.md (the authority)
and were last checked at 23:10 on 3 October. The literature behind the positioning is in
[context/related-work.md](../../context/related-work.md). Before writing, search the literature
again: 2026 preprints in this area appear weekly.
