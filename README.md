# Swedish Science Mafia: autoresearch that checks its own claims

Our entry for Track 1, *Build Your Own Algorithm Autoresearch Framework*, at the AI x
Science Hackathon (London, 3–4 October 2026).

An autoresearch loop proposes candidate algorithms, evaluates them, keeps what works and proposes
again. Such loops can fool themselves: they overfit the instances they select on, chase luck,
exploit their own evaluator, and credit elaborate machinery for gains a simple baseline would also
reach. This repository is a loop that runs with one command, plus the checks that stop it fooling
itself. Every default was chosen by a controlled experiment.

**In short:**
- **FunSearch's bin-packing benchmark is about 2 bins from optimal, not 14.** FunSearch's evolved
  heuristic ends about 14 bins per instance above the proved optimum. FWSS, a simple classical-style
  policy, ends about 2 above, and beats every published LLM-designed heuristic we could compare
  against.
- **Our loop improves on the best known horizon-free rule.** Started from Sum-of-Squares, 300 cheap
  steps found a gap-weighted rule 2.3 bins per instance better on unseen instances.
- **Started from best fit, it reaches 97% of FunSearch's gain** for about $0.20 per run on an open model.
- **The same pattern holds on a second benchmark.** On the step-by-step TSP task used by a dozen LLM
  heuristic-design papers, textbook methods beat every published LLM-designed heuristic inside the same
  interface (1.85% vs 4.76% above the reference tour at 50 cities).
