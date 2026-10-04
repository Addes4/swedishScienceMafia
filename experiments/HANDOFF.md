# Falsify: work completed and research handoff

Written before starting the next experiment. This document records the work done
in this Codex session, the evidence obtained, and the limits of those findings.

## Conclusion so far

**Counterexample replay helped avoid harmful changes. We have not discovered an
algorithm that beats best-fit overall, or demonstrated an autonomous LLM memory
benefit.** The effect is reproducible in this synthetic, bounded heuristic search,
but small in absolute packing efficiency.

## Challenge and literature review

- Read the complete challenge instructions and event website text.
- Reviewed all eight supplied papers, focusing on methods, results, and
  limitations; not every long supplementary example was read line by line.
- Identified the track's actual target: a reusable algorithm research system,
  judged on novelty, performance, interpretability/ease of use, and research
  efficiency. An open mathematical breakthrough is optional.
- Noted the submission mismatch: the website asks for a two-minute demo, while
  the track PDF requests an emailed video of up to four minutes.
- Considered counterexample-guided discovery, behavioural diversity, adaptive
  research strategies, and discovery followed by simplification/explanation.
- Recommended executable failure evidence as the initial project direction.
  Existing papers already include evolutionary archives, novelty filtering,
  adaptive model selection, summaries, and hypothesis critique, so those alone
  would not distinguish our system.

## Tools and resources checked

- Python 3.14 and a local C++ compiler are available.
- Used a temporary `pypdf` environment to extract the supplied PDFs for reading.
- Checked credential presence without printing values. Anthropic, OpenAI,
  Gemini/Google, and Modal keys were not configured in the checked environment
  or `.env` files at the time of the checks.
- Claude CLI is installed but reported logged out.
- Used Codex in this conversation to propose and revise experimental hypotheses.
- No external model API, sponsor compute, Modal deployment, or GPU was used in
  the completed bin-packing experiments.
- Added an optional Anthropic proposal adapter using the documented Messages
  API and structured outputs. Network execution is untested because a key was
  not configured. The user selected the option to configure a key locally;
  authentication values have not entered logs or this document.
- Browser inspection was attempted, but no browser was available through the
  computer-use tool. The report's JavaScript syntax and embedded packing data
  were checked; its visual layout has not been verified in a browser.

## Implemented prototype

Problem: online one-dimensional bin packing with capacity 100 and sequential
integer items. The fixed packer checks feasibility and opens a new bin only when
no existing bin can hold the item. Candidates control the priority of feasible
bins. They cannot reorder items, inspect future items, modify the grader, or
place items illegally.

The initial candidate language has 12 weighted features: residual gap, squared
gap, inverse gap, exact fit, several small-gap conditions, a gap/current-item
comparison, and distances from quarter/half/three-quarter capacity. Best-fit is
the negative residual-gap score. All-zero weights implement first-fit because
ties resolve to the first feasible bin.

Built:

- `falsify/core.py`: synthetic instances, bounded mutations, JSON/gzip helpers,
  native evaluator interface, and input validation.
- `falsify/packing.cpp`: immutable feasibility and scoring implementation.
- `falsify/search.py`: repeated matched-budget searches with three memory arms.
- `falsify/pilot.py`: recorded Codex proposal evaluation and greedy reduction of
  failing inputs within an explicit evaluator budget.
- `falsify/anthropic_propose.py`: optional one-proposal model adapter, bounded
  to 1,024 output tokens and 12,000 prompt characters, with token-usage logging.
- `falsify/report.py`: standalone interactive HTML demonstration and results.
- Six automated checks covering an independent best-fit implementation,
  placement validity, invalid inputs, nonfinite weights, a concrete regression
  and correction, matched budgets, and deterministic reproduction.
- `.gitignore` excludes `.env`, compiled evaluator libraries, and Python caches.
- Replaced the placeholder README with instructions and research limitations.

No changes were committed, published, or sent to the organizers. Files outside
this implementation, including the separately appearing `strategist/` directory,
were not part of this work.

