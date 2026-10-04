# Protocol: Falsify loop with a real LLM on Weibull bin packing (llm-weibull-v1)

> **Archived protocol, never run.** Copied on 4 October 2026 from branch `plan-combined-framework`
> (`experiments/PROTOCOL-llm-v1.md`, kept as local tag `archive/plan-combined-framework`). No paid
> call was made under it. The closest completed study is
> [llm-long-search-v1](../../experiments/llm-long-search-v1/RESULTS.md).

Written and committed before any paid API call, 3 October 2026, about 22:30 BST. Plan:
[PLAN.md](combined-framework-plan.md). Changes after the first paid call are listed under "Deviations" at the
end, with times.

## Questions

1. **Run 1 (descriptive).** With Claude Sonnet 5.5 writing the code, does the loop produce a
   heuristic that uses fewer bins than best-fit on fresh Weibull instances, and what does that
   cost in measured tokens and dollars?
2. **Ablation (directional).** At the same dollar cap, how do three arms compare on a fresh
   audit: the full loop (counterexample gate plus witness feedback), score-only (promotion and
   feedback from training bins alone), and best-of-N (independent calls from best-fit, no
   feedback)? Three seeds per arm cannot establish a difference. Every seed is reported, and no
   significance claim is made.

## Fixed design

| Item | Value |
|---|---|
| Problem | `problems/binpacking_weibull`: online bin packing, capacity 100, items `floor(Weibull(3) × 45)` clipped to [1, 100], FunSearch's interface `priority(item, bins)` |
| Model | `claude-sonnet-5-5`, effort `medium`, `max_tokens` 16,000, server-side refusal fallback on (as in `autoresearch/claude.py`) |
| Calls and budget | 40 implementation calls per run, k = 4 per round, dollar cap $5 per run, enforced before each round from measured usage plus the worst case for the next round |
| Training inputs | 8 × 1,000 items, seed 1,000,000 + s |
| Archive | starts with 16 × 1,000 items (seed 2,000,000 + s); probes where a candidate lost to the incumbent are added, deduplicated, at most 64 kept, largest losses first |
| Per round | 16 archived inputs (seeded sample), 16 fresh validation inputs (seed 3,000,000 + 1,000s + round), 8 fresh probes (seed 4,000,000 + 1,000s + round), shared by the incumbent and every candidate |
| Witness pool | 40 × 120 items (seed 5,000,000 + s), greedy shrinking, at most 250 packings per witness |
| Promotion (full) | training mean strictly below the incumbent's, and `gate_decision('validated_budget', …, max_losses=5, max_loss=4, free_loss=2)` passes, with deltas against the incumbent |
| Promotion (score_only) | training mean strictly below the incumbent's |
| best_of_n | every call starts from best-fit with no history; at the end the champion is the valid program with the lowest training mean, if below best-fit |
| Moves | edit; after 3 rounds without a promotion, 2 rewrite + 2 edit; after 6, 2 restart + rewrite + edit; once 2 programs have been promoted and the loop has stalled for 2 rounds, the last slot is crossover |
| Run 1 | arm `full`, seed 0, output `experiments/llm-weibull-v1/full-s0/` |
| Ablation | arms `full`, `score_only`, `best_of_n` × seeds 1, 2, 3, output `experiments/llm-weibull-v1/<arm>-s<seed>/`, launched only if run 1 works. Total paid budget across everything: $60 |

### Gate calibration (development inputs, used once)

V4's loss limits (at most 2 losses, each at most 1 bin) were set on 80-item inputs. On 48
development inputs of 1,000 items (seed 777000, never reused), here are the per-instance bin
differences in each block of 16 inputs:

| Pair (a − b) | Mean | Losses per 16 | Max loss per 16 |
|---|---|---|---|
| FunSearch Weibull − best-fit | −4.44 | 1, 2, 1 | 1, 3, 3 |
| FunSearch OR − best-fit | −4.79 | 0, 0, 0 | −2, −2, −1 |
| first-fit − best-fit | +1.77 | 13, 14, 11 | 4, 5, 5 |
| best-fit − FunSearch Weibull | +4.44 | 14, 14, 15 | 12, 7, 9 |
| best-fit avoiding gaps under 6 − best-fit | +0.15 | 4, 7, 3 | 1, 2, 2 |
| FunSearch OR − FunSearch Weibull | −0.35 | 6, 6, 7 | 6, 4, 5 |

Chosen limits: at most 5 losses of 16, no single loss above 4 bins, total loss within 2 bins plus
the net gain on fresh validation inputs, and a mean validation delta of 0 or less. With these,
both published FunSearch heuristics pass against best-fit, and first-fit and the small regression
fail. A small, inconsistent gain (the last row) is rejected. This is deliberately conservative.

## Audit (generated only after every run has finished)

| Set | Size | Seed / source |
|---|---|---|
| Weibull 1k | 200 × 1,000 items | 9,100,000 |
| Weibull 5k | 50 × 5,000 items | 9,100,001 |
| Weibull 10k | 10 × 10,000 items | 9,100,002 |
| FunSearch Weibull 5k test set | 5 × 5,000 items | published (`data/funsearch_datasets.json`) |
| OR1–OR4 (out of distribution, capacity 150) | 4 × 20 instances | OR-Library files |

Policies audited: each run's champion (sandboxed), best-fit, first-fit, FunSearch's Weibull
heuristic and FunSearch's OR heuristic (published code). Reported for each set: mean bins, excess
over the L2 lower bound (%), and the paired difference against best-fit in bins per instance, with
a bootstrap 95% interval over instances (10,000 resamples, seed 739), plus wins, ties and losses.

**Primary outcome, run 1:** the champion's paired difference against best-fit on Weibull 1k.
Secondary outcomes: Weibull 5k and 10k, the FunSearch test set (directly comparable with
FunSearch's published 3.98% for best-fit and 0.68% for FunSearch), and out-of-distribution
results on OR.

## Explanation (after the audit)

- **Fingerprint:** the share of the champion's choices that are equivalent (same remaining space)
  to each reference heuristic's, measured along that reference's own trajectory. Uses 20 fresh
  1,000-item instances, seed 9,200,000.
- **Witnesses:** where the champion beats and loses to best-fit, from 40 × 120-item instances
  (seed 9,300,000), shrunk.
- **Simplification:** one LLM call asks for the shortest program with the same behaviour. It is
  accepted only if the mean-bin difference from the champion is within ±0.1 bins per instance
  (two-sided) on 100 × 1,000 items (seed 9,400,000), then confirmed on 100 × 1,000 items (seed
  9,500,000). Its cost is logged separately.

## What will be reported regardless of outcome

Every run, including failed and over-budget ones; all costs and token counts; and every
integrity and gate rejection. If the champion of run 1 is best-fit, the result is a null result
at the measured cost.

## Known limitations, stated in advance

- Claude Sonnet 5.5 has very likely seen the FunSearch paper and its heuristics. A champion close
  to FunSearch's (fingerprint) is a recall, not a discovery.
- One model and one budget. Training on 1,000-item instances only.
- The gate limits are a calibrated design choice. The evidence for counterexample gates comes
  from 80-item weight search (V3/V4), not from this setting.
- The harness isolates an honest loop; it is not a security sandbox.

## Deviations

(None yet.)