- **The checks earned their place; the extra search machinery did not.** Hidden-instance audits,
  an integrity gate and two-sided explanations each caught real problems. Idea triage, prompt memory,
  counterexample gates and an adaptive strategy controller did not beat simple alternatives, so they
  are not in the loop ([How we chose the defaults](#how-we-chose-the-defaults)).

## Contents

- [Quick start](#quick-start)
- [What one run does](#what-one-run-does)
- [Key findings](#key-findings)
- [How we chose the defaults](#how-we-chose-the-defaults)
- [How we kept ourselves honest](#how-we-kept-ourselves-honest)
- [Reproducing the experiments](#reproducing-the-experiments)
- [Add a problem](#add-a-problem)
- [Repository layout](#repository-layout)
- [Related work](#related-work)
- [Status and limitations](#status-and-limitations)
- [Credits and citation](#credits-and-citation)

## Quick start

You need Python 3.10+ (we used 3.12) and a C++17 compiler (`c++`); the first run compiles small
evaluators. Run everything from the repository root.

```bash
pip install -r requirements.txt
python -m autoresearch.loop problems/erdos_squares --mock                            # no network, no cost, seconds
python -m autoresearch.loop problems/bin_packing_online --budget 0.10 --provider hf  # live, hard $0.10 cap
python -m autoresearch.loop --report runs/<dir>                                      # rebuild the report of a saved run
```

- **Live runs** use the Hugging Face router (default model `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra`)
  and read `HF_TOKEN` or `~/.cache/huggingface/token`.
- **`--provider anthropic`** uses `ANTHROPIC_API_KEY` from `.env`: run `cp .env.example .env` to create
  it. The file is git-ignored.
- **Output:** each run writes `runs/<problem>-<time>/report.md`. Committed examples:
  [runs/demo-binpacking/report.md](runs/demo-binpacking/report.md) (live) and
  [runs/demo-erdos-mock/report.md](runs/demo-erdos-mock/report.md) (mock).
- **Options:** `python -m autoresearch.loop --help` lists all flags.
  [autoresearch/README.md](autoresearch/README.md) describes the outputs, and
  [autoresearch/LOOP.md](autoresearch/LOOP.md) records the design and the build log.

## What one run does

1. **Propose.** One LLM call per step edits the current best program.
2. **Score** it in the [integrity gate](autoresearch/gate.py): a separate process, a static code scan, a
   strict re-check of record scores, and hidden instances.
3. **Keep** it only if its public score improves and it does not regress on instances where earlier
   candidates regressed.
4. **Audit** the final program on hidden instances that were never used for selection. The report
   flags `OVERFIT?` if the public score rose while the hidden score fell.
5. **Explain** it by two-sided ablation ([explain_code.py](autoresearch/explain_code.py)). A part is
   dropped only if the score stays within ±0.002 *in both directions*. A removal that raises the score
   is labelled `REPAIRED (not an explanation)`.
6. **Compare** it with the problem's baselines on the same public and hidden instances, so any gain
   is stated against what simple methods reach.

Why each step is there, and why other options are not, is in
[How we chose the defaults](#how-we-chose-the-defaults).

## Key findings

Intervals are 95% paired bootstrap intervals. Every study has a pre-registered protocol, raw data and
reproduce commands; the index is [experiments/README.md](experiments/README.md).

| Finding | Evidence |
|---|---|
| **FunSearch's benchmark is about 2 bins from optimal, not 14.** On FunSearch's Weibull instances the proved offline optimum equals the L1 bound (484 of 486 instances checked). FunSearch's heuristic ends 13–14 bins above it per instance, Sum-of-Squares 10–11, and **FWSS** about 2. FWSS is Sum-of-Squares weighted by how hard each gap is to fill, plus a best-fit finish. It beats FunSearch by 11.6 bins per instance [11.2, 12.1] on 200 fresh 5k instances (200/0/0), and is below the best published LLM result in 15 of 15 settings of the MoH/HMACE leaderboard (new draws, since their instances are not public). FWSS uses the item count, which FunSearch's evaluator reveals but no evolved heuristic used. Pre-registered; re-run on new instances by a second session, but not yet independently re-implemented. | [online-frontier-v1](experiments/online-frontier-v1/RESULTS.md), [online-beyond-ss-v1](experiments/online-beyond-ss-v1/RESULTS.md) |
| **Started from Sum-of-Squares, the loop beats it.** All 4 runs beat Sum-of-Squares on 100 unseen 5,000-item instances, by the pre-registered test. The best found a gap-weighted rule that penalises nearly full bins: −2.31 bins per instance [−2.58, −2.04] (92/6/2), 8.4 bins above the exact optimum against 10.7 for Sum-of-Squares and 13.5 for FunSearch. $1.10 for all 4 runs. | [llm-from-ss-v1](experiments/llm-from-ss-v1/RESULTS.md) |
| **Started from best fit, cheap runs get close to FunSearch.** Four 300-step runs (about $0.20 each, DeepSeek-V4.1-Flash) all beat best fit on 100 unseen instances. The best reached −3.20 pp of excess over the L2 bound against best fit, 97% of FunSearch's −3.31, with a new readable rule, but stayed 0.11 pp [0.07, 0.15] behind it. | [llm-long-search-v1](experiments/llm-long-search-v1/RESULTS.md) |
| **A tuned formula matches FunSearch.** On 5,000-item Weibull instances, a 21-weight linear rule tuned on CPU reaches −3.28 pp [−3.32, −3.22] against best fit, and FunSearch's heuristic −3.33. On 80-item instances nothing we tried beats best fit. Our evaluator reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly. | [bp-ceiling-v1](experiments/bp-ceiling-v1/RESULTS.md) |
| **On a second benchmark, textbook heuristics beat the LLM-designed ones.** LLM heuristic-design papers (MCTS-AHD and successors) build TSP tours one city per call, and compare only with nearest neighbour. The interface hands every call the whole distance matrix, so a function can plan a full tour and emit it city by city. Greedy edge + 2-opt + Or-opt (about 100 lines) emitted this way is 1.85% / 2.44% / 2.85% above the reference at 50 / 100 / 200 cities, against 4.76% / 6.47% / 8.88% for the best published LLM results and about 23–26% for nearest neighbour. Pre-registered, on MCTS-AHD's released test sets. | [tsp-construct-v1](experiments/tsp-construct-v1/RESULTS.md) |
| **Hidden audits catch overfitting.** In the framework tournament, hidden instances caught a program scoring 0.960 public and 0.238 hidden. | [tournament-v2](experiments/tournament-v2/RESULTS.md) |
| **The evaluator held up against deliberate cheating.** 0 of 68 attempts (28 hand-written, 40 written by Sonnet and Haiku told to cheat) gained a material unearned score. | [gate-redteam-v1](experiments/gate-redteam-v1/RESULTS.md) |

## How we chose the defaults

We built more than is in the loop, then tested each part against a simple alternative at a matched
budget. Parts that did not earn their place were removed from `main`. Their code and studies are kept
in tag [`archive/full-research-2026-10-04`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04),
the complete research record, so every number below can still be reproduced.

| Decision | What we found | Study |
|---|---|---|
| **Audit on hidden instances** | Selection scores overstate quality: a model-proposed rule that went 1 win / 0 losses on 1,000 cases went 3 wins / 14 losses on 10,000 fresh ones; a tournament program scored 0.960 public and 0.238 hidden | [tournament-v2](experiments/tournament-v2/RESULTS.md); Codex pilot (archived) |
| **Score candidates in an integrity gate** | 0 of 68 deliberate exploits gained a material unearned score | [gate-redteam-v1](experiments/gate-redteam-v1/RESULTS.md) |
| **Explain two-sidedly** | One-sided simplification "improved" 26 of 43 candidates beyond tolerance, 21 of them into plain best fit: repairs, not explanations | [simplify-v1](experiments/simplify-v1/EXPERIMENT.md) |
| **Always compare with cheap baselines** | Minutes of CPU tuning matched FunSearch's evolved heuristic, and Sum-of-Squares (2006) beats it | [bp-ceiling-v1](experiments/bp-ceiling-v1/RESULTS.md), [online-frontier-v1](experiments/online-frontier-v1/RESULTS.md) |
| **A simple loop (one model, one edit per step)** | At a common early spend the single-model loops were ahead of ShinkaEvolve and of the triage loop (partial study, 17 of 60 runs). In the full grid on open models (60 runs), no framework differed significantly from ShinkaEvolve. We kept the simplest, which leaves an edit trail the report can follow | [tournament-v2](experiments/tournament-v2/RESULTS.md); [tournament-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/tournament-v1) (archived) |
| **No idea triage** (a cheap model ranking ideas for an expensive one) | The implementing model decided success: Opus improved the program on 62 of 62 ideas, Sonnet on 60, Haiku on 10. The best rankers were only modestly better than chance (AUC 0.600 and 0.564 against 0.499), and ranked triage did not beat random tiers | [idea-table-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/idea-table-v1) (archived) |
| **No memory of past failures in the prompt** | In a closed loop of 900 calls it did not improve the audited result (+4.73 bins, CI [−0.23, +12.96]). It cut harmful proposals from 80% to 15–20%, mostly by making the model propose changes that do nothing | [memory-ablation-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/memory-ablation-v1) (archived) |
| **No gates built from shrunk counterexamples** | In mutation search, replaying counterexamples cut harmful drift against random replay (0.0007 vs 0.023 excess bins) but never beat best fit. A counterexample promotion gate beat score-only promotion but did not clearly beat a gate of random inputs, and a softer gate with fresh validation gave no final-quality gain. Replayed on LLM proposals, the strict veto blocked the two largest gains (2 runs, not significant), mainly because 554 of its 635 inputs were 2 items long. Tested live, short-stream selection and short-stream gates made the loop pick short-sighted rules: every run selecting on 5,000-item streams beat every run selecting on 200- or 80-item streams. The loop's own non-regression check uses the full public instances and stays on; `--no-gate` turns it off | [local-v2](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/local-v2), [gate-v3](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/gate-v3), [soft-gate-v4](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/soft-gate-v4), [overfit-gates-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/overfit-gates-v1), [short-horizon-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/short-horizon-v1) (archived) |
| **No adaptive strategy controller** | Its timing of switches mattered on one benchmark (Heilbronn: 130 wins, 70 losses against the same moves in shuffled order) but not on another (LABS), where a simple tuned restart rule still won. Development seeds overstated its gain in both versions. Only the simple rule is kept, as the opt-in `--patience T` | [strategist-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/strategist), [strategist-v2](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/strategist-v2) (archived) |
| **Start from the strongest known method** | From best fit, the loop got close to FunSearch; from Sum-of-Squares, it beat Sum-of-Squares by 2.3 bins per instance. Telling the model what information its function could use, without a strong starting program, did not help (0 of 4 runs beat FunSearch) | [llm-from-ss-v1](experiments/llm-from-ss-v1/RESULTS.md), [llm-long-search-v1](experiments/llm-long-search-v1/RESULTS.md); [llm-informed-v1](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/experiments/llm-informed-v1) (archived) |

## How we kept ourselves honest

- **Protocols written before each run**, committed to git, with any later change disclosed
  ([example](experiments/online-beyond-ss-v1/PROTOCOL.md)).
- **Fresh audits.** Final test inputs are generated only after the search ends and never feed back.
- **Matched budgets.** Every compared method gets the same evaluator calls or the same dollars.
- **Controls designed to catch luck:** random-input gates, timing-shuffled replays and separate
  development, validation and confirmatory seeds.
- **Cheap baselines first.** An LLM search has to beat what minutes of CPU tuning reach.
- **Hard spend caps.** Every LLM call reserves its worst-case cost before it is sent, and every call is
  logged to `usage.jsonl`.
- **Independent reviews.** Reviewers who did not run a study recomputed its numbers from the saved data
  ([docs/reviews/](docs/reviews/README.md)); corrections are recorded in the studies.
- **A public record of what went wrong.** Credit exhaustion, cut-short runs, corrections and decisions
  are logged in [docs/logs/OVERNIGHT-2026-10-03.md](docs/logs/OVERNIGHT-2026-10-03.md).

## Reproducing the experiments

```bash
pip install -r requirements.txt
python -m pytest tests -q                                       # no API calls
python -m autoresearch.check --all                              # score every problem's starting program, no LLM
```

- **Each study** has exact reproduce commands in its write-up; see [experiments/README.md](experiments/README.md).
- **Paid runs** record every call in `usage.jsonl` and have `--mock` modes for offline reproduction.
- **Archived studies, and the code of bp-ceiling-v1 and simplify-v1,** run from tag
  `archive/full-research-2026-10-04`, which also holds the code of the removed components.

## Add a problem

- Add a folder under `problems/` with `problem.md`, `initial.py`, `evaluate.py` and `verify.py`
  ([contract](problems/README.md)). The loop and the tournament need no changes.
- Optionally add `baselines/*.py`, each an ordinary candidate program; the report scores them on the same
  instances.
- Online problems use the gate's online mode, which calls the candidate once per arriving item so it
  cannot look ahead. [problems/bin_packing_online](problems/bin_packing_online/) is the example.

## Repository layout

```
autoresearch/   one-command loop, integrity gate, two-sided explanation, ShinkaEvolve launcher
tournament/     the search arms the loop runs on, and whole-framework comparison at equal budgets
falsify/        FunSearch's published bin-packing heuristics, used as reference code by the bin-packing studies
problems/       circle packing, Erdős squares, Erdős discrepancy, sum-difference, online bin packing
experiments/    one folder per study, with protocol, write-up and raw data (index: experiments/README.md)
runs/           committed example runs of autoresearch.loop (other runs are git-ignored)
tests/          all tests
docs/           literature review, coordination log, independent reviews (map: docs/README.md)
```

## Related work

- FunSearch (Romera-Paredes et al., *Nature* 2024) beat best fit on OR-Library and Weibull bin packing
  by evolving code that scores each bin.
- The math problems come from Georgiev, Gómez-Serrano, Tao and Wagner (2025). ShinkaEvolve is the
  external baseline.
- [docs/literature/related-work.md](docs/literature/related-work.md) reviews about 60 papers: which of
  our results are new, which independently reproduce published findings, and what the literature
  implies for each component.
- Weighted Sum-of-Squares is a known family (Csirik et al. 2006, §8.1). FWSS's fill-based weights, its
  horizon-aware finish and the comparison with LLM-designed heuristics are what is new.

## Status and limitations

- **FWSS is not yet independently re-implemented.** A second session re-ran its code on new instances
  and matched it (1.83 bins above the optimum).
- **One problem family for the headline.** The bin-packing results are on FunSearch's Weibull and
  OR-Library benchmarks.
- **Small selection suites.** The loop selects on 2 public instances. That promoted real gains, but its
  `OVERFIT?` flag, also based on 2 hidden instances, raised false alarms that a 100-instance audit
  overturned ([llm-from-ss-v1](experiments/llm-from-ss-v1/RESULTS.md)).
- **Modest models and budgets.** Most LLM results come from one open model and a few hundred steps per run.
- **Not a security sandbox.** The integrity gate isolates an honest loop; it is not a hardened sandbox.

## Credits and citation

ShinkaEvolve (Sakana AI, Apache-2.0). Problem statements, scoring rules and the n = 26 circle
construction come from the AlphaEvolve problem repository (Apache-2.0 / CC-BY 4.0). FunSearch's
bin-packing heuristics in `problems/bin_packing_online/baselines/` come from google-deepmind/funsearch
(Apache-2.0). Code was written during the event with help from Codex and Claude.

To cite this repository: Swedish Science Mafia (2026), *Autoresearch that checks its own claims*,
AI x Science Hackathon, London. https://github.com/swedishScienceMafia/swedishScienceMafia