## Experiment design

Training families: uniform, small items, large items, bimodal, and complementary
pairs. Additional audit families: near-thirds, near-halves, and narrow bands.
Every instance in the repeated-run experiments contains 80 items.

Each generation evaluates the incumbent and three mutations on a frozen archive
snapshot. Each candidate consumes 48 packing executions:

- 24 fixed search cases;
- 8 replay cases;
- 8 fresh probes evaluated for both the candidate and best-fit, costing 16.

Thus a generation costs 192 packing executions. Fixed instance lengths make
item-step budgets equal. Reference initialization and final audits are separate;
equal evaluator work does not imply equal total computational cost.

Arms:

1. **Random replay:** retain random probe inputs in an archive of up to 64.
2. **Counterexample replay:** retain the largest historically observed excess-bin
   regressions over best-fit and sample replay inputs from that archive.
3. **Counterexamples plus tail fitness:** use the same archive and penalize worst
   replay performance in addition to mean score.

Final audit inputs are generated after search completes and cannot feed back
into that named experiment. The same audit set is shared across seeds and arms.
Paired bootstrap intervals measure search-seed variation conditional on that
set; they do not capture all uncertainty over future inputs or distributions.

## Completed experiments and outcomes

### Local v1: 20 paired seeds, 120 generations

Started at best-fit. Ties preserved the incumbent, limiting neutral exploration.
The tail arm initially penalized absolute bin counts rather than reference-relative
regressions. Each arm used 23,040 search executions per seed.

| Arm | Mean excess bins over best-fit |
|---|---:|
| Random replay | 0.011375 |
| Counterexample replay | 0.0066875 |
| Counterexamples plus tail fitness | 0.0083125 |

Counterexample minus random: -0.0046875 bins; paired bootstrap 95% interval
[-0.012, 0.0019375]. The interval includes zero. No arm beat best-fit overall.

### Local v2: 50 paired seeds, 500 generations

Designed after inspecting v1. Allowed neutral drift to explore score plateaus and
corrected tail fitness to excess bins over the reference. Used a fresh audit seed.
Each arm used 96,000 search executions per seed, or 7.68 million item steps,
plus 32 reference initialization executions. The independent audit comprised
800 instances, 100 per family.

| Arm | Mean excess bins over best-fit |
|---|---:|
| Random replay | 0.023000 |
| Counterexample replay | 0.000725 |
| Counterexamples plus tail fitness | 0.000550 |

Counterexample minus random: -0.022275 bins; paired bootstrap 95% interval
[-0.037825, -0.010825]. Tail variant minus random: -0.022450 bins; interval
[-0.037950, -0.010725].

This supports reduced harmful drift within this setup. It does not support
superiority over the initial best-fit algorithm. The baseline's neutral drift
and fixed-suite overfitting are part of the mechanism being tested.

### Recovery from first-fit: 20 paired seeds, 200 generations

The weak starting policy averaged 0.3275 excess bins over best-fit. After search:

| Arm | Mean excess bins over best-fit |
|---|---:|
| Random replay | 0.016000 |
| Counterexample replay | 0.005375 |
| Counterexamples plus tail fitness | 0.0041875 |

All arms improved the weak starting point. Counterexample arms recovered more
reliably, but none beat best-fit overall. Each arm used 38,400 search executions
per seed.

Paired seed bootstrap intervals (recorded in `local-firstfit/summary.json`, added
to this handoff later): counterexample minus random -0.010625 bins
[-0.018187, -0.003188]; tail minus random -0.011813 bins [-0.018812, -0.005000].
Both exclude zero.

### Codex-guided pilot and revision

Codex proposed seven initial candidates, including a best-fit control, before
evaluating that batch on 1,000 exploratory cases. Several plausible reserve-space
ideas performed worse than best-fit. Reduced counterexamples made the reason
concrete rather than relying on a verbal critique.

