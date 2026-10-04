# Research loop report: bin_packing_online

| | |
|---|---|
| problem | `bin_packing_online` |
| search | lean, 8 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf |
| spend | $0.0038 of a $0.15 hard cap, 8 calls, 11,775 tokens |
| wall time | search 43 s, baselines 8 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 9 (9 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.9616 | 0.9604 | |
| `best_program.py` (final incumbent) | 0.9616 | 0.9604 |  |
| baseline `funsearch_or` | 0.9699 | 0.9702 | `problems/bin_packing_online/baselines/funsearch_or.py` |
| baseline `funsearch_weibull` | 0.9925 | 0.9928 | `problems/bin_packing_online/baselines/funsearch_weibull.py` |

Audit: public 0.9616 → 0.9616 (+0.0000), hidden 0.9604 → 0.9604 (+0.0000); public − hidden gap of the final program 0.0012.

Against the baselines: the final program's public score is below the best baseline (`funsearch_weibull`, 0.9925). Any gain should be stated against these numbers.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Add a "reserve" idea via score shaping: prefer bins that leave a remainder far from 0 (to avoid w... |
| 2 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a hybrid: prefer exact/very-tight fits, but among loose bins prefer th... |
| 3 | edit | not_better | 0.3961 | 0.9616 | $0.0004 | Implement a "harmonic" style scoring that strongly prefers bins where the leftover after placing ... |
| 4 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a blended rule: for each bin compute the best-fit leftover, but add a ... |
| 5 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | I'll implement a capacity-threshold caped best-fit variant: use best-fit (tightest remaining capa... |
| 6 | edit | not_better | 0.9616 | 0.9616 | $0.0005 | I'll replace best-fit with a scaled score that combines tight fit with a mild preference for full... |
| 7 | edit | not_better | 0.9616 | 0.9616 | $0.0009 | Replace pure best-fit with a hybrid rule: primarily choose the tightest fit, but strongly prefer ... |
| 8 | edit | not_better | 0.9616 | 0.9616 | $0.0004 | Replace pure best-fit with a bounded best-fit that also avoids leaving tiny unusable remainders: ... |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Skipped: priority has nothing to remove (a single return without a +/- chain).

## Reproduce

```bash
python -m autoresearch.loop problems/bin_packing_online --budget 0.15 --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 8 --seed 0
python -m autoresearch.loop --report runs/demo-binpacking   # rebuild this report
```

Live runs are not deterministic (the model samples); mock runs are.

Git commit `0a98446f63f7f5014c7793360403c54baf833c3b`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/bin_packing_online/evaluate.py` `0ac9a4a253a299d2`
- `problems/bin_packing_online/initial.py` `609927c5ea619a94`
- `problems/bin_packing_online/problem.md` `aa1aa4a2d6d00d6a`
- `problems/bin_packing_online/verify.py` `b3ea67a1c6f94885`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
