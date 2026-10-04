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

1. After the pilot (Saturday evening, before any confirmatory run): three descriptive
   metrics were added to the audit, because the pilot showed that "repeated failed
   ideas" was dominated by proposals that pack exactly like the incumbent: repeats that
   are not copies of the incumbent, mean fixed-suite excess of proposals that are not
   copies, and the best fixed-suite excess per run. The two counts in secondary 2 remain
   as defined above. The pilot audit was re-run with these metrics; the audit is a pure
   function of the saved traces, so no earlier number changed.
2. Evaluator work follows one rule in every arm, but its amount is not equal across arms:
   shrinking runs only on proposals that lose probes (pilot: about 45,000, 21,000 and
   27,000 packer executions per run for none, prose and executable). It is a few seconds
   of CPU per run and is reported, not matched.
3. **Confirmatory regime fixed (committed in 96f217d at 20:22:17 BST on Saturday 3
   October, before the first confirmatory call at 20:22:41).** (This line originally said
   "about 21:00 BST"; the time was corrected after launch from the commit and usage logs.) The coordinator chose the Weibull 5k code regime. The full
   design is in the section "Confirmatory study" below and supersedes "Confirmatory run"
   above wherever they differ. It adds, identically in all three arms, one sentence to
   the "This call" section of the prompt: "A proposal that packs every fixed-suite
   instance exactly like the incumbent cannot be promoted and uses up a call." The no-op
   rate per arm becomes a secondary endpoint.

# Confirmatory study: Weibull 5k, code representation

Written before launch. Code: `falsify/closed_loop_code.py` (loop, audit, CLI),
`falsify/code_eval.py` (sandboxed evaluation, short-stream mining, shrinking),
`falsify/memory_code.py` (memory sections), `falsify/memory_ablation_modal.py` (Modal
back end and spend cap). The problem adapter and evaluator come from branch
exp/bp-ceiling, merged at commit f736fb2 (merge ec4d132); the adapter
(`problems/bin_packing_online`, the gate's online protocol) is unchanged since ffd72cf.

## Question

The same as above, in a regime with headroom over best-fit. On 5,000-item Weibull(45, 3)
instances, FunSearch's published heuristic uses about 62 fewer bins per instance than
best-fit (positive control from bp-ceiling-v1). Does showing the model executable
counterexamples lead to better audited final policies than no memory, or than a prose
summary of the same failures filling the same number of tokens?

## Loop

- Representation: one complete Python module defining `priority(item, bins)` per call,
  with FunSearch's evaluator semantics (as many bins as items, unused bins included,
  highest score wins, first index on ties). Structured output fields: name, hypothesis,
  falsification, code. Model `claude-haiku-4-5`, `max_tokens` 2048 (code needs more room
  than 20 weights; the same in every arm), default sampling, 30 calls per run.
- The system prompt states the problem, the interface, the item distribution, best-fit
  as the starting incumbent, and the sandbox rules. It does not mention FunSearch.
- The user prompt shows the incumbent's full code, its fixed-suite bins per instance,
  best-fit's, the L2 lower bound, the per-instance difference from best-fit, the call
  number, the promotion rule, the no-op sentence and the arm's memory section.
- Every run starts from best-fit (`return -(bins - item)`).
- Fixed suite per run seed: 5 instances of 5,000 items (namespace
  `memory-ablation-v1/fixed`), shared by the three arms of that seed.
- Evaluation of a proposal: the gate's static checks; then each fixed instance in a
  fresh process through `autoresearch.sandbox.run_online` with the problem's trusted
  driver (items revealed one at a time, credentials stripped, 30 seconds per instance).
  A static rejection, an exception, a timeout or invalid decisions make the call a
  failed call. Evaluation runs in Modal containers with no network, no secrets and no
  access to Modal resources.
- Promotion (same in every arm): the proposal replaces the incumbent if and only if it
  uses strictly fewer total bins than the incumbent on the fixed suite.

## Counterexamples (the evidence both memory arms draw on)

For every proposal that runs, in every arm: a fresh probe stream of 2,000 items per call
(namespace `memory-ablation-v1/probe`, the same for the three arms of a seed) is cut into
50 streams of 40 items. Each short stream is packed from empty bins (40 bins) by the
proposal and by a reference: the incumbent at the time of the proposal, and also
best-fit when that incumbent is not best-fit. Up to the four worst losing streams per
reference are shrunk by greedy single-item deletion (at most 300 trials each) while the
proposal still uses more bins. Shrunk streams of at most 30 items are kept, shortest
first, at most two per reference. Each kept stream is re-run in fresh gate processes
and dropped if the loss does not reproduce. Short streams and shrinking run in one
persistent online child per program (items still revealed one at a time; the module is
re-executed for every stream). This work is counted separately from fixed-suite
evaluation.

## Arms (only the memory section differs)

- **none**: no memory section.
- **prose**: for earlier proposals that were not promoted, newest first: name, stated idea
  (at most 200 characters), fixed-suite bins per instance versus the incumbent of the
  time (and versus best-fit when different), how many short streams it lost and won
  against that reference, whether it packed exactly like the incumbent, and one sentence
  on how its first departure from the reference went on its shrunk losing streams
  (opened a new bin although an open bin had room / chose a roomier or tighter open
  bin), with the median stream length. No concrete input. If the incumbent is not
  best-fit, a summary of its own short-stream losses against the incumbent it replaced
  and against best-fit comes first.
