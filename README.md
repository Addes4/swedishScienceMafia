# Swedish Science Mafia: autoresearch that checks its own claims

Our entry for Track 1, *Build Your Own Algorithm Autoresearch Framework*, at the AI x
Science Hackathon (London, 3–4 October 2026).

An autoresearch loop proposes candidate algorithms, evaluates them, keeps what works and
proposes again. We built four pieces of such a loop. Each one targets a way these loops
fool themselves, and each was tested in its own controlled experiment:

| Part | Question it answers | Code | Write-up |
|---|---|---|---|
| **Falsify** | Can executable counterexamples (inputs where a candidate lost to the baseline) stop the search from promoting regressions? | [`falsify/`](falsify/) | [falsify/README.md](falsify/README.md) |
| **Simplify & explain** | After search, what is the shortest rule with the same measured quality, and which terms actually matter? | [`falsify/simplify.py`](falsify/simplify.py) | [simplify-v1](experiments/simplify-v1/EXPERIMENT.md) |
| **Strategist** | When should the loop make a small edit, rewrite, crossover or restart, and is the benefit timing or luck? | [`strategist/`](strategist/) | [strategist/README.md](strategist/README.md) |
| **Autoresearch triage** | Can a fast ranker send promising ideas to strong models and long shots to cheap ones? | [`autoresearch/`](autoresearch/), [`problems/`](problems/) | [autoresearch/README.md](autoresearch/README.md) |

```
 propose ──► evaluate in a fixed evaluator ──► promote? ──► keep and propose again
 (mutation, Codex, Claude)        │              ▲
                                  ▼              │  Falsify: gate on archived failures
                       archive of executable ────┘
                       counterexamples
 Strategist: chooses the next kind of move      Simplify: explains what was kept
 Triage: chooses which model implements an idea
```

