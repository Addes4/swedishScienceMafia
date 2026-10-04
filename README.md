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

The original studies below evaluated the parts separately. An integrated pilot runner
now connects move selection, OpenAI proposal/ranking, independent evaluation, archived
failure gates, checked simplification and fresh audits across bounded packing, richer
packing code and circle packing. See the [runner guide](autoresearch/EVIDENCE_LOOP.md),
[campaign protocol](runs/CAMPAIGN_PROTOCOL.md), [live results index](runs/FINDINGS.md)
and [methods and findings log](RESEARCH_LOG.md). Live runs are still in progress;
the original evidence folders remain unchanged.

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

## Original local experiment results

**The original local studies did not beat best-fit overall on fresh data.** What those experiments show:

| Study | Finding |
|---|---|
| [Falsify v2](experiments/RESULTS.md), 50 seeds × 500 generations | Counterexample replay cut drift away from best-fit: 0.000725 vs 0.023 excess bins for random replay. Difference −0.0223, 95% CI [−0.0378, −0.0108]. |
| [Recovery from first-fit](experiments/RESULTS.md), 20 seeds | All arms recovered from 0.33 excess bins. Counterexample arms got closer: −0.0106 vs random, CI [−0.0182, −0.0032]. |
| [Codex pilot](experiments/RESULTS.md) | A revision with 1 win / 0 losses on 1,000 cases had 3 wins / 14 losses on 10,000 fresh cases. |
| [V3 promotion gates](experiments/gate-v3/RESULTS.md), 40 seeds | Counterexample gate beat score-only promotion (−0.0022, CI [−0.0041, −0.0006]). Against a random gate: inconclusive. |
| [V4 soft gates](experiments/soft-gate-v4/RESULTS.md), 40 seeds | Validation-backed bounded losses let through 15/16 beneficial proposals and blocked 328/599 harmful ones (strict: 14/16, 270/599). No final-quality gain. |
| [Simplify](experiments/simplify-v1/EXPERIMENT.md), 43 candidates | The 11-term evolved winner reduced to best-fit with equal bin counts on 800 fresh cases; this is not a proof of identical placements. 14 candidates reduce faithfully to best-fit; 21 more were worse and got repaired toward it. |
| [Strategist](strategist/RESULTS.md), 200 seeds × 4 benchmarks | Beats fixed move mixes on LABS and NK; ties the static mix on Heilbronn. Switch timing matters on Heilbronn (130/0/70 seed wins/ties/losses vs shuffled timing). A tuned "restart after 64 stalls" rule beats it on LABS and NK. |
| Autoresearch triage | Implemented and tested; comparison runs not done yet. |

These original Falsify, Simplify and Strategist runs used local CPU only, with no LLM API calls. A
full review with every number checked against the JSON is in
[output/pdf](output/pdf/Swedish_Science_Mafia_Experiment_Review.pdf).

**Related work.** FunSearch (Nature 2024) beat best-fit on OR-Library and Weibull
bin packing by evolving code that sees every bin. [falsify/README.md](falsify/README.md#relation-to-funsearch)
explains how our setup differs. The triage loop uses ShinkaEvolve as its baseline, and
the math problems come from Georgiev, Gómez-Serrano, Tao and Wagner (2025).

## Quick start

Falsify, Simplify and Strategist need only Python 3.10+ and a C++17 compiler (`c++`);
the first run compiles a small evaluator. Run everything from the repository root.

```bash
python3 -m unittest discover -s tests                     # 37 tests
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
pip install -r requirements.txt
cp .env.example .env                 # add ANTHROPIC_API_KEY and TYPESAFE_API_KEY; .env is git-ignored
python -m autoresearch.check --all   # score every problem's starting program, no LLM
python -m pytest tests/              # all 45 tests, including the integrity gate
python -m autoresearch.triage problems/erdos_squares --rounds 10 --budget 10
```

## Add a problem

- **Strategist:** subclass `Problem` in [strategist/problems.py](strategist/problems.py)
  (five methods: random, score, edit, rewrite, crossover).
- **Autoresearch:** add a folder under [problems/](problems/README.md) with `problem.md`,
  `initial.py`, `evaluate.py` and `verify.py`. The framework itself needs no changes.
- **Falsify:** the evaluator is specific to bin packing for now; new item families go in
  `instance()` in [falsify/core.py](falsify/core.py).

## Repository layout

```
falsify/        bin-packing evaluator (C++), replay/gate/soft-gate search, simplify, report
strategist/     adaptive strategy controller, benchmarks, forks, stats, report
autoresearch/   triage loop, rankers, Claude client, integrity gate, ShinkaEvolve launcher
problems/       circle packing, Erdős squares, Erdős discrepancy, sum-difference
experiments/    one folder per experiment: protocol, config, traces, audits, source snapshot
tests/          all tests
output/pdf/     experiment review and addenda
context/        hackathon brief, website text and the supplied papers
```

## Credits

ShinkaEvolve (Sakana AI, Apache-2.0). Problem statements, scoring rules and the n = 26
circle construction come from the AlphaEvolve problem repository (Apache-2.0 / CC-BY 4.0).
The supplied papers are in `context/`. Code was written during the event with help from
Codex and Claude.
