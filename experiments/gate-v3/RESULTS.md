# V3 results: counterexamples as promotion gates

Counterexample gating reduced mean regression compared with score-only promotion, but the comparison with a random gate is inconclusive. No arm beat best-fit overall. Gates rejected more harmful sampled policies and also more empirically beneficial ones.

## Design

40 paired seeds, 400 generations, four common proposals per generation. All arms receive exactly the same proposal stream. Candidate-generation decisions use a fixed 24-case suite and are independent of gate decisions. A candidate can use 20 scoring features, including eight calculated solely from earlier items in the same instance. Each arm has 89,600 search packer executions per seed (7,168,000 item steps). Search totals 10,752,000 packer executions across the three arms. Shared reference initialization costs 40 executions per seed.

The final audit contains 1,600 fresh cases, 200 in each of eight families. A separate 160-case diagnostic suite evaluates 24 uniformly reservoir-sampled, non-control proposals per seed that were no worse than best-fit on the fixed search suite. No audit results enter candidate generation or promotion.

## Final deployed policies

| Arm | Mean excess bins over best-fit | Mean parameter-changing promotions | Mean gate rejections |
|---|---:|---:|---:|
| fixed_only | 0.014000000 | 185.40 | 0.00 |
| random_gate | 0.012859375 | 162.20 | 126.33 |
| counterexample_gate | 0.011828125 | 145.75 | 192.60 |

Lower is better; zero matches best-fit. Promotions count changes in weights, not necessarily distinct packing behaviour. Gate rejection counts concern non-control proposals meeting that arm's incumbent fixed-score threshold.

- Counterexample gate minus fixed_only: -0.002171875 bins; paired seed bootstrap 95% interval [-0.004109375, -0.000609375].
- Counterexample gate minus random_gate: -0.001031250 bins; paired seed bootstrap 95% interval [-0.002390625, 0.000046875].

The score-only comparison interval excludes zero. The random-gate comparison includes zero, so this study does not clearly establish an advantage of counterexamples over equally sized random gates. These intervals are conditional on the shared test set and quantify seed variability; the effect is small in absolute packing efficiency.

## What the gates reject

Classification is by mean excess bins on a separate finite diagnostic suite, not a statistical guarantee of true quality. Proposal samples may contain repeated or behaviourally equivalent policies.

| Diagnostic class | Sampled proposals | Rejected by random gate | Rejected by counterexample gate |
|---|---:|---:|---:|
| better | 62 | 13 (21.0%) | 25 (40.3%) |
| worse | 424 | 152 (35.8%) | 201 (47.4%) |
| tied | 474 | 34 (7.2%) | 52 (11.0%) |

Counterexample gating is more conservative in this sample. It filters more empirically worse proposals, but also blocks more empirically better proposals. A hard requirement to never lose to best-fit on any sampled archive input can obstruct average improvements that involve tradeoffs. Gates check 16 sampled archive entries at promotion time, rather than the entire archive. Existing incumbents are not automatically rolled back when later probes reveal a new failure.

## Per-family audit

| Family | Score only | Random gate | Counterexample gate |
|---|---:|---:|---:|
| uniform | 0.039500 | 0.036375 | 0.031500 |
| small | 0.014875 | 0.013000 | 0.010875 |
| large | 0.008500 | 0.008500 | 0.007250 |
| bimodal | 0.010250 | 0.009750 | 0.008250 |
| complementary | 0.004625 | 0.004250 | 0.005625 |
| near_thirds | -0.012375 | -0.011000 | -0.009875 |
| near_halves | 0.001000 | 0.001000 | 0.002375 |
| bands | 0.045625 | 0.041000 | 0.038625 |

Some shifted near-thirds cases improved, while regression on other families outweighed those gains. This is not an overall better-than-best-fit result. Changes to features, proposal generation and selection mean v3 cannot be compared with v2 as a causal test of contextual features alone.

## Verification and execution notes

- All 14 Falsify tests pass: six original checks and eight contextual/gate checks.
- Native contextual scoring matches an independently written Python specification on 20 random-weight cases.
- The original packer and the contextual packer agree when the eight new weights are zero.
- Prefix decisions are unchanged when future suffixes change.
- Prepared native evaluations match the public interface; capacity and item conservation hold under tested mutations.
- Test runs verify common proposals, deterministic histories, matched budgets, and zero sampled-gate violations for promoted candidates. The full 400-generation seed-0 history was also reproduced exactly after the audit fix.
- End-to-end CLI tests exercise both full audits and resumption from saved configuration.
- A full workspace test discovery observed a failing test in the separately developed strategist controller. Those files were not changed; the Falsify tests were subsequently run by explicit file pattern.
- The first audit failed in per-family aggregation because the mean helper assumed a list and was given a generator. All search runs had already completed. Iterable handling was fixed and the original audit resumed from saved traces. No proposal or selection logic changed. Search and resumed-audit source snapshots are saved separately.
- The failed audit incurred 3,200 discarded executions (1,600 reference and 1,600 first-candidate executions). These are documented in execution_note.json, separate from the matched search budget.

## Recommendation

Post-run code review identified an archive deduplication limitation: when several
proposals shared a probe input, the last proposal could overwrite a larger
within-generation regression. Historical archive maxima were preserved, but
not every current-batch maximum. These results describe that saved
implementation. The V4 soft-gate study corrects this before running and applies
the correction equally to all its arms.

Keep executable counterexamples as evidence, but use them to characterize the conditions under which an idea fails. A rigid no-regression gate is useful for protection and can also prevent discovery. The next model-driven study should compare no memory, prose evidence and executable evidence on the same proposal task and token budget. A softer, condition-aware promotion rule should weigh fixed-suite benefit against the frequency and severity of independently checked regressions.

## Reproduce

```sh
python3 -m falsify.gated_search --seeds 40 --generations 400 --out experiments/my-gate-reproduction
```

If all search traces finished but an audit was interrupted, resume with the original saved configuration:

```sh
python3 -m falsify.gated_search --out experiments/my-gate-reproduction --resume-audit
```

Use a new output directory for a fresh experiment. The source protocol is [PROTOCOL.md](PROTOCOL.md). summary.json, audit.json, diagnostic.json and seed-*.json.gz contain the full evidence.
