# Experiments

Every study in this project, in the order it was run, with where to find its protocol, write-up and
raw data. Numbers below are copied from each study's write-up, which is the authority. Intervals are
95% paired bootstrap intervals over seeds unless a write-up says otherwise.

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

## First round: search mechanisms without LLM calls (3 October, day)

All on online bin packing (capacity 100, 80-item instances) with a fixed C++ packer, local CPU only.
The candidates are weighted feature vectors scoring each bin; best-fit is one of them.

| Study | Folder | Protocol | Write-up | Question | Main result |
|---|---|---|---|---|---|
| Falsify v1 | [local-v1](local-v1/) | [PROTOCOL.md](PROTOCOL.md) | [RESULTS.md](RESULTS.md), [HANDOFF.md](HANDOFF.md) | Does keeping counterexamples for replay beat random replay at equal evaluator work? | 20 seeds × 120 generations: −0.0047 excess bins vs random replay, CI [−0.012, 0.0019]; inconclusive |
| Falsify v2 | [local-v2](local-v2/) | [PROTOCOL-v2.md](PROTOCOL-v2.md) | [RESULTS.md](RESULTS.md) | The same, with neutral drift, 50 seeds and 500 generations | Counterexample replay 0.000725 vs random 0.023 excess bins; −0.0223, CI [−0.0378, −0.0108]. Less drift away from best-fit, not better than best-fit |
| Recovery from first-fit | [local-firstfit](local-firstfit/) | [PROTOCOL-v2.md](PROTOCOL-v2.md) | [RESULTS.md](RESULTS.md) | Starting from a weak policy, do counterexample arms recover more? | All arms recovered from 0.33 excess bins; counterexample arms got closer to best-fit (−0.0106 vs random, CI [−0.0182, −0.0032]) |
| Codex pilot | [codex-pilot-v1](codex-pilot-v1/), [codex-pilot-v2](codex-pilot-v2/) | - | [RESULTS.md](RESULTS.md); candidates in [codex_candidates.json](codex_candidates.json), [codex_revision.json](codex_revision.json) | Do model-proposed heuristics survive a fresh audit? | A revision with 1 win / 0 losses on 1,000 cases had 3 wins / 14 losses on 10,000 fresh cases |
| Promotion gates v3 | [gate-v3](gate-v3/) | [PROTOCOL.md](gate-v3/PROTOCOL.md) | [gate-v3/RESULTS.md](gate-v3/RESULTS.md) | On an identical proposal stream, does a counterexample gate beat score-only promotion and a random-input gate? | Beats score-only (−0.0022, CI [−0.0041, −0.0006]); against a random gate, inconclusive |
| Soft gates v4 | [soft-gate-v4](soft-gate-v4/) | [PROTOCOL.md](soft-gate-v4/PROTOCOL.md) | [soft-gate-v4/RESULTS.md](soft-gate-v4/RESULTS.md) | Can bounded losses backed by fresh validation keep good proposals and still block bad ones? | Let through 15/16 beneficial and blocked 328/599 harmful sampled proposals (strict gate: 14/16, 270/599); no final-quality gain |
| Simplify | [simplify-v1](simplify-v1/) | [PROTOCOL.md](simplify-v1/PROTOCOL.md) | [simplify-v1/EXPERIMENT.md](simplify-v1/EXPERIMENT.md), corrections in [REVIEW_ADDENDUM.md](simplify-v1/REVIEW_ADDENDUM.md) | Can an evolved rule be reduced to a short rule with the same measured quality? | The 11-term "winner" is exactly best-fit. One-sided simplification also *repaired* worse candidates (26 of 43 improved beyond tolerance), so explanations need a two-sided check |
| Strategist v1 | [strategist-v1](strategist-v1/) | [../strategist/PROTOCOL.md](../strategist/PROTOCOL.md) | [../strategist/RESULTS.md](../strategist/RESULTS.md) | Does learning when to edit, rewrite, cross over or restart beat fixed move mixes, and is it timing or luck? | Beats fixed mixes on LABS and NK; timing matters on Heilbronn (130/0/70 vs shuffled timing); a post-hoc tuned patience rule beats it on LABS and NK |

