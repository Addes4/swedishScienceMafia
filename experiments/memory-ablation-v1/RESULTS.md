# Memory ablation v1: results

Status: pilot done. The confirmatory run (10 seeds per arm) waits for the choice of
problem regime; see PROTOCOL.md.

## Pilot: current regime, 2 seeds x 3 arms x 30 calls

This is the first recorded closed-loop LLM run in the project: `claude-haiku-4-5`
proposed 180 candidates, and the harness evaluated, promoted and wrote every next prompt
with no human edits. Backend: the V3/V4 20-feature weights language on 80-item
synthetic families. All runs started from best-fit. Seeds 100 and 101. With two seeds
the intervals in summary.json are not meaningful, so none are quoted here.

**No proposal was promoted in any of the six runs.** None used fewer bins than best-fit
on the 400-instance fixed suite, so every final incumbent is best-fit and the audited
excess is exactly 0 in every arm. In this regime the primary endpoint sits at its floor
and cannot separate the arms. No proposal was better than best-fit on the 800-instance
diagnostic suite either.

The memory section did change how the model searched:

| Arm | Harmful proposals (diagnostic suite) | Mean diagnostic excess of proposals | Proposals packing exactly like the incumbent | Median L1 distance of weights from best-fit, calls 11-30 | Realized memory tokens (mean) | Cost per run |
|---|---:|---:|---:|---:|---:|---:|
| none | 59/60 (98%) | +0.713 bins | 1/60 | 4.35 | 0 | $0.125 |
| prose | 8/60 (13%) | +0.016 bins | 56/60 | 0.03 | 1,258 | $0.167 |
| executable | 23/60 (38%) | +0.094 bins | 40/60 | 0.14 | 1,160 | $0.161 |

"Harmful" means more bins than best-fit on average over the diagnostic suite. Mean
excess is per instance; best-fit is 0.

- **none**: with no record of earlier attempts the prompt barely changes between calls,
  and the model kept proposing large, different rewrites of the weights (many features
  at once). Almost all were much worse than best-fit; none was ever repeated.
- **prose**: after one or two failures the model moved to best-fit plus tiny extra
  weights (around 0.01). These change no packing decision, so 56 of 60 proposals packed
  every fixed instance exactly like best-fit and could not be promoted. The prose memory
  said so explicitly ("It packed every fixed instance exactly like the incumbent"), and
  the model kept doing it. Only 1 of 60 was a literal copy of best-fit.
- **executable**: the same retreat towards best-fit, but less complete. The model kept
  making small, decision-changing edits (median L1 0.14 in later calls against 0.03 for
  prose), which made more of its proposals harmful than in the prose arm. Its closest
  misses lost one fixed instance in 400 (+0.0025 bins). In seed 100 it re-proposed one
  such near-miss four more times, packing exactly as before.

Reading: memory of failures, in either form, cut harmful proposals sharply compared
with no memory, mostly by making the model timid. Prose made it the most timid. Nothing
here shows that either memory finds better policies, because nothing found a better
policy. These are two seeds; the pattern is consistent across both but is a pilot
observation, not a tested result.

### What this means for the confirmatory run

- In this regime a 10-seed confirmatory run would very likely return 0, 0, 0 on the
  primary endpoint. It should use a regime with headroom over best-fit (for example the
  Weibull 5k / priority(item, bins) setting on branch exp/bp-ceiling, where FunSearch's
  heuristic is well ahead of best-fit).
- The retreat to no-op proposals wastes calls in every arm with memory. A one-sentence
  addition to the common prompt ("a proposal that packs every fixed instance exactly
  like the incumbent cannot be promoted and wastes a call") would apply to all arms
  equally. It is not adopted yet; if it is, it will be recorded as an amendment before
  the confirmatory run.

### Budget and provenance

- Anthropic: $0.9059 for the pilot (180 calls, no failed attempts, 96 token-count calls)
  plus $0.0092 for the two-call smoke check: $0.915 in total so far. Mean input per call:
  2,099 tokens (none), 3,351 (prose), 3,253 (executable); output 416-442 tokens.
- No Modal use. Evaluator work followed the same rule in every arm but its amount
  depends on how many failures need shrinking: about 45,000 packer executions per run
  for none, 21,000 for prose and 27,000 for executable, a few seconds of CPU per run.
  Runs took 2-2.5 minutes, almost all of it waiting for the API.
- Audit seed 117994974852159 and diagnostic seed 136480251067372 were taken from the
  hash of the six finished traces. pilot/summary.json, pilot/audit.json and
  pilot/runs/*.json.gz hold every prompt, response, evaluation and counterexample.
- After looking at the pilot, three descriptive metrics were added to the audit
  (repeats excluding copies of the incumbent, mean fixed-suite excess excluding copies,
  best fixed-suite excess) and the pilot audit was re-run with them. The audit is a pure
  function of the saved traces, so the re-run changed no earlier number.

## Reproduce

```sh
python -m falsify.closed_loop run --out experiments/my-pilot --seeds 100 101 --cap-usd 3
python -m falsify.closed_loop audit --out experiments/my-pilot
python -m falsify.closed_loop run --out /tmp/mock --seeds 1 2 --calls 5 --cap-usd 1 --mock   # offline
```

Model sampling is not seeded, so a rerun gives different proposals with the same
harness inputs.
