# Falsify

An experimental counterexample-guided framework for online algorithm discovery.
The first problem adapter is one-dimensional online bin packing: capacity 100,
integer items arriving sequentially, and a fixed packer that enforces feasibility.
Candidates evolve a 12-feature bin-priority function; they cannot inspect future
items, reorder inputs, change the grader, or choose invalid placements.

## What we found

Counterexample replay reduced harmful drift relative to random replay at matched
evaluation budgets. **We have not found an overall improvement over best-fit.**
The repeated-run study uses stochastic parameter mutations; a separate pilot used
Codex in this conversation to propose hypotheses, inspect failures and revise them.
This does not yet establish that counterexamples improve autonomous LLM research.

- [Results and limitations](../experiments/RESULTS.md)
- [Interactive local report](../experiments/report.html): open this file in a browser.
- [Initial protocol](../experiments/PROTOCOL.md)
- [Follow-up protocol](../experiments/PROTOCOL-v2.md)
- [Complete work handoff](../experiments/HANDOFF.md)
- [Promotion-gate experiment protocol](../experiments/PROTOCOL-v3.md)
- [Promotion-gate results](../experiments/gate-v3/RESULTS.md)

## Relation to FunSearch

FunSearch (Romera-Paredes et al., Nature 2024; in `context/Track 1 papers/`) evolved
online bin-packing heuristics that beat best-fit on the OR-Library and Weibull
benchmarks: for example 2.47% versus 4.94% excess bins over the L2 lower bound on
OR4, and 0.68% versus 3.98% on 5,000-item Weibull instances. Its heuristics take the
tightest bin only when the fit is very tight and otherwise leave room, close to the
`tight_or_roomy` idea Codex proposed here.

Falsify asks a different question: whether executable counterexamples make search
safer at a fixed evaluator budget, not whether best-fit can be beaten. Its setup also
differs in ways that plausibly make best-fit harder to beat. We have not tested which
of these matter:

- FunSearch evolves Python code that sees the remaining capacity of every open bin.
  Falsify scores each bin on its own with 12 (or 20) fixed features.
- FunSearch's margin over best-fit grows with instance size, from 0.5 points on OR1
  to 3.8 points on 100,000-item Weibull instances. Falsify instances have 80 items.
- The item distributions differ.

[bp-ceiling-v1](../experiments/bp-ceiling-v1/RESULTS.md) tested which difference matters.
- **80-item instances:** nothing beats best fit by more than 0.09 percentage points of the
  L2 bound. FunSearch's own Weibull heuristic is 15 pp worse.
- **5,000-item Weibull instances:** the existing 20-feature space beats best fit by 1.2 pp.
  Adding one feature that lets the rule open a new bin while an open one still fits reaches
  3.3 pp, level with FunSearch's code. A grid-tuned two-threshold rule also gets there.
- **Our evaluator** (`longpack.py`, `longpack.cpp`) reproduces FunSearch's published figures
  exactly on its released test data: best fit 3.98%, first fit 4.23%, FunSearch 0.68%.

The online benchmark built from this is
[problems/bin_packing_online](../problems/bin_packing_online/). There, a candidate supplies
`priority(item, bins)` and the integrity gate calls it once per arriving item, so it cannot look
ahead.

## Closed-loop LLM memory ablation

[memory-ablation-v1](../experiments/memory-ablation-v1/RESULTS.md) is the first autonomous LLM
test of Falsify's claim. Claude Haiku 4.5 wrote `priority(item, bins)` code on Weibull 5k in
30-call closed loops, 10 seeds per arm. The arms compared no memory, a prose summary of past
failures, and executable counterexamples.
- **Final policy:** executable counterexamples did not improve the audited result. Executable
  minus prose was +4.73 bins per instance [−0.23, +12.96]; executable minus none was +1.29
  [+0.00, +3.86].
- **Behaviour:** memory of either kind cut harmful proposals from 80% to 15–20%, but mostly by
  making the model propose no-op changes (65–82% of proposals).
- **Use counterexamples** as a diagnostic and regression guard, not as a proven way to improve
  proposals.

The loop is in `closed_loop.py` and `closed_loop_code.py`, the memory sections in `memory.py`
and `memory_code.py`, and the spend-capped client in `llm.py`. Programs are evaluated in a
sandbox by `code_eval.py`, locally or on Modal.

## Run locally

Requires Python 3.10+ and a C++17 compiler (`c++`). No Python packages, GPU, API
key, or remote service are needed. The first invocation compiles a tiny evaluator.
Run every command from the repository root; paths below are relative to it.

```sh
python3 -m unittest discover -s tests -p 'test_core.py' -v
python3 -m unittest discover -s tests -p 'test_contextual.py' -v
python3 -m falsify.pilot --out experiments/my-pilot
python3 -m falsify.search --seeds 50 --generations 500 --neutral-drift --audit-seed 961748941 --out experiments/my-reproduction
```

Use a fresh output directory. Use a fresh audit seed for a new exploratory design;
reusing the published seed is appropriate when reproducing the exact experiment.
To reproduce the original v1, use its archived source: it did not allow neutral
drift and used absolute rather than baseline-relative tail fitness.