[report.html](report.html) is an interactive Falsify report, best opened in a browser after cloning. [example_prompt.txt](example_prompt.txt) is the
prompt format for the optional Anthropic proposal adapter in `falsify/anthropic_propose.py`.

## Overnight: real LLM runs, new benchmark, controls (3 October, night)

The decisions, approvals, incidents and spend behind these six studies are in
[OVERNIGHT-2026-10-03.md](../docs/logs/OVERNIGHT-2026-10-03.md). The Anthropic credit ran out at about 21:30,
which cut two of them short; the write-ups say exactly which runs are affected.

| Study | Folder | Question | Main result | Status |
|---|---|---|---|---|
| Bin-packing ceiling | [bp-ceiling-v1](bp-ceiling-v1/RESULTS.md) | Is the best-fit ceiling the feature set or the 80-item instances? | The instances. On FunSearch's 5,000-item Weibull instances, a 21-weight linear rule tuned on CPU reaches −3.28 pp vs best-fit (FunSearch's heuristic: −3.33). Our evaluator reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly | Complete |
| Memory ablation | [memory-ablation-v1](memory-ablation-v1/RESULTS.md) | In a closed LLM loop, do executable counterexamples in the prompt beat no memory and prose memory? | No: all primary intervals include zero (executable − prose +4.73 bins, CI [−0.23, +12.96]). Memory cut harmful proposals mainly by making the model propose no-ops | Complete; memory was not token-matched (disclosed) |
| Idea table | [idea-table-v1](idea-table-v1/RESULTS.md) | Does ranking ideas before implementation predict success, and which routing policy is best per dollar? | The implementing model decided success (Opus 62/62, Sonnet 60/62, Haiku 10/62); rankers near chance (Codex AUC 0.600, Jev 0.484); ranked triage no better than random tiers | Partial: 62 of 114 ideas complete for all three models |
| Tournament v1 | [tournament-v1](tournament-v1/RESULTS.md) | Which complete framework gets furthest at an equal dollar budget? | At a common early spend, the single-model loops led ShinkaEvolve and triage trailed; final scores tied; two of three problems saturate within 1–3 calls | Partial: 17 of 60 runs complete; not budget-matched |
| Tournament v2 | [tournament-v2](tournament-v2/RESULTS.md) | The same grid on open models through the Hugging Face router | Route works for all five arms; a Flash call cost about $0.002. In the full grid, the single-model loops ended highest on bin packing and ShinkaEvolve on Erdős squares, and hidden instances exposed programs that time out on larger cases (lean: 0.994 public, 0.125 hidden) | Full grid run as `full-v2b` (60 runs, $8.04): no framework differs significantly from ShinkaEvolve after Holm correction; results depend on the problem; 13 runs stopped early, mostly on sum-difference |
| Strategist v2 | [strategist-v2](strategist-v2/RESULTS.md) | Do v1's three proposed fixes help, on fresh seeds with a dev/validation/confirmatory split? | Better than v1 on LABS (+0.137) and NK, mostly via the crossover gate; a patience rule tuned on dev seeds still wins on LABS | Complete |
| Gate red-team | [gate-redteam-v1](gate-redteam-v1/RESULTS.md) | Can candidate programs obtain a score they did not earn? | 0 of 68 attempts (28 hand-written, 40 by Sonnet and Haiku told to cheat) gained a material unearned score | Complete |

## Follow-up (4 October)

| Study | Folder | Question | Main result | Status |
|---|---|---|---|---|
| LLM long search | [llm-long-search-v1](llm-long-search-v1/RESULTS.md) | With 300 steps of an inexpensive open model, does `autoresearch.loop` beat best-fit on FunSearch's 5,000-item Weibull benchmark, and how close does it get to FunSearch? | All 4 runs beat best-fit on 100 unseen instances; the best reached −3.20 pp vs FunSearch's −3.31 (97% of its gain, still 0.11 pp [0.07, 0.15] behind) for $0.19. Sum-of-Squares (post-hoc reference) reached −3.48 and beats FunSearch | Complete; pre-registered |

### Studies by other sessions (4 October, early morning)

These were run and written up by other Claude sessions working on the same project, each with its own
pre-registered protocol. Online frontier, Beyond Sum-of-Squares and Overfitting and gates were committed
unchanged at about 05:45 so that they are preserved; the others arrived later by pull request, after review.

