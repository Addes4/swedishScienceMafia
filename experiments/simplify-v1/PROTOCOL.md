# Simplify-and-explain protocol (written before the first run)

Question: after discovery, can a winning heuristic be reduced to a short, readable rule without losing measured quality, and which of its terms actually matter?

Inputs are the final weight vectors already produced by `experiments/local-v1` (all arms, all seeds) and the recorded Codex candidate batches. Nothing in the search code or its outputs is modified.

Three fresh suites, seed-separated from search, from each other and from the local-v1 audit (seed 982451653 is not reused):
- selection: 500 instances, training families, seed 7000001. Used only to choose which candidate to deep-dive (lowest mean bins; ties broken toward more non-zero terms, the harder simplification case).
- simplification: 1000 instances, training families, seed 7000002. Used for greedy term elimination and weight rounding.
- confirmation: 800 instances, training plus shifted families, seed 7000003. Used once, after simplification, for original vs simplified vs best-fit comparison, ablations of the simplified rule, and the shrunken witness. Confirmation results cannot feed back into simplification.

Simplification: weights are normalized by max |w| (argmax packing is invariant to positive scaling). Greedy backward elimination removes the term whose removal costs least, accepted while mean bins on the simplification suite stay within tol = 0.002 bins per instance of the original. Surviving weights are then rounded to the nearest of {1, 2, 5} x 10^k that stays within the same tolerance. Every packing execution is counted; one simplification is capped at 150000 executions.

Reporting: mean bins, mean excess over best-fit, win/tie/loss, identical-packing share and per-item placement agreement, paired per-instance bootstrap 95% intervals (10000 resamples, seed 739). A rule that reduces to best-fit is reported as such.
