# Problems

Each folder is one research problem. The framework knows nothing about any of them: adding a
problem means adding a folder, with no changes to `autoresearch/`.

| Folder | Area | Source | Best known |
|---|---|---|---|
| `circle_packing` | geometry | problem 36 | 2.6359830849 (AlphaEvolve construction, n = 26) |
| `erdos_squares` | geometry | problem 55 | k + c/k for n = k² + 2c + 1 (exact, every n) |
| `erdos_discrepancy` | number theory / combinatorics | problem 40 | 1160 (the maximum for C = 2) |
| `sum_difference` | additive combinatorics | problem 43 | 1.2715 (asymptotic; AlphaEvolve unaided ≈ 1.21); the gate's reference adds the 0.01 maximum size bonus |
| `bin_packing_online` | online algorithms | FunSearch (Nature 2024) Weibull 5k | score = L2 bound / bins; best fit 0.962, FunSearch heuristic 0.993 (no record flag) |
| `bin_packing_online_informed` | online algorithms | Same instances and scoring as `bin_packing_online`; `problem.md` also spells out what the function can know (item count, every open bin, past sizes) without naming an algorithm. Used by experiments/llm-informed-v1 | as above; baselines add Sum-of-Squares 0.994 and FWSS 0.999 (experiments/online-beyond-ss-v1) |

Problem numbers refer to the repository accompanying Georgiev, Gómez-Serrano, Tao and Wagner,
*Mathematical exploration and discovery at scale* (2025),
github.com/google-deepmind/alphaevolve_repository_of_problems. Scoring follows the official
notebooks; deliberate differences are documented at the top of each `verify.py`.

## The contract

```
problems/<name>/
  problem.md    task description used as the LLM's system prompt (no hidden instances, no answers)
  initial.py    seed program; the evolvable part sits between EVOLVE-BLOCK-START / EVOLVE-BLOCK-END
  evaluate.py   ShinkaEvolve entry point (identical in every folder; calls autoresearch.gate)
  verify.py     scoring and integrity checks; never shown to the LLM
  baselines/    optional: *.py candidate programs that `autoresearch.loop` scores on the same
                instances and reports next to the search result (never shown to the LLM)
```

`verify.py` defines (all scores higher-is-better):

```python
FUNCTION = "solve"                      # the candidate defines solve(**instance)
PUBLIC = [{"n": 5}, ...]                # instances whose results the LLM sees
HIDDEN = [{"n": 21}, ...]               # instances it never sees (overfitting check)
TIMEOUT_S = 60                          # per instance
def check(construction, instance) -> {"valid": bool, "score": float, "reason": str}
def best_known(instance) -> float | None
def check_strict(construction, instance) -> bool    # optional independent re-check
def label(instance) -> str                          # optional
```

**Online problems.** If `verify.py` also defines `DRIVER` (trusted source that runs in the child and
calls the candidate once per input) and `online(instance) -> (header, inputs)`, the gate reveals the
inputs one at a time over a private pipe and sends input k+1 only after reading the decision for
input k. Future inputs never exist in the candidate's process, so it cannot look ahead or reorder;
`check()` receives the list of decisions. `bin_packing_online` uses this: the candidate writes
FunSearch's `priority(item, bins)` and the driver applies it per arriving item.

## What the gate does (`autoresearch/gate.py`)

1. **Static checks**: rejects programs that touch files, processes, the network, imports
   machinery or the evaluator.
2. **Separate process**: runs `solve` for every instance in a child process with API keys
   stripped; only the returned construction comes back. The candidate cannot reach `verify.py`.
3. **Scoring**: `check()` per instance; `combined_score` = mean of score / best known over the
   public instances.
4. **Beats the record?** Any score above the best known value triggers `check_strict()`, an
   independent re-check at 1e-12 tolerance. Failing it means an exploit (e.g. hiding overlaps
   inside the 1e-9 tolerance): score 0, quarantined. Passing it flags a possible discovery
   for human review.
5. **Feedback**: the LLM sees per-instance scores and ordinary errors ("squares 3 and 7
   overlap"), but integrity rejections only ever say "rejected by the integrity gate".
   Reasons, hidden-instance scores and flags go to `integrity.json` and the private metrics.

## Usage

```bash
pip install -r requirements.txt
python -m autoresearch.loop problems/erdos_squares --mock            # the whole loop, no network, no cost
python -m autoresearch.check --all                                   # score every initial.py, no LLM
python -m autoresearch.check problems/erdos_squares my_program.py     # score any program
python -m pytest tests/ -q                                            # integrity gate tests
export ANTHROPIC_API_KEY=...
python -m autoresearch.run problems/erdos_squares --generations 50    # ShinkaEvolve baseline
```

`autoresearch/shinka_compat.py` patches shinka-evolve 0.0.7 so it can call Claude Opus 5.5 /
Sonnet 5.5 / Opus 4.8 (it otherwise sends `temperature` and thinking budgets these models
reject, and does not know their prices).

Credits: ShinkaEvolve (Sakana AI, Apache-2.0); problem statements, scoring rules and the n = 26
circle construction from the AlphaEvolve problem repository (Apache-2.0 / CC-BY 4.0).
`problems/bin_packing_online/baselines/` holds FunSearch's published OR and Weibull heuristics,
verbatim from github.com/google-deepmind/funsearch (Copyright 2023 DeepMind Technologies Limited,
Apache-2.0); best fit is `initial.py`.