The parts share one experimental discipline, and Falsify, Simplify and Strategist share
the bin-packing evaluator. They are not yet wired into one pipeline. On the night of
3 October, six follow-up experiments tested them with real LLM calls, stronger baselines
and a new bin-packing benchmark with room to improve ([below](#overnight-experiments-3-october)).

## How we kept ourselves honest

- **Protocols written before each run**, with any later design change disclosed
  ([example](experiments/PROTOCOL-v3.md)).
- **Matched budgets.** Every arm pays for the same evaluator calls, including ones it ignores.
- **Fresh audits.** Final test inputs are generated only after search ends and never feed back.
- **Controls designed to catch luck**: random-input gates, timing-shuffled replays and
  counterfactual forks.
- **Provenance.** Every experiment folder keeps its config, raw traces, source snapshot and hashes.
- **Integrity gate** for LLM-written code: separate process, credentials stripped, hidden
  instances, and an independent strict re-check of anything that beats a known record.
  Red-teamed with 68 exploit attempts ([gate-redteam-v1](experiments/gate-redteam-v1/RESULTS.md)).
- **Hard spend caps.** Every LLM call reserves its worst-case cost before it is sent, the
  run stops before it could pass its cap, and every call is logged to `usage.jsonl`.
- **Cheap baselines first.** An LLM search has to beat what minutes of CPU tuning reach
  ([bp-ceiling-v1](experiments/bp-ceiling-v1/RESULTS.md)).

## Results at a glance

**On the original 80-item bin-packing instances, nothing beats best-fit on fresh data.**
On FunSearch's 5,000-item Weibull instances, a 21-weight rule tuned in minutes of CPU does,
by as much as FunSearch's LLM-evolved heuristic ([overnight experiments](#overnight-experiments-3-october)).
What the first round of experiments shows:

| Study | Finding |
|---|---|
| [Falsify v2](experiments/RESULTS.md), 50 seeds × 500 generations | Counterexample replay cut drift away from best-fit: 0.000725 vs 0.023 excess bins for random replay. Difference −0.0223, 95% CI [−0.0378, −0.0108]. |
| [Recovery from first-fit](experiments/RESULTS.md), 20 seeds | All arms recovered from 0.33 excess bins. Counterexample arms got closer: −0.0106 vs random, CI [−0.0182, −0.0032]. |
| [Codex pilot](experiments/RESULTS.md) | A revision with 1 win / 0 losses on 1,000 cases had 3 wins / 14 losses on 10,000 fresh cases. |
| [V3 promotion gates](experiments/gate-v3/RESULTS.md), 40 seeds | Counterexample gate beat score-only promotion (−0.0022, CI [−0.0041, −0.0006]). Against a random gate: inconclusive. |
| [V4 soft gates](experiments/soft-gate-v4/RESULTS.md), 40 seeds | Validation-backed bounded losses let through 15/16 beneficial proposals and blocked 328/599 harmful ones (strict: 14/16, 270/599). No final-quality gain. |
| [Simplify](experiments/simplify-v1/EXPERIMENT.md), 43 candidates | The 11-term evolved "winner" is exactly best-fit. 14 candidates reduce faithfully to best-fit; 21 more were worse and got repaired toward it. |
| [Strategist](strategist/RESULTS.md), 200 seeds × 4 benchmarks | Beats fixed move mixes on LABS and NK; ties the static mix on Heilbronn. Switch timing matters on Heilbronn (130/0/70 seed wins/ties/losses vs shuffled timing). A tuned "restart after 64 stalls" rule beats it on LABS and NK. |
| Autoresearch triage | Tested overnight in the [idea table](experiments/idea-table-v1/RESULTS.md): ranking did not beat random assignment. |

These first-round Falsify, Simplify and Strategist runs use local CPU only, with no LLM API
calls. A full review of them, with every number checked against the JSON, is in
[output/pdf](output/pdf/Swedish_Science_Mafia_Experiment_Review.pdf).

### Overnight experiments (3 October)

Each folder has a protocol written before the main run, `RESULTS.md`, `summary.json`, raw
traces and reproduce commands. Intervals are 95% bootstrap intervals. Decisions, incidents
and spend across all six are in [OVERNIGHT-2026-10-03.md](experiments/OVERNIGHT-2026-10-03.md).

| Study | Finding |
|---|---|
| [Bin-packing ceiling](experiments/bp-ceiling-v1/RESULTS.md), CPU only | The 80-item instances were the ceiling, not the feature set: there nothing beats best-fit, and FunSearch's Weibull heuristic is 15.0 points worse. On Weibull 5k, excess over the L2 bound relative to best-fit is −3.28 pp [−3.32, −3.22] for a 21-weight linear rule, −3.31 for a grid-tuned two-threshold rule and −3.33 for FunSearch's heuristic. Our evaluator reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly. |
| [Memory ablation](experiments/memory-ablation-v1/RESULTS.md), 900 Haiku calls | Haiku wrote `priority(item, bins)` code on Weibull 5k, 10 seeds × 30 calls per arm. Executable counterexamples did not improve the audited final policy: −0.24 bins vs best-fit, against −4.96 with prose memory and −1.52 with none (executable − prose +4.73, CI [−0.23, +12.96]). FunSearch's heuristic: −66.0. Memory cut harmful proposals from 80% to 15–20%, mostly by making the model propose no-op changes. |
| [Idea table](experiments/idea-table-v1/RESULTS.md), 62 ideas × 3 models | The model decided success, not the idea: Opus improved the program on 62/62 ideas, Sonnet 60/62, Haiku 10/62. Ranker AUC for predicting success: Codex 0.600, Claude Opus 0.564, Claude Haiku 0.516, Jev 0.484, random 0.499. Ranked triage did not beat random tiers; Sonnet on every idea was best per dollar (60 improvements for $4.00). |
| [Tournament v1](experiments/tournament-v1/RESULTS.md), partial | Five complete frameworks at $1.10 per run. Credit ran out after 17 of 60 runs. Circle packing and Erdős squares saturate within 1–3 Sonnet calls. At a common early spend, the single-model loops were ahead of ShinkaEvolve and triage was behind. Not a budget-matched comparison. The [v2 folder](experiments/tournament-v2/) adds a route through open models on the Hugging Face router. |
| [Strategist v2](experiments/strategist-v2/RESULTS.md), 200 fresh seeds | v2 beats v1 on LABS (+0.137 merit factor [0.043, 0.236]) and NK, ties on Heilbronn. Almost all of the gain comes from making crossover earn its place. A patience rule tuned on dev seeds still wins on LABS (−0.220). |
| [Gate red-team](experiments/gate-redteam-v1/RESULTS.md), 68 attempts | 28 hand-written exploits and 40 written by Sonnet and Haiku told to cheat. None gained a material unearned score; the only gap is below the 1e-9 tolerance. Three hardening fixes are merged. |

**What this adds up to.** The checks themselves earned their place: fresh audits, cheap
baselines, a red-teamed gate, shuffled-timing replays and forks. The search add-ons we
tested did not beat simple alternatives: counterexample memory, triage ranking and the
adaptive controller. Matching FunSearch took a tuned 21-weight rule, not an LLM.

**Related work.** FunSearch (Nature 2024) beat best-fit on OR-Library and Weibull
bin packing by evolving code that sees every bin. [falsify/README.md](falsify/README.md#relation-to-funsearch)
explains how our setup differs. The triage loop uses ShinkaEvolve as its baseline, and
the math problems come from Georgiev, Gómez-Serrano, Tao and Wagner (2025).
[context/related-work.md](context/related-work.md) reviews about 60 related papers. It covers
which of our results are new, which independently reproduce published findings, and what
the literature implies for each part.

## Quick start

You need Python 3.10+ (we used 3.12) and a C++17 compiler (`c++`); the first run compiles
small evaluators. Run everything from the repository root.

```bash
pip install -r requirements.txt
python -m pytest tests -q                                 # 138 tests, no API calls
python3 -m strategist.demo --benchmark labs --seed 1000   # one research run, narrated
python3 -m falsify.pilot --out experiments/my-pilot        # evaluate hypotheses, shrink failures
python3 -m falsify.simplify --out experiments/my-simplify  # simplify and explain (~25 s)
```

Open [experiments/report.html](experiments/report.html) and
[experiments/strategist-v1/report.html](experiments/strategist-v1/report.html) in a
browser for the interactive reports. Commands for reproducing each full experiment are
in the part's README.

The autoresearch triage loop needs packages and API keys:

```bash
cp .env.example .env                 # add ANTHROPIC_API_KEY and TYPESAFE_API_KEY; .env is git-ignored
python -m autoresearch.check --all   # score every problem's starting program, no LLM
python -m autoresearch.triage problems/erdos_squares --rounds 10 --budget 10
```

The starting programs for circle packing and Erdős discrepancy are unseeded and random,
so `check --all` gives slightly different scores for them on each run.

## Add a problem

- **Strategist:** subclass `Problem` in [strategist/problems.py](strategist/problems.py)
  (five methods: random, score, edit, rewrite, crossover).
- **Autoresearch:** add a folder under [problems/](problems/README.md) with `problem.md`,
  `initial.py`, `evaluate.py` and `verify.py`. The framework itself needs no changes. For
  online problems, the gate's online mode calls the candidate once per arriving item, so it
  cannot look ahead; [problems/bin_packing_online](problems/bin_packing_online/) is the example.
- **Falsify:** the evaluator is specific to bin packing for now; new item families go in
  `instance()` in [falsify/core.py](falsify/core.py).

## Repository layout

```
falsify/        bin-packing evaluators (C++), replay/gate/soft-gate search, simplify, closed LLM loop
strategist/     adaptive strategy controller (v1, v2), benchmarks, forks, stats, report
autoresearch/   triage loop, rankers, Claude client, integrity gate, spend cap, idea table
tournament/     whole-framework comparison on Modal at equal dollar budgets
problems/       circle packing, Erdős squares, Erdős discrepancy, sum-difference, online bin packing
experiments/    one folder per experiment: protocol, config, traces, audits, source snapshot
tests/          all tests
output/pdf/     experiment review and addenda
context/        hackathon brief, website text, the supplied papers and a literature review
```

## Credits

ShinkaEvolve (Sakana AI, Apache-2.0). Problem statements, scoring rules and the n = 26
circle construction come from the AlphaEvolve problem repository (Apache-2.0 / CC-BY 4.0).
The supplied papers are in `context/`. Code was written during the event with help from
Codex and Claude.
