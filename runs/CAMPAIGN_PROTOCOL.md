# Four-approach live campaign

Frozen before the first paid request, 3 October 2026. Scope: execute the four options in PLAN.md as small pilots, then report all outcomes, costs, failures and limits. Existing experiments are never modified. The protocol may only change through a dated amendment explaining why; earlier run evidence remains intact.

## Runs and allocation

| Order | Approach / run name | Problem | Proposal limit | API cap | Seed |
|---|---|---|---:|---:|---:|
| 1 | lean-bounded-live | 12-weight packing, strict gate, two-sided simplification | 12 | $2 | 7101 |
| 2 | lean-circle-live | Circle solver evolution, patience schedule | 18 | $3 | 7102 |
| 3 | lean-rich-live | Online priority code, patience schedule, strict gate | 18 | $4 | 7103 |
| 4 | full-rich-live | Ranked tiers, adaptive moves, validated loss allowance, code simplification | 6 batches of 3 | $6 | 7104 |
| 5 | full-circle-live | Same integrated architecture with strict geometry promotion | 6 batches of 3 | $4 | 7105 |
| 6 | full-rich-random-live | Random ranking control with the same tiers and adaptive moves | 6 batches of 3 | $3 | 7106 |

These caps sum to $22. The remaining $3 is contingency for documented service failures or an explicitly labelled follow-up; it is not permission to exceed the **$25 campaign ceiling**. A single append-only ledger reserves the maximum request charge before sending each generation request, then settles from provider token usage. An uncertain request retains its full reservation. No automatic retries. API credit does not enlarge the ceiling. Prices and raw usage are retained; amounts are token-based list-price costs, not a claim about the final invoice after credits.

Generation uses `gpt-6.1-sol`; full-stack tiers are `gpt-6-astra`, `gpt-6.1-sol`, `gpt-6-luna`, with a 15% randomized routing swap. Ranker is `gpt-6-luna`, explicitly substituting for Jev because the user configured OpenAI. This does **not** test the original TypeSafe ranker or Claude. Model availability and request compatibility must be verified; any provider substitution is documented before its run. Models use low reasoning effort, 2,048 output-token cap for weights/ideas/ranking, 6,000 for code, and a 6,000 input-token limit. Limits include reasoning tokens. Truncated outputs are paid failures, not silently retried.

## Frozen evaluation method

- Bounded: 24 fixed selection cases, 16 archived stress cases, 16 matched random stress cases, 64 fresh validation cases and 8 archive-discovery probes per step. Five development families; 1,600 fresh audit cases include three shifted families. A separate 1,000-case suite controls simplification; absolute mean bin-count change must be at most 0.002. Audit checks both original and simplified outputs and their placement agreement.
- Rich: six fixed cases, four archive cases, four random controls, six fresh validation cases, two probes per step. Half OR-style and half Weibull. OR development streams have 120 integer items in 20..100 at capacity 150; audit streams have 500. Weibull streams have 5,000 rounded/clipped samples, shape 3, scale 45, capacity 100. Fresh audit: 20 cases; simplification: six separate cases. Code can choose an unused bin early, preserving the published notebook interface.
- Circle: three fixed RNG seeds, two fresh validation seeds per step; five fresh audit seeds and three separate simplification seeds. Maximize radius sum for n=26. Every case must pass the existing independent strict geometry check. Each subprocess has a 30-second wall limit including imports; report solver seconds as well. Fresh seeds test stochastic stability on n=26, not generalization to other sizes or hidden geometry problems.
- All required cases must be valid. A failed required case prevents promotion. The explorer may retain valid rejected code for further proposals, but each deployment gate has its own incumbent. Strategist chooses the move **before** generating code. All three candidates in a full batch share the same captured parents; gates see the archive frozen at batch start.
- Packing gate controls (`score_only`, `random_strict`, `strict`, `validated_budget`) share one proposal stream and are charged equal logical evaluator work. Physical executions are cached and reported separately. These are conditional replays, not four independent searches. Baselines are best-fit and first-fit. Public OR3 (20 cases) and Weibull 5k (five cases), plus published FunSearch priorities, are evaluated only after each run freezes its candidate.
- Public results use the notebook's **L1** bound. Fresh generated audit and public benchmark results are separate. Mean differences weight cases equally; family-specific results must accompany the mixture because Weibull cases have far more items.
- Candidates, prompts, responses, model identities, parents, decisions, token usage, source snapshot/hashes and case files are saved. Record the terminal state even if no proposal succeeds. Raw model text is not evidence of correctness; only independent evaluations are.

