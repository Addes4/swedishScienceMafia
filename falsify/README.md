# falsify: FunSearch's published bin-packing heuristics

`funsearch_heuristics.py` holds FunSearch's published Weibull and OR heuristics, verbatim, and the
ab-WorstFit rule. The headline bin-packing studies import it as reference code:
[online-frontier-v1](../experiments/online-frontier-v1/RESULTS.md),
[online-beyond-ss-v1](../experiments/online-beyond-ss-v1/RESULTS.md) and
[llm-from-ss-v1](../experiments/llm-from-ss-v1/RESULTS.md).

The package keeps its old name so that those studies' recorded code runs unchanged. It was first
**Falsify**, a counterexample-guided search that replays inputs where earlier candidates failed. That
search, its evaluators, the CPU tuning of bp-ceiling-v1 and the simplifier of simplify-v1 were removed
from `main` to keep the repository focused. They are in tag [`archive/full-research-2026-10-04`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04),
and the findings are summarised in the root README's
[How we chose the defaults](../README.md#how-we-chose-the-defaults).
