# overfit-gates-v1: protocol (written before any scoring)

Written at 01:48 BST on 4 October 2026, before any program in this study was scored. The
repository cannot take a commit for a timestamp yet, so `RUN_LOG.md` records this file's SHA-256
and the time before the first scoring command.

## Questions

1. **Selection overfitting.** When a closed LLM loop promotes on a small public suite, how much of
   the promoted program's measured advantage over best fit disappears on fresh instances? How does
   the gap grow with the number of proposals seen, and how does it compare with the
   best-of-K prediction σ·√(2 ln K / n)?
2. **Promotion rules.** If the same proposal streams are replayed through other promotion rules,
   how many false acceptances and false rejections does each make, judged against fresh
   instances? What final fresh score and what extra evaluation cost does each reach?

## Data (no new LLM calls)

- **Proposal streams:**
  - source: [memory-ablation-v1](../memory-ablation-v1/RESULTS.md) confirmatory, `confirmatory/runs/*.json.gz`;
  - 30 runs (arms none, prose and executable × seeds 0–9) × 30 Claude Haiku 4.5 calls;
  - 879 valid proposals, 780 distinct code texts.
- **Public suite:** each run promoted score-only on its 5 fixed Weibull instances of 5,000 items
  (`fixed_specs`). The saved records hold every proposal's code, its fixed-suite bins and its
  packing hashes.
- **The pilot is excluded.** `memory-ablation-v1/pilot` searched a different regime: 20 weights on
  80-item synthetic instances, not code on Weibull 5k.

## Instances

- **Fresh pool:** 40 Weibull 5k instances. They come from the generator the memory study used,
  `falsify.longpack.weibull_items(seed, 5000, namespace)`, with the new namespace
  `overfit-gates-v1/fresh` and seeds 0–39. The salted namespace makes them distinct from every
  instance any earlier study used.
- **Seed reservation.** Neither the pool nor the random-veto inputs use
  `problems/bin_packing_online/verify.items_for`. That is a different generator with a different
  salt, so they cannot collide with:
  - its seeds 81000–83999, reserved by online-frontier-v1;
  - its seeds 50000–53003 and 60000–62001, used by the research-directions probe.
- **Splits, fixed now:**
  - **A (truth):** seeds 0–23 (24 instances). Used only to judge outcomes; never by a gate.
  - **B (Thresholdout holdout):** seeds 24–35 (12 instances).
  - **C (soft-gate validation):** seeds 36–39 (4 instances).
- **Random-veto inputs:** `weibull_items(k, L, 'overfit-gates-v1/random-veto')`, with the same
  lengths L as the archived counterexamples they replace.

## Scoring

- **Same evaluator as the memory study:** `falsify.code_eval.pack_shard`. That is the integrity
  gate's `run_online`: a fresh process per instance, items revealed one at a time, FunSearch's
  evaluator semantics, the static screen and a 30 s timeout. Short archive inputs use
  `falsify.code_eval.PersistentPacker`, as the study's mining did.
- **Positive control 1:** re-score at least 5 programs, including at least 2 promoted ones, on
  their run's own `fixed_specs`. Every saved `fixed.bins` must reproduce exactly before the pool is
  scored. If one does not, stop and investigate.
- **Deduplication (disclosed).**
  - Programs are grouped by the tuple of their 5 saved fixed-suite packing hashes, and one
    representative per group (the first in run/call order) is scored on the pool.
  - Check: for up to 20 groups that contain at least 2 distinct code texts, a second member is
    scored on pool seeds 0–3. Report how many agree on every bin count and packing hash.
- **Errors and timeouts:** a timeout or error on a pool instance is retried once with a 60 s
  timeout because the machine is shared. A program that still fails is counted as failing on that
  instance and is never promoted by any gate. Report how many there are.
- Best fit is computed natively (`falsify.longpack`).

## Analyses

### 1. Selection overfitting, as run

- **Per promotion:** the gap is fixed-suite advantage over best fit minus pool-A advantage over
  best fit, in bins per instance. Report the mean gap with a bootstrap interval (resampling runs),
  and the gap against the call index at which the promotion happened.
- **Per run:** the final incumbent's fixed-suite advantage against its pool-A advantage.

### 2. Selection overfitting, offline

- Use the per-instance bins of every group representative on all 40 pool instances.
- For each run, K ∈ {1, 2, 5, 10, 20, 30} (the first K valid proposals) and public size
  n ∈ {1, 2, 5, 10}:
  1. draw 500 public subsets of size n from the 40 instances;
  2. pick the proposal with the best public mean;
  3. record its public advantage over best fit minus its advantage on the remaining 40 − n
     instances.