Example: a reserve-quarter heuristic uses three bins for `[63, 44, 32, 56]`;
best-fit uses two. At item 32, the heuristic chooses the bin with 56 remaining
instead of the bin with 37 remaining, sacrificing the space needed for the
later 56. Total size is 195, so the two-bin reference reaches the volume lower
bound on this example.

Codex inspected the feedback and proposed six revisions plus a control. The
moderate tight-or-roomy revision fixed that example and recorded one win and
zero losses on the 1,000 exploratory cases. We selected it before generating a
fresh independent audit.

On 10,000 fresh cases across eight families, that revision had:

- 3 wins against best-fit;
- 14 losses;
- 9,983 ties;
- mean excess of 0.0011 bins.

The tempting exploratory improvement did not generalize into an overall gain.
These were model-guided proposals within this conversation, not autonomous API
research or a causal comparison of different LLM memories.

## Verification and artifacts

- All six tests pass.
- Independently checked best-fit on 100 generated cases.
- Checked capacity and item conservation on 100 mutated-policy packings.
- Reproduced all three v2 seed-0 search histories exactly.
- Validated the report's 12 embedded counterexample demonstrations and checked
  JavaScript syntax.
- Saved per-seed weights, histories, archives, budgets, summaries, audit inputs,
  and audit results. Large traces are gzip-compressed JSON.
- Retained source snapshots and hashes. V1 was captured before algorithm changes;
  v2 snapshots describe post-run input-validation and logging changes.

Main entry points:

- `README.md`: reproduction commands and implementation guide.
- `experiments/RESULTS.md`: concise results and limitations.
- `experiments/report.html`: interactive counterexample and packing demonstration.
- `experiments/PROTOCOL.md` and `PROTOCOL-v2.md`: documented designs.
- `experiments/local-v1/`, `local-v2/`, `local-firstfit/`: repeated-run evidence.
- `experiments/codex_candidates.json` and `codex_revision.json`: exact proposals.
- `experiments/codex-pilot-v1/` and `codex-pilot-v2/`: feedback and fresh audit.

## What remains unproven

- Better-than-best-fit algorithm discovery.
- A causal benefit from executable counterexamples in LLM prompts.
- Performance on external benchmarks, variable lengths, or multidimensional packing.
- Generalization beyond the eight synthetic families.
- A novelty claim against the complete literature.
- The effectiveness of a hardened evaluator against arbitrary model-written code.

Historical archive entries can become stale. Changing replay cases also changes
the selection distribution, so replay benefits should not be described as a pure
effect of explanatory memory. The small candidate language and strong best-fit
warm start may limit useful discovery.

## Next experiment

Test counterexamples as a **promotion gate**, separately from candidate
generation. Broaden proposals to use past-item distribution information while
preserving the online constraint. Feed all arms an identical candidate stream,
compare fixed-score-only promotion with random gates and counterexample gates,
charge every evaluator execution, and use a fresh audit. This isolates the gate
from changes in the proposal trajectory.

The immediate question is whether the gate rejects harmful proposals while
retaining genuinely beneficial ones. It is still a local mechanistic experiment;
an LLM memory ablation will require independent model runs, logged prompts and
token budgets, and another fresh audit.


## Subsequent experiment completed: V3 promotion gates

After saving the handoff above, implemented and completed the next experiment.
See `gate-v3/PROTOCOL.md` and `gate-v3/RESULTS.md` for the full design and results.

Added `falsify/contextual.py`, `contextual.cpp`, and `gated_search.py`. Candidates
can now use eight additional features calculated only from earlier items in the
same stream, giving 20 total features. Native scoring was checked against an
independent Python implementation. Future suffix changes do not affect earlier
packing decisions.

The study used 40 paired seeds, 400 generations and identical proposal streams
across three promotion rules. Gate decisions did not alter the generation
trajectory. Each arm consumed 89,600 search executions per seed; all searches
together consumed 10,752,000. The final audit used 1,600 fresh instances, and a
separate 160-case diagnostic suite evaluated 960 sampled proposals after search.

