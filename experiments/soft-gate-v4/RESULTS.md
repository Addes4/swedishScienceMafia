# V4: preserve promising proposals with bounded losses and fresh validation

The validation-backed gate offers an encouraging proposal-level tradeoff, but did not improve final packing performance over the strict gate. Relaxing the gate without validation worsened final results.

## Design

Completed 40 paired seeds × 200 generations, using identical proposals across three arms. All arms incurred the same evaluation budget. Rules were fixed before the audit; see [the protocol](../PROTOCOL-v4.md). This reuses the first 200 generations of V3's proposal trajectory, so it is not an independent search replication. Audit inputs are fresh.

- **Strict:** reject any observed stress-case regression against best-fit.
- **Loss budget:** allow at most two one-bin regressions, with a total loss allowance of one bin plus measured training gains.
- **Validated budget:** retain those severity/frequency caps, require nonpositive mean excess on 64 fresh validation cases, and use validation gains to pay for a second stress-case loss.

All arms also require training performance at least as good as their incumbent. One isolated stress loss may pass with neutral validation. Gates screen proposals; they do not roll back incumbents automatically.

## Independent proposal diagnostic

960 sampled proposals were evaluated on a separate 800-case suite. “Beneficial” and “harmful” describe their average performance relative to best-fit on that suite, not guaranteed behavior on every possible input. Counts include repeated or equivalent proposals.

| Gate | Beneficial proposals allowed (16 total) | Harmful proposals blocked (599 total) |
|---|---:|---:|
| Strict | 14 / 16 (87.5%) | 270 / 599 (45.1%) |
| Loss budget | 16 / 16 (100%) | 120 / 599 (20.0%) |
| Validated budget | 15 / 16 (93.8%) | 328 / 599 (54.8%) |

There were also 345 tied proposals; strict rejected 4, loss budget 0, and validated budget 11. These are raw gate decisions, not actual promotion counts. The beneficial sample is too small to establish a reliable reduction in false rejection. Even the validated gate allowed 271 empirically harmful proposals.

## Final policy audit

Lower mean excess bins relative to best-fit is better. Each final policy was evaluated on the same fresh 1,600-case suite spanning eight input families.

| Gate | Mean excess bins | Difference from strict | Paired bootstrap 95% interval |
|---|---:|---:|---:|
| Strict | 0.007390625 | — | — |
| Loss budget | 0.010062500 | +0.002671875 | [+0.000250000, +0.006125000] |
| Validated budget | 0.007453125 | +0.000062500 | [−0.000593750, +0.000609375] |

Plain relaxation was worse in this experiment. Validation-backed relaxation had no demonstrated final-performance advantage or disadvantage. An interval crossing zero is not proof of equivalence. No arm beat best-fit overall. Bootstrap intervals resample paired search seeds and are conditional on the shared audit suite.

## Verification and limitations

Search used 13,056,000 packer executions, plus 1,600 common initialization executions, 193,600 final-audit executions, and 768,800 diagnostic executions. This is a local mechanistic experiment; it used no external LLM API, GPU, or sponsor compute.

V4 corrects archive deduplication to preserve the largest observed regression for an input across all proposals in a generation. V3 could retain a smaller current-batch regression because of overwrite order. The correction applies equally to all V4 arms; V3 files were preserved and its results now disclose this limitation. Comparisons here are within V4.

Six dedicated checks cover bounded exceptions, severe/repeated loss rejection, fresh-validation rejection, deterministic proposals, equal budgets, and CLI audit/resume. Existing evaluator checks provide independent reference scoring and packing validity.

## Conclusion

Use fresh validation plus explicit severity and frequency limits as the next experimental gate. This is better supported than simply relaxing rejection. It preserves one additional beneficial sampled proposal and blocks 58 additional harmful ones, while final quality remains inconclusive. Keep the strict baseline and test the same rule with a broader supply of genuinely improving proposals before claiming it solves the tradeoff.

Raw results: [summary.json](summary.json), [diagnostic.json](diagnostic.json), [audit.json](audit.json). Configuration, compressed seed traces, source snapshots, and hashes are saved alongside them.
