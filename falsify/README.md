# falsify: bin-packing evaluators and CPU baselines

The bin-packing tools the kept studies run on:

| File | Role | Used by |
|---|---|---|
| `core.py`, `packing.cpp` | Fixed online packer for 80-item instances; candidates are weighted bin-scoring rules | [simplify-v1](../experiments/simplify-v1/EXPERIMENT.md), [bp-ceiling-v1](../experiments/bp-ceiling-v1/RESULTS.md) |
| `contextual.py`, `contextual.cpp` | Features of past items: the contextual rule space | bp-ceiling-v1 |
| `longpack.py`, `longpack.cpp` | Long-instance evaluator; reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly | bp-ceiling-v1 |
| `ceiling.py`, `ceiling_modal.py` | CPU tuning of linear and threshold rules, the fresh audit, the length sweep | bp-ceiling-v1 |
| `funsearch_heuristics.py` | FunSearch's published Weibull and OR heuristics | bp-ceiling-v1 |
| `optimum.py` | Exact offline optimum for small instances, as a headroom measure | bp-ceiling-v1 |
| `simplify.py` | One-sided greedy simplification of evolved rules | simplify-v1 |

The package is named after its first use: **Falsify**, a counterexample-guided search that replays
inputs where earlier candidates failed. Its studies showed less harmful drift but no gain over best
fit, and counterexample gates did not beat simple alternatives with LLM proposals. That code and those
studies were removed from `main`; they are in tag [`archive/full-research-2026-10-04`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04), and the
findings are summarised in the root README's
[How we chose the defaults](../README.md#how-we-chose-the-defaults). `simplify.py`'s inputs (the
first-round weight vectors) are in the tag too.

## Relation to FunSearch

FunSearch (Romera-Paredes et al., Nature 2024) evolved
online bin-packing heuristics that beat best-fit on the OR-Library and Weibull
benchmarks: for example 2.47% versus 4.94% excess bins over the L2 lower bound on
OR4, and 0.68% versus 3.98% on 5,000-item Weibull instances. Its heuristics take the
tightest bin only when the fit is very tight and otherwise leave room, close to the
`tight_or_roomy` idea Codex proposed here.

Our first-round setup differed from FunSearch's in ways that plausibly make best fit harder to beat:

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

## Run

```bash
python -m falsify.ceiling tune-ab --out experiments/my-ceiling   # CPU tuning (bp-ceiling-v1), about 15 minutes
python -m pytest tests/test_core.py tests/test_longpack.py tests/test_ceiling.py tests/test_simplify.py -q
```
