# Swedish Science Mafia: autoresearch that checks its own claims

Our entry for Track 1, *Build Your Own Algorithm Autoresearch Framework*, at the AI x
Science Hackathon (London, 3–4 October 2026).

An autoresearch loop proposes candidate algorithms, evaluates them, keeps what works and proposes
again. Such loops can fool themselves: they overfit the instances they select on, chase luck,
exploit their own evaluator, and credit elaborate machinery for gains a simple baseline would also
reach. This repository contains:
- a loop that runs with one command;
- the components we built to catch those failures;
- a series of controlled experiments testing which components earn their place, indexed in
  [experiments/README.md](experiments/README.md).

**In short:** the checks earned their place, but the search add-ons we tested did not beat simple
alternatives. On FunSearch's bin-packing benchmark, a 21-weight rule tuned in minutes of CPU matched
the LLM-evolved heuristic. Every number below links to a write-up with its protocol, raw data and
reproduce commands.

## Contents

- [Quick start](#quick-start)
- [What one run does](#what-one-run-does)
- [Key findings](#key-findings)
- [How we kept ourselves honest](#how-we-kept-ourselves-honest)
- [Components](#components)
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
  [autoresearch/README.md](autoresearch/README.md#one-command-loop) describes the outputs, and
  [autoresearch/LOOP.md](autoresearch/LOOP.md) records the design decisions and the build log.

## What one run does

Every default is the setting our controlled experiments supported; the rest are flags.

1. **Propose and implement.** One LLM call per step edits the current best program (`lean`). In
   [tournament-v1](experiments/tournament-v1/RESULTS.md) the single-model loops were ahead of
   ShinkaEvolve and triage at a common early spend (partial study: 17 of 60 runs complete).
2. **Score** in the [integrity gate](autoresearch/gate.py): a separate process, a static scan, a
   strict re-check of record scores, and hidden instances. None of 68 exploit attempts gained a
   material unearned score ([gate-redteam-v1](experiments/gate-redteam-v1/RESULTS.md)).
3. **Keep** a candidate only if its public score improves and it does not regress on instances where
   earlier candidates regressed. This is Falsify's archive, used as a gate
   ([gate-v3](experiments/gate-v3/RESULTS.md)). Used as prompt memory instead, it mostly produced
   no-op proposals ([memory-ablation-v1](experiments/memory-ablation-v1/RESULTS.md)).
4. **Audit** the final program on hidden instances that are never used for selection. It flags
   `OVERFIT?` if the public score rose while the hidden score fell. Hidden instances caught a
   program scoring 0.960 public and 0.238 hidden ([tournament-v2](experiments/tournament-v2/RESULTS.md)).
5. **Explain** it by two-sided ablation ([explain_code.py](autoresearch/explain_code.py)).
   - A part is dropped only if the score stays within ±0.002 *in both directions*, so the explanation
     describes the program actually found.
   - A removal that raises the score is labelled `REPAIRED (not an explanation)`.
   - This matters because in [simplify-v1](experiments/simplify-v1/EXPERIMENT.md), one-sided
     simplification improved 26 of 43 candidates beyond the tolerance, 21 of them into best-fit:
     repairs, not explanations.
   - Program simplification itself is standard in genetic programming (survey: Javed, Gobet and Lane
     2022, [doi:10.1007/s10618-022-00830-7](https://doi.org/10.1007/s10618-022-00830-7)).
6. **Compare** with the problem's baselines on the same public and hidden instances. Cheap baselines
   can match FunSearch ([bp-ceiling-v1](experiments/bp-ceiling-v1/RESULTS.md)), so any gain is
   stated against them.

Off by default, but available as flags or modules:

| Option | Why it is off |
|---|---|
| `--patience T` (Strategist's restart rule) | Inside an LLM loop it was tested only in the partial tournament, where lean with gate and patience was not significantly ahead of ShinkaEvolve (+0.195, Holm p = 0.070) |
| `--independent` (no history, no parent) | About as good as lean in tournament-v1 (+0.209 vs +0.233); lean leaves an edit trail that the report and the explanation can follow |
| triage (`python -m autoresearch.triage`) | Ranking ideas did not beat random tiers in the [idea table](experiments/idea-table-v1/RESULTS.md); Sonnet on every idea was best per dollar |
| prompt memory of failures | Did not improve the audited result, and made the model propose no-op changes ([memory-ablation-v1](experiments/memory-ablation-v1/RESULTS.md)) |
| `--no-gate` | For problems with one public instance the gate has nothing to archive; elsewhere it is on |

## Key findings

The full list of studies, with protocols and data, is in
[experiments/README.md](experiments/README.md). Intervals are 95% paired bootstrap intervals.

| Finding | Evidence |
|---|---|
| **Best-fit is unbeatable on short instances; on long ones a tuned formula matches FunSearch.** On 80-item instances no rule we tried beats best-fit, and FunSearch's Weibull heuristic is 15 points worse. On 5,000-item Weibull instances, excess over the L2 bound relative to best-fit is −3.28 pp [−3.32, −3.22] for a 21-weight linear rule tuned on CPU, −3.31 for a tuned two-threshold rule and −3.33 for FunSearch's heuristic. Our evaluator reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly. | [bp-ceiling-v1](experiments/bp-ceiling-v1/RESULTS.md) |
| **Counterexamples work as a gate, not as prompt memory.** A counterexample gate beat score-only promotion (−0.0022 excess bins, CI [−0.0041, −0.0006]); against a random-input gate the result is inconclusive. In a closed LLM loop (900 Haiku calls), counterexamples in the prompt did not improve the audited result (executable − prose memory +4.73 bins, CI [−0.23, +12.96]). Memory cut harmful proposals from 80% to 15–20%, mostly by making the model propose changes that do nothing. | [gate-v3](experiments/gate-v3/RESULTS.md), [memory-ablation-v1](experiments/memory-ablation-v1/RESULTS.md) |
| **The implementing model decides success, not the idea.** Opus improved the program on 62/62 ideas, Sonnet on 60/62, Haiku on 10/62. Rankers predicting success scored near chance (AUC: Codex 0.600, Claude Opus 0.564, Jev 0.484, random 0.499), and ranked triage did not beat random tiers. | [idea-table-v1](experiments/idea-table-v1/RESULTS.md) |
| **Simple loops are hard to beat.** At a common early spend, lean (+0.233 AUC, CI [0.096, 0.386]) and independent sampling (+0.209) were ahead of ShinkaEvolve, and triage was behind (−0.156). Final scores tied, because two of three problems saturate within 1–3 calls. Partial study. | [tournament-v1](experiments/tournament-v1/RESULTS.md) |
| **Fresh audits catch overfitting.** A Codex revision with 1 win / 0 losses on 1,000 cases had 3 wins / 14 losses on 10,000 fresh cases. Hidden instances caught a program scoring 0.960 public and 0.238 hidden. | [experiments/RESULTS.md](experiments/RESULTS.md), [tournament-v2](experiments/tournament-v2/RESULTS.md) |
| **Timing controls separate skill from luck.** The adaptive controller's switch timing matters on Heilbronn (130/0/70 seed wins/ties/losses against the same moves in shuffled order) but not on LABS. v2 beats v1 on LABS (+0.137 merit factor, CI [0.043, 0.236]), but a patience rule tuned on dev seeds still wins there. In both versions, development seeds overstated the gain, and held-out seeds exposed it. | [strategist/RESULTS.md](strategist/RESULTS.md), [strategist-v2](experiments/strategist-v2/RESULTS.md) |
| **The evaluator held up against deliberate cheating.** 0 of 68 attempts (28 hand-written, 40 written by Sonnet and Haiku told to cheat) gained a material unearned score. The only gap is a sub-tolerance overlap worth about 3e-10. | [gate-redteam-v1](experiments/gate-redteam-v1/RESULTS.md) |

## How we kept ourselves honest

- **Protocols written before each run**, with any later design change disclosed
  ([example](experiments/PROTOCOL-v3.md)).
- **Matched budgets.** Every arm pays for the same evaluator calls, including ones it ignores.
- **Fresh audits.** Final test inputs are generated only after search ends and never feed back.
- **Controls designed to catch luck:** random-input gates, timing-shuffled replays, counterfactual
  forks, and separate dev, validation and confirmatory seeds.
- **Provenance.** Every experiment folder keeps its config, raw traces, source snapshot and hashes.
- **An integrity gate** for LLM-written code: a separate process, stripped credentials, hidden
  instances, and an independent strict re-check of anything that beats a known record.
- **Hard spend caps.** Every LLM call reserves its worst-case cost before it is sent, the run stops
  before it could pass its cap, and every call is logged to `usage.jsonl`.
- **Cheap baselines first.** An LLM search has to beat what minutes of CPU tuning reach.
- **A public record of what went wrong.** Credit exhaustion, cut-short runs, corrections and
  decisions are logged in [experiments/OVERNIGHT-2026-10-03.md](experiments/OVERNIGHT-2026-10-03.md).

## Components

```
 propose ──► score in the integrity gate ──► keep? ──► audit on hidden instances ──► explain, compare
 (lean loop, ShinkaEvolve,     │                 ▲
  triage, Codex, Claude)       ▼                 │  Falsify: gate on archived failures
                     archive of executable ──────┘
                     counterexamples
 Strategist: chooses the next kind of move    Triage: chooses which model implements an idea
```

| Component | Question it answers | Code | Documentation |
|---|---|---|---|
| **One-command loop** | Run the whole loop on any problem, with a spend cap, audit and report | [`autoresearch/loop.py`](autoresearch/loop.py) | [autoresearch/README.md](autoresearch/README.md), [LOOP.md](autoresearch/LOOP.md) |
| **Integrity gate** | Did the candidate earn its score? | [`autoresearch/gate.py`](autoresearch/gate.py), [`sandbox.py`](autoresearch/sandbox.py) | [problems/README.md](problems/README.md) |
| **Falsify** | Can executable counterexamples stop the search from promoting regressions? | [`falsify/`](falsify/) | [falsify/README.md](falsify/README.md) |
| **Simplify & explain** | What is the shortest rule with the same measured quality, and which terms matter? | [`falsify/simplify.py`](falsify/simplify.py), [`autoresearch/explain_code.py`](autoresearch/explain_code.py) | [simplify-v1](experiments/simplify-v1/EXPERIMENT.md) |
| **Strategist** | When should the loop edit, rewrite, cross over or restart, and is the benefit timing or luck? | [`strategist/`](strategist/) | [strategist/README.md](strategist/README.md) |
| **Triage and idea table** | Can a fast ranker route ideas to model tiers? Score any routing policy offline | [`autoresearch/triage.py`](autoresearch/triage.py), [`ideatable.py`](autoresearch/ideatable.py) | [autoresearch/README.md](autoresearch/README.md) |
| **Tournament** | Which complete framework gets furthest at an equal dollar budget? | [`tournament/`](tournament/) | [tournament/README.md](tournament/README.md) |

## Reproducing the experiments

```bash
pip install -r requirements.txt
python -m pytest tests -q                                  # 182 tests, no API calls
python -m autoresearch.check --all                         # score every problem's starting program, no LLM
python -m strategist.demo --benchmark labs --seed 1000     # one Strategist run, narrated
python -m falsify.pilot --out experiments/my-pilot         # evaluate hypotheses, shrink failures
python -m falsify.simplify --out experiments/my-simplify   # simplify and explain (~25 s)
```

- **Each study** has exact reproduce commands in its write-up; see [experiments/README.md](experiments/README.md).
- **Interactive reports:** [experiments/report.html](experiments/report.html) (Falsify) and
  [experiments/strategist-v1/report.html](experiments/strategist-v1/report.html) can be opened in a
  browser after cloning.
- **Paid runs:** studies that called a paid API record every call in `usage.jsonl` and have `--mock`
  modes for offline reproduction.
- **Random starting programs:** the starting programs for circle packing and Erdős discrepancy are
  unseeded and random, so `check --all` gives slightly different scores for them on each run.

## Add a problem

- **The loop, triage and tournament** need no changes.
  - Add a folder under `problems/` with `problem.md`, `initial.py`, `evaluate.py` and `verify.py`
    ([contract](problems/README.md)).
  - Optionally add `baselines/*.py`, each an ordinary candidate program; the report scores them on the
    same instances.
  - Online problems use the gate's online mode, which calls the candidate once per arriving item so
    it cannot look ahead. [problems/bin_packing_online](problems/bin_packing_online/) is the example.
- **Strategist:** subclass `Problem` in [strategist/problems.py](strategist/problems.py), implementing
  five methods: random, score, edit, rewrite and crossover.
- **Falsify:** the evaluator is specific to bin packing; new item families go in `instance()` in
  [falsify/core.py](falsify/core.py).

## Repository layout

```
autoresearch/   one-command loop, explanation, integrity gate, triage loop, rankers, idea table, spend cap
falsify/        bin-packing evaluators (C++), replay/gate/soft-gate search, simplify, closed LLM loop
strategist/     adaptive strategy controller (v1, v2), benchmarks, forks, statistics, report
tournament/     whole-framework comparison on Modal at equal dollar budgets
problems/       circle packing, Erdős squares, Erdős discrepancy, sum-difference, online bin packing
experiments/    one folder per study (index: experiments/README.md) and the overnight log
runs/           committed example runs of autoresearch.loop (other runs are git-ignored)
tests/          all tests
context/        hackathon brief, website text, supplied papers, literature review and addendum
output/         experiment review PDF, pitch draft, paper outlines
```

## Related work

- FunSearch (Romera-Paredes et al., *Nature* 2024) beat best-fit on OR-Library and Weibull bin
  packing by evolving code that sees every bin. [falsify/README.md](falsify/README.md#relation-to-funsearch)
  explains how our setup differs.
- The math problems come from Georgiev, Gómez-Serrano, Tao and Wagner (2025). ShinkaEvolve is the
  external baseline.
- [context/related-work.md](context/related-work.md) reviews about 60 papers: which of our results are
  new, which independently reproduce published findings, and what the literature implies for each
  component.
- [context/related-work-addendum.md](context/related-work-addendum.md) adds papers on the questions
  the experiments left open. For example, our CPU-tuned bin-packing result is an extreme case of
  separating algorithm structure from parameter tuning (LLaMEA-HPO, TIDE).

## Status and limitations

- **No new algorithm.** We did not find an algorithm better than published ones. Our contribution is
  the checking machinery and the controlled comparisons.
- **Two partial studies.** The Anthropic credit ran out during the overnight runs. The idea table has
  62 of 114 ideas complete for all three models, and the tournament has 17 of 60 complete runs. Both
  write-ups give the one-command reruns and their cost.
- **Proxy moves.** Strategist and the first-round Falsify studies use stochastic local moves standing
  in for LLM edits, with proxy costs.
- **A different benchmark from FunSearch's.** The bin-packing evaluator reproduces FunSearch's
  published numbers, but our 80-item synthetic families differ from its benchmarks.
- **Not a security sandbox.** The integrity gate isolates an honest loop; it is not a hardened sandbox.

## Credits and citation

ShinkaEvolve (Sakana AI, Apache-2.0). Problem statements, scoring rules and the n = 26 circle
construction come from the AlphaEvolve problem repository (Apache-2.0 / CC-BY 4.0). FunSearch's
bin-packing heuristics in `problems/bin_packing_online/baselines/` come from google-deepmind/funsearch
(Apache-2.0). The supplied papers are in `context/`. Code was written during the event with help
from Codex and Claude.

To cite this repository: Swedish Science Mafia (2026), *Autoresearch that checks its own claims*,
AI x Science Hackathon, London. https://github.com/swedishScienceMafia/swedishScienceMafia
