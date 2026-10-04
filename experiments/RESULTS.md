# Falsify: initial experiments

Counterexample replay reduced harmful drift in a bounded online bin-packing search. It did not produce an overall improvement over best-fit. This is a mechanistic evolutionary-search result; it does not establish an LLM memory benefit.

## Main follow-up: 50 paired seeds, 500 generations

| Arm | Mean excess bins over best-fit | Search executions per seed |
|---|---:|---:|
| random_replay | 0.023000 | 96,000 |
| counterexample_replay | 0.000725 | 96,000 |
| counterexample_tail | 0.000550 | 96,000 |

Lower is better; zero matches best-fit on average. Each test instance contains 80 items. Each arm uses 96,000 packing executions (7,680,000 item steps) per seed, plus 32 reference initialization executions. Final audit uses 800 shared instances (100 per family) and is excluded from search cost.

- counterexample_replay minus random: -0.022275 bins; paired seed bootstrap 95% interval [-0.037825, -0.010825].
- counterexample_tail minus random: -0.022450 bins; paired seed bootstrap 95% interval [-0.037950, -0.010725].

Intervals quantify variation across search seeds, conditional on this shared audit suite. They do not capture uncertainty over all possible test distributions. The effect is small in absolute packing efficiency. V2 was designed after inspecting V1, and used a fresh audit seed. The follow-up remains exploratory.

## Codex-guided experiment

Codex proposed seven hypotheses, inspected measured failures, and proposed six revisions plus a best-fit control. The reserve-quarter heuristic uses 3 bins for [63,44,32,56], while best-fit uses 2. The revised moderate tight-or-roomy heuristic fixes this case.

Its exploratory selection result was one win and no losses on 1,000 cases. The independent 10,000-case audit found 3 wins, 14 losses, and 9,983 ties: mean excess 0.0011 bins. This rejects a broad improvement claim despite the attractive pilot result.

## Recovery from first-fit

The initial first-fit policy averaged 0.327500 excess bins over best-fit on its audit suite. After 200 generations / 20 paired seeds, final excess was random_replay: 0.016000, counterexample_replay: 0.005375, counterexample_tail: 0.004188. All arms improved the weak starting policy; none beat best-fit overall.

- counterexample_replay minus random: -0.010625 bins; paired seed bootstrap 95% interval [-0.018187, -0.003188].
- counterexample_tail minus random: -0.011813 bins; paired seed bootstrap 95% interval [-0.018812, -0.005000].

Both intervals exclude zero: at equal search budgets, the counterexample arms recovered closer to best-fit than random replay.

## Limitations and next experiment

- The candidate language is 12 weighted features, not arbitrary algorithm code. Its expressive power and best-fit warm start constrain discovery.
- Counterexamples are prioritized by the largest historical observed regression, so archive relevance can become stale.
- Changing the replay distribution is part of the treatment; this does not isolate explanatory memory in LLM prompts.
- Audit instances are untouched during each named search but generated in the same researcher-controlled process; this is not a hardened adversarial sandbox.
- Test cases are synthetic, fixed-length, one-dimensional integer packing tasks. External benchmarks and variable lengths remain untested.
- Separate the search archive from a validation gate: candidates should demonstrate benefit on a fixed suite and pass archived regressions before promotion. Then compare no memory, prose memory, and executable counterexample memory with the same model and token budget.

## Reproduction

See README.md and PROTOCOL-v2.md. Raw traces are gzip-compressed JSON; summaries and independent audits are plain JSON. Source snapshots preserve the experiment implementations. Open report.html for the packing demonstration.