The search compares random replay, counterexample replay, and counterexamples
with tail-risk fitness. Each generation evaluates the incumbent and three
mutations on the same frozen archive snapshot. Each candidate costs 48 packer
executions: 24 fixed cases, 8 replay cases, and 8 new probes executed for both
candidate and best-fit. All instances contain 80 items, so item-step budgets match.
Reference initialization and the final audit are counted separately. Equal
evaluator work is not a claim of equal total computational cost.

Probe regressions become archive entries with executable input, observed excess
bins, reference count, family, generation, and identifier. A bounded archive
retains either random probes or the greatest historically observed regressions.
Final audit instances are generated after all search runs finish and never enter
the search archive. The framework is researcher-controlled, not a hardened
adversarial sandbox.

## Inspect experiments

Per-seed traces are compressed JSON. Summaries and audit results are plain JSON.
Each directory includes source snapshots; v2 snapshots have a note describing
post-run validation and logging changes. Seed 0 histories were reproduced exactly
for all three v2 arms. Bootstrap intervals measure variation across search seeds,
conditional on the shared final audit suite.

```python
from falsify.core import read_json
run = read_json("experiments/local-v2/counterexample_replay-0.json.gz")
print(run["weights"])
print(run["search_packing_executions"])
```

The Codex proposals and revisions are recorded in
`experiments/codex_candidates.json` and `experiments/codex_revision.json`.
The pilot greedily shrinks failing inputs within a bounded evaluator budget.
These are reduced counterexamples, not certified globally minimal examples.

Rebuild the report from the recorded results:

```sh
python3 -m falsify.report
```

## Optional Anthropic proposal adapter

An optional adapter requests one bounded, structured hypothesis and feature
vector. It follows the official [Messages API](https://platform.claude.com/docs/en/api/messages/create)
and [structured output](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
interfaces. Network execution has not been tested because no key was configured
during the local experiments. The model is configurable; access depends on your
account. Each request is capped at 1,024 output tokens and 12,000 prompt characters.
The adapter records actual token usage and does not execute model-written code.

Configure `ANTHROPIC_API_KEY` in `.env` locally; never paste it into chat or commit
it. `.env` is ignored by git. Then:

```sh
python3 -m falsify.anthropic_propose --prompt-file experiments/example_prompt.txt --model claude-sonnet-4-6 --out experiments/anthropic-proposal.json
```

This requests one proposal, not an autonomous ablation study. The next study
should compare no memory, prose summaries, and executable counterexample memory
under the same model, evaluation and token budgets, with a new held-out audit.

## Files

- `falsify/core.py`: instance generation, bounded mutations, evaluator interface.
- `falsify/packing.cpp`: fixed online packing and scoring implementation.
- `falsify/search.py`: repeated matched-budget experiments.
- `falsify/pilot.py`: model-authored candidate evaluation and failure reduction.
- `falsify/report.py`: standalone interactive report and written results.
- `falsify/anthropic_propose.py`: optional structured LLM proposal adapter.
- `tests/`: independent reference checks, packing validity, counterexample replay,
  matched budgets and deterministic reproduction.

The original hackathon brief, website text, and papers remain under `context/`.

## Next experiment: promotion gates and online context

`falsify/contextual.py` and `contextual.cpp` add eight features calculated from
past items in the current instance. The candidate has no future-item access.
`falsify/gated_search.py` gives all arms an identical proposal stream and compares
fixed-score-only promotion, a random-input gate, and a counterexample gate.
The generation trajectory is independent of gate decisions. Every arm incurs
the same packer-execution and item-step budgets, including evaluations that the
fixed-only arm ignores. This is another local mechanistic experiment, not an
autonomous LLM memory ablation.

```sh
python3 -m falsify.gated_search --seeds 40 --generations 400 --out experiments/my-gate-reproduction
```

The named experiment `experiments/gate-v3/` uses a new final audit of 1,600 cases
and a separate 160-case diagnostic suite to inspect gate rejections of sampled
proposals. See `experiments/PROTOCOL-v3.md` for the design and interpretation.

The completed gate experiment reduced mean excess bins from 0.014000 with
score-only promotion to 0.011828125 with counterexample gating. Its advantage
over a random gate was inconclusive. Counterexample gates rejected more
empirically harmful and more empirically beneficial proposals. No arm beat
best-fit overall. See `experiments/gate-v3/RESULTS.md` for intervals and limitations.

## Softer gates with fresh validation

`falsify/soft_gates.py` compares strict counterexample rejection with bounded
losses and bounded losses backed by fresh validation. The completed 40-seed
experiment preserved 15/16 empirically beneficial proposals and blocked 328/599
harmful proposals with validation, versus 14/16 and 270/599 with the strict gate.
Final performance was inconclusive; plain relaxation worsened performance.
See [V4 results](../experiments/soft-gate-v4/RESULTS.md) and
[protocol](../experiments/PROTOCOL-v4.md) for the limits of this evidence.

```sh
python3 -m falsify.soft_gates --seeds 40 --generations 200 --out experiments/my-soft-gate-reproduction
```
