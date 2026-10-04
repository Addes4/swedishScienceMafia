# Four-approach execution log

## Authorization and scope — 3 October 2026

The user approved executing all four approaches, documenting methods and findings as work proceeds, with a **USD 25 total paid API ceiling**. This supersedes PLAN.md's stop-for-review and deferred-option choices; PLAN.md remains the original proposal. Worktree: `/private/tmp/ssm-all-approaches`, branch `research/all-approaches`, starting commit `3bb715a`. Existing `experiments/` evidence is immutable. New evidence goes in `runs/`.

The user has OpenAI credits and requested OpenAI API support. Use OpenAI for generation and model tiers. A cheap OpenAI ranker is an explicitly labelled substitute for Jev unless a TypeSafe key becomes available; results cannot establish Jev's performance. No credential value is read into the conversation or saved in evidence. Total calls are governed by one persistent campaign budget ledger, including unresolved reservations.

## Execution order and intended evidence

1. Bounded packing: 12 real sequential proposals, strict promotion, same-stream gate controls, separate simplification and fresh audit.
2. Circle packing: code evolution with fixed compute limits and an independent strict geometry check; compare against the supplied seed.
3. Rich online packing: unrestricted priority-function code with the published FunSearch input interface; generated training/validation, fresh generated audit, and frozen public OR3/Weibull reference datasets.
4. Combined stack: adaptive move selection, ranked model tiers, archive promotion for packing and independent geometry validation for circles, followed by measured simplification. Compare with a simpler schedule/ranker under matched caps where budget permits. Small runs are pilots, not confirmatory statistical studies.

All four must be attempted and their terminal status documented. Missing credentials/service access is a blocker, not a successful execution. Local mock runs are software verification, not LLM experiments.

## Method changes before execution

