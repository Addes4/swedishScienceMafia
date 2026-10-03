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

All of these were made after the probe and before any ranker or main-run call. The probe
revealed the cost per idea and the outcomes of its 9 cells; 7 of the 9 improved.

1. **Pool extended from 80 to 120 ideas.** The sizing rule gave N = 78, capped by the 80-idea
   pool, while the budget allowed about 114 (c = $0.267 per idea). We ran 4 more Opus calls
   with the same prompts and settings (k = 10, history listing all earlier proposals). As
   pre-registered, the new ideas were appended after the existing order (positions 80+), and N
   was recomputed with the unchanged rule. The first 80 ideas were ordered once over the
   whole pool after generation (seed "20261003:0"); during generation, positions had been
   assigned call by call, and that was replaced before anything used the order.
2. **Each ranker sees each batch in its own random order** (seed derived from the ranker name
   and batch index; Codex gets the whole list shuffled). The position each idea was shown in is
   recorded in `rankings.json`. This was prompted by the team's literature review (position
   bias in LLM judges).
3. **Secondary analyses added.** These are every ranker's AUC minus the random ranker's AUC,
   with paired bootstrap intervals; an explicit implementation-noise section (replicate
   disagreement caps the AUC any ranker can reach and confounds success by tier); and the
   correlation between presentation position and ranker key, as a check.
4. **Ranking and the main implementation run were started at the same time** to save wall
   time, rather than one after the other. Blindness is unaffected: no program was evaluated
   until `rankings.json` was committed, so no outcome existed anywhere a ranker could see it.
   For the same reason, a second implementation process (6 more parallel calls) took ideas
   66-113 of the presentation order while the first worked through ideas 0-65. Prompts and
   settings are identical, and both processes enforce the same cap through the shared
   `usage.jsonl`.
5. **Tolerant parse of ClaudeRanker replies.** On the first ranking attempt, Haiku returned
   `"kind"` as a list and `ClaudeRanker`'s parser crashed (`TypeError: unhashable type: 'list'`
   in `autoresearch/rankers.py`). Nothing was saved. The rankers were rerun from the start
   with one change: if `ClaudeRanker.rank` raises, the same reply (already paid for) is parsed
   by `ideatable.parse_rankings`, which reads the same JSON fields but tolerates malformed
   ones. The count is recorded as `tolerant_parses` in `rankings.json`. The crashed attempt's
   calls are in `usage.jsonl` and count against the budget.

## Deviations during the run (recorded afterwards)

6. **Billing cutoff.** The experiment API key ran out of credit at $19.73 of logged spend,
   before the main run finished and before the replicates started. 146 of 342 design cells
   have no result. The analysis uses the 62 ideas with a result from all three models, so the
   pre-registered endpoints are computed on N = 62 rather than 114. Budget-matched levels are
   25% and 50% of `tiers:random`'s cost on those 62 ideas. Implementation noise is not
   measured. `python -m autoresearch.ideatable fill experiments/idea-table-v1` completes the
   design.
7. **Post-hoc analyses.** These were added after seeing outcomes and are labelled as post hoc
   in RESULTS.md:
   - AUC for "solved" (improved and matching the best known value on every public instance),
     added because the improved/not label saturated for Sonnet and Opus;
   - `inverse-tiers` (favourites to Haiku);
   - the missingness report.
