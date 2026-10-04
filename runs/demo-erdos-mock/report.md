# Research loop report: erdos_squares

| | |
|---|---|
| problem | `erdos_squares` |
| search | lean, 12 steps max |
| keep rule | better public score and no regression on archived instances (gate) |
| model | `deepseek-ai/DeepSeek-V4.1-Flash:deepinfra` via hf (mock API) |
| spend | $0 real (mock API; $0.0241 simulated at listed prices), 12 calls, 47,381 tokens |
| wall time | search 3 s, baselines 0 s, explain 0 s |
| stopped | max_iters (stopped_early) |
| evaluations | 13 (10 valid), 0 improvements accepted |

## Scores

Public instances are the ones the loop sees and selects on. Hidden instances are never shown to the model and never used for any decision; they are the fresh audit.

| program | public | hidden | note |
|---|---|---|---|
| `initial.py` (starting program) | 0.8562 | 0.9128 | |
| `best_program.py` (final incumbent) | 0.8562 | 0.9128 |  |
| minimal program (ablation) | 0.8562 | 0.9128 | 0 parts removed |

Audit: public 0.8562 → 0.8562 (+0.0000), hidden 0.9128 → 0.9128 (+0.0000); public − hidden gap of the final program -0.0566.

## Steps

| step | op | outcome | score | best | cost | change (model's own description) |
|---|---|---|---|---|---|---|
| 1 | edit | not_better | 0.8562 | 0.8562 | $0.0018 | Mock change: retune one constant of the construction. |
| 2 | edit | not_better | 0.8562 | 0.8562 | $0.0026 | Mock change: retune one constant of the construction. |
| 3 | edit | not_better | 0.8562 | 0.8562 | $0.0020 | Mock change: retune one constant of the construction. |
| 4 | edit | not_better | 0.8562 | 0.8562 | $0.0027 | Mock change: retune one constant of the construction. |
| 5 | edit | invalid | 0.0000 | 0.8562 | $0.0009 | Mock change: retune one constant of the construction. |
| 6 | edit | invalid | 0.0000 | 0.8562 | $0.0021 | Mock change: retune one constant of the construction. |
| 7 | edit | not_better | 0.8562 | 0.8562 | $0.0024 | Mock change: retune one constant of the construction. |
| 8 | edit | not_better | 0.7984 | 0.8562 | $0.0010 | Mock change: retune one constant of the construction. |
| 9 | edit | invalid | 0.0000 | 0.8562 | $0.0023 | Mock change: retune one constant of the construction. |
| 10 | edit | not_better | 0.8562 | 0.8562 | $0.0022 | Mock change: retune one constant of the construction. |
| 11 | edit | not_better | 0.8562 | 0.8562 | $0.0020 | Mock change: retune one constant of the construction. |
| 12 | edit | not_better | 0.8562 | 0.8562 | $0.0021 | Mock change: retune one constant of the construction. |

## Change: `initial.py` → `best_program.py`

The run kept the starting program: no candidate was accepted.

## Explanation

Two-sided ablation of `solve` (4 parts, 5 evaluations, tolerance ±0.002 on the public score). A part "can go" only if removing it leaves the public score within the tolerance on both sides, so the explanation describes the program actually found, not a repaired one.

**Parts that matter** (largest effect first; Δ = public score without the part minus with it):

| line | part | Δ public | verdict |
|---|---|---|---|
| 9 | `k = math.isqrt(n)` | -0.8562 | essential: the program fails or turns invalid without it |
| 10 | `side = 1.0 / k` | -0.8562 | essential: the program fails or turns invalid without it |
| 11 | `squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in r...` | -0.8562 | essential: the program fails or turns invalid without it |
| 12 | `squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))` | -0.8562 | essential: the program fails or turns invalid without it |

| program | public | hidden |
|---|---|---|
| found (normalised source) | 0.8562 | 0.9128 |
| minimal (0 parts removed) | 0.8562 | 0.9128 |

Minimal program:

```python
"""Baseline: the largest k x k grid that fits, plus size-zero squares for the rest."""
import math

def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
```

## Reproduce

```bash
python -m autoresearch.loop problems/erdos_squares --mock --provider hf --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra --max-iters 12 --seed 0
python -m autoresearch.loop --report runs/demo-erdos-mock   # rebuild this report
```

Mock runs repeat exactly for a given seed.

Git commit `5fe95f807c86ac10ffb1aaaf28bb2f20ada4b87d`, Python 3.12.14. SHA-256 of the files that define this run (all 41 in `job.json`):

- `tournament/lean.py` `a00ce92e3d13d5e8`
- `autoresearch/gate.py` `bda3a654acee26b8`
- `autoresearch/sandbox.py` `9d0cc7a8b8fcab10`
- `problems/erdos_squares/evaluate.py` `0ac9a4a253a299d2`
- `problems/erdos_squares/initial.py` `5ca1aa946ee89389`
- `problems/erdos_squares/problem.md` `5a647d5e5fb3ab37`
- `problems/erdos_squares/verify.py` `4c137c8e586b09d7`

Files: `events.jsonl` (steps), `evals.jsonl` (every evaluation, with hidden scores), `usage.jsonl` (every LLM call and its cost), `summary.json`, `baselines.json`, `explain.json`, `artifacts.tar.gz` (every candidate program).
