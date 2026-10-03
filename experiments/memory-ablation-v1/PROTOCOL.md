# Memory ablation v1: does executable counterexample memory help a closed-loop LLM search?

Written on Saturday 3 October 2026, before the pilot and before any confirmatory run.
Later changes are listed under "Amendments" with the time they were made.

## Question

In a closed-loop search where a language model proposes one candidate per call and a
harness evaluates, promotes and writes the next prompt with no human edits, does
showing the model executable counterexamples (small concrete inputs on which earlier
proposals used more bins than best-fit, with both packings) lead to better audited
final policies than showing nothing, or than a prose summary of the same failures
filling the same number of tokens?

This is the main unproven claim of Falsify (experiments/HANDOFF.md). Earlier evidence
came from mutation search (V1-V4) and one Codex pilot guided by hand inside a
conversation. No closed-loop LLM run has been recorded before this study.

## Loop

- Model `claude-haiku-4-5`, one structured-output call per step (JSON schema: name,
  hypothesis, falsification, one number per feature weight), `max_tokens` 1024, default
  sampling. 30 calls per run. Code: `falsify/closed_loop.py`, `falsify/memory.py`,
  `falsify/llm.py`, `falsify/backends.py`.
- The system prompt (problem, packer rules, feature definitions, families, goal) is the
  same in every arm. The user prompt holds the current incumbent's weights and its
  fixed-suite scores (mean excess bins versus best-fit, wins/ties/losses, per family),
  the call number, the promotion rule, and the arm's memory section.
- Each run starts from best-fit as the incumbent.
- Every proposal that parses is evaluated on: the run's fixed search suite (400
  instances, 80 per training family); 100 fresh probe instances for this call, run for
  the proposal and for best-fit; and up to 16 inputs sampled from the run's archive
  for a shadow gate (below). The up to four largest probe losses are shrunk by greedy
  single-item deletion (at most 2,000 packer executions each), and the two shortest
  shrunk inputs are kept as that proposal's counterexamples, with both packings and
  the first decision where the policies differ. All arms do this work, including arms
  that never show it.
- Invalid replies (schema violation, a weight outside [-12, 12], truncation, refusal,
  or five failed transport attempts) still count as one of the 30 calls.

## Promotion rule (the same in every arm)

Score-only: a proposal replaces the incumbent if and only if it uses strictly fewer
total bins than the incumbent on the fixed suite. Ties do not promote.

Why not the strict archive gate: in the executable arm the archive inputs and the
counterexamples shown to the model come from the same probe failures, so a gate would
reward that arm for passing a test it was shown, confounding "learned from evidence"
with "passed a known check". V3 also found that the strict gate rejected 40% of
empirically better proposals, which a 30-call run cannot afford. A 400-instance
fixed suite (V3 used 24) keeps score-only promotion less noisy. The strict gate from
`falsify/soft_gates.py` is still computed for every proposal on up to 16 sampled
archive inputs, and its verdict is recorded but never used. The archive follows the
V4 rule: deduplicate by input, keep the largest observed loss, keep 64.

## Arms

Only the memory section of the user prompt differs.

- **none**: no memory section. The model sees the incumbent and its scores only.
- **prose**: summaries of earlier proposals that were not promoted, newest first. Each
  gives the proposal's name, its stated idea, its non-zero weights, its fixed-suite
  excess with losses/wins/ties, the two families with the largest excess, probe losses,
  and one sentence on how it first departed from best-fit on its shrunk failing inputs
  (roomier or tighter bin, median space left versus best-fit's). It names no concrete
  input. If the incumbent is not best-fit, a summary of its own failures comes first.
- **executable**: for the same proposals, newest first, the name, non-zero weights,
  fixed-suite excess, and up to two shrunk counterexample inputs each: the items in
  arrival order, the policy's bins and best-fit's bins with their contents, and the
  first different decision. At most 8 counterexamples in total. If the incumbent is not
  best-fit, its own counterexamples come first.

prose and executable fill the same budget of 1,500 input tokens, measured with the
API's token-counting endpoint on the memory text (a characters-per-token estimate is
used only to choose candidates, and if counting fails). Entries that do not fit are
skipped. Realized memory tokens are reported per arm.

## Seeds and pairing

