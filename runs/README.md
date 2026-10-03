# Example runs of `python -m autoresearch.loop`

Only the `demo-*` folders are committed; other runs are git-ignored. Each folder is exactly what
the command wrote. Open `report.md` first. No prompts or raw model responses are stored; the
model's own one-line description of each change is in `events.jsonl`.

| Folder | Command | LLM spend |
|---|---|---|
| [demo-binpacking](demo-binpacking/report.md) | `python -m autoresearch.loop problems/bin_packing_online --budget 0.15 --provider hf --max-iters 8 --gate-workers 8 --out runs/demo-binpacking` | $0.0038 of HF credit (8 calls, 8,158 input and 3,617 output tokens at $0.20 / $0.60 per million) |
| [demo-erdos-mock](demo-erdos-mock/report.md) | `python -m autoresearch.loop problems/erdos_squares --mock --out runs/demo-erdos-mock` | $0 (mock API) |

**What the live run found (3 October, started 23:49 BST, commit `0a98446`).** Nothing beat best fit.
In 8 steps DeepSeek-V4.1-Flash proposed 8 changes; 7 scored exactly 0.9616, the same as best fit
(they pack every item the same way), and one scored 0.3961. The run kept `initial.py` (public
0.9616, hidden 0.9604), below FunSearch's Weibull heuristic (0.9925 / 0.9928) and its OR heuristic
(0.9699 / 0.9702). The search took 43 s and the baselines 8 s; the explanation was skipped because
best fit is a single expression. This is consistent with [bp-ceiling-v1](../experiments/bp-ceiling-v1/RESULTS.md)
(beating best fit on Weibull 5k needs a new-bin option or FunSearch-style code, not a small edit) and
with the no-op proposals in [memory-ablation-v1](../experiments/memory-ablation-v1/RESULTS.md). It
is one seed of 8 steps: it shows the loop working end to end, not what the loop can reach.

The mock run replaces the model by a local stand-in that perturbs one constant per step, so its
steps say nothing about search quality; it shows the second benchmark and the full report with no
network.

## Live demo plan (1 minute 30)

1. **0:00–0:15, start a live run.** In a terminal at the repository root:

   ```bash
   python -m autoresearch.loop problems/bin_packing_online --budget 0.05 --provider hf --max-iters 3
   ```

   Say: one command, any problem folder, a hard dollar cap. Each step streams as it happens:
   the model's change, the gate's outcome and its cost (about $0.0004 a step).
2. **0:15–1:05, open the committed result** while the live run continues:
   [runs/demo-binpacking/report.md](demo-binpacking/report.md). Walk down it:
   - the score table: initial, final, FunSearch's two published heuristics, public and hidden;
   - the audit line: hidden instances are never used for selection, and `OVERFIT?` would flag a
     public gain that does not hold on them;
   - the step log with the cost of every call;
   - the explanation section: here it says "skipped", because the run kept best fit, a one-line
     program (step 3 shows it on a real program).
   Say: every default here won one of our controlled experiments; the others are flags.
3. **1:05–1:20, the explanation on a real program.** The demo run kept best fit, which has
   nothing to ablate, so show the same step on FunSearch's Weibull heuristic (about 7 s, no cost):

   ```bash
   python -m autoresearch.explain_code problems/bin_packing_online problems/bin_packing_online/baselines/funsearch_weibull.py
   ```

   It keeps `(bins - max_bin_cap) ** 2 / item`, the sign flip and the differencing step, and
   drops two terms (public 0.9925 → 0.9920). Mention the second benchmark:
   [demo-erdos-mock](demo-erdos-mock/report.md) is the same report on Erdős squares, made with
   `--mock` in about 4 s.
4. **1:20–1:30, back to the live terminal** for the 10-line summary, or point at it if it is
   still explaining.

If the network fails, run step 1 with `--mock` instead of `--budget 0.05 --provider hf`.
