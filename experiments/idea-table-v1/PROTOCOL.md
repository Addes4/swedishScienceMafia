# Idea table v1: protocol

Written on Saturday 3 October 2026, before any live API call for this study. Later changes
are listed at the end.

## Questions

1. Does ranking ideas before implementation predict which ideas improve the program? Rankers:
   Jev (TypeSafe), Claude Haiku 4.5 and Claude Opus 5.5 through `ClaudeRanker`, Codex, and a
   random control.
2. Which triage policy (which model implements which idea, or whether it is implemented at
   all) gives the best result per dollar?

Rather than run a full triage loop per policy, we build a counterfactual table: every idea is
implemented by every model and scored. Any policy that decides idea by idea can then be
replayed offline at zero API cost.

## Fixed setup

- **Problem and parent.** `problems/erdos_squares`, parent `problems/erdos_squares/initial.py`
  (public `combined_score` 0.8562, `hidden_mean` 0.9128). One round, one parent.
- **Ideas.** `claude-opus-5-5`, effort `medium`, `max_tokens` 16000, the unchanged
  `IDEA_SYSTEM`/`IDEA_USER` prompts (triage defaults). Eight calls asking for 10 ideas each. Call
  0 has history "(none yet)", as in triage round 1. Later calls list the ideas proposed so far
  as "- idea -> proposed, not yet tested", so the pool is not eight copies of the same list.
  This differs from triage, where the history carries outcomes. Lexical dedupe: an idea is
  dropped if its word-sequence similarity or word-set Jaccard with a kept idea is at least
  0.75. Kept ideas get a random presentation order (seed 20261003). The study uses the first N
  ideas in that order. If the pool needs to grow, new ideas are appended after the existing
  order and never reshuffle it.
- **Implementations.** Each of the N ideas by each of `claude-haiku-4-5` (default effort),
  `claude-sonnet-5-5` (effort `high`) and `claude-opus-5-5` (effort `high`). `max_tokens` 32000,
  unchanged `IMPLEMENT_SYSTEM`/`IMPLEMENT_USER`, triage's `Claude` client (including the
  server-side refusal fallback for Opus and Sonnet). These are triage's defaults. Up to six
  calls run in parallel. A cell that fails with an API error is retried, up to 3 attempts.
- **Scoring.** `autoresearch.gate.evaluate`, unchanged, run in Modal containers (1 physical
  core, 1 GiB, Python 3.12, numpy/scipy pinned to the local versions). The outcome is classified
  exactly as `triage.Run.implement` does: `rejected` (integrity), `invalid`, `improved` (public
  `combined_score` > parent + 1e-9), `not_better`; plus `no_code`, `refused`, `api_error`. Hidden
  instances (n = 18, 21, 23, 27) are never shown to any model or ranker. Their mean is recorded
  for every program and used only in the analysis. A program that budgets wall-clock time can
  score differently on other hardware, so 12 programs are evaluated twice to measure this.
- **Replicates.** 12 cells, 4 per model, with ideas drawn at random (seed 7) among the N, are
  implemented a second time with identical prompts and settings. This measures implementation
  noise.
- **Rankers.** They are blind to outcomes: they see only the problem statement, the parent
  program and score, an empty history and the ideas. They run after the probe and before the
  main implementation run. `rankings.json` is committed before the table is built.
  - `random`: `RandomRanker(seed=0)` is stored. In the analysis the random policies draw fresh
    keys in every bootstrap draw.
  - `claude-haiku-4-5`, `claude-opus-5-5`: `ClaudeRanker` unchanged (`max_tokens` 4000, default
    effort), one call per batch of 6 ideas (one triage round). The call is retried once if its
    JSON does not parse. If it fails again, ClaudeRanker's defaults stand and are reported.
  - `jev`: `JevRanker` unchanged, one call per idea.
  - `codex`: `codex exec` (model and effort from the local Codex config, recorded) in an empty
    scratch directory with a read-only sandbox and no API keys in its environment. One prompt
    holds all N ideas, with the same ranking prompt text as ClaudeRanker. Marginal cost $0
    (ChatGPT plan).
  - The sort key is `Ranking.key` from `autoresearch/rankers.py`
    (0.5 x expected promise + 0.5 x p_improve - 0.5 x p_repeat). `p_improve` is used for Brier.

## Budget and sizing (rule fixed now, N computed after the probe)

- Hard Anthropic cap $40 for the whole folder, enforced in code: each request reserves its
  worst-case cost before it is sent and is refused if that could exceed the cap. Every call is
  logged to `usage.jsonl`. Modal cap $5, enforced the same way per container.
- Order: ideas, then the probe (the first 3 ideas x 3 models, kept as table cells), then sizing,
  rankers, the main run, replicates and evaluation.
- Let c be the mean probe cost per idea (sum over the three models). N is the largest multiple
  of 6 with N <= pool size and spent_after_probe + $6 (rankers and contingency) + N x c + 4 x c
  <= $40.
- The main run has a soft stop: no new cell starts once spend reaches $40 - 4 x c - $1.
  Replicates run afterwards under the hard cap. Ideas that do not get all three cells are
  excluded from the analysis and listed.

## Endpoints

Primary:

- **P1, ranker validity.** Pooled AUC of each non-random ranker's key against `improved` over
  all N x 3 replicate-0 cells, with a 95% bootstrap interval over ideas. A ranker "predicts
  improvement" if the lower bound exceeds 0.5.
- **P2, value of the ranking for triage.** Paired difference in the number of improvements
  found over the pool between `tiers:R` and `tiers:random`. Both use the same model mix:
  thirds within batches of 6, favourites to Opus, middle to Sonnet, long shots to Haiku, no
  swaps. Ranking "adds value" if the 95% interval excludes 0 on the positive side.

There are up to four rankers and no multiplicity correction. All intervals are reported.

Secondary, descriptive:

- per-model AUCs; AUC for "at least one model improves"; Spearman correlation between the key
  and the mean public-score gain over the three models; Brier score of `p_improve`, against a
  base-rate predictor; success rate by ranker tier x model;
- the policy table: `uniform:{haiku,sonnet,opus}`, `tiers:R`, `tiers+swap:R` (15% random swaps,
  the triage default), `top{1,2,3}-opus:R` (rank, then Opus implements only the top k of each
  batch of 6), and `oracle-cheapest` as an unattainable reference. For each: dollars,
  improvements, improvements per dollar, dollars per improvement, expected best public score,
  the hidden mean of that best program, recall of all successes, and recall of Haiku's
  successes;
- budget-matched runs (batches of 6 until the budget is reached, checked before each batch as
  triage does) at 25% and 50% of the mean full-pool cost of `tiers:random`;
- disagreement between replicates and between repeated evaluations; sensitivity of P1 and P2
  when single-replicate labels are resampled at the observed disagreement rate.

## Analysis

`python -m autoresearch.policy_eval experiments/idea-table-v1`. 2,000 bootstrap resamples of
ideas (seed 0). In each draw, replicated cells contribute one of their two replicates at
random, batches of 6 are re-formed at random, and random keys are redrawn. Point estimates are
means over 500 draws without resampling. A policy's dollars include the ranker's cost per idea.
Idea generation costs the same for every policy and is reported separately. The best program
follows triage: the first strictly better improvement is kept.

## Limitations, stated in advance

One round and one parent program, with no feedback dynamics: the history, the outcomes seen
by later rounds and triage's promotion/refine step are not evaluated. Ideas come from one
proposer. N is limited by budget. One problem.

## Changes after this protocol

(none yet)