## Controls and claims

The lean code runs and full runs each allow 18 candidate proposals, share evaluator definitions and per-candidate resource limits, and log actual spend. Dollar caps and protocol overhead differ, so this is not a matched-spend efficiency trial. The full random-ranker control holds the generation tiers, scheduler and proposal count fixed; it omits the cheap ranking call and uses an independent trajectory, so one result cannot establish a causal ranking advantage. Report both exact candidate counts and actual costs rather than imply identical expenditure.

Paired case bootstraps describe the frozen candidates on the specified data distributions, conditional on one search trajectory. They do not estimate variation across LLM searches. No record claim, state-of-the-art claim, or general scheduler/ranker superiority follows from these pilots. A local improvement over the provided circle seed is a legitimate result even if far below the repository's reference radius sum. Published FunSearch baselines beating best-fit are reproduced reference behavior, never attributed to our search.

Research efficiency claims require replicated, matched-dollar and matched-evaluator-budget trajectories; these pilots can provide measured costs and failure rates only. A useful negative result is that integration works but does not beat a strong baseline. Generic code simplification is one model proposal accepted only if smaller and quality-preserving on its own suite; audit remains independent. Better quality during simplification is classified as repair, not an explanation of the original algorithm.

## Reproduction

From the execution worktree, with dependencies from `requirements-research.txt` and a local ignored `.env` containing `OPENAI_API_KEY`:

```sh
python -m autoresearch.evidence_loop --problem bounded --steps 12 --seed 7101 --budget 2 --out runs/lean-bounded-live
python -m autoresearch.evidence_loop --problem circle --steps 18 --seed 7102 --budget 3 --out runs/lean-circle-live
python -m autoresearch.evidence_loop --problem rich --steps 18 --seed 7103 --budget 4 --out runs/lean-rich-live
python -m autoresearch.evidence_loop --problem rich --approach full --steps 6 --seed 7104 --budget 6 --out runs/full-rich-live
python -m autoresearch.evidence_loop --problem circle --approach full --steps 6 --seed 7105 --budget 4 --out runs/full-circle-live
python -m autoresearch.evidence_loop --problem rich --approach full --ranker random --steps 6 --seed 7106 --budget 3 --out runs/full-rich-random-live
```

Output directories must be fresh. Do not restart a partly completed run under the same name or erase its usage records. Add `--mock` and choose a different directory for a software check; mock mode reduces case counts and never calls a paid provider.

## Amendment 1 — initial network restriction

Before any paid request, sandbox networking blocked token counting in `lean-bounded-live`. Preserve that failed attempt. Network-enabled bounded execution uses `--seed 7201 --out runs/lean-bounded-live-network`, with the original 12-proposal/$2 limits. All subsequent live runs require the same approved network access. No model response or search result informed this change.

## Amendment 2 — confirmed rate-limit handling

After four completed bounded proposals and two circle proposals, HTTP 429 stopped those trajectories. Their frozen candidates and audits remain final; do not resume selection using those audits. Later runs use a shared 15-second minimum interval between all HTTP requests, including token counting. At most three 60-second retries are allowed **only** for HTTP 429 with machine-readable `rate_limit_exceeded`; these are explicit pre-execution rejections and keep the same outstanding reservation. Other failures stop the run and retain any uncertain reservation. Provider messages are never logged; only constrained error codes. Historical unresolved reservations remain conservatively charged against the cap.

The completed partial trajectories count as pilot evidence, with actual proposal counts reported. Any replacement uses a new seed and directory and counts toward the original approach's dollar allocation. A bookkeeping test also corrected per-run token totals, which had accidentally included other simultaneous runs; per-request usage and dollar settlements were correct. Historical summaries are preserved and corrected totals will be derived from the immutable ledger for the campaign report.