- **executable**: for the same proposals: name, idea, fixed-suite result, and up to two
  shrunk losing streams each, with the items, both packings and the first different
  decision. At most 8 streams in total. If the incumbent is not best-fit, its own
  streams (against the incumbent it replaced and against best-fit) come first.
- In both memory arms, proposals that were rejected by the integrity gate or failed to
  run get the same one-line note (the gate rejection is generic; a runtime failure shows
  the last line of the error). Replies that could not be parsed are left out of memory.
- prose and executable fill the same budget of 1,500 tokens, counted with the API's
  token-counting endpoint. Realized memory tokens are reported per arm.

## Known threat, measured before launch

Short streams packed from empty bins disagree with the long-run objective in this
regime. FunSearch's heuristic used more bins than best-fit on 200 of 200 Weibull streams
of 30 items and of 60 items, and on 199 of 200 of 100 items, yet it ends a 5,000-item
instance 64 bins ahead. In one 5,000-item stream it used more bins than best-fit up to
about item 500 and fewer from about item 1,000 on. Its shrunk counterexamples are two
items long (it opens a new bin for the second item). Executable counterexamples of this
kind can therefore point away from policies that win only over long horizons. Both
memory arms report the short-stream evidence next to the fixed-suite result on
5,000-item instances, so neither arm hides the long-run outcome. This is the design the
coordinator specified; the threat is stated here so that a negative result for the
executable arm can be read correctly.

## Seeds, pairing and budgets

Seeds 0-9, three arms, 30 calls: 900 calls. A seed fixes the fixed suite and the probe
streams, not model sampling. Up to 15 runs in parallel.

- Anthropic: the total cap for the whole task stays at $15, enforced in code and
  counting the $0.94 already spent (pilot, smoke, checks). This invocation is capped at
  $9. Expected: about $0.003 per call, about $3 in total.
- Modal: app `ssm-memory-ablation`, cap $5 including all earlier Modal use under this
  folder. Each call reserves its worst case (the function timeout at list prices plus
  25%) before it is submitted. Expected: under $1.

## Endpoints

Primary: audited mean excess bins per instance of each run's final incumbent over
best-fit, on 400 fresh 5,000-item instances (namespace `memory-ablation-v1/audit`).
Lower is better. Primary contrasts, paired by seed: executable minus prose, and
executable minus none; prose minus none is also reported. Paired seed bootstrap, 10,000
resamples, seed 49999, 95% percentile intervals. The audit uses 400 instances rather
than 1,600, because each instance is 62 times longer: 2 million item steps per policy
against 128,000 in the pilot.

Fixed reference (not an arm): FunSearch's Weibull heuristic (notebook commit cc53f27)
and best-fit on the same 400 audit instances, with an instance-level bootstrap interval.
Also reported as % excess over the L2 lower bound, as FunSearch reports.

Secondaries:

1. Harmful proposals: share of valid proposals with more mean bins than best-fit on 10
   fresh 5,000-item diagnostic instances; and share with more mean bins than the
   incumbent of their time on the same instances.
2. No-op rate: share of valid proposals that pack every fixed instance exactly like the
   incumbent (identical decisions up to bin relabelling).
3. Repeats and reverts: valid proposals that pack the fixed suite exactly like an
   earlier non-promoted proposal of the run, and proposals that pack exactly like a
   former incumbent (reverting to an earlier state).
4. Gate rejections and runtime failures per arm; promotions; best fixed-suite result per
   run.
5. Tokens and dollars per arm; realized memory tokens; Modal seconds; shrinking trials
   and short-stream executions, separately from fixed-suite evaluation.
6. Similarity to FunSearch's published heuristic (added at the coordinator's request
   before launch; FunSearch's code is public and Haiku may reproduce it from memory).
   For every promoted or final candidate: run it on 2 fresh 5,000-item instances
   (namespace `memory-ablation-v1/similarity`), replay its own decisions, and at every
   step ask whether FunSearch's heuristic, given the same bins, would pick a bin with the
   same remaining capacity. Report the agreement fraction (and the same against
   best-fit), flag near-copies (agreement at least 0.99), and give the near-copy rate per
   arm. This does not bias the comparison between arms, but it qualifies any claim that
   a run "found" a better-than-best-fit heuristic.

## Audit freshness

Audit and diagnostic seeds come from the SHA-256 of all 30 finished traces, so the
instances cannot exist before every run has ended. The audit refuses to run unless all
three arms and the expected seeds are present. Nothing from the audit feeds back.

## Interpretation

An executable-minus-prose interval entirely below zero supports the claim that
executable counterexamples beat prose at equal tokens. An interval containing zero is
inconclusive. If final incumbents stay at best-fit in most runs of every arm, the
primary endpoint is at its floor and that will be said plainly.

## Infrastructure checks before this section

Not analysed, kept for provenance: `checks/modal-mock/` (mock model, Modal back end, 3
calls) and `checks/live-code/` (seed 903, three arms, 3 calls each, $0.0263; no
promotions). One cosmetic change followed them: the stated idea in memory is now cut at
a word boundary.
