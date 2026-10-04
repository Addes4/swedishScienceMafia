# V3: counterexamples as promotion gates

Written before running v3 or inspecting its final audit.

## Question

Does a gate based on previously observed regressions reduce harmful promotion
more effectively than an equally sized random-input gate, without constraining
the candidate-generation trajectory?

## Candidate language

Retain the 12 original bin-scoring features and add eight features using only
past items in the current instance: gap times estimated non-fit probability;
nonzero-gap non-fit probability; probability mass near the gap; distance from
the gap to a previously observed item size; estimated probability of fitting the
gap; gap times that probability; the fit-probability difference between the
original remaining capacity and residual gap; and gap times mean past item size.

Empirical probabilities use a uniform pseudocount of 0.25 per size (25 items of
smoothing mass). Nearest-item distance uses actual past observations, with a
uniform-mean fallback before the first observation. No candidate sees future
items or another instance's observations. Capacity remains 100; length remains 80.

## Common proposal trajectory

Use 40 paired seeds and 400 generations. Every generation proposes four policies:
best-fit, the shared explorer, one mutation of that explorer, and a mutation of
one of six predefined contextual anchors. The explorer is selected exclusively
on a fixed 24-instance suite, with random tie selection. This trajectory is common
to all arms and independent of gate decisions. Mutations alter up to five of the
20 weights, each bounded to [-12,12]. Anchor definitions are saved before running.

## Arms

- `fixed_only`: promote when fixed-suite score is no worse than incumbent.
- `random_gate`: same score condition; additionally require no excess bins over
  best-fit on any of 16 randomly sampled archived inputs.
- `counterexample_gate`: same score condition; additionally require no excess
  bins over best-fit on any of 16 sampled archived regressions.

Among eligible candidates, choose the lowest fixed score and randomize ties.
All arms start at best-fit. Equal scores are permitted to preserve exploration.
Their explorer is unaffected if promotion fails. Gate comparison is against the
stable best-fit reference, not a potentially regressed current incumbent.

The counterexample archive keeps the greatest historical observed regressions
among probes from all four proposals, deduplicated and bounded to 64. The random
archive retains a random subset of the same probes. Until enough regressions
exist, initial random cases can remain in the counterexample archive. Freeze
archives at each generation boundary. Evaluate fresh probes only after forming
proposals; they affect gates from the next generation onward.

## Budget

Per candidate, per arm: 24 fixed cases + 16 gate cases + 8 fresh probes + 8
reference probe executions = 56 packer executions, or 4,480 item steps. The
fixed-only arm evaluates its random gate cases for budget matching but ignores
their gate verdict. Four candidates means 224 executions per generation and
89,600 per arm per seed. All actual evaluator calls are charged, including
duplicate reference executions. Shared reference initialization is 40 executions
per seed (24 fixed + 16 initial archive cases), recorded separately. Gate
references for later probes are retained from charged evaluations. Snapshot
source and hashes before running.

## Final audit

After all searches complete, generate 1,600 fresh cases using seed 32452843:
200 per family across the five original families and three shifted families.
Primary outcome: final deployed policy's mean excess bins over best-fit, with
paired seed-level bootstrap intervals (10,000 resamples, bootstrap seed 49999).
Compare counterexample gate with both fixed-only and random gate. Also record
promotions, gate rejections, and the unchanged proposal hashes across arms.

Secondary diagnostic: uniformly sample 24 fixed-score-eligible, non-best-fit
proposals per seed using seed 700000+search_seed. Evaluate them after search on a
separate 160-case diagnostic suite, seed 49979687. Estimate gate rejection and
acceptance among policies that are empirically better/worse/tied with best-fit on
that suite. This is a finite-suite diagnostic, not a statistical assertion of
true superiority. These audit executions are excluded from the search budget
and counted separately. Diagnostic and final audit results cannot feed back
into v3 candidate generation or selection.

## Interpretation

This isolates promotion gating from generation trajectories. It remains a local
mutation experiment, not an LLM memory study. Failure to beat best-fit should be
reported even if a gate reduces regressions. A gate could trivially keep the
starting baseline, so report promotion counts and rejection of empirically
beneficial candidates alongside final quality.