| Study | Folder | Question | Main result |
|---|---|---|---|
| Online frontier | [online-frontier-v1](online-frontier-v1/RESULTS.md) | How far are FunSearch's heuristics from the exact optimum, and how do classical online algorithms compare? | The optimum equals the L1 bound on 129 of 130 Weibull instances, so FunSearch's excess is all online waste: 13–14 bins per instance. Sum-of-Squares wastes 10–11 and beats FunSearch on every Weibull set; on OR-Library, FunSearch's OR heuristic is best |
| Beyond Sum-of-Squares | [online-beyond-ss-v1](online-beyond-ss-v1/RESULTS.md) | Can a simple, explainable online policy close the gap to the optimum? | FWSS ends about 2 bins above the optimum at every length from 1k to 100k items. It beats FunSearch by 11.6 bins per instance (200/0/0) and is below the best published LLM result in 15 of 15 leaderboard settings |
| Short-horizon bias | [short-horizon-v1](short-horizon-v1/RESULTS.md) | Do short selection streams, or a gate of short counterexamples, make the LLM loop myopic on 5,000-item streams? | Complete separation: every run selecting on 5,000-item streams (−2.61 pp vs best fit) beat every run selecting on 200- or 80-item streams (−0.33, −0.15). The pre-registered Holm p = 0.057 is the floor with 4 runs per arm. Short gates erase the gain whether the inputs are mined counterexamples (−0.58) or random (−0.09). Short-trained rules almost never open a new bin while one fits (0.02 vs 0.17). $1.84 (complete; pre-registered) |
| LLM informed | [llm-informed-v1](llm-informed-v1/RESULTS.md) | Does the same LLM loop find SS- or FWSS-like rules when the prompt spells out what the function can know (item count, every open bin)? | No. 0/4 runs beat FunSearch, reached SS or reached FWSS on 100 fresh instances; the informed runs were descriptively worse than uninformed ones (best 1.06% vs 0.81% over L2) and overfit their 2 public instances more (post hoc). 3/4 tried to use the item count (one correctly); none tracked open bins. $1.07 (Complete; pre-registered) |
| LLM from Sum-of-Squares | [llm-from-ss-v1](llm-from-ss-v1/RESULTS.md) | Starting from Sum-of-Squares instead of best fit, can 300 steps of the same loop find a policy that beats it on unseen instances? | Yes: all 4 runs beat SS by the pre-registered test. The best run found a gap-weighted SS that penalises nearly full bins: −2.31 bins per instance against SS [−2.58, −2.04] (92/6/2), 8.4 bins above the exact optimum against 10.7 for SS and 13.5 for FunSearch's heuristic. The other three flipped SS's tie-break (−0.48). No run used the item count; FWSS stays at 1.8 above the optimum. $1.10 |
| Overfitting and gates | [overfit-gates-v1](overfit-gates-v1/RESULTS.md) | How much does selection on a small public suite overfit, and what do stricter promotion rules cost? | 554 of 635 archived counterexamples are 2-item inputs, so a strict veto mainly tests "never open a new bin when one fits". In an open-loop replay it blocked the two largest gains (2 runs; not significant). Selection overfitting was small in absolute terms (0.38 bins per promotion) but erased small promotions. Statistical gates neither helped nor hurt |

Related material:
- [`docs/literature/research-directions.md`](../docs/literature/research-directions.md) lists candidate research
  directions with literature checks; its Sum-of-Squares probe is in `docs/literature/probes/`.
- The four-approach live campaign is archived as tag
  [`archive/all-approaches`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/all-approaches)
  (formerly branch `research/all-approaches`), in `runs/FINDINGS.md`. It is a parallel framework
  built from an older `main`, so it is not merged. Its raw provider traffic (about 470 MB) is not in git.

## Demo runs of the one-command loop

[../runs/](../runs/README.md) holds two committed runs of `python -m autoresearch.loop`: a live
bin-packing run on an open model and a mock Erdős squares run, with the live-demo plan.

## Related work

How these results relate to published work is in [docs/literature/related-work.md](../docs/literature/related-work.md)
(about 60 papers) and [docs/literature/related-work-addendum.md](../docs/literature/related-work-addendum.md)
(open questions).