## Amendment 3 — requested throughput commit and quota-aware new configurations

The user requested commit `d0bbd8c` from `research/throughput-modal`, applied here as `1c4a882`, with `--api-scheduler headers --eval-workers 4` for all new runs and current runs kept intact. All earlier runs reached their own terminal states and frozen audits; no existing trajectory is resumed. The updated test suite passed 75 tests. New evaluators use four local workers (the inexpensive bounded packer remains effectively serial), and wall time is distinct from summed case time. This hardware/concurrency change can affect timeout behavior and is not an algorithmic improvement.

GPT-6.1 Sol's generation headers reported request limit 50, remaining 0, reset-to-full approximately 85,517 seconds, `Retry-After` 1,728 seconds, and a 10,000-token rate limit. Credits do not remove that request constraint. A minimal GPT-6 Sol diagnostic succeeded, reporting 49 remaining requests. Its cost, $0.000092, and the earlier $0.000082 diagnostic are included in the campaign ledger. Uncertain historical reservations remain charged to the ceiling. GPT-5.4 Mini availability is checked before its runs.

New lean runs use **GPT-6 Sol**. New full-stack runs use **GPT-5.4 Mini for idea generation and simplification**, with generation tiers **GPT-6 Astra / GPT-5.4 Mini / GPT-6 Luna**, and the original GPT-6 Luna ranker. Model identities are frozen in configuration and logged per call. These are new configurations, not exact replications of the previous provider mix. Code output allowance is 4,000 tokens, with the existing 6,000 input limit, fitting the observed 10,000-token request allowance; bounded weights, ideas and ranking retain 2,048 output tokens. Truncation is a paid failure, never silently repaired.

| New run | Seed | Proposals | API cap |
|---|---:|---:|---:|
| `lean-bounded-headers` | 7501 | 12 | $1.70 |
| `lean-circle-headers` | 7502 | 18 | $2.50 |
| `lean-rich-headers` | 7503 | 18 | $3.50 |
| `full-rich-headers` | 7504 | 6 × 3 | $5.50 |
| `full-circle-headers` | 7505 | 6 × 3 | $3.50 |
| `full-rich-random-headers` | 7506 | 6 × 3 | $2.50 |

These caps plus previous charges and reservations remain below the campaign ceiling. All use `--api-scheduler headers --eval-workers 4 --code-output-tokens 4000` and the original shared ledger. Every new run starts from its provided seed/best-fit. Previous audit results are not supplied as model feedback.

## Amendment 4 — common confirmation after all selection finishes

After the new runs finish, compare all frozen original and simplified gate incumbents on one common, previously ungenerated suite per problem: bounded 1,600 cases at seed **8902615**; rich 100 cases (50 OR-style/50 Weibull) at **8902715**; circle 10 seeds starting **8902815**. Use the same local four-worker/30-second evaluator, deduplicate identical programs, and freeze the complete input program set before generating cases. Include interrupted pilots as such. No confirmation result is supplied to a model or used for another search. This improves precision and gives a common case comparison of the frozen programs, while leaving the unequal search counts, model mixes and costs explicit. It is not a replicated causal test of the frameworks. Results go under `runs/confirmation/`, using `scripts/confirm_campaign.py`, with no paid calls.

## Amendment 5 — completing the lean circle trajectory

The header-scheduled GPT-6 Sol circle run stopped after five completed proposals when the request bucket became unavailable. Rate rejections also consume request allowance, so counting successful generations alone overestimated the remaining quota. Preserve that run's frozen audit and reservation. To execute a complete lean circle trajectory, run `lean-circle-astra` from the supplied seed with **GPT-6 Astra**, seed **7702**, **18 proposals**, **$5 run cap**, and `--api-scheduler headers --eval-workers 4 --code-output-tokens 4000`. This reallocates unused campaign funds; the **$25 total ceiling remains unchanged**. The new model makes this a distinct configuration, not an exact replication or a matched-model comparison with the full stack. Its audit will not feed further selection.