A run seed fixes all harness randomness: the fixed suite, the initial archive, every
call's probes and the shadow-gate samples. Each seed is run once in every arm, so arms
are paired by seed. Seeds do not fix model sampling, which is not seedable; paired
differences therefore include model-sampling noise.

## Endpoints

Primary: the audited mean excess bins of each run's final incumbent over best-fit on
1,600 fresh instances (200 in each of the five training families and the three shifted
families near_thirds, near_halves and bands). Lower is better; 0 means the same as
best-fit. Two primary contrasts, paired by seed: executable minus prose (does the form
of the evidence matter at equal tokens?) and executable minus none (does the evidence
help at all?). prose minus none is reported as well.

Secondaries:

1. Harmful proposals: the share of valid proposals with positive mean excess over
   best-fit on a separate 800-instance diagnostic suite (100 per family, eight
   families), evaluated after all runs end. Invalid calls are reported separately.
2. Repeated failed ideas: valid proposals whose per-instance bin counts on the fixed
   suite exactly equal those of an earlier non-promoted proposal in the same run; and
   proposals that pack every fixed instance exactly like the incumbent.
3. Input and output tokens and dollars per arm; realized memory tokens per arm.
4. Mean diagnostic excess of all valid proposals; promotions; shadow-gate pass rate.

## Analysis

Means over seeds per arm. Paired seed-level bootstrap intervals (10,000 resamples,
bootstrap seed 49999, 2.5 and 97.5 percentiles) for the contrasts above. Intervals
measure variation across runs (harness seed and model sampling) conditional on the
shared audit and diagnostic suites. No multiplicity correction; the two primary
contrasts are reported together.

Interpretation: an interval for executable minus prose that lies entirely below zero
supports the claim that executable counterexamples beat prose at equal tokens. An
interval that includes zero is inconclusive. If most final incumbents in every arm
are still best-fit, the primary endpoint has no room to move (a floor), and that will
be stated plainly; the secondaries then describe proposal quality only.

## Audit freshness

The audit and diagnostic seeds are taken from the SHA-256 of all finished run traces
(`audit_seeds` in closed_loop.py). The instances therefore cannot exist until every
search run has ended, and the audit refuses to run while any run file is missing.
Audit results are never fed back into a run of this experiment.

## Budgets

- Anthropic: $15 total for this task, enforced in code. Each request reserves an upper
  bound on its cost before sending (one input token per byte of system, user and schema
  text plus 2,000 tokens, plus `max_tokens` output, at the prices in
  autoresearch/claude.py) and is refused if spending plus open reservations could pass
  the invocation cap or the $15 total cap (which counts every usage.jsonl under this
  folder). Every attempt, failed or not, is logged to the run folder's usage.jsonl.
- Expected cost is about $0.005 per call: about $1 for the pilot and about $5 for the
  confirmatory run.
- Evaluator work is milliseconds per proposal, so it runs locally in the API worker
  threads (6 threads, I/O bound). No Modal use is planned.

## Pilot (current regime)

Backend `weights20_synthetic80` (the V3/V4 20-feature language on 80-item synthetic
families), seeds 100 and 101, all three arms, 30 calls each: 180 calls, cap $3. Its
purpose is to check the machinery and see whether this regime gives the primary
endpoint any room. Pilot results are reported as a pilot and are not pooled with the
confirmatory runs. Changes made after looking at the pilot will be listed under
Amendments.

A two-call infrastructure check (seed 900, executable arm, $0.0092) was run before this
protocol was written, to confirm that structured output and token counting work with
this model. It is kept in `smoke/` and is not analysed.

## Confirmatory run

10 seeds (0-9) per arm, 30 calls per run, 900 calls, all other settings as above.
The backend (current regime or a Weibull / code regime with more headroom over
best-fit) will be fixed by an amendment here before the run starts. If the backend
changes, the problem statement in the system prompt changes with it, the same for all
arms.

## Outputs

`config.json` (all settings, source hashes per invocation), `source/` (code snapshot),
`runs/<arm>-s<seed>.json.gz` (every prompt, raw response, parsed proposal, evaluation,
counterexamples, memory token counts and promotion decision), `usage.jsonl`,
`audit.json`, `audit_cases.json.gz`, `summary.json`, and RESULTS.md.

## Amendments

None yet.