- Average over draws and runs, and compare with σ·√(2 ln K / n), where σ is the pooled SD across
  instances of the per-instance difference from best fit among the run's distinct proposals.
- This offline re-selection measures **selection** overfitting only. The proposals were generated
  adaptively from feedback on the original fixed suite, not on these draws.

### 3. Gate replay (open loop)

- Each run's proposals are replayed in call order. Each gate keeps its own incumbent, which starts
  at best fit. A replay cannot change later proposals, unlike a live loop where blocking a
  candidate changes what the model sees next. That is disclosed in the results.
- Notation: Δ is the per-instance difference in bins, candidate minus incumbent, on the 5 fixed
  instances. Gates:
  - **G0 score-only:** sum Δ < 0. This is the rule as run. Positive control 2: G0 must reproduce
    the 17 as-run promotions exactly.
  - **G1 sign test:** one-sided exact sign test over non-tied fixed instances at α = 0.05. With 5
    instances this means 5 wins and 0 losses.
  - **G2 Ladder, parameter-free form (Blum & Hardt 2015):** −mean Δ > sd(Δ)/√5. If sd(Δ) = 0, any
    mean Δ < 0 counts.
  - **G3 Thresholdout (Dwork et al. 2015):** the training estimate is mean Δ on the fixed suite;
    the holdout estimate is mean Δ on split B.
    - Threshold T = 2 bins/instance, noise scale σ = 0.5 bins/instance, budget 30.
    - Draw γ ~ Lap(2σ). For each query, draw η ~ Lap(4σ). If |train − holdout| > T + γ + η,
      answer holdout + Lap(σ), spend one unit of budget and redraw γ; otherwise answer train.
    - Promote iff the answer < 0. When the budget is spent, stop promoting.
    - RNG seed: 20261004 + run index.
    - Secondary sensitivity: T ∈ {1, 4}.
  - **G4 strict archive veto:** G0, and the candidate uses no more bins than the incumbent on
    every archived input. The archive holds the counterexample inputs mined in earlier calls of
    the same run, from the incumbent and best-fit mining lists, with duplicates removed.
  - **G5 size-matched random veto:** as G4, but each archived input is replaced by a random input
    of the same length.
  - **G6 bounded-loss soft gate:** G0; at most 2 archived inputs regress, each by exactly 1 bin;
    and the candidate's mean bins on split C are no worse than the incumbent's.
- **Truth:** a proposal is *truly better* than the gate's current incumbent iff its mean bins on
  split A are lower. It is *materially better* iff they are lower by at least 0.5 bins per
  instance.
  - A false acceptance is a promoted proposal that is not truly better.
  - A false rejection is a proposal that is truly better but not promoted.
  - Both rates are reported among valid proposals, and also with the material threshold.
- **Outcomes per gate:**
  - promotions;
  - false acceptances and false rejections;
  - the final incumbent's split-A mean bins minus best fit;
  - extra evaluation cost beyond the fixed suite, as items packed: holdout or validation instances
    × 5,000, plus archive or random-input items.

### Statistics

- Intervals: paired bootstrap over the 30 runs, 10,000 resamples, seed 4242.
- **Primary contrast:** G2 (Ladder) minus G0 on final split-A bins. Holm correction across the six
  contrasts Gk − G0, k = 1–6, on final split-A bins.
- **Secondary:** false-rejection rates G4 vs G5 (the question gate-v3 left open), G3's sensitivity
  to T, and the analysis 2 curves.
- Everything else is descriptive.

## Threats to validity

- **Open loop:** see §3.
- **Archive mined from the as-run trajectory:** the archive was mined against the as-run
  incumbent, not each gate's own incumbent.
- **Small fresh pool:** split A has 24 instances, so "truly better" is noisy for differences below
  about 1 bin per instance. The material threshold is reported for that reason.
- **Correlated proposals:** many proposals are behaviourally identical, so the effective K is
  smaller than K.
- **Dedup by fixed-suite behaviour:** checked as described under Scoring.
- **Thresholdout parameters** were set by hand and not tuned; the sensitivity is reported.

## Compute and cost

- No API or Modal calls.
- CPU on the shared machine: at most 2 worker processes while the 1-minute load average exceeds 6.
- Expected cost: about 206 groups × 40 instances × about 1 s of CPU.
