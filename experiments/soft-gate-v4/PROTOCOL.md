# V4: soften rejection, preserve protection

Written before V4 search or audit results are inspected. Exploratory design,
motivated by V3 rejecting both harmful and promising proposals.

## Hypothesis

Allowing bounded, compensated losses on stress inputs, with fresh validation,
can retain more empirically beneficial candidates than an all-or-nothing gate
while still rejecting many harmful ones. Success is not assumed: report both
retention of beneficial proposals and rejection of harmful proposals, plus
deployed-policy quality and its uncertainty.

## Common setup

Use the same 20-feature online candidate language and shared proposal-generation
logic as V3. Run 40 paired seeds and 200 generations. Each generation proposes
best-fit, the shared explorer, a mutation of that explorer, and a mutation of a
contextual anchor. Generation uses only a fixed 24-case suite, independently of
promotion decisions. Gates use 16 sampled counterexample-archive cases. The
archive contains up to 64 inputs with the greatest historical observed excess
over best-fit; its initial entries are random until failures replace them.

Each generation also gets 64 fresh validation instances, balanced as closely as
possible across the five original training families. All arms see the same
validation instances. They are never used to select the shared explorer, modify
its mutation stream, or add archive entries. They can affect promotion under the
evidence rule. Probes for archive mining remain eight fresh search instances.

## Gate rules

All arms require the fixed-suite score to be no worse than their deployed
incumbent. The rules below operate independently of that score comparison:

1. `strict`: reject any positive stress-case excess over best-fit.
2. `loss_budget`: permit losses on at most two of the 16 stress inputs, at most
   one bin on any input. Total stress losses must not exceed one plus the total
   best-fit-relative gain on the 24 fixed search cases. This gives one isolated
   one-bin exception even for a score-neutral proposal.
3. `validated_budget`: same loss-frequency and severity limits, require mean
   excess on the 64 fresh validation cases <= 0, and permit total stress losses
   up to one plus the net gain measured on fresh validation cases. This uses
   validation evidence rather than training gain to pay for the second allowed
   loss.

These constants are fixed before the run. An average validation tie is not
proof of equivalence or improvement. Severe/frequent stress losses remain
blocked even if average validation score looks good. Classifier passes do not
necessarily imply promotion: another candidate may score better or the
incumbent may have a lower fixed score. Tied eligible candidates are selected
using the same deterministic selection stream across arms. Gates do not roll
back an incumbent automatically when a later probe exposes a failure.

## Budget accounting

For each candidate, per arm: 24 fixed evaluations + 16 stress evaluations + 64
fresh validation evaluations + 8 probe evaluations + 8 reference probe
evaluations = 120 executions. Validation references cost 64 additional
executions per arm per generation, shared across its four candidates. Each arm
uses 544 executions per generation, 108,800 per seed, or 8,704,000 item steps.
The strict and loss-budget arms also perform validation evaluations, though
they do not use them, keeping evaluator work matched. Shared initialization
is 40 reference executions per seed. Search totals 13,056,000 executions.

Proposal-generation seeds, fixed cases and archive probes reuse the first 200
generations of V3's shared trajectory. This is deliberate, not an independent
replication of search variability. All final audit and diagnostic cases are new.

Before running V4, corrected an archive deduplication issue found in V3:
multiple proposals tested on the same probe could overwrite an earlier larger
within-generation regression with the final proposal's smaller regression.
V4 retains the maximum observed regression for each input across both previous
archive entries and the complete current proposal batch. V3 results remain
unchanged and describe its saved implementation. All V4 arms use this same
corrected archive; the proposal trajectory remains unchanged.

## Final audit and diagnostics

Only after all search runs finish, generate 1,600 final audit instances with
seed 67867967, 200 for each of the five search families and three shifted
families. Primary comparisons: each soft rule minus strict in final mean excess
bins over best-fit. Bootstrap across 40 paired search seeds, 10,000 resamples,
seed 49999. Intervals are conditional on the shared audit suite.

Uniformly reservoir-sample 24 non-control proposals per seed that were no worse
than best-fit on the fixed suite, using the same sample procedure as V3. Audit
these 960 proposal snapshots on a separate 800-case suite, seed 86028121.
Classify each as empirically better, worse or tied by average excess over
best-fit. Report gate rejection counts in every class; these are finite-suite
labels, not guarantees of true algorithm quality. Repeated/behaviourally
equivalent proposals are allowed and disclosed.

Search evaluations, shared initialization, final audit and diagnostic evaluations
are counted separately. Preserve source, hashes, gate statistics, proposal
hashes, weights, trace data and independent test cases. Do not change gate
constants or choose a winning rule using the audit within this named run.
