# Experiments

The studies behind this repository's results and defaults, with their protocol, write-up and raw
data, and a summary of what we tried and dropped. Numbers are copied from each study's write-up,
which is the authority. Intervals are 95% paired bootstrap intervals unless a write-up says otherwise.

## How a study folder is organised

| File | Contents |
|---|---|
| `PROTOCOL.md` | Question, arms, primary endpoint, seeds and budgets, written before the main run; later changes are disclosed in place |
| `RESULTS.md` (`EXPERIMENT.md` for simplify-v1) | Question and answer first, then method, results, limitations, cost, reproduce commands and an index of the folder's files |
| `summary.json` | Headline numbers in machine-readable form |
| `config.json`, `grids/` | The exact configuration that ran |
| `*.json.gz`, `runs/`, `traces/`, `cells/` | Raw traces: per-seed searches, every LLM prompt and response, every evaluation |
| `audit*.json` | The final audit on fresh instances, generated only after search ended |
| `usage.jsonl` | Every paid API call: model, tokens, dollars, outcome (failures included) |
| `source/`, `source_hashes.json` | A snapshot of the code that produced the data |

## Studies on main

| Study | Folder | Question | Main result | Supports |
|---|---|---|---|---|
| Simplify | [simplify-v1](simplify-v1/EXPERIMENT.md) | Can an evolved rule be reduced to a short rule with the same measured quality? | The 11-term "winner" is exactly best-fit. One-sided simplification also *repaired* worse candidates (26 of 43 improved beyond tolerance), so explanations need a two-sided check | Two-sided explanation in the loop |
| Bin-packing ceiling | [bp-ceiling-v1](bp-ceiling-v1/RESULTS.md) | Is the best-fit ceiling the feature set or the 80-item instances? | The instances. On FunSearch's 5,000-item Weibull instances, a 21-weight linear rule tuned on CPU reaches −3.28 pp vs best-fit (FunSearch's heuristic: −3.33). Our evaluator reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly | Baselines in every report |
| Gate red-team | [gate-redteam-v1](gate-redteam-v1/RESULTS.md) | Can candidate programs obtain a score they did not earn? | 0 of 68 attempts (28 hand-written, 40 by Sonnet and Haiku told to cheat) gained a material unearned score | The integrity gate |
| Tournament v2 | [tournament-v2](tournament-v2/RESULTS.md) | Which complete framework (lean loop, independent sampling, lean with gate and patience, triage, ShinkaEvolve) gets furthest at an equal dollar budget, on open models? | Full grid (60 runs, $8.04): no framework differs significantly from ShinkaEvolve after Holm correction, and the winner depends on the problem. Hidden instances caught weak programs, for example 0.960 public and 0.238 hidden. 13 runs stopped early; see the [independent review](../docs/reviews/2026-10-04-tournament-v2.md) | The simple loop; hidden-instance audits |
| LLM long search | [llm-long-search-v1](llm-long-search-v1/RESULTS.md) | With 300 steps of an inexpensive open model, does `autoresearch.loop` beat best-fit on FunSearch's 5,000-item Weibull benchmark, and how close does it get to FunSearch? | All 4 runs beat best-fit on 100 unseen instances; the best reached −3.20 pp vs FunSearch's −3.31 (97% of its gain, still 0.11 pp [0.07, 0.15] behind) for $0.19. Sum-of-Squares (post-hoc reference) reached −3.48 and beats FunSearch | Headline result |
| Online frontier | [online-frontier-v1](online-frontier-v1/RESULTS.md) | How far are FunSearch's heuristics from the exact optimum, and how do classical online algorithms compare? | The optimum equals the L1 bound on 129 of 130 Weibull instances, so FunSearch's excess is all online waste: 13–14 bins per instance. Sum-of-Squares wastes 10–11 and beats FunSearch on every Weibull set; on OR-Library, FunSearch's OR heuristic is best | Headline result |
| Beyond Sum-of-Squares (FWSS) | [online-beyond-ss-v1](online-beyond-ss-v1/RESULTS.md) | Can a simple, explainable online policy close the gap to the optimum? | FWSS ends about 2 bins above the optimum at every length from 1k to 100k items. It beats FunSearch by 11.6 bins per instance (200/0/0) and is below the best published LLM result in 15 of 15 leaderboard settings | Headline result |
| LLM from Sum-of-Squares | [llm-from-ss-v1](llm-from-ss-v1/RESULTS.md) | Starting from Sum-of-Squares instead of best fit, can 300 steps of the same loop find a policy that beats it on unseen instances? | Yes: all 4 runs beat SS by the pre-registered test. The best run found a gap-weighted SS that penalises nearly full bins: −2.31 bins per instance against SS [−2.58, −2.04] (92/6/2), 8.4 bins above the exact optimum against 10.7 for SS and 13.5 for FunSearch's heuristic. The other three flipped SS's tie-break (−0.48). No run used the item count; FWSS stays at 1.8 above the optimum. $1.10 | Headline result |
| TSP step-by-step construction | [tsp-construct-v1](tsp-construct-v1/RESULTS.md) | Do the LLM-designed `select_next_node` TSP heuristics (MCTS-AHD and successors) beat textbook constructions, inside the same interface? | No. The interface passes the whole distance matrix, so a function of its arguments can emit any tour. Greedy + 2-opt + Or-opt (about 100 lines of numpy) is 1.85 / 2.44 / 2.85% above optimal at n = 50 / 100 / 200, against the best published step-by-step 4.76 / 6.47 / 8.88%, and faster than the rollout-based LLM heuristics (50–2,800× with a per-instance plan cache, 1.7–32× without). Farthest insertion (1977) beats every LLM-AHD row of the MCTS-AHD lineage. 5 of 6 released LLM heuristics are Pareto-dominated; the sixth is exactly nearest neighbour. MCTS-AHD's n = 200 optimum (10.659) is 0.46% low (LKH 10.708, confirmed on samples). Pre-registered; CPU only, $0 | Headline result (second benchmark) |

