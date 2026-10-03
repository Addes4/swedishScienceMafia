# Exploratory follow-up, after observing v1

v1 did not beat best-fit, and the counterexample-vs-random confidence interval crossed zero. The initial search refused all score-neutral changes, restricting exploration. Its tail-risk arm also penalized absolute bin counts, which mostly emphasized large-item instances; v2 uses excess over the best-fit reference instead. References for the initial 32 cases cost 32 shared initialization executions per arm; replay references are retained from charged probe evaluations.

v2 allows random selection among tied candidates (neutral drift), uses 50 paired seeds and 500 generations, and uses a fresh final audit seed of 961748941. All search executions are still charged: four candidates per generation, each using 24 fixed cases, 8 replay cases, and 8 fresh probes evaluated for candidate and reference = 192 executions per generation. The replay arm retains observed regressions, the random arm retains random probes, and the tail arm additionally penalizes worst replay excess. All candidate weights and traces are saved. V1 source is preserved in local-v1/source.

A separate first-fit-initialized run uses 20 paired seeds, 200 generations, neutral drift and audit seed 961748927. This tests recovery from a weak baseline, not superiority over best-fit. It uses the same three arms and evaluator accounting.

Codex selected tight_or_roomy_moderate after its v2 pilot had one win and zero losses on 1,000 search cases. Its independent audit uses 10,000 cases, seed 15485863, across eight families. There are no further revisions using this audit within that named experiment.