| Promotion rule | Mean excess bins over best-fit |
|---|---:|
| Fixed search score only | 0.014000000 |
| Random-input gate | 0.012859375 |
| Counterexample gate | 0.011828125 |

Counterexample minus score-only: -0.002171875 bins, paired bootstrap 95% interval
[-0.004109375, -0.000609375]. Counterexample minus random gate: -0.001031250 bins,
interval [-0.002390625, 0.000046875]. The latter comparison is inconclusive.

Among sampled proposals empirically worse on the diagnostic suite, the
counterexample gate rejected 201/424 (47.4%), versus 152/424 (35.8%) for the
random gate. Among empirically better proposals, it rejected 25/62 (40.3%), versus
13/62 (21.0%). These are finite-suite classifications rather than statistically
established true improvements; some proposals are repeated or equivalent.

**Updated conclusion:** counterexample gates are more conservative and offer a
small benefit over score-only promotion in this setup. We have not clearly shown
they outperform random gates. They also obstruct some promising proposals. No
arm beat best-fit overall. This remains a local mutation study, not an LLM memory
ablation. The next design should turn failures into condition-specific evidence
rather than universally banning any candidate that regresses on one old input.

There are now 14 passing Falsify checks, including an end-to-end CLI audit and
resumption test. Full workspace discovery also observed an unrelated failure in
`tests/test_strategist.py`; those separately developed files were left untouched.
An audit aggregation bug was fixed after search completion, and the audit resumed
with the original saved candidates/configuration. Discarded audit work of 3,200
executions is recorded in `gate-v3/execution_note.json`. Search and resumed-audit
source snapshots are retained separately.

The complete V3 seed-0 proposal stream, gate decisions, deployed weights and
diagnostic sample were reproduced exactly after the audit fix. Gates inspect
16 sampled archive inputs at promotion time and do not automatically roll back
an incumbent when later probes reveal a new failure. The 268,800 packer
executions in this verification rerun are separate from the experiment budget.

## V4: bounded exceptions backed by fresh validation

Completed the requested experiment to preserve promising proposals while
continuing to reject harmful ones: 40 paired seeds, 200 generations, identical
proposals, three equally budgeted arms. Rules were written in
`soft-gate-v4/PROTOCOL.md` before the audit. Full findings are in
`soft-gate-v4/RESULTS.md`; traces, source snapshots, hashes, and raw audits are saved.

Strict rejection allowed 14/16 empirically beneficial sampled proposals and
blocked 270/599 harmful ones. Plain bounded relaxation allowed 16/16 but blocked
only 120/599. Adding 64 fresh validation cases allowed 15/16 and blocked 328/599.
The beneficial sample is small; these labels come from an independent 800-case
diagnostic suite and do not guarantee true quality. Repeated proposals count.

On fresh 1,600-case final audits, mean excess bins were 0.007390625 (strict),
0.010062500 (relaxed), and 0.007453125 (validated). Relaxed-minus-strict was
+0.002671875, with paired bootstrap interval [+0.000250000, +0.006125000].
Validated-minus-strict was +0.000062500, interval
[−0.000593750, +0.000609375]: no demonstrated final advantage. No arm beat best-fit.

The validated rule caps losses at two stress inputs and one extra bin per input,
requires nonpositive mean validation excess, and uses validation gains to pay
for a second stress loss. It still allows 271/599 harmful sampled proposals.
Recommendation: retain this as an experimental alternative alongside strict
gating, rather than claiming a solved separator.

V4 also fixes archive deduplication: keep the largest observed regression per
input across a generation's proposals. V3 could overwrite a larger current-batch
loss with a smaller one; its original results are preserved with a disclosure.
The correction is shared across all V4 arms. V4 reuses the first 200 generations
of the V3 search trajectory, so fresh audits do not make it an independent search
replication.

Budget: 13,056,000 search executions, 1,600 initialization, 193,600 final audit,
768,800 diagnostic. No API calls or cloud compute. All 20 scoped Falsify checks
passed (6 core, 8 contextual, 6 soft-gate checks). Unrelated strategist work was
left untouched.