- The public FunSearch notebook uses **L1** volume bounds, whereas the paper reports L2. We will reproduce notebook results as L1 and label them; no relabelling as the paper's L2 table.
- Its priority function sees every feasible bin in a preallocated array, **including unopened bins**, and can elect to open one early. The richer adapter will preserve this behavior. The original bounded evaluator only opens a bin when nothing fits. These are different search interfaces.
- Official FunSearch source pinned at `cc53f274237d7ab05c19df939edbc1f9616a7c19`. Source: https://github.com/google-deepmind/funsearch. Data/code are extracted from the inspected notebook using AST literal parsing, without executing download cells. Attribution and source hashes accompany the extraction.
- Fresh Weibull instances use shape 3, scale 45, clipped/rounded to integers 1..100, capacity 100. OR-style generated instances use integers 20..100, capacity 150. Source: FunSearch paper Appendix E.4 (https://www.nature.com/articles/s41586-023-06924-6).

## Progress

- 18:28 UTC: execution approved; isolated branch/worktree created. No API keys were present in the project, planning worktree, home `.env`, or process environment. Requested local configuration.
- 18:34 UTC: isolated Python environment installed; public reference repository downloaded. No paid calls made.
- OpenAI key setup requested at `/private/tmp/ssm-all-approaches/.env`; implementation can proceed offline while configuration is pending.

## Results index

| Approach | State | Evidence |
|---|---|---|
| 1. Bounded packing | Four-proposal interrupted pilot audited; paced replacement running | `runs/lean-bounded-live-network/`, `runs/lean-bounded-paced/` |
| 2. Circle-first code search | Two-proposal interrupted pilot audited; paced replacement running | `runs/lean-circle-live/`, `runs/lean-circle-paced/` |
| 3. Rich packing | Two-proposal interrupted pilot audited; paced replacement running | `runs/lean-rich-live/`, `runs/lean-rich-paced/` |
| 4. Combined stack | Live packing, circle and random-ranking control running; OpenAI replaces Jev | `runs/full-rich-live/`, `runs/full-circle-live/`, `runs/full-rich-random-live/` |

Costs and numerical findings will be added from saved records, not estimates.

## Offline implementation checks — before paid calls

The shared loop now combines problem adapters, code/weight proposal, move selection, all-case validation, counterexample archive, conditional gate controls, separately checked simplification, fresh audits and a persistent token-cost ledger. This is an OpenAI-compatible integration of the existing mechanisms, not an execution of unchanged `autoresearch/triage.py`. The adaptive bridge updates cost forecasts from measured milli-dollar costs instead of leaving the original fixed cost proxies in place. API-independent unit/integration checks: **59 passed in 3.27 seconds**.

Mock runs exercised all three problem adapters and six full-stack batches (18 candidate attempts), including edit/rewrite/restart/crossover. These fixtures returned the supplied seed or deterministic weight perturbations and cost **$0**. They do not show that an LLM can improve anything. An initial bounded fixture exposed an identity issue: integer zero and floating-point zero hashed differently, allowing an unchanged rule to appear as a promotion. Parsed weights and the initial rule are now canonical floats, and a regression test covers negative zero. Original mock evidence remains preserved.

The richer evaluator independently validates full assignment vectors, capacities and bin counts. On the bundled public data, the **published** FunSearch heuristics used 4.55 fewer bins on average than best-fit on OR3 (19 wins, one tie, zero losses, 20 cases), and 65.6 fewer bins on Weibull 5k (five wins, five cases). Relative excess above mean L1 was 3.106% versus 5.368% for OR3, and 0.684% versus 3.984% for Weibull. These are reference-code reproductions on public data, not new discoveries or fresh-audit results. The mock candidate was best-fit and tied it exactly. Full numbers and provenance are in `runs/software-check-rich/summary.json` and `data/funsearch/provenance.json`.

The frozen live allocation, seeds, stopping rules, controls, limitations and reproduction commands are in [runs/CAMPAIGN_PROTOCOL.md](runs/CAMPAIGN_PROTOCOL.md). No live run has started. The key is requested only through local hidden Terminal entry, and `.env` is ignored by Git.

## Live execution begins

The user saved the OpenAI key locally. The implementation/protocol was committed as `cf02635` before the first API attempt. The first bounded run (`lean-bounded-live`, seed 7101) was blocked by sandbox networking during token counting: zero paid requests and $0 ledger cost. It is retained as a failed attempt, including its baseline-only audit. The network-enabled retry uses a fresh directory `lean-bounded-live-network` and seed **7201**; it retains the planned 12-proposal/$2 limits and the same campaign ledger. This avoids reusing the baseline-only audit stream from the failed attempt.

### First live trajectories — interrupted by HTTP 429

- Bounded: four evaluated proposals, zero deployed promotions. All four modified best-fit with small item-relative gap terms; fixed-score equality and/or stress regressions prevented promotion. Fresh audit of the deployed best-fit policy tied the reference on all 1,600 cases. Actual token usage: 3,641 input / 1,379 output; **$0.0223565**. One additional request has a conservative $0.03548 unresolved reservation. This is a negative four-proposal pilot, not completion of the planned 12-proposal trajectory.
- Circle: two evaluated proposals, two promotions. The second uses balanced staggered rows followed by SLSQP refinement with an analytic Jacobian and conservative radius shrinkage. Radius sum **2.602725380260877**, strictly valid on all five audit seeds; reference seed mean on those cases was approximately 0.961493. The generated algorithm is deterministic, so five repeated audit seeds do not represent five independent discoveries. It remains below the repository reference 2.6359830849176076. Actual tokens: 2,344 input / 2,544 output; **$0.030948**. One request has a $0.075 unresolved reservation.
- Rich: two evaluated proposals, no deployed promotion. Best-fit remained deployed and tied its reference on 20 fresh cases. Actual tokens: 831 input / 950 output; **$0.011162**. One request has a $0.075 unresolved reservation.

The HTTP 429 interruptions exposed the need for campaign-wide pacing. Amendment 2 adds it and allows narrowly limited retries for confirmed rate-limit errors. All 60 tests pass after that change. A per-run token aggregation error in early summaries was also fixed; the figures above were recomputed directly from the ledger, whose individual request usage and dollar charges were correct throughout. No uncertain charges were erased.

### Paced execution

`full-rich-live` (seed 7104, $6 cap) and `full-circle-live` (7105, $4) use the original planned protocols. The bounded replacement is `lean-bounded-paced`, seed **7301**, 12 proposals, **$1.90 cap**; together with its earlier actual charges and reservations it stays within the original $2 allocation. The shared request clock prevents concurrent runs from creating an API burst. Candidate compute and source snapshots remain independently recorded.

The rich replacement is `lean-rich-paced`, seed **7303**, 18 proposals, **$3.90 cap**; the circle replacement is `lean-circle-paced`, seed **7302**, 18 proposals, **$2.80 cap**. Including earlier charges/reservations, both remain within their original $4/$3 allocations. All replacements start from the provided seed/best-fit, not the previous audit-selected result.

### Development observation — first meaningful gate disagreement

At `full-rich-live` batch 2 (restart), GPT-6 Astra proposed candidate `ca787f7d…`: a table of residual-space values computed from the stated arrival distributions over a 24-arrival horizon, combining expected waste, closure probability and an opening charge. It does not see future items. On the six fixed development cases it improved mean bin count by 7.6667, and on the six fresh validation cases by 7.6667. One of four archive cases lost one bin. The strict archive gate rejected it; validated bounded loss, random strict and score-only accepted it. This is an observed difference in promotion decisions on the same candidate stream. **No fresh-audit claim is made at this point**; selection is still running. Candidate code, ranking, raw provider response and exact decisions are preserved in that run.

### Frozen audit results after the second service interruption

All six paced trajectories stopped when GPT-6.1 Sol requests were exhausted; their planned counts were not completed. Their audits are retained, not used to resume selection. `full-rich-live` evaluated nine candidates and froze the residual-value rule above: on 20 fresh cases it saved **8.0 bins per case** against best-fit, paired case-bootstrap interval **[-9.15, -6.95]**, 18 wins / 2 ties / 0 losses. OR-style savings were 2.1 bins/case and Weibull savings 13.9. The strict archive arm kept best-fit. This is one observed beneficial tolerance of an archived loss, not a general causal superiority claim for soft gates.

`lean-rich-paced` evaluated seven candidates and saved **6.3 bins/case** on its separate 20-case audit, interval **[-7.10, -5.60]**, 19 wins / 1 tie / 0 losses (OR: 2.0; Weibull: 10.6). These different seeds and proposal counts do not establish that the full stack outperforms the simpler loop. Both findings demonstrate fresh-data gains in the richer code interface; they do not contradict the original negative bounded-interface studies.

`lean-bounded-paced` evaluated ten proposals and retained best-fit. `lean-circle-paced` evaluated seven; `full-circle-live` evaluated six and reached selection radius sum 2.62156. Exact audit values and token costs are in the generated [findings index](runs/FINDINGS.md). The random-ranking control evaluated six candidates and retained best-fit. Generic code simplification was skipped by the original run logic after service interruption, so these partial full-stack runs do not yet establish a complete propose-to-simplify cycle.

### Requested throughput integration

Applied user-requested `d0bbd8c` as `1c4a882`. It does not alter `research_worker.py`; existing in-memory runs and their evidence were left intact. New runs use header scheduling and four local workers. The complete updated suite passed **75 tests in 5.62 seconds**. Header diagnostics identified the exhausted request bucket, and GPT-6 Sol availability was confirmed. Amendment 3 freezes the new model mix, output allowance, caps and seeds before those runs. The optional Modal backend was reviewed but is not used by this campaign.

### Completed new runs

- `lean-bounded-headers`: **completed all 12 proposals**, 21,961 input / 4,412 output tokens, **$0.0984885**. Best-fit remained deployed; 1,600 fresh audit ties and identical placements. The bounded representation did not improve this baseline in this live pilot.
- `full-rich-headers`: **completed all six batches / 18 proposals**, plus two code-simplification calls, 59,713 input / 15,933 output tokens, **$0.340938575**. All four requested move types were exercised and adaptive decisions followed warmup. The validated-gate winner saved **5.7 bins/case** on 20 fresh cases, interval **[-6.6, -4.8]**, 14 wins / 5 ties / 1 loss, with maximum observed loss one bin. OR-style savings: 0.6; Weibull savings: 10.8.

Both distinct frozen packing incumbents received smaller code proposals with unchanged bin counts and identical placements on the six-case simplification suite. The primary winner's simplification also preserved counts and placements on all 20 fresh audit cases. This is measured preservation on those cases, not an equivalence proof. Its rule combines tight-fit rewards, size-dependent residual-gap shaping and a charge for opening a new bin. On the public sets it saved 1.2 bins/case on OR3 and 10.8 on Weibull 5k, while the published FunSearch code saved 4.55 and 65.6 respectively. Our pilot does not beat that reference.

Timing note: `evaluation_seconds` sums per-case elapsed time, not CPU time. `physical_item_steps` counts items scheduled in physically invoked evaluations; for timed-out cases it is an upper bound on completed packing iterations. API costs and token counts are measured directly; no step-based speedup claim is made.

- `full-circle-headers`: **completed 18 proposals plus one simplification**, 85,122 input / 41,148 output tokens, **$1.10101795**. Frozen radius sum **2.6317301603535457**, strict validity on all five audit cases. The smaller program preserves the score on three simplification cases and all five audit cases. It uses successive linear-programming refinements with a trust region, active contact constraints, multistart initialization and explicit feasibility shrinkage. It has a seeded random generator and a 27-second internal deadline; compute-dependent stopping can affect reproduction on another machine. The repository reference remains higher at 2.6359830849176076.
- `lean-rich-headers`: **completed 18 proposals**, 30,726 input / 7,277 output tokens, **$0.1486235**. Fresh mean difference **-0.35 bins**, interval **[-0.80, +0.15]**, 8 wins / 9 ties / 3 losses. OR improves by 0.8 bins, while Weibull regresses by 0.1. This is inconclusive overall, unlike the earlier smaller pilot with a different model/seed; do not hide either result.
- `lean-circle-headers`: five completed proposals, then the rate coordinator deferred a request whose required wait exceeded five minutes. Cost **$0.07175**, plus **$0.055 reserved**. Its audit is frozen. Amendment 5 defines an 18-proposal Astra replacement from a fresh initial state, within the total campaign ceiling.
