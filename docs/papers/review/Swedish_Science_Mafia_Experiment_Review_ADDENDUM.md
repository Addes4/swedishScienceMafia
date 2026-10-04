# Missing material for the experiment review PDF

For the agent updating `Swedish_Science_Mafia_Experiment_Review.pdf`.
The current nine-page PDF includes Falsify V1-V3 but omits the completed V4
experiment and a subsequently documented V3 implementation limitation.
This addendum supplies the missing material; it does not modify the PDF.

## Suggested changes to the PDF

1. Add the V4 study below after the current page 4 promotion-gate study, and add
   it to the contents and evidence index.
2. Add the archive-deduplication note below to V3's execution/verification notes.
3. Update page 9: softer gates are now tested, rather than only a future proposal.
   The next question is whether validation-backed gates generalize with more
   beneficial proposals and real model-generated research under matched budgets.
4. Keep the overall conclusion that no Falsify arm beat best-fit on its fresh
   overall audit. V4 does not establish a causal LLM-memory benefit.

## New study: V4 - bounded losses and fresh validation

### Question and design

Can a gate preserve promising proposals while continuing to block harmful ones?
Completed 40 paired seeds and 200 generations, with identical proposals across
three equally budgeted arms. Policies use the same 20 online features as V3.
Rules were specified before the final audit. The proposal trajectory reuses the
first 200 generations of V3, so this is not an independent search replication;
the final and diagnostic audit inputs are fresh.

Each candidate is evaluated on 24 fixed training inputs, 16 sampled archive
stress inputs, and 64 fresh validation inputs. All arms perform the same work,
including validation evaluations ignored by the first two arms. All promotion
rules require training performance at least as good as the current incumbent.

- **Strict:** reject any stress-case regression relative to best-fit.
- **Loss budget:** permit losses on at most two stress inputs, at most one extra
  bin on each. Total positive stress loss must be no greater than one bin plus
  the net training gain (if positive) relative to best-fit across 24 cases.
- **Validated budget:** retain those frequency/severity limits, require mean
  validation excess no greater than zero, and permit total positive stress loss
  no greater than one bin plus the net validation gain (if positive).

One isolated one-bin stress loss may pass with neutral validation. A second
requires compensating validation gains. Gates screen new proposals and do not
automatically roll back incumbents after later failures.

### Independent proposal diagnostic

960 sampled proposals were classified using a separate 800-case suite spanning
eight input families. Labels reflect mean bin-count differences from best-fit
on this finite suite, not guaranteed true quality. Samples may contain repeated
or behaviorally equivalent proposals. These are raw gate decisions, not counts
of actual promotions.

| Gate | Beneficial allowed / 16 | Harmful blocked / 599 | Tied rejected / 345 |
|---|---:|---:|---:|
| Strict | 14 (87.5%) | 270 (45.1%) | 4 |
| Loss budget | 16 (100.0%) | 120 (20.0%) | 0 |
| Validated budget | 15 (93.8%) | 328 (54.8%) | 11 |

Validation-backed relaxation preserved one additional beneficial sampled
proposal and blocked 58 additional harmful proposals relative to strict gating.
This is encouraging, but only 16 proposals were classified as beneficial.
It does not establish a reliable reduction in false rejection. The validated
gate still allowed 271 of the 599 empirically harmful proposals.

### Fresh final-policy audit

Each final policy was evaluated on a new shared 1,600-case suite spanning eight
families. Mean excess bins is candidate bin count minus best-fit bin count;
lower is better. Intervals bootstrap paired search seeds and are conditional on
the shared audit suite.

| Gate | Mean excess bins | Difference from strict | Paired 95% bootstrap interval |
|---|---:|---:|---:|
| Strict | 0.007390625 | Reference | - |
| Loss budget | 0.010062500 | +0.002671875 | [+0.000250000, +0.006125000] |
| Validated budget | 0.007453125 | +0.000062500 | [-0.000593750, +0.000609375] |

Plain relaxation worsened final performance in this experiment. Adding fresh
validation produced no demonstrated final advantage or disadvantage versus
strict gating. An interval crossing zero does not prove equivalence.
No arm beat best-fit overall.

### Budget, verification and interpretation

The experiment used 13,056,000 search packer executions, 1,600 common
initialization executions, 193,600 final-audit executions, and 768,800 diagnostic
executions. It used no external LLM API, GPU, or sponsor compute.

All 20 scoped Falsify checks passed: six core, eight contextual, and six dedicated
soft-gate checks. The latter cover bounded exceptions, severe/repeated losses,
fresh-validation rejection, deterministic proposals and reproduction, equal
budgets, and CLI audit/resume. This was not a full-workspace test claim.

Conclusion: validation plus explicit loss limits is an experimental alternative
worth retaining alongside strict gating. Simply weakening rejection is not
supported. Final search quality has not improved, and a larger sample of
beneficial proposals is needed before claiming the tradeoff is solved.

## Correction to V3's implementation notes

V3 archive deduplication could overwrite a larger regression with a smaller
one when several proposals failed on the same probe in a generation. It retained
historical maxima from prior generations, but did not always retain the maximum
within the current batch. V4 fixes this by preserving the largest observed
regression for each input across all proposals. The correction applies equally
to all three V4 arms.

V3's saved results and source snapshots were preserved, and its Markdown results
now disclose the limitation. Do not present V3 as having always stored complete
per-generation maxima. V4 comparisons are within V4; differences from V3 cannot
be attributed solely to softer gating because the archive fix, shorter run,
validation work, and audit inputs also differ.

## Evidence paths (relative to repository root)

- `experiments/soft-gate-v4/RESULTS.md`: complete V4 interpretation.
- `experiments/soft-gate-v4/PROTOCOL.md`: pre-audit design and thresholds.
- `experiments/soft-gate-v4/summary.json`: numerical tables and paired intervals.
- `experiments/soft-gate-v4/diagnostic.json`: independent proposal diagnostic.
- `experiments/soft-gate-v4/audit.json`: fresh final-policy audit.
- `experiments/soft-gate-v4/config.json`, `seed-*.json.gz`, `source/`, and
  `source_hashes.json`: configuration, traces and implementation provenance.
- `falsify/soft_gates.py`: current implementation.
- `tests/test_soft_gates.py`: six dedicated checks.
- `experiments/gate-v3/RESULTS.md`: V3 results with archive limitation disclosure.
- `experiments/HANDOFF.md`: cumulative experiment handoff including V4.

The PDF agent should verify the numbers against the JSON evidence and incorporate
the limitations alongside the positive diagnostic result.