## What we tried and dropped

We built more than ended up in the loop. Each extra part was tested against a simple alternative at the
same budget, and the ones below did not earn their place, so they are not in the framework. Their study
folders, with protocols, raw data and code, are in tag
[`archive/full-research-2026-10-04`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04).

| What we tried | What we found | Studies |
|---|---|---|
| **Counterexample replay and gates** ("Falsify"): keep the inputs where earlier candidates failed, and use them to steer or veto new ones | Replaying them in a mutation search reduced harmful drift (0.0007 vs 0.023 excess bins against random replay) but never beat best fit. As a promotion gate they beat score-only promotion, but not a gate built from random inputs, and a softer gate gave no final gain. On real LLM proposals the strict veto blocked the two largest gains, mainly because 554 of its 635 stored inputs were only 2 items long. Tested live, short selection streams and short-stream gates made the loop pick short-sighted rules: every run that selected on 5,000-item streams beat every run that selected on 200- or 80-item streams | [local-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/local-v1), [local-v2](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/local-v2), [local-firstfit](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/local-firstfit), [gate-v3](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/gate-v3), [soft-gate-v4](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/soft-gate-v4), [overfit-gates-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/overfit-gates-v1), [short-horizon-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/short-horizon-v1) |
| **Memory of past failures in the prompt** | In a closed loop of 900 calls it did not improve the audited result (+4.73 bins, CI [−0.23, +12.96]). It cut harmful proposals from 80% to 15–20%, mostly by making the model propose changes that do nothing | [memory-ablation-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/memory-ablation-v1) |
| **Idea triage**: a cheap model ranks ideas so only promising ones go to an expensive model | The implementing model decided success: Opus improved the program on 62 of 62 ideas, Sonnet on 60, Haiku on 10. The best rankers were only modestly better than chance (AUC 0.600 and 0.564 against 0.499), and ranked triage did not beat random tiers | [idea-table-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/idea-table-v1) |
| **An adaptive strategy controller** ("Strategist"): learn when to edit, rewrite, combine or restart | Its switch timing mattered on one benchmark (Heilbronn: 130 wins, 70 losses against the same moves in shuffled order) but not on another (LABS), where a simple tuned restart rule still won. Development seeds overstated its gain in both versions. Only the simple restart rule is kept, as the opt-in `--patience T` | [strategist-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/strategist), [strategist-v2](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/strategist-v2) |
| **Heavier search frameworks** (ShinkaEvolve, the triage loop) | At a common early spend the simple single-model loops were ahead of both (a partial study: the API credit ran out after 17 of 60 runs). In the full grid on open models no framework differed significantly from ShinkaEvolve ([tournament-v2](tournament-v2/RESULTS.md)), so we kept the simplest | [tournament-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/tournament-v1) |
| **Telling the model what its function can know** (the item count, every open bin) | It did not help: 0 of 4 runs beat FunSearch, none built the state the classical rules need, and the programs overfit more. Starting from a strong program worked instead ([llm-from-ss-v1](llm-from-ss-v1/RESULTS.md)) | [llm-informed-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/llm-informed-v1) |
| **A model-proposed rule under a fresh audit** (the first pilot) | A rule with 1 win and 0 losses on 1,000 cases had 3 wins and 14 losses on 10,000 new ones. This is why every run now ends with an audit on unseen instances | [codex-pilot-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/codex-pilot-v1), [codex-pilot-v2](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/codex-pilot-v2) |

## Demo runs of the one-command loop

[../runs/](../runs/README.md) holds two committed runs of `python -m autoresearch.loop`: a live
bin-packing run on an open model and a mock Erdős squares run, with the live-demo plan.

## Related work

How these results relate to published work is in [docs/literature/related-work.md](../docs/literature/related-work.md)
(about 60 papers) and [docs/literature/related-work-addendum.md](../docs/literature/related-work-addendum.md)
(open questions). Independent reviews of three studies are in [docs/reviews/](../docs/reviews/README.md).
